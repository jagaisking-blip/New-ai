from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

# SSL warnings hide (Pydroid-friendly

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------
# 🔑 API KEY — ENVIRONMENT VARIABLE
# -----------------------------------------------------------
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise RuntimeError("❌ API_KEY not set in environment variables")

# --- SMART FUNCTION: available model auto-pick ---
def get_best_model():
    print("🔍 Searching for available Gemini model...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        if "models" in data:
            for model in data["models"]:
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    model_name = model["name"].replace("models/", "")
                    print(f"✅ Using model: {model_name}")
                    return model_name
    except Exception as e:
        print(f"⚠️ Model search error: {e}")

    print("⚠️ Fallback model used")
    return "gemini-1.5-flash"

CURRENT_MODEL = get_best_model()

@app.route('/')
def home():
    if not os.path.exists('index.html'):
        return "Error: index.html missing"
    return send_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CURRENT_MODEL}:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": reply})

        else:
            print("❌ Gemini error:", response.text)
            return jsonify({"reply": "Google API error. Check server log."})

    except Exception as e:
        print("❌ Connection error:", e)
        return jsonify({"reply": "Server connection error"})

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
