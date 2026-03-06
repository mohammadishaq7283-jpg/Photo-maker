from flask import Flask, request, jsonify, render_template_string
import os
import requests
import json
import re
import io
import base64
import random
import urllib.parse # ✅ New Import for fixing links
from PIL import Image

app = Flask(__name__)

# --- KEYS ---
CHAT_API_KEY = os.getenv("OPENROUTER_API_KEY") 
HF_API_KEY = os.getenv("HUGGING_FACE_KEY") 

CHAT_MODEL = "stepfun/step-3.5-flash:free"
HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-dev"

try:
    from frontend_ui import HTML_CODE
except ImportError:
    HTML_CODE = "<h1>UI Missing</h1>"

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not CHAT_API_KEY:
        return jsonify({"reply": "⚠️ Chat Key Missing!"}), 500

    try:
        data = request.json
        messages = data.get('messages', [])
        locale = data.get('locale', 'English')
        
        system_msg = {
            "role": "system", 
            "content": f"You are PixelMystic. Lang: {locale}. If user wants image, output JSON: {{\"GENERATE_IMAGE\": \"detailed_english_prompt\"}}."
        }
        
        final_messages = [system_msg]
        for m in messages:
            content = m['content']
            if m.get('image'):
                content = [{"type": "text", "text": m['content'] or "Analyze"}, {"type": "image_url", "image_url": {"url": m['image']}}]
            final_messages.append({"role": m['role'], "content": content})

        # 1. Chat Call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {CHAT_API_KEY}"},
            json={"model": CHAT_MODEL, "messages": final_messages},
            timeout=30
        )
        
        reply = response.json()['choices'][0]['message']['content']
        generated_image = None

        # 2. Image Generation Logic
        if 'GENERATE_IMAGE' in reply:
            match = re.search(r'\{"GENERATE_IMAGE":\s*"(.*?)"\}', reply)
            if match:
                raw_prompt = match.group(1)
                
                # --- Attempt 1: Hugging Face (High Quality) ---
                if HF_API_KEY:
                    try:
                        hf_res = requests.post(
                            HF_MODEL_URL,
                            headers={"Authorization": f"Bearer {HF_API_KEY}"},
                            json={"inputs": raw_prompt},
                            timeout=50
                        )
                        
                        if hf_res.status_code == 200:
                            image_bytes = hf_res.content
                            try:
                                img = Image.open(io.BytesIO(image_bytes))
                                buffered = io.BytesIO()
                                img.save(buffered, format="JPEG") # Changed to JPEG for speed
                                img_str = base64.b64encode(buffered.getvalue()).decode()
                                generated_image = f"data:image/jpeg;base64,{img_str}"
                                reply = reply.replace(match.group(0), "🎨 Generated with Flux (HF):")
                            except:
                                pass # Fallback to free if bytes are bad
                    except Exception as e:
                        print(f"HF Failed: {e}")
                
                # --- Attempt 2: Pollinations (Free Mode - FIX APPLIED) ---
                if not generated_image:
                    seed = random.randint(1, 10000)
                    # ✅ FIX: Spaces ko %20 me badalna zaroori hai
                    encoded_prompt = urllib.parse.quote(raw_prompt)
                    
                    generated_image = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&width=1024&height=1024&nologo=true"
                    
                    reply = reply.replace(match.group(0), "🎨 Generated (Free Mode):")

        return jsonify({"reply": reply, "generatedImageUrl": generated_image})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
