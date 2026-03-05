from flask import Flask, request, jsonify, render_template_string
import os
import requests
import json

app = Flask(__name__)

# --- CONFIG ---
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("API_KEY")

# ✅ WAHI MODEL JO RECIPE APP ME CHALA THA
# Yeh bohot fast hai, isliye "Thinking..." par nahi atkega.
CHAT_MODEL = "stepfun/step-3.5-flash:free"

# UI Import
try:
    from frontend_ui import HTML_CODE
except ImportError:
    HTML_CODE = "<h1>Frontend File Missing</h1>"

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    if not API_KEY:
        return jsonify({"reply": "⚠️ Error: API Key missing in Vercel."}), 500

    try:
        data = request.json
        messages = data.get('messages', [])
        locale = data.get('locale', 'English')
        
        # System Prompt
        system_msg = {
            "role": "system", 
            "content": f"You are PixelMystic AI. Language: {locale}. If the user sends an image, analyze it. If the user asks to GENERATE or CREATE an image, output strictly JSON: {{\"GENERATE_IMAGE\": \"english_prompt_here\"}}."
        }
        
        # Messages Formatting
        final_messages = [system_msg]
        
        for m in messages:
            content_payload = m['content']
            # Image Handling
            if m.get('image'):
                content_payload = [
                    {"type": "text", "text": m['content'] or "Describe this image detailed for a prompt"},
                    {"type": "image_url", "image_url": {"url": m['image']}}
                ]
            final_messages.append({"role": m['role'], "content": content_payload})

        # 1. AI Call (StepFun)
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://pixelmystic.app", 
            },
            json={
                "model": CHAT_MODEL,
                "messages": final_messages,
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30 # 30 Second Timeout
        )
        
        if response.status_code != 200:
            return jsonify({"reply": f"⚠️ Model Error: {response.text}"})

        result = response.json()
        
        if not result.get('choices'):
            return jsonify({"reply": "⚠️ AI sent empty response. Try again."})
            
        reply = result['choices'][0]['message']['content']
        generated_image = None

        # 2. Image Generation Logic (Agar user ne maanga ho)
        if 'GENERATE_IMAGE' in reply:
            try:
                import re
                match = re.search(r'\{"GENERATE_IMAGE":\s*"(.*?)"\}', reply)
                if match:
                    prompt = match.group(1)
                    
                    # DALL-E 3 Call for Generation
                    img_res = requests.post(
                        "https://openrouter.ai/api/v1/images/generations",
                        headers={"Authorization": f"Bearer {API_KEY}"},
                        json={
                            "model": "openai/dall-e-3", 
                            "prompt": prompt
                        },
                        timeout=45
                    )
                    img_data = img_res.json()
                    
                    if 'data' in img_data:
                        generated_image = img_data['data'][0]['url']
                        reply = reply.replace(match.group(0), "🎨 Here is your AI Art:")
                    else:
                        reply = "⚠️ Failed to generate image. Please try a simpler prompt."
            except Exception as img_err:
                print(f"Gen Error: {img_err}")

        return jsonify({"reply": reply, "generatedImageUrl": generated_image})

    except Exception as e:
        return jsonify({"reply": f"⚠️ Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
