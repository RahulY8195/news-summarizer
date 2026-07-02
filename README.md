# News Summarizer

A Python API that fetches live news articles, summarizes them with a locally-running LLM, and stores everything in a database. Fully containerized with Docker — completely free to run, no API keys required at all.

## Features

- Fetches current headlines from Google News (via its public RSS feed, no key needed)
- Summarizes each article using a local LLM served by Ollama (no cloud LLM cost)
- Stores articles and their summaries in PostgreSQL
- REST API to trigger fetching and browse articles/summaries

## Tech Stack

- **Python** + **FastAPI** — REST API
- **PostgreSQL** — persistent storage
- **Ollama** — runs a local open-source LLM for summarization
- **Docker Compose** — orchestrates the app, database, and LLM containers together
- **Google News RSS** — source of news articles

## Setup

1. Start everything:
   ```bash
   docker compose up -d --build
   ```
2. Pull a local model into Ollama (one-time step, run after containers are up):
   ```bash
   docker compose exec ollama ollama pull llama3.2:1b
   ```

## Usage

Fetch and summarize the latest technology headlines:

```bash
curl -X POST "http://localhost:8000/articles/fetch?query=technology"
```

List all summarized articles:

```bash
curl "http://localhost:8000/articles/"
```

Interactive API docs: http://localhost:8000/docs
