import requests
import json
import time
import os
from ..utils.logger import get_logger
from ..utils.reporter import NekoReporter

try:
    import shodan
except ImportError:
    shodan = None

logger = get_logger()

class SearchMode:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.reporter = NekoReporter(args.output) if args.output else None

    def run(self):
        logger.info(f"Starting search mode...")
        
        if getattr(self.args, 'cve', False):
            self.search_cve()
            
        if getattr(self.args, 'shodan', False):
            self.search_shodan()
            
        if getattr(self.args, 'dorks', False):
            self.generate_dorks()
            
        if getattr(self.args, 'subdomains', False):
            self.subdomain_enum()

        if self.reporter:
            self.reporter.report(self.results)

    def search_cve(self):
        query = self.args.cve
        logger.info(f"Searching CVEs for: {query}")
        # Using NVD API v2 (requires API key for better rate limits, but works without)
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                logger.success(f"Found {len(vulnerabilities)} vulnerabilities.")
                
                cve_data = []
                for v in vulnerabilities[:10]: # Limit to top 10
                    cve_id = v['cve']['id']
                    description = v['cve']['descriptions'][0]['value'][:100] + "..."
                    logger.success(f"{cve_id}: {description}")
                    cve_data.append({"id": cve_id, "description": description})
                
                self.results['cves'] = cve_data
            else:
                logger.error(f"NVD API returned error: {response.status_code}")
        except Exception as e:
            logger.error(f"CVE search failed: {e}")

    def search_shodan(self):
        if not shodan:
            logger.error("shodan package not installed. Use 'pip install shodan'.")
            return
            
        api_key = getattr(self.args, 'api_key', None)
        if not api_key:
            logger.error("Shodan API key is required (--api-key).")
            return
            
        api = shodan.Shodan(api_key)
        query = self.args.target
        logger.info(f"Searching Shodan for: {query}")
        
        try:
            # Check if target is IP or query
            results = api.search(query)
            logger.success(f"Total results: {results['total']}")
            
            hosts = []
            for result in results['matches'][:5]:
                host_info = {
                    "ip": result['ip_str'],
                    "port": result['port'],
                    "org": result.get('org', 'N/A'),
                    "os": result.get('os', 'N/A')
                }
                logger.success(f"HOST: {host_info['ip']}:{host_info['port']} ({host_info['org']})")
                hosts.append(host_info)
            self.results['shodan'] = hosts
        except Exception as e:
            logger.error(f"Shodan search failed: {e}")

    def generate_dorks(self):
        target = self.args.target
        logger.info(f"Generating Google Dorks for: {target}")
        
        dorks = [
            f"site:{target} filetype:pdf",
            f"site:{target} intitle:index.of",
            f"site:{target} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini",
            f"site:{target} inurl:login",
            f"site:{target} intext:\"sql syntax near\"",
            f"site:{target} inurl:phpinfo.php",
            f"site:{target} inurl:\"/phpmyadmin/index.php\""
        ]
        
        for dork in dorks:
            logger.success(f"DORK: {dork}")
            
        self.results['dorks'] = dorks

    def subdomain_enum(self):
        target = self.args.target
        wordlist_path = getattr(self.args, 'wordlist', None)
        
        if not wordlist_path or not os.path.exists(wordlist_path):
            logger.warning("No valid wordlist provided for subdomain enumeration. Using basic common list.")
            subdomains = ['www', 'dev', 'staging', 'mail', 'api', 'test', 'vpn', 'remote', 'blog', 'admin']
        else:
            with open(wordlist_path, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]

        logger.info(f"Enumerating subdomains for {target} using {len(subdomains)} words...")
        
        found = []
        for sub in subdomains:
            full_domain = f"{sub}.{target}"
            try:
                ip = socket.gethostbyname(full_domain)
                logger.success(f"Found: {full_domain} -> {ip}")
                found.append({"domain": full_domain, "ip": ip})
            except:
                continue
                
        self.results['subdomains'] = found
        logger.info(f"Subdomain enumeration complete. Found {len(found)} subdomains.")
import socket
