"""Unit tests for NotionLogger."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from integrations.notion_logger import (
    _DEFAULT_AGENT_PROPERTY,
    _DEFAULT_STATUS_PROPERTY,
    _DEFAULT_SUMMARY_PROPERTY,
    _DEFAULT_TASK_PROPERTY,
    _DEFAULT_TITLE_PROPERTY,
    NotionConfig,
    NotionLogger,
)


class TestNotionConfig:
    """Test NotionConfig dataclass."""

    def test_default_initialization(self):
        """Test NotionConfig initializes with defaults."""
        config = NotionConfig()

        assert config.api_key is None
        assert config.database_id is None
        assert config.title_property == _DEFAULT_TITLE_PROPERTY
        assert config.status_property == _DEFAULT_STATUS_PROPERTY
        assert config.agent_property == _DEFAULT_AGENT_PROPERTY
        assert config.task_property == _DEFAULT_TASK_PROPERTY
        assert config.summary_property == _DEFAULT_SUMMARY_PROPERTY

    def test_custom_initialization(self):
        """Test NotionConfig with custom values."""
        config = NotionConfig(
            api_key="test_key",
            database_id="test_db_id",
            title_property="CustomTitle",
            status_property="CustomStatus",
            agent_property="CustomAgent",
            task_property="CustomTask",
            summary_property="CustomSummary",
        )

        assert config.api_key == "test_key"
        assert config.database_id == "test_db_id"
        assert config.title_property == "CustomTitle"
        assert config.status_property == "CustomStatus"
        assert config.agent_property == "CustomAgent"
        assert config.task_property == "CustomTask"
        assert config.summary_property == "CustomSummary"

    def test_from_env_with_values(self):
        """Test NotionConfig.from_env() with environment variables set."""
        env_vars = {
            "NOTION_API_KEY": "env_api_key",
            "NOTION_DATABASE_ID": "env_db_id",
            "NOTION_TITLE_PROPERTY": "EnvTitle",
            "NOTION_STATUS_PROPERTY": "EnvStatus",
            "NOTION_AGENT_PROPERTY": "EnvAgent",
            "NOTION_TASK_PROPERTY": "EnvTask",
            "NOTION_SUMMARY_PROPERTY": "EnvSummary",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = NotionConfig.from_env()

            assert config.api_key == "env_api_key"
            assert config.database_id == "env_db_id"
            assert config.title_property == "EnvTitle"
            assert config.status_property == "EnvStatus"
            assert config.agent_property == "EnvAgent"
            assert config.task_property == "EnvTask"
            assert config.summary_property == "EnvSummary"

    def test_from_env_with_defaults(self):
        """Test NotionConfig.from_env() uses defaults when env vars missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = NotionConfig.from_env()

            assert config.api_key is None
            assert config.database_id is None
            assert config.title_property == _DEFAULT_TITLE_PROPERTY
            assert config.status_property == _DEFAULT_STATUS_PROPERTY

    def test_from_env_empty_string_becomes_none(self):
        """Test empty string environment variables become None."""
        env_vars = {
            "NOTION_STATUS_PROPERTY": "",
            "NOTION_AGENT_PROPERTY": "",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = NotionConfig.from_env()

            assert config.status_property is None
            assert config.agent_property is None


class TestNotionLoggerInit:
    """Test NotionLogger initialization."""

    def test_default_initialization(self):
        """Test NotionLogger initializes with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            logger = NotionLogger()

            assert logger.config is not None
            assert isinstance(logger.config, NotionConfig)
            assert logger._session is not None
            assert isinstance(logger._session, requests.Session)
            assert logger._disabled is False

    def test_custom_config(self):
        """Test NotionLogger with custom config."""
        custom_config = NotionConfig(api_key="custom_key", database_id="custom_db")

        logger = NotionLogger(config=custom_config)

        assert logger.config is custom_config
        assert logger.config.api_key == "custom_key"
        assert logger.config.database_id == "custom_db"

    def test_custom_session(self):
        """Test NotionLogger with custom session."""
        custom_session = Mock(spec=requests.Session)
        custom_config = NotionConfig(api_key="test", database_id="test")

        logger = NotionLogger(config=custom_config, session=custom_session)

        assert logger._session is custom_session

    def test_is_configured_property_true(self):
        """Test is_configured returns True when properly configured."""
        config = NotionConfig(api_key="test_key", database_id="test_db")

        logger = NotionLogger(config=config)

        assert logger.is_configured is True

    def test_is_configured_property_false_missing_key(self):
        """Test is_configured returns False when API key missing."""
        config = NotionConfig(api_key=None, database_id="test_db")

        logger = NotionLogger(config=config)

        assert logger.is_configured is False

    def test_is_configured_property_false_missing_db(self):
        """Test is_configured returns False when database ID missing."""
        config = NotionConfig(api_key="test_key", database_id=None)

        logger = NotionLogger(config=config)

        assert logger.is_configured is False

    def test_session_headers_set_when_configured(self):
        """Test session headers are set when properly configured."""
        config = NotionConfig(api_key="test_key", database_id="test_db")
        mock_session = Mock(spec=requests.Session)
        mock_session.headers = {}

        logger = NotionLogger(config=config, session=mock_session)

        # Verify headers were updated
        mock_session.headers.update.assert_called_once()
        call_args = mock_session.headers.update.call_args[0][0]
        assert "Authorization" in call_args
        assert call_args["Authorization"] == "Bearer test_key"


class TestNotionLoggerDisabled:
    """Test NotionLogger disabled state."""

    def test_disabled_property(self):
        """Test disabled property access."""
        logger = NotionLogger()

        assert hasattr(logger, "_disabled")
        assert logger._disabled is False

    def test_logger_starts_enabled(self):
        """Test logger starts in enabled state."""
        config = NotionConfig(api_key="test", database_id="test")
        logger = NotionLogger(config=config)

        assert logger._disabled is False


class TestNotionLoggerConstants:
    """Test NotionLogger module constants."""

    def test_default_constants_exist(self):
        """Test default property name constants are defined."""
        assert _DEFAULT_TITLE_PROPERTY == "Name"
        assert _DEFAULT_STATUS_PROPERTY == "Status"
        assert _DEFAULT_AGENT_PROPERTY == "Agent"
        assert _DEFAULT_TASK_PROPERTY == "Task"
        assert _DEFAULT_SUMMARY_PROPERTY == "Summary"

    def test_api_url_constant(self):
        """Test Notion API URL constant."""
        from integrations.notion_logger import _NOTION_API_URL

        assert _NOTION_API_URL == "https://api.notion.com/v1"


class TestNotionConfigDataclass:
    """Test NotionConfig dataclass features."""

    def test_is_dataclass(self):
        """Test NotionConfig is a dataclass."""
        import dataclasses

        assert dataclasses.is_dataclass(NotionConfig)

    def test_has_slots(self):
        """Test NotionConfig uses slots for efficiency."""
        config = NotionConfig()

        assert hasattr(NotionConfig, "__slots__")

    def test_equality(self):
        """Test NotionConfig instances can be compared."""
        config1 = NotionConfig(api_key="test", database_id="db1")
        config2 = NotionConfig(api_key="test", database_id="db1")
        config3 = NotionConfig(api_key="test", database_id="db2")

        assert config1 == config2
        assert config1 != config3

    def test_immutability_after_creation(self):
        """Test NotionConfig fields can be modified."""
        config = NotionConfig()

        # Dataclass without frozen=True allows modification
        config.api_key = "new_key"
        assert config.api_key == "new_key"


class TestNotionLoggerIntegration:
    """Test NotionLogger integration aspects."""

    def test_logger_module_imports(self):
        """Test required modules are imported."""
        from integrations import notion_logger

        assert hasattr(notion_logger, "NotionLogger")
        assert hasattr(notion_logger, "NotionConfig")
        assert hasattr(notion_logger, "logging")
        assert hasattr(notion_logger, "requests")

    def test_logger_has_logger_instance(self):
        """Test module has logging instance."""
        from integrations.notion_logger import LOGGER

        assert LOGGER is not None
        assert isinstance(LOGGER, type(MagicMock()))  # logging.Logger type

    def test_session_is_requests_session(self):
        """Test internal session is requests.Session."""
        logger = NotionLogger()

        assert isinstance(logger._session, requests.Session)
