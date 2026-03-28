import argparse
import sys
import textwrap
import os
from .utils.logger import init_logger, get_logger, console
from .utils.config import get_config
from .utils.plugin_loader import get_plugin_loader
from .core.listener import NekoCore
from .modes.recon import ReconMode
from .modes.search import SearchMode
from .modes.exploit import ExploitMode
from .modes.attack import AttackMode

# Application Metadata
__version__ = "2.1.0"
__author__ = "Kanishk"

BANNER = r"""
 [bold cyan]
  _   _      _         
 | \ | | ___| | _____  
 |  \| |/ _ \ |/ / _ \ 
 | |\  |  __/   < (_) |
 |_| \_|\___|_|\_\___/ 
                       
  [v{0}] - Production-Grade Security Framework
 [/bold cyan]
""".format(__version__)

DISCLAIMER = """
[bold red]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!![/bold red]
[bold white]NEKO OFFENSIVE SECURITY FRAMEWORK[/bold white]
[bold yellow]Disclaimer: For authorized educational and testing use only.[/bold yellow]
[bold yellow]Illegal use of this tool is strictly prohibited.[/bold yellow]
[bold yellow]The authors are not responsible for any misuse.[/bold yellow]
[bold red]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!![/bold red]
"""

class NekoCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="neko",
            description='Neko: Production-Grade Security Framework',
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        self.config = get_config()
        self.setup_args()

    def setup_args(self):
        # Global Flags
        self.parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        self.parser.add_argument('-o', '--output', help='Save results to file (JSON/CSV)')
        self.parser.add_argument('--force', action='store_true', help='Skip safety confirmation prompts')
        self.parser.add_argument('--version', action='version', version=f'Neko v{__version__}')
        
        subparsers = self.parser.add_subparsers(dest='mode', help='Operating mode', required=True)

        # --- RECON MODE ---
        recon = subparsers.add_parser('recon', help='Network reconnaissance (Port scan, DNS, WHOIS)')
        recon.add_argument('-t', '--target', required=True, help='Target IP/Domain/Subnet')
        recon.add_argument('--scan-ports', action='store_true', help='Perform port scan')
        recon.add_argument('--range', default='1-1024', help='Port range (e.g. 1-1024)')
        recon.add_argument('--threads', type=int, help='Concurrent scan threads')
        recon.add_argument('--dns', action='store_true', help='DNS enumeration')
        recon.add_argument('--whois', action='store_true', help='WHOIS lookup')
        recon.add_argument('--ping-sweep', action='store_true', help='Subnet host discovery')

        # --- SEARCH MODE ---
        search = subparsers.add_parser('search', help='OSINT and CVE searching')
        search.add_argument('-t', '--target', help='Target IP/Domain')
        search.add_argument('--cve', help='Search CVEs by product/keyword')
        search.add_argument('--shodan', action='store_true', help='Search Shodan')
        search.add_argument('--api-key', help='Shodan API key (overrides config)')
        search.add_argument('--dorks', action='store_true', help='Generate Google Dorks')
        search.add_argument('--subdomains', action='store_true', help='Subdomain enumeration')
        search.add_argument('--wordlist', help='Subdomain wordlist path')

        # --- EXPLOIT MODE ---
        exploit = subparsers.add_parser('exploit', help='Exploitation aids & C2')
        exploit.add_argument('--revshell', action='store_true', help='Generate reverse shell payload')
        exploit.add_argument('--lhost', help='Local host for reverse shell')
        exploit.add_argument('--lport', type=int, help='Local port for reverse shell')
        exploit.add_argument('--type', choices=['bash', 'python', 'php', 'powershell'], default='bash', help='Payload type')
        exploit.add_argument('--encode', choices=['b64', 'url', 'xor'], help='Payload encoding')
        exploit.add_argument('--key', default='neko', help='XOR key')
        exploit.add_argument('--serve', action='store_true', help='Start non-blocking HTTP payload server')
        exploit.add_argument('--dir', default='.', help='Directory to serve')
        exploit.add_argument('--port', type=int, default=8080, help='Port for HTTP server/C2')
        exploit.add_argument('--c2', action='store_true', help='Start C2 listener')

        # --- ATTACK MODE ---
        attack = subparsers.add_parser('attack', help='Active attacks and brute-force (Safety prompts enabled)')
        attack.add_argument('-t', '--target', required=True, help='Target URL/IP/Domain')
        attack.add_argument('--flood', action='store_true', help='Network flooding (Stress test)')
        attack.add_argument('--protocol', choices=['tcp', 'udp'], default='tcp', help='Flooding protocol')
        attack.add_argument('--duration', type=int, default=10, help='Flood duration (seconds)')
        attack.add_argument('--port', type=int, help='Target port')
        attack.add_argument('--bruteforce', choices=['ssh', 'http'], help='Brute-force login')
        attack.add_argument('--user', default='root', help='Username for brute-force')
        attack.add_argument('--wordlist', help='Wordlist path')
        attack.add_argument('--dirbrute', action='store_true', help='HTTP directory brute-force')
        attack.add_argument('--takeover', action='store_true', help='Subdomain takeover check')

        # --- CORE / LEGACY MODE ---
        core = subparsers.add_parser('core', help='Netcat-style listener and client')
        core.add_argument('-c', '--command', action='store_true', help='Command shell')
        core.add_argument('-e', '--execute', help='Execute a command on connection')
        core.add_argument('-l', '--listen', action='store_true', help='Listen for incoming connections')
        core.add_argument('-p', '--port', type=int, default=5555, help='Target port')
        core.add_argument('-t', '--target', default='0.0.0.0', help='Target IP (client mode only)')
        core.add_argument('-u', '--upload', help='Upload file to server')
        core.add_argument('-d', '--download', help='Download file from server')

    def run(self):
        # Support legacy argument order (neko -t ... -> neko core -t ...)
        args_list = sys.argv[1:]
        if args_list and (args_list[0].startswith('-') and args_list[0] not in ['-v', '--verbose', '-o', '--output', '--force', '-h', '--help', '--version']):
            args_list = ['core'] + args_list
        
        args = self.parser.parse_args(args_list)
        
        # Initialize Logger
        logger = init_logger(args.verbose)
        
        # Print Banner & Disclaimer
        console.print(BANNER)
        console.print(DISCLAIMER)

        try:
            if args.mode == 'core':
                buffer = ''
                if not args.listen and not sys.stdin.isatty():
                    buffer = sys.stdin.read()
                nk = NekoCore(args, buffer.encode() if buffer else None)
                nk.run()
            elif args.mode == 'recon':
                ReconMode(args).run()
            elif args.mode == 'search':
                SearchMode(args).run()
            elif args.mode == 'exploit':
                ExploitMode(args).run()
            elif args.mode == 'attack':
                AttackMode(args).run()
        except KeyboardInterrupt:
            logger.warning("\nUser interrupted execution. Exiting...")
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()

def main():
    cli = NekoCLI()
    cli.run()

if __name__ == '__main__':
    main()
