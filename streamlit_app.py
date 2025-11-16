"""
Framework Advisor - Streamlit Web UI mit Bosch-Branding
Eine professionelle webbasierte Oberfläche zur intelligenten Framework-Empfehlung.

Starten mit: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
from my_agent.agent import FrameworkAdvisorAgent, FrameworkMatch, FrameworkMultiScore, format_multi_score_report


# ============================================================================
# Seiten-Konfiguration
# ============================================================================

st.set_page_config(
    page_title="Framework Consultant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS für Bosch-Branding und professionelles Design
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
    
    .card-box label {
        color: #333;
        font-size: 14px;
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
    
    .pros-cons-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin: 15px 0;
    }
    
    .pros-box, .cons-box {
        padding: 12px;
        border-radius: 10px;
    }
    
    .pros-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    
    .cons-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    
    .pros-box h4, .cons-box h4 {
        margin: 0 0 10px 0;
        font-size: 13px;
        font-weight: 600;
    }
    
    .pros-box ul, .cons-box ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .pros-box li, .cons-box li {
        font-size: 12px;
        margin: 5px 0;
        padding-left: 20px;
    }
    
    .pros-box li:before {
        content: "✓ ";
        color: #4caf50;
        font-weight: bold;
        margin-right: 5px;
    }
    
    .cons-box li:before {
        content: "✗ ";
        color: #f44336;
        font-weight: bold;
        margin-right: 5px;
    }
    
    /* Buttons */
    .btn-generate {
        background-color: #ff6600;
        color: white;
        padding: 12px 40px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .btn-generate:hover {
        background-color: #e55a00;
    }
    
    .btn-back {
        background-color: #ccc;
        color: #333;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        cursor: pointer;
        margin-bottom: 20px;
    }
    
    /* Checkboxes & Radio */
    .stCheckbox, .stRadio {
        padding: 8px 0;
    }
    
    /* Responsive Grid */
    .result-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        gap: 25px;
    }
    
    @media (max-width: 1024px) {
        .result-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Import & Setup
# ============================================================================

import os
from my_agent.agent import FrameworkAdvisorAgent

# ============================================================================
# Session State Initialization
# ============================================================================

if 'stage' not in st.session_state:
    st.session_state['stage'] = 'form'

if 'form_data' not in st.session_state:
    st.session_state['form_data'] = {
        'agent_type': 'Multi-Agent Systems',
        'criteria': [],
        'use_case': '',
        'recommendation': None
    }

# ============================================================================
# Agent Caching
# ============================================================================

@st.cache_resource
def load_agent():
    agent = FrameworkAdvisorAgent()
    return agent

@st.cache_resource
def seed_knowledge(_agent):
    _agent.seed_basic_framework_knowledge()
    return _agent

# Initialize agent
agent = load_agent()
seed_knowledge(agent)

# ============================================================================
# Render Functions - View 1: Questionnaire Form
# ============================================================================

def render_questionnaire_view():
    """Render the questionnaire form (View 1)."""
    
    # Header mit Bosch-Branding
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
            <div class="bosch-logo">⚙️ BOSCH</div>
            <div class="header-text">
                <h1>🤖 Framework Consultant</h1>
                <p>Finde den perfekten Framework für dein Projekt</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Agent Type Selection
    st.markdown("""
    <div class="card-box">
        <h3>1️⃣ Agent-Typ auswählen</h3>
    </div>
    """, unsafe_allow_html=True)
    
    agent_types = [
        "Multi-Agent Systems",
        "Workflow Automation",
        "Knowledge Processing",
        "Data Analysis",
        "Natural Language Processing"
    ]
    
    st.session_state['form_data']['agent_type'] = st.radio(
        "Welche Art von Agent-System benötigst du?",
        agent_types,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Criteria Selection
    st.markdown("""
    <div class="card-box">
        <h3>2️⃣ Wichtige Kriterien</h3>
    </div>
    """, unsafe_allow_html=True)
    
    criteria_options = [
        "Benutzerfreundlichkeit",
        "Community Support",
        "Performance",
        "Lernkurve",
        "Flexibilität",
        "Enterprise-Ready",
        "Open Source",
        "Kostenlos"
    ]
    
    st.session_state['form_data']['criteria'] = st.multiselect(
        "Welche Kriterien sind dir wichtig?",
        criteria_options,
        default=st.session_state['form_data'].get('criteria', []),
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use Case Description
    st.markdown("""
    <div class="card-box">
        <h3>3️⃣ Dein Use-Case</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.session_state['form_data']['use_case'] = st.text_area(
        "Beschreibe deinen Use-Case oder deine Anforderungen:",
        value=st.session_state['form_data'].get('use_case', ''),
        height=150,
        placeholder="z.B. 'Ich brauche eine automatisierte Workflow-Lösung für die Produktionsplanung...'",
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🚀 Empfehlungen abrufen", use_container_width=True, key="analyze_btn"):
            if st.session_state['form_data']['use_case'].strip():
                st.session_state['stage'] = 'result'
                st.rerun()
            else:
                st.error("Bitte gib einen Use-Case ein!")
    
    with col2:
        if st.button("🔄 Zurücksetzen", use_container_width=True):
            st.session_state['form_data'] = {
                'agent_type': 'Multi-Agent Systems',
                'criteria': [],
                'use_case': '',
                'recommendation': None
            }
            st.rerun()


# ============================================================================
# Render Functions - View 2: Results with Framework Cards
# ============================================================================

def render_result_card(framework_data):
    """Render a single result card."""
    
    name = framework_data.get('name', 'Unknown')
    score = framework_data.get('overall_score', 0)
    summary = framework_data.get('summary', '')
    pros = framework_data.get('pros', [])
    cons = framework_data.get('cons', [])
    
    # Score color coding
    if score >= 8:
        score_color = "#4caf50"
    elif score >= 6:
        score_color = "#ff9800"
    else:
        score_color = "#f44336"
    
    pros_list = "<br>".join([f"<li>{p}</li>" for p in pros]) if pros else "<li>N/A</li>"
    cons_list = "<br>".join([f"<li>{c}</li>" for c in cons]) if cons else "<li>N/A</li>"
    
    card_html = f"""
    <div class="result-card">
        <div class="result-card-header">
            <div class="result-card-title">{name}</div>
            <div class="score-badge" style="background-color: {score_color};">{score:.2f} / 10</div>
        </div>
        <div class="summary-text">{summary}</div>
        <div class="pros-cons-container">
            <div class="pros-box">
                <h4>✅ Stärken</h4>
                <ul>{pros_list}</ul>
            </div>
            <div class="cons-box">
                <h4>❌ Herausforderungen</h4>
                <ul>{cons_list}</ul>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_results_view():
    """Render the results view (View 2) with framework cards."""
    
    # Back Button
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("← Zurück zum Fragebogen", use_container_width=True):
            st.session_state['stage'] = 'form'
            st.rerun()
    
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
            <div class="bosch-logo">⚙️ BOSCH</div>
            <div class="header-text">
                <h1>📊 Framework-Empfehlungen</h1>
                <p>Basierend auf deinen Anforderungen</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Show form summary
    with st.expander("� Deine Anforderungen"):
        st.write(f"**Agent-Typ:** {st.session_state['form_data']['agent_type']}")
        st.write(f"**Wichtige Kriterien:** {', '.join(st.session_state['form_data']['criteria']) if st.session_state['form_data']['criteria'] else 'Keine angegeben'}")
        st.write(f"**Use-Case:** {st.session_state['form_data']['use_case']}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze and get recommendations
    with st.spinner("🔍 Analysiere deine Anforderungen..."):
        try:
            # Build enriched prompt
            enriched_prompt = f"""
            Agent-Typ: {st.session_state['form_data']['agent_type']}
            Wichtige Kriterien: {', '.join(st.session_state['form_data']['criteria'])}
            Use-Case: {st.session_state['form_data']['use_case']}
            """
            
            # Get multi-criteria evaluation
            recommendations = agent.evaluate_frameworks_multi_criteria(enriched_prompt)
            
            # Convert to display format with pros/cons
            framework_cards = []
            for rec in recommendations[:3]:  # Top 3
                card_data = {
                    'name': rec.name,
                    'overall_score': rec.overall_score,
                    'summary': rec.summary,
                    'pros': [
                        "Hohe Benutzerfreundlichkeit",
                        "Gute Community Support",
                        "Schnelle Performance"
                    ],
                    'cons': [
                        "Steile Lernkurve anfangs",
                        "Limited offline Funktionen"
                    ]
                }
                framework_cards.append(card_data)
            
            # Render cards in grid
            st.markdown('<div class="result-grid">', unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, card in enumerate(framework_cards):
                with cols[idx % 3]:
                    render_result_card(card)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed table
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.subheader("📊 Detaillierte Vergleichstabelle")
            
            data = []
            for rec in recommendations:
                data.append({
                    "Framework": rec.name,
                    "Score": f"{rec.overall_score:.2f}/10",
                    "Benutzerfreundlichkeit": f"{rec.criteria_scores.get('ease_of_use', 0):.1f}",
                    "Community": f"{rec.criteria_scores.get('community', 0):.1f}",
                    "Performance": f"{rec.criteria_scores.get('performance', 0):.1f}",
                    "Learning Curve": f"{rec.criteria_scores.get('learning_curve', 0):.1f}",
                    "Flexibilität": f"{rec.criteria_scores.get('flexibility', 0):.1f}",
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Fehler: {e}")
            st.info("Bitte versuche es erneut.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer
    if st.button("← Neue Anfrage", use_container_width=True):
        st.session_state['stage'] = 'form'
        st.rerun()


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application logic."""
    if st.session_state['stage'] == 'form':
        render_questionnaire_view()
    elif st.session_state['stage'] == 'result':
        render_results_view()


if __name__ == "__main__":
    main()
