"""
DEMO APP - ohne LLM-Calls, zeigt die Architektur
"""

import streamlit as st
from datetime import datetime
import json

st.set_page_config(page_title="Framework Advisor DEMO", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.main { padding: 20px; }
.header { background: linear-gradient(135deg, #001f3f 0%, #003d7a 100%); padding: 30px; margin-bottom: 30px; border-bottom: 4px solid #ff6600; color: white; }
.card { background: #f7efe7; border-radius: 15px; padding: 20px; margin: 15px 0; border: 1px solid #e8dfd0; }
.section { margin: 30px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h1>🤖 Framework Advisor - DEMO</h1>
    <p>LangGraph + 6 Agents + Bosch Use Cases</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🚀 Quick Demo", "📊 Architecture", "📚 How It Works"])

with tab1:
    st.markdown("### Quick Recommendation Demo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Input")
        user_input = st.text_area(
            "What do you want to build?",
            value="I need a RAG system for technical documentation Q&A",
            height=100
        )
        
        if st.button("🔍 Get Recommendation", type="primary"):
            with st.spinner("Running 6-Agent Flow..."):
                # DEMO: Simulated response (no actual LLM calls)
                st.session_state.demo_result = {
                    "framework": "LangChain",
                    "score": 0.92,
                    "reasoning": "LangChain is the best choice for RAG systems with built-in prompt templates and document loaders.",
                    "top_3": [
                        {"name": "LangChain", "score": 0.92},
                        {"name": "LlamaIndex", "score": 0.85},
                        {"name": "Google ADK", "score": 0.78}
                    ],
                    "matched_usecases": [
                        {"title": "Technical Documentation Q&A", "category": "RAG", "score": 0.88},
                        {"title": "Knowledge Management", "category": "RAG", "score": 0.82}
                    ],
                    "assumptions": [
                        "Documents are in PDF or text format",
                        "Latency < 2 seconds is acceptable"
                    ],
                    "risks": [
                        "Hallucination in Q&A responses",
                        "Vector DB scaling for large doc sets"
                    ],
                    "iterations": 1
                }
    
    with col2:
        st.markdown("#### Result")
        if "demo_result" in st.session_state:
            result = st.session_state.demo_result
            
            st.markdown(f"""
            **Recommended:** {result['framework']}
            
            **Score:** {result['score']:.2f}
            
            **Reasoning:** {result['reasoning']}
            """)
            
            st.markdown("**Top 3:**")
            for fw in result['top_3']:
                st.write(f"• {fw['name']}: {fw['score']:.2f}")
            
            st.markdown("**Matched Use Cases:**")
            for uc in result['matched_usecases']:
                st.write(f"• {uc['title']} ({uc['score']:.2f})")
            
            st.markdown("**Assumptions:**")
            for a in result['assumptions']:
                st.write(f"✓ {a}")
            
            st.markdown("**Risks:**")
            for r in result['risks']:
                st.write(f"⚠️ {r}")
            
            st.markdown(f"**Iterations:** {result['iterations']}")
        else:
            st.info("Click 'Get Recommendation' to see results")

with tab2:
    st.markdown("### LangGraph Flow Architecture")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**6 Agents:**")
        agents = [
            ("A", "RequirementsAgent", "Parse input → Requirements"),
            ("B", "ProfilerAgent", "Create UserProfile"),
            ("C", "UseCaseAnalyzerAgent", "Match Bosch UseCases"),
            ("D", "FrameworkAnalyzerAgent", "Find Frameworks"),
            ("E", "DecisionAgent", "Create Recommendation"),
            ("F", "ControlAgent", "Quality gate + Loop")
        ]
        for code, name, desc in agents:
            st.write(f"**{code}** {name}: {desc}")
    
    with col2:
        st.markdown("**Flow:**")
        st.text("""
START
  ↓
[A] Requirements Agent
  ↓
[B] Profiler Agent
  ↓
[C] UseCase Analyzer Agent
  ↓
[D] Framework Analyzer Agent
  ↓
[E] Decision Agent
  ↓
[F] Control Agent
  ├─→ END (if high confidence)
  ├─→ RERUN_USECASE (if conf < 0.60)
  ├─→ RERUN_FRAMEWORK (if type mismatch)
  └─→ ASK_USER (if critical info missing)
        """)
    
    st.markdown("---")
    st.markdown("**Loop Rules:**")
    st.write("""
- usecase_confidence < 0.60 → RERUN_USECASE
- framework_confidence < 0.60 → RERUN_FRAMEWORK
- Type Mismatch → RERUN_FRAMEWORK
- Critical Info Missing → ASK_USER
- Hard Limit: 2 iterations max
    """)

with tab3:
    st.markdown("### System Components")
    
    components = {
        "🤖 Orchestration": {
            "LangGraph": "StateGraph with 6 nodes + conditional routing",
            "State Management": "Pydantic V2 models for type safety"
        },
        "🧠 LLM Integration": {
            "Model": "Google Gemini 2.5 Flash",
            "Embeddings": "Google GenAI embedding-001",
            "Framework": "google-genai Python client"
        },
        "🗄️ Data Layer": {
            "Vector DB": "Chromadb (persistent, cosine similarity)",
            "Framework Knowledge": "8 seed frameworks + dynamic RAG",
            "Use Cases": "15 Bosch use cases in Chroma"
        },
        "💾 Persistence": {
            "Feedback": "JSON file store (./data/feedback/sessions.jsonl)",
            "Session State": "Streamlit session_state",
            "Database": "Chroma collection (bosch_usecases)"
        },
        "🎨 UI/UX": {
            "Web": "Streamlit (4 modes: quick, guided, deep-dive, demo)",
            "CLI": "Interactive menu with styled output",
            "Branding": "Bosch corporate colors (#001f3f, #ff6600)"
        }
    }
    
    for category, items in components.items():
        with st.expander(category, expanded=False):
            for name, desc in items.items():
                st.write(f"**{name}**: {desc}")

# Footer
st.markdown("---")
st.markdown("""
<small>
Framework Advisor v0.2.0 | Agent-for-Agents Platform | LangGraph + Google ADK Integration
</small>
""", unsafe_allow_html=True)
