<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aether - Ründe ja Koodi Testimiskeskkond</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Kohandatud kerimisriba terminali stiili jaoks */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #0a0a0a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #555; }
        
        .terminal-output {
            text-shadow: 0 0 2px rgba(74, 222, 128, 0.5);
        }
    </style>
</head>
<body class="bg-black text-gray-300 font-mono h-screen flex flex-col overflow-hidden">

    <!-- Päis -->
    <header class="bg-gray-900 border-b border-green-900 p-4 flex justify-between items-center shrink-0">
        <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <h1 class="text-green-500 font-bold text-xl tracking-widest">AETHER_CMD_CENTER <span class="text-xs text-gray-500">v2.0.4</span></h1>
        </div>
        <div class="text-xs text-gray-500 flex space-x-4">
            <span>SIHTMÄRK: <span class="text-white" id="target-display">MÄÄRAMATA</span></span>
            <span>STAATUS: <span class="text-green-500">VALMIS</span></span>
        </div>
    </header>

    <!-- Põhisisu -->
    <main class="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        <!-- Vasak paneel: Koodi redaktor -->
        <div class="w-full md:w-1/2 flex flex-col border-r border-gray-800 h-full">
            <div class="bg-gray-900 p-2 text-xs text-gray-400 border-b border-gray-800 flex justify-between">
                <span>SKRIPTI_SISEND.py</span>
                <button onclick="clearEditor()" class="hover:text-red-400 transition-colors">TÜHJENDA</button>
            </div>
            <textarea id="code-editor" class="flex-1 bg-[#0d0d0d] text-gray-200 p-4 focus:outline-none resize-none font-mono text-sm" spellcheck="false" placeholder="# Sisesta oma Pythoni payload või recon skript siia..."></textarea>
            
            <!-- Juhtpaneel -->
            <div class="bg-gray-900 p-4 flex space-x-3 shrink-0">
                <input type="text" id="target-input" placeholder="sihtmärk.com" class="bg-black border border-gray-700 text-green-500 px-3 py-2 text-sm focus:outline-none focus:border-green-500 flex-1">
                <button onclick="runSimulation()" class="bg-green-900 hover:bg-green-700 text-green-100 px-6 py-2 rounded-sm text-sm font-bold uppercase transition-all flex items-center">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Käivita Simulaator
                </button>
            </div>
        </div>

        <!-- Parem paneel: Terminali väljund -->
        <div class="w-full md:w-1/2 flex flex-col h-full bg-black">
            <div class="bg-gray-900 p-2 text-xs text-gray-400 border-b border-gray-800 flex justify-between">
                <span>TERMINAL_VÄLJUND</span>
                <span class="text-green-500" id="execution-time">0.00s</span>
            </div>
            <div id="terminal" class="flex-1 p-4 overflow-y-auto text-green-400 text-sm terminal-output whitespace-pre-wrap">
Aether OS (v2.0.4) käivitatud.
Ootan käske...
> _
            </div>
        </div>
    </main>

    <script>
        // Eellaetud kood kasutaja eelmise sõnumi põhjal
        const defaultCode = `import subprocess
import sys

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout.strip()
    except:
        return ""

target = sys.argv[1]

print("[+] Starting full recon on", target)

# Subdomain enumeration
subdomains = run_command(f"subfinder -d {target} -silent | anew subdomains.txt")
subdomains += run_command(f"amass enum -passive -d {target} -o amass.txt")

# Live hosts
run_command("cat subdomains.txt | httpx -silent -mc 200,403,500 -o live_hosts.txt")

# Tech detection
run_command("cat live_hosts.txt | whatweb - --log-json tech.json")

print("[+] Recon completed. Live hosts:", len(open("live_hosts.txt").readlines()))`;

        document.getElementById('code-editor').value = defaultCode;
        const terminal = document.getElementById('terminal');
        const targetInput = document.getElementById('target-input');
        const targetDisplay = document.getElementById('target-display');

        function clearEditor() {
            document.getElementById('code-editor').value = '';
        }

        function appendToTerminal(text, type = 'normal') {
            const span = document.createElement('span');
            if (type === 'error') span.className = 'text-red-500';
            else if (type === 'system') span.className = 'text-blue-400';
            else if (type === 'success') span.className = 'text-green-300 font-bold';
            
            span.textContent = text + '\n';
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function runSimulation() {
            const code = document.getElementById('code-editor').value;
            const target = targetInput.value.trim() || 'example.com';
            
            targetDisplay.textContent = target.toUpperCase();
            terminal.innerHTML = '';
            
            appendToTerminal(`> python3 skript.py ${target}`, 'system');
            
            if (!code) {
                appendToTerminal('[!] Viga: Koodi redaktor on tühi.', 'error');
                return;
            }

            // Simuleerime töövoogu
            const lines = code.split('\n');
            let isReconScript = code.includes('subfinder') || code.includes('httpx');

            await sleep(500);

            if (isReconScript) {
                appendToTerminal(`[+] Starting full recon on ${target}`);
                await sleep(800);
                appendToTerminal(`[*] Running: subfinder -d ${target} -silent`);
                await sleep(1200);
                appendToTerminal(`[*] Running: amass enum -passive -d ${target}`);
                await sleep(1500);
                appendToTerminal(`[+] Found 142 subdomains.`);
                await sleep(500);
                appendToTerminal(`[*] Running: httpx -silent -mc 200,403,500`);
                await sleep(2000);
                appendToTerminal(`[+] 38 live hosts identified.`);
                await sleep(800);
                appendToTerminal(`[*] Running technology detection (whatweb)...`);
                await sleep(1500);
                appendToTerminal(`[!] CRITICAL FOCUS: Found 2 instances of outdated Jenkins and 1 exposed Gitlab.`, 'success');
                appendToTerminal(`[+] Recon completed. Live hosts: 38`);
            } else {
                // Generiline simulatsioon tundmatu koodi jaoks
                appendToTerminal('[*] Analüüsin koodi süntaksit...');
                await sleep(1000);
                appendToTerminal('[*] Kood on süntaktiliselt korrektne (simuleeritud).', 'success');
                appendToTerminal('[!] Kuna tegemist on brauseri liivakastiga, ei saa süsteemseid käske reaalselt käivitada.', 'error');
                appendToTerminal('[*] Valmis kopeerimiseks Cloud Shell / VPS keskkonda.', 'system');
            }

            appendToTerminal('\n> _');
        }

        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    </script>
</body>
</html>