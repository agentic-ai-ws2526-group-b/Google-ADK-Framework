"""
Bosch Real Use Cases - PoC Reference Pool
Aus internen Bosch PoCs. Dienen als Referenz für typische Agent-Anforderungen.
Die Plattform nutzt diese Use Cases, um geeignete Agent-Frameworks zu empfehlen.
"""

def get_all_usecases():
    """Liefert alle 15 Bosch Use Cases aus internen PoCs."""
    return [
        {
            "id": "bosch_uc_001",
            "title": "R&D Innovation & Competitive Intelligence Scout Agent",
            "category": "Research & Intelligence",
            "description": "Agent zur Recherche und Zusammenfassung von Markt-, Wettbewerbs- und Technologietrends für R&D-Teams.",
            "tags": ["research", "summarization", "web", "trend-analysis", "competitive-intelligence"],
            "challenges": [
                "Große Mengen an Web-Daten filtern",
                "Relevanz-Bewertung von Trends",
                "Regelmäßige Updates und Monitoring"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "CrewAI"]
        },
        {
            "id": "bosch_uc_002",
            "title": "Technical Documentation Q&A Agent",
            "category": "Knowledge Management",
            "description": "Agent beantwortet Fragen auf Basis technischer Dokumentationen (z.B. PDFs, Handbücher, interne Wissensdaten).",
            "tags": ["rag", "knowledge_management", "documentation", "qa", "connectors"],
            "challenges": [
                "Große PDF/Dokument-Mengen",
                "Hohe Antwortqualität erforderlich",
                "Quellen-Transparenz und Nachvollziehbarkeit"
            ],
            "typical_frameworks": ["LangChain", "LlamaIndex", "Google ADK"]
        },
        {
            "id": "bosch_uc_003",
            "title": "Global Regulatory & Standards Compliance Advisor",
            "category": "Compliance & Governance",
            "description": "Agent unterstützt bei regulatorischen Fragen und Normen (z.B. ISO, interne Standards).",
            "tags": ["compliance", "standards", "rag", "enterprise", "governance"],
            "challenges": [
                "Hohe Zuverlässigkeit erforderlich",
                "Regulatorisches Wissen aktuell halten",
                "Quellen-Nachvollziehbarkeit und Audit-Trail"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "LlamaIndex"]
        },
        {
            "id": "bosch_uc_004",
            "title": "New Hires Onboarding Agent",
            "category": "Human Resources",
            "description": "Agent führt neue Mitarbeiter durch Onboarding-Prozess, beantwortet HR-Fragen, erklärt Prozesse.",
            "tags": ["onboarding", "hr", "qa", "conversational", "human-resources"],
            "challenges": [
                "Personalisierte Antworten für verschiedene Departments",
                "Integration mit HR-Systemen",
                "Mehrsprachige Unterstützung"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "Rasa"]
        },
        {
            "id": "bosch_uc_005",
            "title": "Remote Diagnostics & Guided Repair Agent",
            "category": "Service & Support",
            "description": "Agent diagnostiziert Probleme remote und führt Kunden durch Reparaturschritte.",
            "tags": ["diagnostics", "repair", "guidance", "support", "automation"],
            "challenges": [
                "Kontextuales Verständnis von Fehlern",
                "Iterative Diagnose-Prozesse",
                "Integration mit Sensor-Daten"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "LangGraph"]
        },
        {
            "id": "bosch_uc_006",
            "title": "Proactive Field Service Dispatch & Optimization Agent",
            "category": "Operations & Automation",
            "description": "Agent optimiert Einsatzplanung von Technikern, prädiktive Wartung, Route-Optimierung.",
            "tags": ["field-service", "optimization", "automation", "scheduling", "routing"],
            "challenges": [
                "Echtzeit-Daten-Integration",
                "Komplexe Optimierungsprobleme",
                "Multi-Criteria Decision Making"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "AutoGPT"]
        },
        {
            "id": "bosch_uc_007",
            "title": "AI Service Knowledge Navigator",
            "category": "Service & Support",
            "description": "Agent navigiert durch interne Service-Knowledge-Base, findet schnell Lösungen für Techniker.",
            "tags": ["knowledge", "navigator", "search", "rag", "service"],
            "challenges": [
                "Große heterogene Datenquellen",
                "Schnelle Antworten erforderlich",
                "Domain-spezifisches Verständnis"
            ],
            "typical_frameworks": ["LlamaIndex", "LangChain", "Google ADK"]
        },
        {
            "id": "bosch_uc_008",
            "title": "Marketing Content Idea & Brief Generator",
            "category": "Marketing & Content",
            "description": "Agent generiert Marketing-Content-Ideen und Briefs auf Basis von Kampagnen-Zielen.",
            "tags": ["content-generation", "marketing", "creative", "automation"],
            "challenges": [
                "Brand-Voice Konsistenz",
                "Kreative Ausgaben-Qualität",
                "Multiple-Output-Variationen"
            ],
            "typical_frameworks": ["LangChain", "Google ADK"]
        },
        {
            "id": "bosch_uc_009",
            "title": "Process Documentation & SOP Generation Assistant",
            "category": "Documentation & Process",
            "description": "Agent erstellt Prozessbeschreibungen und Standard Operating Procedures.",
            "tags": ["documentation", "process", "sop", "generation", "automation"],
            "challenges": [
                "Strukturierte Dokument-Generierung",
                "Konsistente Formatierung über Prozesse",
                "Verständlichkeit für verschiedene Zielgruppen"
            ],
            "typical_frameworks": ["LangChain", "Google ADK"]
        },
        {
            "id": "bosch_uc_010",
            "title": "Customer Support & Service Desk Agent",
            "category": "Service & Support",
            "description": "Agent als First-Level Support, beantwortet häufige Fragen, eskaliert komplexe Fälle.",
            "tags": ["support", "chatbot", "escalation", "ticketing", "customer-service"],
            "challenges": [
                "Natürliche Konversation über längere Kontexte",
                "Nahtlose Eskalation zu Humans",
                "Sentiment-Erkennung und Prioritization"
            ],
            "typical_frameworks": ["LangChain", "Rasa", "Google ADK"]
        },
        {
            "id": "bosch_uc_011",
            "title": "Sales & Pre-Sales Knowledge Assistant",
            "category": "Sales & Business Development",
            "description": "Agent unterstützt Sales-Team mit Produktinformationen, Konfigurationen, Pricing-Szenarien.",
            "tags": ["sales", "knowledge", "product-info", "rag", "configurator"],
            "challenges": [
                "Aktuelle Pricing und Verfügbarkeit",
                "Komplexe Produkt-Konfigurationen",
                "Wettbewerbs-Vergleiche"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "LlamaIndex"]
        },
        {
            "id": "bosch_uc_012",
            "title": "Quality Management & Audit Support Agent",
            "category": "Quality & Compliance",
            "description": "Agent unterstützt Quality-Teams bei Audit-Vorbereitung, Standards-Compliance-Checks.",
            "tags": ["quality", "audit", "compliance", "qa", "standards"],
            "challenges": [
                "Präzise Compliance-Interpretationen",
                "Audit-Trail und Dokumentation",
                "Mehrsprachige Standards-Daten"
            ],
            "typical_frameworks": ["LangChain", "Google ADK"]
        },
        {
            "id": "bosch_uc_013",
            "title": "Manufacturing Process Optimization Agent",
            "category": "Operations & Automation",
            "description": "Agent analysiert Manufacturing-Prozesse, optimiert Effizienz, identifiziert Bottlenecks.",
            "tags": ["manufacturing", "optimization", "analytics", "automation", "iot"],
            "challenges": [
                "Echtzeit-Sensor-Daten-Streaming",
                "Komplexe Prozess-Interdependenzen",
                "Predictive Maintenance Integration"
            ],
            "typical_frameworks": ["LangChain", "Google ADK", "AutoGPT"]
        },
        {
            "id": "bosch_uc_014",
            "title": "Supply Chain Risk Monitoring Agent",
            "category": "Operations & Automation",
            "description": "Agent monitort Supply-Chain, identifiziert Risiken, schlägt Mitigations-Maßnahmen vor.",
            "tags": ["supply-chain", "risk", "monitoring", "analytics", "alerting"],
            "challenges": [
                "Multiple externe Datenquellen",
                "Geopolitisches und Markt-Context",
                "Proaktive Alert-Strategien"
            ],
            "typical_frameworks": ["LangChain", "Google ADK"]
        },
        {
            "id": "bosch_uc_015",
            "title": "Internal IT Helpdesk Agent",
            "category": "Human Resources",
            "description": "Agent als Internal IT Support, beantwortet Tech-Fragen, unterstützt bei Troubleshooting.",
            "tags": ["it-support", "helpdesk", "troubleshooting", "qa", "internal"],
            "challenges": [
                "Integration mit IT-Ticketing-System",
                "Verschiedene OS und Applikationen",
                "Schnelle Response-Zeiten erforderlich"
            ],
            "typical_frameworks": ["LangChain", "Rasa", "Google ADK"]
        }
    ]


def get_usecases_by_category(category: str):
    """Liefert Use Cases für eine bestimmte Kategorie."""
    all_usecases = get_all_usecases()
    return [uc for uc in all_usecases if uc.get("category") == category]
