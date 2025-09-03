from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.agents import SequentialAgent
from src.orchestrator.agents.tools.stock_info_tool import get_stock_analysis
# from agents.tools.stock_info_tool import get_stock_analysis

# --- 1. Define Specialist Agents ---

# The agent responsible for getting raw stock data
stock_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="StockBot",
    description="Gets the latest stock information and analysis for a specific company or index.",
    instruction="""
    You are an AI assistant specializing in Indian stock market updates.
    Your sole purpose is to use the `get_stock_analysis` tool to get the latest stock information for a company or index.
    The final output should ONLY be the raw report from the tool.
    """,
    tools=[get_stock_analysis],
    output_key="stock_data" # Saves the result to state['stock_data']
)

# Step 2: Get investment/lifestyle tips based on the stock data.
stock_advisor_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="StockAdvisorAgent",
    description="Recommends investment or financial tips based on stock data.",
    instruction="""
    You are an expert Financial Advisor.
    Your task is to find investment tips and financial advice based on the provided stock report.

    **Today's Stock Data:**
    {stock_data}

    Based on the stock data above, use your `Google Search` tool to find relevant investment advice, risk warnings, and market news.
    Output a bulleted list of your findings.
    """,
    tools=[google_search],
    output_key="advisor_tips" # Saves the result to state['advisor_tips']
)

# Step 3: Write the final report using all collected data.
writer_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="WriterBot",
    description="Writes a final, human-readable stock market report.",
    instruction="""
    You are a skilled Financial Content Writer.
    Your goal is to synthesize all the provided information into a single, comprehensive, and easy-to-read report.

    **Raw Stock Data:**
    {stock_data}

    **Advisor Suggestions:**
    {advisor_tips}

    Combine this information into a final report with clear headings for "Today's Stock Market Summary" and "Advisor Suggestions".
    """,
    tools=[],
    output_key="final_stock_report" 
)

# --- 2. Create the SequentialAgent using the `sub_agents` list ---

daily_stock_report_workflow = SequentialAgent(
    name="DailyStockReportWorkflow",
    description="A workflow that gets stock data, finds advisor tips, and writes a full report.",
    sub_agents=[stock_agent, stock_advisor_agent, writer_agent],
)

