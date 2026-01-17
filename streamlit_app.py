"""
Framework Advisor - Streamlit Web UI mit LangGraph + Bosch Branding
Ein professionelles, vollständiges Agent-for-Agents System.

Starten mit: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

from orchestrator.langgraph_flow import run_advisor_flow, print_flow_architecture
from models.schemas import AdvisorState, ControlAction, AutomationLevel
from memory.feedback_store import FeedbackStore, SessionFeedback
from adk_adapter import print_adk_agent_definitions

# ============================================================================
# Seiten-Konfiguration
# ============================================================================

st.set_page_config(
    page_title="Framework Advisor - Agent for Agents",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für Bosch-Branding
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background-color: #f5f5f5;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        padding: 0;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #001f3f 0%, #003d7a 100%);
        padding: 30px 50px;
        margin-bottom: 40px;
        border-bottom: 4px solid #ff6600;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .bosch-logo {
        font-size: 28px;
        font-weight: bold;
        color: #ff6600;
        letter-spacing: 2px;
    }
    
    .header-text h1 {
        color: white;
        font-size: 36px;
        margin: 0;
        font-weight: 700;
    }
    
    .header-text p {
        color: #ccc;
        font-size: 14px;
        margin: 5px 0 0 0;
    }
    
    /* Card Styles */
    .card-box {
        background-color: #f7efe7;
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid #e8dfd0;
    }
    
    .card-box h3 {
        color: #001f3f;
        font-size: 18px;
        margin-bottom: 15px;
        font-weight: 600;
    }
    
    /* Result Cards */
    .result-card {
        background-color: white;
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-top: 5px solid #ff6600;
    }
    
    .result-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 15px;
    }
    
    .result-card-title {
        font-size: 22px;
        font-weight: 700;
        color: #001f3f;
    }
    
    .score-badge {
        background-color: #ff6600;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .summary-text {
        font-size: 14px;
        color: #555;
        margin-bottom: 15px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Session State Management
# ============================================================================

if "current_mode" not in st.session_state:
    st.session_state.current_mode = None

if "flow_state" not in st.session_state:
    st.session_state.flow_state = None

if "feedback_store" not in st.session_state:
    st.session_state.feedback_store = FeedbackStore()

if "show_feedback_form" not in st.session_state:
    st.session_state.show_feedback_form = False

# ============================================================================
# Header
# ============================================================================

st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div class="bosch-logo">BOSCH</div>
        <div class="header-text">
            <h1>🤖 Framework Advisor</h1>
            <p>Agent-for-Agents Platform • Multi-Agent LangGraph Orchestration • Google ADK Integration</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Sidebar Navigation
# ============================================================================

st.sidebar.markdown("### 🎯 Navigation")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Wähle einen Modus:",
    ["🚀 Quick Recommendation", "🎯 Guided Advisory", "📊 Architecture & Deep Dive", "💡 About & Demo"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 System Info")

feedback_stats = st.session_state.feedback_store.get_feedback_stats()
if feedback_stats["total"] > 0:
    st.sidebar.metric("Sessions Analyzed", feedback_stats["total"])
    st.sidebar.metric("Average Rating", f"{feedback_stats['average_rating']} ⭐")
    st.sidebar.metric("Helpful Rate", f"{feedback_stats['helpful_percentage']}%")

# ============================================================================
# Page: Quick Recommendation
# ============================================================================

if page == "🚀 Quick Recommendation":
    st.markdown("""
    <div class="card-box">
        <h3>⚡ Quick Recommendation Mode</h3>
        <p>Beschreibe kurz, was du bauen möchtest. Das System wird dir einen passenden Framework empfehlen.</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area(
        "📝 Was möchtest du bauen?",
        placeholder="z.B. 'Ich brauche einen Agent der technische Dokumentation durchsucht und Q&A beantwortet' oder 'Workflow-Automation ohne Programmieren'",
        height=120
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        run_button = st.button("🔍 Recommendation ermitteln", type="primary", use_container_width=True)
    
    with col2:
        if st.button("ℹ️ Flow zeigen"):
            with st.expander("LangGraph Flow Architektur"):
                print_flow_architecture()
    
    if run_button and user_input:
        with st.spinner("🔄 Running 6-Agent LangGraph Flow (max 15 sec)..."):
            try:
                import time
                start = time.time()
                
                # Flow mit Timeout
                flow_result = {"state": None, "error": None}
                
                def run_flow():
                    try:
                        flow_result["state"] = run_advisor_flow(user_input, verbose=False)
                    except Exception as e:
                        flow_result["error"] = str(e)
                
                import threading
                thread = threading.Thread(target=run_flow, daemon=True)
                thread.start()
                thread.join(timeout=15)  # 15 second timeout
                
                elapsed = time.time() - start
                
                if flow_result["state"] is None:
                    error = flow_result["error"] or "Flow timeout (>15s)"
                    st.warning(f"⚠️ Flow took too long or failed: {error}")
                    st.info("💡 Tip: This is likely a network/API issue. Try the Demo mode or use the Architecture tab.")
                else:
                    st.session_state.flow_state = flow_result["state"]
                    st.session_state.show_feedback_form = True
                    st.success(f"✓ Flow completed in {elapsed:.1f}s")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("Technical Details"):
                    traceback.print_exc()
    
    # Display Results
    if st.session_state.flow_state:
        state = st.session_state.flow_state
        
        if state.recommendation:
            st.markdown("---")
            st.markdown("### ✅ Empfehlung")
            
            # Top 1
            rec = state.recommendation
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-card-header">
                        <div class="result-card-title">{rec.recommended_framework}</div>
                        <div class="score-badge">{rec.recommended_score:.2f}</div>
                    </div>
                    <div class="summary-text"><b>Empfehlung:</b> {rec.reasoning_summary}</div>
                    <div class="summary-text"><b>Architektur:</b> {rec.architecture_suggestion.agent_type.upper()} • RAG: {str(rec.architecture_suggestion.requires_rag)} • Tools: {str(rec.architecture_suggestion.requires_tools)}</div>
                    <div class="summary-text"><b>Notizen:</b> {rec.architecture_suggestion.notes}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px;">
                    <p><b>Iterationen:</b> {state.iteration_count}</p>
                    <p><b>Status:</b> ✓ Completed</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Top 3
            if len(rec.top_3) > 1:
                st.markdown("### 🏆 Top 3 Alternativen")
                for i, fw in enumerate(rec.top_3[1:], 2):
                    with st.expander(f"{i}. {fw.framework_name} (Score: {fw.score:.2f})"):
                        st.write(fw.reason)
                        if fw.sources:
                            st.markdown("**Quellen:**")
                            for src in fw.sources[:3]:
                                st.write(f"- {src}")
            
            # Bosch Use Case Matches
            if rec.matched_bosch_usecases:
                st.markdown("### 🔗 Gematchtе Bosch Use Cases")
                uc_data = [{
                    "Use Case": uc.usecase_title,
                    "Category": uc.category,
                    "Match Score": f"{uc.match_score:.2f}"
                } for uc in rec.matched_bosch_usecases[:3]]
                st.dataframe(pd.DataFrame(uc_data), use_container_width=True)
            
            # Risks & Assumptions
            col1, col2 = st.columns(2)
            with col1:
                if rec.assumptions:
                    st.markdown("### 📋 Annahmen")
                    for assumption in rec.assumptions:
                        st.write(f"✓ {assumption}")
            
            with col2:
                if rec.risks:
                    st.markdown("### ⚠️ Risiken")
                    for risk in rec.risks:
                        st.write(f"⚠️ {risk}")
    
    # Feedback Form
    if st.session_state.show_feedback_form and st.session_state.flow_state:
        st.markdown("---")
        st.markdown("### 📝 Feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            rating = st.slider("Hat die Empfehlung geholfen? (1-5 Sterne)", 1, 5, 3)
        with col2:
            helpful = st.checkbox("Würdest du diese Empfehlung verwenden?", value=True)
        
        comment = st.text_area("Optional: Kommentar oder Verbesserungsvorschläge", height=80)
        
        if st.button("✉️ Feedback speichern", type="secondary"):
            feedback = SessionFeedback(
                rating=rating,
                helpful=helpful,
                comment=comment if comment else None,
                session_id=st.session_state.flow_state.session_id
            )
            st.session_state.feedback_store.save_feedback(feedback)
            st.success("✓ Feedback gespeichert! Danke für dein Input.")
            st.session_state.show_feedback_form = False

# ============================================================================
# Page: Guided Advisory
# ============================================================================

elif page == "🎯 Guided Advisory":
    st.markdown("""
    <div class="card-box">
        <h3>🎯 Geführte Beratung</h3>
        <p>Beantworte einige gezielte Fragen - das System wird dir die beste Empfehlung geben.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fragebogen
    col1, col2 = st.columns(2)
    
    with col1:
        use_case = st.text_area(
            "❓ Was möchtest du grob bauen?",
            placeholder="z.B. RAG-System, Automation, Multi-Agent Collaboration",
            height=80
        )
        
        skill_level = st.selectbox(
            "🎓 Dein technisches Skill Level?",
            ["🟢 Anfänger (Kein Code)", "🟡 Intermediate (Etwas Python/JS)", "🔴 Expert (Erfahrene*r Entwickler*in)", "⚙️ DevOps/Infrastructure"]
        )
    
    with col2:
        automation_level = st.radio(
            "⚙️ Art der Automatisierung?",
            ["Q&A nur (No Automation)", "Tool Actions (APIs aufrufen)", "Komplexe Workflows (Multi-Step)"]
        )
        
        no_code_importance = st.slider(
            "📊 Wie wichtig ist No-Code?",
            1, 5, 3,
            help="1 = egal, 5 = absolut notwendig"
        )
    
    enterprise_needed = st.checkbox("🏢 Enterprise Features erforderlich?")
    
    constraints = st.multiselect(
        "⛓️ Constraints/Anforderungen (optional)",
        ["GDPR/Datenschutz", "Real-Time Performance", "High Autonomy", "Scalability", "Cost-Effective"]
    )
    
    # Build combined input
    full_input = f"""
Use Case: {use_case}
Skill Level: {skill_level}
Automation: {automation_level}
Enterprise: {enterprise_needed}
No-Code Importance: {no_code_importance}/5
Constraints: {', '.join(constraints) if constraints else 'None'}
    """
    
    if st.button("🔍 Empfehlung ermitteln", type="primary", use_container_width=True):
        with st.spinner("🔄 Running Full LangGraph Flow..."):
            try:
                flow_state = run_advisor_flow(full_input, verbose=False)
                st.session_state.flow_state = flow_state
                st.session_state.show_feedback_form = True
                st.success("✓ Analyse abgeschlossen!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display Results (same as Quick Mode)
    if st.session_state.flow_state:
        state = st.session_state.flow_state
        
        if state.recommendation:
            st.markdown("---")
            st.markdown("### ✅ Empfehlung")
            
            rec = state.recommendation
            st.markdown(f"""
            <div class="result-card">
                <div class="result-card-header">
                    <div class="result-card-title">{rec.recommended_framework}</div>
                    <div class="score-badge">{rec.recommended_score:.2f}</div>
                </div>
                <div class="summary-text">{rec.reasoning_summary}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if len(rec.top_3) > 1:
                st.markdown("### Top 3")
                for fw in rec.top_3[1:]:
                    st.write(f"• **{fw.framework_name}** ({fw.score:.2f}): {fw.reason[:100]}...")

# ============================================================================
# Page: Architecture & Deep Dive
# ============================================================================

elif page == "📊 Architecture & Deep Dive":
    st.markdown("### 🏗️ System Architektur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🤖 6-Agent LangGraph System
        1. **RequirementsAgent** - Parst User-Input
        2. **ProfilerAgent** - Erstellt User-Profile
        3. **UseCaseAnalyzerAgent** - Matcht Bosch Use Cases
        4. **FrameworkAnalyzerAgent** - Findet Frameworks
        5. **DecisionAgent** - Erstellt Empfehlung
        6. **ControlAgent** - Quality Gate + Loops
        """)
    
    with col2:
        st.markdown("""
        #### 🔄 LangGraph Flow
        - Conditional Routing basierend auf Quality Gates
        - Max 2 Iterationen (Hard Limit)
        - Loop Trigger bei niedriger Confidence
        - ASK_USER für fehlende Infos
        """)
    
    # ADK Info
    st.markdown("---")
    st.markdown("### 🏗️ Google ADK Integration")
    
    with st.expander("ADK Agent Definitions anzeigen"):
        print_adk_agent_definitions()
    
    # Bosch Use Cases
    st.markdown("---")
    st.markdown("### 📚 Bosch Use Cases Pool")
    
    from data.bosch_usecases_seed import get_all_usecases, get_usecases_by_category
    
    all_ucs = get_all_usecases()
    st.write(f"**Total Use Cases:** {len(all_ucs)}")
    
    # By Category
    categories = set(uc["category"] for uc in all_ucs)
    selected_category = st.selectbox("Kategorie:", sorted(categories))
    
    ucs_in_category = get_usecases_by_category(selected_category)
    
    for uc in ucs_in_category:
        with st.expander(f"🔹 {uc['title']}"):
            st.write(f"**Description:** {uc['description']}")
            st.write(f"**Tags:** {', '.join(uc['tags'])}")
            st.write(f"**Challenges:** {', '.join(uc['challenges'][:2])}")
            st.write(f"**Typical Frameworks:** {', '.join(uc['typical_frameworks'])}")

# ============================================================================
# Page: About & Demo
# ============================================================================

elif page == "💡 About & Demo":
    st.markdown("""
    ### 🎯 Was ist die Framework Advisor?
    
    Die **Agent-for-Agents Plattform** ist ein intelligentes System, das dir hilft, 
    den richtigen Framework für deinen Use Case zu finden.
    
    **Das System besteht aus:**
    - **6 intelligente Agenten** orchestriert durch LangGraph
    - **Google ADK Integration** für strukturierte Agent-Definition
    - **Bosch Use-Case Pool** als semantische Referenzbasis
    - **Feedback Loop** für kontinuierliches Lernen
    
    ---
    
    ### 📈 Beispiel Prompts (zum Copy-Paste)
    """)
    
    examples = [
        {
            "title": "Beispiel 1: RAG Q&A System",
            "prompt": "Ich möchte einen Agenten bauen, der über tausende von technischen Dokumentationen unser Bosch-Ingenieur-Teams Q&A beantwortet. Der Agent soll relevant Snippets finden und zitieren können.",
            "expected": "Wird RAG-Framework wie LangChain empfehlen"
        },
        {
            "title": "Beispiel 2: Compliance & Automation",
            "prompt": "Wir brauchen einen vollautomatisierten Workflow, der globale Regulatory Changes monitored und unser Compliance Team benachrichtigt. Muss Enterprise-ready sein.",
            "expected": "Wird Multi-Agent + Automation wie LangGraph/Google ADK empfehlen"
        },
        {
            "title": "Beispiel 3: No-Code Geschäftsprozess",
            "prompt": "Geschäftsteam möchte Workflow-Automation ohne Programmierung. Müssen verschiedene Systeme (SAP, CRM, Email) verbinden.",
            "expected": "Wird No-Code wie n8n empfehlen"
        }
    ]
    
    for i, ex in enumerate(examples, 1):
        with st.expander(f"📋 {ex['title']}"):
            st.markdown(f"**Prompt:**")
            st.code(ex['prompt'])
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Erwartetes Ergebnis:** {ex['expected']}")
            with col2:
                if st.button(f"📋 Copy & Run Example {i}", key=f"ex{i}"):
                    st.session_state.current_mode = "quick"
    
    st.markdown("---")
    st.markdown("""
    ### 🔧 Technologie Stack
    - **Orchestrator:** LangGraph (Conditional Routing)
    - **LLM:** Google GenAI (Gemini 2.5 Flash)
    - **Embeddings:** Google GenAI Embedding Model
    - **Vector DB:** Chroma (Persistent Storage)
    - **Frameworks:** 8+ (Google ADK, LangChain, LangGraph, n8n, CrewAI, etc.)
    - **Feedback:** JSON + optional Chroma Collection
    
    ### 📚 Dokumentation
    - [GitHub Repository](https://github.com/example)
    - [README](../README.md)
    - [API Docs](../docs)
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Powered by Bosch • LangGraph • Google ADK • 2026</p>", unsafe_allow_html=True)
