"""Ready-made checks to pass to evaluate()."""
from .prompts import QUESTION_INSTRUCTIONS


def embedding_check(model="sentence-transformers/all-mpnet-base-v2"):
    """Cosine similarity of sentence embeddings: what a threshold-based semantic cache
    does (pip install fow-cache[embeddings]). Embeddings are memoised per text."""
    from sentence_transformers import SentenceTransformer

    encoder, memo = SentenceTransformer(model), {}

    def embed(text):
        if text not in memo:
            memo[text] = encoder.encode(text, normalize_embeddings=True)
        return memo[text]

    return lambda a, b: float((embed(a) * embed(b)).sum())


def last_message(check):
    """Adapt a question check to conversations by comparing only the final user messages,
    which is what GPTCache's default `last_content` pre-processor does."""
    return lambda a, b: check(a[-1]["content"], b[-1]["content"])


def jev_check(client=None):
    """Jev yes/no: would the cached answer also answer the new question?"""
    from .jev import JevClient

    client = client or JevClient()
    return lambda a, b: client.noul({"cached_question": a, "new_question": b}, QUESTION_INSTRUCTIONS)


def guard_check(guard):
    """The conversation Guard as a check: replays each conversation through it. Makes one
    LLM call per 4 exchanges per conversation plus the rewrites, so it costs real money."""
    def check(a, b):
        return guard.check(guard.replay(a), guard.replay(b)).serve
    return check
