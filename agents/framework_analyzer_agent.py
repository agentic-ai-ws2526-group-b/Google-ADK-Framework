"""
Framework Analyzer Agent (Agent D)
Findet Framework-Kandidaten über bestehende framework_docs RAG.
"""

from typing import Optional, Dict, Any
import json
import threading
from models.schemas import (
    Requirements, UseCaseMatch, FrameworkCandidates, FrameworkCandidate
)
from my_agent.agent import FrameworkAdvisorAgent

class FrameworkAnalyzerAgent:
    """
    Framework Analyzer: Nutzt bestehende FrameworkAdvisorAgent Logik,
    kapselt sie aber in eine strukturierte Interface.
    """

    def __init__(self):
        """Initialisiert den FrameworkAnalyzerAgent mit bestehendem FrameworkAdvisorAgent."""
        self.framework_agent = FrameworkAdvisorAgent()

    def analyze_requirements(
        self,
        requirements: Requirements,
        usecase_match: Optional[UseCaseMatch] = None,
        top_k: int = 5,
        adjustments: Optional[Dict[str, Any]] = None
    ) -> FrameworkCandidates:
        """
        Findet Framework-Kandidaten basierend auf Requirements.

        Args:
            requirements: Requirements Objekt
            usecase_match: Optional UseCaseMatch für Kontext
            top_k: Anzahl der Top-K Frameworks
            adjustments: Optional dict mit Adjustments (z.B. constraints erhöht)

        Returns:
            FrameworkCandidates Objekt
        """

        # Baue Query-String
        query_text = requirements.use_case_goal
        
        if usecase_match:
            # Ergänze mit Use-Case Kontext
            top_uc = usecase_match.matched_usecases[0] if usecase_match.matched_usecases else None
            if top_uc:
                query_text += f" (ähnlich zu: {top_uc.usecase_title})"

        # Adjustments anwenden (z.B. top_k erhöhen bei niedriger Confidence)
        if adjustments:
            top_k = adjustments.get("top_k", top_k)

        # Nutze bestehende find_candidate_frameworks Methode mit Timeout
        framework_matches = None
        
        def call_framework_agent():
            nonlocal framework_matches
            try:
                framework_matches = self.framework_agent.find_candidate_frameworks(
                    user_need=query_text,
                    top_k=top_k
                )
            except Exception as e:
                print(f"  (Framework agent error: {e})")
                framework_matches = []
        
        thread = threading.Thread(target=call_framework_agent, daemon=True)
        thread.start()
        thread.join(timeout=5)  # 5 second timeout
        
        if framework_matches is None:
            print("  (Framework agent timeout, using defaults)")
            framework_matches = []

        # Konvertiere zu FrameworkCandidate Objects
        candidates = [
            FrameworkCandidate(
                framework_name=fm.name,
                score=fm.score,
                reason=fm.reason,
                sources=fm.sources or []
            )
            for fm in framework_matches
        ]

        # Berechne Confidence
        confidence = max([c.score for c in candidates]) if candidates else 0.3

        # Zusammenfassung
        summary = self._generate_summary(candidates, requirements)

        return FrameworkCandidates(
            candidates=candidates,
            framework_confidence=confidence,
            summary=summary
        )

    def _generate_summary(self, candidates, requirements: Requirements) -> str:
        """Generiert Summary."""
        if not candidates:
            return "Keine Framework-Kandidaten gefunden."
        
        top = candidates[0]
        automation = requirements.automation_level or "unspecified"
        return f"Top-Framework: {top.framework_name} (Score: {top.score:.2f}). Für {automation} Anforderungen."
