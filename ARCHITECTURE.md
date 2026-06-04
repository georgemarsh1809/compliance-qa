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

### 2026-05-22 — Grounded generation: prompt design (Phase 3)

**Decision:** RAG answers are generated by Claude (Haiku) under a system prompt
that enforces four rules: answer only from the provided retrieved sources, use
no outside knowledge, cite the source number and page for each claim, and state
plainly when the sources don't contain the answer rather than guessing or
fabricating.

**Reasoning:** Grounding is the entire point of RAG over a curated corpus.
Without the "sources only" constraint, the model falls back on its (lossy,
uncitable, possibly outdated) parametric knowledge of food law, which defeats
the purpose and undermines citation. The honest-refusal rule is what makes the
system trustworthy: tested against an out-of-corpus question ("chilled food
storage temperature"); the model correctly declined to answer from training
knowledge and pointed to the FSA website instead, despite almost certainly
"knowing" the answer.

**Structure:** Rules live in the `system` prompt (stable, per-call-invariant
behaviour); the retrieved context and the user's question go in the user message
(per-call data). Context is formatted with `[Source N - Page X]` labels so
citations have a consistent, traceable handle.

**Verified:** In-corpus question (due diligence defence) produced an accurate,
fully-cited answer drawn from the correct chunk. Out-of-corpus question produced
an honest refusal. Both grounding and refusal behaviours confirmed by hand;
these two cases are candidate items for the Phase 6 eval.

### 2026-05-22 — Type narrowing at the Anthropic response boundary (Phase 3)

**Decision:** Extract the answer text via `isinstance(block, TextBlock)`
narrowing rather than a `cast` or `# type: ignore`.

**Reasoning:** The Anthropic SDK types `response.content` blocks as a union
(TextBlock, ToolUseBlock, etc.); only TextBlock has `.text`. Strict mypy
correctly objects to accessing `.text` on the union. `isinstance` narrowing
satisfies mypy _and_ adds a real runtime guard: if a non-text block ever comes
back, the code raises a clear ValueError rather than crashing obscurely or
silently mis-typing. Preferred over `cast`, which would suppress the type error
without any runtime check.

**General pattern:** Union types at typed/untyped or external-API boundaries are
narrowed with `isinstance` (and `is not None` for Optionals) rather than cast
away. The same boundary issue recurs across the LLM ecosystem.

### 2026-05-27 — Agent architecture: LangGraph retrieval-grading loop (Phase 4)

**Decision:** The agent is a LangGraph StateGraph with four nodes (retrieve,
grade, rewrite, generate) and a conditional edge after grading. Flow: retrieve
chunks for the current query, grade whether they're sufficient to answer the
question, and either generate (if sufficient) or rewrite the query and retrieve
again (if not), bounded by a retry cap.

**Reasoning:** This adds genuine self-correction over a straight-line RAG
pipeline; the system evaluates its own retrieval and re-queries when the first
attempt is inadequate, rather than blindly generating from whatever came back.
Modelling it as an explicit graph (nodes/edges/state) keeps the decision
structure legible and modifiable, compared to the same logic buried in nested
control flow.

**State model:** TypedDict (the LangGraph idiom; plain dict at runtime, typed at
check-time). `question` (fixed, what we answer) and `query` (mutable, what we
search with and rewrite) are deliberately separate fields, this separation is
what makes the rewrite loop coherent: retrieve searches with `query`, generate
answers the `question`. `retry_count` initialised to 0 at invoke;
`chunks`/`grade`/`answer` filled in by nodes as the graph runs (NotRequired).

**Honest framing:** LangGraph is arguably overkill for a loop this simple (a
while-loop would suffice). Chosen to build genuine fluency with the
stateful-graph model used in production agent systems and named in target roles,
with the trade-off acknowledged rather than hidden.

### 2026-05-27 — Retry cap and graceful fallback (Phase 4)

**Decision:** The conditional edge after grading caps retries at MAX_RETRIES
(2). On exhaustion it routes to generate anyway rather than looping or erroring.

**Reasoning:** Without a cap, a question the corpus genuinely cannot answer
would loop forever (rewrite → retrieve → grade → insufficient → rewrite...). The
cap limits worst-case latency and API calls. The fall-through to generate means
the system always produces a best-effort answer; the grounding/honesty rules in
generate_answer then ensure it admits the gap rather than fabricating. Verified
on an out-of-corpus question (chilled-food storage temperature): the loop fired
twice, hit the cap, generated, and honestly declined.

### 2026-05-27 — Rescue cases are rare on this corpus (Phase 4 finding)

**Decision/finding:** Verified the retrieval-grading-rewrite loop works (fires,
retries, caps, falls back gracefully). However, the specific case where a
rewrite _rescues_ a near-miss first retrieval is rare on this corpus, even
colloquially-phrased, legally-imprecise questions ("if a shop sells me something
different from what I paid for...") retrieve the correct content first-try,
including at top_k=1.

**Interpretation:** This reflects strong semantic retrieval over a small,
coherent corpus, not a defect. The self-correction architecture's value scales
with corpus size and noise, where first-pass retrieval misses more often.
Documented honestly rather than engineering an artificial failure to force a
rescue demonstration.

### 2026-05-27 — Shared call_claude helper + node-name/state-key collision (Phase 4)

**Decision:** Extracted a shared
`call_claude(model, system_prompt, max_tokens, user_content) -> str` helper in
llm.py, centralising Anthropic client construction, the messages.create call,
and TextBlock response narrowing. Used by generate_answer and by the
grade/rewrite nodes.

**Reasoning:** Rule of three; the construct-call-narrow boilerplate appeared in
three places (generate_answer, grade, rewrite). Centralising means any change to
how Claude is called (retries, logging, error handling) happens in one place,
and each node's distinctive logic (its prompt, its parsing) stands out instead
of being buried in boilerplate. Callers pass keyword arguments to avoid
positional-order bugs across the similarly-typed parameters.

**Gotcha logged:** LangGraph keeps node names and state keys in one namespace,
so a node cannot share a name with a state field (a node named "grade" collides
with the `grade` state key). Resolved by naming graph nodes with a `_node`
suffix matching the function names.

### 2026-06-04 — Frontend scaffold: React + TypeScript + Vite + Tailwind v4

**Decision:** Scaffold `compliance-qa/frontend/` as a sibling to `backend/`
using Vite's `react-ts` template and pnpm. Tailwind v4 installed via
`@tailwindcss/vite` plugin. Single `@import "tailwindcss"` in `index.css`
replaces v3's three-directive approach. React compiler variant not used.

**Reasoning:**

- Tailwind v4's Vite-native plugin removes the need for `tailwind.config.js` and
  a PostCSS config, reducing setup surface.
- pnpm consistent with the rest of the project tooling.
- React compiler is experimental and targets rendering optimisation; the
  portfolio value here is in TypeScript and RAG integration, not React
  performance.

**Trade-offs:**

- Tailwind v4 is newer and some plugins (typography) have compatibility issues
  in this setup. Encountered and resolved during this phase; see entry below.

---

### 2026-06-04 — Component architecture: split components from the start

**Decision:** Split UI into `QueryForm`, `ResponseDisplay`, and `SourceCard`
rather than a monolithic `App.tsx`. State owned by `App`, passed down as props;
callbacks passed up for user events.

**Reasoning:**

- More representative of production React patterns than a single-component
  approach.
- Directly addresses the TypeScript/React gap in the CV story; split components
  require explicit prop typing, callback typing, and controlled input patterns.

**Trade-offs:**

- Slightly more scaffolding upfront than a single component. Worth it given the
  learning and CV objectives.

---

### 2026-06-04 — TypeScript types mirror backend Pydantic models exactly

**Decision:** Defined `QueryRequest`, `Source`, and `QueryResponse` in
`src/types.ts` as direct TypeScript equivalents of the backend Pydantic models.
Used `import type` throughout for type-only imports.

**Reasoning:**

- Single source of truth for the API contract. If the backend models change, the
  frontend types are the first update required.
- `import type` signals intent clearly and ensures type imports are erased at
  build time.

---

### 2026-06-04 — Typed fetch client in `src/api.ts`

**Decision:** Single exported `queryCompliance` function handles all API
interaction. POSTs to `http://localhost:8000/query`, returns
`Promise<QueryResponse>`. No abstraction layer beyond this.

**Reasoning:**

- Keeps API surface minimal. A full HTTP client library (axios, etc.) is not
  justified at this scale.
- Explicit typing of the request and response against `types.ts` keeps the
  contract enforced at the call site.

---

### 2026-06-04 — Markdown rendering: react-markdown with custom components

**Decision:** Used `react-markdown` to render the answer field. Passed a custom
`components` prop to style headings and paragraphs for the dark UI, rather than
using `@tailwindcss/typography`.

**Reasoning:**

- `@tailwindcss/typography` failed to resolve correctly in the Tailwind v4 +
  Vite plugin setup (both `@plugin` CSS directive and `vite.config.ts` plugin
  config attempted; both failed).
- Custom components give explicit control over rendered output and avoid an
  additional dependency.
- Tailwind's preflight CSS strips default heading styles, so without either the
  typography plugin or custom components, markdown renders without visual
  hierarchy.

**Trade-offs:**

- Custom components require manual maintenance if heading styles need updating.
- The typography plugin would be the cleaner long-term solution if Tailwind v4
  compatibility improves.

---

### 2026-06-04 — Eval harness: automated refusal detection, manual review for the rest

**Decision:** `backend/eval/run_evals.py` runs all 21 eval questions against the
live backend. `out_of_corpus` questions are scored automatically via string
matching against a list of known refusal signals. Happy path and oblique
questions are saved to a timestamped JSON file in `eval/results/` for manual
review.

**Reasoning:**

- Fully automated scoring (LLM-as-judge) adds complexity and introduces its own
  reliability questions. Not justified before the question set is
  domain-validated.
- String matching on refusal signals is transparent and auditable; the signal
  list was derived empirically by running out-of-corpus questions against the
  live system and observing actual phrasing.
- Manual review for happy path and oblique questions is appropriate given the
  small dataset size and pending domain-expert validation.

**Known limitation:** The model occasionally phrases refusals in novel ways that
don't match any signal, producing false negatives. Two confirmed cases observed
across runs (q17, q18). The signal list is updated as new patterns are observed,
but this is an inherent limitation of the approach.

**Trade-offs:**

- String matching is brittle against novel phrasing. LLM-as-judge is logged as
  the natural next step once a validated baseline exists.

---

### 2026-06-04 — LLM-as-judge scoring: deferred

**Decision:** Not implemented in this phase. Logged as a future improvement.

**Reasoning:**

- String matching covers the automatable subset (refusal detection) well enough
  for a first run.
- LLM-as-judge is better justified once the question set is domain-validated and
  the string-matching baseline is established. Adding it now would be
  sophistication ahead of evidence.

---

### 2026-06-04 — Timestamped results files

**Decision:** Each eval run writes a new JSON file to `backend/eval/results/`
with a `results_YYYYMMDD_HHMMSS.json` filename.

**Reasoning:**

- Preserves run history so score changes across iterations are visible.
- Directly useful once the question set is updated after domain-expert
  validation; the before/after comparison is the point.

---

### 2026-06-04 — Eval question set pending domain-expert validation

**Decision:** 21-question eval set drafted and sent to a food industry contact
for domain-expert review. Harness runs against the current set but results are
treated as provisional until validation is complete.

**Reasoning:**

- Measure-before-optimise discipline. Running the harness now establishes a
  baseline. Scores become defensible after validation confirms question quality
  and reference answers are accurate.
- The eval categories (happy path, out-of-corpus refusal, oblique phrasing) were
  chosen to test distinct failure modes rather than to inflate headline pass
  rates.
