# Quick Start Guide - Framework Advisor

## 🚀 5-Minuten Setup

### 1. Prerequisites

- Python 3.10+
- Google GenAI API Key (kostenlos: https://ai.google.dev)

### 2. Install

```bash
cd /Users/lenny/Google-ADK-Framework
pip install -r requirements.txt
```

### 3. Configure

```bash
# Create .env file in project root
cat > .env << EOF
GOOGLE_API_KEY=your-api-key-here
CHROMA_DB_DIR=./data/chroma
EOF
```

### 4. Run

**Web UI (empfohlen für Anfänger):**
```bash
streamlit run streamlit_app.py
# Öffnet http://localhost:8501
```

**CLI (für Power Users):**
```bash
python main.py
# Menü mit 3 Optionen
```

---

## 📋 Demo Cases - Copy & Paste Ready

### Demo 1: RAG Q&A System (Leicht)

**Schwierigkeit:** ⭐ Easy  
**Expected Loop Iterations:** 0 (direkt END)

**Prompt zum kopieren:**
```
Ich möchte einen Agenten bauen, der über tausende von 
technischen Dokumentationen unsere Bosch-Ingenieur-Teams 
Q&A beantwortet. Der Agent soll relevant Snippets finden 
und zitieren können.
```

**Was passiert:**
1. RequirementsAgent: Erkennt `rag_required=True, automation_level=qa_only`
2. ProfilerAgent: User ist technisch (Expert implied)
3. UseCaseAnalyzerAgent: Matcht zu "Technical Documentation Q&A Agent" (score ~0.85)
4. FrameworkAnalyzerAgent: Top = LangChain (RAG-optimiert)
5. DecisionAgent: Empfieht LangChain, Architektur=AGENTIC_RAG
6. ControlAgent: `usecase_confidence=0.85 > 0.60, framework_confidence=0.90 > 0.60` → END

**Ergebnis:**
```
✨ HAUPT-EMPFEHLUNG
Framework: LangChain / LangGraph
Score: 0.90

Architektur: AGENTIC_RAG
  - RAG Required: True
  - Tools: False
  - Escalation: False
  
Matched Bosch Use Cases:
  • Technical Documentation Q&A Agent (0.85)

Assumptions:
  ✓ Dokumentation ist zeitnah verfügbar
  ✓ Team hat Zugang zu erforderlichen Datenquellen
```

**How to run:**
```bash
# Option A: CLI
python main.py
# Wahl: 1 (Quick Recommendation)
# Paste prompt above

# Option B: Web UI
streamlit run streamlit_app.py
# Click "Quick Recommendation"
# Paste prompt
```

---

### Demo 2: Compliance & Automation (Mittelschwer)

**Schwierigkeit:** ⭐⭐ Medium  
**Expected Loop Iterations:** 1 (framework_confidence < 0.60, RERUN_FRAMEWORK)

**Prompt zum kopieren:**
```
Wir brauchen einen vollautomatisierten Workflow, der globale 
Regulatory Changes monitored und unser Compliance Team 
benachrichtigt. Muss Enterprise-ready sein mit Audit Trail 
und Approval Workflows.
```

**Was passiert:**
1. RequirementsAgent: Erkennt `compliance_high=True, automation_level=workflow_automation, enterprise_needed=True`
2. ProfilerAgent: Enterprise Context, Medium-High Risk Tolerance
3. UseCaseAnalyzerAgent: Matcht zu "Global Regulatory & Standards Compliance Advisor" (score ~0.80)
   - Derived: `compliance_high=True, rag_required=True`
4. FrameworkAnalyzerAgent: Top candidates = Google ADK, LangGraph (score ~0.65)
5. ControlAgent: `framework_confidence=0.65 > 0.60` BUT `automation_high & compliance_high` → Type Mismatch Check
   - Mismatch: "Automation High + Enterprise Compliance benötigt stärker ADK als LangChain"
   - Action: **RERUN_FRAMEWORK** mit `adjustments={"top_k": 8}`
6. FrameworkAnalyzerAgent (RERUN): Jetzt Top = Google ADK (score ~0.92)
7. DecisionAgent: Empfieht Google ADK, Architektur=MULTI_AGENT
8. ControlAgent: Confidence jetzt >0.80 → **END**

**Ergebnis:**
```
✨ HAUPT-EMPFEHLUNG
Framework: Google ADK
Score: 0.92

Architektur: MULTI_AGENT
  - RAG Required: True
  - Tools: True (für Workflow Connectors)
  - Escalation: True (Approval Pattern)
  
⚠️ RISIKEN
  ⚠️ Connector-Permissions müssen geklärt werden
  ⚠️ Compliance-Audit vor Produktion erforderlich
  ⚠️ 2 kritische Infos fehlen (Iterationen: 1/2)
```

**How to run:**
```bash
# CLI mit Geführter Beratung
python main.py
# Wahl: 2 (Guided Advisory)
# Antworte auf Fragen:
#   - Use Case: "Compliance & Regulatory Monitoring"
#   - Skill: "Expert"
#   - Automation: "Komplexe Workflows (3)"
#   - Enterprise: Ja
#   - Constraints: GDPR, Audit Trail, Approval
```

**Beobachte den Loop:**
- Iteration 1: framework_confidence ~0.65 → trigger RERUN
- Iteration 2: framework_confidence ~0.92 → END (Hard Limit 2)

---

### Demo 3: No-Code Automation (Einfach)

**Schwierigkeit:** ⭐ Easy  
**Expected Loop Iterations:** 0 (direkt END)

**Prompt zum kopieren:**
```
Geschäftsteam möchte Workflow-Automation ohne Programmierung. 
Müssen verschiedene Systeme (SAP, CRM, Email) verbinden. 
Team sind Nicht-Techniker, brauchen sehr No-Code-freundlich 
Lösung.
```

**Was passiert:**
1. RequirementsAgent: Erkennt `no_code_importance=5, automation_level=workflow_automation, connectors_required=True`
2. ProfilerAgent: `skill_level=BEGINNER, prefers_nocode=True`
3. UseCaseAnalyzerAgent: Matcht zu "New Hires Onboarding Agent", "Marketing Content Generator" (score ~0.75)
4. FrameworkAnalyzerAgent: Top = n8n (No-Code optimiert, score ~0.88)
5. DecisionAgent: Empfieht n8n, Architektur=SINGLE_AGENT (wird via UI konfiguriert)
6. ControlAgent: Confidence >0.60 → END

**Ergebnis:**
```
✨ HAUPT-EMPFEHLUNG
Framework: n8n
Score: 0.88

Architektur: SINGLE_AGENT
  - RAG Required: False
  - Tools: True (Connectors)
  - Escalation: False
  
Matched Bosch Use Cases:
  • New Hires Onboarding Agent (0.75)
  • Marketing Content Idea & Brief Generator (0.72)

⚠️ RISIKEN
  ⚠️ Connector-Permissions müssen geklärt werden (SAP, CRM)
  ⚠️ Standard No-Code Limits könnten überschritten werden bei Scale

📋 ASSUMPTIONS
  ✓ Annahme: Community-Support reicht aus für No-Code Framework
  ✓ Annahme: Connectors sind für SAP/CRM verfügbar
```

**How to run:**
```bash
# Web UI empfohlen (No-Code Tool!)
streamlit run streamlit_app.py
# Klick "Guided Advisory"
# Antworte:
#   - Use Case: "Geschäftsprozess Automation"
#   - Skill: "Anfänger (1)"
#   - No-Code: 5/5
#   - Automation: "Komplexe Workflows (3)"
#   - Enterprise: Nein
#   - Constraints: "Cost-Effective"
```

---

## 🔍 Beobachte die Agent-Ausführung

### Verbose Mode (See All Agent Steps)

```bash
# In CLI mit verbose=True
python main.py
# Wahl 1 → Input → Sehe alle Agent-Outputs

# Output sieht aus wie:
# 🚀 ADVISOR FLOW STARTED
# ==============================================================================
# User Input: "Ich möchte einen Agenten bauen..."
# Flow Nodes: 6 Agents + LangGraph Orchestration + Loop Control
# ==============================================================================
#
# 🔹 [NODE] Requirements Agent
#    Input: Ich möchte einen Agenten bauen...
#    ✓ Requirements: 2 constraints
#
# 🔹 [NODE] Profiler Agent
#    ✓ Profile: intermediate / enterprise
#
# 🔹 [NODE] UseCase Analyzer Agent
#    ✓ Matched 3 usecases (conf: 0.82)
#
# 🔹 [NODE] Framework Analyzer Agent
#    ✓ Found 5 candidates (conf: 0.88)
#
# 🔹 [NODE] Decision Agent
#    ✓ Recommended: LangChain (score: 0.90)
#
# 🔹 [NODE] Control Agent
#    ✓ Decision: END (Iteration: 1)
#
# ✓ ADVISOR FLOW COMPLETED
# ==============================================================================
```

### Inspect State Details

```python
from orchestrator.langgraph_flow import run_advisor_flow

state = run_advisor_flow("Your prompt", verbose=True)

# Inspect each agent's output:
print("=== REQUIREMENTS ===")
print(state.requirements.use_case_goal)
print(state.requirements.unknowns)

print("\n=== USER PROFILE ===")
print(state.user_profile.skill_level)
print(state.user_profile.org_context)

print("\n=== USECASE MATCHES ===")
for uc in state.usecase_match.matched_usecases[:3]:
    print(f"- {uc.usecase_title}: {uc.match_score:.2f}")

print("\n=== FRAMEWORK CANDIDATES ===")
for fw in state.framework_candidates.candidates[:3]:
    print(f"- {fw.framework_name}: {fw.score:.2f}")

print("\n=== RECOMMENDATION ===")
print(f"Top: {state.recommendation.recommended_framework}")
print(f"Architektur: {state.recommendation.architecture_suggestion.agent_type}")
print(f"Risks: {state.recommendation.risks}")

print(f"\n=== CONTROL DECISION ===")
print(f"Action: {state.control_decision.action}")
print(f"Iterations: {state.iteration_count}/2")
```

---

## 📊 System Architecture Anzeigen

### LangGraph Flow Diagram

```bash
python main.py
# Wahl 3 (Show Architecture)
```

Siehe Ausgabe:

```
🏗️ LANGGRAPH + ADK ARCHITECTURE
==============================================================================

AGENTS:
1. RequirementsAgent (A) -> Parse User Input
2. ProfilerAgent (B) -> Create User Profile
3. UseCaseAnalyzerAgent (C) -> Match Bosch UseCases
4. FrameworkAnalyzerAgent (D) -> Find Candidates
5. DecisionAgent (E) -> Create Recommendation
6. ControlAgent (F) -> Quality Gate + Routing

FLOW EDGES:
START -> A -> B -> C -> D -> E -> F -> [conditional] -> END/ASK/RERUN

LOOP RULES (in ControlAgent):
- usecase_confidence < 0.60 => RERUN_USECASE
- framework_confidence < 0.60 => RERUN_FRAMEWORK
- Type Mismatch => RERUN_FRAMEWORK
- Critical Info Missing => ASK_USER
- Else => END
- Hard Limit: 2 max iterations

ADK INTEGRATION:
- 6 ADK Agent Definitions created
- Tools, Policies, Knowledge Bases defined
- Policies: quality_gate_enforcement, iteration_limit_2
```

---

## 💾 Feedback Location & Format

### JSON Feedback Storage

```bash
./data/feedback/sessions.jsonl
```

**Beispiel Content:**
```json
{"rating": 4, "helpful": true, "comment": "Good recommendation", "timestamp": "2026-01-17T10:30:45.123456", "session_id": "1705483845.123"}
{"rating": 5, "helpful": true, "comment": "Exactly what we needed", "timestamp": "2026-01-17T10:35:12.456789", "session_id": "1705483912.456"}
```

### Feedback Stats

```python
from memory.feedback_store import FeedbackStore

store = FeedbackStore()
stats = store.get_feedback_stats()

print(f"Total Sessions: {stats['total']}")
print(f"Average Rating: {stats['average_rating']} ⭐")
print(f"Helpful Rate: {stats['helpful_percentage']}%")
```

---

## 🛠️ Häufige Fragen

### Q: Wie lange dauert eine Empfehlung?

**A:** Typischerweise 5-10 Sekunden ohne Loops, 10-15 Sekunden mit 1 Loop. Max 2 Iterationen sind hart codiert.

### Q: Kann ich die Loop-Regeln ändern?

**A:** Ja, edit `agents/control_agent.py` → `decide_continuation()` Funktion.

### Q: Wie werden neue Bosch Use Cases hinzugefügt?

**A:** Edit `data/bosch_usecases_seed.py` und re-seed mit `UseCaseAnalyzerAgent().seed_bosch_usecases()`.

### Q: Kann ich offline arbeiten?

**A:** Nein, Google GenAI API ist erforderlich. Embeddings und LLM-Calls brauchen Internet.

### Q: Was ist die Fehlerquote?

**A:** ControlAgent's Loop-Regeln fangen die meisten Fehler ab. Bei Hard Limit 2 wird Best-Effort Empfehlung gegeben.

---

## 🎓 Next Steps

1. **Run Demo 1** (RAG Q&A) - Leicht zu verstehen
2. **Run Demo 2** (Compliance) - Sehe einen Loop in Aktion
3. **Run Demo 3** (No-Code) - Nutze Web UI
4. **Inspect Architecture** - Verstehe die 6 Agenten
5. **Modifiziere Prompts** - Teste deine eigenen Use Cases

---

## 🐛 Troubleshooting

**Issue: "GOOGLE_API_KEY not set"**
```bash
echo "GOOGLE_API_KEY=sk-..." > .env
```

**Issue: "No module named 'langgraph'"**
```bash
pip install langgraph langchain pydantic
```

**Issue: "Chroma collection not found"**
```python
# Force re-seed
from agents.usecase_analyzer_agent import UseCaseAnalyzerAgent
UseCaseAnalyzerAgent().seed_bosch_usecases()
```

**Issue: Slow responses**
- Check internet connection (API calls)
- CPU might be busy (Embeddings computation)
- Check `./data/chroma/` permissions

---

**Happy Exploring! 🚀**

For full documentation, see `README.md`
