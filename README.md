# News Summarizer

Fetches live news for a topic, groups articles that are covering the same story across different outlets, and summarizes each one with a locally-run LLM. No external API keys needed — everything runs in Docker.

## Features

- Pulls current headlines from Google News RSS for any topic
- Embeds each article and clusters near-duplicate coverage into a `Story` using cosine similarity over `pgvector`
- Generates a per-article summary and, when multiple outlets cover the same story, a synthesized cross-source summary that notes where they disagree
- Stores articles, embeddings, and stories in PostgreSQL
- REST API with API-key auth on the write endpoint
- Streamlit UI: enter a topic, click one button, see all matching articles with summaries
- Unit tests for the clustering, summarization, and auth logic, run in CI on every push

## Tech Stack

Python, FastAPI, PostgreSQL + pgvector, Ollama (local LLM + embeddings), Streamlit, Docker Compose, pytest, GitHub Actions.

## Setup

1. Start everything:
   ```bash
   docker compose up -d --build
   ```
2. Pull the local models (one-time, after containers are up):
   ```bash
   docker compose exec ollama ollama pull llama3.2:1b
   docker compose exec ollama ollama pull nomic-embed-text
   ```
3. Copy `.env.example` to `.env` and set `API_KEY` if you want something other than the default.

## Usage

### UI

Open http://localhost:8501, type a topic, click **Fetch & Summarize**.

### API

Fetch and summarize a topic (requires `X-API-Key`):

```bash
curl -X POST "http://localhost:8000/articles/fetch?query=technology" \
  -H "X-API-Key: dev-key"
```

List articles:

```bash
curl "http://localhost:8000/articles/"
```

List clustered stories:

```bash
curl "http://localhost:8000/stories/"
```

Get one story with its source articles:

```bash
curl "http://localhost:8000/stories/1"
```

Full API docs: http://localhost:8000/docs

## Tests

```bash
pip install -r requirements.txt
pytest -v
```

Two tiers:

- **Unit tests** (`test_auth.py`, `test_clustering.py`, `test_summarizer.py`) — pure logic, network calls mocked, no external services required.
- **API integration tests** (`test_api_integration.py`) — exercise the full request path through FastAPI, SQLAlchemy, and a real Postgres/pgvector database (Ollama and the news RSS fetch are mocked; only persistence is real). These need Postgres running:

  ```bash
  docker compose up -d db
  pytest -v
  ```

  If Postgres isn't reachable, this file's tests are skipped automatically rather than failing — CI runs both tiers via a Postgres service container.

## How the clustering works

1. Each new article gets embedded locally (`nomic-embed-text`).
2. Its embedding is compared against one representative embedding per story seen for the same topic in the last 3 days.
3. Above a similarity threshold, it joins that story; otherwise it starts a new one.
4. The story summary is regenerated from all of its articles, so it improves as more outlets get added, and the LLM is asked to flag disagreement between sources.
