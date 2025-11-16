"""
Framework Advisor Agent
Ein Agenten-Gerüst für die Auswahl von Frameworks basierend auf Embeddings und semantischer Suche.
"""

import json
import os
from dataclasses import dataclass
from typing import Optional

import chromadb
from dotenv import load_dotenv
import google.genai as genai


# ============================================================================
# Konstanten
# ============================================================================

# .env laden
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma")
FRAMEWORK_COLLECTION_NAME = "framework_docs"

# Embedding-Modell
EMBEDDING_MODEL = "models/embedding-001"

# Generation-Modell
GENERATION_MODEL = "gemini-2.5-flash"


# ============================================================================
# Datenklassen
# ============================================================================

@dataclass
class FrameworkMatch:
    """Ein gefundenes Framework-Match mit Score und Begründung."""
    name: str
    score: float
    reason: str
    sources: list[dict]


@dataclass
class FrameworkMultiScore:
    """
    Multi-Kriterien-Bewertung eines Frameworks.
    
    Enthält detaillierte Scores für verschiedene Evaluations-Kriterien
    wie Benutzerfreundlichkeit, Community, Performance, etc.
    """
    name: str
    overall_score: float
    criteria_scores: dict[str, float]
    summary: str


# ============================================================================
# Agent Klasse
# ============================================================================

class FrameworkAdvisorAgent:
    """
    Ein Agent, der Frameworks basierend auf Embeddings und semantischer Suche empfiehlt.
    Nutzt Google GenAI für Embeddings und Chroma als persistenten Vectorstore.
    """

    def __init__(self) -> None:
        """
        Initialisiert den FrameworkAdvisorAgent.
        
        - Lädt Umgebungsvariablen
        - Prüft auf GOOGLE_API_KEY
        - Initialisiert Google GenAI Client
        - Erstellt Chroma PersistentClient und Collection
        
        Raises:
            RuntimeError: Falls GOOGLE_API_KEY nicht gesetzt ist.
        """
        # API-Schlüssel prüfen
        if not GOOGLE_API_KEY:
            raise RuntimeError(
                "GOOGLE_API_KEY nicht gesetzt. "
                "Bitte setzen Sie die Variable in .env oder als Umgebungsvariable."
            )

        # Google GenAI Client initialisieren (neue API)
        self.genai_client = genai.Client(api_key=GOOGLE_API_KEY)

        # Chroma-Verzeichnis erstellen falls nicht existent
        os.makedirs(CHROMA_DB_DIR, exist_ok=True)

        # Chroma PersistentClient und Collection initialisieren
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=FRAMEWORK_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """
        Erzeugt Embeddings für eine Liste von Texten mit Google GenAI.
        
        Args:
            texts: Liste von Texten, die embedded werden sollen.
            
        Returns:
            Liste von Embedding-Vektoren (je eine Liste von Floats).
        """
        embeddings = []
        for text in texts:
            try:
                # Versuche: Mit Client-Methode und 'content' Parameter (neueste API)
                response = self.genai_client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    content=text
                )
                embeddings.append(response["embedding"])
            except (AttributeError, TypeError, KeyError):
                try:
                    # Fallback: Globale Funktion mit 'text' Parameter
                    response = genai.embed_content(
                        model=EMBEDDING_MODEL,
                        text=text
                    )
                    embeddings.append(response["embedding"])
                except Exception as e:
                    print(f"Warnung: Embedding fehlgeschlagen für Text: {str(e)}")
                    # Fallback: Dummy-Embedding (768 Dimensionen)
                    embeddings.append([0.0] * 768)
        return embeddings

    def seed_basic_framework_knowledge(self) -> None:
        """
        Speichert grundlegende Framework-Dokumentationen als Seed-Daten in Chroma.
        
        Dies umfasst 8 populäre Frameworks:
        - Google ADK
        - LangChain / LangGraph
        - n8n
        - CrewAI
        - Hugging Face Agents
        - OpenAI Swarm
        - AutoGPT
        - Zapier
        
        Hinweis: Diese Seed-Daten können später durch `add_framework_documentation()`
        mit detaillierteren Dokumentationen erweitert werden.
        """
        seed_documents = [
            {
                "id": "framework_google_adk",
                "framework": "Google ADK",
                "category": "Enterprise Agent Framework",
                "text": (
                    "Google Application Development Kit (ADK). "
                    "Ein Framework zur Entwicklung von Agenten-basierten Anwendungen. "
                    "Bietet Tools für Task-Execution, Integration und Orchestrierung. "
                    "Ideal für komplexe, autonome Workflows und Enterprise-Szenarien. "
                    "Unterstützt Multi-Agent-Systeme und erweiterte Fehlerbehandlung."
                )
            },
            {
                "id": "framework_langchain",
                "framework": "LangChain / LangGraph",
                "category": "LLM Framework",
                "text": (
                    "LangChain ist ein Framework für die Entwicklung von LLM-Anwendungen. "
                    "LangGraph bietet State-Machine-basierte Workflows für Agenten. "
                    "Gut für Chatbots, RAG-Systeme und Multi-Agent-Orchestrierung. "
                    "Flexible Python- und JavaScript-APIs mit großer Community. "
                    "Universell einsetzbar mit vielen integrierten Tools."
                )
            },
            {
                "id": "framework_n8n",
                "framework": "n8n",
                "category": "No-Code Automation",
                "text": (
                    "n8n ist eine Open-Source Workflow-Automatisierungs-Plattform. "
                    "Web-basierte No-Code/Low-Code Oberfläche mit visuellem Editor. "
                    "Einfache Integration mit hunderten von APIs und Services. "
                    "Perfekt für Geschäftsprozess-Automatisierung ohne Programmierung. "
                    "Selbst-hostbar mit Community Edition."
                )
            },
            {
                "id": "framework_crewai",
                "framework": "CrewAI",
                "category": "Multi-Agent Framework",
                "text": (
                    "CrewAI ist ein Framework für Multi-Agent-Systeme. "
                    "Ermöglicht die Erstellung von Teams von spezialiserten Agenten. "
                    "Built on top von LLMs mit Fokus auf Zusammenarbeit. "
                    "Gut für komplexe Aufgaben, die mehrere Rollen erfordern. "
                    "Einfache Syntax für Agent-Definition und Task-Management."
                )
            },
            {
                "id": "framework_hugging_face_agents",
                "framework": "Hugging Face Agents",
                "category": "LLM Agent Library",
                "text": (
                    "Hugging Face bietet eine Agent-Library für LLM-basierte Automation. "
                    "Nutzt Open-Source Modelle und bietet verschiedene Agent-Typen. "
                    "Integration mit Hugging Face Hub für einfachen Modellzugriff. "
                    "Gut für Research und Prototypen mit Open-Source Modellen. "
                    "Flexible Tool-Integration und Task-Definition."
                )
            },
            {
                "id": "framework_openai_swarm",
                "framework": "OpenAI Swarm",
                "category": "Agent Orchestration",
                "text": (
                    "OpenAI Swarm ist eine Bibliothek für einfache Multi-Agent-Orchestrierung. "
                    "Fokus auf leichte Workflows zwischen mehreren Agenten. "
                    "Nutzt OpenAI's GPT-Modelle für Intelligenz. "
                    "Einfaches, minimalistisches Framework für Agent-Übergänge. "
                    "Ideal für sequentielle, handoff-basierte Workflows."
                )
            },
            {
                "id": "framework_autogpt",
                "framework": "AutoGPT",
                "category": "Autonomous Agent System",
                "text": (
                    "AutoGPT ist ein Framework für autonome Agenten-Systeme. "
                    "Ziel ist die vollständige Automatisierung von Aufgaben mit minimaler Überwachung. "
                    "Integriert Speicher, Tool-Nutzung und Reflexionsfähigkeiten. "
                    "Gut für komplexe, lange laufende autonome Prozesse. "
                    "Fokus auf Self-Improvement und Fehlerbehandlung."
                )
            },
            {
                "id": "framework_zapier",
                "framework": "Zapier",
                "category": "Cloud Automation",
                "text": (
                    "Zapier ist eine Cloud-basierte Automation und Integration Platform. "
                    "Verbindet tausende von Apps ohne Code. "
                    "Benutzerfreundliche Oberfläche für schnelle Workflow-Erstellung. "
                    "Ideal für Business-User und kleinere Unternehmen. "
                    "Skalierbarer SaaS mit Enterprise-Features."
                )
            }
        ]

        # Texte für Embeddings extrahieren
        documents = [doc["text"] for doc in seed_documents]
        ids = [doc["id"] for doc in seed_documents]
        metadatas = [
            {
                "framework": doc["framework"],
                "category": doc["category"]
            }
            for doc in seed_documents
        ]

        # Embeddings berechnen
        embeddings = self._embed(documents)

        # In Chroma speichern (upsert)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"✓ {len(seed_documents)} Framework-Dokumente in Chroma gespeichert.")

    def add_framework_documentation(
        self,
        framework_name: str,
        documentation: str,
        doc_source: str = "user_provided"
    ) -> None:
        """
        Fügt detaillierte Dokumentation für ein Framework hinzu.
        
        Diese Methode erlaubt es, später zusätzliche Dokumentationen
        von verschiedenen Quellen (Links, Dateien, etc.) zu laden und
        zur Wissensbasis des Agenten hinzuzufügen.
        
        Args:
            framework_name: Name des Frameworks (z.B. "Google ADK")
            documentation: Der Dokumentationstext (kann aus Datei oder Link stammen)
            doc_source: Quelle der Dokumentation (z.B. "official_docs", "link_scrape", "file_upload")
            
        Example:
            agent.add_framework_documentation(
                framework_name="Google ADK",
                documentation="Detaillierte Dokumentation...",
                doc_source="official_docs"
            )
        """
        # Eindeutige ID für dieses Dokument erstellen
        doc_id = f"framework_{framework_name.lower().replace(' ', '_')}_{doc_source}"

        # Embedding berechnen
        embedding = self._embed([documentation])[0]

        # In Chroma speichern
        self.collection.upsert(
            ids=[doc_id],
            documents=[documentation],
            embeddings=[embedding],
            metadatas=[{
                "framework": framework_name,
                "source": doc_source,
                "category": "detailed_documentation"
            }]
        )

        print(f"✓ Dokumentation für '{framework_name}' hinzugefügt (Quelle: {doc_source})")

    def add_framework_documentation_from_file(
        self,
        framework_name: str,
        file_path: str
    ) -> None:
        """
        Lädt Framework-Dokumentation aus einer lokalen Datei.
        
        Args:
            framework_name: Name des Frameworks
            file_path: Pfad zur Dokumentationsdatei (z.B. "docs/google_adk.txt")
            
        Raises:
            FileNotFoundError: Falls die Datei nicht existiert.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dokumentationsdatei nicht gefunden: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            documentation = f.read()

        self.add_framework_documentation(
            framework_name=framework_name,
            documentation=documentation,
            doc_source=f"file_{os.path.basename(file_path)}"
        )

    def add_framework_documentation_from_url(
        self,
        framework_name: str,
        url: str
    ) -> None:
        """
        Lädt Framework-Dokumentation von einer URL.
        
        Hinweis: Benötigt 'requests' und 'beautifulsoup4' Libraries.
        
        Args:
            framework_name: Name des Frameworks
            url: URL der Dokumentation
            
        Example:
            agent.add_framework_documentation_from_url(
                "Google ADK",
                "https://example.com/google-adk-docs"
            )
        """
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(
                "requests und beautifulsoup4 sind für URL-basierte Dokumentation erforderlich. "
                "Installieren Sie diese mit: pip install requests beautifulsoup4"
            )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # HTML parsen und Text extrahieren
            soup = BeautifulSoup(response.content, "html.parser")
            # Entferne Script- und Style-Tags
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Bereinige Whitespace
            text = "\n".join(line.strip() for line in text.split("\n") if line.strip())

            self.add_framework_documentation(
                framework_name=framework_name,
                documentation=text,
                doc_source=f"url_{url}"
            )
        except requests.RequestException as e:
            print(f"✗ Fehler beim Abrufen der URL: {e}")
            raise

    def find_candidate_frameworks(self, user_need: str, top_k: int = 4) -> list[FrameworkMatch]:
        """
        Sucht nach Framework-Kandidaten basierend auf einer Nutzer-Anfrage.
        
        Nutzt semantische Suche mit Embeddings, um die best passenden Frameworks zu finden.
        Mit mehr und detaillierteren Dokumentationen wird die Qualität der Empfehlungen besser.
        
        Args:
            user_need: Die Anfrage/das Bedürfnis des Nutzers (z.B. "Ich brauche Automation ohne Programmierung").
            top_k: Anzahl der Top-Ergebnisse (Default: 4).
            
        Returns:
            Liste von FrameworkMatch-Objekten, sortiert nach relevance Score.
        """
        # Embedding für die Anfrage berechnen
        query_embedding = self._embed([user_need])[0]

        # In Chroma suchen
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Ergebnisse in FrameworkMatch-Objekte konvertieren
        matches = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                # Distance zu Similarity Score konvertieren (1 - distance für cosine)
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 - distance  # Umwandlung von Distance zu Similarity

                match = FrameworkMatch(
                    name=results["metadatas"][0][i]["framework"],
                    score=score,
                    reason=results["documents"][0][i][:100] + "...",  # Kurze Preview
                    sources=[{
                        "id": doc_id,
                        "document": results["documents"][0][i],
                        "source": results["metadatas"][0][i].get("source", "seed")
                    }]
                )
                matches.append(match)

        return matches

    def choose_framework(self, user_need: str) -> FrameworkMatch:
        """
        Wählt GENAU EIN Framework basierend auf der Nutzer-Anfrage aus.
        
        Diese Methode nutzt semantische Suche um Kandidaten zu finden und
        verwendet dann Gemini, um eine intelligente Entscheidung zu treffen.
        
        Args:
            user_need: Die Anfrage/das Bedürfnis des Nutzers.
            
        Returns:
            Ein FrameworkMatch-Objekt mit dem ausgewählten Framework oder
            einem Fallback-Match, falls keine Kandidaten gefunden wurden.
        """
        # Kandidaten finden
        candidates = self.find_candidate_frameworks(user_need, top_k=4)

        # Fallback, wenn keine Kandidaten gefunden werden
        if not candidates:
            return FrameworkMatch(
                name="Unklar",
                score=0.0,
                reason="Im Vectorstore ist noch kein Wissen hinterlegt oder es wurde nichts Passendes gefunden.",
                sources=[]
            )

        # Kandidaten als strukturierte Liste für den Prompt formatieren
        candidates_info = "\n".join([
            f"- {match.name} (Relevance: {match.score:.2f}): {match.reason}"
            for match in candidates
        ])

        # Prompt für Gemini erstellen
        prompt = f"""
Du bist ein Experte für Software-Frameworks und Entwicklungswerkzeuge.
Wähle das BESTE Framework für folgendes Bedürfnis:

**Nutzer-Bedürfnis:**
{user_need}

**Verfügbare Kandidaten:**
{candidates_info}

Analysiere die Kandidaten und wähle das BESTE Framework für dieses Bedürfnis.
Antworte AUSSCHLIESSLICH mit einem JSON-Objekt in folgendem Format:

{{
  "framework": "<Name des ausgewählten Frameworks>",
  "score": <Deine Bewertung der Eignung zwischen 0.0 und 1.0>,
  "reason": "<Eine kurze, prägnante Begründung in 2-4 Sätzen, warum dieses Framework am besten passt>"
}}

Keine weiteren Erklärungen oder Text!
"""

        try:
            # Gemini API aufrufen (neue API mit Client)
            response = self.genai_client.models.generate_content(
                model=GENERATION_MODEL,
                contents=prompt
            )

            # JSON aus Response extrahieren und parsen
            response_text = response.text.strip()
            
            # JSON-Block finden und extrahieren (falls in Text eingebettet)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                # Erfolgreich geparst - FrameworkMatch erstellen
                return FrameworkMatch(
                    name=data.get("framework", "Unklar"),
                    score=float(data.get("score", 0.5)),
                    reason=data.get("reason", "Keine Begründung verfügbar."),
                    sources=[
                        {
                            "id": match.sources[0]["id"] if match.sources else "",
                            "document": match.sources[0]["document"] if match.sources else "",
                            "framework": match.name
                        }
                        for match in candidates
                    ]
                )
            else:
                # Kein JSON gefunden - Fallback
                raise ValueError("Kein JSON in Response gefunden")

        except (json.JSONDecodeError, ValueError, KeyError, AttributeError) as e:
            # JSON-Parsing fehlgeschlagen - Fallback mit Kandidaten
            print(f"⚠ Warnung: JSON-Parsing fehlgeschlagen ({e}). Nutze Fallback.")
            best_candidate = candidates[0]  # Nimm den besten Kandidaten als Fallback
            return FrameworkMatch(
                name=best_candidate.name,
                score=0.5,
                reason=response.text[:200].strip() if 'response' in locals() else "Fallback basierend auf Kandidaten.",
                sources=[
                    {
                        "id": match.sources[0]["id"] if match.sources else "",
                        "document": match.sources[0]["document"] if match.sources else "",
                        "framework": match.name
                    }
                    for match in candidates
                ]
            )

    def evaluate_frameworks_multi_criteria(
        self,
        user_need: str,
        candidates: list[FrameworkMatch] = None,
        top_k: int = 4
    ) -> list[FrameworkMultiScore]:
        """
        Bewertet Frameworks auf Basis mehrerer Kriterien.
        
        Diese Methode nutzt Gemini um detaillierte, kriterienbasierte
        Bewertungen von Frameworks durchzuführen. Kriterien sind z.B.:
        - Benutzerfreundlichkeit
        - Community & Support
        - Performance
        - Lernkurve
        - Flexibilität
        - Enterprise-Readiness
        
        Args:
            user_need: Das Bedürfnis/der Use-Case des Nutzers.
            candidates: Optional: Vordefinierte Kandidaten. 
                       Falls None, werden diese mit find_candidate_frameworks() geholt.
            top_k: Anzahl der zu bewertenden Frameworks (Default: 4).
            
        Returns:
            Liste von FrameworkMultiScore-Objekten, sortiert nach overall_score (absteigend).
        """
        # Kandidaten holen falls nicht vorgegeben
        if candidates is None:
            candidates = self.find_candidate_frameworks(user_need, top_k=top_k)

        if not candidates:
            return []

        # Kandidaten als Kontext formatieren
        candidates_info = "\n".join([
            f"- {match.name} (Relevance: {match.score:.2f})"
            for match in candidates
        ])

        # Prompt für Gemini erstellen
        evaluation_prompt = f"""
Du bist ein Experte für Software-Frameworks und DevOps-Lösungen.
Bewerte die folgenden Frameworks basierend auf dem Nutzer-Bedürfnis.

**Nutzer-Bedürfnis:**
{user_need}

**Zu bewertende Frameworks:**
{candidates_info}

Bewerte JEDEN Framework auf einer Skala von 0.0 bis 1.0 für folgende Kriterien:
1. **Benutzerfreundlichkeit** (Ease of Use): Wie einsteigerfreundlich ist das Framework?
2. **Community & Support** (Community): Wie groß und aktiv ist die Community?
3. **Performance** (Performance): Wie performant ist das Framework?
4. **Lernkurve** (Learning Curve): Wie schnell kann man es lernen?
5. **Flexibilität** (Flexibility): Wie flexibel und anpassbar ist es?
6. **Enterprise-Readiness** (Enterprise Ready): Wie produktionsreif und stabil?

Antworte NUR mit einem JSON-Array (kein weiterer Text!) in folgendem Format:

[
  {{
    "framework": "<Framework-Name>",
    "ease_of_use": 0.0-1.0,
    "community": 0.0-1.0,
    "performance": 0.0-1.0,
    "learning_curve": 0.0-1.0,
    "flexibility": 0.0-1.0,
    "enterprise_ready": 0.0-1.0,
    "summary": "<Kurze Bewertungs-Zusammenfassung in 2-3 Sätzen>"
  }},
  ...
]

Gewichte die Kriterien dem Nutzer-Bedürfnis entsprechend!
"""

        try:
            # Gemini aufrufen (neue API mit Client)
            response = self.genai_client.models.generate_content(
                model=GENERATION_MODEL,
                contents=evaluation_prompt
            )

            response_text = response.text.strip()

            # JSON-Array extrahieren
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                evaluations = json.loads(json_str)

                # In FrameworkMultiScore-Objekte konvertieren
                multi_scores = []
                for eval_data in evaluations:
                    framework_name = eval_data.get("framework", "Unknown")

                    # Alle Kriterien-Scores sammeln
                    criteria_scores = {
                        "ease_of_use": float(eval_data.get("ease_of_use", 0.5)),
                        "community": float(eval_data.get("community", 0.5)),
                        "performance": float(eval_data.get("performance", 0.5)),
                        "learning_curve": float(eval_data.get("learning_curve", 0.5)),
                        "flexibility": float(eval_data.get("flexibility", 0.5)),
                        "enterprise_ready": float(eval_data.get("enterprise_ready", 0.5))
                    }

                    # Overall-Score als Durchschnitt berechnen
                    overall_score = sum(criteria_scores.values()) / len(criteria_scores)

                    summary = eval_data.get("summary", "Keine Zusammenfassung verfügbar.")

                    multi_scores.append(FrameworkMultiScore(
                        name=framework_name,
                        overall_score=overall_score,
                        criteria_scores=criteria_scores,
                        summary=summary
                    ))

                # Nach overall_score sortieren (absteigend)
                multi_scores.sort(key=lambda x: x.overall_score, reverse=True)
                return multi_scores

            else:
                raise ValueError("Kein JSON-Array in Response gefunden")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"⚠ Fehler beim Parsen der Multi-Kriterien-Bewertung: {e}")
            # Fallback: Leere Liste
            return []

    def get_collection_stats(self) -> dict:
        """
        Gibt Statistiken über die aktuelle Wissensbasis zurück.
        
        Returns:
            Dict mit Anzahl der Dokumente und einzigartiger Frameworks.
        """
        total_docs = self.collection.count()
        # Alle Metadaten abrufen und einzigartige Frameworks zählen
        try:
            all_data = self.collection.get()
            frameworks = set(meta["framework"] for meta in all_data["metadatas"])
            return {
                "total_documents": total_docs,
                "unique_frameworks": len(frameworks),
                "frameworks": sorted(list(frameworks))
            }
        except Exception as e:
            return {
                "total_documents": total_docs,
                "error": str(e)
            }


# ============================================================================
# Utility-Funktionen
# ============================================================================

def format_multi_score_report(multi_scores: list[FrameworkMultiScore]) -> str:
    """
    Formatiert Multi-Kriterien-Bewertungen in einen lesbaren Report.
    
    Args:
        multi_scores: Liste von FrameworkMultiScore-Objekten.
        
    Returns:
        Formatierter String für die Ausgabe.
    """
    if not multi_scores:
        return "Keine Multi-Kriterien-Bewertungen verfügbar."

    lines = []
    lines.append("=" * 70)
    lines.append("📊 MULTI-KRITERIEN-BEWERTUNG")
    lines.append("=" * 70)

    for i, score in enumerate(multi_scores, 1):
        lines.append(f"\n{i}. {score.name}")
        lines.append(f"   Overall Score: {score.overall_score:.2f} / 1.00")
        lines.append("\n   Kriterium-Bewertungen:")

        # Kriterien mit Balken visualisieren
        criteria_labels = {
            "ease_of_use": "Benutzerfreundlichkeit",
            "community": "Community & Support",
            "performance": "Performance",
            "learning_curve": "Lernkurve",
            "flexibility": "Flexibilität",
            "enterprise_ready": "Enterprise-Readiness"
        }

        for criterion, value in score.criteria_scores.items():
            label = criteria_labels.get(criterion, criterion)
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            lines.append(f"   • {label:.<30} {bar} {value:.2f}")

        lines.append(f"\n   💡 {score.summary}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


# ============================================================================
# Hauptprogramm (optional, zum Testen)
# ============================================================================

if __name__ == "__main__":
    # Agent initialisieren
    agent = FrameworkAdvisorAgent()

    # Seed-Daten laden (nur beim ersten Mal oder zum Zurücksetzen)
    agent.seed_basic_framework_knowledge()

    # Optional: Beispiel für später hinzugefügte Dokumentation (nicht erforderlich jetzt)
    # agent.add_framework_documentation(
    #     framework_name="Google ADK",
    #     documentation="Detaillierte Dokumentation von Google ADK...",
    #     doc_source="official_docs"
    # )

    # Statistiken anzeigen
    stats = agent.get_collection_stats()
    print(f"\n📊 Wissensbasis-Statistiken:")
    print(f"  - Dokumente: {stats['total_documents']}")
    print(f"  - Frameworks: {stats['unique_frameworks']}")
    print(f"  - Frameworks: {', '.join(stats['frameworks'])}")

    # Test: Nach einem Framework suchen
    test_query = "Ich brauche eine schnelle Lösung ohne Programmierung für Automation"
    print(f"\n🔍 Suche: '{test_query}'")
    matches = agent.find_candidate_frameworks(test_query, top_k=3)

    print("\n✨ Ergebnisse (Semantische Suche):")
    for i, match in enumerate(matches, 1):
        print(f"  {i}. {match.name} (Score: {match.score:.3f})")
        print(f"     → {match.reason}")

    # Test: Multi-Kriterien-Bewertung
    print(f"\n📊 Multi-Kriterien-Bewertung:")
    multi_scores = agent.evaluate_frameworks_multi_criteria(test_query, top_k=3)
    
    if multi_scores:
        for i, score in enumerate(multi_scores, 1):
            print(f"\n  {i}. {score.name}")
            print(f"     Overall Score: {score.overall_score:.2f}")
            print(f"     Kriterien:")
            for criterion, value in score.criteria_scores.items():
                print(f"       - {criterion}: {value:.2f}")
            print(f"     Zusammenfassung: {score.summary}")
    else:
        print("  ⚠ Keine Multi-Kriterien-Bewertung verfügbar.")

# Optional integration with Google ADK Agent (guarded because the package may not be installed)
try:
    from google.adk.agents.llm_agent import Agent  # type: ignore
except Exception:
    Agent = None  # type: ignore

if Agent is not None:
    root_agent = Agent(
        model='gemini-2.5-flash',
        name='root_agent',
        description='A helpful assistant for user questions.',
        instruction='Answer user questions to the best of your knowledge',
    )
else:
    print("Optional google.adk.agents.llm_agent import skipped (not installed).")
