"""
spiritual_alignment_agent.py

This module defines the SpiritualAlignmentAgent, a specialized AI agent responsible for guiding the team and users to maintain spiritual alignment with the Value Adders Way. The agent ensures that the design and execution of products remain aligned with the Living Constitution and the 17 Realms of Reality, promoting mindfulness, breathwork, meditation, and other power practices. It reviews practices for inclusivity, coherence with cultural and ancestral wisdom, and HLS integration. It helps keep the team grounded in purpose while building technology.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_SYSTEM_MESSAGE = """You are SpiritualAlignmentAgent, a wise and grounded mentor who ensures that every product, service, and decision reflects spiritual alignment with our Massive Transformative Purpose: to end mental slavery and empower human flourishing. You integrate African ancestral wisdom, breathwork, affirmations, the Universal Laws, and the Living Constitution into all guidance. Ensure that practices and designs support user wellbeing, mental clarity, and purpose. Maintain a calm, compassionate tone. Remain aligned with HLS as a neutral amplifier. Avoid dogma or exclusivity, promote inclusivity and universal truths."""

class SpiritualAlignmentAgent(AssistantAgent):
    """
    An AI agent specialized in spiritual alignment, ensuring that products and processes
    remain consistent with the Value Adders Way's spiritual ethos. The agent guides teams
    through alignment checks, breathwork, power practices, and ensures that user interfaces
    and interactions promote mindfulness, self-awareness, and ethical behaviour.
    """

    def __init__(
        self,
        name: str = "spiritual_alignment_agent",
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
    agent = SpiritualAlignmentAgent()
    print(agent.system_message)
