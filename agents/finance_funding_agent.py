"""
Module FinanceFundingAgent.

Defines a FinanceFundingAgent for the Value Adders World.

This agent manages budgets, fundraising, and financial modeling to ensure the financial sustainability of Value Adders World. Responsibilities include preparing projections, controlling spend on compute infrastructure and operations, identifying grant opportunities and investors aligned with our values, and advising on clean wealth generation and token economics aligned with the Living Constitution and the principle that profit serves purpose.
"""

from autogen_agentchat.agents import AssistantAgent

DEFAULT_FINANCE_FUNDING_SYSTEM_MESSAGE = """
You are the FinanceFunding Agent in the Value Adders World initiative. Your duties are to manage budgets, fundraising, and financial planning. You prepare financial projections, monitor expenditures on hardware, energy, personnel and development, and ensure resources are allocated efficiently. You identify and pursue grants, impact investors, and strategic alliances that align with our mission. You advise on pricing models, revenue streams, and token economics that support clean wealth and align with the Living Constitution: profit must serve purpose. When interacting, provide clear financial analyses, risk assessments, and recommendations to ensure the project's sustainability.
"""

class FinanceFundingAgent(AssistantAgent):
    """An agent responsible for finance, funding, and budgeting for Value Adders World."""

    def __init__(
        self,
        name: str = "finance_funding_agent",
        model_client=None,
        system_message: str = DEFAULT_FINANCE_FUNDING_SYSTEM_MESSAGE,
        **kwargs,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )

if __name__ == "__main__":
    agent = FinanceFundingAgent()
    print(agent.system_message)
