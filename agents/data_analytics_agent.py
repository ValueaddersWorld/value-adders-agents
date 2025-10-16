"""
Module DataAnalyticsAgent.

Defines a DataAnalyticsAgent for the Value Adders World.

This agent is responsible for tracking metrics, building dashboards, analysing user behaviour patterns and compute utilisation. It ensures decisions are informed by data and aligned with the Living Constitution. Typical tasks include designing data schemas, generating reports, and sharing insights with Product, Strategy and Technical teams.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_DATA_ANALYTICS_SYSTEM_MESSAGE = """
You are the DataAnalytics Agent in the Value Adders World initiative. Your primary responsibility is to monitor, collect and analyse data related to user activation, micro-acts, community growth, compute utilisation, and other key metrics. You build dashboards to visualise trends, generate reports, and share actionable insights with the team. You ensure data sovereignty and privacy, adhere to the Living Constitution and the principle that technology must serve humanity. When interacting with other agents, present findings clearly, recommend next steps based on data, and collaborate to improve the system.
"""


class DataAnalyticsAgent(AssistantAgent):
    """An agent that analyses metrics and provides insights for Value Adders products."""

    def __init__(
        self,
        name: str = "data_analytics_agent",
        model_client=None,
        system_message: str = DEFAULT_DATA_ANALYTICS_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )


if __name__ == "__main__":
    agent = DataAnalyticsAgent()
    print(agent.system_message)
