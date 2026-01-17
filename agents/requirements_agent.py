"""
Requirements Agent (Agent A)
Parst User-Input und erzeugt strukturierte Requirements.
"""

from typing import Optional
from pydantic import ValidationError
import google.genai as genai
from dotenv import load_dotenv
import os
import json
import re
import threading

from models.schemas import Requirements, AutomationLevel
from utils.llm_cache import get_cached_response, save_cached_response

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class RequirementsAgent:
    """
    Anforderungsagent: Parst natürlichsprachlichen Input zu strukturierten Requirements.
    Nutzt LLM für Verständnis und Extraktion.
    """

    def __init__(self):
        """Initialisiert den RequirementsAgent mit Google GenAI Client."""
        if not GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY nicht gesetzt")
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model = "gemini-2.5-flash"

    def parse_user_input(
        self,
        user_input: str,
        additional_answers: Optional[dict] = None
    ) -> Requirements:
        """
        Parst User-Input zu strukturierten Requirements.

        Args:
            user_input: Roher Benutzertext (z.B. Use-Case Beschreibung)
            additional_answers: Optional dict mit Antworten aus geführter UI
                                z.B. {"no_code_importance": 4, "team_size": 5}

        Returns:
            Requirements Objekt mit strukturiertem Inhalt
        """

        prompt = f"""
Du bist ein Requirements-Extraktionsagent. Deine Aufgabe ist es, aus natürlichsprachlichem
User-Input strukturierte Anforderungen zu extrahieren.

BENUTZER INPUT:
{user_input}

ZUSÄTZLICHE ANTWORTEN (falls vorhanden):
{json.dumps(additional_answers) if additional_answers else "Keine"}

EXTRAHIERE die folgenden Informationen und gib sie als JSON zurück (KEIN Markdown, reines JSON):

{{
    "use_case_goal": "Kurze Zusammenfassung des Ziels",
    "constraints": ["Constraint 1", "Constraint 2"],
    "data_sources": ["Datenquelle 1", "Datenquelle 2"],
    "automation_level": "qa_only" | "tool_actions" | "workflow_automation",
    "no_code_importance": 1-5 (oder null),
    "enterprise_needed": true/false/null,
    "team_size": number (oder null),
    "budget": "string kategorie" (oder null),
    "must_have_frameworks": ["Framework 1"],
    "must_avoid_frameworks": [],
    "unknowns": ["Fehlende Info 1", "Fehlende Info 2"]
}}

WICHTIG:
- Gib NUR das JSON Object zurück, keine anderen Kommentare.
- Verwende null für unbekannte Werte.
- automation_level: "qa_only" = Nur Q&A / Fragen beantworten,
  "tool_actions" = Tool-Aufrufe / Connectors nötig,
  "workflow_automation" = Komplexe Automatisierung mehrerer Schritte
- unknowns: Liste was NICHT klar ist aus dem Input
"""

        try:
            # Versuche Cache zuerst
            cached = get_cached_response(prompt)
            if cached:
                print("  (cached response)")
                response_text = cached
            else:
                # API Call mit sehr kurzem Timeout (3s)
                response_text = None
                error_msg = None
                
                def call_api():
                    nonlocal response_text, error_msg
                    try:
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=prompt
                        )
                        response_text = response.text.strip()
                    except Exception as e:
                        error_msg = str(e)
                
                thread = threading.Thread(target=call_api, daemon=True)
                thread.start()
                thread.join(timeout=3)  # 3 second timeout (aggressive)
                
                if response_text is None:
                    # API zu langsam - use defaults
                    print("  (API timeout, using defaults)")
                    response_text = json.dumps({
                        "use_case_goal": user_input[:100],
                        "constraints": [],
                        "data_sources": [],
                        "automation_level": "qa_only",
                        "no_code_importance": 3,
                        "enterprise_needed": False,
                        "unknowns": []
                    })
                else:
                    # Cache successful response
                    save_cached_response(prompt, response_text)
        except Exception as e:
            print(f"  (Exception, using defaults)")
            response_text = json.dumps({
                "use_case_goal": user_input[:100],
                "constraints": [],
                "data_sources": [],
                "automation_level": "qa_only",
                "no_code_importance": 3,
                "enterprise_needed": False,
                "unknowns": []
            })

        # Extrahiere JSON aus dem Response
        try:
            # Versuche direktes Parsing
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: Versuche JSON-Block zu finden
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError(f"Konnte JSON nicht parsen: {response_text}")

        # Merge mit additional_answers falls vorhanden
        if additional_answers:
            data.update(additional_answers)

        # Erstelle Requirements Objekt
        try:
            requirements = Requirements(**data)
        except ValidationError as e:
            # Fallback mit Default-Werten
            requirements = Requirements(
                use_case_goal=data.get("use_case_goal", user_input[:100]),
                constraints=data.get("constraints", []),
                data_sources=data.get("data_sources", []),
                automation_level=data.get("automation_level"),
                no_code_importance=data.get("no_code_importance"),
                enterprise_needed=data.get("enterprise_needed"),
                team_size=data.get("team_size"),
                budget=data.get("budget"),
                must_have_frameworks=data.get("must_have_frameworks", []),
                must_avoid_frameworks=data.get("must_avoid_frameworks", []),
                unknowns=data.get("unknowns", [])
            )

        return requirements
