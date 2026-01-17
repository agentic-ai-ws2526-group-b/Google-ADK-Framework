"""
Profiler Agent (Agent B)
Leitet UserProfile aus Requirements ab.
"""

import json
import re
from typing import Optional
import google.genai as genai
from dotenv import load_dotenv
import os
import threading

from models.schemas import Requirements, UserProfile, SkillLevel, OrgContext, RiskTolerance
from utils.llm_cache import get_cached_response, save_cached_response

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


class ProfilerAgent:
    """
    Profilierungs-Agent: Leitet UserProfile (Skill Level, Org Context, Risk Tolerance) 
    aus Requirements und optional direkt gesammelten Antworten ab.
    """

    def __init__(self):
        """Initialisiert den ProfilerAgent."""
        if not GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY nicht gesetzt")
        self.client = genai.Client(api_key=GOOGLE_API_KEY)
        self.model = "gemini-2.5-flash"

    def profile_user(
        self,
        requirements: Requirements,
        direct_inputs: Optional[dict] = None
    ) -> UserProfile:
        """
        Erstellt ein UserProfile basierend auf Requirements.

        Args:
            requirements: Requirements Objekt
            direct_inputs: Optional dict mit direkten Antworten
                          z.B. {"skill_level": "intermediate", "org_context": "enterprise"}

        Returns:
            UserProfile Objekt
        """

        prompt = f"""
Du bist ein User-Profilierungs-Agent. Deine Aufgabe ist es, aus Requirements und
ggf. direkten Antworten ein Benutzer-Profil zu erstellen.

REQUIREMENTS:
{json.dumps(requirements.model_dump(), default=str)}

DIREKTE ANTWORTEN (falls vorhanden):
{json.dumps(direct_inputs) if direct_inputs else "Keine"}

LEITE ab oder NUTZ die Antworten um folgendes Profil zu erstellen (REINES JSON):

{{
    "skill_level": "beginner" | "intermediate" | "expert",
    "org_context": "prototype" | "enterprise",
    "risk_tolerance": "low" | "medium" | "high",
    "compliance_sensitivity": "low" | "medium" | "high",
    "prefers_nocode": true/false
}}

DEFINITIONEN:
- skill_level: Aus no_code_importance und generellem Input ablesen
  beginner = hohe no_code_importance (4-5), einfache Anforderungen
  intermediate = gemischte Anforderungen
  expert = low no_code_importance, technische Komplexität
- org_context: Aus enterprise_needed, team_size, budget
  prototype = kleine Teams, Proof-of-Concept
  enterprise = große Teams, Budget, Compliance-Anforderungen
- risk_tolerance: Aus constraints und usecase_goal
  high = "schnelle Lösung egal wie", low = "muss stabil/sicher sein"
- compliance_sensitivity: Aus Constraints (z.B. "GDPR", "regulatory")
- prefers_nocode: Aus no_code_importance und automation_level

NUR JSON zurückgeben, kein weiterer Text.
"""

        try:
            # Versuche Cache zuerst
            cached = get_cached_response(prompt)
            if cached:
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
                    print("  (API timeout, using defaults)")
                    response_text = json.dumps({
                        "skill_level": "intermediate",
                        "org_context": "prototype",
                        "risk_tolerance": "medium",
                        "compliance_sensitivity": "low",
                        "prefers_nocode": False
                    })
                else:
                    # Cache successful response
                    save_cached_response(prompt, response_text)
        except Exception as e:
            print(f"  (Exception, using defaults)")
            response_text = json.dumps({
                "skill_level": "intermediate",
                "org_context": "prototype",
                "risk_tolerance": "medium",
                "compliance_sensitivity": "low",
                "prefers_nocode": False
            })

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback mit Defaults
                data = {
                    "skill_level": "intermediate",
                    "org_context": "enterprise" if requirements.enterprise_needed else "prototype",
                    "risk_tolerance": "medium",
                    "compliance_sensitivity": "low",
                    "prefers_nocode": (requirements.no_code_importance or 3) >= 3
                }

        # Merge mit direct_inputs
        if direct_inputs:
            data.update(direct_inputs)

        try:
            profile = UserProfile(**data)
        except Exception as e:
            # Fallback
            profile = UserProfile(
                skill_level=SkillLevel.INTERMEDIATE,
                org_context=OrgContext.ENTERPRISE if requirements.enterprise_needed else OrgContext.PROTOTYPE,
                risk_tolerance=RiskTolerance.MEDIUM,
                compliance_sensitivity=RiskTolerance.LOW,
                prefers_nocode=requirements.no_code_importance and requirements.no_code_importance >= 3
            )

        return profile
