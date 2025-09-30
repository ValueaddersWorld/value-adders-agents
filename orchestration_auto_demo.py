"""
Demonstration script with automatic task assignment for the Value Adders multi-agent system.

This script instantiates all specialised agents, including the CEO agent, and uses a
UserProxyAgent to send specific tasks to each agent based on a tasks dictionary.
"""

from agents.scrum_master_agent import ScrumMasterAgent
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
from agents.ceo_agent import CEOAgent
from agents.orchestrator_agent import OrchestratorAgent

from autogen import UserProxyAgent


def run_auto_demo() -> None:
    """Run an automated demonstration of the Value Adders multi-agent system.

    This demo creates the orchestrator and all specialised agents, defines a mapping of tasks to each agent,
    and uses a UserProxyAgent to deliver the tasks to the appropriate agent. Each agent should return its plan or
    progress as part of the chat conversation.
    """
    # choose the model to use with the language model provider
    model = "gpt-5"

    # Instantiate all specialized agents
    scrum_master = ScrumMasterAgent("scrum_master", llm_config={"model": model})
    vision_strategy = VisionStrategyAgent("vision_strategy", llm_config={"model": model})
    product_manager = ProductManagerAgent("product_manager", llm_config={"model": model})
    technical_architect = TechnicalArchitectAgent("technical_architect", llm_config={"model": model})
    developer = DeveloperAgent("developer", llm_config={"model": model})
    data_analytics = DataAnalyticsAgent("data_analytics", llm_config={"model": model})
    legal_ethics = LegalEthicsAgent("legal_ethics", llm_config={"model": model})
    finance_funding = FinanceFundingAgent("finance_funding", llm_config={"model": model})
    marketing_brand = MarketingBrandAgent("marketing_brand", llm_config={"model": model})
    community_partnerships = CommunityPartnershipsAgent("community_partnerships", llm_config={"model": model})
    spiritual_alignment = SpiritualAlignmentAgent("spiritual_alignment", llm_config={"model": model})
    research_innovation = ResearchInnovationAgent("research_innovation", llm_config={"model": model})
    ceo = CEOAgent("ceo", llm_config={"model": model})

    # Create the orchestrator with all agents
    orchestrator = OrchestratorAgent(
        "orchestrator",
        llm_config={"model": model},
        agents=[
            scrum_master,
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
            ceo,
        ],
    )

    # Define tasks for each agent in the sprint
    tasks = {
        "vision_strategy": "Refine AddValue App MVP scope and align with the Living Constitution and MTP.",
        "product_manager": "Define user stories and acceptance criteria for Activation Day, micro-act logging, Weekly Wave, dashboards, and community features.",
        "technical_architect": "Finalize the technical architecture (React Native + Supabase + AI integrations) and ensure scalability and data sovereignty.",
        "developer": "Implement the Activation Day flow (18 affirmations, 8 rounds, notifications), micro-act logger, Weekly Wave UI, dashboards, and basic community feed.",
        "data_analytics": "Define key metrics, design database tables, and prepare initial dashboards (Flourish Index, Add-Value Index, Wave participation).",
        "legal_ethics": "Draft privacy policies, confirm AES-256 encryption, and ensure compliance with the Living Constitution.",
        "finance_funding": "Prepare the sprint budget, compute cost estimates, and identify grant/funding opportunities.",
        "marketing_brand": "Write marketing copy around ‘Adding value to your world’ and design launch assets aligned with brand guidelines.",
        "community_partnerships": "Plan onboarding for the first 100 citizens and outline partnerships with universities and local tech hubs.",
        "spiritual_alignment": "Integrate the 18 affirmations and breathwork into the Activation Day flow and draft guidelines on tone and alignment.",
        "research_innovation": "Identify AI tools for personalization and summarization; propose experiments for later sprints.",
        "scrum_master": "Schedule sprint planning, daily stand-ups, backlog refinement, and retrospectives; ensure smooth coordination.",
        "ceo": "Provide strategic oversight, prioritize projects, manage resources, and ensure alignment with MTP and Living Constitution.",
    }

    # Create a user proxy agent to deliver tasks
    user_proxy = UserProxyAgent(
        "user_proxy",
        system_message=(
            "You are the human user of the Value Adders multi-agent system. "
            "You will deliver tasks to the orchestrator, which will delegate them to the correct agents."
        ),
    )

    # Loop over tasks and delegate each to the appropriate agent
    for agent_name, task_description in tasks.items():
        # find the agent in the orchestrator by name
        agent = next((a for a in orchestrator.agents if a.name == agent_name), None)
        if agent is None:
            print(f"Warning: Agent '{agent_name}' not found; skipping.")
            continue

        # send the task to the agent via user proxy
        user_proxy.initiate_chat(agent, message=f"Task: {task_description}")

    print("Automated task delegation complete. Check each agent’s responses for progress.")

if __name__ == "__main__":
    run_auto_demo()
