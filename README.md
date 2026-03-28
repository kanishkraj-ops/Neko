<h1 align="center">🐾 Neko Security Framework</h1>
<p align="center">
    A powerful multi-mode offensive security framework written in Python.<br>
    Designed for reconnaissance, OSINT, exploitation aids, and authorized penetration testing.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://img.shields.io/badge/Version-2.0.0--beta-red.svg">
</p>

---

## 🔧 Features

Neko has been upgraded from a simple netcat tool to a modular framework:

- 📡 **Core**: Netcat-style listeners, reverse shells, and file transfers (Legacy compatible).
- 🔍 **Recon**: Port scanning, service detection, DNS enumeration, and WHOIS lookups.
- 🕵️ **Search**: CVE searching, Shodan integration, Google dorking, and subdomain enumeration.
- 🧨 **Exploit**: Reverse shell payload generator (Bash, Python, PHP, PowerShell), HTTP payload hosting, and C2 mode.
- ⚔️ **Attack**: TCP/UDP flooding, SSH/HTTP brute-forcing, and directory brute-forcing.
- 📊 **Reporting**: Export results to JSON or CSV.
- 🐍 **Modular**: Clean Pythonic architecture with colored terminal output.

---

## 📦 Installation

### 🔗 Clone the Repository

```bash
git clone https://github.com/kanishkraj-ops/Neko.git
cd neko
```

### 🐍 Install Dependencies & Tool

```bash
# Using pip
pip install .

# Install required external packages
pip install rich requests dnspython paramiko python-whois shodan
```

---

## 🚀 Usage

Neko uses a subparser system: `neko <mode> [options]`

### 1️⃣ Recon Mode
```bash
# Port scan a target with service detection
neko recon -t example.com --scan-ports --range 1-1000

# DNS enumeration and WHOIS lookup
neko recon -t example.com --dns --whois
```

### 2️⃣ Search Mode
```bash
# Search for CVEs related to a product
neko search --cve "apache 2.4.49"

# Generate Google Dorks for a domain
neko search -t example.com --dorks

# Subdomain enumeration (requires wordlist)
neko search -t example.com --subdomains --wordlist wordlist.txt
```

### 3️⃣ Exploit Mode
```bash
# Generate a Python reverse shell payload (Base64 encoded)
neko exploit --revshell --lhost 192.168.1.10 --lport 4444 --type python --encode b64

# Host a payload directory via HTTP
neko exploit --serve --port 8080 --dir ./payloads
```

### 4️⃣ Attack Mode
```bash
# SSH Brute-force
neko attack -t 192.168.1.100 --bruteforce ssh --user root --wordlist rockyou.txt

# HTTP Directory Brute-force
neko attack -t http://example.com --dirbrute --wordlist common.txt

# TCP Flood (Stress Test)
neko attack -t 192.168.1.100 --flood --port 80 --duration 30
```

### 5️⃣ Core Mode (Netcat Logic)
```bash
# Start a listener with a command shell (Legacy style)
neko core --listen --port 5555 --command

# Connect to a target
neko core --target 192.168.1.100 --port 5555
```

---

## 📁 Project Structure

```
Neko/
├── neko/
│   ├── cli.py           # Main entry point
│   ├── core.py          # Netcat logic
│   ├── modes/           # Feature-specific modules
│   │   ├── recon.py
│   │   ├── search.py
│   │   ├── exploit.py
│   │   └── attack.py
│   └── utils/           # Shared utilities
│       ├── logger.py    # Colored output
│       ├── reporter.py  # JSON/CSV export
│       └── encoder.py   # Payload encoding
├── setup.py
├── pyproject.toml
└── README.md
```

---

## ⚠️ Disclaimer

> [!IMPORTANT]
> This tool is developed strictly for **educational purposes** and **authorized penetration testing** only. 
> Illegal use of this tool is strictly prohibited. The authors are not responsible for any misuse.

---

## 🧠 Author

Built with passion by **Kanishk Raj** 🛠️  
[GitHub](https://github.com/kanishkraj-ops) • [LinkedIn](https://www.linkedin.com/in/kanishk-raj-841715332/) 

➡️ Contributions, issues, and stars ⭐ are always welcome!


---

