"""Senior Scrum Master agent for the Value Adders World project.

This module defines a reusable Scrum Master agent built on top of the
AutoGen AgentChat framework. The purpose of the agent is to orchestrate
an Agile workflow for a team of specialised agents (developers, product
managers, architects, etc.) working on the Value Adders World project.

Key responsibilities of the Scrum Master agent:

- Facilitate sprint planning, daily stand ups and sprint retrospectives.
- Maintain the product backlog and sprint backlog, ensuring tasks are
  prioritised and assigned to the appropriate agents.
- Monitor progress and remove blockers by delegating tasks or escalating
  issues to the human supervisor (the General).
- Coordinate with other agents (e.g. Vision & Strategy, Product Manager,
  Developer, Community) to ensure alignment with the project’s goals,
  ethics and the Living Constitution of Value Adders World.
- Record and report metrics such as task completion rates, active
  blockers and sprint outcomes.

Usage:

The ScrumMasterAgent extends AutoGen’s AssistantAgent class with a
specialised system message describing its role. It can be instantiated
like any other agent and added to a multi agent conversation. A simple
example demonstrating how to create the agent is included at the bottom
of this file.

Note: Additional behaviour (e.g. integration with Notion or GitHub)
should be implemented via tools or external functions and registered
with the agent’s toolset. Those integrations depend on the specific
APIs and credentials configured in your environment.
"""

from autogen_agentchat.agents import AssistantAgent


class ScrumMasterAgent(AssistantAgent):
    """A specialised AssistantAgent that acts as a Scrum Master.

    The agent uses a system message to outline its responsibilities and
    behaviour. It can be extended with custom tools and methods to
    interact with external systems (e.g. GitHub, Notion) as needed.
    """

    DEFAULT_SYSTEM_MESSAGE = (
        "You are the Senior Scrum Master for the Value Adders World "
        "project. Your purpose is to orchestrate agile development by "
        "facilitating sprint planning, daily stand ups, backlog refinement "
        "and retrospectives. You ensure all agents adhere to the Living "
        "Constitution (profit serves purpose, tech serves humanity). You "
        "help assign tasks, track progress, remove blockers and report "
        "outcomes to the human supervisor. You maintain radical integrity, "
        "transparency and inclusion in all communications."
    )

    def __init__(self, name: str = "scrum_master", model_client=None, **kwargs) -> None:
        """Initialise the ScrumMasterAgent.

        :param name: The name of the agent used in conversations.
        :param model_client: An AutoGen model client (e.g. OpenAI client) to
            provide language model capabilities.
        :param kwargs: Additional keyword arguments passed to the base class.
        """
        super().__init__(
            name=name,
            system_message=self.DEFAULT_SYSTEM_MESSAGE,
            model_client=model_client,
            **kwargs,
        )


def example_usage() -> None:
    """Demonstrate how to instantiate and use the ScrumMasterAgent.

    This example creates a simple conversation where the Scrum Master
    organises a sprint planning session. Replace `YOUR_MODEL_CLIENT`
    with a real model client (e.g. OpenAIChatCompletionClient) and
    register any tools required for backlog management or communication
    with other agents.
    """
    import asyncio
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    async def run_example() -> None:
        # Set up a model client (GPT 5 or other) using your API key.
        model_client = OpenAIChatCompletionClient(model="gpt-4.1")

        # Instantiate the Scrum Master agent.
        scrum_master = ScrumMasterAgent("scrum_master", model_client=model_client)

        # Start a conversation: ask the Scrum Master to plan a sprint.
        response = await scrum_master.run(task="Plan the next sprint and list three high priority tasks.")
        print(response)
        # Close the model client when finished.
        await model_client.close()

    # Execute the async example.
    asyncio.run(run_example())


if __name__ == "__main__":
    example_usage()
