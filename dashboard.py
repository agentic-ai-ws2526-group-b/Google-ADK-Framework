"""
Gradio Dashboard for the Agent Routing System.
A modern, interactive interface for the agent selection and execution system.
"""
import gradio as gr
from advisor_agent import advise_best_agent
from agent_implementations import get_agent_executor

def process_task(task: str):
    """Process the user's task and return formatted results."""
    if not task:
        return "⚠️ Bitte geben Sie eine Aufgabe ein!"
        
    # Get recommendation
    result = advise_best_agent(task)
    
    if not result.chosen_agent_id:
        return f"""
### ❌ Kein passender Agent gefunden

**Grund:**
{result.reason}

**Empfehlung:**
{result.action_recommendation}
"""
    
    # Execute the chosen agent
    agent_class = get_agent_executor(result.chosen_agent_id)
    agent_response = agent_class.execute(task) if agent_class else None
    
    # Format the response with custom styling
    response = f"""
# 🎯 Analyse & Ausführung

### 🤖 Gewählter Agent
{result.chosen_agent_name} ({result.chosen_agent_id})

### 📊 Confidence Score
{result.confidence * 100:.1f}%

### 💡 Begründung
{result.reason}

### ✨ Ausführungsergebnis
{agent_response.output if agent_response else "Keine Ausführung möglich"}

### 📝 Metadaten
"""
    
    if agent_response and agent_response.metadata:
        for key, value in agent_response.metadata.items():
            response += f"- **{key}**: {value}\n"
            
    return response

# Create the Gradio interface
with gr.Blocks(theme=gr.themes.Soft(
    primary_hue="red",
    secondary_hue="blue",
)) as demo:
    gr.Markdown(
        """
        # 🎯 Agent Routing System
        
        ### Ihr intelligenter Wegweiser zu spezialisierten KI-Agenten
        
        Beschreiben Sie Ihre Aufgabe, und das System wählt den am besten geeigneten Agenten aus:
        
        🤖 **Verfügbare Agenten:**
        - 📝 Content Agent (Text & Marketing)
        - 📊 Summary Agent (Zusammenfassungen)
        - � Analytics Agent (Datenanalyse)
        """
    )
    
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Ihre Aufgabe",
                placeholder="z.B.: Schreibe eine Produktbeschreibung für den neuen Bosch Akku-Bohrhammer",
                lines=4
            )
            submit_btn = gr.Button("🚀 Aufgabe ausführen", variant="primary")
            
        with gr.Column():
            output = gr.Markdown(label="Ergebnis")
            
    submit_btn.click(
        fn=process_task,
        inputs=input_text,
        outputs=output
    )
    
    gr.Examples(
        [
            ["Schreibe eine Produktbeschreibung für den neuen Bosch Staubsauger"],
            ["Fasse diese 20 Kundenbeschwerden in 5 Bullet Points zusammen"],
            ["Welche Support-Kategorie ist aktuell am kritischsten?"]
        ],
        input_text,
        output,
        fn=process_task,
        cache_examples=True
    )

# Launch the interface
if __name__ == "__main__":
    demo.launch()