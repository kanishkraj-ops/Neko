import socket
import threading
import sys
import os
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor
from ..utils.logger import get_logger
from ..utils.reporter import NekoReporter

try:
    import dns.resolver
except ImportError:
    dns = None

try:
    import whois
except ImportError:
    whois = None

logger = get_logger()

class ReconMode:
    def __init__(self, args):
        self.args = args
        self.results = {}
        self.reporter = NekoReporter(args.output) if args.output else None

    def run(self):
        logger.info(f"Starting reconnaissance on {self.args.target}")
        
        if getattr(self.args, 'scan_ports', False):
            self.port_scan()
            
        if getattr(self.args, 'dns', False):
            self.dns_enum()
            
        if getattr(self.args, 'whois', False):
            self.whois_lookup()
            
        if getattr(self.args, 'ping_sweep', False):
            self.ping_sweep()

        if self.reporter:
            self.reporter.report(self.results)
        
        self.print_summary()

    def port_scan(self):
        target = self.args.target
        port_range = getattr(self.args, 'range', '1-1024')
        try:
            start_port, end_port = map(int, port_range.split('-'))
        except ValueError:
            logger.error("Invalid port range format. Use e.g. 1-1024")
            return

        logger.info(f"Scanning ports {start_port}-{end_port} on {target}...")
        open_ports = []
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(self._scan_single_port, target, port) for port in range(start_port, end_port + 1)]
            for future in futures:
                result = future.result()
                if result:
                    open_ports.append(result)
        
        self.results['ports'] = open_ports
        for p in open_ports:
            logger.success(f"Port {p['port']}/tcp OPEN ({p['service']}) - Banner: {p['banner']}")

    def _scan_single_port(self, target, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                if s.connect_ex((target, port)) == 0:
                    banner = ""
                    try:
                        # Attempt banner grabbing
                        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                        banner = s.recv(1024).decode(errors='ignore').strip().replace('\n', ' ')[:50]
                    except:
                        pass
                    
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "unknown"
                        
                    return {
                        "port": port,
                        "status": "open",
                        "service": service,
                        "banner": banner
                    }
        except:
            pass
        return None

    def dns_enum(self):
        if not dns:
            logger.error("dnspython is not installed. Use 'pip install dnspython' for DNS enumeration.")
            return

        target = self.args.target
        logger.info(f"Enumerating DNS for {target}...")
        dns_results = {}
        
        record_types = ['A', 'MX', 'NS', 'CNAME', 'TXT']
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(target, rtype)
                dns_results[rtype] = [str(rdata) for rdata in answers]
                for rdata in dns_results[rtype]:
                    logger.success(f"DNS {rtype}: {rdata}")
            except:
                continue
        
        self.results['dns'] = dns_results

    def whois_lookup(self):
        if not whois:
             logger.error("whois is not installed. Use 'pip install python-whois' for WHOIS lookup.")
             return
             
        target = self.args.target
        logger.info(f"Performing WHOIS lookup for {target}...")
        try:
            w = whois.whois(target)
            # Convert to dict for reporting
            whois_data = {
                "domain_name": str(w.domain_name),
                "registrar": str(w.registrar),
                "creation_date": str(w.creation_date),
                "expiration_date": str(w.expiration_date),
                "emails": str(w.emails)
            }
            self.results['whois'] = whois_data
            logger.success(f"Registrar: {whois_data['registrar']}")
            logger.success(f"Creation: {whois_data['creation_date']}")
        except Exception as e:
            logger.error(f"WHOIS lookup failed: {e}")

    def ping_sweep(self):
        target_network = self.args.target
        logger.info(f"Performing ping sweep on {target_network}...")
        # Basic implementation for CIDR or range
        # For simplicity, we'll assume target is a single IP or user knows what they are doing
        # A full ping sweep implementation usually requires ipaddress module and ICMP
        # Here we'll just check the single target or provide a placeholder for subnet logic
        if '/' in target_network:
             logger.warning("Subnet sweep requested. This might take a while...")
             # In a real tool, we'd iterate over the subnet.
             # For this demo, let's just ping the target.
        
        is_windows = os.name == 'nt'
        ping_cmd = ["ping", "-n" if is_windows else "-c", "1", "-w", "1000", target_network]
        
        try:
            res = subprocess.call(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res == 0:
                logger.success(f"Host {target_network} is UP")
                self.results['ping'] = {"status": "up"}
            else:
                logger.warning(f"Host {target_network} is DOWN or blocking ICMP")
                self.results['ping'] = {"status": "down"}
        except Exception as e:
            logger.error(f"Ping sweep error: {e}")

    def print_summary(self):
        logger.info("--- Recon Summary ---")
        if 'ports' in self.results:
            logger.info(f"Open Ports: {len(self.results['ports'])}")
        if 'dns' in self.results:
            logger.info(f"DNS Records found: {sum(len(v) for v in self.results['dns'].values())}")
        if 'whois' in self.results:
            logger.info("WHOIS data retrieved.")
