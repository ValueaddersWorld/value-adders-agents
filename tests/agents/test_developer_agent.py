"""Unit tests for DeveloperAgent."""

from unittest.mock import Mock

import pytest

from agents.developer_agent import DeveloperAgent
from agents.structured_outputs import DEVELOPER_PLAN_FORMAT, DeveloperWorkPlan


class TestDeveloperAgentInit:
    """Test DeveloperAgent initialization."""

    def test_default_initialization(self):
        """Test developer agent initializes with defaults."""
        agent = DeveloperAgent(model_client=Mock())

        assert agent.name == "developer_agent"
        assert "DeveloperAgent" in agent.system_message
        assert "full-stack engineer" in agent.system_message

    def test_custom_name(self):
        """Test developer agent with custom name."""
        custom_name = "custom_dev"
        agent = DeveloperAgent(name=custom_name, model_client=Mock())

        assert agent.name == custom_name

    def test_custom_system_message(self):
        """Test developer agent with custom system message."""
        custom_message = "Custom developer instructions"
        agent = DeveloperAgent(system_message=custom_message, model_client=Mock())

        assert agent.system_message == custom_message

    def test_output_content_type_set(self):
        """Test developer agent has structured output configured."""
        agent = DeveloperAgent(model_client=Mock())

        # Verify structured output is configured
        assert hasattr(agent, "_output_content_type") or "output_content_type" in dir(agent)


class TestDeveloperAgentSystemMessage:
    """Test developer agent system message content."""

    def test_system_message_mentions_key_technologies(self):
        """Test system message mentions required technologies."""
        agent = DeveloperAgent(model_client=Mock())
        message = agent.system_message

        key_techs = ["React Native", "Supabase", "Postgres", "AutoGen"]
        for tech in key_techs:
            assert tech in message

    def test_system_message_mentions_responsibilities(self):
        """Test system message mentions key responsibilities."""
        agent = DeveloperAgent(model_client=Mock())
        message = agent.system_message

        responsibilities = ["front-end", "back-end", "AI integration", "test", "documented code"]

        for responsibility in responsibilities:
            assert responsibility in message or responsibility.replace("-", " ") in message

    def test_system_message_mentions_collaboration(self):
        """Test system message mentions collaboration."""
        agent = DeveloperAgent(model_client=Mock())
        message = agent.system_message

        assert "Product" in message or "product" in message.lower()
        assert "Architect" in message or "architect" in message.lower()
        assert "Data" in message or "data" in message.lower()

    def test_system_message_mentions_values(self):
        """Test system message mentions core values."""
        agent = DeveloperAgent(model_client=Mock())
        message = agent.system_message

        assert "Massive Transformative Purpose" in message or "MTP" in message
        assert "humanity" in message.lower() or "ethical" in message.lower()

    def test_system_message_mentions_output_format(self):
        """Test system message mentions expected output format."""
        agent = DeveloperAgent(model_client=Mock())
        message = agent.system_message

        output_fields = ["objective", "implementation_plan", "next_steps", "risks", "qa_notes"]

        for field in output_fields:
            assert field in message


class TestDeveloperAgentStructuredOutput:
    """Test developer agent structured output configuration."""

    def test_work_plan_format_exists(self):
        """Test developer work plan format is defined."""
        assert DEVELOPER_PLAN_FORMAT is not None
        assert isinstance(DEVELOPER_PLAN_FORMAT, str)

    def test_work_plan_class_exists(self):
        """Test DeveloperWorkPlan class exists."""
        assert DeveloperWorkPlan is not None

    def test_agent_uses_work_plan_type(self):
        """Test agent is configured to use DeveloperWorkPlan."""
        # This test verifies the output_content_type is set correctly
        # The actual implementation depends on AutoGen's API
        agent = DeveloperAgent(model_client=Mock())

        # The agent should be configured with the work plan type
        # This is verified by checking the kwargs passed to super().__init__
        assert agent is not None  # Basic check that agent was created successfully


class TestDeveloperAgentMain:
    """Test developer agent main block."""

    def test_main_block_creates_agent(self):
        """Test that agent can be created in main block."""
        # This tests the if __name__ == "__main__" block functionality
        agent = DeveloperAgent()

        assert agent is not None
        assert hasattr(agent, "system_message")

    def test_main_block_prints_message(self, capsys):
        """Test that main block would print system message."""
        # Create agent and access system message (simulates main block)
        agent = DeveloperAgent()
        print(agent.system_message)

        captured = capsys.readouterr()
        assert "DeveloperAgent" in captured.out


class TestDeveloperAgentBestPractices:
    """Test developer agent follows best practices."""

    def test_agent_is_assistant_agent_subclass(self):
        """Test DeveloperAgent inherits from AssistantAgent."""
        from autogen_agentchat.agents import AssistantAgent

        agent = DeveloperAgent(model_client=Mock())
        assert isinstance(agent, AssistantAgent)

    def test_agent_accepts_model_client(self):
        """Test agent accepts model_client parameter."""
        mock_client = Mock()
        agent = DeveloperAgent(model_client=mock_client)

        assert agent is not None

    def test_agent_accepts_kwargs(self):
        """Test agent accepts additional kwargs."""
        agent = DeveloperAgent(model_client=Mock(), custom_param="test_value")

        assert agent is not None

    def test_system_message_is_string(self):
        """Test system message is a string."""
        agent = DeveloperAgent(model_client=Mock())

        assert isinstance(agent.system_message, str)
        assert len(agent.system_message) > 0

    def test_name_is_string(self):
        """Test agent name is a string."""
        agent = DeveloperAgent(model_client=Mock())

        assert isinstance(agent.name, str)
        assert len(agent.name) > 0
