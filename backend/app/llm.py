from typing import cast

from anthropic import Anthropic
from anthropic.types import TextBlock
from llama_index.core.schema import NodeWithScore

from app.config import get_settings
from app.retrieval import retrieve


def format_context(nodes: list[NodeWithScore]) -> str:
    context = []
    for i, n in enumerate(nodes, start=1):
        context.append(f"[Source: {i} - Page {n.node.metadata.get('page_label')}]\n{n.node.text}")
    return "\n\n".join(context)


def generate_answer(question: str, nodes: list[NodeWithScore]) -> str:
    # 1. Get settings (inside the function so config isn't build on import - cached settings are reused)
    s = get_settings()

    # 2. Construct client
    client = Anthropic(api_key=s.anthropic_api_key)

    # 3. Take nodes and build context
    context = format_context(nodes)

    # 4. Build system prompt
    system_prompt = """
    You are answering questions about the UK food safety law for food businesses, based on provided sources.
    You are to answer using ONLY the provided sources; DO NOT use outside knowledge.
    For every answer you provide, return the source number and page number for any claims (e.g. 'Source 2 - Page 11')
    so the answer is traceable. If the sources don't contain the answer,
    say so plainly rather than guessing, fabricating, or filling gaps from general knowledge.
    """

    # 5. Build content (the context (nodes) and and the question being asked)
    user_content = f"Here are the sources: {context}. Question: {question}"

    # 6. Call the client
    response = client.messages.create(
        model=s.chat_model,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )

    # 7. Narrow to a text block so we safely access .text (and fail loudly otherwise)
    block = response.content[0]
    if isinstance(block, TextBlock):
        return cast(str, block.text)
    raise ValueError("Expected a text block from Claude, but got something else.")


def answer_question(question: str, top_k: int = 3) -> str:
    # Find relevant chunks from the corpus, based on the question:
    nodes = retrieve(question, top_k)
    # Pass the relevant chunks to Claude, with the original question, so it can formulate an answer
    return generate_answer(question, nodes)


if __name__ == "__main__":
    print(answer_question("what temperature should I store chilled food at?"))
