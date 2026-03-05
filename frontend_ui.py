HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PixelMystic AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        /* Themes */
        :root { --primary: #00f3ff; --bg: #050505; --card: #121212; --text: #fff; }
        [data-theme="light"] { --primary: #2563eb; --bg: #f3f4f6; --card: #ffffff; --text: #1f2937; }
        
        body { background: var(--bg); color: var(--text); transition: 0.3s; font-family: sans-serif; }
        .theme-card { background: var(--card); border: 1px solid rgba(128,128,128,0.1); }
        .theme-btn { background: var(--primary); color: black; font-weight: bold; }
        
        /* Loader */
        .loader { border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--primary); border-radius: 50%; width: 20px; height: 20px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="h-screen flex overflow-hidden">

    <!-- SIDEBAR -->
    <div id="sidebar" class="w-72 theme-card border-r h-full flex flex-col transition-all transform -translate-x-full md:translate-x-0 absolute md:relative z-20 shadow-xl">
        <div class="p-4 border-b border-gray-700/20 flex justify-between items-center">
            <h2 class="font-bold text-lg" style="color: var(--primary)">HISTORY</h2>
            <button onclick="toggleSidebar()" class="md:hidden"><i data-lucide="x"></i></button>
        </div>
        
        <div class="p-4 space-y-3">
            <label class="text-xs text-gray-500 font-bold uppercase">Language / Zaban</label>
            <select id="lang-select" class="w-full p-3 rounded-lg theme-card border border-gray-600 outline-none text-sm">
                <option value="English">English 🇺🇸</option>
                <option value="Urdu">Urdu (اردو) 🇵🇰</option>
                <option value="Roman Urdu">Roman Urdu (Kaisay ho) 🗣️</option>
                <option value="Hindi">Hindi (हिंदी) 🇮🇳</option>
                <option value="Arabic">Arabic (العربية) 🇸🇦</option>
                <option value="Spanish">Spanish (Español) 🇪🇸</option>
                <option value="French">French (Français) 🇫🇷</option>
                <option value="German">German (Deutsch) 🇩🇪</option>
                <option value="Chinese">Chinese (中文) 🇨🇳</option>
            </select>

            <button onclick="startNewChat()" class="w-full flex items-center gap-2 p-3 rounded-lg border border-dashed border-gray-500 hover:bg-white/5 transition text-sm font-medium">
                <i data-lucide="plus" class="w-4"></i> New Chat
            </button>
        </div>

        <div id="history-list" class="flex-1 overflow-y-auto p-2 space-y-1"></div>

        <div class="p-4 border-t border-gray-700/20">
            <button onclick="toggleTheme()" class="flex items-center gap-3 w-full p-2 rounded hover:bg-white/5 text-sm">
                <i data-lucide="moon" class="w-4"></i> Switch Theme
            </button>
        </div>
    </div>

    <!-- MAIN CHAT -->
    <div class="flex-1 flex flex-col h-full relative">
        <!-- Header -->
        <div class="h-16 theme-card border-b flex items-center px-4 justify-between z-10">
            <div class="flex items-center gap-3">
                <button onclick="toggleSidebar()" class="md:hidden"><i data-lucide="menu"></i></button>
                <h1 class="font-bold text-xl flex items-center gap-2" style="color: var(--primary)">
                    <i data-lucide="sparkles" class="w-5"></i> PixelMystic
                </h1>
            </div>
        </div>

        <!-- Messages -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-6">
            <!-- Welcome Message -->
            <div class="flex flex-col items-center justify-center h-full opacity-50 text-center space-y-4" id="welcome-msg">
                <i data-lucide="aperture" class="w-16 h-16"></i>
                <p>Upload a photo to analyze or ask to generate an image.</p>
            </div>
        </div>

        <!-- Input Area -->
        <div class="p-4 theme-card border-t">
            <div id="image-preview" class="hidden mb-2 relative w-fit">
                <img id="preview-img" class="h-16 rounded-lg border border-gray-500 shadow-md">
                <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-500 rounded-full w-5 h-5 text-white flex items-center justify-center text-xs shadow-sm">×</button>
            </div>
            
            <div class="flex gap-2 items-center">
                <input type="file" id="file-input" class="hidden" accept="image/*" onchange="handleImage(this)">
                
                <button onclick="document.getElementById('file-input').click()" class="p-3 rounded-xl hover:bg-white/10 theme-card border border-gray-600/50 transition">
                    <i data-lucide="image" class="w-5 text-gray-400"></i>
                </button>
                
                <input id="user-input" type="text" placeholder="Describe an image or ask anything..." class="flex-1 p-3 rounded-xl theme-card border border-gray-600/50 outline-none focus:border-blue-500 transition" onkeydown="if(event.key === 'Enter') sendMessage()">
                
                <button onclick="sendMessage()" id="send-btn" class="p-3 rounded-xl theme-btn hover:opacity-90 shadow-lg shadow-blue-500/20 transition">
                    <i data-lucide="send" class="w-5"></i>
                </button>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        let sessions = JSON.parse(localStorage.getItem('pm_sessions')) || [];
        let currentId = null;
        let currentImage = null;

        // Init
        if(sessions.length === 0) startNewChat();
        else { renderHistory(); loadSession(sessions[0].id); }
        
        // Theme Check
        if(localStorage.getItem('pm_theme') === 'light') document.documentElement.setAttribute('data-theme', 'light');

        function toggleTheme() {
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            document.documentElement.setAttribute('data-theme', isLight ? 'dark' : 'light');
            localStorage.setItem('pm_theme', isLight ? 'dark' : 'light');
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('-translate-x-full');
        }

        function startNewChat() {
            const id = Date.now().toString();
            sessions.unshift({ id, title: "New Chat", messages: [] });
            saveSessions();
            loadSession(id);
            if(window.innerWidth < 768) document.getElementById('sidebar').classList.add('-translate-x-full');
        }

        function loadSession(id) {
            currentId = id;
            renderHistory();
            const session = sessions.find(s => s.id === id);
            const container = document.getElementById('chat-container');
            container.innerHTML = '';
            
            if(session.messages.length > 0) document.getElementById('welcome-msg')?.remove();
            else container.innerHTML = `<div class="flex flex-col items-center justify-center h-full opacity-50 text-center space-y-4" id="welcome-msg"><i data-lucide="aperture" class="w-16 h-16"></i><p>Upload a photo or start chatting.</p></div>`;

            session.messages.forEach(msg => appendMessage(msg));
            lucide.createIcons();
        }

        function renderHistory() {
            const list = document.getElementById('history-list');
            list.innerHTML = sessions.map(s => `
                <div onclick="loadSession('${s.id}')" class="p-3 rounded-lg cursor-pointer truncate text-sm transition ${s.id === currentId ? 'bg-white/10 border-l-2 border-[var(--primary)]' : 'hover:bg-white/5'}">
                    ${s.messages[0]?.content || s.title}
                </div>
            `).join('');
        }

        function saveSessions() {
            localStorage.setItem('pm_sessions', JSON.stringify(sessions));
            renderHistory();
        }

        function handleImage(input) {
            const file = input.files[0];
            if(file) {
                const reader = new FileReader();
                reader.onload = e => {
                    currentImage = e.target.result;
                    document.getElementById('preview-img').src = currentImage;
                    document.getElementById('image-preview').classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        }

        function removeImage() {
            currentImage = null;
            document.getElementById('image-preview').classList.add('hidden');
            document.getElementById('file-input').value = '';
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const text = input.value.trim();
            if(!text && !currentImage) return;

            document.getElementById('welcome-msg')?.remove();

            const userMsg = { role: 'user', content: text, image: currentImage };
            appendMessage(userMsg);
            
            const session = sessions.find(s => s.id === currentId);
            session.messages.push(userMsg);
            saveSessions();

            input.value = '';
            removeImage();
            const loadingDiv = showLoading();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        messages: session.messages,
                        locale: document.getElementById('lang-select').value
                    })
                });
                
                const data = await res.json();
                loadingDiv.remove();

                const aiMsg = { 
                    role: 'assistant', 
                    content: data.reply, 
                    generatedImage: data.generatedImageUrl 
                };
                
                appendMessage(aiMsg);
                session.messages.push(aiMsg);
                saveSessions();

            } catch(e) {
                loadingDiv.innerHTML = "⚠️ Error: " + e.message;
            }
        }

        function showLoading() {
            const div = document.createElement('div');
            div.className = "flex gap-2 items-center text-gray-500 ml-2";
            div.innerHTML = `<div class="loader"></div> <span class="text-sm">Magic in progress...</span>`;
            document.getElementById('chat-container').appendChild(div);
            return div;
        }

        function appendMessage(msg) {
            const div = document.createElement('div');
            div.className = `flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`;
            
            let contentHtml = '';
            if(msg.image) contentHtml += `<img src="${msg.image}" class="w-64 rounded-xl border border-gray-700 mb-2 shadow-lg">`;
            if(msg.content) contentHtml += `<div class="p-3.5 rounded-2xl max-w-lg leading-relaxed shadow-sm whitespace-pre-wrap ${msg.role === 'user' ? 'theme-btn rounded-br-none' : 'theme-card rounded-bl-none text-sm'}">${msg.content}</div>`;
            if(msg.generatedImage) contentHtml += `<div class="mt-3 group relative"><img src="${msg.generatedImage}" class="w-72 rounded-xl shadow-xl border border-[var(--primary)]"><a href="${msg.generatedImage}" download class="absolute bottom-3 right-3 bg-black/80 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition"><i data-lucide="download" class="w-4 h-4"></i></a></div>`;

            div.innerHTML = `<div class="flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}">${contentHtml}</div>`;
            
            const container = document.getElementById('chat-container');
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
            lucide.createIcons();
        }
    </script>
</body>
</html>
"""
