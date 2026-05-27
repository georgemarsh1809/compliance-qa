from typing import NotRequired, TypedDict

from llama_index.core.schema import NodeWithScore


class AgentState(TypedDict):
    question: str
    query: str
    chunks: NotRequired[list[NodeWithScore]]
    grade: NotRequired[bool]
    retry_count: int
    answer: NotRequired[str]
