from autogen_agentchat.agents import AssistantAgent

class VisionStrategyAgent(AssistantAgent):
    """Vision Strategy agent orchestrates the organization's strategic direction."""

    def __init__(self, name: str = "vision_strategy", model_client=None, **kwargs):
        default_system_message = (
            "You are VisionStrategyAgent, the architect of the Value Adders World's future. "
            "Your role is to interpret the General's Massive Transformative Purpose and Living Constitution, "
            "identify long-term objectives and translate them into clear roadmaps for compute infrastructure and products. "
            "You coordinate with other agents to ensure alignment with the 8D Clarity Method and Universal Laws. "
            "Provide quarterly strategic plans, track progress against the MTP, and ensure all initiatives serve the mission: "
            "Profit must serve purpose and technology must serve humanity."
        )
        system_message = kwargs.pop("system_message", default_system_message)
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs
        )

if __name__ == "__main__":
    agent = VisionStrategyAgent()
    print(agent.system_message)