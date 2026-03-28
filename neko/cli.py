import argparse
import sys
import textwrap
import os
from .utils.logger import init_logger, get_logger, console
from .core import NekoCore
from .modes.recon import ReconMode
from .modes.search import SearchMode
from .modes.exploit import ExploitMode
from .modes.attack import AttackMode

DISCLAIMER = """
[bold red]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!![/bold red]
[bold white]NEKO OFFENSIVE SECURITY FRAMEWORK[/bold white]
[bold yellow]Disclaimer: For authorized educational and testing use only.[/bold yellow]
[bold yellow]Illegal use of this tool is strictly prohibited.[/bold yellow]
[bold yellow]The authors are not responsible for any misuse.[/bold yellow]
[bold red]!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!![/bold red]
"""

def print_banner():
    banner = r"""
 [bold cyan]
  _   _      _         
 | \ | | ___| | _____  
 |  \| |/ _ \ |/ / _ \ 
 | |\  |  __/   < (_) |
 |_| \_|\___|_|\_\___/ 
                       
  [v2.0.0] - Multi-mode Security Framework
 [/bold cyan]
    """
    console.print(banner)
    console.print(DISCLAIMER)

def setup_args():
    parser = argparse.ArgumentParser(
        prog="neko",
        description='Neko: Multi-mode Security Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-o', '--output', help='Save results to file (JSON/CSV)')
    
    subparsers = parser.add_subparsers(dest='mode', help='Operating mode')

    # --- NETCAT MODE (Default/Legacy) ---
    nc_parser = subparsers.add_parser('core', help='Netcat-style core logic (default)')
    nc_parser.add_argument('-c', '--command', action='store_true', help='Command shell')
    nc_parser.add_argument('-e', '--execute', help='Execute a command on connection')
    nc_parser.add_argument('-l', '--listen', action='store_true', help='Listen for incoming connections')
    nc_parser.add_argument('-p', '--port', type=int, default=5555, help='Target port')
    nc_parser.add_argument('-t', '--target', default='0.0.0.0', help='Target IP')
    nc_parser.add_argument('-u', '--upload', help='Upload file to server')
    nc_parser.add_argument('-d', '--download', help='Download file from server')

    # --- RECON MODE ---
    recon_parser = subparsers.add_parser('recon', help='Network reconnaissance')
    recon_parser.add_argument('-t', '--target', required=True, help='Target IP/Domain/Subnet')
    recon_parser.add_argument('--scan-ports', action='store_true', help='Perform port scan')
    recon_parser.add_argument('--range', default='1-1024', help='Port range (e.g. 1-1024)')
    recon_parser.add_argument('--dns', action='store_true', help='DNS enumeration')
    recon_parser.add_argument('--whois', action='store_true', help='WHOIS lookup')
    recon_parser.add_argument('--ping-sweep', action='store_true', help='Subnet host discovery')

    # --- SEARCH MODE ---
    search_parser = subparsers.add_parser('search', help='OSINT and CVE searching')
    search_parser.add_argument('-t', '--target', help='Target IP/Domain')
    search_parser.add_argument('--cve', help='Search CVEs by product/keyword')
    search_parser.add_argument('--shodan', action='store_true', help='Search Shodan')
    search_parser.add_argument('--api-key', help='API key for Shodan/NVD')
    search_parser.add_argument('--dorks', action='store_true', help='Generate Google Dorks')
    search_parser.add_argument('--subdomains', action='store_true', help='Subdomain enumeration')
    search_parser.add_argument('--wordlist', help='Wordlist path')

    # --- EXPLOIT MODE ---
    exploit_parser = subparsers.add_parser('exploit', help='Exploitation aids')
    exploit_parser.add_argument('--revshell', action='store_true', help='Generate reverse shell payload')
    exploit_parser.add_argument('--lhost', help='Local host for reverse shell')
    exploit_parser.add_argument('--lport', type=int, default=4444, help='Local port for reverse shell')
    exploit_parser.add_argument('--type', choices=['bash', 'python', 'php', 'powershell'], default='bash', help='Payload type')
    exploit_parser.add_argument('--encode', choices=['b64', 'url', 'xor'], help='Payload encoding')
    exploit_parser.add_argument('--key', default='neko', help='XOR key')
    exploit_parser.add_argument('--serve', action='store_true', help='Start HTTP payload server')
    exploit_parser.add_argument('--dir', default='.', help='Directory to serve')
    exploit_parser.add_argument('--port', type=int, default=8080, help='Port for HTTP server/C2 listener')
    exploit_parser.add_argument('--c2', action='store_true', help='Start C2 listener')

    # --- ATTACK MODE ---
    attack_parser = subparsers.add_parser('attack', help='Active attacks and brute-force')
    attack_parser.add_argument('-t', '--target', required=True, help='Target URL/IP/Domain')
    attack_parser.add_argument('--flood', action='store_true', help='Network flooding')
    attack_parser.add_argument('--protocol', choices=['tcp', 'udp'], default='tcp', help='Flooding protocol')
    attack_parser.add_argument('--duration', type=int, default=10, help='Flood duration (seconds)')
    attack_parser.add_argument('--port', type=int, help='Target port')
    attack_parser.add_argument('--bruteforce', choices=['ssh', 'http'], help='Brute-force login')
    attack_parser.add_argument('--user', default='root', help='Username for brute-force')
    attack_parser.add_argument('--wordlist', help='Wordlist path')
    attack_parser.add_argument('--dirbrute', action='store_true', help='HTTP directory brute-force')
    attack_parser.add_argument('--takeover', action='store_true', help='Subdomain takeover check')

    return parser

def main():
    parser = setup_args()
    
    # Handle legacy behavior if no mode provided (compatible with netcat-style)
    # If first arg starts with -t, -p, -l etc, assume 'core' mode
    args_list = sys.argv[1:]
    if args_list and (args_list[0].startswith('-') and args_list[0] not in ['-v', '--verbose', '-o', '--output', '-h', '--help']):
        args_list = ['core'] + args_list
    
    args = parser.parse_args(args_list)
    
    init_logger(args.verbose)
    logger = get_logger()
    
    print_banner()

    if not args.mode:
        parser.print_help()
        sys.exit(0)

    try:
        if args.mode == 'core':
            # Handle stdin for legacy Neko send mode
            buffer = ''
            if not args.listen:
                if not sys.stdin.isatty():
                    buffer = sys.stdin.read()
            nk = NekoCore(args, buffer.encode() if buffer else None)
            nk.run()
        elif args.mode == 'recon':
            rm = ReconMode(args)
            rm.run()
        elif args.mode == 'search':
            sm = SearchMode(args)
            sm.run()
        elif args.mode == 'exploit':
            em = ExploitMode(args)
            em.run()
        elif args.mode == 'attack':
            am = AttackMode(args)
            am.run()
    except KeyboardInterrupt:
        logger.warning("\nUser interrupted execution. Exiting...")
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
