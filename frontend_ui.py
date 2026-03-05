HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixelMystic AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        /* Themes */
        :root { --primary: #00f3ff; --bg: #050505; --card: #121212; --text: #fff; }
        [data-theme="light"] { --primary: #2563eb; --bg: #f3f4f6; --card: #ffffff; --text: #1f2937; }
        
        body { background: var(--bg); color: var(--text); transition: 0.3s; }
        .theme-card { background: var(--card); border: 1px solid rgba(128,128,128,0.1); }
        .theme-btn { background: var(--primary); color: white; }
        
        /* Loader */
        .loader { border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--primary); border-radius: 50%; width: 24px; height: 24px; animation: spin 1s linear infinite; }
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
            <select id="lang-select" class="w-full p-2 rounded theme-card border border-gray-600 outline-none">
                <option value="English">English</option>
                <option value="Urdu">Urdu</option>
            </select>
            <button onclick="startNewChat()" class="w-full flex items-center gap-2 p-3 rounded-lg border border-dashed border-gray-500 hover:bg-white/5 transition">
                <i data-lucide="plus" class="w-4"></i> New Chat
            </button>
        </div>

        <div id="history-list" class="flex-1 overflow-y-auto p-2 space-y-1"></div>

        <div class="p-4 border-t border-gray-700/20">
            <button onclick="toggleTheme()" class="flex items-center gap-3 w-full p-2 rounded hover:bg-white/5">
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
                <h1 class="font-bold text-xl" style="color: var(--primary)">PixelMystic</h1>
            </div>
        </div>

        <!-- Messages -->
        <div id="chat-container" class="flex-1 overflow-y-auto p-4 space-y-4"></div>

        <!-- Input Area -->
        <div class="p-4 theme-card border-t">
            <div id="image-preview" class="hidden mb-2 relative w-fit">
                <img id="preview-img" class="h-16 rounded border border-gray-500">
                <button onclick="removeImage()" class="absolute -top-2 -right-2 bg-red-500 rounded-full w-5 h-5 text-white flex items-center justify-center text-xs">×</button>
            </div>
            
            <div class="flex gap-2 items-center">
                <input type="file" id="file-input" class="hidden" accept="image/*" onchange="handleImage(this)">
                <button onclick="document.getElementById('file-input').click()" class="p-3 rounded-lg hover:bg-white/10 theme-card border"><i data-lucide="image"></i></button>
                
                <input id="user-input" type="text" placeholder="Type a message..." class="flex-1 p-3 rounded-lg theme-card border border-gray-600 outline-none focus:border-blue-500" onkeydown="if(event.key === 'Enter') sendMessage()">
                
                <button onclick="sendMessage()" id="send-btn" class="p-3 rounded-lg theme-btn hover:opacity-90"><i data-lucide="send"></i></button>
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
        
        // Theme
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
            if(window.innerWidth < 768) toggleSidebar();
        }

        function loadSession(id) {
            currentId = id;
            renderHistory();
            const session = sessions.find(s => s.id === id);
            const container = document.getElementById('chat-container');
            container.innerHTML = '';
            session.messages.forEach(msg => appendMessage(msg));
        }

        function renderHistory() {
            const list = document.getElementById('history-list');
            list.innerHTML = sessions.map(s => `
                <div onclick="loadSession('${s.id}')" class="p-3 rounded cursor-pointer truncate text-sm ${s.id === currentId ? 'bg-white/10' : 'hover:bg-white/5'}">
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

            const userMsg = { role: 'user', content: text, image: currentImage };
            appendMessage(userMsg);
            
            // Save to state
            const session = sessions.find(s => s.id === currentId);
            session.messages.push(userMsg);
            saveSessions();

            // Clear UI
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
                loadingDiv.innerHTML = "Error: " + e.message;
            }
        }

        function showLoading() {
            const div = document.createElement('div');
            div.className = "flex gap-2 items-center text-gray-500";
            div.innerHTML = `<div class="loader"></div> Thinking...`;
            document.getElementById('chat-container').appendChild(div);
            return div;
        }

        function appendMessage(msg) {
            const div = document.createElement('div');
            div.className = `flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`;
            
            let contentHtml = '';
            if(msg.image) contentHtml += `<img src="${msg.image}" class="w-48 rounded-lg border mb-2">`;
            if(msg.content) contentHtml += `<div class="p-3 rounded-xl max-w-md whitespace-pre-wrap ${msg.role === 'user' ? 'theme-btn' : 'theme-card'}">${msg.content}</div>`;
            if(msg.generatedImage) contentHtml += `<div class="mt-2"><img src="${msg.generatedImage}" class="w-64 rounded-lg shadow-lg"><a href="${msg.generatedImage}" download class="text-xs text-blue-400 underline block mt-1">Download</a></div>`;

            div.innerHTML = `<div class="flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}">${contentHtml}</div>`;
            
            const container = document.getElementById('chat-container');
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""
