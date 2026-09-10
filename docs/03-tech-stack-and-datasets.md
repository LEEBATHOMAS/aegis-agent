# 03 — Tech Stack & Datasets (all free)

## Stack

| Layer | Choice | Cost | Notes |
|---|---|---|---|
| Warehouse | DuckDB | free | Embedded, parquet-native |
| Vector DB | Qdrant | free | Docker container |
| Embeddings | FastEmbed `BAAI/bge-small-en-v1.5` | free | Local, offline |
| LLM | Groq `llama-3.3-70b-versatile` | free tier | Fast; Ollama = offline fallback |
| Agent framework | LangGraph | free | State-machine agents |
| MCP | Python `mcp` SDK (FastMCP) | free | Tool boundary |
| MCP client adapter | `langchain-mcp-adapters` | free | Lets LangGraph call MCP tools |
| Observability | Langfuse | free tier / self-host | Traces + evals |

### Python dependencies (`requirements.txt`)

```
duckdb
pandas
pyarrow
qdrant-client
fastembed
mcp
langgraph
langchain-mcp-adapters
langchain-groq
groq
python-dotenv
httpx
sseclient-py        # only if you add the Wikimedia live stream
```

### Environment (`.env`)

```
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile
QDRANT_URL=http://localhost:6333
```

Get a free Groq key at `console.groq.com/keys`.

## Datasets (free, no paywall)

### Primary (batch) — NYC TLC Trip Records

- Source: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Monthly parquet, public CloudFront, no key:
  `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet`
- Real, high volume (~3M rows/month), clean schema. Perfect "operational events" table.

### Optional (real-time flavor) — Wikimedia EventStreams

- Source: `https://stream.wikimedia.org/v2/stream/recentchange`
- A free live SSE firehose of wiki edits, no API key. Great for a "streaming ingestion"
  story if you want to show near-real-time detection.

### Chaos injector (we build it)

Deterministically manufactures **real** incidents so the agent always has something to
solve:

- Volume drop (simulate a dead upstream source)
- Null spike in a column (upstream schema/field change)
- Duplicate keys (bad dedup after a deploy)
- Schema drift (renamed/added/removed column)
- Out-of-range values (negative fares)
- Timezone shift (off-by-hours bug)

## What needs Docker vs. not

- **Docker:** Qdrant (and optionally Langfuse self-host, Ollama).
- **Not Docker:** DuckDB (embedded file), the MCP server, the agent — all plain Python.

This split (embedded vs. service) is itself a design lesson: containerize the things that
are genuinely long-running services; keep embedded engines embedded.
