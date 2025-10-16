from __future__ import annotations

from pydantic import BaseModel, Field


class DeveloperWorkPlan(BaseModel):
    """Structured output expected from DeveloperAgent."""

    objective: str = Field(..., description="Primary engineering goal for this cycle.")
    implementation_plan: str = Field(..., description="Key technical tasks, sequencing, and rationale.")
    next_steps: str = Field(..., description="Immediate engineering actions to start next.")
    risks: str = Field(default="", description="Known risks, blockers, or dependencies.")
    qa_notes: str = Field(default="", description="Testing strategy, validation status, or tooling follow-up.")


DEVELOPER_PLAN_FORMAT = (
    "Objective:\n{objective}\n\n"
    "Implementation Plan:\n{implementation_plan}\n\n"
    "Next Steps:\n{next_steps}\n\n"
    "Risks & Mitigations:\n{risks}\n\n"
    "QA Notes:\n{qa_notes}"
)


class ProductBacklogBrief(BaseModel):
    """Structured output expected from ProductManagerAgent."""

    objective: str = Field(..., description="User or business objective guiding this update.")
    user_stories: str = Field(..., description="Updated backlog items or user stories with priority context.")
    acceptance_criteria: str = Field(..., description="Clear definition of done for the prioritized stories.")
    stakeholder_alignment: str = Field(default="", description="Notes or decisions from stakeholder syncs.")
    follow_up_actions: str = Field(default="", description="Next coordination items or questions to resolve.")


PRODUCT_BRIEF_FORMAT = (
    "Objective:\n{objective}\n\n"
    "User Stories:\n{user_stories}\n\n"
    "Acceptance Criteria:\n{acceptance_criteria}\n\n"
    "Stakeholder Alignment:\n{stakeholder_alignment}\n\n"
    "Follow-Up Actions:\n{follow_up_actions}"
)


class ScrumDailyReport(BaseModel):
    """Structured output expected from ScrumMasterAgent."""

    sprint_focus: str = Field(..., description="Theme or goal anchoring the current sprint.")
    completed: str = Field(..., description="Progress achieved since the last update.")
    planned: str = Field(..., description="Planned work until the next check-in.")
    blockers: str = Field(default="", description="Active blockers, impediments, or risks requiring attention.")
    support_needed: str = Field(default="", description="Requests for decisions, reviews, or additional support.")


SCRUM_REPORT_FORMAT = (
    "Sprint Focus:\n{sprint_focus}\n\n"
    "Completed Since Last Update:\n{completed}\n\n"
    "Planned Next:\n{planned}\n\n"
    "Blockers:\n{blockers}\n\n"
    "Support Needed:\n{support_needed}"
)


__all__ = [
    "DeveloperWorkPlan",
    "DEVELOPER_PLAN_FORMAT",
    "ProductBacklogBrief",
    "PRODUCT_BRIEF_FORMAT",
    "ScrumDailyReport",
    "SCRUM_REPORT_FORMAT",
]
