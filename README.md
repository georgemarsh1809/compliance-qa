# ComplianceQA

A grounded Q&A agent for UK food safety compliance, with cited sources and a
domain-expert-reviewed evaluation framework.

**Status:** Version 1 shipped. Live at:
https://compliance-qa-project.netlify.app/

## What it does

Answers questions about the UK Food Safety Act 1990 and FSA guidance, with
citations to the specific source document and page. Built on a pre-loaded corpus
of FSA guidance material and designed to refuse out-of-scope questions rather
than hallucinate answers from outside the corpus.

## Why this exists

UK food businesses operate under overlapping regulatory regimes. Navigating
these manually is slow and error-prone. A grounded Q&A agent with traceable
citations is more reliable than search-and-skim, and more auditable than a
standard LLM response.

Built to demonstrate practical experience with the current agentic AI stack,
evaluated against a 21-question domain-reviewed question set, rather than
informal testing.

## Architecture

The agent runs a self-correcting retrieval loop: queries are routed, retrieved
chunks are graded for relevance, and low-confidence results trigger a re-query
before generation. Answers are grounded in retrieved source material with
explicit citations; the system refuses rather than hallucinating when retrieval
confidence is low.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for design decisions and trade-offs.

## Stack

- **Backend:** FastAPI, Python 3.11
- **RAG:** LlamaIndex with Voyage embeddings
- **Agent:** LangGraph (retrieval-grading loop)
- **Structured outputs:** Anthropic native tool-calling with Pydantic schemas
- **LLM:** Anthropic Claude Haiku 4.5
- **Frontend:** React + TypeScript + Vite (Netlify)
- **Storage:** S3 (corpus + persisted vector index)
- **Compute:** AWS ECS Fargate
- **IaC:** Terraform
- **CI/CD:** GitHub Actions

## Evaluation

Designed and ran a structured evaluation harness across 21 domain-specific
questions covering retrieval quality, answer grounding, and refusal behaviour.
Out-of-corpus refusal detection is automated via string matching against known
refusal signals. Happy path and oblique answers reviewed manually against
reference answers and the source corpus. Question set reviewed with a
subject-matter expert with industry experience in food storage and distribution.
Evaluation methodology and results documented in ARCHITECTURE.md.

## Running locally

Requires Python 3.11, an Anthropic API key, a Voyage API key, and AWS
credentials with S3 read access.

```bash
# Clone the repo
git clone https://github.com/georgemarsh1809/compliance-qa
cd compliance-qa

# Install dependencies (uv recommended)
cd backend
uv sync

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys and S3 bucket names

# Start the backend
uv run uvicorn app.main:app --reload --port 8000
```

To run the eval harness:

```bash
uv run python eval/run_evals.py
```

The frontend is deployed to Netlify and points to the production backend by
default. To run the frontend locally against the local backend:

```bash
cd frontend
pnpm install
pnpm run dev
```

The frontend reads the backend URL from `VITE_API_URL` in `frontend/.env`. This
defaults to `http://localhost:8000` for local development.

## Disclaimer

This is a portfolio project and is not legal advice. Outputs are AI-generated
and should not be relied on for compliance decisions without verification
against the original sources.
