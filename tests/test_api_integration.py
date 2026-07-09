from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import POSTGRES_AVAILABLE

pytestmark = pytest.mark.skipif(
    not POSTGRES_AVAILABLE,
    reason="Postgres not reachable at DATABASE_URL; run `docker compose up -d db` to enable these tests",
)

# get_recent_story_candidates() only looks back RECENT_STORY_WINDOW (3 days), so
# these need to be "recent" relative to whenever the test actually runs.
_NOW = datetime.now(timezone.utc)

# Two articles covering the same event (from different outlets) plus one unrelated article.
FAKE_ARTICLES = [
    {
        "title": "Company X ships new chip",
        "source": "Outlet A",
        "url": "https://outlet-a.example.com/chip-story",
        "published_at": _NOW - timedelta(hours=2),
        "content": "Company X announced a new chip today with major performance gains.",
    },
    {
        "title": "X unveils next-gen chip",
        "source": "Outlet B",
        "url": "https://outlet-b.example.com/chip-story",
        "published_at": _NOW - timedelta(hours=1),
        "content": "Outlet B also covers Company X's new chip launch this morning.",
    },
    {
        "title": "Local weather update",
        "source": "Outlet C",
        "url": "https://outlet-c.example.com/weather",
        "published_at": _NOW,
        "content": "Sunny skies expected this weekend across the region.",
    },
]

# High cosine similarity between A and B (same story), low similarity to C.
# Padded to EMBEDDING_DIM=768 to match the pgvector column's fixed dimension.
_PAD = [0.0] * 765
EMBEDDING_A = [1.0, 0.0, 0.0] + _PAD
EMBEDDING_B = [0.99, 0.01, 0.0] + _PAD
EMBEDDING_C = [0.0, 1.0, 0.0] + _PAD
_EMBEDDING_BY_CONTENT = {
    FAKE_ARTICLES[0]["content"]: EMBEDDING_A,
    FAKE_ARTICLES[1]["content"]: EMBEDDING_B,
    FAKE_ARTICLES[2]["content"]: EMBEDDING_C,
}


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Fetching news and calling the local LLM are external services (RSS, Ollama);
    everything else in this file exercises the real API + Postgres/pgvector layer."""
    monkeypatch.setattr(
        "app.routers.articles.news_client.fetch_articles",
        lambda query, **kwargs: FAKE_ARTICLES,
    )
    monkeypatch.setattr(
        "app.routers.articles.embeddings.get_embedding",
        lambda text: _EMBEDDING_BY_CONTENT.get(text, EMBEDDING_C),
    )
    monkeypatch.setattr(
        "app.routers.articles.summarizer.summarize",
        lambda text: f"Summary of: {text[:30]}",
    )
    monkeypatch.setattr(
        "app.routers.articles.summarizer.summarize_story",
        lambda texts, sources: f"Synthesized from {len(texts)} source(s)",
    )


def test_list_articles_empty(client):
    resp = client.get("/articles/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_fetch_without_api_key_is_rejected(client):
    resp = client.post("/articles/fetch", params={"query": "chips"})
    assert resp.status_code in (401, 422)


def test_fetch_with_wrong_api_key_is_rejected(client):
    resp = client.post(
        "/articles/fetch", params={"query": "chips"}, headers={"X-API-Key": "wrong-key"}
    )
    assert resp.status_code == 401


def test_fetch_creates_articles_and_clusters_matching_story(client):
    resp = client.post(
        "/articles/fetch", params={"query": "chips"}, headers={"X-API-Key": "dev-key"}
    )
    assert resp.status_code == 200
    body = resp.json()

    assert body["fetched"] == 3
    assert body["new"] == 3
    assert len(body["articles"]) == 3
    assert all(a["summary"] is not None for a in body["articles"])

    stories_resp = client.get("/stories/")
    stories = stories_resp.json()

    # A and B should cluster into one story; C should be its own story.
    assert len(stories) == 2
    sizes = sorted(
        len(client.get(f"/stories/{s['id']}").json()["articles"]) for s in stories
    )
    assert sizes == [1, 2]

    clustered_story = next(s for s in stories if s["title"] in ("Company X ships new chip",))
    detail = client.get(f"/stories/{clustered_story['id']}").json()
    assert detail["summary"] == "Synthesized from 2 source(s)"
    sources = {a["source"] for a in detail["articles"]}
    assert sources == {"Outlet A", "Outlet B"}


def test_fetch_is_idempotent_on_rerun(client):
    first = client.post(
        "/articles/fetch", params={"query": "chips"}, headers={"X-API-Key": "dev-key"}
    ).json()
    second = client.post(
        "/articles/fetch", params={"query": "chips"}, headers={"X-API-Key": "dev-key"}
    ).json()

    assert first["new"] == 3
    assert second["fetched"] == 3
    assert second["new"] == 0  # all three URLs already exist, deduped by URL

    all_articles = client.get("/articles/").json()
    assert len(all_articles) == 3


def test_get_article_404_for_unknown_id(client):
    resp = client.get("/articles/999999")
    assert resp.status_code == 404


def test_get_story_404_for_unknown_id(client):
    resp = client.get("/stories/999999")
    assert resp.status_code == 404


def test_list_articles_filters_by_query(client, monkeypatch):
    client.post("/articles/fetch", params={"query": "chips"}, headers={"X-API-Key": "dev-key"})

    other_query_articles = [
        {
            "title": "Different topic entirely",
            "source": "Outlet D",
            "url": "https://outlet-d.example.com/other",
            "published_at": datetime(2026, 1, 2, tzinfo=timezone.utc),
            "content": "Something unrelated to chips.",
        }
    ]
    monkeypatch.setattr(
        "app.routers.articles.news_client.fetch_articles",
        lambda query, **kwargs: other_query_articles,
    )
    monkeypatch.setattr(
        "app.routers.articles.embeddings.get_embedding",
        lambda text: [0.5, 0.5, 0.5] + _PAD,
    )
    client.post("/articles/fetch", params={"query": "widgets"}, headers={"X-API-Key": "dev-key"})

    chips_only = client.get("/articles/", params={"query": "chips"}).json()
    assert len(chips_only) == 3
    assert all(a["query"] == "chips" for a in chips_only)
