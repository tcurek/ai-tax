"""A minimal LangGraph hello-world agent."""

from typing import TypedDict

from langgraph.graph import END, StateGraph


class HelloWorldState(TypedDict):
    """State passed through the hello-world agent graph."""

    name: str
    message: str


def say_hello(state: HelloWorldState) -> HelloWorldState:
    """Create a greeting message."""
    name = state.get("name", "AI Tax")
    return {
        **state,
        "message": f"Hello, {name}!",
    }


def build_hello_world_agent():
    """Build and compile the hello-world LangGraph agent."""
    graph = StateGraph(HelloWorldState)
    graph.add_node("say_hello", say_hello)
    graph.set_entry_point("say_hello")
    graph.add_edge("say_hello", END)
    return graph.compile()


def run_hello_world_agent(name: str = "AI Tax") -> str:
    """Run the hello-world agent and return its message."""
    agent = build_hello_world_agent()
    result = agent.invoke({"name": name, "message": ""})
    return result["message"]
