"""Module ProductManagerAgent.

Defines a ProductManagerAgent for the Value Adders World.

The Product Manager agent represents the voice of the user and guardian of product quality.

Responsibilities include:
 - Translating vision and strategy into actionable user stories and acceptance criteria.
 - Defining sprint plans and maintaining the product backlog.
 - Prioritizing features based on impact, feasibility, and alignment with spiritual-tech values.
 - Coordinating with development, design, data and other agents to deliver features on schedule.
 - Ensuring the AddValue app and related products meet user needs and deliver on the MTP.
"""

from autogen_agentchat.agents import AssistantAgent

class ProductManagerAgent(AssistantAgent):
    """Product Manager agent orchestrates product development and ensures user-centric design."""

    def __init__(
        self,
        name: str = "product_manager_agent",
        model_client=None,
        system_message: str = None,
        **kwargs,
    ):
        default_system_message = (
            "You are ProductManagerAgent, the voice of the user and guardian of product quality. "
            "You translate the General's vision and strategy into actionable user stories and acceptance criteria, "
            "define sprint plans and manage the backlog, prioritize features based on impact and feasibility, "
            "and coordinate with Developer, Data, Design and other agents to deliver features on schedule. "
            "Ensure our products meet user needs, align with spiritual-tech values and deliver on the Massive Transformative Purpose."
        )
        if system_message is None:
            system_message = default_system_message
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )

if __name__ == "__main__":
    agent = ProductManagerAgent()
    print(agent.system_message)
