from flask import Flask, request, jsonify, render_template_string
import os
import requests
import json
import random

app = Flask(__name__)

# --- CONFIG ---
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("API_KEY")
CHAT_MODEL = "stepfun/step-3.5-flash:free"

try:
    from frontend_ui import HTML_CODE
except ImportError:
    HTML_CODE = "<h1>UI Missing</h1>"

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not API_KEY:
        return jsonify({"reply": "⚠️ Error: API Key missing!"}), 500

    try:
        data = request.json
        messages = data.get('messages', [])
        default_locale = data.get('locale', 'English')
        
        # --- SMART SYSTEM PROMPT ---
        system_msg = {
            "role": "system", 
            "content": f"""
            You are PixelMystic AI. 
            
            === LANGUAGE RULES ===
            1. Default Language: {default_locale}.
            2. OVERRIDE RULE: If the user explicitly asks to speak in another language (e.g., "Speak in Urdu", "English me batao"), or types in a different language, you MUST switch to that language immediately. Mirror the user's language.
            
            === IMAGE RULES ===
            1. If user asks to generate/create/make an image, output STRICTLY this JSON: {{"GENERATE_IMAGE": "english_prompt"}}.
            2. Do not explain the image generation, just output JSON.
            """
        }
        
        final_messages = [system_msg]
        for m in messages:
            content = m['content']
            if m.get('image'):
                content = [{"type": "text", "text": m['content'] or "Analyze image"}, {"type": "image_url", "image_url": {"url": m['image']}}]
            final_messages.append({"role": m['role'], "content": content})

        # 1. Chat AI Call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": CHAT_MODEL, "messages": final_messages}
        )
        
        if response.status_code != 200:
            return jsonify({"reply": f"⚠️ API Error: {response.text}"})

        reply = response.json()['choices'][0]['message']['content']
        generated_image = None

        # 2. Image Generation Logic (Pollinations AI)
        if 'GENERATE_IMAGE' in reply:
            import re
            match = re.search(r'\{"GENERATE_IMAGE":\s*"(.*?)"\}', reply)
            if match:
                prompt = match.group(1)
                seed = random.randint(1, 99999)
                generated_image = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true&width=1024&height=1024"
                reply = reply.replace(match.group(0), "🎨 Here is your AI Art:")

        return jsonify({"reply": reply, "generatedImageUrl": generated_image})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
