from app.clustering import cosine_similarity, find_matching_story

IDENTICAL = [1.0, 0.0, 0.0]
SIMILAR = [0.95, 0.05, 0.0]
ORTHOGONAL = [0.0, 1.0, 0.0]
OPPOSITE = [-1.0, 0.0, 0.0]


def test_cosine_similarity_identical_vectors_is_one():
    assert cosine_similarity(IDENTICAL, IDENTICAL) == 1.0


def test_cosine_similarity_orthogonal_vectors_is_zero():
    assert cosine_similarity(IDENTICAL, ORTHOGONAL) == 0.0


def test_cosine_similarity_opposite_vectors_is_negative_one():
    assert cosine_similarity(IDENTICAL, OPPOSITE) == -1.0


def test_cosine_similarity_zero_vector_returns_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_find_matching_story_returns_none_with_no_candidates():
    assert find_matching_story(IDENTICAL, []) is None


def test_find_matching_story_matches_close_candidate():
    candidates = [(1, ORTHOGONAL), (2, SIMILAR)]
    assert find_matching_story(IDENTICAL, candidates) == 2


def test_find_matching_story_returns_none_below_threshold():
    candidates = [(1, ORTHOGONAL)]
    assert find_matching_story(IDENTICAL, candidates) is None


def test_find_matching_story_picks_best_not_first_match():
    close_match = [0.99, 0.01, 0.0]
    weak_match = [0.87, 0.13, 0.0]
    candidates = [(1, weak_match), (2, close_match)]
    assert find_matching_story(IDENTICAL, candidates) == 2
