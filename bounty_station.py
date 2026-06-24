import asyncio
import sqlite3
import logging
import os
from aiohttp import web, ClientSession
from datetime import datetime

# --- CONFIG ---
WEB_PORT = 5000
DB_PATH = "/home/coder/project/recon.db"
TELEGRAM_TOKEN = "8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc"
CHAT_ID = "8687532870"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# --- DB SETUP ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS targets (domain TEXT PRIMARY KEY, status TEXT, added_at TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS findings (id INTEGER PRIMARY KEY, domain TEXT, type TEXT, data TEXT, severity TEXT)")
    conn.commit()
    conn.close()

# --- RECON LOGIC ---
async def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        async with ClientSession() as session:
            await session.post(url, json={"chat_id": CHAT_ID, "text": f"🎯 [BOUNTY]: {msg}"})
    except: pass

async def run_recon(domain):
    logging.info(f"Alustan luuret: {domain}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE targets SET status = 'scanning' WHERE domain = ?", (domain,))
    conn.commit()

    # 1. Samm: HTTPX kontroll (Kas on elus?)
    cmd_httpx = f"echo {domain} | httpx -silent"
    proc = await asyncio.create_subprocess_shell(cmd_httpx, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    
    if not stdout:
        logging.warning(f"Domeen {domain} ei vasta. Katkestan.")
        conn.execute("UPDATE targets SET status = 'dead' WHERE domain = ?", (domain,))
        conn.commit()
        return

    # 2. Samm: Nuclei (Kiire skänn)
    await send_telegram(f"Sihtmärk {domain} on elus. Käivitan Nuclei...")
    cmd_nuclei = f"echo {domain} | nuclei -severity high,critical -ni -silent"
    proc = await asyncio.create_subprocess_shell(cmd_nuclei, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    
    if stdout:
        finding = stdout.decode().strip()
        conn.execute("INSERT INTO findings (domain, type, data, severity) VALUES (?, ?, ?, ?)", 
                     (domain, "Nuclei", finding, "HIGH"))
        await send_telegram(f"LEID: {finding}")

    conn.execute("UPDATE targets SET status = 'done' WHERE domain = ?", (domain,))
    conn.commit()
    conn.close()

# --- SCANNER WORKER ---
async def worker():
    while True:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT domain FROM targets WHERE status = 'pending' LIMIT 1").fetchone()
        conn.close()
        
        if row:
            await run_recon(row[0])
        await asyncio.sleep(10)

# --- WEB SERVER ---
async def handle_home(request):
    conn = sqlite3.connect(DB_PATH)
    targets = conn.execute("SELECT * FROM targets").fetchall()
    findings = conn.execute("SELECT * FROM findings").fetchall()
    conn.close()
    
    html = f"<html><head><title>Bounty Station</title><style>body{{background:#111;color:#0f0;font-family:monospace;padding:20px;}} .finding{{color:red;border-bottom:1px solid #333;}}</style></head><body>"
    html += "<h1>🛰️ BOUNTY STATION COMMAND</h1>"
    html += "<h3>Lisa sihtmärk:</h3><form action='/add' method='POST'><input name='d' placeholder='target.com'><button>RÜNDA</button></form>"
    html += "<h2>Sihtmärgid</h2><ul>" + "".join([f"<li>{t[0]} - [{t[1]}]</li>" for t in targets]) + "</ul>"
    html += "<h2>Leidud</h2>" + "".join([f"<div class='finding'>{f[1]} | {f[2]} | {f[3]}</div>" for f in findings])
    html += "</body></html>"
    return web.Response(text=html, content_type='text/html')

async def handle_add(request):
    data = await request.post()
    domain = data['d']
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO targets VALUES (?, 'pending', ?)", (domain, datetime.now().isoformat()))
        conn.commit()
    except: pass
    conn.close()
    return web.HTTPFound('/')

# --- START ---
if __name__ == "__main__":
    init_db()
    app = web.Application()
    app.router.add_get('/', handle_home)
    app.router.add_post('/add', handle_add)
    
    loop = asyncio.get_event_loop()
    loop.create_task(worker())
    web.run_app(app, port=WEB_PORT)