# Framework Advisor - Agent-for-Agents Platform

## 🎯 Übersicht

Die **Framework Advisor** ist eine intelligente Plattform zur Empfehlung von Software-Frameworks für spezifische Use Cases. Sie nutzt ein **Multi-Agent LangGraph System mit Google ADK Integration** zur Orchestrierung und Bosch Use-Case Pool als semantische Referenzbasis.

### ✨ Highlights

- **6 Intelligente Agenten** orchestriert durch LangGraph
- **Google ADK Integration** für strukturierte Agent-Definitionen
- **Bosch Use-Case Pool** (15+ vordefinierte Use Cases)
- **Semantic Matching** via Google GenAI Embeddings + Chroma Vector DB
- **Loop Control** mit Max 2 Iterationen + Quality Gates
- **Feedback System** für kontinuierliches Lernen
- **Dual Interface**: Web-UI (Streamlit) + CLI

---

## 🏗️ System Architektur

### Die 6 Agenten (LangGraph Nodes)

```
START
  ↓
1. RequirementsAgent (A)
   → Parst User-Input zu strukturierten Requirements
  ↓
2. ProfilerAgent (B)
   → Erstellt User-Profil (Skill, Org Context, Risk Tolerance)
  ↓
3. UseCaseAnalyzerAgent (C)
   → Matcht gegen Bosch Use-Case Pool in Chroma
  ↓
4. FrameworkAnalyzerAgent (D)
   → Findet Framework-Kandidaten (nutzt bestehende Agent-Logik)
  ↓
5. DecisionAgent (E)
   → Kombiniert alle Inputs zu finaler Empfehlung
  ↓
6. ControlAgent (F) [Router]
   → Quality Gates + Loop Entscheidungen
       ├─ END → Finish
       ├─ ASK_USER → Zurück zu Requirements
       ├─ RERUN_USECASE → Loop zu Agent C
       └─ RERUN_FRAMEWORK → Loop zu Agent D

MAX 2 ITERATIONEN (Hard Limit)
```

### Loop-Regeln (in ControlAgent)

```python
if iteration_count >= 2:
    return ControlDecision(action=END)  # Hard limit

if usecase_confidence < 0.60:
    return ControlDecision(action=RERUN_USECASE)

if framework_confidence < 0.60:
    return ControlDecision(action=RERUN_FRAMEWORK)

if type_mismatch_detected:
    return ControlDecision(action=RERUN_FRAMEWORK)

if critical_info_missing:
    return ControlDecision(action=ASK_USER)

return ControlDecision(action=END)  # All good
```

### Google ADK Integration

Die ADK Integration ist **sichtbar im Code**:

- **`adk_adapter.py`**: Definiert ADK Agent Struktur für alle 6 Agenten
  - `ADKAgentDefinition`: Kapselt Agent-Definition (Tools, Instructions, Policies)
  - `ADKTool`: Tool-Spezifikation
  - `ADKAgentRuntime`: Execution Context
  - `ADKAgentFactory`: Factory zur Erstellung von ADK Agent Definitions

- Jeder Agent hat eine entsprechende ADK Definition mit:
  - Tools (Input/Output Schemas)
  - Instructions (System Prompts)
  - Knowledge Base IDs (falls relevant)
  - Policies (z.B. quality_gate_enforcement, iteration_limit_2)

---

## 📁 Projektstruktur

```
Google-ADK-Framework/
├── agents/                          # Alle 6 Agenten als separate Module
│   ├── __init__.py
│   ├── requirements_agent.py        # Agent A
│   ├── profiler_agent.py            # Agent B
│   ├── usecase_analyzer_agent.py    # Agent C
│   ├── framework_analyzer_agent.py  # Agent D
│   ├── decision_agent.py            # Agent E
│   └── control_agent.py             # Agent F
│
├── orchestrator/                    # LangGraph Flow
│   ├── __init__.py
│   └── langgraph_flow.py           # Main Flow + Runner
│
├── models/                          # Pydantic Schemas
│   ├── __init__.py
│   └── schemas.py                   # All data models + AdvisorState
│
├── memory/                          # Feedback & Session Management
│   ├── __init__.py
│   └── feedback_store.py            # JSON + Chroma storage
│
├── data/
│   ├── chroma/                      # Chroma persistent DB
│   │   ├── chroma.sqlite3
│   │   └── bosch_usecases/          # Bosch Use Cases Collection
│   ├── feedback/                    # Session Feedback
│   │   └── sessions.jsonl
│   └── bosch_usecases_seed.py       # Use Case Definitions
│
├── my_agent/                        # Bestehendes Code (noch genutzt)
│   ├── agent.py                     # FrameworkAdvisorAgent (Core)
│   ├── doc_loader.py
│   └── framework_docs_config.py
│
├── adk_adapter.py                   # Google ADK Integration
├── main.py                          # CLI Interface
├── streamlit_app.py                 # Web UI
├── requirements.txt                 # Dependencies
├── pyproject.toml                   # Project Config
├── .env                             # API Keys (nicht im Repo)
└── README.md                        # This file
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone/Setup
cd /Users/lenny/Google-ADK-Framework

# Install dependencies
pip install -r requirements.txt

# Oder via pyproject.toml
pip install .
```

### 2. Environment Setup

Erstelle `.env` Datei im Projektroot:

```bash
GOOGLE_API_KEY=your-google-genai-api-key-here
CHROMA_DB_DIR=./data/chroma
```

### 3. Starten

**CLI Mode:**
```bash
python main.py
```

**Web UI (Streamlit):**
```bash
streamlit run streamlit_app.py
```

---

## 📊 Demo & Test Cases

### Test Case 1: RAG Q&A System

**Prompt:**
```
Ich möchte einen Agenten bauen, der über tausende von technischen 
Dokumentationen unsere Bosch-Ingenieur-Teams Q&A beantwortet. 
Der Agent soll relevant Snippets finden und zitieren können.
```

**Erwartete Empfehlung:**
- Top 1: **LangChain** (RAG-Framework)
- Architektur: **AGENTIC_RAG** mit Semantic Search
- Bosch UC Match: "Technical Documentation Q&A Agent"
- Requirements Abgeleitet: `rag_required=True, automation_level=qa_only`

**Run:**
```bash
# In main.py, Wahl 1 (Quick Recommendation)
# Paste prompt above
```

---

### Test Case 2: Compliance & Automation

**Prompt:**
```
Wir brauchen einen vollautomatisierten Workflow, der globale 
Regulatory Changes monitored und unser Compliance Team benachrichtigt. 
Muss Enterprise-ready sein mit Audit Trail.
```

**Erwartete Empfehlung:**
- Top 1: **Google ADK** (Multi-Agent + Enterprise)
- Architektur: **MULTI_AGENT** mit Escalation Pattern
- Bosch UC Match: "Global Regulatory & Standards Compliance Advisor"
- Requirements: `compliance_high=True, automation_high=True, enterprise_needed=True`
- Risks: "Compliance-Audit vor Produktion erforderlich"

**Run:**
```bash
# In main.py, Wahl 2 (Guided Advisory)
# Answer questions
```

---

### Test Case 3: No-Code Automation

**Prompt:**
```
Geschäftsteam möchte Workflow-Automation ohne Programmierung. 
Müssen verschiedene Systeme (SAP, CRM, Email) verbinden.
Skill Level: Anfänger, No-Code Importance: 5/5
```

**Erwartete Empfehlung:**
- Top 1: **n8n** (No-Code Automation)
- Architektur: **SINGLE_AGENT** (wird UI-basiert konfiguriert)
- Bosch UC Match: "New Hires Onboarding Agent"
- Requirements: `no_code_importance=5, automation_level=workflow_automation, connectors_required=True`
- Risks: "Connector-Permissions müssen geklärt werden"

**Run:**
```bash
# In Streamlit: Wahl "Guided Advisory"
# Oder CLI mit main.py → Wahl 2
```

---

## 🔄 Feedback System

### Persistierung

**JSON-basiert** (Standard):
- Datei: `./data/feedback/sessions.jsonl`
- Format: Ein SessionFeedback-JSON pro Zeile
- Enthält: rating (1-5), helpful (bool), comment, timestamp, session_id

**Optional Chroma Collection** (`session_feedback`):
- Embedded feedback text für spätere RAG-Analysen
- Ermöglicht "Learning from Feedback" in Zukunft

### Usage

```python
from memory.feedback_store import FeedbackStore, SessionFeedback

store = FeedbackStore(use_chroma=True)

# Save feedback
feedback = SessionFeedback(
    rating=4,
    helpful=True,
    comment="Good recommendation!",
    session_id="unique-session-id"
)
store.save_feedback(feedback)

# Load statistics
stats = store.get_feedback_stats()
print(f"Average Rating: {stats['average_rating']}")
print(f"Helpful Rate: {stats['helpful_percentage']}%")
```

---

## 🔀 LangGraph Flow Control

### State Management

```python
from models.schemas import AdvisorState
from orchestrator.langgraph_flow import run_advisor_flow

# Run flow
state = run_advisor_flow("My use case description", verbose=True)

# Inspect state
print(f"Requirements: {state.requirements}")
print(f"User Profile: {state.user_profile}")
print(f"Recommendation: {state.recommendation}")
print(f"Iterations: {state.iteration_count}")
```

### Conditional Routing Example

```python
# Im ControlAgent:
def route_from_control(state: AdvisorState) -> str:
    """Entscheidet nächsten Node basierend auf Quality Gates."""
    
    if state.iteration_count >= 2:
        return END  # Hard limit
    
    if state.usecase_match.usecase_confidence < 0.60:
        return "node_usecase_analyzer_agent"  # Loop
    
    if state.framework_candidates.framework_confidence < 0.60:
        return "node_framework_analyzer_agent"  # Loop
    
    return END  # Finish
```

---

## 🏛️ Google ADK Integration Details

### ADK Agent Definitions

Alle 6 Agenten haben ADK-konforme Definitionen:

```python
from adk_adapter import create_all_adk_agent_definitions

adk_agents = create_all_adk_agent_definitions()

for agent_id, agent_def in adk_agents.items():
    print(f"Agent: {agent_def.agent_name}")
    print(f"  Tools: {[t.name for t in agent_def.tools]}")
    print(f"  Policies: {agent_def.policies}")
```

### ADK Concepts Genutzt

1. **Agent Definition**: `ADKAgentDefinition` kapselt Agent-Struktur
2. **Tools**: `ADKTool` mit Input/Output Schemas
3. **Knowledge Bases**: KB IDs für Framework + UseCase Docs
4. **Policies**: Enforcement Policies (quality_gate, iteration_limit)
5. **Runtime**: `ADKAgentRuntime` für Execution Context

### Integration in LangGraph

```python
# Jeder LangGraph Node hat entsprechende ADK Definition
# Beispiel:
from adk_adapter import ADKAgentFactory

factory = ADKAgentFactory()
requirements_adk = factory.create_requirements_agent()

# ADK Definition: Tools, Instructions, Knowledge Bases
# Actual Execution: Python Agent Class + LLM (Google GenAI)
```

---

## 📚 Bosch Use Cases Pool

### Seed Data

Definiert in `data/bosch_usecases_seed.py`:

```python
from data.bosch_usecases_seed import get_all_usecases

usecases = get_all_usecases()
# Returns 15+ Bosch Use Cases with:
# - ID, Title, Description
# - Category, Tags, Challenges
# - Typical Frameworks
```

### Verfügbare Use Cases

1. R&D Innovation & Competitive Intelligence Scout Agent
2. Technical Documentation Q&A Agent
3. Global Regulatory & Standards Compliance Advisor
4. New Hires Onboarding Agent
5. Remote Diagnostics & Guided Repair
6. Proactive Field Service Dispatch & Optimization
7. AI Service Knowledge Navigator
8. Marketing Content Idea & Brief Generator
9. Process Documentation & SOP Generation Assistant
10. Supply Chain Risk & Logistics Optimizer
11. Employee Skills & Talent Marketplace Agent
12. Energy & Sustainability Compliance Reporter
13. Customer Sentiment & Feedback Analyzer
14. Patent & IP Strategy Advisor
15. Manufacturing Quality Control Inspector

### Seeding

```python
from agents.usecase_analyzer_agent import UseCaseAnalyzerAgent

agent = UseCaseAnalyzerAgent()
# Beim Initialisieren automatisch seeded:
agent.seed_bosch_usecases()

# Oder manuell:
# Chroma Collection "bosch_usecases" wird mit Embeddings gefüllt
```

---

## 🔧 Development

### Adding a New Framework

1. Füge zu `framework_docs_config.py` hinzu:
```python
FRAMEWORK_DOCUMENTATION_URLS = {
    "Your Framework": [
        {"title": "...", "url": "...", "source": "official"}
    ]
}
```

2. Framework wird automatisch in `seed_basic_framework_knowledge()` genutzt

### Modifying Loop Rules

Edit `agents/control_agent.py`:

```python
def decide_continuation(self, state: AdvisorState) -> ControlDecision:
    # Modify conditions here
    if custom_condition:
        return ControlDecision(action=ControlAction.RERUN_USECASE, ...)
```

### Adding New Bosch Use Cases

Füge zu `data/bosch_usecases_seed.py` hinzu:

```python
BOSCH_USECASES.append({
    "id": "bosch_uc_016",
    "title": "Your Use Case",
    "category": "Category",
    "description": "...",
    "tags": ["rag_required", ...],
    "challenges": [...],
    "frameworks_commonly_used": [...]
})
```

---

## 📊 Monitoring & Debugging

### Verbose Mode

```bash
# CLI mit verbose output
python main.py
# Wahl 1 → Verbose Ausgabe der Agent-Schritte

# Oder in Code:
state = run_advisor_flow("prompt", verbose=True)
```

### Logs & History

```python
# State speichert message history
state.messages_history  # List of agent messages

# Feedback statistics
from memory.feedback_store import FeedbackStore
store = FeedbackStore()
stats = store.get_feedback_stats()
```

### Chroma Collections

```python
import chromadb
client = chromadb.PersistentClient(path="./data/chroma")

# Available collections:
collections = client.list_collections()
# ['framework_docs', 'bosch_usecases', 'session_feedback']
```

---

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not set"

```bash
# Stelle sicher dass .env in Projektroot ist:
echo "GOOGLE_API_KEY=your-key" > .env
```

### Chroma Collection Error

```python
# Manuell seeden:
from agents.usecase_analyzer_agent import UseCaseAnalyzerAgent
agent = UseCaseAnalyzerAgent()
agent.seed_bosch_usecases()
```

### LangGraph Import Error

```bash
pip install langgraph
pip install langchain
```

---

## 📈 Performance

### Typical Flow Time

- Without Loops: ~5-10 seconds (all 6 agents)
- With 1 Loop: ~10-15 seconds
- Max 2 Iterations: Hard capped at 2 loops

### Cost (Google GenAI)

- Embeddings: ~$0.02 per 1M tokens
- LLM Calls: ~$0.10 per 1M input tokens (Gemini 2.5 Flash)
- Typical Session: <$0.01 USD

---

## 📝 API Reference

### Main Entry Point

```python
from orchestrator.langgraph_flow import run_advisor_flow

state = run_advisor_flow(
    user_input="Describe your use case",
    verbose=True  # Print detailed logs
)
# Returns: AdvisorState with Recommendation
```

### Agent Classes

```python
from agents import (
    RequirementsAgent,
    ProfilerAgent,
    UseCaseAnalyzerAgent,
    FrameworkAnalyzerAgent,
    DecisionAgent,
    ControlAgent
)

# Each agent can be used independently:
req_agent = RequirementsAgent()
requirements = req_agent.parse_user_input("...")
```

### Models

```python
from models.schemas import (
    AdvisorState,
    Requirements,
    UserProfile,
    UseCaseMatch,
    FrameworkCandidates,
    Recommendation,
    ControlDecision,
    SessionFeedback
)
```

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Add tests
4. Submit PR

---

## 📄 License

Proprietary - Bosch 2026

---

## 👥 Authors

- Framework Advisor Team
- Powered by: LangGraph, Google GenAI, Chroma, Streamlit

---

## 📞 Support

For issues or questions:
- Check troubleshooting section
- Review logs in `./data/feedback/`
- Inspect Chroma collections

---

**Last Updated:** January 17, 2026
