import ctypes
import os
import platform

if platform.system() == 'Windows':
    os.system('')

class Colors:
    # Standard ANSI Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # High Intensity Colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Aliases for backward compatibility
    HEADER = BRIGHT_MAGENTA
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def get(name):
        """Get color code by name (case-insensitive)"""
        if not isinstance(name, str):
            return Colors.ENDC
        return getattr(Colors, name.upper(), Colors.ENDC)

def setup_dpi_awareness():
    if platform.system() == 'Windows':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
