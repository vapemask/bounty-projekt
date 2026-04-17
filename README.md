GitHub README.md sisuettepanek
🛰️ Bounty Machine V4 - Professionaalne Pilve-Luurejaam
!(https://img.shields.io/badge/Docker-required-blue)

📖 Süsteemi Kirjeldus
Bounty Machine on täielikult automatiseeritud asünkroonne turvauuringute platvorm, mis on optimeeritud töötama Google Cloud Shelli Boost Mode keskkonnas. Süsteem ühendab endas kaasaegseimad recon-tööriistad ja asünkroonse Pythoni loogika, et tuvastada kriitilisi turvaauke masinkiirusel.

🚀 Põhivõimekused
Asünkroonne Analüüs: Kuni 100 paralleelset ühendust korraga tänu asyncio arhitektuurile.

Täielik Recon Workflow: Alamdomeenide passiivne loetlemine, tehnoloogia fingerprinting ja elusate serverite tuvastamine.

Kriitiliste Failide Jaht: Automaatne .env, .git, backupide ja PHP seadistusfailide otsing.

XSS & Fuzzing: Integreeritud DalFox ja FFUF süvitsi minevaks haavatavuste otsimiseks.

Reaalajas Teavitused: Kohene feedback Telegrami boti kaudu koos kullaaugude linkidega.

Professionaalne IDE: VS Code (code-server) integratsioon arendustöödeks otse brauseris.

🛠️ Tehnoloogiline Pinu
Keeled: Python 3.11+ (Asünkroonne), Go 1.24

Infrastruktuur: Docker (Debian-based), Google Cloud Shell (Boost Mode)

Tööriistad: Nuclei, Subfinder, Katana, httpx, DalFox, Naabu, FFUF, SecLists

📦 Kiirpaigaldus
Ava(https://shell.cloud.google.com).

Aktiveeri Boost Mode (üleval paremal kolm täppi -> Enable Boost Mode).

Kopeeri ja käivita:bash
git clone https://github.com/vapemask/bounty-projekt.git
cd bounty-projekt
chmod +x setup.sh &&./setup.sh


🔐 Turvalisus ja Seadistused
Kõik API võtmed ja saladused asuvad failis .env. Ära kunagi jaga seda faili avalikult!

Code snippet
TELEGRAM_TOKEN=8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc
CHAT_ID=8687532870
⚠️ Vastutuse välistamine
See süsteem on loodud ainult eetiliseks turvauuringuks ja hariduslikel eesmärkidel. Autor ei vastuta süsteemi väärkasutuse eest. Kasutaja kohustub järgima kõiki seadusi ja Bug Bounty programmide reegleid.


## Operatiivjuhend: Süsteemi käivitamine nullist profini

Järgnev juhend on koostatud "copy-paste" printsiibil, tagades süsteemi tõrgeteta ülesseadmise ka uue arvuti taga ilma sügavate tehniliste eelteadmisteta.

### I etapp: Keskkonna ettevalmistus (Google Cloud Shell)

1.  Logi sisse aadressil [console.cloud.google.com](https://console.cloud.google.com).
2.  Klõpsa paremal ülaservas ikoonile `>_` (Activate Cloud Shell).
3.  **Kriitiline samm**: Vali terminali akna ülaservas kolme täpiga ikoon, vali "Enable Boost Mode" ja kinnita taaskäivitus. See samm on vajalik 15 GB RAM-i saamiseks, ilma milleta skannerid kokku jooksevad.

### II etapp: Projekti struktuuri loomine

Kopeeri ja kleebi terminali järgnev käsk, mis loob puhta töökeskkonna ja vajalikud failid:
```bash
mkdir -p ~/bounty-projekt && cd ~/bounty-projekt && \
touch Dockerfile targets.txt raha_masin.py veeb.py.env
III etapp: Docker-keskkonna konfigureerimine
Dockerfile on süsteemi süda, mis paneb paika kõik tööriistad. Ava toimetis käsuga cloudshell edit Dockerfile ja asenda sisu järgmisega:

Dockerfile
FROM codercom/code-server:latest
USER root
# Süsteemi tööriistad ja Go installimine
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl wget dnsutils unzip libpcap-dev nmap golang-go \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Pythoni raamatukogud
RUN pip3 install --no-cache-dir --break-system-packages \
    pandas flask cloudscraper aiohttp requests psutil python-dotenv beautifulsoup4 tldextract
# Tööriistade installimine (Pre-compiled binaries kiiruse huvides)
WORKDIR /usr/local/bin
RUN wget https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_linux_amd64.zip && unzip -o subfinder_2.6.6_linux_amd64.zip
RUN wget https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_linux_amd64.zip && unzip -o httpx_1.6.0_linux_amd64.zip
RUN wget https://github.com/projectdiscovery/nuclei/releases/download/v3.1.8/nuclei_3.1.8_linux_amd64.zip && unzip -o nuclei_3.1.8_linux_amd64.zip
RUN wget https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_linux_amd64.zip && unzip -o katana_1.1.0_linux_amd64.zip
RUN rm -rf *.zip && chmod +x /usr/local/bin/*
USER coder
WORKDIR /home/coder/project
Salvesta fail (Ctrl+S) ja pane aken kinni.   

IV etapp: Skanneri ja veebiliidese koodi lisamine
Kasutades sama meetodit (cloudshell edit failinimi), täida skriptid:

raha_masin.py: Kleebi sinna asünkroonne skanner, mis kasutab aiohttp ja subprocess mooduleid.   

veeb.py: Kleebi Flaski kood, mis jookseb pordil 5000.   

.env: Lisa oma Telegrami token ja ID (nt TELEGRAM_TOKEN=8740053883:AAHBfNjeYIRn4YNWHxWR8_n8ztc7K86uBzc ja CHAT_ID=8687532870).   

V etapp: Süsteemi käivitamine
Käivita ehitusprotsess (võtab aega ca 3 minutit):

Bash
docker build -t bounty-machine.
Konteineri käivitamine taustal koos pordisuunamisega:

Bash
docker rm -f jaht-station 2>/dev/null; \
docker run -d --name jaht-station \
  -p 8082:8080 \
  -p 8080:5000 \
  -v $(pwd):/home/coder/project \
  bounty-machine \
  code-server --auth none --bind-addr 0.0.0.0:8080 /home/coder/project
VI etapp: Jahtima asumine
Koodi vaatamine: Ava "Web Preview" -> "Change Port" -> trüki 8082. Seal näed oma faile. Ava sealne terminal ja käivita skriptid: python3 veeb.py & python3 raha_masin.py &.   

Juhtpaneel: Ava "Web Preview" pordiga 8080. Sealt saad lisada uusi domeene (nt uber.com) ja vaadata skannimise progressi.   

Telegram: Hoia telefon käepärast. Kõik kriitilised leiud (nt [!] https://target.com/.env) tulevad automaatselt sinu seadmesse.   

Kokkuvõtvad soovitused ja eetikakoodeks
"Bounty Machine" projekt on arenenud võimekaks küberluure platvormiks, mis kasutab ära pilvemasinate varjatud potentsiaali. Kuid tehniline võimekus toob kaasa vastutuse.

Olulised tähelepanekud operatiivseks eduks:

Vähem müra, rohkem tõendeid: Nuclei kasutamisel keskendu "Critical" ja "High" raskusastmetega mallidele, et vältida triaažisüsteemide koormamist ebaoluliste leidudega.   

IP Maine haldamine: Kuigi Google Cloud Shell pakub head ribalaiust, võivad liiga agressiivsed skannid (ilma rate-limitita) viia IP blokeerimiseni. Kasuta alati asünkroonsete päringute vahel mõistlikke ooteaegu.   

Pidev õppimine: Bug Bounty maailm uueneb nädalatega. Uurija peab pidevalt jälgima uusi Nuclei malle ja haavatavuse trende (nt mass-assignment API-des), et hoida oma süsteem konkurentsivõimelisena.   

Lõppkokkuvõttes on "Bounty Machine" V4 stabiilne vundament, millele saab järgnevatel aastatel ehitada peale täielikult autonoomse, agendipõhise tehisintellekti kihi, muutes turvauuringud kättesaadavamaks ja efektiivsemaks kui kunagi varem.   

