"""Daily playbook definitions for orchestrated runs."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Dict
from pathlib import Path

# Default fallback tasks identical to prior sprint configuration
_DEFAULT_TASKS: Dict[str, str] = {
    "ceo": "Set the authoritative priorities for Sprint 1, validate resource allocation, and confirm alignment with the Massive Transformative Purpose.",
    "vision_strategy": "Refine AddValue App MVP scope and align with the Living Constitution and MTP.",
    "product_manager": "Define user stories and acceptance criteria for Activation Day, micro-act logging, Weekly Wave, dashboards, and community features.",
    "technical_architect": "Finalize the technical architecture (React Native + Supabase + AI integrations) and ensure scalability and data sovereignty.",
    "developer": "Implement the Activation Day flow (18 affirmations, 8 rounds, notifications), micro-act logger, Weekly Wave UI, dashboards, and basic community feed.",
    "data_analytics": "Define key metrics, design database tables, and prepare initial dashboards (Flourish Index, AddValue Index, Wave participation).",
    "legal_ethics": "Draft privacy policies, confirm AES-256 encryption, and ensure compliance with the Living Constitution.",
    "finance_funding": "Prepare the sprint budget, compute cost estimates, and identify grant or funding opportunities.",
    "marketing_brand": "Write marketing copy around 'Adding value to your world' and design launch assets aligned with brand guidelines.",
    "community_partnerships": "Plan onboarding for the first 100 citizens and outline partnerships with universities and local tech hubs.",
    "spiritual_alignment": "Integrate the 18 affirmations and breathwork into the Activation Day flow and draft guidelines on tone and alignment.",
    "research_innovation": "Identify AI tools for personalization and summarization; propose experiments for later sprints.",
    "scrum_master": "Initiate Sprint 1 planning, announce assignments, and ensure ceremonies are on the calendar.",
}

_WEEKLY_PLAYBOOK: Dict[int, Dict[str, str]] = {
    # Monday - research heavy
    0: {
        "research_innovation": "Compile latest AI tooling news relevant to personalization and summarization; include citations.",
        "data_analytics": "Pull weekly metrics snapshot for user engagement and prep insights for leadership.",
    },
    # Tuesday - marketing
    1: {
        "marketing_brand": "Draft Product Hunt teaser copy and social posts; include launch visuals requirements.",
        "community_partnerships": "Line up outreach emails for top 50 potential launch supporters.",
    },
    # Wednesday - build
    2: {
        "developer": "Outline implementation tasks for prioritized backlog items; include PR plan.",
        "technical_architect": "Review architecture for upcoming releases and highlight blockers.",
    },
    # Thursday - compliance/finance
    3: {
        "legal_ethics": "Re-audit compliance checklist for new features shipping this sprint.",
        "finance_funding": "Update cost forecast and funding runway after latest spend.",
    },
    # Friday - wrap and vision
    4: {
        "ceo": "Prepare weekly briefing for stakeholders summarizing wins, risks, and asks.",
        "vision_strategy": "Refresh quarterly roadmap based on week's learnings; flag shifts for leadership.",
    },
}


def get_tasks_for_today(today: datetime | None = None) -> Dict[str, str]:
    """Return tasks for today's run using the weekly playbook or fallback."""
    current = today or datetime.utcnow()
    weekday = current.weekday()
    base_tasks = dict(_DEFAULT_TASKS)
    overrides = _WEEKLY_PLAYBOOK.get(weekday)
    if overrides:
        base_tasks.update(overrides)
    manual_override = os.getenv("PLAYBOOK_OVERRIDE")
    if manual_override:
        path = Path(manual_override)
        if path.exists():
            override_tasks = {
                key.strip(): value.strip()
                for key, value in (line.split("=", 1) for line in path.read_text().splitlines() if "=" in line)
            }
            base_tasks.update(override_tasks)
    return base_tasks


__all__ = ["get_tasks_for_today"]

