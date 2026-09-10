# 01 — Architecture & System Design

## The four planes

Aegis is organized into four planes. The source-code folders mirror these planes on
purpose, so the structure itself teaches the design.

| Plane | Responsibility | Code |
|---|---|---|
| **Data plane** | Ingest + model data (medallion), compute quality metrics | `warehouse.py`, `dq.py`, `chaos.py` |
| **Knowledge plane** | Store & retrieve institutional knowledge (RAG) | `rag.py` |
| **Tool boundary** | Expose capabilities to any agent via MCP | `mcp_server.py` |
| **Control plane** | The agent: reasoning + orchestration | `agent.py` |
| **Observability** | Traces + evals across everything | Langfuse |

## Big-picture diagram

```
                          +------------------------------------------------+
                          |            CONTROL PLANE (the "agent")         |
                          |              LangGraph state machine           |
   dq_metrics anomaly --->|  Detector -> Investigator -> RCA -> Approval -> Reporter
                          |               (ReAct loop)          (human)     |
                          +-------+---------------------------+-------------+
                                  | calls tools over MCP      | writes report
                                  v                           v
        +-------------------------------------------+   incident_report.md
        |         MCP SERVER  (tool boundary)       |
        |  run_sql - get_dq_metrics - get_lineage   |
        |  get_pipeline_runs - search_runbooks(RAG) |
        |  propose_fix - execute_fix (guarded)      |
        +-------+---------------------------+-------+
                |                           |
     +----------v----------+     +----------v-----------+
     |   DATA PLANE        |     |   KNOWLEDGE PLANE     |
     |  DuckDB warehouse   |     |   Qdrant vector DB    |
     |  bronze>silver>gold |     |  runbooks, contracts, |
     |  + dq_metrics table |     |  postmortems (RAG)    |
     +----------^----------+     +-----------------------+
                |
     +----------+----------+
     |  Ingestion + Chaos  |  <- NYC TLC trips (batch) + optional live Wikimedia stream
     |  (injects real DQ   |     + a "chaos" injector that creates real incidents
     |   incidents)        |
     +---------------------+

         All steps traced/evaluated in Langfuse (observability plane)
```

## The MCP mental model (most important concept)

There are **three roles** in MCP. Confusing them is the most common misconception.

- **MCP Host / Client** = your agent app (LangGraph). It holds the LLM and decides *what
  to do*.
- **MCP Server** = a process that *exposes capabilities* (tools, resources, prompts). It
  knows nothing about the LLM.
- **The LLM** = the reasoning engine inside the host that *chooses* which server tool to
  call.

> Why MCP at all instead of the agent calling Python functions directly? Because MCP is a
> **standardized boundary** between "reasoning" and "capabilities." The same MCP server
> can be reused by Cursor, Claude Desktop, your LangGraph agent, or a teammate's app,
> without rewriting anything. It decouples tools from the model. Interview line:
> *"MCP turns tools into a reusable, language-agnostic contract, so capabilities become
> platform infrastructure instead of being welded to one agent."*

## The agent as a state machine

```
        +-------------+
        |  DETECTOR   |  reads dq_metrics, finds the worst active anomaly
        +------+------+
               | incident context
               v
     +-------------------+   need more info?
     |   INVESTIGATOR    |<---------------+
     |   (ReAct loop)    |                |  loops, calling MCP tools:
     |  think>act>observe|----------------+  run_sql, get_lineage,
     +---------+---------+                    get_pipeline_runs, search_runbooks
               | enough evidence
               v
        +-------------+
        |     RCA     |  synthesize root cause, grounded in retrieved runbook
        +------+------+
               v
        < confidence high AND fix is safe? >
           |yes                    |no
           v                       v
     +-----------+          +------------+
     |  APPROVAL |          |  REPORTER  |  (report only, no fix)
     |  (human)  |          +------------+
     +-----+-----+
      approved
           v
     +------------+     +------------+
     | EXECUTE_FIX|---->|  REPORTER  |
     +------------+     +------------+
```

> Why a graph instead of a single "give the LLM all tools and pray" agent? You gain
> **control**: bounded loops (no infinite tool-calling), a mandatory human gate before
> mutations, checkpointing/resumability, and clear places to attach evals. That is the
> difference between "I made an agent" and "I designed an agent system."

## Single-server vs. orchestration — the learning ladder

- **Phase A — Single MCP server, single agent.** One server exposes all tools; one
  LangGraph agent uses them. Learn the MCP protocol and the ReAct loop cleanly.
- **Phase B — Multi-agent orchestration, still one server.** Split the *reasoning* into a
  supervisor + specialist sub-agents (a SQL analyst, a lineage/deploy correlator, a
  knowledge agent). Learn the **supervisor/worker** pattern.
- **Phase C — Multi-server MCP.** Split the *capabilities* into separate MCP servers
  (Warehouse server, Lineage/Ops server, Knowledge server). Learn **why** you separate:
  independent scaling, security boundaries (the fix-executor needs write creds; the read
  servers do not), and bounded contexts.

This progression is literally a system-design answer to "how do you evolve from a
monolith to services."
