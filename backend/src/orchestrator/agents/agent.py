from google.adk.agents import Agent
# from .agent_prompts import ROOT_AGENT_DESCRIPTION ,ROOT_AGENT_INSTRUCTION
# from .sub_agents.sub_agents import google_search_agent

# root_agent = Agent(
#     model="gemini-2.0-flash-001",
#     name="hey_buddy",
#     description=ROOT_AGENT_DESCRIPTION,
#     instruction=ROOT_AGENT_INSTRUCTION,
#     # tools=[],
#     sub_agents=[google_search_agent]
# )

from google.adk.agents import LlmAgent 
from google.adk.tools import google_search
from google.adk.tools import load_memory # Tool to query memory
from src.orchestrator.agents.sub_agents.city_weather.agent import daily_weather_report_workflow
from src.orchestrator.agents.sub_agents.indian_stock.agent import daily_stock_report_workflow

from src.config.logging import logger

# from agents.sub_agents.city_weather.agent import daily_weather_report_workflow
# from agents.sub_agents.indian_stock.agent import daily_stock_report_workflow

from google.adk.tools.agent_tool import AgentTool
Agent_Search = Agent(
    model='gemini-2.0-flash-exp',
    name='SearchAgent',
    instruction="""
    You're a spealist in Google Search.
    Use the `google_search` tool to find information on any topic.
    """,
    tools=[google_search]
)

buddy_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="hey_buddy",
    description="A helpful AI assistant that can answer general questions, provide real-time weather updates (with or without location details) and generate daily stock market reports with investment advice.",
    instruction=(
        "You are a helpful assistant. You can answer general questions, provide real-time weather updates for any city and also can detect location if city is not provided, and generate daily stock market reports with investment advice. "
        "Use the appropriate tool for each request: use the weather workflow for weather-related queries and the stock report workflow for stock/investment queries. "
        "Always specify the name of the tool or workflow you are using to answer the question. If you are using a tool, make sure to mention its name in your response."
    ),
    tools=[
        AgentTool(agent=Agent_Search), 
        AgentTool(agent=daily_weather_report_workflow), 
        AgentTool(agent=daily_stock_report_workflow)
        ],  # preferred way with multiple tools
    # tools=[get_weather_by_city] # worked with only one tool
    # sub_agents=[memory_recall_agent]  # Add the memory recall agent as a sub-agent
)

root_agent = buddy_agent

# This is to run agent seperately for testing purposes via python .\src\orchestrator\agents\agent.py
# from google.genai import types
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService

# APP_NAME="buddy_orchestrator"
# USER_ID="user1"
# SESSION_ID="1234"

# import asyncio

# session_service = InMemorySessionService()

# async def setup():
#     session = await session_service.create_session(
#         app_name=APP_NAME,
#         user_id=USER_ID,
#         session_id=SESSION_ID,
#     )
#     return session

# session = asyncio.run(setup())
# runner = Runner(agent=buddy_agent, app_name=APP_NAME, session_service=session_service)

# def call_agent(query):
#     content = types.Content(role='user', parts=[types.Part(text=query)])
#     events = runner.run(
#         user_id=USER_ID,
#         session_id=SESSION_ID,
#         new_message= content,
#     )

#     for event in events:
#         if event.is_final_response() and event.content and event.content.parts:
#             final_response = event.content.parts[0].text
#             logger.info("AGENT RESPONSE:", final_response)


# async def explore_session_events():

#     call_agent("What is the capital of France?")
    
#     logger.info("========== Session Event Exploration 1 ==========")
#     session = await session_service.get_session(
#         app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
#     )
#     logger.info(f"Type of session: {type(session)}")
#     if session is not None:
#         logger.info(f"Session State: {session.state}")
#         logger.info(f"Session Events: {len(session.events)}")
#     else:
#         logger.info("Session is None. Cannot display state or events.")
#     logger.info("===============================================")

#     call_agent("What is the capital of India?")

#     logger.info("========== Session Event Exploration 2 ==========")
#     session = await session_service.get_session(
#         app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
#     )
#     logger.info(f"Type of session: {type(session)}")
#     if session is not None:
#         logger.info(f"Session State: {session.state}")
#         logger.info(f"Session Events: {len(session.events)}")
#     else:
#         logger.info("Session is None. Cannot display state or events.")
#     logger.info("===============================================")

# asyncio.run(explore_session_events())