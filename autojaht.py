import os
import subprocess
import asyncio
import aiohttp
import time
from datetime import datetime

# --- KONFIGURATSIOON ---
TELEGRAM_TOKEN = "8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc"
CHAT_ID = "8687532870"
ARCHIVE_ROOT = "/home/coder/project/archive_5tb"
SCREENSHOT_DIR = "/home/coder/project/screenshots"

# Kaustade ettevalmistus
for folder in [ARCHIVE_ROOT, SCREENSHOT_DIR]:
    os.makedirs(folder, exist_ok=True)

async def teavita(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

async def saada_pilt(path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        data = aiohttp.FormData()
        data.add_field('photo', open(path, 'rb'))
        data.add_field('chat_id', CHAT_ID)
        data.add_field('caption', caption)
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=data)
    except: pass

async def gowitness_snaiper(url):
    """Teeb veebilehest pildi ja saadab selle kohe."""
    safe_url = url.replace("://", "_").replace(".", "_").replace("/", "_")[:50]
    img_path = f"{SCREENSHOT_DIR}/{safe_url}.png"
    cmd = f"gowitness single {url} --disable-db --disable-logging -o {img_path}"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    if os.path.exists(img_path):
        await saada_pilt(img_path, f"📸 Snaiper-vaade: {url}")

async def autojaht_snaiper():
    print("\n" + "="*40)
    print("🎯 BOUNTY HUNTER - SNAIPER REŽIIM")
    print("="*40)
    
    domain = input("👉 Sisesta sihtmärk (nt tesla.com): ").strip()
    if not domain: return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    work_dir = os.path.join(ARCHIVE_ROOT, f"SNIPER_{domain}_{timestamp}")
    os.makedirs(work_dir, exist_ok=True)

    await teavita(f"🔭 <b>SNAIPER-JAHT ALUSTATUD: {domain}</b>")

    # 1. ETAPP: Recon
    print(f"🔍 1/4: Teostan luuret domeenile {domain}...")
    subs_file = os.path.join(work_dir, "subs.txt")
    subprocess.run(f"subfinder -d {domain} -all -silent -o {subs_file}", shell=True)
    
    live_file = os.path.join(work_dir, "live.txt")
    subprocess.run(f"httpx -l {subs_file} -silent -sc -td -title -o {live_file}", shell=True)

    if not os.path.exists(live_file) or os.path.getsize(live_file) == 0:
        print("❌ Elusaid alamdomeene ei leitud.")
        return

    with open(live_file, "r") as f:
        urls = [line.split()[0] for line in f if line.strip()]

    # 2. ETAPP: Nuclei süvaskann
    print(f"🧬 2/4: Käivitan Nuclei süvaskaneerimise ({len(urls)} targetit)...")
    nuclei_out = os.path.join(work_dir, "nuclei_results.txt")
    # -as automaatne tehnoloogia tuvastus on siin kriitiline
    nuclei_cmd = f"nuclei -l {live_file} -as -severity critical,high -ni -o {nuclei_out}"
    
    # Jookseme nuclei ja jälgime väljundit reaalajas
    process = await asyncio.create_subprocess_shell(nuclei_cmd, stdout=asyncio.subprocess.PIPE)
    while True:
        line = await process.stdout.readline()
        if not line: break
        decoded = line.decode().strip()
        if any(s in decoded.lower() for s in ["[critical]", "[high]"]):
            await teavita(f"🔴 <b>KRIITILINE LEID:</b>\n<code>{decoded}</code>")

    # 3. ETAPP: Gowitness pildid
    print(f"📸 3/4: Teostan visuaalset kontrolli (top 10 lehte)...")
    tasks = [gowitness_snaiper(url) for url in urls[:10]]
    await asyncio.gather(*tasks)

    # 4. ETAPP: JS Saladuste jaht
    print(f"🔑 4/4: Otsin saladusi JS failidest (Katana)...")
    for url in urls[:5]:
        js_cmd = f"katana -u {url} -d 3 -jc -em js -silent | nuclei -tags token,secret -ni"
        subprocess.run(js_cmd, shell=True)

    print(f"\n✅ JAHT LÕPPENUD! Tulemused kaustas: {work_dir}")
    await teavita(f"🏁 <b>SNAIPER-JAHT LÕPPENUD: {domain}</b>\nKõik andmed on 5TB arhiivis.")

if __name__ == "__main__":
    asyncio.run(autojaht_snaiper())
