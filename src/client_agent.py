from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import asyncio

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

model = ChatOpenAI(model="gpt-5-mini")

BASE_DIR = Path(__file__).resolve().parent  # .../code_research_agent/src
MAX_MESSAGES = 6  # 3 turns

server_params = StdioServerParameters(
    command="python",
    args=[str(BASE_DIR / "server.py")],
)

async def main():
    # Start MCP server over stdio and keep it alive for the whole session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()

            # Load MCP tools (set_repo, list_all_files, read_file)
            tools = await load_mcp_tools(session)
            agent = create_agent(model, tools)

            print("Code Research Agent")
            print("Type your question about the repo, or 'exit' to quit.\n")

            history = []

            while True:
                try:
                    user_input = input("You> ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

                if not user_input:
                    continue
                if user_input.lower() in {"exit", "quit", "q"}:
                    print("Exiting")
                    break


                history.append(HumanMessage(content=user_input))

                result = await agent.ainvoke({"messages": history})

                final_msg = result["messages"][-1].content

                # after appending AIMessage
                history.append(AIMessage(content=final_msg))

                if len(history) > MAX_MESSAGES:
                    history = history[-MAX_MESSAGES:]
                print(f"GPT> {final_msg}\n")


if __name__ == "__main__":
    asyncio.run(main())