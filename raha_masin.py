import os
import subprocess
import asyncio
import aiohttp
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any

# Seadistame logimise konsooli
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. KONFIGURATSIOON ---
TELEGRAM_TOKEN = "8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc"
CHAT_ID = "8687532870"
KULD_PATH = "/home/coder/project/kuld.txt"
SCREENSHOT_DIR = "/home/coder/project/screenshots"
DB_PATH = "/home/coder/project/findings.db"

# Avalikud võtmed ja parameetrid, mis on müra ja mida me ei raporteeri
IGNORED_KEYS = ["wg_", "pk_live_", "maps.googleapis.com", "google-analytics", "recaptcha"] 
SAADETUD_LEIUD = set() # Sessioonisisene duplikaatide vältimise mälu

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

# --- 2. ANDMEBAASI STRUKTUUR ---
def init_db():
    """Loob andmebaasi tabeli leidude jaoks, kui seda veel pole."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            type TEXT,
            details TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

def db_query(query: str, params: tuple = ()):
    """Universaalne andmebaasi päringute abimees."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"⚠️ Viga andmebaasi päringul: {e}")

# --- 3. INFRASTRUKTUUR JA MEEDIA ---
def uuenda_kuld_list():
    """Laeb alla värske 500+ kuldse fuzzer nimekirja."""
    logging.info("Wait... Värskendan laskemoona (500+ list)...")
    url = "https://raw.githubusercontent.com/Bo0oM/fuzz.txt/master/fuzz.txt"
    try:
        import requests
        r = requests.get(url)
        with open(KULD_PATH, "w") as f:
            f.write(r.text)
        logging.info("✅ Kuldne nimekiri valmis.")
    except Exception as e:
        logging.warning(f"⚠️ Kasutan lokaalset listi. Viga allalaadimisel: {e}")

async def teavita(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        logging.error(f"Telegrami teavitus ebaõnnestus: {e}")

async def saada_pilt(file_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        data = aiohttp.FormData()
        data.add_field('photo', open(file_path, 'rb'))
        data.add_field('chat_id', CHAT_ID)
        data.add_field('caption', caption)
        async with aiohttp.ClientSession() as session:
            await session.post(url, data=data)
    except Exception as e:
        logging.error(f"Telegrami pildi saatmine ebaõnnestus: {e}")

# --- 4. INTEGRATSIOON JA MÜRASUMMUTUS ---
async def salvesta_ja_raporteeri(domain: str, type_tag: str, details: str):
    """
    Süstemaatiline mürasummutus, de-duplikatsioon ja raporteerimine.
    Hoiab ära Telegrami ummistamise ja korduvad teavitused.
    """
    clean_details = details.strip()
    if not clean_details:
        return

    # 1. Filtreerimine: Kas sisaldab ignoreeritavaid võtmeid?
    if any(ignored in clean_details.lower() for ignored in IGNORED_KEYS):
        logging.info(f"🔇 Mürasummutus: Ignoreeriti tuntud avalik võti domeenil {domain}")
        return

    # 2. De-duplikatsioon: Kas oleme seda täna juba näinud?
    finding_id = f"{domain}_{type_tag}_{clean_details[:80]}"
    if finding_id in SAADETUD_LEIUD:
        logging.info(f"🔄 Duplikaat tuvastatud ja blokeeritud: {finding_id}")
        return

    # Lisame sessiooni mällu
    SAADETUD_LEIUD.add(finding_id)

    # 3. Salvestamine SQLite andmebaasi
    aeg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_query(
        "INSERT INTO findings (domain, type, details, time) VALUES (?, ?, ?, ?)", 
        (domain, type_tag, clean_details[:300], aeg)
    )

    # 4. Telegrami teavitus
    if type_tag == "JS_SECRET":
        await teavita(f"🔑 JS SALADUS ({domain}):\n{clean_details[:200]}")
    elif type_tag == "NUCLEI":
        await teavita(f"🔴 NUCLEI LEID ({domain}):\n{clean_details[:200]}")
    else:
        await teavita(f"💰 LEID ({domain} - {type_tag}):\n{clean_details[:200]}")

# --- 5. RÜNDEMOODULID ---
async def tee_foto(url):
    safe_name = url.replace("://", "_").replace(".", "_").replace("/", "_")[:50]
    path = f"{SCREENSHOT_DIR}/{safe_name}.png"
    cmd = f"gowitness single -u {url} --write-db=false --disable-logging -o {path}"
    proc = await asyncio.create_subprocess_shell(cmd)
    await proc.wait()
    if os.path.exists(path):
        await saada_pilt(path, f"📸 Screenshot: {url}")

async def jooksuta_nuclei(targets_file, domain):
    """CVE skaneerimine nuclei abil."""
    cmd = f"nuclei -l {targets_file} -severity critical,high -tags env,git,config,backup,exposure,takeover,cve -ni -rl 15"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    if process.stdout:
        for line in process.stdout:
            clean_line = line.strip()
            if any(x in clean_line.lower() for x in ["[critical]", "[high]"]):
                await salvesta_ja_raporteeri(domain, "NUCLEI", clean_line)

async def jooksuta_js_jaht(url, domain):
    """Otsib JS failidest peidetud API võtmeid ja muid saladusi."""
    logging.info(f"🕵️ JS-Jaht: {url}")
    cmd = f"katana -u {url} -d 2 -jc -em js | nuclei -tags token,secret,generic-beautifier -ni -rl 10"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, text=True)
    if process.stdout:
        for line in process.stdout:
            clean_line = line.strip()
            if "info" not in clean_line.lower():
                await salvesta_ja_raporteeri(domain, "JS_SECRET", clean_line)

async def jooksuta_ffuf(url, domain):
    """Kiire failide fuzzimine."""
    ffuf_cmd = f"ffuf -u {url}/FUZZ -w {KULD_PATH} -e .bak,.old,.zip -mc 200,403 -t 40 -sf -s"
    result = await asyncio.to_thread(subprocess.run, ffuf_cmd, shell=True, capture_output=True, text=True)
    output = result.stdout.strip()
    if output:
        lines = output.splitlines()[:3]
        await salvesta_ja_raporteeri(domain, "FFUF", "\n".join(lines))

async def runda_domeeni(domain):
    await teavita(f"🎯 JAHT ALUSTATUD: {domain}")
    
    # Alamdomeenide leidmine
    subprocess.run(f"subfinder -d {domain} -all -o subs.txt", shell=True)
    
    # Käivitame httpx ainult siis, kui subfinder päriselt midagi leidis
    if os.path.exists("subs.txt") and os.path.getsize("subs.txt") > 0:
        subprocess.run("httpx -l subs.txt -sc -td -o elusad.txt", shell=True)
    else:
        logging.warning(f"⚠️ Subfinder ei leidnud alamdomeene domeenile {domain}")
        return

    if os.path.exists("elusad.txt") and os.path.getsize("elusad.txt") > 0:
        with open("elusad.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip()][:8]

        tasks = []
        tasks.append(jooksuta_nuclei("elusad.txt", domain))
        for url in urls:
            tasks.append(jooksuta_ffuf(url, domain))
            tasks.append(jooksuta_js_jaht(url, domain))
        
        await asyncio.gather(*tasks)

    # Koristame ajutised failid
    for f in ["subs.txt", "elusad.txt"]:
        if os.path.exists(f): 
            os.remove(f)

# --- 6. PEAMINE KÄIVITUSTSÜKKEL ---
async def main():
    init_db()
    uuenda_kuld_list()
    
    if not os.path.exists("targets.txt"): 
        logging.error("Loo targets.txt fail domeenidega!")
        return
        
    with open("targets.txt", "r") as f:
        domains = [l.strip() for l in f if l.strip()]
    
    await teavita("🚀 ULTRA-MASIN (JS-EDITION) KÄIVITATUD")
    for d in domains:
        await runda_domeeni(d)
    await teavita("🏆 JAHT LÕPPENUD!")

if __name__ == "__main__":
    asyncio.run(main())