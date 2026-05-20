from fastapi import FastAPI

from app.config import get_settings

app = FastAPI(title="ComplianceQA", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    s = get_settings()

    # We are also returning the chat model and the embedding model,
    # since a proper health check should exercise and return the things
    # whose failure would make the service unable to do its job.
    # Config load is one of those things.

    return {"status": "ok", "chat_model": s.chat_model, "embedding_model": s.embedding_model}
