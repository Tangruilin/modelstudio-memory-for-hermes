"""Hermes Agent memory provider for Alibaba Cloud Bailian (百炼).

This plugin integrates Bailian's long-term memory API as a MemoryProvider
for Hermes Agent, enabling persistent recall across sessions.

Bailian uses a custom REST API protocol, not Mem0-compatible.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://dashscope.aliyuncs.com/api/v2/apps/memory"


class BailianMemoryProvider:
    """Memory provider for Alibaba Cloud Bailian service.

    Implements the MemoryProvider ABC from hermes-agent, exposing
    memory add, search, list, and delete operations as agent tools.

    Attributes:
        name: Provider identifier ('bailian').
        _api_key: DashScope API key for authentication.
        _base_url: Base URL for Bailian memory API.
        _user_id: User identifier for memory operations.
        _session_id: Current session identifier.
        _auto_capture: Whether to auto-capture turns to memory.
        _auto_recall: Whether to prefetch memory before each turn.
        _top_k: Default number of search results.
        _min_score: Default minimum search score threshold.
    """

    def __init__(self) -> None:
        """Initialize provider with default state."""
        self._api_key: Optional[str] = None
        self._base_url: str = BASE_URL
        self._user_id: Optional[str] = None
        self._session_id: str = ""
        self._auto_capture: bool = True
        self._auto_recall: bool = True
        self._top_k: int = 5
        self._min_score: float = 0.0
        self._pending_turns: List[Dict[str, str]] = []

    @property
    def name(self) -> str:
        """Return provider identifier."""
        return "bailian"

    def is_available(self) -> bool:
        """Check if Bailian API key is configured.

        Returns:
            True if DASHSCOPE_API_KEY environment variable is set.
        """
        return os.environ.get("DASHSCOPE_API_KEY") is not None

    def initialize(self, session_id: str, **kwargs) -> None:
        """Initialize provider for a session.

        Args:
            session_id: Hermes session identifier.
            **kwargs: Additional context from Hermes agent:
                - hermes_home: Active HERMES_HOME directory.
                - platform: Platform identifier (cli, telegram, etc.).
                - agent_context: Agent context type.
                - agent_identity: Profile name for scoping.
                - user_id: Platform user identifier.

        Raises:
            ValueError: If required configuration is missing.
        """
        self._session_id = session_id
        self._api_key = os.environ.get("DASHSCOPE_API_KEY")

        # Extract user_id from kwargs or use session_id as fallback
        user_id = kwargs.get("user_id")
        if user_id:
            self._user_id = user_id
        else:
            # Use agent_identity + session_id for per-profile scoping
            identity = kwargs.get("agent_identity", "default")
            self._user_id = f"{identity}_{session_id[:8]}"

        # Load optional config from environment
        self._base_url = os.environ.get(
            "BAILIAN_BASE_URL", BASE_URL
        )
        self._auto_capture = os.environ.get(
            "BAILIAN_AUTO_CAPTURE", "true"
        ).lower() in ("true", "1", "yes")
        self._auto_recall = os.environ.get(
            "BAILIAN_AUTO_RECALL", "true"
        ).lower() in ("true", "1", "yes")
        self._top_k = int(os.environ.get("BAILIAN_TOP_K", "5"))
        self._min_score = float(os.environ.get("BAILIAN_MIN_SCORE", "0.0"))

        if not self._api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY environment variable is required"
            )

        logger.info(
            f"BailianMemoryProvider initialized for user={self._user_id}"
        )

    def system_prompt_block(self) -> str:
        """Return provider info for system prompt.

        Returns:
            Static text describing Bailian memory capabilities.
        """
        return """
You have access to Bailian long-term memory. Use these tools to:
- Store important facts about the user for future sessions
- Search past memories to recall relevant context
- List all stored memories
- Delete outdated or incorrect memories
"""

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """Recall relevant context for the upcoming turn.

        Args:
            query: The user's message to use for recall.
            session_id: Optional session identifier.

        Returns:
            Formatted recall context, or empty string if nothing found.
        """
        if not self._auto_recall or not self._api_key:
            return ""

        try:
            results = self._search_memory(query, top_k=self._top_k)
            if not results:
                return ""

            formatted = "\n\n**Relevant memories from past conversations:**\n"
            for mem in results:
                content = mem.get("content", "")
                score = mem.get("score", 0)
                formatted += f"- {content} (relevance: {score:.2f})\n"
            return formatted
        except Exception as e:
            logger.warning(f"Prefetch failed: {e}")
            return ""

    def sync_turn(self, user_content: str, assistant_content: str, *, session_id: str = "") -> None:
        """Persist a completed turn to memory.

        Args:
            user_content: User's message content.
            assistant_content: Assistant's response content.
            session_id: Optional session identifier.
        """
        if not self._auto_capture or not self._api_key:
            return

        # Queue for batch write
        self._pending_turns.append({
            "user": user_content,
            "assistant": assistant_content,
        })

        # Flush if we have accumulated enough
        if len(self._pending_turns) >= 3:
            self._flush_pending_turns()

    def _flush_pending_turns(self) -> None:
        """Flush accumulated turns to Bailian."""
        if not self._pending_turns:
            return

        messages = []
        for turn in self._pending_turns:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})

        try:
            self._add_memory(messages)
            self._pending_turns.clear()
            logger.debug(f"Flushed {len(messages)} messages to Bailian")
        except Exception as e:
            logger.warning(f"Failed to flush turns: {e}")

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Return tool schemas for Bailian memory operations.

        Returns:
            List of OpenAI-format tool schema dicts.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "bailian_add_memory",
                    "description": "Store a memory to Bailian long-term memory. Use this to remember important facts about the user, preferences, or context for future sessions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The memory content to store. Be specific and factual."
                            },
                        },
                        "required": ["content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "bailian_search_memory",
                    "description": "Search Bailian long-term memory for relevant past memories. Use this to recall facts about the user or past context.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant memories.",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Maximum number of results to return.",
                                "default": 5,
                            },
                            "min_score": {
                                "type": "number",
                                "description": "Minimum relevance score threshold.",
                                "default": 0.0,
                            },
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "bailian_list_memories",
                    "description": "List all stored memories for the current user. Use this to see what information is currently remembered.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "bailian_delete_memory",
                    "description": "Delete a specific memory by ID. Use this to remove outdated or incorrect information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "The ID of the memory to delete.",
                            },
                        },
                        "required": ["memory_id"],
                    },
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        """Handle a tool call for Bailian memory operations.

        Args:
            tool_name: Name of the tool to invoke.
            args: Tool arguments from the model.
            **kwargs: Additional context.

        Returns:
            JSON string with the tool result.

        Raises:
            ValueError: If tool_name is not recognized.
        """
        handlers = {
            "bailian_add_memory": self._handle_add_memory,
            "bailian_search_memory": self._handle_search_memory,
            "bailian_list_memories": self._handle_list_memories,
            "bailian_delete_memory": self._handle_delete_memory,
        }

        handler = handlers.get(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            result = handler(args)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _handle_add_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bailian_add_memory tool call."""
        content = args.get("content", "")
        if not content:
            return {"error": "content is required"}

        messages = [{"role": "user", "content": content}]
        return self._add_memory(messages)

    def _handle_search_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bailian_search_memory tool call."""
        query = args.get("query", "")
        top_k = args.get("top_k", self._top_k)
        min_score = args.get("min_score", self._min_score)

        if not query:
            return {"error": "query is required"}

        results = self._search_memory(query, top_k=top_k, min_score=min_score)
        return {"memories": results, "count": len(results)}

    def _handle_list_memories(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bailian_list_memories tool call."""
        memories = self._list_memories()
        return {"memories": memories, "count": len(memories)}

    def _handle_delete_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bailian_delete_memory tool call."""
        memory_id = args.get("memory_id", "")
        if not memory_id:
            return {"error": "memory_id is required"}

        return self._delete_memory(memory_id)

    # -- Bailian API Client Methods -----------------------------------------

    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to Bailian API.

        Args:
            method: HTTP method (GET, POST, DELETE).
            path: API path (e.g., '/add', '/memory_nodes/search').
            data: Request body for POST requests.

        Returns:
            Response JSON as dict.

        Raises:
            requests.RequestException: On network or API errors.
        """
        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    def _add_memory(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Add memory to Bailian.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            API response with memory_id.
        """
        payload = {
            "user_id": self._user_id,
            "messages": messages,
        }
        return self._make_request("POST", "/add", data=payload)

    def _search_memory(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search Bailian memory.

        Args:
            query: Search query string.
            top_k: Maximum results to return.
            min_score: Minimum relevance score.

        Returns:
            List of memory result dicts.
        """
        payload = {
            "user_id": self._user_id,
            "query": query,
            "top_k": top_k,
            "min_score": min_score,
        }
        response = self._make_request("POST", "/memory_nodes/search", data=payload)
        return response.get("memory_nodes", [])

    def _list_memories(self) -> List[Dict[str, Any]]:
        """List all memories for the user.

        Returns:
            List of memory dicts.
        """
        params = {"user_id": self._user_id}
        # Bailian uses query params for GET
        url = f"{self._base_url}/memory_nodes?user_id={self._user_id}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("memory_nodes", [])

    def _delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Delete a memory by ID.

        Args:
            memory_id: Memory identifier to delete.

        Returns:
            API response.
        """
        url = f"{self._base_url}/memory_nodes/{memory_id}"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        response = requests.delete(url, headers=headers, timeout=30)
        response.raise_for_status()
        return {"success": True, "memory_id": memory_id}

    def shutdown(self) -> None:
        """Clean shutdown - flush pending turns."""
        if self._pending_turns:
            self._flush_pending_turns()
        logger.info("BailianMemoryProvider shutdown complete")

    def on_session_switch(
        self,
        new_session_id: str,
        *,
        parent_session_id: str = "",
        reset: bool = False,
        **kwargs,
    ) -> None:
        """Handle session ID switch mid-process.

        Args:
            new_session_id: The new session identifier.
            parent_session_id: Previous session if meaningful.
            reset: True for genuinely new conversation.
            **kwargs: Additional context.
        """
        if reset:
            # Flush any pending turns for old session
            self._flush_pending_turns()
            # Reset user_id for new session
            identity = kwargs.get("agent_identity", "default")
            self._user_id = f"{identity}_{new_session_id[:8]}"

        self._session_id = new_session_id

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        """Handle session end - flush pending memories.

        Args:
            messages: Full conversation history.
        """
        self._flush_pending_turns()

    def get_config_schema(self) -> List[Dict[str, Any]]:
        """Return config fields for 'hermes memory setup'.

        Returns:
            List of config field dicts.
        """
        return [
            {
                "key": "api_key",
                "description": "DashScope API key (sk-xxx format) for Bailian authentication",
                "secret": True,
                "required": True,
                "env_var": "DASHSCOPE_API_KEY",
                "url": "https://dashscope.console.aliyun.com/apiKey",
            },
            {
                "key": "user_id",
                "description": "User identifier for memory storage. Defaults to session-based ID.",
                "secret": False,
                "required": False,
                "default": "",
            },
            {
                "key": "auto_capture",
                "description": "Automatically capture conversation turns to memory",
                "secret": False,
                "required": False,
                "default": True,
            },
            {
                "key": "auto_recall",
                "description": "Automatically prefetch relevant memories before each turn",
                "secret": False,
                "required": False,
                "default": True,
            },
            {
                "key": "top_k",
                "description": "Maximum number of memories to retrieve in search",
                "secret": False,
                "required": False,
                "default": 5,
            },
            {
                "key": "min_score",
                "description": "Minimum relevance score threshold for memory search",
                "secret": False,
                "required": False,
                "default": 0.0,
            },
        ]

    def save_config(self, values: Dict[str, Any], hermes_home: str) -> None:
        """Write non-secret config to provider config file.

        Args:
            values: Non-secret config values.
            hermes_home: Active HERMES_HOME directory path.
        """
        import pathlib

        config_path = pathlib.Path(hermes_home) / "memory" / "bailian.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write config values
        config = {
            "user_id": values.get("user_id", ""),
            "auto_capture": values.get("auto_capture", True),
            "auto_recall": values.get("auto_recall", True),
            "top_k": values.get("top_k", 5),
            "min_score": values.get("min_score", 0.0),
        }

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Bailian config saved to {config_path}")


def register() -> BailianMemoryProvider:
    """Register function for Hermes plugin discovery.

    Returns:
        BailianMemoryProvider instance.
    """
    return BailianMemoryProvider()