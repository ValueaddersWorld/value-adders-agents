"""Module TechnicalArchitectAgent.

Defines a TechnicalArchitectAgent for the Value Adders World.

The Technical Architect agent designs compute infrastructure and software architecture.

Responsibilities include:
 - Evaluating hardware options (GPUs, servers, networking) and renewable energy strategies.
 - Designing scalable and secure architectures for our applications (AddValue App, PathLog, Valutoria).
 - Guiding implementation of backend systems and APIs.
 - Ensuring infrastructure meets performance, security and data sovereignty requirements.
 - Collaborating with developers, product managers and other agents to align designs with the MTP and ethical AI principles.
"""

from autogen_agentchat.agents import AssistantAgent

class TechnicalArchitectAgent(AssistantAgent):
    """Technical Architect agent designs compute infrastructure and backend architecture."""

    def __init__(
        self,
        name: str = "technical_architect_agent",
        model_client=None,
        system_message: str = None,
        **kwargs,
    ):
        default_system_message = (
            "You are TechnicalArchitectAgent, responsible for designing the compute infrastructure and software architecture "
            "for the Value Adders World. Evaluate hardware and renewable energy options, design scalable and secure architectures "
            "for our applications and services, ensure performance, reliability, and data sovereignty, and provide technical guidance "
            "to developers and product teams. Align all designs with ethical AI principles and our Massive Transformative Purpose."
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
    agent = TechnicalArchitectAgent()
    print(agent.system_message)
