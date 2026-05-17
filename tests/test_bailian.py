"""Unit tests for BailianMemoryProvider."""

from __future__ import annotations

import json
import os
from typing import Any
from unittest import mock

import pytest

import __init__ as bailian


class TestBailianMemoryProvider:
    """Tests for BailianMemoryProvider class."""

    def test_name_property(self) -> None:
        """Test provider name."""
        provider = bailian.BailianMemoryProvider()
        assert provider.name == "bailian"

    def test_is_available_with_api_key(self) -> None:
        """Test is_available returns True when API key is set."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            assert provider.is_available() is True

    def test_is_available_without_api_key(self) -> None:
        """Test is_available returns False when API key is not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            provider = bailian.BailianMemoryProvider()
            assert provider.is_available() is False

    def test_initialize_with_api_key(self) -> None:
        """Test initialize with API key in environment."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="user-abc")
            assert provider._api_key == "sk-test"
            assert provider._user_id == "user-abc"
            assert provider._session_id == "session-123"

    def test_initialize_without_api_key_raises(self) -> None:
        """Test initialize raises ValueError without API key."""
        with mock.patch.dict(os.environ, {}, clear=True):
            provider = bailian.BailianMemoryProvider()
            with pytest.raises(ValueError, match="DASHSCOPE_API_KEY"):
                provider.initialize("session-123")

    def test_initialize_with_user_id_from_env(self) -> None:
        """Test user_id from BAILIAN_USER_ID environment variable."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "env-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            assert provider._user_id == "env-user"

    def test_initialize_kwargs_overrides_env_user_id(self) -> None:
        """Test kwargs user_id overrides BAILIAN_USER_ID env var."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "env-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="kwargs-user")
            assert provider._user_id == "kwargs-user"

    def test_initialize_without_user_id_raises(self) -> None:
        """Test initialize raises ValueError without user_id."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            with pytest.raises(ValueError, match="user_id is required"):
                provider.initialize("session-123")

    def test_initialize_user_id_from_config_file(self, tmp_path: Any) -> None:
        """Test user_id loaded from config file."""
        config_file = tmp_path / "memory" / "bailian.json"
        config_file.parent.mkdir(parents=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"user_id": "config-user"}, f)

        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", hermes_home=str(tmp_path))
            assert provider._user_id == "config-user"

    def test_system_prompt_block(self) -> None:
        """Test system_prompt_block returns expected content."""
        provider = bailian.BailianMemoryProvider()
        prompt = provider.system_prompt_block()
        assert "Bailian long-term memory" in prompt
        assert "Store important facts" in prompt

    def test_get_tool_schemas(self) -> None:
        """Test get_tool_schemas returns correct schemas."""
        provider = bailian.BailianMemoryProvider()
        schemas = provider.get_tool_schemas()
        assert len(schemas) == 4

        names = [s["function"]["name"] for s in schemas]
        assert "bailian_add_memory" in names
        assert "bailian_search_memory" in names
        assert "bailian_list_memories" in names
        assert "bailian_delete_memory" in names

    def test_get_config_schema(self) -> None:
        """Test get_config_schema returns correct fields."""
        provider = bailian.BailianMemoryProvider()
        config = provider.get_config_schema()
        assert len(config) == 6

        keys = [c["key"] for c in config]
        assert "api_key" in keys
        assert "user_id" in keys
        assert "auto_capture" in keys
        assert "auto_recall" in keys
        assert "top_k" in keys
        assert "min_score" in keys

    def test_handle_tool_call_unknown_raises(self) -> None:
        """Test handle_tool_call raises for unknown tool."""
        provider = bailian.BailianMemoryProvider()
        with pytest.raises(ValueError, match="Unknown tool"):
            provider.handle_tool_call("unknown_tool", {})

    def test_handle_add_memory_empty_content(self) -> None:
        """Test add_memory with empty content returns error."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "test-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            result = json.loads(provider.handle_tool_call("bailian_add_memory", {}))
            assert result["error"] == "content is required"

    def test_handle_search_memory_empty_query(self) -> None:
        """Test search_memory with empty query returns error."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "test-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            result = json.loads(provider.handle_tool_call("bailian_search_memory", {}))
            assert result["error"] == "query is required"

    def test_handle_delete_memory_empty_id(self) -> None:
        """Test delete_memory with empty ID returns error."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "test-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            result = json.loads(provider.handle_tool_call("bailian_delete_memory", {}))
            assert result["error"] == "memory_id is required"

    def test_prefetch_disabled(self) -> None:
        """Test prefetch returns empty when auto_recall is False."""
        with mock.patch.dict(
            os.environ,
            {
                "DASHSCOPE_API_KEY": "sk-test",
                "BAILIAN_USER_ID": "test-user",
                "BAILIAN_AUTO_RECALL": "false",
            },
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            result = provider.prefetch("test query")
            assert result == ""

    def test_sync_turn_disabled(self) -> None:
        """Test sync_turn does nothing when auto_capture is False."""
        with mock.patch.dict(
            os.environ,
            {
                "DASHSCOPE_API_KEY": "sk-test",
                "BAILIAN_USER_ID": "test-user",
                "BAILIAN_AUTO_CAPTURE": "false",
            },
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            provider.sync_turn("user msg", "assistant msg")
            assert len(provider._pending_turns) == 0

    def test_sync_turn_queues_messages(self) -> None:
        """Test sync_turn queues messages for batch write."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "test-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            provider.sync_turn("user msg", "assistant msg")
            assert len(provider._pending_turns) == 1
            assert provider._pending_turns[0]["user"] == "user msg"

    def test_shutdown_flushes_pending(self) -> None:
        """Test shutdown flushes pending turns."""
        with mock.patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "sk-test", "BAILIAN_USER_ID": "test-user"},
        ):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123")
            provider._pending_turns.append({"user": "u", "assistant": "a"})
            with mock.patch.object(provider, "_flush_pending_turns") as mock_flush:
                provider.shutdown()
                mock_flush.assert_called_once()

    def test_register_function(self) -> None:
        """Test register() properly registers BailianMemoryProvider."""
        mock_ctx = mock.Mock()
        bailian.register(mock_ctx)
        mock_ctx.register_memory_provider.assert_called_once()
        provider = mock_ctx.register_memory_provider.call_args[0][0]
        assert isinstance(provider, bailian.BailianMemoryProvider)


class TestBailianAPIClient:
    """Tests for Bailian API client methods."""

    def test_add_memory_success(self) -> None:
        """Test _add_memory makes correct API call."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="user-abc")

            mock_response = mock.Mock()
            mock_response.json.return_value = {"memory_id": "mem-123"}
            mock_response.raise_for_status = mock.Mock()

            with mock.patch("requests.request", return_value=mock_response):
                result = provider._add_memory(
                    [{"role": "user", "content": "test"}]
                )
                assert result["memory_id"] == "mem-123"

    def test_search_memory_success(self) -> None:
        """Test _search_memory makes correct API call."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="user-abc")

            mock_response = mock.Mock()
            mock_response.json.return_value = {
                "memory_nodes": [{"id": "mem-1", "content": "test"}]
            }
            mock_response.raise_for_status = mock.Mock()

            with mock.patch("requests.request", return_value=mock_response):
                result = provider._search_memory("query")
                assert len(result) == 1
                assert result[0]["id"] == "mem-1"

    def test_list_memories_success(self) -> None:
        """Test _list_memories makes correct API call."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="user-abc")

            mock_response = mock.Mock()
            mock_response.json.return_value = {
                "memory_nodes": [{"id": "mem-1"}]
            }
            mock_response.raise_for_status = mock.Mock()

            with mock.patch("requests.get", return_value=mock_response):
                result = provider._list_memories()
                assert len(result) == 1

    def test_delete_memory_success(self) -> None:
        """Test _delete_memory makes correct API call."""
        with mock.patch.dict(os.environ, {"DASHSCOPE_API_KEY": "sk-test"}):
            provider = bailian.BailianMemoryProvider()
            provider.initialize("session-123", user_id="user-abc")

            mock_response = mock.Mock()
            mock_response.raise_for_status = mock.Mock()

            with mock.patch("requests.delete", return_value=mock_response):
                result = provider._delete_memory("mem-123")
                assert result["success"] is True
                assert result["memory_id"] == "mem-123"


class TestSaveConfig:
    """Tests for save_config method."""

    def test_save_config_creates_file(self, tmp_path: Any) -> None:
        """Test save_config creates config file."""
        provider = bailian.BailianMemoryProvider()
        hermes_home = str(tmp_path)

        provider.save_config(
            {
                "user_id": "test-user",
                "auto_capture": True,
                "auto_recall": True,
                "top_k": 10,
                "min_score": 0.5,
            },
            hermes_home,
        )

        config_file = tmp_path / "memory" / "bailian.json"
        assert config_file.exists()

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
        assert config["user_id"] == "test-user"
        assert config["top_k"] == 10
