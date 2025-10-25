"""
Catalog of available specialized agents with their capabilities and typical use cases.
This module serves as a simple "database" of agent profiles for the routing system.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

@dataclass
class AgentProfile:
    """Profile describing a specialized agent's capabilities and typical use cases."""
    id: str
    name: str
    description: str
    skills: List[str]
    typical_tasks: List[str]


def get_all_agents() -> List[AgentProfile]:
    """
    Returns a list of all available specialized agents.
    
    Note: In future iterations, this could load from a vector DB like Chroma
    instead of being hardcoded. The agent profiles could be stored in a 
    cloud-based vector store for easy updates and scaling.
    """
    return [
        AgentProfile(
            id="agent_comparison",
            name="Product Comparison Agent",
            description="Spezialisiert auf detaillierte Produktvergleiche und Preis-Leistungs-Analysen. "
                      "Bewertet und vergleicht Produkte anhand verschiedener Kriterien wie Preis, "
                      "Leistung, Qualität und Funktionsumfang. Erstellt übersichtliche Rankings "
                      "und Empfehlungen basierend auf spezifischen Kundenanforderungen.",
            skills=[
                "Produktvergleich",
                "Preis-Leistungs-Analyse",
                "Feature-Vergleich",
                "Produktranking",
                "Technische Spezifikationen vergleichen",
                "Zielgruppenspezifische Empfehlungen"
            ],
            typical_tasks=[
                "Vergleiche alle Bosch Bohrmaschinen nach Preis-Leistungs-Verhältnis",
                "Welches Werkzeug ist am besten für Heimwerker geeignet?",
                "Erstelle eine Übersicht der Professional-Serie sortiert nach Leistung",
                "Zeige die Top 5 Akku-Bohrschrauber im mittleren Preissegment"
            ]
        ),
        AgentProfile(
            id="agent_content",
            name="Content Agent",
            description="Erstellt hochwertige Texte in Deutsch und Englisch. Schreibt "
                      "Produktbeschreibungen, Marketing-Texte, professionelle E-Mails "
                      "an Kunden und Social-Media-Posts in brand-konformer Tonalität.",
            skills=[
                "Marketing Copy",
                "Produktbeschreibung",
                "Kunden-E-Mail formulieren",
                "Social Media Posts",
                "Tonality / Branding"
            ],
            typical_tasks=[
                "Schreibe eine Produktbeschreibung für den neuen Bosch Akku-Bohrhammer für Amazon.",
                "Formuliere eine freundliche E-Mail-Antwort an einen unzufriedenen Kunden.",
                "Erstelle einen LinkedIn-Post über unser neues Feature."
            ]
        ),
        AgentProfile(
            id="agent_summary",
            name="Summary Agent",
            description="Fasst große Mengen von Feedback, Beschwerden oder Support-Tickets "
                      "in klaren, strukturierten Management-Summaries zusammen. Liefert "
                      "Executive-Level Bullet Points und Pain Points.",
            skills=[
                "Zusammenfassen",
                "Pain Points extrahieren",
                "Executive Summary schreiben",
                "Themen clustern"
            ],
            typical_tasks=[
                "Fasse diese 20 Kundenbeschwerden in 5 Bullet Points zusammen.",
                "Was sind die drei größten Pain Points der Kunden aktuell?",
                "Gib mir eine Executive Summary für das Management-Update."
            ]
        ),
        AgentProfile(
            id="agent_analytics",
            name="Analytics Agent",
            description="Interpretiert Kundendaten und Support-Tickets. Erkennt Muster, "
                      "priorisiert Risiken und schlägt nächste Schritte für das Customer "
                      "Care Team vor. Arbeitet aktuell rein sprachbasiert als Berater (Simulation).",
            skills=[
                "Trend-Erkennung",
                "Risikobewertung",
                "Priorisierung",
                "Handlungsempfehlungen formulieren"
            ],
            typical_tasks=[
                "Welche Support-Kategorie ist aktuell am kritischsten?",
                "Wo droht Eskalation, und was sollten wir intern kommunizieren?",
                "Welche zwei Themen sollten wir nächste Woche priorisieren?"
            ]
        )
    ]


def get_agent_by_id(agent_id: str) -> AgentProfile | None:
    """
    Retrieves an agent profile by its ID.
    
    Args:
        agent_id: The unique identifier of the agent to find
        
    Returns:
        AgentProfile if found, None otherwise
    """
    for agent in get_all_agents():
        if agent.id == agent_id:
            return agent
    return None