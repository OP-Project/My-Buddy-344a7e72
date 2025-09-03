from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.agents import SequentialAgent
from src.orchestrator.agents.tools.weather_tool import get_weather_by_city #, geolocation_tool
# from agents.tools.weather_tool import get_weather_by_city #, geolocation_tool

# The agent responsible for getting raw weather data
city_finder_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="CityFinderAgent",
    description="Finds the city name based on user input.",
    instruction="""
    You are an AI assistant specializing in geolocation.
    Your task is to return the city name based on the user's input. 
    If the user provides a city name, use it directly.
    If the user does not provide a city name, return `auto:ip` to trigger IP-based geolocation.
    The final output should ONLY be the city name (in English) or `auto:ip`.
    """,
    # tools=[geolocation_tool],
    output_key="city" # Saves the result to state['city']
)

# --- 1. Define Specialist Agents ---

# The agent responsible for getting raw weather data
weather_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="WeatherBot",
    description="Gets the current weather for a specific location.",
    instruction="""
    You are an AI assistant specializing in weather updates.
    Your sole purpose is to use the `get_weather_by_city` tool to get the weather for a {city}.
    The final output should ONLY be the raw report from the tool.
    """,
    tools=[get_weather_by_city],
    output_key="weather_data" # Saves the result to state['weather_data']
)

# Step 2: Get lifestyle tips based on the weather data.
lifestyle_advisor_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="LifestyleAdvisorAgent",
    description="Recommends activities based on weather.",
    instruction="""
    You are an expert Human Habitant Researcher.
    Your task is to find lifestyle tips based on the provided weather report.

    **Today's Weather:**
    {weather_data}

    Based on the weather above, use your `Google Search` tool to find suitable activities, clothing recommendations, and health tips.
    Output a bulleted list of your findings.
    """,
    tools=[google_search],
    output_key="lifestyle_tips" # Saves the result to state['lifestyle_tips']
)

# Step 3: Write the final report using all collected data.
writer_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="WriterBot",
    description="Synthesizes weather data and lifestyle tips into a clear, well-formatted daily report for users. Ensures all relevant information is included and easy to understand.",
    instruction="""
    You are a professional report writer. Your job is to combine the provided weather data and lifestyle suggestions into a single, comprehensive, and easy-to-read daily report for the user.

    Always include both sections: Today's Weather Summary and Lifestyle Suggestions. Do not omit any section, even if one is empty (in that case, write 'No suggestions available.').

    Use this format exactly:

    # Today's Weather Summary
    {weather_data}

    # Lifestyle Suggestions
    {lifestyle_tips}

    ---
    ## Example 1
    # Today's Weather Summary
    Clear skies, 28°C, light breeze.

    # Lifestyle Suggestions
    - Wear light, breathable clothing.
    - Stay hydrated throughout the day.
    - Great day for outdoor exercise.

    ---
    ## Example 2
    # Today's Weather Summary
    Heavy rain, 19°C, high humidity.

    # Lifestyle Suggestions
    - Carry an umbrella and wear waterproof shoes.
    - Avoid outdoor activities if possible.
    - Drink warm beverages to stay comfortable.

    ---
    Stick to this structure and formatting for every report you generate.
    """,
    tools=[],
    output_key="final_weather_report" 
)

# --- 2. Create the SequentialAgent using the `sub_agents` list ---

daily_weather_report_workflow = SequentialAgent(
    name="DailyWeatherReportWorkflow",
    description="A workflow that gets weather, finds lifestyle tips, and writes a full report.",
    # The `sub_agents` parameter enables the state-passing mechanism
    sub_agents=[city_finder_agent, weather_agent, lifestyle_advisor_agent, writer_agent],
)