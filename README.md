<h1 align="center">🐾 Neko CLI</h1>
<p align="center">
    A powerful Netcat-style backdoor tool written in Python.<br>
    Designed for file transfer, command execution, and remote shell access.
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
git clone https://github.com/YOUR_USERNAME/neko-cli.git
cd neko-cli
```

### 🐍 Install with `pip`

```bash
pip install .
```

✅ Now you can run `neko` from anywhere in your terminal.

---

## 🚀 Usage

Use `--help` to see all options:

```bash
neko --help
```

### 🖥️ Start Listener (Server Mode)

Start an interactive shell on your machine:

```bash
neko --listen --port 5555 --command
```

### 📡 Connect to Target (Client Mode)

Connect to the server's IP and port:

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
neko-cli/
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

This tool is developed strictly for **educational purposes** and **authorized penetration testing** only. Unauthorized access to systems or misuse of this tool is **illegal and unethical**. Use responsibly.

---

## 🧠 Author

Built with passion by [Your Name].

➡️ Contributions, issues, and stars ⭐ are always welcome!

---
