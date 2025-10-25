"""
Core logic for the Advisor/Router Agent that matches user tasks to specialized agents.
This module implements a simple scoring system to find the best matching agent
for a given task description.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set
from agents_catalog import AgentProfile, get_all_agents


@dataclass
class AdvisorResult:
    """Result of the agent matching process, including reasoning and confidence."""
    chosen_agent_id: str | None
    chosen_agent_name: str | None
    reason: str
    action_recommendation: str
    confidence: float  # 0.0 - 1.0


def _get_keywords_from_agent(agent: AgentProfile) -> Set[str]:
    """Helper function to extract all relevant keywords from an agent profile."""
    keywords = set()
    
    # Add skills
    for skill in agent.skills:
        keywords.update(skill.lower().split())
        
    # Add words from typical tasks
    for task in agent.typical_tasks:
        keywords.update(task.lower().split())
        
    # Remove common stop words that might create false matches
    stop_words = {"der", "die", "das", "und", "für", "ein", "eine", "in", "im", "an", "diese", "dieser"}
    keywords = keywords - stop_words
    
    return keywords


def score_match(task: str, agent: AgentProfile) -> float:
    """
    Calculate a matching score between a user task and an agent profile.
    
    This is a simple heuristic implementation that counts matching keywords
    and includes additional context-specific scoring rules.
    TODO 1: Replace heuristic scoring with LLM-based semantic routing prompt
    
    Args:
        task: The user's task description
        agent: The agent profile to match against
        
    Returns:
        float: Score between 0.0 and 1.0 indicating match quality
    """
    task_lower = task.lower()
    agent_keywords = _get_keywords_from_agent(agent)
    
    # Special case scoring for content creation tasks
    if agent.id == "agent_content":
        content_indicators = {
            "instagram": 1.0,
            "post": 0.8,
            "werbetext": 1.0,
            "werbung": 0.8,
            "social media": 1.0,
            "marketing": 0.8,
            "schreibe": 0.7,
            "text": 0.6,
            "vorstellen": 0.7,
            "beschreibung": 0.7
        }
        # Check for content-specific keywords
        score = 0.0
        for keyword, weight in content_indicators.items():
            if keyword in task_lower:
                score = max(score, weight)
        if score > 0:
            return score
    
    # Default scoring for other cases
    task_words = set(task_lower.split())
    matches = len(task_words & agent_keywords)
    
    # Calculate score (normalized by keyword count to avoid bias towards verbose profiles)
    max_possible = min(len(task_words), len(agent_keywords))
    if max_possible == 0:
        return 0.0
        
    return matches / max_possible


def _get_default_recommendation(task_words: Set[str]) -> str:
    """Generate a recommendation for new agent capabilities based on task keywords."""
    skill_hints = []
    
    # Map task keywords to suggested capabilities
    keyword_to_skill = {
        "sql": "Datenbankanalyse",
        "datenbank": "Datenbankanalyse",
        "präsentation": "Visual Storytelling",
        "slides": "Präsentationserstellung",
        "powerpoint": "Visual Storytelling",
        "grafik": "Grafikdesign",
        "design": "UI/UX Design",
        "code": "Software Development",
        "programmier": "Software Development",
        "rechtlich": "Legal Writing",
        "vertrag": "Contract Management"
    }
    
    for word in task_words:
        if word in keyword_to_skill:
            skill_hints.append(keyword_to_skill[word])
    
    if not skill_hints:
        skill_hints = ["Textanalyse", "Fachexpertise"]  # Default fallback
        
    return f"Bitte neuen Agent definieren. Benötigte Fähigkeiten: {', '.join(skill_hints)}"


def advise_best_agent(task: str) -> AdvisorResult:
    """
    Find the most suitable agent for a given task description.
    
    This function scores all available agents against the task and returns
    the best match along with reasoning and confidence score. If no agent
    is suitable, it suggests creating a new specialized agent.
    
    TODO 2: Add feedback loop after each session to learn from user confirmation
    
    Args:
        task: The user's task description
        
    Returns:
        AdvisorResult containing the matching result and recommendation
    """
    agents = get_all_agents()
    scores = [(agent, score_match(task, agent)) for agent in agents]
    best_agent, best_score = max(scores, key=lambda x: x[1])
    
    # If no agent scores well enough, suggest creating a new one
    if best_score < 0.2:
        return AdvisorResult(
            chosen_agent_id=None,
            chosen_agent_name=None,
            reason="Kein existierender Agent passt wirklich gut zu dieser Aufgabe.",
            action_recommendation=_get_default_recommendation(set(task.lower().split())),
            confidence=0.0
        )
    
    # Determine reason based on task keywords
    task_lower = task.lower()
    if any(word in task_lower for word in ["schreibe", "text", "beschreibung", "email", "post"]):
        reason = "Die Anfrage klingt nach Textproduktion/Marketing."
    elif any(word in task_lower for word in ["fasse", "zusammen", "summary", "pain points", "beschwerden"]):
        reason = "Die Aufgabe erfordert das Zusammenfassen und Extrahieren von Pain Points."
    elif any(word in task_lower for word in ["trend", "kritisch", "priorisieren", "risk", "eskalation", 
                                           "kategorie", "welches problem"]):
        reason = "Es geht um Trend-Analyse und Priorisierung von Problemen."
    else:
        reason = "Die Fähigkeiten des Agents passen am besten zur Anfrage."
    
    # Generate action recommendation based on agent type
    if best_agent.id == "agent_content":
        action = "Lass den Content Agent jetzt einen professionellen Textentwurf erzeugen."
    elif best_agent.id == "agent_summary":
        action = "Lass den Summary Agent die wichtigsten Pain Points in Bullet Points destillieren."
    else:  # agent_analytics
        action = "Lass den Analytics Agent einen Management-kompatiblen Statusbericht formulieren."
    
    return AdvisorResult(
        chosen_agent_id=best_agent.id,
        chosen_agent_name=best_agent.name,
        reason=reason,
        action_recommendation=action,
        confidence=best_score
    )