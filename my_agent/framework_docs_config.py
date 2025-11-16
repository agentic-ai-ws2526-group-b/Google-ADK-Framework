"""
Framework Documentation Configuration
Zentrale Verwaltung der offiziellen Dokumentations-Links für alle Frameworks.
"""

# Offizielle Dokumentations-URLs für alle Frameworks
FRAMEWORK_DOCUMENTATION_URLS = {
    "Google ADK": [
        {
            "title": "Agent Development Kit - Official Documentation",
            "url": "https://docs.cloud.google.com/agent-builder/agent-development-kit/overview",
            "source": "official"
        },
        {
            "title": "ADK Open-Source Documentation",
            "url": "https://google.github.io/adk-docs/",
            "source": "open_source"
        }
    ],
    "LangChain": [
        {
            "title": "LangChain - Python Overview",
            "url": "https://docs.langchain.com/oss/python/langchain/overview",
            "source": "official"
        }
    ],
    "LangGraph": [
        {
            "title": "LangGraph - Python Overview",
            "url": "https://docs.langchain.com/oss/python/langgraph/overview",
            "source": "official"
        },
        {
            "title": "LangGraph - API Reference",
            "url": "https://langchain-ai.github.io/langgraph/reference/",
            "source": "reference"
        }
    ],
    "n8n": [
        {
            "title": "n8n Documentation",
            "url": "https://docs.n8n.io/",
            "source": "official"
        }
    ],
    "CrewAI": [
        {
            "title": "CrewAI Documentation",
            "url": "https://docs.crewai.com/",
            "source": "official"
        }
    ],
    "Hugging Face Agents": [
        {
            "title": "Hugging Face Transformers - Agents",
            "url": "https://huggingface.co/docs/transformers/agents",
            "source": "official"
        }
    ],
    "OpenAI Swarm": [
        {
            "title": "OpenAI Swarm - GitHub Repository",
            "url": "https://github.com/openai/swarm",
            "source": "github"
        }
    ],
    "AutoGPT": [
        {
            "title": "AutoGPT - GitHub Repository",
            "url": "https://github.com/Significant-Gravitas/AutoGPT",
            "source": "github"
        }
    ],
    "Zapier": [
        {
            "title": "Zapier Help Center",
            "url": "https://zapier.com/help/",
            "source": "official"
        }
    ]
}


def get_documentation_urls(framework_name: str) -> list:
    """
    Gibt alle Dokumentations-URLs für ein Framework zurück.
    
    Args:
        framework_name: Name des Frameworks (z.B. "LangChain").
        
    Returns:
        Liste von Dicts mit title, url und source.
    """
    return FRAMEWORK_DOCUMENTATION_URLS.get(framework_name, [])


def get_all_frameworks() -> list:
    """Gibt eine Liste aller konfigurierten Frameworks zurück."""
    return list(FRAMEWORK_DOCUMENTATION_URLS.keys())


def print_documentation_index() -> None:
    """Druckt einen schönen Index aller verfügbaren Dokumentationen."""
    print("=" * 70)
    print("📚 Framework Documentation Index")
    print("=" * 70)
    
    for framework, docs in FRAMEWORK_DOCUMENTATION_URLS.items():
        print(f"\n🔹 {framework}")
        for doc in docs:
            print(f"   • {doc['title']}")
            print(f"     → {doc['url']}")
            print(f"     (Quelle: {doc['source']})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print_documentation_index()
