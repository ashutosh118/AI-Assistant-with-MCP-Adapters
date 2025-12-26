# MCP-based Multi-Tool Orchestrator Example

This project demonstrates how to build an interactive, MCP-compliant application using the Model Context Protocol (MCP) with multiple tools (as MCP servers) orchestrated by a LangChain/LangGraph agent and Azure OpenAI LLM.

## Structure
- `tools/math_server.py`: Math tool MCP server (add, multiply)
- `tools/weather_server.py`: Weather tool MCP server (real-time weather)
- `tools/summarizer_server.py`: Summarizer tool MCP server (summarizes text using local LLM)
- `tools/web_search_server.py`: Web search tool (DuckDuckGo API)
- `tools/currency_converter_server.py`: Currency converter tool (exchangerate.host)
- `tools/wikipedia_server.py`: Wikipedia summary tool
- `tools/unit_converter_server.py`: Unit converter tool (length, weight, temperature)
- `agent_orchestrator.py`: Interactive orchestrator using a LangChain agent and Azure OpenAI
- `requirements.txt`: Python dependencies

## What is MCP?
Model Context Protocol (MCP) is an open protocol for exposing tools (functions, APIs, or services) in a standardized way so that agents and LLMs can discover and use them dynamically. Each tool runs as an independent MCP server, and agents can connect to one or many such servers. This enables modular, distributed, and scalable AI applications.

## How the App Works
- Each tool (math, weather, summarizer, web search, currency converter, Wikipedia, unit converter) is implemented as a separate MCP server using FastMCP.
- The orchestrator script (`agent_orchestrator.py`) launches all tool servers and connects to them using the `langchain-mcp-adapters` library.
- The agent is powered by Azure OpenAI (or any LLM that supports tool-calling).
- The app starts with a disclaimer listing all supported query types.
- The user is prompted for a query (label: Query:). The agent analyzes the query and uses only the relevant tool(s) to answer.
- The app displays which tool(s) were used (or if the answer came from the model only) and shows the final answer.
- The app loops, allowing follow-up questions, and only exits on Ctrl+C.

## Supported Tools & Example Queries
- **Math:** `what's (3 + 5) x 12?`
- **Weather:** `what is the weather in Paris?`
- **Summarizer:** `Summarize: LangChain is a framework for developing applications powered by language models.`
- **Web Search:** `Search: latest news on AI`
- **Currency Converter:** `Convert 100 USD to EUR`
- **Wikipedia Lookup:** `Wikipedia: Alan Turing`
- **Unit Converter:** `Convert 10 miles to kilometers`

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your Azure OpenAI credentials and config as described in `agent_orchestrator.py`.
3. (Optional) If using Ollama for summarization, make sure you have Ollama installed and the Phi-3 model pulled:
   ```bash
   ollama pull phi3
   ```
4. Run the agent orchestrator:
   ```bash
   python agent_orchestrator.py
   ```


## Why is this app MCP-compliant?
- **All tools are exposed as MCP servers** using the FastMCP library, following the MCP protocol for tool registration, invocation, and communication.
- **The orchestrator (agent) connects to tools via MCP** using the `langchain-mcp-adapters` library, which discovers and loads tools dynamically.
- **You can add, remove, or update tools independently**—the agent will discover them at runtime, making the system modular and scalable.
- **Any agent or LLM that speaks MCP can use your tools**, and your agent can use any MCP-compliant tool, enabling interoperability across the AI ecosystem.

## How to Scale the Application

This MCP-based architecture is designed for easy scaling and extensibility. Here’s how you can scale your application:

### 1. Add More Tools (Servers)
- Create a new Python script in the `tools/` directory using FastMCP, following the examples provided.
- Implement your tool logic and expose it with `@mcp.tool()`.
- Start the new tool server as a separate process, or add it to the orchestrator config.
- The agent will automatically discover and use the new tool if it is included in the orchestrator’s `MultiServerMCPClient` config.

### 2. Add More Clients (Agents)
- You can run multiple orchestrator scripts (clients) on different machines or containers.
- Each client can connect to any set of MCP tool servers, local or remote, by specifying their connection details (e.g., stdio, HTTP, etc.).
- Clients can use different LLMs or agent logic as needed.

### 3. Distribute Servers and Tools
- Each MCP tool server can run on a different machine, VM, or container.
- Use network transports (e.g., HTTP) to connect clients and servers across machines or cloud environments.
- Secure your servers with authentication headers if needed.

### 4. Update or Replace Tools Without Downtime
- Stop the old tool server and start the new version with the same MCP interface.
- The agent will continue to discover and use the tool as long as the MCP protocol is followed.

### 5. Add New LLMs or Agents
- Swap out the LLM in your orchestrator (e.g., use a different Azure deployment, OpenAI, or local model) by updating the config.
- You can run multiple agents with different LLMs, each connecting to the same or different set of tools.

### 6. Example: Adding a New Tool
1. Create `tools/my_new_tool_server.py`:
   ```python
   from mcp.server.fastmcp import FastMCP
   mcp = FastMCP("MyNewTool")
   @mcp.tool()
   def do_something(x: int) -> int:
       return x * 2
   if __name__ == "__main__":
       mcp.run(transport="stdio")
   ```
2. Add to orchestrator config:
   ```python
   "mynewtool": {
       "command": "python",
       "args": ["tools/my_new_tool_server.py"],
       "transport": "stdio",
   }
   ```
3. The agent can now use `do_something` as a tool in responses.

---

This project is a template for building scalable, modular, and LLM-powered applications using MCP and LangChain. You can easily extend it by adding more tools or swapping out the LLM/agent as needed.

**Credits:** Ashutosh Srivastava