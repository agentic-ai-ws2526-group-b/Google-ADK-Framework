"""
Data Models & State Management für das Agent-for-Agents System.

Pydantic V2 Models für strukturierte Kommunikation zwischen Agenten.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# Enums für strukturierte Typen
# ============================================================================

class AutomationLevel(str, Enum):
    """Automatisierungsstufen eines Use Cases."""
    QA_ONLY = "qa_only"
    TOOL_ACTIONS = "tool_actions"
    WORKFLOW_AUTOMATION = "workflow_automation"


class SkillLevel(str, Enum):
    """Technisches Skill Level des Users."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class OrgContext(str, Enum):
    """Organisatorischer Kontext."""
    PROTOTYPE = "prototype"
    ENTERPRISE = "enterprise"


class RiskTolerance(str, Enum):
    """Risikotoleranz des Nutzers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ControlAction(str, Enum):
    """Aktionen, die der ControlAgent auslösen kann."""
    END = "end"
    ASK_USER = "ask_user"
    RERUN_USECASE = "rerun_usecase"
    RERUN_FRAMEWORK = "rerun_framework"


# ============================================================================
# Requirements Agent Output
# ============================================================================

class Requirements(BaseModel):
    """Strukturierte Anforderungen aus User-Input."""
    
    use_case_goal: str = Field(..., description="Beschreibung des Use-Case Ziels")
    constraints: List[str] = Field(default_factory=list, description="Constraints/Einschränkungen")
    data_sources: List[str] = Field(default_factory=list, description="Erforderliche Datenquellen")
    automation_level: Optional[AutomationLevel] = Field(None, description="Automatisierungsstufe")
    no_code_importance: Optional[int] = Field(None, ge=1, le=5, description="No-Code Wichtigkeit (1-5)")
    enterprise_needed: Optional[bool] = Field(None, description="Enterprise Features erforderlich?")
    team_size: Optional[int] = Field(None, description="Team-Größe")
    budget: Optional[str] = Field(None, description="Budget-Kategorie")
    must_have_frameworks: List[str] = Field(default_factory=list, description="Muss-Frameworks")
    must_avoid_frameworks: List[str] = Field(default_factory=list, description="Zu vermeidende Frameworks")
    unknowns: List[str] = Field(default_factory=list, description="Unbekannte/fehlende Informationen")
    
    class Config:
        use_enum_values = True


# ============================================================================
# Profiler Agent Output
# ============================================================================

class UserProfile(BaseModel):
    """Profil des Benutzers."""
    
    skill_level: SkillLevel = Field(..., description="Technisches Skill Level")
    org_context: OrgContext = Field(..., description="Organisatorischer Kontext")
    risk_tolerance: RiskTolerance = Field(..., description="Risikotoleranz")
    compliance_sensitivity: RiskTolerance = Field(..., description="Compliance-Sensibilität")
    prefers_nocode: bool = Field(default=False, description="Bevorzugt No-Code Lösungen?")
    
    class Config:
        use_enum_values = True


# ============================================================================
# UseCase Analyzer Output
# ============================================================================

class UseCaseMatchItem(BaseModel):
    """Ein gematched Bosch Use Case."""
    
    usecase_id: str = Field(..., description="ID des Use Cases")
    usecase_title: str = Field(..., description="Titel des Use Cases")
    match_score: float = Field(..., ge=0, le=1, description="Match Score (0-1)")
    category: str = Field(..., description="Kategorie des Use Cases")
    tags: List[str] = Field(default_factory=list, description="Tags des Use Cases")


class UseCaseMatch(BaseModel):
    """Output des UseCaseAnalyzerAgent."""
    
    matched_usecases: List[UseCaseMatchItem] = Field(..., description="Top-K gematchtе Use Cases")
    usecase_confidence: float = Field(..., ge=0, le=1, description="Gesamtvertrauen (0-1)")
    derived_requirements: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Abgeleitete Anforderungen (z.B. rag_required, automation_high)"
    )
    summary: str = Field(..., description="Kurze Zusammenfassung")


# ============================================================================
# Framework Analyzer Output
# ============================================================================

class FrameworkCandidate(BaseModel):
    """Ein Framework-Kandidat."""
    
    framework_name: str = Field(..., description="Framework Name")
    score: float = Field(..., ge=0, le=1, description="Score (0-1)")
    reason: str = Field(..., description="Begründung")
    sources: List[Dict[str, str]] = Field(default_factory=list, description="Quellen aus Chroma")


class FrameworkCandidates(BaseModel):
    """Output des FrameworkAnalyzerAgent."""
    
    candidates: List[FrameworkCandidate] = Field(..., description="Framework-Kandidaten")
    framework_confidence: float = Field(..., ge=0, le=1, description="Vertrauen in Kandidaten (0-1)")
    summary: str = Field(..., description="Kurze Zusammenfassung")


# ============================================================================
# Decision Agent Output
# ============================================================================

class ArchitectureSuggestion(BaseModel):
    """Architektur-Vorschlag."""
    
    agent_type: str = Field(..., description="z.B. 'single_agent', 'multi_agent', 'agentic_rag'")
    requires_rag: bool = Field(..., description="RAG erforderlich?")
    requires_tools: bool = Field(..., description="Tools/Connectors erforderlich?")
    requires_escalation: bool = Field(..., description="Human Escalation Pattern erforderlich?")
    notes: str = Field(..., description="Notizen zur Architektur")


class Recommendation(BaseModel):
    """Finale Empfehlung des Systems."""
    
    recommended_framework: str = Field(..., description="Top-1 Framework")
    recommended_score: float = Field(..., ge=0, le=1, description="Score (0-1)")
    top_3: List[FrameworkCandidate] = Field(..., description="Top 3 Kandidaten")
    
    architecture_suggestion: ArchitectureSuggestion = Field(..., description="Architektur-Vorschlag")
    reasoning_summary: str = Field(..., description="Kurze Begründung")
    matched_bosch_usecases: List[UseCaseMatchItem] = Field(default_factory=list, description="Gematchtе Bosch Use Cases")
    
    assumptions: List[str] = Field(default_factory=list, description="Annahmen der Empfehlung")
    risks: List[str] = Field(default_factory=list, description="Identifizierte Risiken")
    sources: List[str] = Field(default_factory=list, description="Quellen-Referenzen")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Zeitstempel der Empfehlung")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# Control Agent Output
# ============================================================================

class ControlDecision(BaseModel):
    """Entscheidung des ControlAgent."""
    
    action: ControlAction = Field(..., description="Aktion (END, ASK_USER, RERUN_USECASE, RERUN_FRAMEWORK)")
    reasoning: str = Field(..., description="Begründung der Entscheidung")
    user_question: Optional[str] = Field(None, description="Rückfrage an User (falls ASK_USER)")
    adjustments: Optional[Dict[str, Any]] = Field(None, description="Parameter-Anpassungen für nächste Iteration")
    
    class Config:
        use_enum_values = True


# ============================================================================
# Session & Feedback
# ============================================================================

class SessionFeedback(BaseModel):
    """Feedback nach einer Session."""
    
    rating: int = Field(..., ge=1, le=5, description="1-5 Sterne Bewertung")
    helpful: bool = Field(..., description="Hat geholfen?")
    comment: Optional[str] = Field(None, description="Optionaler Kommentar")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Zeitstempel")
    session_id: str = Field(..., description="Session ID")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================================================
# Global State Management für LangGraph
# ============================================================================

class AdvisorState(BaseModel):
    """Globaler State für den LangGraph Flow."""
    
    # Input
    user_input: str = Field(..., description="Rohes User-Input")
    
    # Agenten-Outputs
    requirements: Optional[Requirements] = Field(None, description="Requirements aus Agent A")
    user_profile: Optional[UserProfile] = Field(None, description="Profile aus Agent B")
    usecase_match: Optional[UseCaseMatch] = Field(None, description="Use-Case Matches aus Agent C")
    framework_candidates: Optional[FrameworkCandidates] = Field(None, description="Framework-Kandidaten aus Agent D")
    recommendation: Optional[Recommendation] = Field(None, description="Finale Empfehlung aus Agent E")
    
    # Kontroll-Flow
    control_decision: Optional[ControlDecision] = Field(None, description="Entscheidung vom Control Agent")
    iteration_count: int = Field(default=0, description="Anzahl der Loop-Iterationen")
    messages_history: List[Dict[str, str]] = Field(default_factory=list, description="Nachrichtenhistorie")
    
    # Feedback
    feedback: Optional[SessionFeedback] = Field(None, description="Session Feedback")
    session_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()), description="Session ID")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = False  # Keep enums as objects for processing
