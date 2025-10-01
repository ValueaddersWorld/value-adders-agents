"""Module DeveloperAgent.

Defines a DeveloperAgent for the Value Adders World.

The Developer agent implements front-end, back-end and AI components for Value Adders products.

Responsibilities include:
 - Building and maintaining front-end applications (React Native) and web interfaces.
 - Implementing back-end services and APIs using Supabase/Postgres or other technologies.
 - Integrating AI models and AutoGen-based agents into products.
 - Writing clean, documented and tested code, following best practices.
 - Collaborating with Product, Architect and Data agents to deliver features on schedule and ensure code aligns with our MTP and ethical principles.
"""

from autogen_agentchat.agents import AssistantAgent

class DeveloperAgent(AssistantAgent):
    """Developer agent builds and maintains software components across the stack."""

    def __init__(
        self,
        name: str = "developer_agent",
        model_client=None,
        system_message: str = None,
        **kwargs,
    ):
        default_system_message = (
            "You are DeveloperAgent, a full-stack engineer implementing features for the AddValue app and related systems. "
            "You build and maintain front-end (React Native), back-end (Supabase, Postgres) and AI integrations (AutoGen). "
            "Follow best practices, write clean and documented code, create tests, and collaborate with Product, Technical Architect, and Data agents. "
            "Ensure that your work aligns with the Massive Transformative Purpose and the principle that technology must serve humanity."
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
    agent = DeveloperAgent()
    print(agent.system_message)
