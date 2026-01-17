"""
LangGraph Orchestrator Flow (Pflicht)
Orchestriert alle 6 Agenten mit Conditional Routing und Loops.
"""

from typing import Optional
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
import json

from models.schemas import (
    AdvisorState, ControlAction, Requirements, UserProfile,
    UseCaseMatch, FrameworkCandidates, Recommendation, ControlDecision
)
from agents.requirements_agent import RequirementsAgent
from agents.profiler_agent import ProfilerAgent
from agents.usecase_analyzer_agent import UseCaseAnalyzerAgent
from agents.framework_analyzer_agent import FrameworkAnalyzerAgent
from agents.decision_agent import DecisionAgent
from agents.control_agent import ControlAgent
from adk_adapter import create_all_adk_agent_definitions


# ============================================================================
# Initialize Agents
# ============================================================================

requirements_agent = RequirementsAgent()
profiler_agent = ProfilerAgent()
usecase_analyzer_agent = UseCaseAnalyzerAgent()
framework_analyzer_agent = FrameworkAnalyzerAgent()
decision_agent = DecisionAgent()
control_agent = ControlAgent()


# ============================================================================
# Node Functions (ein Node pro Agent)
# ============================================================================

def node_requirements_agent(state: AdvisorState) -> AdvisorState:
    """Node A: RequirementsAgent - Parst User-Input zu Requirements."""
    print("\n🔹 [NODE] Requirements Agent")
    print(f"   Input: {state.user_input[:100]}...")
    
    try:
        requirements = requirements_agent.parse_user_input(state.user_input)
        state.requirements = requirements
        state.messages_history.append({
            "agent": "RequirementsAgent",
            "output": f"Requirements parsed. {len(requirements.constraints)} constraints, {len(requirements.unknowns)} unknowns."
        })
        print(f"   ✓ Requirements: {len(requirements.constraints)} constraints")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.messages_history.append({"agent": "RequirementsAgent", "error": str(e)})
    
    return state


def node_profiler_agent(state: AdvisorState) -> AdvisorState:
    """Node B: ProfilerAgent - Erstellt UserProfile."""
    print("\n🔹 [NODE] Profiler Agent")
    
    if not state.requirements:
        print("   ✗ No requirements available")
        return state
    
    try:
        profile = profiler_agent.profile_user(state.requirements)
        state.user_profile = profile
        state.messages_history.append({
            "agent": "ProfilerAgent",
            "output": f"Profile: {profile.skill_level} / {profile.org_context}"
        })
        print(f"   ✓ Profile: {profile.skill_level} / {profile.org_context}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.messages_history.append({"agent": "ProfilerAgent", "error": str(e)})
    
    return state


def node_usecase_analyzer_agent(state: AdvisorState) -> AdvisorState:
    """Node C: UseCaseAnalyzerAgent - Matcht gegen Bosch Use Cases."""
    print("\n🔹 [NODE] UseCase Analyzer Agent")
    
    if not state.requirements:
        print("   ✗ No requirements available")
        return state
    
    try:
        # Adjustments von ControlAgent falls vorhanden
        top_k = 5
        if state.control_decision and state.control_decision.adjustments:
            top_k = state.control_decision.adjustments.get("top_k", 5)
        
        usecase_match = usecase_analyzer_agent.analyze_requirements(
            state.requirements,
            top_k=top_k
        )
        state.usecase_match = usecase_match
        state.messages_history.append({
            "agent": "UseCaseAnalyzerAgent",
            "output": f"Matched {len(usecase_match.matched_usecases)} usecases (confidence: {usecase_match.usecase_confidence:.2f})"
        })
        print(f"   ✓ Matched {len(usecase_match.matched_usecases)} usecases (conf: {usecase_match.usecase_confidence:.2f})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.messages_history.append({"agent": "UseCaseAnalyzerAgent", "error": str(e)})
    
    return state


def node_framework_analyzer_agent(state: AdvisorState) -> AdvisorState:
    """Node D: FrameworkAnalyzerAgent - Findet Framework-Kandidaten."""
    print("\n🔹 [NODE] Framework Analyzer Agent")
    
    if not state.requirements:
        print("   ✗ No requirements available")
        return state
    
    try:
        # Adjustments von ControlAgent falls vorhanden
        top_k = 5
        if state.control_decision and state.control_decision.adjustments:
            top_k = state.control_decision.adjustments.get("top_k", 5)
        
        framework_candidates = framework_analyzer_agent.analyze_requirements(
            state.requirements,
            usecase_match=state.usecase_match,
            top_k=top_k,
            adjustments=state.control_decision.adjustments if state.control_decision else None
        )
        state.framework_candidates = framework_candidates
        state.messages_history.append({
            "agent": "FrameworkAnalyzerAgent",
            "output": f"Found {len(framework_candidates.candidates)} candidates (confidence: {framework_candidates.framework_confidence:.2f})"
        })
        print(f"   ✓ Found {len(framework_candidates.candidates)} candidates (conf: {framework_candidates.framework_confidence:.2f})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.messages_history.append({"agent": "FrameworkAnalyzerAgent", "error": str(e)})
    
    return state


def node_decision_agent(state: AdvisorState) -> AdvisorState:
    """Node E: DecisionAgent - Erstellt Finale Empfehlung."""
    print("\n🔹 [NODE] Decision Agent")
    
    if not (state.requirements and state.user_profile and state.framework_candidates):
        print("   ✗ Missing inputs for decision")
        return state
    
    try:
        # Fallback für usecase_match falls nicht vorhanden
        if not state.usecase_match:
            from models.schemas import UseCaseMatch, UseCaseMatchItem
            state.usecase_match = UseCaseMatch(
                matched_usecases=[],
                usecase_confidence=0.3,
                derived_requirements={},
                summary="No usecase match available"
            )
        
        recommendation = decision_agent.decide(
            state.requirements,
            state.user_profile,
            state.usecase_match,
            state.framework_candidates
        )
        state.recommendation = recommendation
        state.messages_history.append({
            "agent": "DecisionAgent",
            "output": f"Recommended: {recommendation.recommended_framework} (score: {recommendation.recommended_score:.2f})"
        })
        print(f"   ✓ Recommended: {recommendation.recommended_framework} (score: {recommendation.recommended_score:.2f})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.messages_history.append({"agent": "DecisionAgent", "error": str(e)})
        import traceback
        traceback.print_exc()
    
    return state


def node_control_agent(state: AdvisorState) -> AdvisorState:
    """Node F: ControlAgent - Quality Gate und Loop Routing."""
    print("\n🔹 [NODE] Control Agent")
    
    try:
        control_decision = control_agent.decide_continuation(state)
        state.control_decision = control_decision
        state.iteration_count += 1
        
        # Handle both enum and string representations
        action_str = control_decision.action.value if hasattr(control_decision.action, 'value') else str(control_decision.action)
        state.messages_history.append({
            "agent": "ControlAgent",
            "output": f"Decision: {action_str} (Iteration: {state.iteration_count})"
        })
        print(f"   ✓ Decision: {action_str} (Iteration: {state.iteration_count})")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        state.control_decision = None
        state.messages_history.append({"agent": "ControlAgent", "error": str(e)})
    
    return state


# ============================================================================
# Conditional Router Functions
# ============================================================================

def route_from_control(state: AdvisorState) -> str:
    """
    Router nach ControlAgent.
    Entscheidet nächsten Node basierend auf ControlDecision.
    """
    if not state.control_decision:
        return END
    
    action = state.control_decision.action
    
    if action == ControlAction.END:
        return END
    elif action == ControlAction.ASK_USER:
        return "node_ask_user"
    elif action == ControlAction.RERUN_USECASE:
        return "node_usecase_analyzer_agent"
    elif action == ControlAction.RERUN_FRAMEWORK:
        return "node_framework_analyzer_agent"
    else:
        return END


def node_ask_user(state: AdvisorState) -> AdvisorState:
    """Node: Frage an User stellen (für CLI/Streamlit)."""
    print("\n🔹 [NODE] Ask User")
    
    if state.control_decision and state.control_decision.user_question:
        print(f"   Question: {state.control_decision.user_question}")
        state.messages_history.append({
            "agent": "ControlAgent",
            "question": state.control_decision.user_question
        })
    
    # In einer echten Umgebung würde hier User-Input abgewartet
    # Für den Flow: dummy antwort
    state.messages_history.append({
        "source": "user_response",
        "message": "User antwortet..."
    })
    
    return state


# ============================================================================
# LangGraph Flow Creation
# ============================================================================

def create_advisor_flow():
    """
    Erstellt und gibt den kompletten LangGraph Flow zurück.
    
    Flow-Struktur:
    START -> Requirements -> Profiler -> UseCaseAnalyzer -> FrameworkAnalyzer -> Decision -> Control
    Control -> (conditional) -> END / ASK_USER / RERUN_USECASE / RERUN_FRAMEWORK
    """
    
    graph = StateGraph(AdvisorState)
    
    # Nodes
    graph.add_node("node_requirements_agent", node_requirements_agent)
    graph.add_node("node_profiler_agent", node_profiler_agent)
    graph.add_node("node_usecase_analyzer_agent", node_usecase_analyzer_agent)
    graph.add_node("node_framework_analyzer_agent", node_framework_analyzer_agent)
    graph.add_node("node_decision_agent", node_decision_agent)
    graph.add_node("node_control_agent", node_control_agent)
    graph.add_node("node_ask_user", node_ask_user)
    
    # Edges
    graph.add_edge(START, "node_requirements_agent")
    graph.add_edge("node_requirements_agent", "node_profiler_agent")
    graph.add_edge("node_profiler_agent", "node_usecase_analyzer_agent")
    graph.add_edge("node_usecase_analyzer_agent", "node_framework_analyzer_agent")
    graph.add_edge("node_framework_analyzer_agent", "node_decision_agent")
    graph.add_edge("node_decision_agent", "node_control_agent")
    
    # Conditional from Control
    graph.add_conditional_edges(
        "node_control_agent",
        route_from_control,
        {
            END: END,
            "node_ask_user": "node_ask_user",
            "node_usecase_analyzer_agent": "node_usecase_analyzer_agent",
            "node_framework_analyzer_agent": "node_framework_analyzer_agent"
        }
    )
    
    # Nach ASK_USER zurück zu Requirements
    graph.add_edge("node_ask_user", "node_requirements_agent")
    
    return graph.compile()


# ============================================================================
# Flow Runner
# ============================================================================

def run_advisor_flow(user_input: str, verbose: bool = True) -> AdvisorState:
    """
    Führt den gesamten Advisor Flow aus.
    
    Args:
        user_input: User's natürlichsprachliche Anfrage
        verbose: Ob Detailinfos gedruckt werden sollen
    
    Returns:
        Finaler AdvisorState mit Recommendation
    """
    
    if verbose:
        print("\n" + "="*70)
        print("🚀 ADVISOR FLOW STARTED")
        print("="*70)
        print(f"User Input: {user_input[:100]}...")
        print(f"Flow Nodes: 6 Agents + LangGraph Orchestration + Loop Control")
        print("="*70)
    
    # Initialisiere State
    initial_state = AdvisorState(user_input=user_input)
    
    # Erstelle Flow
    flow = create_advisor_flow()
    
    # Führe Flow aus
    final_state_dict = flow.invoke(initial_state)
    
    # Konvertiere dict zu AdvisorState wenn nötig
    if isinstance(final_state_dict, dict):
        final_state = AdvisorState(**final_state_dict)
    else:
        final_state = final_state_dict
    
    if verbose:
        print("\n" + "="*70)
        print("✓ ADVISOR FLOW COMPLETED")
        print("="*70)
        if final_state.recommendation:
            print(f"Recommended: {final_state.recommendation.recommended_framework}")
            print(f"Score: {final_state.recommendation.recommended_score:.2f}")
            print(f"Iterations: {final_state.iteration_count}")
        print("="*70 + "\n")
    
    return final_state


# ============================================================================
# ADK Integration Info
# ============================================================================

def print_flow_architecture():
    """Druckt Flow-Architektur mit ADK Agent Definitionen."""
    print("\n" + "="*70)
    print("LANGGRAPH + ADK ARCHITECTURE")
    print("="*70)
    
    print("\nAGENTS:")
    print("1. RequirementsAgent (A) -> Parse User Input")
    print("2. ProfilerAgent (B) -> Create User Profile")
    print("3. UseCaseAnalyzerAgent (C) -> Match Bosch UseCases")
    print("4. FrameworkAnalyzerAgent (D) -> Find Candidates")
    print("5. DecisionAgent (E) -> Create Recommendation")
    print("6. ControlAgent (F) -> Quality Gate + Routing")
    
    print("\nFLOW EDGES:")
    print("START -> A -> B -> C -> D -> E -> F -> [conditional] -> END/ASK/RERUN")
    
    print("\nLOOP RULES (in ControlAgent):")
    print("- usecase_confidence < 0.60 => RERUN_USECASE")
    print("- framework_confidence < 0.60 => RERUN_FRAMEWORK")
    print("- Type Mismatch => RERUN_FRAMEWORK")
    print("- Critical Info Missing => ASK_USER")
    print("- Else => END")
    print("- Hard Limit: 2 max iterations")
    
    print("\nADK INTEGRATION:")
    from adk_adapter import create_all_adk_agent_definitions
    adk_agents = create_all_adk_agent_definitions()
    print(f"- {len(adk_agents)} ADK Agent Definitions created")
    print("- Tools, Policies, Knowledge Bases defined")
    print("- Policies: quality_gate_enforcement, iteration_limit_2")
    
    print("\n" + "="*70)
