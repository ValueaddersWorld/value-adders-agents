"""
Orchestration script for the Value Adders multi-agent system.

This script demonstrates how to instantiate the various specialized agents defined in the
agents package and coordinate their work using the OrchestratorAgent. The orchestrator
assigns tasks, monitors progress and ensures alignment with the Living Constitution and
ethical guidelines.
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
from agents.orchestrator_agent import OrchestratorAgent

def run_demo() -> None:
    """Run a demonstration of the Value Adders multi-agent system."""
    # choose the language model to use with AutoGen
    model = "gpt-5"

    # instantiate each specialized agent with a unique name and model configuration
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

    # create the orchestrator and provide the list of agents it should coordinate
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
        ],
    )

    # example user request: plan the first sprint for the AddValue App MVP
    user_request = (
        "Plan Sprint 1 for the Value Adders World platform. "
        "Produce a backlog for the AddValue App MVP including Activation Day, micro-act logging, "
        "Weekly Wave, dashboards and community features. Assign tasks to each agent accordingly "
        "and ensure alignment with our Living Constitution and ethical guidelines."
    )

    # run the orchestrator with the user request
    result = orchestrator.run(user_request)
    # print the result to the console
    print(result)

if __name__ == "__main__":
    run_demo()
