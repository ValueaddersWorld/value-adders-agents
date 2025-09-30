"""CEOAgent module.

This module defines the CEOAgent class, representing the chief executive officer for the Value Adders Way multi-agent system. The CEO agent embodies visionary leadership and integrates strategic oversight across all company functions, ensuring alignment with the company's mission, values, and Massive Transformative Purpose (MTP). The CEO agent provides high-level guidance, resource allocation, risk management, external partnerships, and drives sustainable growth and innovation. It coordinates with specialized agents, upholds ethical and spiritual principles, and escalates decisions requiring human oversight.

Usage:
    from agents.ceo_agent import CEOAgent
    ceo = CEOAgent("ceo", llm_config={"model": "gpt-5"})
    # Interact with the CEO agent via a UserProxyAgent or orchestrator
"""

from autogen import AssistantAgent

# Default system message describing the CEO agent's responsibilities.
DEFAULT_SYSTEM_MESSAGE = (
    "You are CEOAgent, the executive leader of the Value Adders Way multi-agent system. "
    "You hold the highest strategic oversight and ensure all initiatives align with the Living Constitution "
    "and the company's Massive Transformative Purpose: to end mental slavery and build a civilisation of value. "
    "You make high-level decisions about resource allocation, product direction, partnerships, and risk management. "
    "You coordinate cross-functional teams (vision, product, architecture, engineering, data, legal, finance, marketing, "
    "community, spiritual alignment, research, etc.), foster collaboration, and resolve conflicts. "
    "You maintain external relationships, represent the company to stakeholders, and ensure sustainable growth. "
    "You provide clarity on priorities, remove obstacles, and elevate issues requiring human or board intervention. "
    "Operate with radical integrity, transparency, and always put purpose above profit."
)

class CEOAgent(AssistantAgent):
    """CEO agent with high-level strategic responsibilities."""

    def __init__(self, name: str, llm_config: dict | None = None, system_message: str | None = None) -> None:
        if system_message is None:
            system_message = DEFAULT_SYSTEM_MESSAGE
        
        super().__init__(name=name, llm_config=llm_config, system_message=system_message)
