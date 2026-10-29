"""fow-cache: measure how often a semantic cache serves the wrong answer, and guard
against it in multi-turn chats."""
from .data import load_conversations, load_questions
from .evaluate import Report, evaluate
from .cache import GuardedCache, Hit, InMemoryBackend
from .guard import Conversation, Decision, Entry, Guard, anthropic_llm, merge_fold

__version__ = "0.2.1"
__all__ = ["evaluate", "Report", "load_questions", "load_conversations",
           "Guard", "Conversation", "Entry", "Decision", "anthropic_llm", "merge_fold",
           "GuardedCache", "Hit", "InMemoryBackend"]
