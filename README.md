# Aegis — an Agentic Data Reliability Engineer (DRE)

Aegis is a learning-grade but real-world project: an autonomous agent that detects
data-quality incidents in a warehouse, investigates root cause the way an
engineer would (querying the warehouse, inspecting lineage, reading runbooks and past
postmortems, correlating with recent pipeline runs), writes a root-cause report, and
proposes a **safe** remediation for human approval.

The project is designed with the below AI components in play:

- **MCP (Model Context Protocol)** — servers, tools, resources, and the host/client model.
- **LLM agent architecture** — ReAct loops, plan/act/observe, memory, and agents as state machines.
- **RAG** — chunking, embeddings, retrieval, and grounding an LLM in institutional knowledge.
- **Single-server vs. orchestrated designs** — and *why* you evolve from one to the other.
- **Scalability & performance** — as a deliberate roadmap, not a prerequisite.

Everything runs on **free tiers** and a laptop. Docker is used only for Qdrant
(and optionally Langfuse/Ollama later).

## How to read these docs

Read them in order:

1. [`docs/00-problem-statement.md`](docs/00-problem-statement.md) — the problem and why it's a good teacher.
2. [`docs/01-architecture-and-design.md`](docs/01-architecture-and-design.md) — the system design with diagrams.
3. [`docs/02-why-decisions.md`](docs/02-why-decisions.md) — every major decision and the reasoning behind it.
4. [`docs/03-tech-stack-and-datasets.md`](docs/03-tech-stack-and-datasets.md) — the free-tier stack and datasets.
5. [`docs/04-roadmap.md`](docs/04-roadmap.md) — the phased build plan (Phase 0–9).
6. `docs/phase-*.md` — step-by-step implementation for each phase, with the *why* at each step.

