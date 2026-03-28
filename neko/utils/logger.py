import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme

# Custom theme for security tools
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "debug": "dim white",
    "brute": "magenta",
    "exploit": "bold blue"
})

console = Console(theme=custom_theme)

class NekoLogger:
    def __init__(self, verbose=False):
        self.verbose = verbose
        level = logging.DEBUG if verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
        )
        self.log = logging.getLogger("neko")

    def info(self, msg):
        self.log.info(f"[info] {msg}")

    def success(self, msg):
        console.print(f"[success][+] {msg}[/success]")

    def warning(self, msg):
        self.log.warning(f"[warning][!] {msg}")

    def error(self, msg):
        self.log.error(f"[error][-] {msg}")

    def debug(self, msg):
        if self.verbose:
            self.log.debug(f"[debug][*] {msg}")

    def brute(self, msg):
        console.print(f"[brute][>] {msg}[/brute]")

    def status(self, msg):
        return console.status(msg)

# Global logger instance (will be initialized in cli.py)
logger = None

def init_logger(verbose=False):
    global logger
    logger = NekoLogger(verbose)
    return logger

def get_logger():
    global logger
    if logger is None:
        logger = NekoLogger()
    return logger
