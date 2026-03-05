HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelMystic Ultimate</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
    <style>
        :root { --primary: #00f3ff; --bg: #050505; --card: #121212; --text: #fff; }
        body { background: var(--bg); color: var(--text); font-family: sans-serif; height: 100vh; display: flex; overflow: hidden; }
        
        .nav-item { padding: 12px; cursor: pointer; color: #888; display: flex; flex-direction: column; align-items: center; gap: 5px; font-size: 10px; }
        .nav-item.active { color: var(--primary); border-left: 3px solid var(--primary); background: rgba(255,255,255,0.05); }
        .nav-item:hover { color: #fff; }
        
        /* EDITOR Styles */
        .tool-btn { background: #222; border: 1px solid #333; padding: 10px; border-radius: 8px; cursor: pointer; text-align: center; }
        .tool-btn:hover { background: var(--primary); color: black; }
        canvas { border: 2px dashed #333; }
        
        /* CHAT Styles */
        .chat-bubble { padding: 12px; border-radius: 12px; max-width: 80%; margin-bottom: 10px; }
        .user-msg { background: var(--primary); color: black; align-self: flex-end; margin-left: auto; }
        .ai-msg { background: #222; color: #ddd; align-self: flex-start; border: 1px solid #333; }
    </style>
</head>
<body>

    <!-- 1. SIDEBAR NAVIGATION -->
    <div class="w-20 bg-[#111] border-r border-[#222] flex flex-col pt-4">
        <div class="nav-item active" onclick="switchTab('chat')" id="nav-chat">
            <i data-lucide="message-square"></i> CHAT
        </div>
        <div class="nav-item" onclick="switchTab('editor')" id="nav-editor">
            <i data-lucide="palette"></i> EDITOR
        </div>
        <div class="mt-auto nav-item" onclick="location.reload()">
            <i data-lucide="refresh-cw"></i> RESET
        </div>
    </div>

    <!-- 2. MAIN CONTENT AREA -->
    <div class="flex-1 relative">
        
        <!-- === TAB 1: CHAT & VISION (Old Logic) === -->
        <div id="tab-chat" class="h-full flex flex-col">
            <div class="h-16 border-b border-[#222] flex items-center px-6 font-bold text-xl text-[var(--primary)]">
                <i data-lucide="sparkles" class="mr-2"></i> PixelMystic Chat
            </div>
            
            <div id="chat-box" class="flex-1 overflow-y-auto p-4 flex flex-col">
                <div class="ai-msg chat-bubble">Hello! Upload a photo to analyze or ask me to generate an image.</div>
            </div>
            
            <div class="p-4 border-t border-[#222] bg-[#0a0a0a]">
                <div id="img-preview" class="hidden mb-2"><img id="preview-src" class="h-16 rounded border border-[var(--primary)]"></div>
                <div class="flex gap-2">
                    <input type="file" id="chat-upload" hidden onchange="handleChatUpload(this)">
                    <button onclick="document.getElementById('chat-upload').click()" class="p-3 bg-[#222] rounded-lg text-gray-400 hover:text-white"><i data-lucide="image"></i></button>
                    <input id="chat-input" class="flex-1 bg-[#111] border border-[#333] rounded-lg p-3 outline-none focus:border-[var(--primary)]" placeholder="Type here..." onkeydown="if(event.key==='Enter') sendChat()">
                    <button onclick="sendChat()" class="p-3 bg-[var(--primary)] rounded-lg text-black font-bold"><i data-lucide="send"></i></button>
                </div>
            </div>
        </div>

        <!-- === TAB 2: PHOTO EDITOR (New Logic) === -->
        <div id="tab-editor" class="h-full hidden flex-col md:flex-row">
            <!-- Canvas -->
            <div class="flex-1 bg-[#000] flex items-center justify-center relative p-4">
                <canvas id="editor-canvas"></canvas>
                <div id="editor-placeholder" class="absolute text-gray-600 pointer-events-none text-center">
                    <i data-lucide="image-plus" class="w-16 h-16 mx-auto mb-2"></i>
                    <p>Upload Image or Generate AI Art</p>
                </div>
            </div>
            
            <!-- Tools Panel -->
            <div class="w-full md:w-80 bg-[#111] border-l border-[#222] p-4 flex flex-col gap-4 overflow-y-auto">
                <h3 class="font-bold text-[var(--primary)]">TOOLS</h3>
                
                <div class="grid grid-cols-2 gap-2">
                    <input type="file" id="editor-upload" hidden onchange="handleEditorUpload(this)">
                    <div class="tool-btn" onclick="document.getElementById('editor-upload').click()"><i data-lucide="upload"></i> Upload</div>
                    <div class="tool-btn" onclick="downloadArt()"><i data-lucide="download"></i> Save</div>
                </div>

                <div class="border-t border-[#333] my-2"></div>
                
                <h4 class="text-sm font-bold text-gray-400">AI GENERATOR</h4>
                <textarea id="ai-prompt" class="w-full bg-[#222] p-2 rounded border border-[#333] text-sm" placeholder="e.g. Cyberpunk city"></textarea>
                <button onclick="generateArt()" class="w-full bg-[var(--primary)] text-black font-bold py-2 rounded">Generate</button>

                <div class="border-t border-[#333] my-2"></div>

                <h4 class="text-sm font-bold text-gray-400">FILTERS</h4>
                <div class="grid grid-cols-3 gap-2 text-xs">
                    <div class="tool-btn" onclick="applyFilter('sepia')">Sepia</div>
                    <div class="tool-btn" onclick="applyFilter('grayscale')">B&W</div>
                    <div class="tool-btn" onclick="applyFilter('vintage')">Vintage</div>
                </div>

                <h4 class="text-sm font-bold text-gray-400 mt-2">ADD</h4>
                <div class="flex gap-2">
                    <button onclick="addText()" class="flex-1 bg-blue-600 py-2 rounded text-xs">Text</button>
                    <button onclick="addSticker('🔥')" class="flex-1 bg-red-600 py-2 rounded text-xs">🔥</button>
                </div>
            </div>
        </div>

    </div>

    <script>
        lucide.createIcons();
        let currentTab = 'chat';
        let chatImage = null;
        const canvas = new fabric.Canvas('editor-canvas', { width: 500, height: 500 });

        // --- TABS ---
        function switchTab(tab) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.getElementById('nav-'+tab).classList.add('active');
            
            document.getElementById('tab-chat').classList.add('hidden');
            document.getElementById('tab-editor').classList.add('hidden');
            document.getElementById('tab-'+tab).classList.remove('hidden');
            
            if(tab === 'editor') {
                document.getElementById('tab-editor').style.display = 'flex'; // Fix flex issue
                resizeCanvas();
            }
        }

        // --- CHAT LOGIC ---
        function handleChatUpload(input) {
            const file = input.files[0];
            if(file) {
                const reader = new FileReader();
                reader.onload = e => {
                    chatImage = e.target.result;
                    document.getElementById('preview-src').src = chatImage;
                    document.getElementById('img-preview').classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        async function sendChat() {
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if(!text && !chatImage) return;

            // UI Update
            const chatBox = document.getElementById('chat-box');
            let userHtml = `<div class="user-msg chat-bubble">${text}`;
            if(chatImage) userHtml += `<br><img src="${chatImage}" class="mt-2 w-32 rounded">`;
            userHtml += `</div>`;
            chatBox.innerHTML += userHtml;

            const tempImage = chatImage;
            input.value = ''; chatImage = null;
            document.getElementById('img-preview').classList.add('hidden');
            chatBox.scrollTop = chatBox.scrollHeight;

            // API Call
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: [{ role: 'user', content: text, image: tempImage }],
                        locale: 'English'
                    })
                });
                const data = await res.json();
                
                let aiHtml = `<div class="ai-msg chat-bubble">${data.reply}`;
                if(data.generatedImageUrl) aiHtml += `<br><img src="${data.generatedImageUrl}" class="mt-2 w-64 rounded">`;
                aiHtml += `</div>`;
                chatBox.innerHTML += aiHtml;
                chatBox.scrollTop = chatBox.scrollHeight;

            } catch(e) {
                chatBox.innerHTML += `<div class="ai-msg chat-bubble text-red-400">Error: ${e.message}</div>`;
            }
        }

        // --- EDITOR LOGIC ---
        function resizeCanvas() {
            const container = document.querySelector('#tab-editor > div'); // Canvas container
            if(container) {
                canvas.setWidth(container.clientWidth * 0.9);
                canvas.setHeight(container.clientHeight * 0.9);
                canvas.renderAll();
            }
        }
        window.addEventListener('resize', resizeCanvas);

        function handleEditorUpload(input) {
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                fabric.Image.fromURL(e.target.result, (img) => {
                    img.scaleToWidth(canvas.width);
                    canvas.centerObject(img);
                    canvas.add(img);
                    canvas.setActiveObject(img);
                    document.getElementById('editor-placeholder').style.display = 'none';
                });
            };
            reader.readAsDataURL(file);
        }

        function generateArt() {
            const prompt = document.getElementById('ai-prompt').value;
            if(!prompt) return alert("Enter prompt");
            
            const seed = Math.floor(Math.random() * 1000);
            const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?seed=${seed}&width=512&height=512&nologo=true`;
            
            fabric.Image.fromURL(url, (img) => {
                img.scaleToWidth(canvas.width);
                canvas.centerObject(img);
                canvas.add(img);
                document.getElementById('editor-placeholder').style.display = 'none';
            }, { crossOrigin: 'anonymous' });
        }

        function applyFilter(type) {
            const obj = canvas.getActiveObject();
            if(!obj || !obj.filters) return alert("Select an image first!");
            
            if(type === 'sepia') obj.filters.push(new fabric.Image.filters.Sepia());
            if(type === 'grayscale') obj.filters.push(new fabric.Image.filters.Grayscale());
            if(type === 'vintage') obj.filters.push(new fabric.Image.filters.Vintage());
            
            obj.applyFilters();
            canvas.renderAll();
        }

        function addText() {
            const t = new fabric.IText('Hello', { left: 100, top: 100, fill: 'white', fontSize: 40 });
            canvas.add(t);
        }

        function addSticker(emoji) {
            const t = new fabric.IText(emoji, { left: 150, top: 150, fontSize: 60 });
            canvas.add(t);
        }

        function downloadArt() {
            const link = document.createElement('a');
            link.download = 'pixel-art.png';
            link.href = canvas.toDataURL({ format: 'png', quality: 1.0 });
            link.click();
        }
    </script>
</body>
</html>
"""
