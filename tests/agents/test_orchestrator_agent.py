"""Unit tests for OrchestratorAgent."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from autogen_agentchat.agents import AssistantAgent

from agents.orchestrator_agent import DEFAULT_SYSTEM_MESSAGE, OrchestratorAgent


class TestOrchestratorAgentInit:
    """Test OrchestratorAgent initialization."""

    def test_default_initialization(self):
        """Test orchestrator initializes with default values."""
        agent = OrchestratorAgent(model_client=Mock())

        assert agent.name == "orchestrator"
        assert agent.system_message == DEFAULT_SYSTEM_MESSAGE
        assert agent.agents == []
        assert agent.last_task_results == {}
        assert agent.last_task_errors == {}
        assert agent.last_plan_result is None
        assert agent.last_plan_text is None
        assert isinstance(agent._agents_by_alias, dict)
        assert len(agent._agents_by_alias) == 0

    def test_custom_name_and_message(self):
        """Test orchestrator with custom name and system message."""
        custom_name = "custom_orchestrator"
        custom_message = "Custom system message"

        agent = OrchestratorAgent(
            name=custom_name, system_message=custom_message, model_client=Mock()
        )

        assert agent.name == custom_name
        assert agent.system_message == custom_message

    def test_with_notion_logger_and_slack_notifier(self):
        """Test orchestrator with custom integrations."""
        mock_notion = Mock()
        mock_slack = Mock()

        agent = OrchestratorAgent(
            model_client=Mock(), notion_logger=mock_notion, slack_notifier=mock_slack
        )

        assert agent.notion_logger is mock_notion
        assert agent.slack_notifier is mock_slack

    def test_with_review_aliases(self):
        """Test orchestrator with review aliases."""
        aliases = ["dev", "pm", "architect"]

        agent = OrchestratorAgent(model_client=Mock(), review_aliases=aliases)

        assert agent.review_aliases == set(aliases)

    def test_with_agents_parameter(self):
        """Test orchestrator initialized with agents."""
        agent1 = Mock(spec=AssistantAgent, name="agent1")
        agent2 = Mock(spec=AssistantAgent, name="agent2")

        orchestrator = OrchestratorAgent(model_client=Mock(), agents=[agent1, agent2])

        assert len(orchestrator.agents) == 2
        assert agent1 in orchestrator.agents
        assert agent2 in orchestrator.agents
        assert "agent1" in orchestrator._agents_by_alias
        assert "agent2" in orchestrator._agents_by_alias


class TestOrchestratorAgentRegistration:
    """Test agent registration methods."""

    def test_register_single_agent(self):
        """Test registering a single agent."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent = Mock(spec=AssistantAgent, name="test_agent")

        result = orchestrator.register_agent(agent)

        assert result is agent
        assert agent in orchestrator.agents
        assert orchestrator._agents_by_alias["test_agent"] is agent

    def test_register_agent_with_alias(self):
        """Test registering agent with custom alias."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent = Mock(spec=AssistantAgent, name="test_agent")

        orchestrator.register_agent(agent, alias="custom_alias")

        assert agent in orchestrator.agents
        assert orchestrator._agents_by_alias["custom_alias"] is agent

    def test_register_agent_duplicate_raises_error(self):
        """Test registering duplicate agent alias raises error."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent1 = Mock(spec=AssistantAgent, name="test_agent")
        agent2 = Mock(spec=AssistantAgent, name="test_agent")

        orchestrator.register_agent(agent1)

        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register_agent(agent2)

    def test_register_agent_duplicate_with_overwrite(self):
        """Test overwriting registered agent."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent1 = Mock(spec=AssistantAgent, name="test_agent")
        agent2 = Mock(spec=AssistantAgent, name="test_agent")

        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2, overwrite=True)

        assert agent2 in orchestrator.agents
        assert agent1 not in orchestrator.agents
        assert orchestrator._agents_by_alias["test_agent"] is agent2

    def test_register_agent_without_name_raises_error(self):
        """Test registering agent without name raises error."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent = Mock(spec=AssistantAgent)
        agent.name = None

        with pytest.raises(ValueError, match="must provide a non-empty name"):
            orchestrator.register_agent(agent)

    def test_register_multiple_agents(self):
        """Test registering multiple agents at once."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent1 = Mock(spec=AssistantAgent, name="agent1")
        agent2 = Mock(spec=AssistantAgent, name="agent2")
        agent3 = Mock(spec=AssistantAgent, name="agent3")

        orchestrator.register_agents(agent1, agent2, agent3)

        assert len(orchestrator.agents) == 3
        assert all(agent in orchestrator.agents for agent in [agent1, agent2, agent3])
        assert len(orchestrator._agents_by_alias) == 3

    def test_register_agent_clears_previous_state(self):
        """Test re-registering agent clears previous state."""
        orchestrator = OrchestratorAgent(model_client=Mock())
        agent = Mock(spec=AssistantAgent, name="test_agent")

        # Register and add state
        orchestrator.register_agent(agent)
        orchestrator.last_task_results["test_agent"] = Mock()
        orchestrator.last_task_errors["test_agent"] = Exception("test")
        orchestrator._notion_pages["test_agent"] = "page_id"

        # Re-register with overwrite
        orchestrator.register_agent(agent, overwrite=True)

        assert "test_agent" not in orchestrator.last_task_results
        assert "test_agent" not in orchestrator.last_task_errors
        assert "test_agent" not in orchestrator._notion_pages


class TestOrchestratorIntegrations:
    """Test orchestrator integrations with Notion and Slack."""

    def test_notion_logger_default(self):
        """Test default Notion logger is created."""
        with patch("agents.orchestrator_agent.NotionLogger") as mock_notion_class:
            mock_instance = Mock()
            mock_notion_class.return_value = mock_instance

            agent = OrchestratorAgent(model_client=Mock())

            assert agent.notion_logger is not None

    def test_slack_notifier_default(self):
        """Test default Slack notifier is created."""
        with patch("agents.orchestrator_agent.SlackNotifier") as mock_slack_class:
            mock_instance = Mock()
            mock_slack_class.return_value = mock_instance

            agent = OrchestratorAgent(model_client=Mock())

            assert agent.slack_notifier is not None

    def test_custom_integrations_override_defaults(self):
        """Test custom integrations override defaults."""
        custom_notion = Mock()
        custom_slack = Mock()

        agent = OrchestratorAgent(
            model_client=Mock(), notion_logger=custom_notion, slack_notifier=custom_slack
        )

        assert agent.notion_logger is custom_notion
        assert agent.slack_notifier is custom_slack


class TestOrchestratorStateManagement:
    """Test orchestrator state management."""

    def test_task_results_tracking(self):
        """Test task results are tracked."""
        orchestrator = OrchestratorAgent(model_client=Mock())

        assert orchestrator.last_task_results == {}

        mock_result = Mock()
        orchestrator.last_task_results["agent1"] = mock_result

        assert orchestrator.last_task_results["agent1"] is mock_result

    def test_task_errors_tracking(self):
        """Test task errors are tracked."""
        orchestrator = OrchestratorAgent(model_client=Mock())

        assert orchestrator.last_task_errors == {}

        test_error = Exception("test error")
        orchestrator.last_task_errors["agent1"] = test_error

        assert orchestrator.last_task_errors["agent1"] is test_error

    def test_plan_result_tracking(self):
        """Test plan results are tracked."""
        orchestrator = OrchestratorAgent(model_client=Mock())

        assert orchestrator.last_plan_result is None
        assert orchestrator.last_plan_text is None

        mock_plan_result = Mock()
        orchestrator.last_plan_result = mock_plan_result
        orchestrator.last_plan_text = "test plan"

        assert orchestrator.last_plan_result is mock_plan_result
        assert orchestrator.last_plan_text == "test plan"

    def test_notion_pages_tracking(self):
        """Test Notion page IDs are tracked."""
        orchestrator = OrchestratorAgent(model_client=Mock())

        assert orchestrator._notion_pages == {}

        orchestrator._notion_pages["agent1"] = "page_id_123"

        assert orchestrator._notion_pages["agent1"] == "page_id_123"


class TestOrchestratorSystemMessage:
    """Test orchestrator system message content."""

    def test_default_system_message_content(self):
        """Test default system message contains key concepts."""
        assert "OrchestratorAgent" in DEFAULT_SYSTEM_MESSAGE
        assert "central coordinator" in DEFAULT_SYSTEM_MESSAGE
        assert "Value Adders" in DEFAULT_SYSTEM_MESSAGE
        assert "multi-agent" in DEFAULT_SYSTEM_MESSAGE
        assert "task" in DEFAULT_SYSTEM_MESSAGE.lower()
        assert "agent" in DEFAULT_SYSTEM_MESSAGE.lower()

    def test_mentions_key_agents(self):
        """Test system message mentions key specialist agents."""
        key_agents = [
            "Vision",
            "Product Manager",
            "Architect",
            "Developer",
            "Data",
            "Legal",
            "Finance",
            "Marketing",
            "Community",
            "Spiritual",
            "Research",
        ]

        for agent_type in key_agents:
            assert agent_type in DEFAULT_SYSTEM_MESSAGE

    def test_mentions_agile_concepts(self):
        """Test system message mentions Agile concepts."""
        agile_concepts = ["Agile", "progress", "collaboration"]

        for concept in agile_concepts:
            assert (
                concept in DEFAULT_SYSTEM_MESSAGE
                or concept.lower() in DEFAULT_SYSTEM_MESSAGE.lower()
            )
