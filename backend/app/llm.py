from functools import lru_cache
from typing import cast

from anthropic import Anthropic
from anthropic.types import TextBlock
from llama_index.core.schema import NodeWithScore

from app.config import get_settings
from app.retrieval import retrieve


@lru_cache
def get_client() -> Anthropic:
    s = get_settings()
    return Anthropic(api_key=s.anthropic_api_key)


def call_claude(model: str, system_prompt: str, max_tokens: int, user_content: str) -> str:
    # 1. Construct client
    client = get_client()

    # 2. Call the client
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    block = response.content[0]
    if isinstance(block, TextBlock):
        return cast(str, block.text.strip())
    raise ValueError("Expected a text block from Claude, but got something else.")


def format_context(nodes: list[NodeWithScore]) -> str:
    context = []
    for i, n in enumerate(nodes, start=1):
        context.append(f"[Source: {i} - Page {n.node.metadata.get('page_label')}]\n{n.node.text}")
    return "\n\n".join(context)


def generate_answer(question: str, nodes: list[NodeWithScore]) -> str:
    s = get_settings()

    # 1. Take nodes and build context
    context = format_context(nodes)

    # 2. Build system prompt
    system_prompt = """
    You are answering questions about the UK food safety law for food businesses, based on provided sources.
    You are to answer using ONLY the provided sources; DO NOT use outside knowledge.
    For every answer you provide, return the source number and page number for any claims (e.g. 'Source 2 - Page 11')
    so the answer is traceable. If the sources don't contain the answer,
    say so plainly rather than guessing, fabricating, or filling gaps from general knowledge.
    """

    # 3. Build content (the context (nodes) and and the question being asked)
    user_content = f"Here are the sources: {context}. Question: {question}"

    response = call_claude(
        model=s.chat_model, system_prompt=system_prompt, max_tokens=1024, user_content=user_content
    )

    return response


def answer_question(question: str, top_k: int = 3) -> str:
    # Find relevant chunks from the corpus, based on the question:
    nodes = retrieve(question, top_k)
    # Pass the relevant chunks to Claude, with the original question, so it can formulate an answer
    return generate_answer(question, nodes)


if __name__ == "__main__":
    print(answer_question("what is the definition of due dilligence?"))
