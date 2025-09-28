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
mcp_port = int(os.environ.get("FUNCTIONS_CUSTOMHANDLER_PORT", 8080))
mcp = FastMCP("jokes", stateless_http=True, port=mcp_port)

@mcp.tool()
async def call_joke_agent(query: str) -> str:
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


if __name__ == "__main__":
    print("Starting MCP API caller server...")
    mcp.run(transport="streamable-http")