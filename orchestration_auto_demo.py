"""
Demonstration script with automatic task assignment for the Value Adders multi-agent system.

Instantiates the CEO and all specialised agents, registers them with the orchestrator,
and prints a delegation summary for each team member's initial task.
"""

from __future__ import annotations

import logging
import os
from typing import Sequence

from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

from agents.ceo_agent import CEOAgent
from agents.community_partnerships_agent import CommunityPartnershipsAgent
from agents.data_analytics_agent import DataAnalyticsAgent
from agents.developer_agent import DeveloperAgent
from agents.finance_funding_agent import FinanceFundingAgent
from agents.legal_ethics_agent import LegalEthicsAgent
from agents.marketing_brand_agent import MarketingBrandAgent
from agents.orchestrator_agent import OrchestratorAgent
from agents.product_manager_agent import ProductManagerAgent
from agents.research_innovation_agent import ResearchInnovationAgent
from agents.scrum_master_agent import ScrumMasterAgent
from agents.spiritual_alignment_agent import SpiritualAlignmentAgent
from agents.technical_architect_agent import TechnicalArchitectAgent
from agents.vision_strategy_agent import VisionStrategyAgent
from automation.playbook import get_tasks_for_today
from integrations.notion_task_loader import NotionTaskLoader
from integrations.slack_notifier import SlackNotifier
from outputs.deliverable_writer import DeliverableWriter
from tools.web_fetch import WEB_FETCH_TOOL

LOGGER = logging.getLogger(__name__)


def _parse_aliases(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [alias.strip() for alias in raw.split(",") if alias.strip()]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"false", "0", "no"}


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _resolve_active_tasks(
    *,
    tasks_override: dict[str, str] | None,
    notion_loader: NotionTaskLoader | None,
    base_tasks: dict[str, str],
) -> dict[str, str]:
    """Merge default tasks with Notion context when available."""
    if tasks_override is not None:
        return tasks_override

    loader = notion_loader or NotionTaskLoader()
    if not loader.is_configured:
        return base_tasks

    try:
        merged = loader.generate_follow_up_tasks(base_tasks)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Failed to merge Notion follow-up tasks: %s", exc)
        return base_tasks

    return merged or base_tasks


def run_auto_demo(
    tasks: dict[str, str] | None = None, *, notion_loader: NotionTaskLoader | None = None
) -> None:
    load_dotenv()
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    max_tokens = _env_int("OPENAI_MAX_TOKENS", 600)
    client_kwargs: dict[str, object] = {"model": model}
    if max_tokens is not None:
        client_kwargs["max_tokens"] = max_tokens
    model_client = OpenAIChatCompletionClient(**client_kwargs)

    # Instantiate agents with a shared model client
    ceo = CEOAgent("ceo", model_client=model_client, tools=[WEB_FETCH_TOOL])
    vision_strategy = VisionStrategyAgent(
        "vision_strategy", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    product_manager = ProductManagerAgent(
        "product_manager", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    technical_architect = TechnicalArchitectAgent(
        "technical_architect", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    developer = DeveloperAgent("developer", model_client=model_client, tools=[WEB_FETCH_TOOL])
    data_analytics = DataAnalyticsAgent(
        "data_analytics", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    legal_ethics = LegalEthicsAgent(
        "legal_ethics", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    finance_funding = FinanceFundingAgent(
        "finance_funding", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    marketing_brand = MarketingBrandAgent(
        "marketing_brand", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    community_partnerships = CommunityPartnershipsAgent(
        "community_partnerships", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    spiritual_alignment = SpiritualAlignmentAgent(
        "spiritual_alignment", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    research_innovation = ResearchInnovationAgent(
        "research_innovation", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )
    scrum_master = ScrumMasterAgent(
        "scrum_master", model_client=model_client, tools=[WEB_FETCH_TOOL]
    )

    orchestrator = OrchestratorAgent("orchestrator", model_client=model_client)
    orchestrator.register_agents(
        ceo,
        vision_strategy,
        product_manager,
        technical_architect,
        developer,
        data_analytics,
        legal_ethics,
        finance_funding,
        marketing_brand,
        community_partnerships,
        spiritual_alignment,
        research_innovation,
        scrum_master,
    )

    sprint_brief = "Plan Sprint 1 for the Value Adders World platform, ensuring every team functions under the CEO's direction."
    print(orchestrator.run(sprint_brief))

    base_tasks = get_tasks_for_today()
    active_tasks = _resolve_active_tasks(
        tasks_override=tasks,
        notion_loader=notion_loader,
        base_tasks=base_tasks,
    )
    review_aliases: Sequence[str] = _parse_aliases(os.getenv("REVIEW_REQUIRED_ALIASES", ""))
    notifier = SlackNotifier()
    deliverable_writer: DeliverableWriter | None = None
    if _env_bool("WRITE_DELIVERABLES", True):
        deliverable_writer = DeliverableWriter()

    sprint_summary = orchestrator.run_sprint(
        active_tasks,
        initiator_alias=os.getenv("SPRINT_INITIATOR", "scrum_master"),
        execute=_env_bool("AUTO_EXECUTE", True),
        review_aliases=review_aliases,
        deliverable_writer=deliverable_writer,
        slack_notifier=notifier,
    )

    print("\nSprint summary:\n")
    print(sprint_summary)


if __name__ == "__main__":
    run_auto_demo()
