"""
CLI Interface für Framework Advisor
Nutzt LangGraph Flow für Orchestrierung.

Starten mit:
  python main.py                    # Menü
  streamlit run streamlit_app.py    # Web UI
"""

from orchestrator.langgraph_flow import run_advisor_flow, print_flow_architecture
from memory.feedback_store import FeedbackStore, SessionFeedback
from adk_adapter import print_adk_agent_definitions


# ============================================================================
# Helper Functions
# ============================================================================

def print_header(title: str) -> None:
    """Druckt einen schönen Header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_recommendation(state) -> None:
    """Druckt die Empfehlung schön formatiert."""
    if not state.recommendation:
        print("\n❌ Keine Empfehlung generiert.")
        return

    rec = state.recommendation

    print("\n" + "-" * 70)
    print("✨ HAUPT-EMPFEHLUNG")
    print("-" * 70)
    print(f"Framework: {rec.recommended_framework}")
    print(f"Score: {rec.recommended_score:.2f}")
    print()
    print("Begründung:")
    print(rec.reasoning_summary)
    print()

    print("-" * 70)
    print("🏆 TOP 3 ALTERNATIVEN")
    print("-" * 70)
    for i, candidate in enumerate(rec.top_3, 1):
        print(f"{i}. {candidate.framework_name} ({candidate.score:.2f})")
        print(f"   → {candidate.reason[:100]}...")
        print()

    if rec.matched_bosch_usecases:
        print("-" * 70)
        print("🔗 GEMATCHTЕ BOSCH USE CASES")
        print("-" * 70)
        for uc in rec.matched_bosch_usecases[:3]:
            print(f"• {uc.usecase_title}")
            print(f"  Category: {uc.category} | Match: {uc.match_score:.2f}")
        print()

    if rec.architecture_suggestion:
        print("-" * 70)
        print("🏗️ ARCHITEKTUR VORSCHLAG")
        print("-" * 70)
        arch = rec.architecture_suggestion
        print(f"Type: {arch.agent_type}")
        print(f"RAG Required: {arch.requires_rag}")
        print(f"Tools/Connectors: {arch.requires_tools}")
        print(f"Human Escalation: {arch.requires_escalation}")
        print(f"Notes: {arch.notes}")
        print()

    if rec.assumptions:
        print("-" * 70)
        print("📋 ASSUMPTIONS")
        print("-" * 70)
        for assumption in rec.assumptions:
            print(f"✓ {assumption}")
        print()

    if rec.risks:
        print("-" * 70)
        print("⚠️ IDENTIFIZIERTE RISIKEN")
        print("-" * 70)
        for risk in rec.risks:
            print(f"⚠️ {risk}")
        print()

    print(f"Iterationen: {state.iteration_count}/2")
    print("-" * 70)


def print_menu() -> None:
    """Druckt das Hauptmenü."""
    print("\n" + "=" * 70)
    print("🤖 Framework Advisor - Multi-Agent LangGraph System")
    print("=" * 70)
    print("\nWie möchtest du einen Framework auswählen?")
    print()
    print("  1️⃣  Schnelle Empfehlung")
    print("      → Gib einfach deinen Use-Case ein, erhalte eine Empfehlung")
    print()
    print("  2️⃣  Geführte Beratung")
    print("      → Ich stelle dir gezielte Fragen für eine bessere Empfehlung")
    print()
    print("  3️⃣  System Architektur anzeigen")
    print("      → Zeige LangGraph Flow + ADK Agent Definitions")
    print()
    print("  0️⃣  Beenden")
    print()
    print("=" * 70)


def get_user_choice() -> str:
    """Liest die Nutzereingabe."""
    choice = input("Deine Wahl (1/2/3/0): ").strip().lower()
    return choice


# ============================================================================
# Beratungs-Modi
# ============================================================================

def quick_recommendation_flow() -> None:
    """
    Schnelle Empfehlung: Der Nutzer gibt einen Use-Case ein,
    erhält eine Framework-Empfehlung via LangGraph Flow.
    """
    print_header("🚀 SCHNELLE EMPFEHLUNG")

    print("\nBeschreibe kurz, was du bauen möchtest:")
    print("(z.B. 'Ich brauche einen RAG-Agent für technische Fragen')")
    print()

    user_need = input("📝 Dein Use-Case: ").strip()

    if not user_need:
        print("❌ Bitte geben Sie einen Use-Case ein.")
        return

    print()
    print("🔄 Starte 6-Agent LangGraph Flow...")
    print("   RequirementsAgent → ProfilerAgent → UseCaseAnalyzer")
    print("   → FrameworkAnalyzer → DecisionAgent → ControlAgent")
    print()

    try:
        # Führe LangGraph Flow aus
        state = run_advisor_flow(user_need, verbose=True)

        # Drucke Empfehlung
        print_recommendation(state)

        # Handle Loops falls nötig
        if state.control_decision:
            action_value = state.control_decision.action.value if hasattr(state.control_decision.action, 'value') else str(state.control_decision.action)
            if action_value == "ask_user":
                print("❓ Zusätzliche Frage für bessere Empfehlung:")
                print(state.control_decision.user_question)
                additional_input = input("📝 Deine Antwort: ").strip()
                if additional_input:
                    # Re-run mit zusätzlichem Input
                    combined_input = f"{user_need}\n\nZusätzliche Info: {additional_input}"
                    state = run_advisor_flow(combined_input, verbose=False)
                    print_recommendation(state)

        # Feedback sammeln
        print_feedback_form(state)

    except Exception as e:
        print(f"❌ Fehler bei der Empfehlung: {e}")
        import traceback
        traceback.print_exc()


def guided_advisory_flow() -> None:
    """
    Geführte Beratung: Ein strukturierter Fragebogen hilft dabei,
    den besten Framework zu finden. Nutzt LangGraph Flow dahinter.
    """
    print_header("🎯 GEFÜHRTE BERATUNG")

    print("\nIch stelle dir einige Fragen, um die beste Empfehlung zu geben.")
    print("Beantworte sie so genau wie möglich!\n")

    # Frage 1: Was möchtest du bauen?
    print("❓ Frage 1/6")
    print("-" * 70)
    print("Was möchtest du grob bauen?")
    print("(z.B. 'Workflow-Automatisierung', 'Chatbot', 'Multi-Agent-System')")
    use_case = input("📝 Deine Antwort: ").strip()

    if not use_case:
        use_case = "Nicht spezifiziert"

    # Frage 2: Technischer Hintergrund
    print("\n❓ Frage 2/6")
    print("-" * 70)
    print("Wie ist dein technischer Hintergrund?")
    print("  1) Kein Code / Anfänger")
    print("  2) Etwas Python / JavaScript")
    print("  3) Erfahrene*r Entwickler*in")
    print("  4) DevOps / Infrastructure")
    tech_background = input("🎓 Wähle (1-4): ").strip()

    background_map = {
        "1": "Kein Code / Anfänger",
        "2": "Etwas Python / JavaScript",
        "3": "Erfahrene*r Entwickler*in",
        "4": "DevOps / Infrastructure"
    }
    tech_background = background_map.get(tech_background, "Nicht spezifiziert")

    # Frage 3: No-Code/Low-Code Wichtigkeit
    print("\n❓ Frage 3/6")
    print("-" * 70)
    print("Wie wichtig ist No-Code / Low-Code für dich?")
    print("(1 = völlig unwichtig, 5 = absolut notwendig)")
    no_code_importance = input("📊 Wert (1-5): ").strip()
    try:
        no_code_importance = int(no_code_importance)
        if no_code_importance < 1 or no_code_importance > 5:
            no_code_importance = 3
    except ValueError:
        no_code_importance = 3

    # Frage 4: Automation Level
    print("\n❓ Frage 4/6")
    print("-" * 70)
    print("Welche Art von Automatisierung brauchst du?")
    print("  1) Q&A / Nur Informationen bereitstellen")
    print("  2) Tool Actions / APIs aufrufen")
    print("  3) Komplexe Workflows / Multi-Step Automatisierung")
    automation_level = input("⚙️ Wähle (1-3): ").strip()

    automation_map = {
        "1": "qa_only",
        "2": "tool_actions",
        "3": "workflow_automation"
    }
    automation_level = automation_map.get(automation_level, "qa_only")

    # Frage 5: Enterprise
    print("\n❓ Frage 5/6")
    print("-" * 70)
    enterprise = input("🏢 Enterprise Features erforderlich? (j/n): ").strip().lower() == "j"

    # Frage 6: Budget/Constraints
    print("\n❓ Frage 6/6")
    print("-" * 70)
    constraints = input("⛓️ Constraints (z.B. GDPR, Real-Time, Cost-Effective): ").strip()

    # Kombiniere zu Input für LangGraph
    full_input = f"""
Use Case: {use_case}
Technical Background: {tech_background}
No-Code Importance: {no_code_importance}/5
Automation Level: {automation_level}
Enterprise Needed: {enterprise}
Constraints: {constraints if constraints else 'None'}
"""

    print()
    print("🔄 Starte LangGraph Flow mit Antworten...")
    print()

    try:
        state = run_advisor_flow(full_input, verbose=True)
        print_recommendation(state)
        print_feedback_form(state)

    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


def print_feedback_form(state) -> None:
    """Sammelt Feedback nach einer Session."""
    print()
    print("=" * 70)
    print("📝 FEEDBACK")
    print("=" * 70)

    rating = input("Wie hilfreich war die Empfehlung? (1-5): ").strip()
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            rating = 3
    except ValueError:
        rating = 3

    helpful = input("Würdest du diese Empfehlung verwenden? (j/n): ").strip().lower() == "j"

    comment = input("Kommentar (optional, Enter zum überspringen): ").strip()

    feedback = SessionFeedback(
        rating=rating,
        helpful=helpful,
        comment=comment if comment else None,
        session_id=state.session_id
    )

    store = FeedbackStore()
    store.save_feedback(feedback)

    print()
    print("✓ Feedback gespeichert! Danke für dein Input.")


# ============================================================================
# Main Entry Point
# ============================================================================

def main() -> None:
    """Hauptfunktion - CLI Loop."""
    while True:
        print_menu()
        choice = get_user_choice()

        if choice == "1":
            quick_recommendation_flow()
        elif choice == "2":
            guided_advisory_flow()
        elif choice == "3":
            print_flow_architecture()
            print("\n")
            print_adk_agent_definitions()
        elif choice == "0":
            print("\n👋 Auf Wiedersehen!\n")
            break
        else:
            print("\n❌ Ungültige Eingabe. Bitte versuche es erneut.\n")


if __name__ == "__main__":
    main()
