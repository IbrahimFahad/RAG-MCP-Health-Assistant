import nltk
from transformers import AutoTokenizer

# Use the same tokenizer as our embedding model to count tokens accurately
_tokenizer = None

def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
    return _tokenizer

def count_tokens(text: str) -> int:
    """Count how many tokens a text string uses."""
    tokenizer = get_tokenizer()
    return len(tokenizer.encode(text, add_special_tokens=False))

def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    NLTK handles English well. For Arabic, we fall back to
    splitting on common Arabic sentence-ending punctuation.
    """
    try:
        sentences = nltk.sent_tokenize(text)
        # If NLTK returned only 1 sentence for a long text, use newline/punctuation fallback
        if len(sentences) <= 2 and len(text) > 300:
            fallback = _split_arabic_sentences(text)
            if len(fallback) > len(sentences):
                sentences = fallback
        return [s.strip() for s in sentences if s.strip()]
    except Exception:
        return _split_arabic_sentences(text)

def _split_arabic_sentences(text: str) -> list[str]:
    """Fallback sentence splitter for Arabic and mixed text using punctuation and newlines."""
    import re
    # Split on: sentence-ending punctuation followed by whitespace, OR plain newlines
    sentences = re.split(r'(?<=[.!?؟۔])\s+|\n+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(
    text: str,
    max_tokens: int = 400,
    overlap_sentences: int = 2
) -> list[str]:
    """
    Split text into overlapping chunks, each under max_tokens.

    Args:
        text: The full document text to chunk.
        max_tokens: Max tokens per chunk (default 400, leaves room for
                    the 'passage: ' prefix and special tokens within 512 limit).
        overlap_sentences: How many sentences to repeat between chunks
                           to preserve context at boundaries.

    Returns:
        List of text chunks.
    """
    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_token_count = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If a single sentence exceeds max_tokens, split it by words
        if sentence_tokens > max_tokens:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
            chunks.append(sentence[:2000])  # hard cap for runaway sentences
            current_sentences = []
            current_token_count = 0
            continue

        # If adding this sentence would exceed the limit, save current chunk
        if current_token_count + sentence_tokens > max_tokens and current_sentences:
            chunks.append(" ".join(current_sentences))
            # Keep last N sentences as overlap for next chunk
            current_sentences = current_sentences[-overlap_sentences:]
            current_token_count = sum(count_tokens(s) for s in current_sentences)

        current_sentences.append(sentence)
        current_token_count += sentence_tokens

    # Don't forget the last chunk
    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks
