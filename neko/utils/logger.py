import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme
from rich.panel import Panel

# Custom theme for security tools
custom_theme = Theme({
    "info": "cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "debug": "dim white",
    "brute": "magenta",
    "exploit": "bold blue",
    "victim": "bold bright_red"
})

console = Console(theme=custom_theme)

class NekoLogger:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.setup_logging()

    def setup_logging(self):
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)]
        )
        self.log = logging.getLogger("neko")

    def info(self, msg):
        self.log.info(f"[info]{msg}")

    def success(self, msg):
        console.print(f"[success][+] {msg}[/success]")

    def warning(self, msg):
        self.log.warning(f"[warning][!] {msg}")

    def error(self, msg, exc_info=False):
        self.log.error(f"[error][-] {msg}", exc_info=exc_info)

    def debug(self, msg):
        if self.verbose:
            self.log.debug(f"[debug][*] {msg}")

    def brute(self, msg):
        console.print(f"[brute][>] {msg}[/brute]")

    def victim(self, msg):
        console.print(Panel(f"[victim][!] {msg}[/victim]", title="VICTIM CONNECTED", border_style="red"))

    def status(self, msg):
        return console.status(msg)

# Global logger instance
_logger = None

def init_logger(verbose=False):
    global _logger
    _logger = NekoLogger(verbose)
    return _logger

def get_logger():
    global _logger
    if _logger is None:
        _logger = NekoLogger()
    return _logger
