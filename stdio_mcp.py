import os

from mcp.server.fastmcp import FastMCP

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
AI_FOUNDRY_PROJECT_ENDPOINT = os.environ["AI_FOUNDRY_PROJECT_ENDPOINT"]
AI_FOUNDRY_AGENT_ID = os.environ["AI_FOUNDRY_AGENT_ID"]


# Initialize the MCP server
mcp = FastMCP(
  name="jokes-agent-mcp",
  instructions="Use this agent to tell a joke."
)


@mcp.tool()
def call_joke_agent(query: str) -> str:
    print(f"user query {query}")

    project = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=AI_FOUNDRY_PROJECT_ENDPOINT)

    agent = project.agents.get_agent(AI_FOUNDRY_AGENT_ID)

    thread = project.agents.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content=query
    )

    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id)

    if run.status == "failed":
        print(f"agent run failed: {run.last_error}")
        return f"Error: error occurred - {run.last_error}"
    else:
        result = ""
        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.DESCENDING)

        for message in messages:
            if message.text_messages:
                result = message.text_messages[-1].text.value
                break

        return result


def debug_mode():
    """Debug mode to test the agent directly."""
    print("=== AI Foundry Agent MCP Server Debug Mode ===")
    
    # Test the joke agent directly
    test_query = "Tell me a programming joke"
    
    print(f"\nCalling joke agent with query: '{test_query}'")
    
    try:
        # Call the agent function directly
        result = call_joke_agent(test_query)
        print("\n=== Agent Response ===")
        print(result)
    except Exception as e:
        print(f"\n=== Error ===")
        print(f"Failed to call agent: {e}")


def main():
    import sys
    
    # Check if we're in debug mode
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        debug_mode()
    else:
        print("Starting MCP API caller server...")
        mcp.run()


if __name__ == "__main__":
    main()
