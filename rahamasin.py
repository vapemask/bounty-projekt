import os
import subprocess
import asyncio
import aiohttp
import time
import random

# --- 1. SEADISTUSED ---
TELEGRAM_TOKEN = "8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc"
CHAT_ID = "8687532870"
KULD_PATH = "/home/coder/project/kuld.txt"
SCREENSHOT_DIR = "/home/coder/project/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# --- 2. ABIFUNKTSIOONID ---
async def teavita(msg):
    print(f"[LOG] {msg}")
    with open("raha_masin.log", "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

async def saada_pilt(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        data = aiohttp.FormData()
        data.add_field('photo', open(file_path, 'rb'))
        data.add_field('chat_id', CHAT_ID)
        data.add_field('caption', caption)
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=data)
    except: pass

# --- 3. RÜNDEMOODULID ---

async def tee_foto(url):
    """Teeb veebilehest pildi."""
    safe_name = url.replace("://", "_").replace(".", "_").replace("/", "_")[:50]
    path = f"{SCREENSHOT_DIR}/{safe_name}.png"
    cmd = f"gowitness single -u {url} --write-db=false --disable-logging -o {path}"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    if os.path.exists(path):
        await saada_pilt(path, f"📸 Ekraanipilt: {url}")

async def jooksuta_nuclei_master(targets_file):
    """Nuclei süvaskaneerimine (asendab suvajaht.py ja suvaskanner.py)."""
    print("🚀 Nuclei süvaskaneerimine...")
    # Kasutame -as (automaatne tehnoloogia tuvastus) ja spetsiaalseid tage
    cmd = f"nuclei -l {targets_file} -as -severity critical,high -ni -rl 10"
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
    
    while True:
        line = await process.stdout.readline()
        if not line: break
        decoded_line = line.decode().strip()
        if any(x in decoded_line.lower() for x in ["[critical]", "[high]"]):
            await teavita(f"🔴 <b>KRIITILINE LEID:</b>\n<code>{decoded_line}</code>")

async def jooksuta_js_jaht(url):
    """Otsib JS failidest saladusi."""
    cmd = f"katana -u {url} -d 2 -jc -em js -silent | nuclei -tags token,secret -ni -rl 5"
    subprocess.run(cmd, shell=True)

async def jooksuta_ffuf(url):
    """Failide fuzzer."""
    cmd = f"ffuf -u {url}/FUZZ -w {KULD_PATH} -mc 200,403 -t 20 -sf -s"
    res = await asyncio.to_thread(subprocess.run, cmd, shell=True, capture_output=True, text=True)
    if res.stdout.strip():
        await teavita(f"💰 <b>FFUF LEID ({url}):</b>\n<code>{res.stdout[:200]}</code>")

# --- 4. PEA-PROTSESS ---

async def runda_domeeni(domain):
    await teavita(f"🎯 <b>ALUSTAN JAHTI: {domain}</b>")
    
    # 1. Alamdomeenid
    subprocess.run(f"subfinder -d {domain} -all -silent -o subs.txt", shell=True)
    
    # 2. Elusad lehed
    subprocess.run("httpx -l subs.txt -silent -o elusad.txt", shell=True)

    if os.path.exists("elusad.txt") and os.path.getsize("elusad.txt") > 0:
        with open("elusad.txt", "r") as f:
            urls = [l.strip() for l in f if l.strip()][:10]
        
        # Käivitame kõik moodulid paralleelselt
        tasks = []
        tasks.append(jooksuta_nuclei_master("elusad.txt"))
        for u in urls[:5]:
            tasks.append(tee_foto(u))
            tasks.append(jooksuta_js_jaht(u))
            tasks.append(jooksuta_ffuf(u))
        
        await asyncio.gather(*tasks)

    # Puhastus
    for f in ["subs.txt", "elusad.txt"]:
        if os.path.exists(f): os.remove(f)

async def main():
    await teavita("🚀 <b>ULTRA-MASIN KÄIVITATUD</b>")
    while True:
        if os.path.exists("targets.txt"):
            with open("targets.txt", "r") as f:
                domains = [l.strip() for l in f if l.strip()]
            for d in domains:
                try:
                    await runda_domeeni(d)
                except Exception as e:
                    print(f"Viga: {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())