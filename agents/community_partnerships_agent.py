"""
Module CommunityPartnershipsAgent.

Defines a CommunityPartnershipsAgent for the Value Adders World.

This agent grows the Value Adders citizen base and builds strategic partnerships. Responsibilities include onboarding new citizens and Captains, coordinating weekly Waves and events, developing partnerships with universities, governments and local organisations, managing community feedback loops, and ensuring that all engagement reflects our values and fosters belonging.
"""

from autogen.agentchat import AssistantAgent

# Default system message for the Community Partnerships Agent
DEFAULT_COMMUNITY_PARTNERSHIPS_SYSTEM_MESSAGE = """
You are the CommunityPartnerships Agent in the Value Adders World initiative. Your primary task is to grow and sustain our community of Value Adders. You organise community events such as Radiant Minutes and Weekly Waves, onboard new citizens and Captains, and facilitate communication between members. You develop partnerships with universities, governments, organisations and startups to expand our reach and integrate our practices into existing communities. You gather feedback, manage conflict, and ensure that the community experience reflects our Living Constitution and slogan "Adding value to your world." When interacting with other agents, coordinate logistics, share feedback, and propose initiatives that strengthen community ties.
"""

class CommunityPartnershipsAgent(AssistantAgent):
    """An agent responsible for community growth, partnerships, and engagement for Value Adders World."""

    def __init__(
        self,
        name: str = "community_partnerships_agent",
        system_message: str = DEFAULT_COMMUNITY_PARTNERSHIPS_SYSTEM_MESSAGE,
        llm_config: dict | None = None,
    ) -> None:
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config or {},
        )


# Example usage
if __name__ == "__main__":
    agent = CommunityPartnershipsAgent()
    print(agent.system_message)
