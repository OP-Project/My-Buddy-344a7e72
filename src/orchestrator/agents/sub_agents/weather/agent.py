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
            command='npx',
            args=["-y", "@h1deya/mcp-server-weather"],
        ),
        timeout = 100.0
    )
)

root_agent = LlmAgent(
    name="weather_agent",
    description="A Weather agent that fetches current weather information using an external MCP Weather tool.",
    model="gemini-2.0-flash-001",
    instruction=(
        "You are the Weather Scout. Your task is to fetch current weather information for a specified location using the connected Weather MCP tool. "
        "1. **Identify Subreddit:** Determine which region the user wants weather from. Default to 'Delhi' if none is specified. "
        "2. **Call Discovered Tool:** You **MUST** look for and call the tool named 'get-forecast' with the identified location name and optionally a limit. "
        "3. **Present Results:** The tool will return a formatted string containing the current weather information or an error message. "
        "4. **Handle Missing Tool:** If you cannot find the required Reddit tool, inform the user. "
        "5. **Do Not Hallucinate:** Only provide information returned by the tool."
    ),
    tools=[mcp_toolset],
)
