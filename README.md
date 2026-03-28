<h1 align="center">🐾 Neko Security Framework</h1>
<p align="center">
    A production-grade, multi-mode offensive security framework written in Python.<br>
    Built for scale, speed, and real-world penetration testing.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://img.shields.io/badge/Version-2.1.0-red.svg">
  <img src="https://img.shields.io/badge/Status-Production--Grade-green.svg">
</p>

---

## 🔧 Features

Neko v2.1.0 is a complete redesign focused on modularity and performance:

- 📡 **Core**: High-performance Netcat logic with interactive shell and file transfer.
- 🔍 **Recon**: Multi-threaded port scanner with banner grabbing and DNS enumeration.
- 🕵️ **Search**: CVE lookup (NVD API) with CVSS scores and Severity ratings. Shodan integration.
- 🧨 **Exploit**: Non-blocking HTTP payload server with real-time victim logging.
- ⚔️ **Attack**: Stress testing (TCP/UDP flood) with real-time PPS stats and brute-force.
- 🧩 **Plugin System**: Dynamically load your own security modules.
- ⚙️ **Configurable**: Global settings managed in `~/.neko/config.json`.
- 📊 **Reporting**: Structured JSON and CSV exports for all scan data.

---

## 📦 Installation

### 🐍 Recommended: Using `pipx` (Global Access)

```bash
# Clone and install globally
git clone https://github.com/kanishkraj-ops/Neko.git
cd neko
pipx install .
```

### 🔨 Development: Using `pip`

```bash
pip install -e .
```

✅ Once installed, you can simply run `neko` from any directory.

---

## 🚀 Usage

Neko uses a subparser system: `neko <mode> [options]`

### 1️⃣ Recon Mode
```bash
# Fast port scan with banner grabbing
neko recon -t example.com --scan-ports --range 1-1000 --threads 50
```

### 2️⃣ Search Mode
```bash
# Search for vulnerabilities with CVSS scores
neko search --cve "log4j"
```

### 3️⃣ Exploit Mode
```bash
# Start HTTP payload server with victim monitoring
neko exploit --serve --port 8080 --dir ./payloads
```

### 4️⃣ Attack Mode
```bash
# Run a 30s TCP flood with live stats
neko attack -t 192.168.1.100 --flood --port 80 --duration 30
```

---

## 📁 Project Structure

```
Neko/
├── neko/
│   ├── cli.py           # Improved CLI entry point
│   ├── core/            # Listener and network logic
│   ├── modes/           # Modular toolsets (Recon, Search, etc.)
│   ├── utils/           # Shared utilities (Logger, Config, Loader)
│   └── plugins/         # Dynamic module directory
├── pyproject.toml       # Modern packaging configuration
└── README.md
```

---

## 🛡️ Security & Safety

> [!CAUTION]
> **Neko v2.1.0 implements safety confirmation prompts for all destructive actions.**
> To bypass these prompts in automated environments, use the `--force` flag.

---

## ⚠️ Disclaimer

> [!IMPORTANT]
> This tool is developed strictly for **educational purposes** and **authorized penetration testing** only. 
> Illegal use of this tool is strictly prohibited. The authors are not responsible for any misuse.

---

## 🧠 Author

Built with passion by **Kanishk Raj** 🛠️  
[GitHub](https://github.com/kanishkraj-ops) • [LinkedIn](https://www.linkedin.com/in/kanishk-raj-841715332/) 
