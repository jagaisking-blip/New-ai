from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ✅ API key ONLY from environment
API_KEY = os.environ.get("API_KEY")

# ✅ Stable model (no beta nonsense)
MODEL = "gemini-1.5-flash"

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    url = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        return jsonify({"reply": "⚠️ Gemini API error. Try again in few seconds."})

    data = response.json()
    reply = data["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
