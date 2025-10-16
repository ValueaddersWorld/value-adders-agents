"""Unit tests for Product Manager Agent."""

from unittest.mock import Mock

import pytest

from agents.product_manager_agent import ProductManagerAgent


class TestProductManagerAgentInit:
    """Test ProductManagerAgent initialization."""

    def test_default_initialization(self):
        """Test PM agent initializes with defaults."""
        agent = ProductManagerAgent(model_client=Mock())

        assert agent.name == "product_manager_agent"
        assert "ProductManagerAgent" in agent.system_message

    def test_custom_name(self):
        """Test PM agent with custom name."""
        custom_name = "custom_pm"
        agent = ProductManagerAgent(name=custom_name, model_client=Mock())

        assert agent.name == custom_name

    def test_custom_system_message(self):
        """Test PM agent with custom system message."""
        custom_message = "Custom PM instructions"
        agent = ProductManagerAgent(system_message=custom_message, model_client=Mock())

        assert agent.system_message == custom_message


class TestProductManagerAgentSystemMessage:
    """Test PM agent system message content."""

    def test_system_message_mentions_product_management(self):
        """Test system message mentions product management concepts."""
        agent = ProductManagerAgent(model_client=Mock())
        message = agent.system_message

        pm_concepts = ["product", "feature", "roadmap", "requirements", "user"]
        # At least some PM concepts should be present
        assert any(concept in message.lower() for concept in pm_concepts)

    def test_system_message_is_comprehensive(self):
        """Test system message is comprehensive."""
        agent = ProductManagerAgent(model_client=Mock())
        message = agent.system_message

        assert len(message) > 50

    def test_agent_inherits_from_assistant_agent(self):
        """Test ProductManagerAgent inherits from AssistantAgent."""
        from autogen_agentchat.agents import AssistantAgent

        agent = ProductManagerAgent(model_client=Mock())
        assert isinstance(agent, AssistantAgent)
