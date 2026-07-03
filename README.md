# ComplianceQA

A grounded Q&A agent for UK food safety and compliance, with cited sources and a
domain-expert-validated evaluation framework.

**Status:** Version 1 shipped. Live at:
https://compliance-qa-project.netlify.app/

## What it does

Answers questions about UK food law, FSA guidance, and publicly available BRCGS
material, with citations to the specific source document and section. Built on a
pre-loaded corpus of UK food compliance documentation and designed to be
corpus-agnostic, so it can be pointed at other regulatory domains without
architectural changes.

## Why this exists

UK food businesses operate under overlapping regulatory regimes: the Food Safety
Act 1990, FSA guidance, and BRCGS standards. Navigating these manually is slow
and error-prone. A grounded Q&A agent with traceable citations is more reliable
than search-and-skim, and more auditable than a standard LLM response.

Built to demonstrate practical experience with the current agentic AI stack,
evaluated against a 21-question domain-validated question set reviewed with a
subject-matter expert, rather than informal testing.

## Architecture

The agent runs a self-correcting retrieval loop: queries are routed, retrieved
chunks are graded for relevance, and low-confidence results trigger a re-query
before generation. Answers are grounded in retrieved source material with
explicit citations; the system is designed to refuse rather than hallucinate
when retrieval confidence is low.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for design decisions and trade-offs.

## Stack

- **Backend:** FastAPI, Python 3.11
- **RAG:** LlamaIndex with Voyage embeddings
- **Agent:** LangGraph (retrieval-grading loop)
- **Structured outputs:** Anthropic native tool-calling with Pydantic schemas
- **LLM:** Anthropic Claude (Haiku 4.5 on live path, Sonnet 4.6 as eval judge)
- **Frontend:** React + TypeScript + Vite (Netlify)
- **Storage:** S3 (corpus + persisted vector index)
- **Compute:** AWS ECS Fargate
- **IaC:** Terraform
- **CI/CD:** GitHub Actions

## Evaluation

Designed and ran a structured evaluation harness across 21 domain-specific
questions covering retrieval quality, answer grounding, and refusal behaviour.
Results reviewed with a subject-matter expert. Evaluation methodology documented
in ARCHITECTURE.md.

## Running locally

Requires Python 3.11, an Anthropic API key, a Voyage API key, and AWS
credentials with S3 read access.

```bash
# Clone the repo
git clone https://github.com/georgemarsh1809/compliance-qa
cd compliance-qa

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Optional: install dev dependencies (eval harness, linting, type checking)
pip install -r requirements-dev.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys and S3 bucket names

# Start the backend
uvicorn app.main:app --reload --port 8000
```

The frontend is deployed to Netlify and points to the production backend by
default. To run the frontend locally:

```bash
cd frontend
npm install
npm run dev
```

Update the API base URL in the frontend config to point to localhost:8000.

## Disclaimer

This is a portfolio project and is not legal advice. Outputs are AI-generated
and should not be relied on for compliance decisions without verification
against the original sources.
