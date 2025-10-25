"""
CLI demo for the Agent Routing System.
This module provides a simple command-line interface to demonstrate
the agent routing capabilities.

Note: In final product, this CLI call will be replaced by a dashboard
text field in the Bosch internal tool.
"""
import textwrap
import time
from advisor_agent import advise_best_agent
from agent_implementations import get_agent_executor


def format_output(task: str, result, agent_response=None) -> str:
    """Format the advisor result and agent execution output for CLI display."""
    # Prepare the header
    output = [
        "=" * 80,
        "Nutzer-Task:",
        textwrap.fill(task, width=76, initial_indent="  ", subsequent_indent="  "),
        "",
    ]
    
    # Add agent recommendation section
    if result.chosen_agent_id:
        output.extend([
            "Empfohlener Agent:",
            f"  {result.chosen_agent_name} ({result.chosen_agent_id}) | "
            f"Confidence: {result.confidence:.2f}",
            "",
            "Begründung:",
            textwrap.fill(result.reason, width=76, initial_indent="  ", 
                         subsequent_indent="  "),
        ])
        
        # Add agent execution results if available
        if agent_response:
            output.extend([
                "",
                "=" * 80,
                f"Ausführung durch {agent_response.agent_name}:",
                "",
                textwrap.fill(agent_response.output, width=76, initial_indent="  ",
                             subsequent_indent="  ")
            ])
    else:
        output.extend([
            "Kein passender Agent gefunden!",
            "",
            "Grund:",
            textwrap.fill(result.reason, width=76, initial_indent="  ",
                         subsequent_indent="  "),
            "",
            "Empfehlung:",
            textwrap.fill(result.action_recommendation, width=76, initial_indent="  ",
                         subsequent_indent="  ")
        ])
    
    output.append("=" * 80)
    return "\n".join(output)


def main():
    """Run the CLI demo."""
    print("\nWillkommen beim Agent Routing System (Prototyp 1)")
    print("=" * 80)
    print("\nBitte beschreiben Sie Ihre Aufgabe. Der Advisor Agent wird den am besten")
    print("geeigneten spezialisierten Agenten empfehlen und die Aufgabe ausführen.\n")
    
    while True:
        # Get user input
        task = input("\nWas ist deine Aufgabe? (oder 'exit' zum Beenden)\n> ").strip()
        
        if task.lower() in ('exit', 'quit', 'q'):
            break
            
        if not task:
            continue
        
        # Get recommendation
        result = advise_best_agent(task)
        
        # Execute the chosen agent if one was found
        agent_response = None
        if result.chosen_agent_id:
            print("\nWähle Agent aus und führe Aufgabe aus...")
            print("Bitte warten...")
            
            # Simulate some processing time
            time.sleep(1.5)
            
            # Get and execute the appropriate agent
            agent_class = get_agent_executor(result.chosen_agent_id)
            if agent_class:
                agent_response = agent_class.execute(task)
        
        # Display results
        print("\n" + format_output(task, result, agent_response))
    
    print("\nDanke für die Nutzung des Agent Routing Systems!\n")


if __name__ == "__main__":
    main()
