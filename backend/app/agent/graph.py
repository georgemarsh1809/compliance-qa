from langgraph.graph import END, START, StateGraph

from app.agent.nodes import generate_node, grade_node, retrieve_node, rewrite_node
from app.agent.state import AgentState

MAX_RETRIES = 2


def decide_after_grade(state: AgentState) -> str:
    if state["grade"]:
        return "generate"
    if state["retry_count"] >= MAX_RETRIES:
        return "generate"
    return "rewrite"


builder = StateGraph(AgentState)

# Define Nodes
builder.add_node("retrieve_node", retrieve_node)
builder.add_node("grade_node", grade_node)
builder.add_node("rewrite_node", rewrite_node)
builder.add_node("generate_node", generate_node)

# Define Edges
builder.add_edge(START, "retrieve_node")
builder.add_edge("retrieve_node", "grade_node")
builder.add_edge("rewrite_node", "retrieve_node")
builder.add_edge("generate_node", END)

builder.add_conditional_edges(
    "grade_node", decide_after_grade, {"generate": "generate_node", "rewrite": "rewrite_node"}
)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke(
        {
            "question": "if a shop sells me something different from what I paid for, is that against food law?",
            "query": "if a shop sells me something different from what I paid for, is that against food law?",
            "retry_count": 0,
        }
    )

    print(result["answer"])
