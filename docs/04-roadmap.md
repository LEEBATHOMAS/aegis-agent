# 04 — Build Roadmap (Phases 0–9)

We build one phase at a time. Each phase has its own doc with step-by-step instructions
and the *why* at each step.

| Phase | Goal | Doc | Status |
|---|---|---|---|
| 0 | Foundation: repo, Docker (Qdrant), venv, LLM choice | delivered in chat | done |
| 1 | Data plane: NYC TLC -> DuckDB medallion (bronze/silver/gold) | delivered in chat | in progress |
| 2 | Data-quality metrics + chaos/incident injector | `phase-2-dq-and-chaos.md` | pending |
| 3 | MCP server (run_sql, get_dq_metrics, get_lineage, get_pipeline_runs) | `phase-3-mcp-server.md` | pending |
| 4 | Knowledge plane: runbooks -> Qdrant, `search_runbooks` RAG tool | `phase-4-rag.md` | pending |
| 5 | Single agent: LangGraph Detector -> Investigator -> RCA -> Reporter | `phase-5-agent.md` | pending |
| 6 | Human-in-the-loop remediation (propose_fix/execute_fix + approval) | `phase-6-remediation.md` | pending |
| 7 | Orchestration: supervisor + sub-agents; then multi-server MCP | `phase-7-orchestration.md` | pending |
| 8 | Observability + evals with Langfuse | `phase-8-observability.md` | pending |
| 9 | Scalability roadmap (Kafka/Redpanda, Postgres/Snowflake, workers, caching) | `phase-9-scalability.md` | pending |

## Why this order

1. **Data before agent.** The agent is only interesting if there is real data and real
   breakage to reason about. Phases 1–2 create that world.
2. **Tools before reasoning.** The MCP server (Phase 3) and RAG (Phase 4) are the agent's
   "hands and memory." Build them before the "brain."
3. **Single before orchestrated.** Phase 5–6 prove the concept simply; Phase 7 evolves it
   only once the value is clear.
4. **Observability before scale.** You cannot scale what you cannot measure (Phase 8
   before Phase 9).

## Learning outcomes mapped to phases

- MCP fundamentals: Phase 3, Phase 7 (multi-server)
- RAG: Phase 4
- Agent architecture (ReAct, state machine, HITL): Phase 5–6
- Orchestration (supervisor/worker, multi-agent, multi-server): Phase 7
- Evals & observability: Phase 8
- Systems/scale tradeoffs: Phase 9 (and every "why" along the way)
