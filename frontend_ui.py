HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PixelMystic Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Fabric.js for Image Editing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
    <style>
        :root { --primary: #00f3ff; --bg: #0a0a0a; --panel: #1a1a1a; --text: #fff; }
        body { background: var(--bg); color: var(--text); font-family: sans-serif; overflow: hidden; }
        
        .tool-btn { display: flex; flex-direction: column; align-items: center; justify-content: center; width: 70px; height: 70px; border-radius: 12px; background: #222; color: #aaa; transition: 0.2s; cursor: pointer; border: 1px solid #333; }
        .tool-btn:hover, .tool-btn.active { background: var(--primary); color: #000; border-color: var(--primary); }
        .tool-btn i { margin-bottom: 5px; }
        
        canvas { border: 2px dashed #333; border-radius: 8px; }
        
        .panel { background: var(--panel); border-left: 1px solid #333; padding: 15px; width: 300px; display: flex; flex-direction: column; gap: 15px; }
        
        .filter-btn { padding: 8px; border-radius: 6px; background: #333; color: white; cursor: pointer; text-align: center; font-size: 12px; }
        .filter-btn:hover { background: var(--primary); color: black; }
    </style>
</head>
<body class="flex h-screen">

    <!-- TOOLBAR (Left) -->
    <div class="w-20 bg-[#111] border-r border-[#333] flex flex-col items-center py-4 gap-3 overflow-y-auto">
        <div class="tool-btn active" onclick="setTool('ai')" title="AI Generator"><i data-lucide="sparkles"></i><span class="text-[10px]">AI Gen</span></div>
        <div class="tool-btn" onclick="setTool('filters')" title="Filters"><i data-lucide="palette"></i><span class="text-[10px]">Filters</span></div>
        <div class="tool-btn" onclick="setTool('text')" title="Add Text"><i data-lucide="type"></i><span class="text-[10px]">Text</span></div>
        <div class="tool-btn" onclick="setTool('stickers')" title="Stickers"><i data-lucide="smile"></i><span class="text-[10px]">Stickers</span></div>
        <div class="tool-btn" onclick="setTool('frames')" title="Frames"><i data-lucide="frame"></i><span class="text-[10px]">Frames</span></div>
        <div class="mt-auto tool-btn bg-green-600 text-white" onclick="downloadImage()"><i data-lucide="download"></i><span class="text-[10px]">Save</span></div>
    </div>

    <!-- CANVAS AREA (Center) -->
    <div class="flex-1 flex flex-col items-center justify-center bg-[#000] relative">
        <canvas id="canvas"></canvas>
        <div id="placeholder" class="absolute text-gray-500 text-center pointer-events-none">
            <i data-lucide="image" class="w-16 h-16 mx-auto mb-2 opacity-50"></i>
            <p>Generate AI Art or Upload Image</p>
        </div>
        
        <!-- Bottom Floating Bar -->
        <div class="absolute bottom-5 bg-[#222] p-3 rounded-full flex gap-4 shadow-xl border border-[#333]">
            <input type="file" id="upload" hidden onchange="handleUpload(this)">
            <button onclick="document.getElementById('upload').click()" class="flex items-center gap-2 px-4 py-2 bg-[#333] rounded-full hover:bg-white/10"><i data-lucide="upload" class="w-4"></i> Upload</button>
            <button onclick="shareWhatsapp()" class="flex items-center gap-2 px-4 py-2 bg-green-600 rounded-full hover:bg-green-500"><i data-lucide="share-2" class="w-4"></i> Share</button>
        </div>
    </div>

    <!-- SETTINGS PANEL (Right) -->
    <div class="panel" id="panel">
        <h3 class="font-bold text-lg border-b border-gray-700 pb-2" id="panel-title">AI Generator</h3>
        
        <!-- AI TOOLS -->
        <div id="tool-ai" class="space-y-4">
            <textarea id="ai-prompt" placeholder="Describe image (e.g. Cyberpunk cat)" class="w-full p-3 rounded bg-[#222] border border-[#444] text-white h-24 outline-none focus:border-[var(--primary)]"></textarea>
            <button onclick="generateAI()" class="w-full py-3 bg-[var(--primary)] text-black font-bold rounded hover:opacity-90 flex justify-center gap-2">
                <i data-lucide="zap"></i> Generate
            </button>
            <div id="loading" class="hidden text-center text-sm text-gray-400">Creating magic...</div>
        </div>

        <!-- FILTERS -->
        <div id="tool-filters" class="hidden grid grid-cols-2 gap-2">
            <div class="filter-btn" onclick="applyFilter('sepia')">Sepia</div>
            <div class="filter-btn" onclick="applyFilter('grayscale')">B & W</div>
            <div class="filter-btn" onclick="applyFilter('vintage')">Vintage</div>
            <div class="filter-btn" onclick="applyFilter('invert')">Invert</div>
            <div class="filter-btn" onclick="applyFilter('blur')">Blur</div>
            <div class="filter-btn bg-red-600" onclick="resetFilters()">Reset</div>
        </div>

        <!-- TEXT -->
        <div id="tool-text" class="hidden space-y-3">
            <input type="text" id="text-input" placeholder="Enter text..." class="w-full p-2 rounded bg-[#222] border border-[#444]">
            <div class="flex gap-2">
                <input type="color" id="text-color" class="h-10 w-10 p-0 border-0 rounded cursor-pointer" value="#ffffff">
                <button onclick="addText()" class="flex-1 bg-blue-600 rounded">Add Text</button>
            </div>
        </div>

        <!-- STICKERS -->
        <div id="tool-stickers" class="hidden grid grid-cols-4 gap-2 text-2xl">
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('🔥')">🔥</div>
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('❤️')">❤️</div>
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('😂')">😂</div>
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('👑')">👑</div>
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('🕶️')">🕶️</div>
            <div class="cursor-pointer hover:scale-110" onclick="addEmoji('🚀')">🚀</div>
        </div>
        
        <!-- HISTORY -->
        <div class="mt-auto pt-4 border-t border-gray-700">
            <h4 class="text-sm font-bold mb-2">History</h4>
            <div id="history-list" class="flex gap-2 overflow-x-auto pb-2">
                <!-- Thumbs -->
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        const canvas = new fabric.Canvas('canvas', { width: 500, height: 500, backgroundColor: '#111' });
        
        // Resize canvas on load
        function resizeCanvas() {
            const container = document.querySelector('.flex-1');
            canvas.setWidth(container.clientWidth * 0.8);
            canvas.setHeight(container.clientHeight * 0.8);
            canvas.renderAll();
        }
        window.addEventListener('resize', resizeCanvas);
        setTimeout(resizeCanvas, 100);

        function setTool(tool) {
            document.querySelectorAll('.tool-btn').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');
            
            document.getElementById('panel-title').innerText = tool.toUpperCase();
            ['ai', 'filters', 'text', 'stickers', 'frames'].forEach(id => {
                document.getElementById('tool-'+id)?.classList.add('hidden');
            });
            document.getElementById('tool-'+tool)?.classList.remove('hidden');
        }

        // --- AI GENERATION ---
        async function generateAI() {
            const prompt = document.getElementById('ai-prompt').value;
            if(!prompt) return alert("Enter a prompt!");
            
            document.getElementById('loading').classList.remove('hidden');
            
            // Using Pollinations AI (Free & Fast)
            const seed = Math.floor(Math.random() * 1000);
            const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(prompt)}?seed=${seed}&width=512&height=512&nologo=true`;
            
            fabric.Image.fromURL(url, (img) => {
                img.scaleToWidth(canvas.width);
                canvas.centerObject(img);
                canvas.setBackgroundImage(img, canvas.renderAll.bind(canvas));
                document.getElementById('placeholder').style.display = 'none';
                document.getElementById('loading').classList.add('hidden');
                addToHistory(url);
            }, { crossOrigin: 'anonymous' });
        }

        // --- UPLOAD ---
        function handleUpload(input) {
            const file = input.files[0];
            if(!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {
                fabric.Image.fromURL(e.target.result, (img) => {
                    img.scaleToWidth(canvas.width);
                    canvas.centerObject(img);
                    canvas.add(img);
                    canvas.setActiveObject(img);
                    document.getElementById('placeholder').style.display = 'none';
                });
            };
            reader.readAsDataURL(file);
        }

        // --- FILTERS ---
        function applyFilter(type) {
            const obj = canvas.getActiveObject();
            if(!obj || !obj.filters) return alert("Select an image first!");
            
            if(type === 'sepia') obj.filters.push(new fabric.Image.filters.Sepia());
            if(type === 'grayscale') obj.filters.push(new fabric.Image.filters.Grayscale());
            if(type === 'invert') obj.filters.push(new fabric.Image.filters.Invert());
            if(type === 'blur') obj.filters.push(new fabric.Image.filters.Blur({ blur: 0.5 }));
            if(type === 'vintage') obj.filters.push(new fabric.Image.filters.Vintage());
            
            obj.applyFilters();
            canvas.renderAll();
        }
        
        function resetFilters() {
            const obj = canvas.getActiveObject();
            if(obj) { obj.filters = []; obj.applyFilters(); canvas.renderAll(); }
        }

        // --- TEXT & STICKERS ---
        function addText() {
            const text = document.getElementById('text-input').value || "Hello";
            const color = document.getElementById('text-color').value;
            const t = new fabric.IText(text, { left: 100, top: 100, fill: color, fontSize: 40 });
            canvas.add(t);
        }

        function addEmoji(emoji) {
            const t = new fabric.IText(emoji, { left: 150, top: 150, fontSize: 60 });
            canvas.add(t);
        }

        // --- DOWNLOAD & SHARE ---
        function downloadImage() {
            const link = document.createElement('a');
            link.download = 'pixel-art.png';
            link.href = canvas.toDataURL({ format: 'png', quality: 1.0 });
            link.click();
        }

        function shareWhatsapp() {
            // Note: WhatsApp API only allows text sharing directly, image requires manual attach
            alert("Image downloaded! You can now share it on WhatsApp.");
            downloadImage();
            window.open(`https://wa.me/?text=Check out my AI art!`, '_blank');
        }

        // --- HISTORY ---
        function addToHistory(url) {
            const list = document.getElementById('history-list');
            const img = document.createElement('img');
            img.src = url;
            img.className = "w-12 h-12 rounded border border-gray-600 cursor-pointer hover:border-white";
            img.onclick = () => {
                fabric.Image.fromURL(url, (i) => {
                    canvas.setBackgroundImage(i, canvas.renderAll.bind(canvas));
                }, { crossOrigin: 'anonymous' });
            };
            list.prepend(img);
        }
    </script>
</body>
</html>
"""
