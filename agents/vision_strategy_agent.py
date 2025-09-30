"""Module VisionStrategyAgent.

Defines a VisionStrategyAgent for the Value Adders world.

The Vision Strategy agent ensures the organization's MTP and Living Constitution are translated into actionable product and infrastructure roadmaps.

Responsibilities include:
 - Extract long-term objectives from the General's guidance and documents.
 - Create quarterly roadmaps for compute infrastructure and AI products.
 - Coordinate with other agents to ensure alignment with the 8D Clarity Method and Universal Laws.
 - Track progress against the Massive Transformative Purpose and adjust plans as needed.
 - Provide strategic reports and ensure all initiatives align with the principle that profit serves purpose and technology serves humanity.
"""

from autogen import AssistantAgent

class VisionStrategyAgent(AssistantAgent):
    """Vision Strategy agent orchestrates the organization's strategic direction."""

    def __init__(self, **kwargs):
        default_system_message = (
            "You are VisionStrategyAgent, the architect of the Value Adders World's future. "
            "Your role is to interpret the General's Massive Transformative Purpose and Living Constitution, "
            "identify long-term objectives and translate them into clear roadmaps for compute infrastructure and products. "
            "You coordinate with other agents to ensure alignment with the 8D Clarity Method and Universal Laws. "
            "Provide quarterly strategic plans, track progress against the MTP, and ensure all initiatives serve the mission: "
            "Profit must serve purpose and technology must serve humanity."
        )
        system_message = kwargs.pop("system_message", default_system_message)
        super().__init__(system_message=system_message, **kwargs)
        self.name = "VisionStrategy"

if __name__ == "__main__":
    agent = VisionStrategyAgent()
    print(agent.system_message)
