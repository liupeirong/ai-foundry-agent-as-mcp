# Azure AI Foundry Agent as MCP Server

This repo exposes an Azure AI Foundry agent as an MCP server running on
Azure Functions. This lets you call an AI Foundry agent from any client that
supports MCP.

## Local MCP Server using stdio

[stdio_mcp.py](./stdio_mcp.py) implements a simple local MCP server that
wraps the Foundry agent. To run it in vscode,

* run `uv sync` to install the packages.
* copy [sample.env](./sample.env) to .env and set the values.
* run `az login` so that the mcp server can use your credential to access
AI Foundry.
* open the file [mcp.json](./.vscode/mcp.json), and __start__ the
 `ai-foundry-joke-agent-stdio-mcp`.
* in the chat pane, set GitHub Copilot to agent mode, __Configure Tools__ to
only include this mcp.
* type a query in the chat pane, for example, "tell me a joke about vibe coding.".
VSCode should invoke the Foundry agent.

## Remote MCP Server running in Azure Function

[function_mcp.py](./function_mcp.py) implements a http MCP server.
It can run locally or in Azure Function. This part is inspired by
[Azure Sample - mcp-sdk-functions-hosting-python](https://github.com/Azure-Samples/mcp-sdk-functions-hosting-python).
Follow the instructions to [host this mcp server in Azure Functions](https://github.com/Azure-Samples/mcp-sdk-functions-hosting-python/blob/main/ExistingServer.md).

> Note that this project is initialized with `uv`. However, to run Azure
Functions locally or remotely, use `requirements.txt`.

## Integrate with Copilot Studio

At the time of this writing, Microsoft Copilot Studio doesn't yet support
out-of-the-box integration with Azure AI Foundry Agent. However it does
support integration with MCP server. To integrate our MCP server with
Copilot Studio:

* Create an agent in Copilot Studio.
* Once the agent is created, go to the __Tools__ tab, __Add a Tool__,
 __New Tool__, click on __Model Context Protocol__. Input your Azure Function
 URL. Select API Key for authentication, and the key will be provided
 in the request header `x-functions-key`.
* Once the tool is added, create a connection by providing the API Key
of your Azure Function.
* Now you should be able to test the Copilot Studio agent to invoke
the Foundry agent.

> Note that to publish the Copilot Studio agent to a channel such as Teams,
You need to have the role `Copilot Studio Author` and have a paid license
for Copilot Studio. Trial license doesn't let you publish agents.

## Troubleshooting

To verify the client indeed invoked the Azure Function, check the metrics
and logs in Azure Function.

If the Azure Function fails to run, check if it can access the blob storage
provisioned with the Azure Function. For testing, it's easiest to enable public network
just to rule out other causes of failures. Please note that certain policies
might revert the blob storage to private network after a period of time, for example, 24 hours.

If the MCP server fails to run, check Azure Function's logs in App Insights.
If it fails to retrieve the Foundry agent, make sure:

* your Function has either System Managed Identity or User Managed Identity
 enabled.
* Grant the identity `Azure AI User` role on the Foundry instance.
* For User Managed Identity, set the environment variable `AZURE_CLIENT_ID`
to be the client ID of the User Managed Identity.
