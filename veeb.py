# veeb.py
import os
import subprocess
import tempfile
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aether - Ründe ja Koodi Testimiskeskkond</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
        .terminal-output { text-shadow: 0 0 2px rgba(74, 222, 128, 0.5); }
    </style>
</head>
<body class="bg-black text-gray-300 font-mono h-screen flex flex-col overflow-hidden">
    <header class="bg-gray-900 border-b border-green-900 p-4 flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <h1 class="text-green-500 font-bold text-xl tracking-widest">AETHER_CMD_CENTER <span class="text-xs text-gray-500">v2.1.0 (LIVE)</span></h1>
        </div>
        <div class="text-xs text-gray-500 flex space-x-4">
            <span>SIHTMÄRK: <span class="text-white" id="target-display">MÄÄRAMATA</span></span>
            <span>STAATUS: <span class="text-green-500" id="status-indicator">VALMIS</span></span>
        </div>
    </header>

    <main class="flex-1 flex flex-col md:flex-row overflow-hidden">
        <div class="w-full md:w-1/2 flex flex-col border-r border-gray-800 h-full">
            <div class="bg-gray-900 p-2 text-xs text-gray-400 border-b border-gray-800 flex justify-between">
                <span>SKRIPTI_SISEND.py</span>
                <button onclick="clearEditor()" class="hover:text-red-400 transition-colors">TÜHJENDA</button>
            </div>
            <textarea id="code-editor" class="flex-1 bg-[#0d0d0d] text-gray-200 p-4 focus:outline-none resize-none font-mono text-sm" spellcheck="false" placeholder="# Sisesta oma Pythoni payload või recon skript siia..."></textarea>
            
            <div class="bg-gray-900 p-4 flex space-x-3 shrink-0">
                <input type="text" id="target-input" placeholder="example.com" class="bg-black border border-gray-700 text-green-500 px-3 py-2 text-sm focus:outline-none focus:border-green-500 flex-1">
                <button id="run-btn" onclick="executePayload()" class="bg-green-900 hover:bg-green-700 text-green-100 px-6 py-2 rounded-sm text-sm font-bold uppercase transition-all flex items-center">
                    Käivita Kood
                </button>
            </div>
        </div>

        <div class="w-full md:w-1/2 flex flex-col h-full bg-black">
            <div class="bg-gray-900 p-2 text-xs text-gray-400 border-b border-gray-800 flex justify-between">
                <span>TERMINAL_VÄLJUND</span>
            </div>
            <div id="terminal" class="flex-1 p-4 overflow-y-auto text-green-400 text-sm terminal-output whitespace-pre-wrap">Aether OS (v2.1.0 LIVE) käivitatud. Ootan käske...\n> _</div>
        </div>
    </main>

    <script>
        // Siia panime uue diagnostikakoodi! Backtickid (`) hoiavad reavahetusi elus.
        const defaultCode = `import os
import sys
import urllib.request

target = sys.argv[1] if len(sys.argv) > 1 else "example.com"

print("-" * 40)
print(f"[*] AETHER C2 DIAGNOSTIKA & RECON")
print("-" * 40)

# 1. Keskkonna tuvastamine
print("[+] Kontrollin lokaalset süsteemi (Privacy-First):")
os.system("whoami")
os.system("ip a | grep 'inet ' | awk '{print $2}'")

# 2. SSRF Simulatsioon (Cloud Metadata Endpoint)
metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/name"
headers = {"Metadata-Flavor": "Google"}

print("\\\\n[*] Testin sisemist SSRF ligipääsu (GCP Metadata):")
try:
    req = urllib.request.Request(metadata_url, headers=headers)
    with urllib.request.urlopen(req, timeout=3) as response:
        data = response.read().decode()
        print(f"[!] KRIITILINE: Ligipääs sisevõrgule olemas! Instants: {data}")
except Exception as e:
    print(f"[+] Turvaline: Sisemine metaandmete server pole otse kättesaadav ({e})")

# 3. Välise sihtmärgi baaskontroll
print(f"\\\\n[*] Proovin resolvida sihtmärki: {target}")
os.system(f"ping -c 2 {target}")

print("\\\\n[+] Diagnostika lõpetatud!")`;

        document.getElementById('code-editor').value = defaultCode;
        const terminal = document.getElementById('terminal');
        const targetInput = document.getElementById('target-input');
        const targetDisplay = document.getElementById('target-display');
        const statusInd = document.getElementById('status-indicator');
        const runBtn = document.getElementById('run-btn');

        function clearEditor() { document.getElementById('code-editor').value = ''; }

        function appendToTerminal(text, type = 'normal') {
            const span = document.createElement('span');
            if (type === 'error') span.className = 'text-red-500';
            else if (type === 'system') span.className = 'text-blue-400';
            span.textContent = text + '\\n';
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function executePayload() {
            const code = document.getElementById('code-editor').value;
            const target = targetInput.value.trim() || 'example.com';
            
            targetDisplay.textContent = target.toUpperCase();
            terminal.innerHTML = '';
            appendToTerminal(`> Skripti saatmine serverisse (Target: ${target})...`, 'system');
            
            statusInd.textContent = "TÖÖTAB...";
            statusInd.className = "text-yellow-500 animate-pulse";
            runBtn.disabled = true;

            try {
                const basePath = window.location.pathname.replace(/\\/$/, '');
                const apiUrl = basePath + '/api/execute';
                
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code, target: target })
                });
                
                const result = await response.json();
                
                if (result.status === "success") {
                    appendToTerminal(result.output);
                } else {
                    appendToTerminal("[!] Viga skripti käivitamisel:\\n" + result.error, 'error');
                }
            } catch (err) {
                appendToTerminal("[!] Ühenduse viga serveriga: " + err.message, 'error');
            }

            statusInd.textContent = "VALMIS";
            statusInd.className = "text-green-500";
            runBtn.disabled = false;
            appendToTerminal('> _');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code', '')
    target = data.get('target', 'example.com')

    if not code.strip():
        return jsonify({"status": "error", "error": "Kood on tühi!"})

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(code)
        temp_script_path = temp_script.name

    try:
        result = subprocess.run(
            ['python3', temp_script_path, target],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[VIGAD/HOIATUSED]:\n{result.stderr}"

        return jsonify({"status": "success", "output": output})

    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "error": "Skripti käivitamine aegus (Timeout > 60s)."})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})
    finally:
        if os.path.exists(temp_script_path):
            os.remove(temp_script_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)