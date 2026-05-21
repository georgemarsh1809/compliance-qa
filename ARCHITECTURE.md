# Architecture

_Design decisions and trade-offs. Updated as the project evolves._

## Decision log

### 2026-05-19 — Domain and corpus

**Decision:** UK food safety and compliance, built on a curated corpus of
publicly available regulatory and guidance documents.

**Alternatives considered:** Generic document Q&A, GDPR/DPA assistant,
BRCGS-specific assistant.

**Reasoning:**

- Generic Q&A is the most common AI demo and doesn't differentiate.
- GDPR is over-trodden in UK Python portfolio projects.
- BRCGS specifically would require working off paywalled source material;
  restricts the public repo story.
- UK food compliance is a coherent slice with freely redistributable source
  documents (Open Government Licence) and a clear user persona (UK food SME
  owners and quality managers).
- Domain expert available (food industry contact) for eval validation.

**Trade-offs:**

- Smaller pool of interviewers immediately recognise the domain vs GDPR.
- Mitigated by the project pitch being architecture-and-rigour first, domain
  second.

### 2026-05-19 — Cloud and infrastructure

**Decision:** AWS App Runner for the backend, S3 for corpus and persisted vector
index, Netlify for the frontend. Pulumi (Python) for IaC.

**Alternatives considered:** Fly.io (familiar, simpler, but already on the CV);
ECS Fargate (more services touched, but more infra learning for the same agent
project); Lambda + API Gateway (cold starts and 30s API Gateway limit
incompatible with the agent's retrieval-grading loop).

**Reasoning:**

- AWS Cloud Practitioner cert + AWS on stack but no API deployments to AWS =
  credibility gap to close.
- App Runner is the minimum AWS surface area that solves the problem without
  becoming an infra-padding exercise.
- S3 decouples corpus and persisted index from compute (re-deploy doesn't lose
  state).
- Netlify for the frontend because SPA hosting on AWS (S3 + CloudFront) is pure
  infra learning that doesn't strengthen the agentic-AI story.

**Trade-offs:**

- App Runner is less common in interviews than ECS, so requires explanation.
- $5-15/month running cost vs $0 on Fly.io free tier.

### 2026-05-19 — IaC: Pulumi (Python) over Terraform

**Decision:** Pulumi with Python.

**Reasoning:**

- IaC in the same language as the rest of the backend reduces context-switching.
- Terraform is the default; using Pulumi is mildly differentiating in 2026
  interviews.
- Smaller community than Terraform means more reading of docs, fewer Stack
  Overflow answers. Acceptable trade.

### 2026-05-19 — Package manager: uv (mid-Phase-0)

**Decision:** Switched from pip to uv during Phase 0 dependency installation.

**Why mid-stream:** Initially chose pip for familiarity. Hit four cascading
dependency conflicts in the LlamaIndex / Voyage / Pydantic-AI ecosystem. Each
resolution required a fresh pip run, eating minutes per iteration. uv's resolver
surfaces conflicts in seconds and produces sharper error messages.

**Reasoning:**

- Faster install / resolution loop is the dominant factor on a project that
  touches multiple LLM ecosystem packages with active version drift.
- uv reads existing `requirements.txt` and `requirements-dev.txt` natively, so
  no project restructure required.
- Same author as ruff (Astral);s consistent tooling choice.

**Trade-offs:**

- Less universally familiar to interviewers than pip. Mitigated by explaining
  the trade in the README.
- Mid-stream tool change is a small consistency cost but worth the productivity
  gain.

### 2026-05-19 — Dropped Pydantic AI from v1

**Decision:** Removed Pydantic AI from the stack. Structured outputs will be
implemented via Anthropic's native tool-calling with Pydantic schemas.

**Why:** Pydantic AI 0.0.13 requires Pydantic >= 2.10, which is incompatible
with llama-index-core 0.11.20 due to a Pydantic 2.10 schema generation
regression on AsyncGenerator types. The fix would require upgrading the entire
LlamaIndex 0.11.x to 0.12.x stack, introducing multiple new version constraints
with no guarantee of stability.

**Trade-offs:**

- Lose Pydantic AI's ergonomic agent definition syntax.
- Gain: fewer dependencies, less version pressure, no pre-1.0 library in
  critical path.
- Same end result: typed structured outputs from LLM calls, validated against
  Pydantic schemas.

**Lesson:** Pre-1.0 libraries in fast-moving ecosystems create version pressure
that can cascade through the rest of the stack. Default to mature, well-known
libraries where possible.

### 2026-05-20 — mypy: disabled `disallow_untyped_decorators`

**Decision:** Kept mypy in strict mode but disabled the single sub-flag
`disallow_untyped_decorators`.

**Why:** FastAPI's route decorators (`@app.get`, `@app.post`, etc.) are not
typed to the standard mypy strict mode demands. Under full strict mode,
pre-commit complains and every decorated route handler triggers an "Untyped
decorator makes function untyped" error, despite the handler itself being fully
annotated.

**Alternatives considered:** A per-line `# type: ignore[misc]` on every route
decorator. Rejected because it would have to persists across every endpoint in
the project and adds noise without adding safety.

**Trade-offs:**

- Lose strict enforcement that decorators are typed.
- Keep every other strict check on the actual application code.
- Net: a precise, contained deviation rather than a blunt one.

### 2026-05-21 — Chunking strategy (Phase 2)

**Decision:** SentenceSplitter at chunk_size=512, chunk_overlap=50, for v1.

**Reasoning:** Standard, well-supported default. Respects sentence boundaries
(no mid-sentence cuts); overlap mitigates boundary-loss. Chosen deliberately as
a measurable baseline before investing in more sophisticated chunking.

**Observed:** Inspected the persisted docstore.json (42 chunks from the FSA
guide). Chunks are coherent, but PDF-extraction noise is real... Mangled running
headers (letter-spacing artifacts) and a front-matter chunk (title, contact
phone). Deferred cleanup pending eval evidence on whether it degrades retrieval.

**Candidate refinements (pending eval):** semantic chunking, structure-aware
chunking (the guide's Q&A heading structure aligns well with semantic units),
small-to-big / sentence-window retrieval, contextual retrieval. Each introduces
its own tunable parameter; none justified without measured evidence of a
problem.

### 2026-05-21 — S3 deferred to deployment (Phase 8)

**Decision:** Ingestion operates on local filesystem paths for now. S3
integration deferred to Phase 8.

**Reasoning:** S3 only becomes necessary at deployment, when laptop-side
ingestion and App-Runner-side query need to share an index via common storage.
Until then, local disk is simpler and sufficient for building retrieval, the
agent, and the eval. `build_index` takes corpus/index directories as parameters,
so the S3 path is a thin download/upload wrapper around the unchanged pipeline
(boto3 fetch-to-temp, build, upload), not a rewrite. Adding it now would mean
debugging AWS credentials and boto3 on top of the agentic work that is the
actual focus.

### 2026-05-21 — Embedding model: voyage-3.5

**Decision:** Use voyage-3.5 as the embedding model (updated from the
originally-planned voyage-3).

**Reasoning:** Voyage launched the Voyage 4 series in Jan 2026 and plain
voyage-3 is no longer in their recommended model list. voyage-3.5 is the current
general-purpose option, well within free/cheap usage for a corpus this size.
voyage-4-large (top accuracy) is overkill for a 29-page guide; voyage-4-lite
would be the cost-optimised pick if cost was more of a factor.

**Note:** The same embedding model must be used at query time as at ingestion
time, or query and chunk vectors live in incompatible spaces and similarity
search breaks. Both ingestion and retrieval read the model name from the single
`embedding_model` setting, keeping them in sync automatically.

### Pending

- LangGraph state shape (Phase 4)
- Eval design: LLM-as-judge with retrieval recall and baseline comparison
  (Phase 6)
