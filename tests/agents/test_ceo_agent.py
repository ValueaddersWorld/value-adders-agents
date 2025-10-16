"""Unit tests for CEO Agent."""

from unittest.mock import Mock

import pytest

from agents.ceo_agent import CEOAgent


class TestCEOAgentInit:
    """Test CEOAgent initialization."""

    def test_default_initialization(self):
        """Test CEO agent initializes with defaults."""
        agent = CEOAgent(model_client=Mock())

        assert agent.name == "ceo_agent"
        assert "CEOAgent" in agent.system_message
        assert "Chief Executive Officer" in agent.system_message

    def test_custom_name(self):
        """Test CEO agent with custom name."""
        custom_name = "custom_ceo"
        agent = CEOAgent(name=custom_name, model_client=Mock())

        assert agent.name == custom_name

    def test_custom_system_message(self):
        """Test CEO agent with custom system message."""
        custom_message = "Custom CEO instructions"
        agent = CEOAgent(system_message=custom_message, model_client=Mock())

        assert agent.system_message == custom_message


class TestCEOAgentSystemMessage:
    """Test CEO agent system message content."""

    def test_system_message_mentions_leadership(self):
        """Test system message mentions leadership concepts."""
        agent = CEOAgent(model_client=Mock())
        message = agent.system_message

        leadership_terms = ["strategic", "vision", "leadership", "executive"]
        # At least one leadership term should be present
        assert any(term in message.lower() for term in leadership_terms)

    def test_system_message_mentions_value_adders(self):
        """Test system message mentions Value Adders."""
        agent = CEOAgent(model_client=Mock())
        message = agent.system_message

        assert "Value Adders" in message or "value adders" in message.lower()

    def test_system_message_is_comprehensive(self):
        """Test system message is comprehensive."""
        agent = CEOAgent(model_client=Mock())
        message = agent.system_message

        # CEO message should be substantial
        assert len(message) > 50

    def test_agent_inherits_from_assistant_agent(self):
        """Test CEOAgent inherits from AssistantAgent."""
        from autogen_agentchat.agents import AssistantAgent

        agent = CEOAgent(model_client=Mock())
        assert isinstance(agent, AssistantAgent)
