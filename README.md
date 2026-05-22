# ComplianceQA

A grounded Q&A agent for UK food safety and compliance, with cited sources and a
domain-expert-validated evaluation framework.

**Status:** In active development. Building in public.

## What it does

Answers questions about UK food law, FSA guidance, and publicly available BRCGS
material, with citations to the specific source document and section. Built on a
pre-loaded corpus of UK food compliance documentation; designed to be
corpus-agnostic so it can be pointed at other regulatory domains.

## Why this exists

Built as a portfolio project to develop and demonstrate experience with the 2026
agentic AI stack (LangGraph, LlamaIndex), evaluated against a domain-validated
question set rather than vibes.

UK food businesses are subject to overlapping regulatory regimes (Food Safety
Act 1990, FSA guidance, BRCGS standards). A grounded Q&A agent with traceable
citations is more useful than search-and-skim.

## Stack

- **Backend:** FastAPI, Python 3.11
- **RAG:** LlamaIndex with Voyage embeddings
- **Agent:** LangGraph (retrieval-grading loop)
- **Structured outputs:** Anthropic native tool-calling with Pydantic schemas
- **LLM:** Anthropic Claude (Haiku 4.5 for agent, Sonnet 4.6 for judge)
- **Frontend:** React + TypeScript + Vite (deployed to Netlify)
- **Storage:** S3 (corpus + persisted vector index)
- **Compute:** AWS App Runner
- **IaC:** Pulumi (Python)
- **CI/CD:** GitHub Actions
- **Observability:** structlog, OpenTelemetry, LangSmith

See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for design decisions and trade-offs.

## Roadmap

- [x] Phase 0: Tooling and skeleton
- [x] Phase 1: FastAPI shell and config
- [x] Phase 2: Document ingestion (LlamaIndex + S3)
- [x] Phase 3: Retrieval and first LLM answer
- [ ] Phase 4: LangGraph agent with grading loop
- [ ] Phase 5: React frontend
- [ ] Phase 6: Evaluation framework
- [ ] Phase 7: Observability
- [ ] Phase 8: CI/CD and AWS deployment
- [ ] Phase 9: Documentation and polish

## Disclaimer

This is a portfolio project and is not legal advice. Outputs are AI-generated
and should not be relied on for compliance decisions without verification
against the original sources.
