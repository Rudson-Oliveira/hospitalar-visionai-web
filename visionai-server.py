#!/usr/bin/env python3
"""
VisionAI Server Permanente - Hospitalar Saúde
Roda localmente e se conecta aos serviços existentes
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests

# Configurações - Usar variável de ambiente
PORT = 3020
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Serviços locais
SERVICES = {
    'bridge': 'http://localhost:5000',
    'obsidian': 'http://localhost:5001', 
    'hub': 'http://localhost:5002',
    'vision': 'http://localhost:5003'
}

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionAI - Hospitalar Saúde</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0a; color: #fff; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #1a1a2e; padding: 8px 16px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid #333; }
        .logo { font-weight: bold; color: #4a9eff; font-size: 18px; }
        .nav-bar { flex: 1; display: flex; align-items: center; gap: 8px; }
        .nav-input { flex: 1; background: #2a2a3e; border: 1px solid #444; border-radius: 20px; padding: 8px 16px; color: #fff; font-size: 14px; }
        .env-btn { padding: 6px 16px; border-radius: 4px; border: none; cursor: pointer; font-weight: 600; font-size: 12px; }
        .env-btn.dev { background: #ff6b35; color: #fff; }
        .env-btn.prod { background: #4a9eff; color: #fff; }
        .env-btn.active { box-shadow: 0 0 10px currentColor; }
        .main { display: flex; flex: 1; overflow: hidden; }
        .browser-frame { flex: 1; background: #fff; }
        .browser-frame iframe { width: 100%; height: 100%; border: none; }
        .chat-panel { width: 350px; background: #1a1a2e; display: flex; flex-direction: column; border-left: 1px solid #333; }
        .chat-header { padding: 16px; border-bottom: 1px solid #333; }
        .chat-header h3 { color: #4a9eff; margin-bottom: 4px; }
        .chat-header p { color: #888; font-size: 12px; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 16px; }
        .message { margin-bottom: 16px; padding: 12px; border-radius: 8px; }
        .message.assistant { background: #2a2a3e; }
        .message.user { background: #4a9eff22; border: 1px solid #4a9eff44; }
        .chat-input-area { padding: 16px; border-top: 1px solid #333; }
        .chat-input { width: 100%; background: #2a2a3e; border: 1px solid #444; border-radius: 8px; padding: 12px; color: #fff; resize: none; }
        .send-btn { width: 100%; margin-top: 8px; background: #4a9eff; color: #fff; border: none; padding: 10px; border-radius: 8px; cursor: pointer; font-weight: 600; }
        .send-btn:hover { background: #3a8eef; }
        .status { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
        .status-item { font-size: 10px; padding: 2px 8px; border-radius: 10px; }
        .status-item.online { background: #22c55e22; color: #22c55e; }
        .status-item.offline { background: #ef444422; color: #ef4444; }
    </style>
</head>
<body>
    <div class="header">
        <span class="logo">Vision AI</span>
        <button class="env-btn" onclick="showChannels()">Canais</button>
        <div class="nav-bar">
            <input type="text" class="nav-input" id="urlInput" placeholder="Digite a URL..." value="https://dev.hospitalarsaude.app.br/#/dashboard/home">
            <button onclick="navigate()" style="background:#4a9eff;color:#fff;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;">Ir</button>
        </div>
        <button class="env-btn dev active" id="devBtn" onclick="setEnv('dev')">DEV</button>
        <button class="env-btn prod" id="prodBtn" onclick="setEnv('prod')">PROD</button>
    </div>
    <div class="main">
        <div class="browser-frame">
            <iframe id="mainFrame" src="https://dev.hospitalarsaude.app.br/#/dashboard/home"></iframe>
        </div>
        <div class="chat-panel">
            <div class="chat-header">
                <h3>Assistente Hospitalar</h3>
                <p>Especializado no sistema</p>
                <div class="status" id="statusArea">
                    <span class="status-item online">Bridge</span>
                    <span class="status-item online">Vision</span>
                    <span class="status-item online">Hub</span>
                </div>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <p>Olá! Como posso ajudar?</p>
                    <p style="margin-top:8px;font-size:12px;color:#888;">Pergunte sobre o sistema Hospitalar Saúde</p>
                </div>
            </div>
            <div class="chat-input-area">
                <textarea class="chat-input" id="chatInput" rows="3" placeholder="Pergunte sobre o sistema..."></textarea>
                <button class="send-btn" onclick="sendMessage()">Enviar</button>
            </div>
        </div>
    </div>
    <script>
        let currentEnv = 'dev';
        
        function setEnv(env) {
            currentEnv = env;
            document.getElementById('devBtn').classList.toggle('active', env === 'dev');
            document.getElementById('prodBtn').classList.toggle('active', env === 'prod');
            const base = env === 'dev' ? 'https://dev.hospitalarsaude.app.br' : 'https://hospitalarsaude.app.br';
            document.getElementById('urlInput').value = base + '/#/dashboard/home';
            document.getElementById('mainFrame').src = base + '/#/dashboard/home';
        }
        
        function navigate() {
            const url = document.getElementById('urlInput').value;
            document.getElementById('mainFrame').src = url;
        }
        
        function showChannels() {
            alert('Canais: Email, WhatsApp, Sistema');
        }
        
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const msg = input.value.trim();
            if (!msg) return;
            
            const messagesDiv = document.getElementById('chatMessages');
            messagesDiv.innerHTML += '<div class="message user"><p>' + msg + '</p></div>';
            input.value = '';
            
            messagesDiv.innerHTML += '<div class="message assistant" id="typing"><p>Digitando...</p></div>';
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, env: currentEnv })
                });
                const data = await response.json();
                document.getElementById('typing').remove();
                messagesDiv.innerHTML += '<div class="message assistant"><p>' + (data.response || data.error) + '</p></div>';
            } catch (e) {
                document.getElementById('typing').remove();
                messagesDiv.innerHTML += '<div class="message assistant"><p>Erro: ' + e.message + '</p></div>';
            }
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    </script>
</body>
</html>'''

class VisionAIHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            status = {'server': 'online', 'services': {}}
            for name, url in SERVICES.items():
                try:
                    r = requests.get(f'{url}/status', timeout=2)
                    status['services'][name] = 'online'
                except:
                    status['services'][name] = 'offline'
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            message = data.get('message', '')
            env = data.get('env', 'dev')
            
            if not OPENAI_API_KEY:
                answer = 'Erro: OPENAI_API_KEY não configurada. Execute: set OPENAI_API_KEY=sua_chave'
            else:
                try:
                    response = requests.post(
                        'https://api.openai.com/v1/chat/completions',
                        headers={
                            'Authorization': f'Bearer {OPENAI_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            'model': 'gpt-4o-mini',
                            'messages': [
                                {'role': 'system', 'content': f'Você é um assistente especializado no sistema Hospitalar Saúde ({env}). Ajude com orçamentos, pacientes, relatórios e navegação no sistema.'},
                                {'role': 'user', 'content': message}
                            ],
                            'max_tokens': 1000
                        },
                        timeout=30
                    )
                    result = response.json()
                    answer = result['choices'][0]['message']['content']
                except Exception as e:
                    answer = f'Erro ao processar: {str(e)}'
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'response': answer}).encode())
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', PORT), VisionAIHandler)
    print(f'''
========================================
  VisionAI Server Permanente
========================================
  URL: http://localhost:{PORT}/
  OpenAI: {'CONFIGURED' if OPENAI_API_KEY else 'NOT CONFIGURED'}
  
  Para configurar OpenAI:
  set OPENAI_API_KEY=sua_chave
========================================
''')
    server.serve_forever()

if __name__ == '__main__':
    run_server()
