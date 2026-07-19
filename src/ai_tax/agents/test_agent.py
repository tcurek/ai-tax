"""Test/example agent module.

This file is intentionally simple for now. It gives us a placeholder for
experimenting with future tax-focused agents without wiring them into the app.
"""

from pydantic import BaseModel


class TestAgentInput(BaseModel):
    """Input for the test agent."""

    prompt: str


class TestAgentOutput(BaseModel):
    """Output from the test agent."""

    response: str


def run_test_agent(agent_input: TestAgentInput) -> TestAgentOutput:
    """Run a simple deterministic test agent."""
    return TestAgentOutput(response=f"Test agent received: {agent_input.prompt}")
