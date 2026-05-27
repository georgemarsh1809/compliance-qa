from typing import Any

from app.agent.state import AgentState
from app.config import get_settings
from app.llm import call_claude, format_context, generate_answer
from app.retrieval import retrieve


# Node: Grade
def grade_node(state: AgentState) -> dict[str, Any]:
    s = get_settings()

    # 1. Read question and chunks from state
    question = state["question"]
    chunks = format_context(state["chunks"])

    # 2. Build grading prompt
    system_prompt = """
    You are assessing whether the provided source extracts contain enough information to answer the question.
    You MUST reply with ONLY one word answers.
    Reply YES if the sources are sufficient to answer it, NO if they are not.
    """

    user_content = f"Question: {question}\n\nSources:\n{chunks}"

    response = call_claude(
        model=s.chat_model, system_prompt=system_prompt, max_tokens=10, user_content=user_content
    )

    is_sufficient = response.upper() == "YES"
    return {"grade": is_sufficient}


# Node: Rewrite
def rewrite_node(state: AgentState) -> dict[str, Any]:
    # This node will run if the grading node says the retrieval is insufficient

    s = get_settings()

    initial_question = state["question"]

    system_prompt = """
    You are rewriting a question as a better search query for retrieving relevant passages from a corpus text.
    Make sure to rephrase using different terms or a different angle that might match how the source material is written.
    Return ONLY a string containing the new question.
    """

    response = call_claude(
        model=s.chat_model,
        system_prompt=system_prompt,
        max_tokens=64,
        user_content=initial_question,
    )

    return {"query": response, "retry_count": state["retry_count"] + 1}


# Node: Retrieve
def retrieve_node(state: AgentState) -> dict[str, Any]:
    return {"chunks": retrieve(state["query"])}


# Node: Generate
def generate_node(state: AgentState) -> dict[str, Any]:
    return {"answer": generate_answer(state["question"], state["chunks"])}


if __name__ == "__main__":
    chunks = retrieve("What is the due dilligence defence?")

    state: AgentState = {
        "question": "what is the due diligence defence?",
        "query": "what is the due diligence defence?",
        "chunks": chunks,
        "retry_count": 0,
    }

    print(rewrite_node(state))
