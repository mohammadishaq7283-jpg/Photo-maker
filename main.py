from flask import Flask, request, jsonify, render_template_string
import os
import requests
import json

# --- CONFIG ---
app = Flask(__name__)
API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- UI CODE IMPORT ---
# Hum UI ko alag file me rakhenge taake main file saaf rahe
from frontend_ui import HTML_CODE

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not API_KEY:
        return jsonify({"error": "API Key missing"}), 500

    try:
        data = request.json
        messages = data.get('messages', [])
        locale = data.get('locale', 'English')
        
        # System Prompt Setup
        system_prompt = f"You are PixelMystic AI. Language: {locale}. If user wants an image, output EXACTLY this JSON: {{\"GENERATE_IMAGE\": \"detailed prompt\"}}. Otherwise just chat."
        
        # Messages ko format karna (OpenAI Format)
        formatted_msgs = [{"role": "system", "content": system_prompt}]
        for m in messages:
            content = m['content']
            # Agar image hai to vision format use karein
            if m.get('image'):
                content = [
                    {"type": "text", "text": m['content'] or "Analyze this image"},
                    {"type": "image_url", "image_url": {"url": m['image']}}
                ]
            formatted_msgs.append({"role": m['role'], "content": content})

        # 1. Chat/Vision Call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "openai/gpt-4o",
                "messages": formatted_msgs
            }
        )
        
        result = response.json()
        reply = result['choices'][0]['message']['content']
        generated_image = None

        # 2. Check for Image Generation Request
        if '{"GENERATE_IMAGE":' in reply:
            try:
                # Extract JSON safely
                import re
                match = re.search(r'\{"GENERATE_IMAGE":\s*"(.*?)"\}', reply)
                if match:
                    prompt = match.group(1)
                    # Call Image API
                    img_res = requests.post(
                        "https://openrouter.ai/api/v1/images/generations",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        json={
                            "model": "openai/dall-e-3",
                            "prompt": prompt
                        }
                    )
                    img_data = img_res.json()
                    generated_image = img_data['data'][0]['url']
                    # Clean reply
                    reply = reply.replace(match.group(0), "Here is your image:")
            except Exception as e:
                print(f"Image Gen Error: {e}")

        return jsonify({"reply": reply, "generatedImageUrl": generated_image})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
