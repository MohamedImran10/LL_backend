#!/usr/bin/env python3
"""
Standalone Flight Agent Script
This script implements the agentic flight search functionality from your original code.
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()
AMADEUS_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_SECRET = os.getenv("AMADEUS_SECRET")

# Debug environment variables
print(f"🔑 API Key present: {bool(AMADEUS_KEY)}")
print(f"🔒 API Secret present: {bool(AMADEUS_SECRET)}")

def parse_relative_date(date_str: str) -> str:
    """Convert relative dates like 'tomorrow' to YYYY-MM-DD format"""
    today = datetime.now().date()
    
    date_str_lower = date_str.lower().strip()
    print(f"📅 Parsing date: '{date_str}' -> Today is {today}")
    
    # Handle relative dates
    if date_str_lower == 'tomorrow':
        future_date = today + timedelta(days=1)
    elif date_str_lower == 'today':
        future_date = today
    elif 'next monday' in date_str_lower:
        days_until_monday = (0 - today.weekday()) % 7
        if days_until_monday == 0:  # Today is Monday
            days_until_monday = 7
        future_date = today + timedelta(days=days_until_monday)
    elif 'next tuesday' in date_str_lower:
        days_until_tuesday = (1 - today.weekday()) % 7
        if days_until_tuesday == 0:  # Today is Tuesday
            days_until_tuesday = 7
        future_date = today + timedelta(days=days_until_tuesday)
    elif 'next wednesday' in date_str_lower:
        days_until_wednesday = (2 - today.weekday()) % 7
        if days_until_wednesday == 0:  # Today is Wednesday
            days_until_wednesday = 7
        future_date = today + timedelta(days=days_until_wednesday)
    elif 'next thursday' in date_str_lower:
        days_until_thursday = (3 - today.weekday()) % 7
        if days_until_thursday == 0:  # Today is Thursday
            days_until_thursday = 7
        future_date = today + timedelta(days=days_until_thursday)
    elif 'next friday' in date_str_lower:
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:  # Today is Friday
            days_until_friday = 7
        future_date = today + timedelta(days=days_until_friday)
    elif 'next saturday' in date_str_lower:
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:  # Today is Saturday
            days_until_saturday = 7
        future_date = today + timedelta(days=days_until_saturday)
    elif 'next sunday' in date_str_lower:
        days_until_sunday = (6 - today.weekday()) % 7
        if days_until_sunday == 0:  # Today is Sunday
            days_until_sunday = 7
        future_date = today + timedelta(days=days_until_sunday)
    elif 'next week' in date_str_lower:
        future_date = today + timedelta(days=7)
    else:
        # If it's already in YYYY-MM-DD format, validate it
        try:
            input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            # If date is in past, add 1 year to make it future
            if input_date < today:
                print(f"⚠️ Date {date_str} is in the past, adding 1 year")
                future_date = input_date.replace(year=input_date.year + 1)
            else:
                future_date = input_date
        except ValueError:
            # If not a valid date format, return the original string and let the tool handle it
            print(f"⚠️ Invalid date format '{date_str}', passing as-is")
            return date_str
    
    print(f"📅 Final calculated date: {future_date.strftime('%Y-%m-%d')}")
    return future_date.strftime("%Y-%m-%d")

def flight_search(origin: str, destination: str, date: str) -> List[Dict]:
    """
    Searches for flights using the Amadeus API for any origin, any destination, and date.
    Date can be in YYYY-MM-DD format or relative terms like 'tomorrow', 'next Monday', etc.
    Returns a list of flight options or an error message.
    """
    # Parse relative dates - this will handle the conversion
    formatted_date = parse_relative_date(date)
    
    print(f"\n--- 🛠️ Calling Tool: flight_search(origin='{origin}', destination='{destination}', date='{formatted_date}') ---\n")
    
    try:
        # Step 1: Get access token
        print("🔐 Getting access token...")
        token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        token_data = {
            "grant_type": "client_credentials", 
            "client_id": AMADEUS_KEY, 
            "client_secret": AMADEUS_SECRET
        }
        token_headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        print(f"🔐 Token response status: {token_response.status_code}")
        
        if token_response.status_code != 200:
            return [{"error": f"Authentication failed: {token_response.status_code} - {token_response.text}"}]
        
        token_json = token_response.json()
        access_token = token_json.get("access_token")
        
        if not access_token:
            return [{"error": "Failed to get access token from Amadeus API"}]
        
        print("✅ Successfully obtained access token")
        
        # Step 2: Search for flights
        print("🔍 Searching for flights...")
        search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin.upper(), 
            "destinationLocationCode": destination.upper(), 
            "departureDate": formatted_date, 
            "adults": 1, 
            "max": 5,
            "currencyCode": "INR"
        }
        
        search_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔍 Search params: {params}")
        search_response = requests.get(search_url, headers=search_headers, params=params)
        print(f"🔍 Search response status: {search_response.status_code}")
        
        if search_response.status_code != 200:
            error_msg = f"Flight search failed: {search_response.status_code}"
            try:
                error_detail = search_response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {search_response.text}"
            return [{"error": error_msg}]
        
        search_data = search_response.json()
        flights = search_data.get("data", [])
        print(f"✈️ Found {len(flights)} flights")

        if not flights:
            return [{"error": f"No flights found from {origin} to {destination} on {formatted_date}."}]

        # Step 3: Process flight data
        results = []
        for flight in flights:
            try:
                # Get airline code
                airlines = flight.get("validatingAirlineCodes", [])
                airline = airlines[0] if airlines else "Unknown"
                
                # Get price
                price_info = flight.get("price", {})
                total_price = price_info.get("total", "N/A")
                currency = price_info.get("currency", "INR")
                
                # Get itinerary details
                itineraries = flight.get("itineraries", [])
                if itineraries:
                    segments = itineraries[0].get("segments", [])
                    if segments:
                        departure_segment = segments[0]
                        arrival_segment = segments[-1]
                        
                        dep_time = departure_segment.get("departure", {}).get("at", "N/A")
                        arr_time = arrival_segment.get("arrival", {}).get("at", "N/A")
                        
                        # Format times to be more readable
                        dep_time_formatted = format_time(dep_time)
                        arr_time_formatted = format_time(arr_time)
                        
                        # Calculate duration
                        duration = calculate_duration(dep_time, arr_time)
                        
                        results.append({
                            "airline": airline, 
                            "price": f"₹{total_price}", 
                            "departure_time": dep_time_formatted, 
                            "arrival_time": arr_time_formatted,
                            "duration": duration,
                            "flight_number": f"{airline} {departure_segment.get('number', '')}",
                            "origin": origin.upper(),
                            "destination": destination.upper(),
                            "date": formatted_date
                        })
            except Exception as flight_error:
                print(f"⚠️ Error processing flight: {flight_error}")
                continue
        
        if not results:
            return [{"error": "No valid flight data could be processed"}]
            
        return results
        
    except requests.exceptions.RequestException as e:
        return [{"error": f"Network error: {e}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {e}"}]

def format_time(iso_time: str) -> str:
    """Convert ISO time to readable format"""
    try:
        dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        return dt.strftime("%H:%M")
    except:
        return iso_time

def calculate_duration(departure: str, arrival: str) -> str:
    """Calculate flight duration"""
    try:
        dep_dt = datetime.fromisoformat(departure.replace('Z', '+00:00'))
        arr_dt = datetime.fromisoformat(arrival.replace('Z', '+00:00'))
        duration = arr_dt - dep_dt
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    except:
        return "N/A"

def get_flight_agent_response(query: str) -> str:
    """
    Takes a user query, processes it, and returns a formatted response.
    This is a simplified version without LangChain for the MVP.
    """
    import re
    
    # Extract origin, destination, and date from query
    def extract_origin(query):
        from_pattern = re.search(r'from\s+(\w+)', query, re.IGNORECASE)
        return from_pattern.group(1) if from_pattern else 'DEL'
    
    def extract_destination(query):
        to_pattern = re.search(r'to\s+(\w+)', query, re.IGNORECASE)
        return to_pattern.group(1) if to_pattern else 'BOM'
    
    def extract_date(query):
        query_lower = query.lower()
        if 'tomorrow' in query_lower:
            return 'tomorrow'
        elif 'today' in query_lower:
            return 'today'
        elif 'next monday' in query_lower:
            return 'next monday'
        elif 'next tuesday' in query_lower:
            return 'next tuesday'
        elif 'next wednesday' in query_lower:
            return 'next wednesday'
        elif 'next thursday' in query_lower:
            return 'next thursday'
        elif 'next friday' in query_lower:
            return 'next friday'
        elif 'next saturday' in query_lower:
            return 'next saturday'
        elif 'next sunday' in query_lower:
            return 'next sunday'
        elif 'next week' in query_lower:
            return 'next week'
        else:
            return 'tomorrow'  # Default
    
    try:
        origin = extract_origin(query)
        destination = extract_destination(query)
        date = extract_date(query)
        
        # Search for flights
        flights = flight_search(origin, destination, date)
        
        if flights and not flights[0].get('error'):
            response = "🛫 I found these flights for you:\n\n"
            for i, flight in enumerate(flights):
                response += f"{i + 1}. **{flight['airline']}** {flight['flight_number']} - {flight['price']}\n"
                response += f"   🛫 Departure: {flight['departure_time']} | 🛬 Arrival: {flight['arrival_time']} | ⏱️ Duration: {flight['duration']}\n\n"
            response += "💡 Tap on any flight card below to book or get more details!"
            return response
        else:
            error = flights[0].get('error', 'Unknown error') if flights else 'No flights found'
            return f"❌ Sorry, I couldn't find any flights for that route and date. Error: {error}"
            
    except Exception as e:
        return f"⚠️ An unexpected error occurred: {e}"

# --- Main Application Loop ---
if __name__ == "__main__":
    print("🛫 Universal Flight Agent - AMADEUS API 🛫")
    print("🌍 Search flights between ANY two airports worldwide")
    print("💡 Examples: 'NYC to London tomorrow', 'Bangkok to Singapore next Monday'")
    print(f"📅 Today's date: {datetime.now().strftime('%Y-%m-%d')}")
    print("🚨 IMPORTANT: The agent now correctly handles relative dates like 'next Thursday'")
    
    while True:
        query = input("\nYour request (or 'exit'): ")
        if query.lower() in ("exit", "quit"):
            print("Exiting.")
            break
        
        final_answer = get_flight_agent_response(query)
        print("\n✅ Final Answer:")
        print(final_answer)
        print("-" * 50)
