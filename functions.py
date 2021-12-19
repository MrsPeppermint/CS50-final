import os
from flask import redirect, session
import requests
from functools import wraps

# login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/guest")
        return f(*args, **kwargs)
    return decorated_function

# collect weather info
def weather_info(location):
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        response = requests.get(url)
        # check for error codes
        response.raise_for_status()
    # if url doesn't go through
    except requests.RequestException:
        return None
    

    try:
        weather = response.json()
        
        # categorize weather codes
        code = weather["weather"][0]["id"]
        # precipitation
        if code > 200 and code < 700:
            weath_cat = 1
            # dense clouds + athmosphere
        elif code == 803 or code == 804 or (code > 700 and code < 800):
            weath_cat = 2
        # sparse clouds
        elif code == 801 or code == 802:
            weath_cat = 4
        # clear
        elif code == 800:
            weath_cat = 5
        else:
            weath_cat = 3
        
        #categorize temperatures (in kelvins)
        temperature = weather["main"]["temp"]
        if temperature <= 280:
            temp_cat = 1
        elif temperature <= 295 and temperature > 280:
            temp_cat = 2
        elif temperature <= 305 and temperature > 195:
            temp_cat = 4
        elif temperature > 305:
            temp_cat = 5
        else:
            temp_cat = 3

        
        # return weather info (temperature, weather description, code for comparing)
        return {
            "id": weath_cat,
            "temp": weather["main"]["temp"],
            "temp_cat": temp_cat,
            "description": weather["weather"][0]["description"],
            "icon": weather["weather"][0]["icon"],
            "city": weather["name"]
        }
        # if there is error in json file
    except(KeyError, ValueError, TypeError):
        return None 

def celsius(kelvin):
    return(f"{(kelvin-273.15):.1f}")

def fahr(kelvin):
    result = (kelvin-273.15) * (9/5) + 32 
    return(f"{result:.1f}")