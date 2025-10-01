"""
Demonstration script with automatic task assignment for the Value Adders multi-agent system.

Instantiates the CEO and all specialised agents, registers them with the orchestrator,
and prints a delegation summary for each team member's initial task.
"""

from __future__ import annotations

import os
from typing import Sequence

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

from automation.playbook import get_tasks_for_today
from integrations.slack_notifier import SlackNotifier
from outputs.deliverable_writer import DeliverableWriter
from tools.web_fetch import web_fetch

from agents.ceo_agent import CEOAgent
from agents.vision_strategy_agent import VisionStrategyAgent
from agents.product_manager_agent import ProductManagerAgent
from agents.technical_architect_agent import TechnicalArchitectAgent
from agents.developer_agent import DeveloperAgent
from agents.data_analytics_agent import DataAnalyticsAgent
from agents.legal_ethics_agent import LegalEthicsAgent
from agents.finance_funding_agent import FinanceFundingAgent
from agents.marketing_brand_agent import MarketingBrandAgent
from agents.community_partnerships_agent import CommunityPartnershipsAgent
from agents.spiritual_alignment_agent import SpiritualAlignmentAgent
from agents.research_innovation_agent import ResearchInnovationAgent
from agents.scrum_master_agent import ScrumMasterAgent
from agents.orchestrator_agent import OrchestratorAgent


def _parse_aliases(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [alias.strip() for alias in raw.split(",") if alias.strip()]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() not in {"false", "0", "no"}


def run_auto_demo(tasks: dict[str, str] | None = None) -> None:
    load_dotenv()
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    model_client = OpenAIChatCompletionClient(model=model, parallel_tool_calls=False)

    # Instantiate agents with a shared model client
    ceo = CEOAgent("ceo", model_client=model_client, tools=[web_fetch])
    vision_strategy = VisionStrategyAgent("vision_strategy", model_client=model_client, tools=[web_fetch])
    product_manager = ProductManagerAgent("product_manager", model_client=model_client, tools=[web_fetch])
    technical_architect = TechnicalArchitectAgent("technical_architect", model_client=model_client, tools=[web_fetch])
    developer = DeveloperAgent("developer", model_client=model_client, tools=[web_fetch])
    data_analytics = DataAnalyticsAgent("data_analytics", model_client=model_client, tools=[web_fetch])
    legal_ethics = LegalEthicsAgent("legal_ethics", model_client=model_client, tools=[web_fetch])
    finance_funding = FinanceFundingAgent("finance_funding", model_client=model_client, tools=[web_fetch])
    marketing_brand = MarketingBrandAgent("marketing_brand", model_client=model_client, tools=[web_fetch])
    community_partnerships = CommunityPartnershipsAgent("community_partnerships", model_client=model_client, tools=[web_fetch])
    spiritual_alignment = SpiritualAlignmentAgent("spiritual_alignment", model_client=model_client, tools=[web_fetch])
    research_innovation = ResearchInnovationAgent("research_innovation", model_client=model_client, tools=[web_fetch])
    scrum_master = ScrumMasterAgent("scrum_master", model_client=model_client, tools=[web_fetch])

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

    sprint_brief = (
        "Plan Sprint 1 for the Value Adders World platform, ensuring every team functions under the CEO's direction."
    )
    print(orchestrator.run(sprint_brief))

    active_tasks = tasks or get_tasks_for_today()
    review_aliases: Sequence[str] = _parse_aliases(os.getenv("REVIEW_REQUIRED_ALIASES", "developer,ceo"))
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
