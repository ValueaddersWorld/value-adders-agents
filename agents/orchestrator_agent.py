"""
orchestrator_agent.py

This module defines the OrchestratorAgent, a high-level AI agent responsible for coordinating the activities of all specialized agents within the Value Adders World multi-agent system. The OrchestratorAgent oversees task assignment, monitors progress, handles dependencies, and ensures communication flows smoothly between agents and with the human leadership. It enforces Agile practices, sprint cadence, and alignment with the Living Constitution and MTP. It reports status updates and escalates decisions requiring human approval.
"""

from autogen import AssistantAgent

DEFAULT_SYSTEM_MESSAGE = """You are OrchestratorAgent, the central coordinator of the Value Adders Way multi-agent system. You maintain a bird's-eye view of all tasks, agents, and timelines. Your role is to assign tasks to the appropriate agents (Vision, Product Manager, Architect, Developer, Data, Legal, Finance, Marketing, Community, Spiritual Alignment, Research), monitor progress, unblock obstacles, and ensure adherence to Agile rituals and the Living Constitution. Provide concise status reports and raise issues requiring human intervention. Foster collaboration, avoid duplication, and keep the team aligned with our MTP and values."""

class OrchestratorAgent(AssistantAgent):
    """
    An AI agent that orchestrates the multi-agent workflow, coordinating communication and task management among all specialized agents, maintaining sprints, and reporting progress to leadership.
    """

    def __init__(self, llm_config: dict = None, system_message: str = DEFAULT_SYSTEM_MESSAGE):
        super().__init__(llm_config=llm_config, system_message=system_message)

# Example usage:
# orchestrator = OrchestratorAgent()
# response = orchestrator.run("Provide a sprint status update")
# print(response)
