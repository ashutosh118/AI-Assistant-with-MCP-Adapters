import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
import config as cf
from config import *

# Set Azure OpenAI environment variables
os.environ["OPENAI_API_TYPE"] = OPENAI_API_TYPE
os.environ["OPENAI_API_VERSION"] = OPENAI_API_VERSION
os.environ["OPENAI_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    deployment_name=azure_openai_config['deployment_name'],
    model_name=azure_openai_config['model_name'],
    openai_api_version=azure_openai_config['openai_api_version'],
    openai_api_type=azure_openai_config['openai_api_type'],
    temperature=azure_openai_config['temperature']
)

def extract_final_answer(response):
    # Find the last AIMessage with non-empty content
    for msg in reversed(response.get("messages", [])):
        if hasattr(msg, "content") and msg.content:
            return msg.content
    return "No answer found."

def extract_tools_used(response):
    tools = set()
    for msg in response.get("messages", []):
        # ToolMessage: has 'name' attribute (tool name)
        if hasattr(msg, "name") and msg.name:
            tools.add(msg.name)
        # AIMessage: may have 'tool_calls' in additional_kwargs
        if hasattr(msg, "additional_kwargs") and msg.additional_kwargs:
            tool_calls = msg.additional_kwargs.get("tool_calls", [])
            for call in tool_calls:
                if "name" in call:
                    tools.add(call["name"])
    return tools

async def main():
    print("""
    DISCLAIMER: This application supports the following types of queries:
    - Math operations (e.g., what's (3 + 5) x 12?)
    - Weather information (e.g., what is the weather in Paris?)
    - Text summarization (e.g., Summarize: <your text>)
    - Web search (e.g., Search: latest news on AI)
    - Currency conversion (e.g., Convert 100 USD to EUR)
    - Wikipedia lookup (e.g., Wikipedia: Alan Turing)
    - Unit conversion (e.g., Convert 10 miles to kilometers)
    You can ask follow-up questions. Type Ctrl+C to exit.
    """)
    client = MultiServerMCPClient({
        "math": {
            "command": "python",
            "args": ["tools/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            "command": "python",
            "args": ["tools/weather_server.py"],
            "transport": "stdio",
        },
        "summarizer": {
            "command": "python",
            "args": ["tools/summarizer_server.py"],
            "transport": "stdio",
        },
        "websearch": {
            "command": "python",
            "args": ["tools/web_search_server.py"],
            "transport": "stdio",
        },
        "currencyconverter": {
            "command": "python",
            "args": ["tools/currency_converter_server.py"],
            "transport": "stdio",
        },
         "wikipedia": {
            "command": "python",
            "args": ["tools/wikipedia_server.py"],
            "transport": "stdio",
        },
        "unitconverter": {
            "command": "python",
            "args": ["tools/unit_converter_server.py"],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    conversation = []
    try:
        while True:
            user_query = input("\nQuery: ")
            if not user_query.strip():
                print("Please enter a query.")
                continue
            conversation.append({"role": "user", "content": user_query})
            response = await agent.ainvoke({"messages": conversation})
            tools_used = extract_tools_used(response)
            if tools_used:
                print(f"\n[Used tool(s): {', '.join(tools_used)}]")
            else:
                print("\n[Response from model only]")
            answer = extract_final_answer(response)
            print("Answer:", answer)
            print("-"*100)
            conversation.append({"role": "assistant", "content": answer})
    except KeyboardInterrupt:
        print("\nExiting. Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
