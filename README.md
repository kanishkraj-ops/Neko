<h1 align="center">🐾 Neko CLI</h1>
<p align="center">
    A powerful Netcat-style backdoor tool written in Python.<br>
    Designed for file transfer, command execution, and remote shell access.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
</p>

---

## 🔧 Features

- 📡 Connect to remote systems over TCP
- 💻 Remote interactive shell
- 🧨 Execute system commands
- 📁 File upload & download
- ⚙️ Cross-platform (Windows, Linux, Mac)
- 🐍 Installable as a Python CLI tool

---

## 📦 Installation

### 🔗 Clone the Repository

```bash
git clone https://github.com/kanishkraj-ops/Neko.git
cd Neko
```

### 🐍 Install with `pip` or `pipx`

```bash
# Using pip
pip install .

# Using pipx (recommended for CLI tools)
pipx install .
```

✅ Once installed, you can run `neko` from anywhere in your terminal.

---

## 🚀 Usage

Use `--help` to see all options:

```bash
neko --help
```

### 🖥️ Start Listener (Server Mode)

```bash
neko --listen --port 5555 --command
```

### 📡 Connect to Target (Client Mode)

```bash
neko --target 192.168.1.100 --port 5555
```

### 📁 Upload a File to Server

Server:

```bash
neko --listen --port 4444 --upload received.txt
```

Client:

```bash
neko --target 192.168.1.100 --port 4444 --upload myfile.txt
```

### 📥 Download a File from Server

Server:

```bash
neko --listen --port 4444 --download secret.txt
```

Client:

```bash
neko --target 192.168.1.100 --port 4444 --download save_as.txt
```

### 🧨 Execute a Command Once

Server:

```bash
neko --listen --port 6666 --execute "whoami"
```

Client:

```bash
neko --target 192.168.1.100 --port 6666
```

---

## 📁 Project Structure

```
Neko/
├── neko/
│   ├── __init__.py
│   └── cli.py
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
```

---

## ⚠️ Disclaimer

This tool is developed strictly for **educational purposes** and **authorized penetration testing** only.  
**Unauthorized use is illegal and unethical. Please use responsibly.**

---

## 🧠 Author

Built with passion by **Kanishk Raj** 🛠️  
[GitHub](https://github.com/kanishkraj-ops) • [LinkedIn](https://www.linkedin.com/in/kanishk-raj-841715332/) 

➡️ Contributions, issues, and stars ⭐ are always welcome!

---

