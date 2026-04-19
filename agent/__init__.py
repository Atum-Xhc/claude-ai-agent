"""
claude-ai-agent
~~~~~~~~~~~~~~~
AI Agent z narzędziami oparty na Claude API (Anthropic).
"""

from .agent import ClaudeAgent
from .memory import ConversationMemory
from .tools import TOOLS, execute_tool

__all__ = ["ClaudeAgent", "ConversationMemory", "TOOLS", "execute_tool"]
__version__ = "1.0.0"
