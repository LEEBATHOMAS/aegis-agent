# 00 — Problem Statement

## The problem (one paragraph)

> A data platform ingests high-volume operational data into a warehouse. Data breaks
> **silently** — a schema drifts, a column starts arriving null, volumes drop because an
> upstream source died, duplicates sneak in after a bad deploy. By the time a dashboard
> looks wrong, hours have passed and an on-call data engineer spends ~45 minutes manually
> running SQL, checking lineage, grepping runbooks, and correlating with recent pipeline
> runs to find root cause.

## What we build

An **autonomous agent** that:

1. **Detects** data-quality incidents in near-real-time (freshness misses, volume drops,
   null spikes, duplicate keys, schema drift, out-of-range values).
2. **Investigates** root cause by *deciding* which tools to call next — query the
   warehouse, inspect lineage, read the relevant runbook/postmortem (RAG), correlate with
   recent pipeline runs.
3. **Explains** — writes a root-cause report grounded in retrieved knowledge.
4. **Proposes** a safe remediation (backfill, quarantine bad rows) that a human approves
   before anything mutates data.

## Why this problem is a great teacher

- **It is genuinely agentic.** The agent must *decide* the next action based on what it
  just learned. There is no fixed script. This is the essence of "agentic system design"
  and exactly what interviewers probe for.
- **RAG has a real job.** Retrieving the *right* runbook/postmortem is what converts raw
  symptoms into a diagnosis. RAG here is institutional memory, not a gimmick.
- **It is a senior data engineer's actual world.** Data contracts, medallion layers,
  freshness SLAs, schema drift, lineage, backfills. You will speak this language fluently.
- **Scalability is a natural roadmap.** You start on a laptop with DuckDB and grow toward
  Kafka/Snowflake/distributed workers. This is the perfect setup for "how would you scale
  this?" questions.

## What "done" looks like for the MVP

- A healthy medallion warehouse (bronze → silver → gold) built from real NYC taxi data.
- A data-quality metrics layer that computes freshness, volume, null%, and schema hash.
- A chaos injector that manufactures *real* incidents on demand.
- An MCP server exposing investigation tools + a RAG-backed runbook search.
- A LangGraph agent that: detects the incident → investigates via ReAct → produces an
  RCA report → proposes a fix gated by human approval.
- Full traces in Langfuse so you can see and evaluate what the agent did.

## Interview framing (say this out loud)

> "I built an autonomous data-reliability engineer. It watches quality metrics across a
> medallion warehouse, and when an SLA breaks it runs a bounded ReAct investigation over
> MCP tools — SQL, lineage, pipeline history, and RAG over runbooks — to produce a
> grounded root-cause report and a human-approved remediation. I started single-server /
> single-agent and evolved to a supervisor with specialist sub-agents and multiple MCP
> servers, which let me talk concretely about when and why you split a monolith."
