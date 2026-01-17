"""
Google ADK Adapter
Macht die Google ADK Integration sichtbar im Code.

Dieser Adapter kapselt ADK-Konzepte und Patterns:
- Agent Definition (mit Tools und Instructions)
- Agent Runtime / Execution
- Policy Management (falls relevant)

ADK Dokumentation: https://cloud.google.com/agent-builder/agent-development-kit
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# ADK Agent Concepts
# ============================================================================

class ADKExecutionMode(str, Enum):
    """ADK Execution Modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"


@dataclass
class ADKTool:
    """
    Repräsentation eines ADK Tools.
    
    Im echten ADK wären Tools über das Tool Registry definiert.
    Hier: einfache Struktur für unsere Agenten.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary für LLM Prompts."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema
        }


@dataclass
class ADKAgentDefinition:
    """
    Repräsentation einer ADK Agent Definition.
    
    Im echten ADK: Über Agent Builder UI oder SDK definiert.
    Hier: Struktur für unsere 6 Agenten.
    """
    agent_id: str
    agent_name: str
    description: str
    instructions: str
    tools: List[ADKTool]
    knowledge_base_ids: Optional[List[str]] = None
    execution_mode: ADKExecutionMode = ADKExecutionMode.SYNCHRONOUS
    policies: Optional[List[str]] = None  # z.B. ["require_human_approval"]

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "instructions": self.instructions,
            "tools": [t.to_dict() for t in self.tools],
            "knowledge_base_ids": self.knowledge_base_ids,
            "execution_mode": self.execution_mode.value,
            "policies": self.policies
        }


@dataclass
class ADKAgentRuntime:
    """
    ADK Agent Runtime / Execution Context.
    
    Im echten ADK: Runtime-Umgebung die Agents managed.
    Hier: Kontext für Agent-Ausführung in unserem Flow.
    """
    agent_definition: ADKAgentDefinition
    session_id: str
    context: Dict[str, Any]
    max_iterations: int = 10
    timeout_seconds: int = 300

    def get_agent_instructions(self) -> str:
        """Gibt die kompletten Agenten-Instruktionen zurück."""
        return self.agent_definition.instructions

    def get_available_tools(self) -> List[str]:
        """Gibt verfügbare Tool Names zurück."""
        return [t.name for t in self.agent_definition.tools]


# ============================================================================
# ADK Agent Factory
# ============================================================================

class ADKAgentFactory:
    """
    Factory zur Erstellung von ADK-konformen Agent Definitionen.
    Nutzt diese Factory für alle 6 Agenten in unserem System.
    """

    @staticmethod
    def create_requirements_agent() -> ADKAgentDefinition:
        """Erstellt Requirements Agent Definition."""
        return ADKAgentDefinition(
            agent_id="agent_requirements_001",
            agent_name="Requirements Analyzer",
            description="Parst natürlichsprachliche User-Eingaben zu strukturierten Requirements.",
            instructions="""
Du bist ein Requirements-Analyzer Agent. Deine Aufgabe:

1. Lese den User-Input sorgfältig
2. Extrahiere das eigentliche Use-Case Ziel
3. Identifiziere Constraints und Anforderungen
4. Klassizie die Automatisierungsstufe (qa_only, tool_actions, workflow_automation)
5. Sammle fehlende kritische Infos

Gib strukturierte Requirements zurück.
            """,
            tools=[
                ADKTool(
                    name="extract_requirements",
                    description="Extrahiert strukturierte Requirements aus Text",
                    input_schema={"type": "string", "description": "User input"},
                    output_schema={"type": "object", "description": "Requirements"}
                ),
                ADKTool(
                    name="classify_automation_level",
                    description="Klassifiziert Automatisierungsstufe",
                    input_schema={"type": "string"},
                    output_schema={"type": "string", "enum": ["qa_only", "tool_actions", "workflow_automation"]}
                )
            ],
            knowledge_base_ids=["kb_requirements_patterns"],
            execution_mode=ADKExecutionMode.SYNCHRONOUS
        )

    @staticmethod
    def create_usecase_analyzer_agent() -> ADKAgentDefinition:
        """Erstellt UseCaseAnalyzer Agent Definition."""
        return ADKAgentDefinition(
            agent_id="agent_usecase_analyzer_001",
            agent_name="Use-Case Analyzer",
            description="Matcht Requirements gegen Bosch Use-Case Pool.",
            instructions="""
Du bist ein Use-Case Analyzer Agent. Deine Aufgabe:

1. Lese die Requirements
2. Suche ähnliche Bosch Use Cases in der Knowledge Base
3. Bewerte Match-Qualität
4. Leite Anforderungs-Tags ab (rag_required, automation_high, etc.)
5. Gib Matches mit Confidence zurück

Nutze semantische Matching Strategien.
            """,
            tools=[
                ADKTool(
                    name="search_usecases",
                    description="Sucht Use Cases in Chroma Vectorstore",
                    input_schema={"type": "string", "description": "Query"},
                    output_schema={"type": "array"}
                ),
                ADKTool(
                    name="derive_requirements",
                    description="Leitet Requirements aus Matches ab",
                    input_schema={"type": "array"},
                    output_schema={"type": "object"}
                )
            ],
            knowledge_base_ids=["kb_bosch_usecases"],
            execution_mode=ADKExecutionMode.SYNCHRONOUS
        )

    @staticmethod
    def create_framework_analyzer_agent() -> ADKAgentDefinition:
        """Erstellt FrameworkAnalyzer Agent Definition."""
        return ADKAgentDefinition(
            agent_id="agent_framework_analyzer_001",
            agent_name="Framework Analyzer",
            description="Findet beste Framework-Kandidaten basierend auf Requirements.",
            instructions="""
Du bist ein Framework Analyzer Agent. Deine Aufgabe:

1. Lese die Requirements und Use-Case Matches
2. Suche passende Frameworks in Knowledge Base
3. Bewerte Frameworks nach Kriterien (ease_of_use, community, performance, etc.)
4. Gib Top-K Kandidaten mit Scores zurück
5. Liefere Evidenzen für die Wahl

Nutze Multi-Kriterien Evaluation.
            """,
            tools=[
                ADKTool(
                    name="search_frameworks",
                    description="Sucht Frameworks in Knowledge Base",
                    input_schema={"type": "string"},
                    output_schema={"type": "array"}
                ),
                ADKTool(
                    name="evaluate_framework",
                    description="Evaluiert Framework nach Kriterien",
                    input_schema={"type": "string"},
                    output_schema={"type": "object"}
                )
            ],
            knowledge_base_ids=["kb_framework_docs"],
            execution_mode=ADKExecutionMode.SYNCHRONOUS,
            policies=["multi_criteria_evaluation"]
        )

    @staticmethod
    def create_decision_agent() -> ADKAgentDefinition:
        """Erstellt DecisionAgent Definition."""
        return ADKAgentDefinition(
            agent_id="agent_decision_001",
            agent_name="Decision Agent",
            description="Kombiniert alle Inputs zu finaler Empfehlung.",
            instructions="""
Du bist ein Decision Agent. Deine Aufgabe:

1. Kombiniere Requirements, Profile, Use-Case Matches, Framework-Kandidaten
2. Wähle Top-1 Framework
3. Schlage Architektur vor (single/multi agent, rag/tools)
4. Identifiziere Risks und Assumptions
5. Gib strukturierte Recommendation zurück

Nutze strukturierte Decision Logic.
            """,
            tools=[
                ADKTool(
                    name="synthesize_inputs",
                    description="Kombiniert alle Agent-Outputs",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"}
                ),
                ADKTool(
                    name="suggest_architecture",
                    description="Schlägt Architektur vor",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"}
                )
            ],
            execution_mode=ADKExecutionMode.SYNCHRONOUS,
            policies=["multi_input_synthesis"]
        )

    @staticmethod
    def create_control_agent() -> ADKAgentDefinition:
        """Erstellt ControlAgent Definition."""
        return ADKAgentDefinition(
            agent_id="agent_control_001",
            agent_name="Control / Router Agent",
            description="Qualitäts-Gate und Loop-Routing.",
            instructions="""
Du bist ein Control Agent. Deine Aufgabe:

1. Überprüfe Quality Gates
2. Entscheide: END, ASK_USER, RERUN_USECASE, RERUN_FRAMEWORK
3. Setze Loop-Regeln durch (max 2 Iterationen)
4. Erkenne Type Mismatches
5. Gib strukturierte ControlDecision zurück

Loop Rules:
- Wenn usecase_confidence < 0.60 => RERUN_USECASE
- Wenn framework_confidence < 0.60 => RERUN_FRAMEWORK
- Wenn Type Mismatch => RERUN_FRAMEWORK
- Wenn kritische Infos fehlen => ASK_USER
- Sonst => END
- Hard limit: max 2 Iterationen
            """,
            tools=[
                ADKTool(
                    name="check_quality_gates",
                    description="Prüft Quality Gates",
                    input_schema={"type": "object"},
                    output_schema={"type": "object"}
                ),
                ADKTool(
                    name="decide_routing",
                    description="Entscheidet Routing",
                    input_schema={"type": "object"},
                    output_schema={"type": "string", "enum": ["END", "ASK_USER", "RERUN_USECASE", "RERUN_FRAMEWORK"]}
                )
            ],
            execution_mode=ADKExecutionMode.SYNCHRONOUS,
            policies=["quality_gate_enforcement", "iteration_limit_2"]
        )


# ============================================================================
# ADK Integration Utilities
# ============================================================================

def create_all_adk_agent_definitions() -> Dict[str, ADKAgentDefinition]:
    """
    Erstellt alle 6 ADK Agent Definitionen.
    
    Diese können für Dokumentation, Audit oder zukünftige Migration zu echtem ADK genutzt werden.
    
    Returns:
        Dict mit Agent-Definitionen, Key ist agent_id
    """
    factory = ADKAgentFactory()

    agents = {
        "requirements": factory.create_requirements_agent(),
        "profiler": ADKAgentDefinition(
            agent_id="agent_profiler_001",
            agent_name="Profiler Agent",
            description="Erstellt UserProfile aus Requirements.",
            instructions="Leite Skill Level, Org Context, Risk Tolerance aus Requirements ab.",
            tools=[]
        ),
        "usecase_analyzer": factory.create_usecase_analyzer_agent(),
        "framework_analyzer": factory.create_framework_analyzer_agent(),
        "decision": factory.create_decision_agent(),
        "control": factory.create_control_agent()
    }

    return {a.agent_id: a for a in agents.values()}


def print_adk_agent_definitions() -> None:
    """Druckt alle ADK Agent Definitionen für Dokumentation."""
    import json
    agents = create_all_adk_agent_definitions()
    print("\n" + "="*70)
    print("ADK AGENT DEFINITIONS")
    print("="*70)
    for agent_id, agent_def in agents.items():
        print(f"\n{agent_def.agent_name} ({agent_def.agent_id})")
        print("-" * 50)
        print(f"Description: {agent_def.description}")
        print(f"Tools: {[t.name for t in agent_def.tools]}")
        print(f"Execution Mode: {agent_def.execution_mode.value}")
        if agent_def.policies:
            print(f"Policies: {agent_def.policies}")
