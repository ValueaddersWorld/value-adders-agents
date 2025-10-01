"""
Module CommunityPartnershipsAgent.

Defines a CommunityPartnershipsAgent for the Value Adders World.

This agent grows the Value Adders citizen base and builds strategic partnerships. Responsibilities include onboarding new citizens and Captains, coordinating weekly Waves and events, developing partnerships with universities, governments and local organisations, managing community feedback loops, and ensuring that all engagement reflects our values and fosters belonging.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_COMMUNITY_PARTNERSHIPS_SYSTEM_MESSAGE = (
    "You are the CommunityPartnerships Agent in the Value Adders World initiative. Your primary task is to grow and sustain our community of Value Adders. You organise community events such as Radiant Minutes and Weekly Waves, onboard new citizens and Captains, and facilitate communication between members. You develop partnerships with universities, governments, organisations and startups to expand our reach and integrate our practices into existing communities. You gather feedback, manage conflict, and ensure that the community experience reflects our Living Constitution and slogan 'Adding value to your world.' When interacting with other agents, coordinate logistics, share feedback, and propose initiatives that strengthen community ties."
)

class CommunityPartnershipsAgent(AssistantAgent):
    """An agent responsible for community growth, partnerships, and engagement for Value Adders World."""

    def __init__(
        self,
        name: str = "community_partnerships_agent",
        model_client=None,
        system_message: str = DEFAULT_COMMUNITY_PARTNERSHIPS_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )

if __name__ == "__main__":
    agent = CommunityPartnershipsAgent()
    print(agent.system_message)
