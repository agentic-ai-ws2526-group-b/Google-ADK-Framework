"""
Decision Agent (Agent E)
Kombiniert Requirements + Profile + UseCaseMatch + FrameworkCandidates zu Recommendation.
"""

from typing import Optional, List
from models.schemas import (
    Requirements, UserProfile, UseCaseMatch, FrameworkCandidates,
    Recommendation, ArchitectureSuggestion, FrameworkCandidate
)


class DecisionAgent:
    """
    Decision Agent: Kombiniert alle Agent-Outputs zu einer finalen Empfehlung.
    """

    def __init__(self):
        """Initialisiert den DecisionAgent."""
        pass

    def decide(
        self,
        requirements: Requirements,
        user_profile: UserProfile,
        usecase_match: UseCaseMatch,
        framework_candidates: FrameworkCandidates
    ) -> Recommendation:
        """
        Erstellt finale Empfehlung.

        Args:
            requirements: Requirements Objekt
            user_profile: UserProfile Objekt
            usecase_match: UseCaseMatch Objekt
            framework_candidates: FrameworkCandidates Objekt

        Returns:
            Recommendation Objekt
        """

        # Top-1 und Top-3
        if not framework_candidates.candidates:
            # Fallback wenn keine Kandidaten gefunden
            print("  (Warning: No framework candidates, using default)")
            fallback_candidates = [
                FrameworkCandidate(
                    framework_name="LangChain",
                    score=0.75,
                    reason="Universal framework for AI agents. Suitable for most use cases.",
                    sources=[]
                ),
                FrameworkCandidate(
                    framework_name="Google ADK",
                    score=0.70,
                    reason="Google's agent development kit. Good for cloud-native solutions.",
                    sources=[]
                ),
                FrameworkCandidate(
                    framework_name="LlamaIndex",
                    score=0.65,
                    reason="Specialized for RAG and data indexing tasks.",
                    sources=[]
                )
            ]
            framework_candidates.candidates = fallback_candidates
            framework_candidates.framework_confidence = 0.70

        top_1 = framework_candidates.candidates[0]
        top_3 = framework_candidates.candidates[:3]

        # Architektur-Vorschlag
        architecture = self._suggest_architecture(requirements, usecase_match, framework_candidates)

        # Reasoning
        reasoning = self._generate_reasoning(
            requirements, user_profile, usecase_match, top_1
        )

        # Assumptions & Risks
        assumptions, risks = self._identify_assumptions_and_risks(
            requirements, user_profile, usecase_match
        )

        # Sources
        sources = self._collect_sources(framework_candidates)

        return Recommendation(
            recommended_framework=top_1.framework_name,
            recommended_score=top_1.score,
            top_3=top_3,
            architecture_suggestion=architecture,
            reasoning_summary=reasoning,
            matched_bosch_usecases=usecase_match.matched_usecases[:3],
            assumptions=assumptions,
            risks=risks,
            sources=sources
        )

    def _suggest_architecture(
        self,
        requirements: Requirements,
        usecase_match: UseCaseMatch,
        framework_candidates: FrameworkCandidates
    ) -> ArchitectureSuggestion:
        """Schlägt Architektur vor."""

        requires_rag = usecase_match.derived_requirements.get("rag_required", False)
        requires_tools = usecase_match.derived_requirements.get("connectors_required", False)
        requires_escalation = "unknowns" in requirements.__dict__ and len(requirements.unknowns) > 0

        # Agent-Typ
        if usecase_match.derived_requirements.get("multi_agent_recommended"):
            agent_type = "multi_agent"
        elif requires_rag and not requires_tools:
            agent_type = "agentic_rag"
        else:
            agent_type = "single_agent"

        notes = []
        if requires_rag:
            notes.append("RAG mit Semantic Search für Dokument-Retrieval")
        if requires_tools:
            notes.append("Connector-Integration für API/Datenquellen")
        if requires_escalation:
            notes.append("Human-Escalation Pattern für komplexe Cases")

        return ArchitectureSuggestion(
            agent_type=agent_type,
            requires_rag=requires_rag,
            requires_tools=requires_tools,
            requires_escalation=requires_escalation,
            notes="; ".join(notes) if notes else "Standard Single-Agent Setup"
        )

    def _generate_reasoning(
        self,
        requirements: Requirements,
        user_profile: UserProfile,
        usecase_match: UseCaseMatch,
        top_framework
    ) -> str:
        """Generiert Begründungs-Text."""

        parts = [
            f"Framework '{top_framework.framework_name}' empfohlen basierend auf:",
            f"- Use-Case: {requirements.use_case_goal[:50]}...",
        ]

        if usecase_match.matched_usecases:
            top_uc = usecase_match.matched_usecases[0]
            parts.append(f"- Match zu Bosch UC: {top_uc.usecase_title} (Score: {top_uc.match_score:.2f})")

        parts.append(f"- Profil: {user_profile.skill_level} Skill, {user_profile.org_context} Context")
        parts.append(f"- Top Begründung: {top_framework.reason[:80]}...")

        return " ".join(parts)

    def _identify_assumptions_and_risks(
        self,
        requirements: Requirements,
        user_profile: UserProfile,
        usecase_match: UseCaseMatch
    ):
        """Identifiziert Assumptions und Risks."""

        assumptions = [
            "Annahme: Dokumentation ist zeitnah verfügbar",
            "Annahme: Team hat Zugang zu erforderlichen APIs/Datenquellen",
        ]

        if user_profile.skill_level == "beginner":
            assumptions.append("Annahme: Community-Support reicht aus für No-Code Framework")

        risks = []

        if usecase_match.derived_requirements.get("connectors_required"):
            risks.append("Risiko: Connector-Permissions müssen geklärt werden")
            risks.append("Risiko: API-Latenz und Verfügbarkeit sind kritisch")

        if usecase_match.derived_requirements.get("compliance_high"):
            risks.append("Risiko: Compliance-Audit vor Produktion erforderlich")

        if requirements.unknowns:
            risks.append(f"Risiko: {len(requirements.unknowns)} kritische Infos fehlen")

        if user_profile.risk_tolerance == "low" and usecase_match.derived_requirements.get("automation_high"):
            risks.append("Risiko: High-Automation + Low-Risk-Tolerance erfordert robust Error Handling")

        return assumptions, risks

    def _collect_sources(self, framework_candidates: FrameworkCandidates) -> List[str]:
        """Sammelt Quellen-Referenzen."""
        sources = []
        for candidate in framework_candidates.candidates[:3]:
            if candidate.sources:
                for source in candidate.sources[:2]:
                    if isinstance(source, dict):
                        doc_ref = source.get("framework", "") + " - " + source.get("document", "")[:50]
                        sources.append(doc_ref)
        return sources[:5]  # Top 5 sources
