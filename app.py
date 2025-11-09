import os
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Load Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


@app.route("/", methods=["GET"])
def home():
    return "Gemini + Weather Webhook is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True, force=True)

    # Extract user message
    user_message = data.get("queryResult", {}).get("queryText", "")

    # WEATHER HANDLER
    if "weather" in user_message.lower() or "temperature" in user_message.lower():
        try:
            url = "https://api.open-meteo.com/v1/forecast?latitude=28.625&longitude=77.25&current_weather=true"
            weather_json = requests.get(url).json()

            current = weather_json.get("current_weather", {})
            temp = current.get("temperature")
            wind = current.get("windspeed")

            reply = f"The current temperature is {temp}°C with wind speed {wind} km/h."
            return jsonify({"fulfillmentText": reply})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Weather API error: {str(e)}"})


    # GEMINI GENERAL CHAT
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            response = model.generate_content(user_message)
            return jsonify({"fulfillmentText": response.text})

        except Exception as e:
            return jsonify({"fulfillmentText": f"Gemini error: {e}"})


    # FALLBACK
    return jsonify({"fulfillmentText": "I'm here to help!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


