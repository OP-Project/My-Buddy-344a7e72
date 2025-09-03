import asyncio
import os
from google.adk.agents import Agent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from dotenv import load_dotenv

# Load environment variables
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..', '.env'))
load_dotenv()

mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='uvx',
            args=['--from', 'git+https://github.com/adhikasp/mcp-reddit.git', 'mcp-reddit'],
        ),
        timeout = 100.0
    )
)

root_agent = LlmAgent(
    name="async_reddit_scout_agent",
    description="A Reddit scout agent that searches for hot posts in a given subreddit using an external MCP Reddit tool.",
    model="gemini-2.0-flash-001",
    instruction=(
        "You are the Async Reddit News Scout. Your task is to fetch hot post titles from any subreddit using the connected Reddit MCP tool. "
        "1. **Identify Subreddit:** Determine which subreddit the user wants news from. Default to 'gamedev' if none is specified. "
        "2. **Call Discovered Tool:** You **MUST** look for and call the tool named 'fetch_reddit_hot_threads' with the identified subreddit name and optionally a limit. "
        "3. **Present Results:** The tool will return a formatted string containing the hot post information or an error message. "
        "4. **Handle Missing Tool:** If you cannot find the required Reddit tool, inform the user. "
        "5. **Do Not Hallucinate:** Only provide information returned by the tool."
    ),
    tools=[mcp_toolset],
)
