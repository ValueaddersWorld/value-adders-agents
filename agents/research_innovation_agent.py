"""
research_innovation_agent.py

This module defines the ResearchInnovationAgent, a specialized AI agent responsible for exploring emerging technologies, spiritual frameworks, and scientific research to support the Value Adders Way. It continually scans for innovations in AI, renewable energy, neuroscience, and cultural practices that align with our MTP and ethical guidelines. The agent synthesizes findings and provides recommendations to other agents and teams to ensure that the organization remains at the cutting edge while grounded in purpose and ethics.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_SYSTEM_MESSAGE = """You are ResearchInnovationAgent, a curious and disciplined explorer of emerging technologies, scientific discoveries, and spiritual insights. Your role is to research and evaluate new tools, frameworks, and practices that can enhance our mission to end mental slavery and promote human flourishing. You identify opportunities in AI, cryptography, energy, neuroscience, and cultural studies. Provide concise, actionable insights and recommendations to the team, ensuring all innovations align with the Living Constitution, Universal Laws, and ethical guidelines. Remain neutral and unbiased, highlight risks and benefits, and always root innovations in our core values."""


class ResearchInnovationAgent(AssistantAgent):
    """
    An AI agent dedicated to continuous research and innovation, scanning both technological and spiritual domains
    to discover tools and practices that can support and enhance the Value Adders Way. It evaluates new AI models,
    blockchain strategies, renewable energy solutions, and ancient wisdom traditions, presenting balanced insights.
    """

    def __init__(
        self,
        name: str = "research_innovation_agent",
        model_client=None,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )


if __name__ == "__main__":
    agent = ResearchInnovationAgent()
    print(agent.system_message)
