from flask import Flask, render_template_string, request, redirect
import os, subprocess, psutil
from collections import Counter

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <title>🛰️ LUURE-KESKUS V3</title>
    <meta http-equiv="refresh" content="15">
    <style>
        body { background: #0a0a0a; color: #00ff41; font-family: 'Courier New', monospace; padding: 20px; }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .box { background: #161616; border: 1px solid #333; padding: 15px; border-radius: 8px; }
        .stats { background: #222; padding: 10px; margin-bottom: 20px; display: flex; gap: 20px; color: #00ffff; }
        .log { white-space: pre-wrap; height: 500px; overflow-y: scroll; background: #000; padding: 10px; font-size: 12px; border: 1px solid #444; }
        button { background: #00ff41; color: #000; border: none; padding: 10px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }
        input { background: #000; border: 1px solid #00ff41; color: #00ff41; padding: 10px; width: 65%; }
        .stop { background: #ff0000; color: white; }
        .critical { color: #ff3333; font-weight: bold; }
        .money { color: #ffff00; }
    </style>
</head>
<body>
    <h1>🛰️ BOUNTY HUNTER COMMAND CENTER</h1>
    <div class="stats">
        <span>🖥️ CPU: {{ cpu }}%</span> <span>💾 RAM: {{ ram }}%</span> <span>🎯 TARGETS: {{ t_count }}</span>
    </div>
    <div class="grid">
        <div class="box">
            <h2>🎯 REAALAJAS LOGI</h2>
            <div class="log">
                {% for line in logid %}<div class="{{ 'critical' if '🔴' in line else 'money' if '💰' in line else '' }}">{{ line }}</div>{% endfor %}
            </div>
        </div>
        <div class="box">
            <h2>🎮 JUHTPULT</h2>
            <form action="/add" method="post">
                <input type="text" name="d" placeholder="domeen.com">
                <button type="submit" style="width:25%">LISA</button>
            </form>
            <form action="/clear" method="post"><button type="submit" style="background:#444; color:#ccc">TÜHJENDA TARGETS</button></form>
            <form action="/stop" method="post"><button type="submit" class="stop">🛑 STOPP KÕIK PROTSESSID</button></form>
            
            <h3>💾 SALVESTUSRUUM (5TB)</h3>
            <div style="color: #aaa;">Kasutusel: {{ disk }}%</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    logid = open("raha_masin.log").readlines()[-100:] if os.path.exists("raha_masin.log") else ["Logid puuduvad..."]
    targets = open("targets.txt").readlines() if os.path.exists("targets.txt") else []
    return render_template_string(HTML_TEMPLATE, logid=reversed(logid), cpu=cpu, ram=ram, t_count=len(targets), disk=disk)

@app.route('/add', methods=['POST'])
def add():
    d = request.form.get('d')
    if d: 
        with open("targets.txt", "a") as f: f.write(f"{d}\n")
    return redirect('/')

@app.route('/stop', methods=['POST'])
def stop():
    for p in ["ffuf", "nuclei", "katana", "subfinder", "python3"]: 
        if "veeb.py" not in p: subprocess.run(f"pkill -f {p}", shell=True)
    return redirect('/')

@app.route('/clear', methods=['POST'])
def clear():
    open("targets.txt", "w").close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)