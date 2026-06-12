from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.graph import build_agent
from app.config import get_settings
from app.retrieval import load_index
from app.schemas import QueryRequest, QueryResponse, Source


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup
    app.state.agent = build_agent()
    app.state.index = load_index()
    yield


app = FastAPI(title="ComplianceQA", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://compliance-qa-project.netlify.app"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    s = get_settings()

    # We are also returning the chat model and the embedding model,
    # since a proper health check should exercise and return the things
    # whose failure would make the service unable to do its job.
    # Config load is one of those things.

    return {"status": "ok", "chat_model": s.chat_model, "embedding_model": s.embedding_model}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    result = app.state.agent.invoke(
        {"question": request.question, "query": request.question, "retry_count": 0}
    )

    sources = [
        Source(page=n.node.metadata.get("page_label"), text=n.node.text) for n in result["chunks"]
    ]

    return QueryResponse(answer=result["answer"], sources=sources)
