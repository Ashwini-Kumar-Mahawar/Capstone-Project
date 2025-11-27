from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "bold red"
})

console = Console(theme=custom_theme)

def log_info(msg):
    console.print(f"[info] {msg}")

def log_success(msg):
    console.print(f"[success] {msg}")

def log_warning(msg):
    console.print(f"[warning] {msg}")

def log_error(msg):
    console.print(f"[error] {msg}")
