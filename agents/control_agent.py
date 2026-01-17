"""
Control Agent (Agent F)
Qualitätscheck und Loop-Entscheidungen.
Max 2 Iterationen, intelligente Entscheidung ob loopen oder enden.
"""

from typing import Optional
from models.schemas import (
    Requirements, UserProfile, UseCaseMatch, FrameworkCandidates,
    Recommendation, ControlDecision, ControlAction, AdvisorState
)


class ControlAgent:
    """
    Control Agent: Router und Quality Gate.
    Bestimmt ob Loop fortgesetzt wird oder endet.
    Max 2 Iterationen als Hard Limit.
    """

    def __init__(self):
        """Initialisiert den ControlAgent."""
        self.max_iterations = 2  # Hard limit

    def decide_continuation(self, state: AdvisorState) -> ControlDecision:
        """
        Entscheidet ob Loop fortgesetzt, User gefragt, oder Agenten rerun werden.

        Args:
            state: Vollständiger AdvisorState

        Returns:
            ControlDecision mit Action und optional user_question
        """

        # Hard limit check
        if state.iteration_count >= self.max_iterations:
            return ControlDecision(
                action=ControlAction.END,
                reasoning=f"Max iterations ({self.max_iterations}) erreicht. Beende mit bester verfügbarer Empfehlung."
            )

        # Keine Empfehlung yet = keine Decision möglich
        if not state.recommendation:
            return ControlDecision(
                action=ControlAction.END,
                reasoning="Keine Empfehlung generiert. Beende."
            )

        usecase_confidence = state.usecase_match.usecase_confidence if state.usecase_match else 0.5
        framework_confidence = state.framework_candidates.framework_confidence if state.framework_candidates else 0.5

        # Loop-Regel 1: Usecase Confidence zu niedrig
        if usecase_confidence < 0.60:
            return ControlDecision(
                action=ControlAction.RERUN_USECASE,
                reasoning=f"Use-Case Confidence zu niedrig ({usecase_confidence:.2f} < 0.60). Erneutes Matching.",
                adjustments={"top_k": 8}  # Erhöhe top_k
            )

        # Loop-Regel 2: Framework Confidence zu niedrig
        if framework_confidence < 0.60:
            return ControlDecision(
                action=ControlAction.RERUN_FRAMEWORK,
                reasoning=f"Framework Confidence zu niedrig ({framework_confidence:.2f} < 0.60). Suche erweitern.",
                adjustments={"top_k": 8}
            )

        # Loop-Regel 3: Mismatch zwischen Usecase-Typ und Framework-Typ
        if state.usecase_match and state.framework_candidates:
            mismatch = self._check_type_mismatch(state.usecase_match, state.framework_candidates)
            if mismatch:
                return ControlDecision(
                    action=ControlAction.RERUN_FRAMEWORK,
                    reasoning=f"Typ-Mismatch erkannt: {mismatch}",
                    adjustments={"enforce_constraint": True}
                )

        # Loop-Regel 4: Kritische Infos fehlen
        if state.requirements and state.requirements.unknowns:
            if len(state.requirements.unknowns) >= 2:
                question = self._generate_clarification_question(state.requirements.unknowns)
                return ControlDecision(
                    action=ControlAction.ASK_USER,
                    reasoning="Kritische Informationen fehlen für bessere Empfehlung.",
                    user_question=question
                )

        # Alles ok = Ende
        return ControlDecision(
            action=ControlAction.END,
            reasoning="Qualitäts-Gates bestanden. Empfehlung ist solide."
        )

    def _check_type_mismatch(
        self,
        usecase_match: UseCaseMatch,
        framework_candidates: FrameworkCandidates
    ) -> Optional[str]:
        """
        Prüft auf Typ-Mismatch zwischen Usecase und Framework.
        Z.B. Usecase = RAG Q&A, aber Framework = primär Automation Tool.

        Returns:
            Beschreibung des Mismatches oder None
        """

        derived_reqs = usecase_match.derived_requirements or {}

        # Wenn RAG required aber kein RAG-Framework in Top 3?
        if derived_reqs.get("rag_required"):
            # Einfache Heuristik: LangChain/Chroma sind RAG-frameworks
            rag_frameworks = ["LangChain", "Chroma", "LangGraph", "Google ADK"]
            top_3_names = [c.framework_name for c in framework_candidates.candidates[:3]]
            if not any(fw in str(top_3_names) for fw in rag_frameworks):
                return "Usecase benötigt RAG, aber Top-Frameworks sind nicht RAG-fokussiert"

        # Wenn Automation High aber Framework ist primär No-Code?
        if derived_reqs.get("automation_high"):
            nocode_frameworks = ["n8n", "Zapier"]
            top_1_name = framework_candidates.candidates[0].framework_name if framework_candidates.candidates else ""
            if any(fw in top_1_name for fw in nocode_frameworks):
                # Das ist ok, n8n hat durchaus Automations-Power
                pass

        return None

    def _generate_clarification_question(self, unknowns: list) -> str:
        """Generiert eine Clarification Question."""
        unknown_str = ", ".join(unknowns[:2])
        return f"Kannst du noch präzisieren: {unknown_str}?"
