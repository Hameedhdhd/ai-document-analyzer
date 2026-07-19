# AI Document Analyzer

[![CI](https://github.com/Hameedhdhd/ai-document-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/Hameedhdhd/ai-document-analyzer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Code style: ruff](https://img.shields.io/badge/lint-ruff-orange)

A production-style **FastAPI microservice** that classifies documents, generates
summaries, and extracts entities (emails, amounts, dates) using an LLM — with a
built-in offline fallback so it runs anywhere, even without an API key.

Built to demonstrate practical **AI engineering**: clean API design, typed
schemas, graceful degradation, containerization and tests.

## Features

- `POST /analyze` — returns document type, language, summary, entities and sentiment
- LLM-powered analysis via OpenAI (configurable model) with structured JSON output
- **Offline rule-based fallback** — fully functional with zero credentials
- Typed request/response models with Pydantic v2
- Dockerized, CORS-ready, unit-tested

## Tech stack

Python · FastAPI · Pydantic v2 · OpenAI API · Docker · pytest

## Quickstart

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000/docs
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "INVOICE\nTotal due: €1,240.00\nVAT included", "summarize": true}'
```

To enable the LLM path, copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.

## Run with Docker

```bash
docker build -t ai-document-analyzer .
docker run -p 8000:8000 --env-file .env ai-document-analyzer
```

## Endpoints

| Method | Path       | Description                                   |
| ------ | ---------- | --------------------------------------------- |
| GET    | `/health`  | Liveness probe                                |
| POST   | `/analyze` | Classify, summarize and extract entities      |

Interactive docs (Swagger UI) are served at `/docs`.

## Development

```bash
pip install -r requirements.txt ruff
ruff check .   # lint
pytest -q      # tests (run fully offline — no API key needed)
```

CI runs lint + tests on Python 3.10–3.12 via GitHub Actions on every push.

## Tests

```bash
pytest
```

## Author

**Hamid Abdullah** — AI / IT Engineer, Hamburg
[LinkedIn](https://www.linkedin.com/in/hamidabdullah-41b91319)
