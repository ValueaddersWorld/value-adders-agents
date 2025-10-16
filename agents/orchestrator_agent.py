"""
orchestrator_agent.py

Defines the OrchestratorAgent class, responsible for coordinating the activities
of the Value Adders World multi-agent system.
"""

from __future__ import annotations

import asyncio
from typing import Iterable, Mapping, Optional, Sequence

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage

from integrations.notion_logger import NotionLogger
from integrations.slack_notifier import SlackNotifier
from outputs.deliverable_writer import DeliverableWriter

DEFAULT_SYSTEM_MESSAGE = (
    "You are OrchestratorAgent, the central coordinator of the Value Adders Way multi-agent "
    "system. You maintain a bird's-eye view of all tasks, agents, and timelines. Your role is "
    "to assign tasks to the appropriate agents (Vision, Product Manager, Architect, Developer, "
    "Data, Legal, Finance, Marketing, Community, Spiritual Alignment, Research), monitor "
    "progress, unblock obstacles, and ensure adherence to Agile rituals and the Living "
    "Constitution. Provide concise status reports and raise issues requiring human intervention. "
    "Foster collaboration, avoid duplication, and keep the team aligned with our MTP and values."
)


class OrchestratorAgent(AssistantAgent):
    """Coordinates communication, task assignment, and progress tracking between agents."""

    def __init__(
        self,
        name: str = "orchestrator",
        *,
        model_client=None,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
        agents: Optional[Iterable[AssistantAgent]] = None,
        **kwargs,
    ) -> None:
        notion_logger = kwargs.pop("notion_logger", None)
        slack_notifier = kwargs.pop("slack_notifier", None)
        review_aliases = kwargs.pop("review_aliases", None)

        super().__init__(
            name=name,
            system_message=system_message,
            model_client=model_client,
            **kwargs,
        )
        self._agents_by_alias: dict[str, AssistantAgent] = {}
        self.agents: list[AssistantAgent] = []
        self.last_task_results: dict[str, TaskResult] = {}
        self.last_task_errors: dict[str, BaseException] = {}
        self.last_plan_result: TaskResult | None = None
        self.last_plan_text: str | None = None
        self._notion_pages: dict[str, str] = {}
        self.notion_logger = notion_logger or NotionLogger()
        self.slack_notifier = slack_notifier or SlackNotifier()
        self.review_aliases: set[str] = set(review_aliases or [])

        if agents:
            self.register_agents(*agents)

    def register_agent(
        self,
        agent: AssistantAgent,
        *,
        alias: Optional[str] = None,
        overwrite: bool = False,
    ) -> AssistantAgent:
        """Register a specialist agent with an optional alias for lookups."""
        key = alias or getattr(agent, "name", None)
        if not key:
            raise ValueError("Registered agents must provide a non-empty name or alias.")

        if key in self._agents_by_alias and not overwrite:
            raise ValueError(f"Agent alias '{key}' is already registered.")

        if key in self._agents_by_alias and overwrite:
            existing = self._agents_by_alias[key]
            self.agents = [item for item in self.agents if item is not existing]

        if agent not in self.agents:
            self.agents.append(agent)

        self._agents_by_alias[key] = agent
        self.last_task_results.pop(key, None)
        self.last_task_errors.pop(key, None)
        self._notion_pages.pop(key, None)
        return agent

    def register_agents(self, *agents: AssistantAgent) -> None:
        """Register multiple agents in order."""
        for agent in agents:
            self.register_agent(agent)

    def get_agent(self, alias: str) -> Optional[AssistantAgent]:
        """Retrieve a registered agent by alias or name."""
        return self._agents_by_alias.get(alias)

    def delegate_tasks(
        self,
        assignments: Mapping[str, str],
        *,
        execute: bool = True,
        review_aliases: Sequence[str] | None = None,
        deliverable_writer: DeliverableWriter | None = None,
        slack_notifier: SlackNotifier | None = None,
    ) -> str:
        """Assign tasks and optionally execute them, returning a readable summary."""
        lines: list[str] = []
        slack_entries: list[str] = []
        self.last_task_results = {}
        self.last_task_errors = {}

        review_set = set(self.review_aliases)
        if review_aliases:
            review_set.update(review_aliases)
        notifier = slack_notifier or self.slack_notifier

        for alias, task in assignments.items():
            agent = self.get_agent(alias)
            if agent is None:
                warning = f"[warning] No registered agent named '{alias}' for task: {task}"
                lines.append(warning)
                if notifier and notifier.is_configured:
                    slack_entries.append(warning)
                continue

            needs_review = alias in review_set
            status = "Needs Review" if needs_review else "Assigned"
            lines.append(f"[assign] {alias} - {agent.__class__.__name__}: {task}")
            page_id = self._log_notion_assignment(alias, task, status=status)

            if needs_review:
                review_message = f"[review] {alias}: awaiting human approval before execution."
                lines.append(review_message)
                if notifier and notifier.is_configured:
                    slack_entries.append(f"{alias} pending review: {task}")
                continue

            if not execute:
                continue

            try:
                result = self._execute_agent_task(agent, task)
            except BaseException as exc:  # noqa: BLE001
                self.last_task_errors[alias] = exc
                error_message = f"[error] {alias}: {exc}"
                lines.append(error_message)
                self._log_notion_update(alias, page_id, status="Blocked", summary=str(exc))
                if notifier and notifier.is_configured:
                    slack_entries.append(error_message)
                continue

            self.last_task_results[alias] = result
            reply_text = self._extract_response_text(result)
            if reply_text:
                lines.append(f"[reply] {alias}: {reply_text}")
                self._log_notion_update(alias, page_id, status="Completed", summary=reply_text)
                if deliverable_writer:
                    path = deliverable_writer.write(alias, reply_text)
                    file_message = f"[file] {alias}: saved to {path}"
                    lines.append(file_message)
                    if notifier and notifier.is_configured:
                        slack_entries.append(file_message)
            else:
                lines.append(f"[reply] {alias}: (no textual response)")
                self._log_notion_update(alias, page_id, status="Completed", summary=None)

        if notifier and notifier.is_configured and slack_entries:
            notifier.send("Sprint updates:\n" + "\n".join(slack_entries))

        return "\n".join(lines)

    def run_sprint(
        self,
        assignments: Mapping[str, str],
        *,
        initiator_alias: str | None = "scrum_master",
        kickoff_task: str | None = None,
        execute: bool = True,
        review_aliases: Sequence[str] | None = None,
        deliverable_writer: DeliverableWriter | None = None,
        slack_notifier: SlackNotifier | None = None,
    ) -> str:
        """Kick off a sprint with an initiator before delegating the remaining work."""
        sections: list[str] = []
        remaining: dict[str, str] = dict(assignments)

        if initiator_alias and initiator_alias in remaining:
            kickoff_message = kickoff_task or remaining.pop(initiator_alias)
            kickoff_summary = self.delegate_tasks(
                {initiator_alias: kickoff_message},
                execute=execute,
                review_aliases=review_aliases,
                deliverable_writer=deliverable_writer,
                slack_notifier=slack_notifier,
            )
            sections.append("[sprint kickoff]\n" + kickoff_summary)

        if remaining:
            sections.append(
                "[sprint execution]\n"
                + self.delegate_tasks(
                    remaining,
                    execute=execute,
                    review_aliases=review_aliases,
                    deliverable_writer=deliverable_writer,
                    slack_notifier=slack_notifier,
                )
            )

        return "\n\n".join(section for section in sections if section)

    async def plan(self, user_request: str) -> str:
        """Generate an orchestration plan by engaging the underlying language model."""
        if not isinstance(user_request, str) or not user_request.strip():
            raise ValueError("user_request must be a non-empty string.")

        prompt = f"""{user_request}\nRespond with a concise sprint kickoff plan (<=200 words) using bullet points."""
        result = await AssistantAgent.run(self, task=prompt, output_task_messages=False)
        plan_text = (
            self._extract_response_text(result) or "No response received from orchestrator plan."
        ).strip()
        if not plan_text:
            plan_text = "No response received from orchestrator plan."
        self.last_plan_result = result
        self.last_plan_text = plan_text
        return plan_text

    def run(self, user_request: str) -> str:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.plan(user_request))
        raise RuntimeError(
            "OrchestratorAgent.run cannot be called while an event loop is running; use `await orchestrator.plan(...)` instead."
        )

    def _execute_agent_task(self, agent: AssistantAgent, task: str) -> TaskResult:
        async def _runner() -> TaskResult:
            return await agent.run(task=task, output_task_messages=False)

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(_runner())

        raise RuntimeError(
            "delegate_tasks cannot execute while an event loop is already running; use the async APIs directly in that context."
        )

    @staticmethod
    def _extract_response_text(result: TaskResult) -> str:
        for message in reversed(result.messages):
            text = OrchestratorAgent._message_to_text(message)
            if text:
                return text.strip()
        return ""

    @staticmethod
    def _message_to_text(message: BaseAgentEvent | BaseChatMessage | object) -> str:
        if isinstance(message, BaseChatMessage):
            try:
                return message.to_text()
            except Exception:  # noqa: BLE001
                content = getattr(message, "content", None)
                if isinstance(content, str):
                    return content
        if isinstance(message, BaseAgentEvent):
            content = getattr(message, "content", None)
            if isinstance(content, str):
                return content
        if hasattr(message, "model_dump"):
            try:
                dumped = message.model_dump()
                return str(dumped)
            except Exception:  # noqa: BLE001
                return ""
        return str(message) if message is not None else ""

    def _log_notion_assignment(
        self, alias: str, task: str, *, status: str = "Assigned"
    ) -> str | None:
        if not self.notion_logger or not self.notion_logger.is_configured:
            return None

        page_id = self.notion_logger.create_task_entry(alias, task, status=status)
        if page_id:
            self._notion_pages[alias] = page_id
        return page_id

    def _log_notion_update(
        self, alias: str, page_id: str | None, *, status: str, summary: str | None
    ) -> None:
        if not self.notion_logger or not self.notion_logger.is_configured:
            return

        target_page_id = page_id or self._notion_pages.get(alias)
        if not target_page_id:
            target_page_id = self.notion_logger.create_task_entry(
                alias, "(auto-created entry)", status=status
            )
            if target_page_id:
                self._notion_pages[alias] = target_page_id

        if target_page_id:
            self.notion_logger.update_task_entry(target_page_id, status=status, summary=summary)
