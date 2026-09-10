# 02 — Why: Every Major Decision Explained

This is the most important document for interviews. For each choice, we record **what we
picked**, **the alternative**, and **why**. Being able to defend a design is what
separates senior from junior.

## Warehouse: DuckDB (embedded)

- **Alternative:** Postgres, Snowflake, BigQuery.
- **Why DuckDB:** Zero infrastructure, parquet-native, runs in-process on a laptop, and
  *feels* like real analytics SQL. A managed warehouse adds ops overhead you do not need
  while learning. Crucially, DuckDB → Postgres/Snowflake is a *deliberate later swap*
  (Phase 9); making that swap is itself the scalability lesson.
- **Tradeoff:** DuckDB is single-node and embedded — not for concurrent multi-writer
  production. That is exactly the limitation you will "graduate" from.

## Vector store: Qdrant (Docker)

- **Alternative:** pgvector, Chroma, FAISS.
- **Why Qdrant:** Production-grade, free, excellent metadata filtering, runs in one
  container. pgvector couples storage + search in a way that hides what a vector DB does;
  Chroma is fine but Qdrant teaches you a real production system with a REST API and a
  dashboard.

## Embeddings: local FastEmbed (`BAAI/bge-small-en-v1.5`)

- **Alternative:** OpenAI/Cohere embedding APIs.
- **Why local:** Zero API cost, zero rate limits, fully offline. It also drives home that
  **embeddings are a separate model from the LLM** — a point many people blur.

## LLM: Groq free tier (`llama-3.3-70b-versatile`)

- **Alternatives:** Ollama (fully local), Google Gemini Flash free tier.
- **Why Groq:** Free and extremely fast, which matters a lot inside a tight ReAct loop
  (many sequential LLM calls). Ollama is the offline fallback. All three are free; config
  lets you swap without code changes.

## Agent framework: LangGraph

- **Alternatives:** raw ReAct loop, CrewAI, AutoGen.
- **Why LangGraph:** An agent *is* a state machine, and LangGraph makes the graph
  explicit — nodes, edges, conditional transitions, retries, checkpoints, human-in-the-
  loop. You can draw it and reason about it. CrewAI/AutoGen hide control flow, which is
  bad for *learning* fundamentals. A raw loop teaches the basics but gives you no
  structure for approval gates or resumability.

## Start single-server, then orchestrate

- **Alternative:** design multi-agent / multi-server from day one.
- **Why phased:** Premature microservices/multi-agent is the classic junior mistake. By
  starting simple you will *feel* the pain point that justifies splitting — and that
  story ("we split when X hurt") is exactly what interviewers want, versus cargo-culting
  microservices.

## Human-in-the-loop before any data mutation

- **Alternative:** fully autonomous remediation.
- **Why gated:** Agents are non-deterministic. Letting one auto-run a backfill or delete
  rows on prod is how you cause an outage. The approval gate teaches **guardrails and safe
  autonomy** — and read vs. write privilege separation.

## Observability first-class (Langfuse)

- **Alternative:** print statements / no tracing.
- **Why:** You cannot improve or debug an agent you cannot see. Traces + evals are what
  separate a demo from a system, and they let you answer "how do you know it works?"

## Medallion layering (bronze/silver/gold)

- **Why:** Industry standard, and it *aids debugging*: schema drift shows in bronze, null
  spikes in silver, volume drops in gold. The agent "walks the layers" like a senior
  engineer. It also gives natural homes for data contracts (validation lives at the
  bronze→silver boundary).

## Config in the environment (`.env`)

- **Why:** Secrets are configuration, not source (12-factor). It lets us swap Groq →
  Ollama by changing config, not code.

## Pushing compute to the data engine (DuckDB `httpfs`)

- **Why:** DuckDB reads parquet directly over HTTPS instead of pulling rows into Python.
  This is the same principle behind predicate pushdown — let the engine do the heavy
  lifting, do not drag data into app memory.
