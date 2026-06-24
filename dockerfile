FROM codercom/code-server:latest
USER root

# 1. Paigaldame süsteemi baasvahendid, sõltuvused ja Debiani-põhise Chromiumi screenshotide jaoks
RUN apt-get update && apt-get install -y \
    python3 python3-pip git curl wget dnsutils unzip libpcap-dev \
    chromium libnss3 libatk-bridge2.0-0 libx11-xcb1 \
    libxcb-dri3-0 libxcomposite1 libxcursor1 libxdamage1 libxi6 \
    libxrandr2 libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# 2. Paigaldame Pythoni raamistikud (sh Arjun)
RUN 

# Tööriistade paigaldamine (Go-põhised stabiilsed binaarid)
WORKDIR /usr/local/bin/

# 1. Subfinder
RUN wget -q https://github.com/projectdiscovery/subfinder/releases/download/v2.6.6/subfinder_2.6.6_linux_amd64.zip && \
    unzip -o subfinder_2.6.6_linux_amd64.zip && rm subfinder_*.zip

# 2. HTTPX
RUN wget -q https://github.com/projectdiscovery/httpx/releases/download/v1.6.0/httpx_1.6.0_linux_amd64.zip && \
    unzip -o httpx_1.6.0_linux_amd64.zip && rm httpx_*.zip

# 3. Nuclei
RUN wget -q https://github.com/projectdiscovery/nuclei/releases/download/v3.1.8/nuclei_3.1.8_linux_amd64.zip && \
    unzip -o nuclei_3.1.8_linux_amd64.zip && rm nuclei_*.zip

# 4. Katana
RUN wget -q https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_linux_amd64.zip && \
    unzip -o katana_1.1.0_linux_amd64.zip && rm katana_*.zip

# 5. Naabu
RUN wget -q https://github.com/projectdiscovery/naabu/releases/download/v2.3.1/naabu_2.3.1_linux_amd64.zip && \
    unzip -o naabu_2.3.1_linux_amd64.zip && rm naabu_*.zip

# 6. Ffuf
RUN wget -q https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_linux_amd64.tar.gz && \
    tar -xzf ffuf_2.1.0_linux_amd64.tar.gz ffuf && rm ffuf_*.tar.gz

# 7. Dalfox
RUN wget -q https://github.com/hahwul/dalfox/releases/download/v2.9.3/dalfox_2.9.3_linux_amd64.tar.gz && \
    tar -xzf dalfox_2.9.3_linux_amd64.tar.gz dalfox && rm dalfox_*.tar.gz

# 8. Gowitness (Screenshotid)
RUN wget -q https://github.com/sensepost/gowitness/releases/download/2.5.1/gowitness-2.5.1-linux-amd64 -O /usr/local/bin/gowitness && \
    chmod +x /usr/local/bin/gowitness

# 9. Waybackurls
RUN apt-get update && apt-get install -y golang && \
    GO111MODULE=on go install github.com/tomnomnom/waybackurls@latest && \
    GOBIN=$(go env GOPATH)/bin && \
    cp ${GOBIN}/waybackurls /usr/local/bin/ && \
    apt-get purge -y golang && apt-get autoremove -y && \
    rm -rf /root/go /home/coder/go /var/lib/apt/lists/*

# Uuendame Nuclei mallid valmis, et skännid algaksid kohe viivituseta
RUN nuclei -update-templates

# Naaseme turvalise kasutaja juurde ja määrame töökausta
USER coder
WORKDIR /home/coder/project

# Käivituskomand sinu Pythoni mootorile
CMD ["python3", "raha_masin.py"]