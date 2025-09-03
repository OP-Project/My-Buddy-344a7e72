import os
import ipinfo
import requests
import geocoder
from dotenv import load_dotenv
load_dotenv()

def get_weather_by_city(location: str) -> dict:
    """
    Get current weather information for a given city using the WeatherAPI.

    Parameters:
        location (str): Name of the city or location (e.g., 'London', 'New York').

    Returns:
        dict: A dictionary with:
            - If success:
                {
                    "status": "success",
                    "report": "<human-readable weather summary>"
                }
            - If error:
                {
                    "status": "error",
                    "error_message": "<what went wrong>"
                }
    """
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "http://api.weatherapi.com/v1/current.json"
    print("get_weather_by_city called with location:", location)
    try:
        response = requests.get(f"{base_url}?key={api_key}&q={location}")
        response.raise_for_status()
        data = response.json()

        report = (
            f"Weather in {data['location']['name']} ({data['location']['country']}, {data['location']['region']}):\n"
            f"Condition: {data['current']['condition']['text']}\n"
            f"Temperature: {data['current']['temp_c']}°C / {data['current']['temp_f']}°F\n"
            f"Feels Like: {data['current']['feelslike_c']}°C / {data['current']['feelslike_f']}°F\n"
            f"Humidity: {data['current']['humidity']}%\n"
            f"Wind: {data['current']['wind_kph']} km/h from {data['current']['wind_dir']}\n"
            f"Visibility: {data['current']['vis_km']} km\n"
            f"Pressure: {data['current']['pressure_mb']} mb\n"
            f"UV Index: {data['current']['uv']}\n"
            f"Last Updated: {data['current']['last_updated']}"
        )
        print("weather temp:", data['current']['temp_c'])
        return {
            "status": "success",
            "report": report
        }

    except Exception as e:
        print("Error fetching weather data:", str(e))
        return {
            "status": "error",
            "error_message": f"Failed to fetch weather data: {str(e)}"
        }


# # Initialize IPInfo for geolocation
# ipinfo_token = os.getenv("IPINFO_TOKEN")
# ipinfo_handler = ipinfo.getHandler(ipinfo_token) if ipinfo_token else None

# def geolocation_tool() -> str:
#     """Get current location using IP geolocation"""
#     ipinfo_token_env = os.getenv("IPINFO_TOKEN")
#     if ipinfo_token_env is not None:
#         os.environ["IPINFO_TOKEN"] = ipinfo_token_env
#     try:
#         if ipinfo_handler:
#             # Use IPInfo for more accurate geolocation
#             ip_address = requests.get('https://api.ipify.org').text
#             details = ipinfo_handler.getDetails(ip_address)
            
#             location_info = f"""
#             Current Location (IP-based):
#             City: {details.city}
#             Region: {details.region}
#             Country: {details.country}
#             Coordinates: {details.loc}
#             IP Address: {ip_address}
#             """
#             print("Hello",location_info)
#             return details.city
#         else:
#             # Fallback to geocoder
#             g = geocoder.ip('me')
#             if g.ok:
#                 location_info = f"""
#                 Current Location (IP-based):
#                 City: {g.city}
#                 State: {g.state}
#                 Country: {g.country}
#                 Coordinates: {g.lat}, {g.lng}
#                 """
#                 return g.city
#             else:
#                 return "Could not determine current location"
#     except Exception as e:
#         return f"Error getting location: {str(e)}"