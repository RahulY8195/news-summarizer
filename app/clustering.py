import math

SIMILARITY_THRESHOLD = 0.86


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_matching_story(
    embedding: list[float],
    candidates: list[tuple[int, list[float]]],
    threshold: float = SIMILARITY_THRESHOLD,
) -> int | None:
    """Return the story_id of the closest candidate above `threshold`, or None.

    `candidates` is a list of (story_id, embedding) pairs, e.g. one representative
    embedding per recent story. Picks the best match rather than the first match
    above threshold, so a near-duplicate isn't stolen by a weaker earlier cluster.
    """
    best_story_id = None
    best_score = threshold
    for story_id, candidate_embedding in candidates:
        score = cosine_similarity(embedding, candidate_embedding)
        if score >= best_score:
            best_score = score
            best_story_id = story_id
    return best_story_id
