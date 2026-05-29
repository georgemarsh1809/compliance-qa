from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class Source(BaseModel):
    page: int | None
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
