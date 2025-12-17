from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import os

# SSL எச்சரிக்

app = Flask(__name__)
CORS(app)

# -----------------------------------------------------------
# உங்கள் API KEY-ஐ இங்கே போடவும்
# -----------------------------------------------------------
RAW_API_KEY = os.environ.get("API_KEY")
API_KEY = RAW_API_KEY.strip()

# --- SMART FUNCTION: தானாகவே நல்ல மாடலை கண்டுபிடிக்கும் ---
def get_best_model():
    print("🔍 மாடலை தேடுகிறேன் (Searching for available models)...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        # verify=False என்பது போனில் பாதுகாப்பாக இணைய உதவும்
        response = requests.get(url, verify=False)
        data = response.json()
        
        if "models" in data:
            for model in data["models"]:
                # 'generateContent' வசதி உள்ள மாடலை மட்டும் எடு
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    model_name = model["name"].replace("models/", "")
                    print(f"✅ Found Model: {model_name}")
                    return model_name
    except Exception as e:
        print(f"⚠️ Error finding model: {e}")
    
    # எதுவும் கிடைக்கவில்லை என்றால் இதை முயற்சி செய்
    return "gemini-1.5-flash"

# ஆப் ஸ்டார்ட் ஆகும்போது ஒருமுறை மாடலை கண்டுபிடித்துவிடும்
CURRENT_MODEL = get_best_model()

@app.route('/')
def home():
    if not os.path.exists('index.html'):
        return "Error: index.html file missing!"
    return send_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    # நாம் கண்டுபிடித்த மாடலை பயன்படுத்துவோம்
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CURRENT_MODEL}:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": user_message}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            bot_reply = result['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": bot_reply})
        else:
            # ஒருவேளை Error வந்தால் வேறு மாடலை முயற்சி செய்வோம் (Backup)
            print(f"❌ Error with {CURRENT_MODEL}: {response.text}")
            return jsonify({"reply": f"Google Error ({response.status_code}). Check Terminal."})

    except Exception as e:
        return jsonify({"reply": "Connection Error on Phone."})

if __name__ == '__main__':
    print(f"🚀 Server Started using model: {CURRENT_MODEL}")
    app.run(host='0.0.0.0', port=5000)
                                
