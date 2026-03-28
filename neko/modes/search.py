import requests
import json
import time
import os
import socket
from ..utils.logger import get_logger
from ..utils.reporter import NekoReporter
from ..utils.config import get_config

try:
    import shodan
except ImportError:
    shodan = None

logger = get_logger()
config = get_config()

class SearchMode:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.reporter = NekoReporter(args.output) if args.output else None
        self.api_key = getattr(self.args, 'api_key', config.get('api_keys', {}).get('shodan', ""))

    def run(self):
        logger.info(f"Starting Search mode...")
        
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
        logger.info(f"Searching NVD for CVEs related to: {query}")
        # Using NVD API v2
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={query}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])
                logger.success(f"Found {len(vulnerabilities)} vulnerabilities.")
                
                cve_data = []
                for v in vulnerabilities[:10]: # Top 10 results
                    cve = v['cve']
                    cve_id = cve['id']
                    desc = cve['descriptions'][0]['value']
                    
                    # Extraction of CVSS and Severity data
                    metrics = cve.get('metrics', {})
                    cvss_v3 = metrics.get('cvssMetricV31', metrics.get('cvssMetricV30', []))
                    
                    score = "N/A"
                    severity = "UNKNOWN"
                    
                    if cvss_v3:
                        score = cvss_v3[0]['cvssData']['baseScore']
                        severity = cvss_v3[0]['cvssData']['baseSeverity']
                    
                    # Color coding severity
                    sev_color = "white"
                    if severity == "HIGH": sev_color = "bold red"
                    elif severity == "CRITICAL": sev_color = "bold bright_red"
                    elif severity == "MEDIUM": sev_color = "yellow"
                    elif severity == "LOW": sev_color = "green"
                    
                    logger.success(f"[{cve_id}] Score: {score} | Severity: [{sev_color}]{severity}[/{sev_color}]")
                    logger.debug(f"Description: {desc[:100]}...")
                    
                    cve_data.append({
                        "id": cve_id,
                        "score": score,
                        "severity": severity,
                        "description": desc
                    })
                
                self.results['cves'] = cve_data
            else:
                logger.error(f"NVD API error Code {response.status_code}")
        except Exception as e:
            logger.error(f"CVE search failed: {e}")

    def search_shodan(self):
        if not shodan:
            logger.warning("shodan package not installed. 'pip install shodan'.")
            return
            
        if not self.api_key:
            logger.error("Shodan API key is required (--api-key or ~/.neko/config.json).")
            return
            
        api = shodan.Shodan(self.api_key)
        query = self.args.target
        logger.info(f"Querying Shodan for: {query}")
        
        try:
            results = api.search(query)
            logger.success(f"Total results: {results['total']}")
            
            hosts = []
            for result in results['matches'][:5]:
                host_info = {
                    "ip": result['ip_str'],
                    "port": result['port'],
                    "org": result.get('org', 'N/A'),
                    "os": result.get('os', 'N/A'),
                    "location": f"{result['location']['city']}, {result['location']['country_name']}"
                }
                logger.success(f"IP: {host_info['ip']}:{host_info['port']} | Org: {host_info['org']} | Location: {host_info['location']}")
                hosts.append(host_info)
            self.results['shodan'] = hosts
        except shodan.APIError as e:
            logger.error(f"Shodan API Error: {e}")
        except Exception as e:
            logger.error(f"Shodan search failed: {e}")

    def generate_dorks(self):
        target = self.args.target
        logger.info(f"Generating optimized Google Dorks for {target}...")
        
        # Array of useful Google Dorks for reconnaissance
        dorks = [
            f"site:{target} ext:php | ext:aspx | ext:jsp",
            f"site:{target} intitle:index.of",
            f"site:{target} inurl:admin | inurl:login",
            f"site:{target} ext:pdf | ext:doc | ext:docx | ext:xls | ext:xlsx",
            f"site:{target} \"sql syntax near\"",
            f"site:{target} intext:\"password\" | intext:\"username\" | intext:\"credential\"",
            f"site:{target} \"PHP Parse error\" | \"PHP Warning\" | \"Fatal error\""
        ]
        
        for dork in dorks:
            logger.success(f"DORK: {dork}")
            
        self.results['dorks'] = dorks

    def subdomain_enum(self):
        target = self.args.target
        wordlist_path = getattr(self.args, 'wordlist', None)
        
        # Load subdomains wordlist
        if not wordlist_path or not os.path.exists(wordlist_path):
            subdomains = ['www', 'dev', 'beta', 'mail', 'api', 'staff', 'admin', 'portal', 'vpn', 'remote']
            logger.warning("No valid wordlist provided. Using minimal default common list.")
        else:
            with open(wordlist_path, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]

        logger.info(f"Scanning {len(subdomains)} subdomains for {target}...")
        
        found_subs = []
        for sub in subdomains:
            full_domain = f"{sub}.{target}"
            try:
                ip = socket.gethostbyname(full_domain)
                logger.success(f"Subdomain FOUND: {full_domain} -> {ip}")
                found_subs.append({"domain": full_domain, "ip": ip})
            except socket.gaierror:
                continue
            except Exception as e:
                logger.debug(f"Error resolving {full_domain}: {e}")
                continue
                
        self.results['subdomains'] = found_subs
        logger.info(f"Scan complete. Found {len(found_subs)} subdomains.")
