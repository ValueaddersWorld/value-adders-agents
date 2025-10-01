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
"""

from autogen_agentchat.agents import AssistantAgent


class ScrumMasterAgent(AssistantAgent):
    """A specialised AssistantAgent that acts as a Scrum Master."""

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

    def __init__(
        self,
        name: str = "scrum_master",
        model_client=None,
        system_message: str = None,
        **kwargs,
    ):
        if system_message is None:
            system_message = self.DEFAULT_SYSTEM_MESSAGE
        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )


if __name__ == "__main__":
    agent = ScrumMasterAgent()
    print(agent.system_message)
