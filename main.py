"""
Agentic AI Framework Advisor - CLI mit Menü und geführter Beratung
Ein Command-Line Interface für intelligente Framework-Empfehlungen.
"""

from my_agent.agent import FrameworkAdvisorAgent, FrameworkMatch, FrameworkMultiScore, format_multi_score_report


# ============================================================================
# Hilfsfunktionen
# ============================================================================

def print_header(title: str) -> None:
    """Druckt einen schönen Header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_recommendation(match: FrameworkMatch) -> None:
    """Druckt eine schöne Haupt-Empfehlung."""
    print("\n" + "-" * 70)
    print("✨ HAUPT-EMPFEHLUNG")
    print("-" * 70)
    print(f"Framework: {match.name}")
    print(f"Score: {match.score:.2f}")
    print()
    print("Begründung:")
    print(match.reason)
    print()

    # Quellen anzeigen (falls vorhanden)
    if match.sources:
        print("-" * 70)
        print("📚 Genutzte Wissens-Snippets")
        print("-" * 70)
        for i, source in enumerate(match.sources, 1):
            framework = source.get("framework", "N/A")
            doc_preview = source.get("document", "N/A")

            # Kurze Vorschau (erste 100 Zeichen)
            if len(doc_preview) > 100:
                doc_preview = doc_preview[:100] + "..."

            print(f"{i}. {framework}")
            print(f"   → {doc_preview}")
            print()


def print_multi_criteria_summary(multi_scores: list[FrameworkMultiScore]) -> None:
    """Druckt eine Zusammenfassung der Multi-Kriterien-Bewertung."""
    if not multi_scores:
        print("⚠ Keine Multi-Kriterien-Bewertung verfügbar.")
        return

    print("\n" + "-" * 70)
    print("📊 DETAILLIERTE MULTI-KRITERIEN-BEWERTUNG")
    print("-" * 70)

    criteria_labels = {
        "ease_of_use": "Benutzerfreundlichkeit",
        "community": "Community & Support",
        "performance": "Performance",
        "learning_curve": "Lernkurve",
        "flexibility": "Flexibilität",
        "enterprise_ready": "Enterprise-Readiness"
    }

    for i, score in enumerate(multi_scores, 1):
        print(f"\n{i}. {score.name}")
        print(f"   Overall Score: {score.overall_score:.2f} / 1.00")
        print("\n   Bewertung nach Kriterien:")

        for criterion, value in score.criteria_scores.items():
            label = criteria_labels.get(criterion, criterion)
            bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            print(f"   • {label:.<35} {bar} {value:.2f}")

        print(f"\n   💡 {score.summary}")

    print("\n" + "-" * 70)


def print_menu() -> None:
    """Druckt das Hauptmenü."""
    print("\n" + "=" * 70)
    print("🔧 Agentic AI Framework Advisor - Hauptmenü")
    print("=" * 70)
    print("\nWie möchtest du einen Framework auswählen?")
    print()
    print("  1️⃣  Schnelle Empfehlung")
    print("      → Gib einfach deinen Use-Case ein, erhalte eine Empfehlung")
    print()
    print("  2️⃣  Geführte Beratung")
    print("      → Ich stelle dir gezielte Fragen für eine bessere Empfehlung")
    print()
    print("  0️⃣  Beenden")
    print()
    print("=" * 70)


def get_user_choice() -> str:
    """Liest die Nutzereingabe."""
    choice = input("Deine Wahl (1/2/0): ").strip().lower()
    return choice


# ============================================================================
# Beratungs-Modi
# ============================================================================

def quick_recommendation_flow(agent: FrameworkAdvisorAgent) -> None:
    """
    Schnelle Empfehlung: Der Nutzer gibt einen Use-Case ein,
    erhält eine Framework-Empfehlung.
    """
    print_header("🚀 SCHNELLE EMPFEHLUNG")

    print("\nBeschreibe kurz, was du bauen möchtest:")
    print("(z.B. 'Ich brauche eine Automation ohne Programmierung')")
    print()

    user_need = input("📝 Dein Use-Case: ").strip()

    if not user_need:
        print("❌ Bitte geben Sie einen Use-Case ein.")
        return

    print()
    print("🔍 Analysiere deine Anfrage...")
    print()

    try:
        # Haupt-Empfehlung
        match = agent.choose_framework(user_need)
        print_recommendation(match)

        # Multi-Kriterien-Bewertung
        multi_scores = agent.evaluate_frameworks_multi_criteria(user_need)
        if multi_scores:
            report = format_multi_score_report(multi_scores)
            print(report)

        print("\n✓ Empfehlung abgeschlossen.")

    except Exception as e:
        print(f"❌ Fehler bei der Empfehlung: {e}")
        import traceback
        traceback.print_exc()


def guided_advisory_flow(agent: FrameworkAdvisorAgent) -> None:
    """
    Geführte Beratung: Ein strukturierter Fragebogen hilft dabei,
    den besten Framework zu finden.
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

    # Frage 4: Multi-Agent/Orchestrierung Wichtigkeit
    print("\n❓ Frage 4/6")
    print("-" * 70)
    print("Wie wichtig ist Multi-Agent-Fähigkeit / Orchestrierung?")
    print("(1 = nicht wichtig, 5 = sehr wichtig)")
    multi_agent_importance = input("� Wert (1-5): ").strip()
    try:
        multi_agent_importance = int(multi_agent_importance)
        if multi_agent_importance < 1 or multi_agent_importance > 5:
            multi_agent_importance = 3
    except ValueError:
        multi_agent_importance = 3

    # Frage 5: Visuelle Workflows
    print("\n❓ Frage 5/6")
    print("-" * 70)
    print("Möchtest du visuelle Workflows (Drag & Drop Interface)?")
    print("  j) Ja, sehr wichtig")
    print("  n) Nein, nicht nötig")
    visual_workflows = input("🎨 Deine Wahl (j/n): ").strip().lower()
    visual_workflows_text = "Ja" if visual_workflows in ["j", "yes", "y"] else "Nein"

    # Frage 6: Deployment-Ziel
    print("\n❓ Frage 6/6")
    print("-" * 70)
    print("Wo soll die Lösung laufen?")
    print("  1) Cloud (AWS, GCP, Azure)")
    print("  2) On-Premise (eigene Server)")
    print("  3) Egal / Flexibel")
    deployment = input("☁️  Wähle (1-3): ").strip()

    deployment_map = {
        "1": "Cloud (AWS, GCP, Azure)",
        "2": "On-Premise (eigene Server)",
        "3": "Egal / Flexibel"
    }
    deployment = deployment_map.get(deployment, "Egal / Flexibel")

    # Zusammenfassung bauen
    print("\n" + "=" * 70)
    print("📋 Zusammenfassung deiner Anforderungen")
    print("=" * 70)
    print(f"Use-Case: {use_case}")
    print(f"Technischer Hintergrund: {tech_background}")
    print(f"No-Code/Low-Code Wichtigkeit: {no_code_importance}/5")
    print(f"Multi-Agent/Orchestrierung Wichtigkeit: {multi_agent_importance}/5")
    print(f"Visuelle Workflows gewünscht: {visual_workflows_text}")
    print(f"Deployment-Ziel: {deployment}")
    print("=" * 70)

    # Reichhaltigen user_need String bauen
    user_need = f"""
Use-Case:
{use_case}

Nutzerprofil:
- Technischer Hintergrund: {tech_background}
- Wichtigkeit No-Code/Low-Code (1-5): {no_code_importance}
- Wichtigkeit Multi-Agent/Orchestrierung (1-5): {multi_agent_importance}
- Wunsch nach visuellen Workflows: {visual_workflows_text}
- Ziel-Plattform / Deployment: {deployment}
"""

    print("\n🔍 Analysiere deine Anforderungen...")
    print()

    try:
        # Haupt-Empfehlung
        match = agent.choose_framework(user_need)
        print_recommendation(match)

        # Multi-Kriterien-Bewertung
        multi_scores = agent.evaluate_frameworks_multi_criteria(user_need)
        if multi_scores:
            print_multi_criteria_summary(multi_scores)

        print("\n✓ Beratung abgeschlossen.")

    except Exception as e:
        print(f"❌ Fehler bei der Beratung: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# Hauptfunktion
# ============================================================================

def main() -> None:
    """
    Hauptfunktion des Framework Advisors.

    - Agent initialisieren
    - Wissensbasis füllen
    - Menü-Loop für Benutzerinteraktion
    """
    print("=" * 70)
    print("🔧 Agentic AI Framework Advisor")
    print("=" * 70)
    print()

    # Agent initialisieren
    try:
        agent = FrameworkAdvisorAgent()
    except RuntimeError as e:
        print(f"❌ Fehler beim Initialisieren des Agenten: {e}")
        return

    # Wissensbasis füllen (nur einmalig nötig)
    # Auskommentieren nach der ersten Ausführung, wenn die DB schon gefüllt ist:
    try:
        agent.seed_basic_framework_knowledge()
        print("✓ Wissensbasis geladen")
        print()
    except Exception as e:
        print(f"⚠ Warnung: Fehler beim Laden der Seed-Daten: {e}")
        print("  Die bestehende Wissensbasis wird verwendet.")
        print()

    # Menü-Loop
    while True:
        print_menu()
        choice = get_user_choice()

        if choice in ["0", "q", "quit", "exit", "beenden"]:
            print("\n👋 Auf Wiedersehen! Viel Erfolg mit deinem Framework!")
            break

        elif choice == "1":
            quick_recommendation_flow(agent)
            input("\n[Drücke Enter um ins Menü zurückzukehren]")

        elif choice == "2":
            guided_advisory_flow(agent)
            input("\n[Drücke Enter um ins Menü zurückzukehren]")

        else:
            print("\n❌ Ungültige Eingabe. Bitte wähle 0, 1 oder 2.")
            input("\n[Drücke Enter um weiterzumachen]")


if __name__ == "__main__":
    main()
