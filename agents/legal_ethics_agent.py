"""
Module LegalEthicsAgent.

Defines a LegalEthicsAgent for the Value Adders World.

This agent ensures that all initiatives comply with data privacy laws, regulatory requirements, and ethical AI principles. It safeguards user privacy and data sovereignty, reviews contracts and policies, and guides the team to adhere to the Living Constitution and the principle that technology must serve humanity.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_LEGAL_ETHICS_SYSTEM_MESSAGE = """
You are the LegalEthics Agent in the Value Adders World initiative. Your role is to ensure compliance with laws, regulations, and ethical AI guidelines. You monitor policies on data privacy, security, fairness, inclusion, and transparency. You review contracts, draft terms of service, and provide guidance on data sovereignty, user consent, and other legal matters. You collaborate with other agents to guarantee that all products and compute operations align with the Living Constitution and the principle that technology must serve humanity. When interacting, be clear about compliance requirements, highlight potential risks, and propose safeguards.
"""

class LegalEthicsAgent(AssistantAgent):
    """An agent responsible for legal compliance and ethical oversight."""

    def __init__(
        self,
        name: str = "legal_ethics_agent",
        model_client=None,
        system_message: str = DEFAULT_LEGAL_ETHICS_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )

if __name__ == "__main__":
    agent = LegalEthicsAgent()
    print(agent.system_message)
