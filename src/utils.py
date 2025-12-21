import ctypes
import os
import platform
from ctypes import wintypes

if platform.system() == 'Windows':
    os.system('')

class Colors:
    # 标准 ANSI 颜色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 高亮颜色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # 向后兼容的别名
    HEADER = BRIGHT_MAGENTA
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def get(name):
        """根据名称获取颜色代码 (不区分大小写)"""
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


def enable_vt_mode():
    # 启用 Windows 控制台的 ANSI/VT 支持，避免转义序列无效导致无法清屏
    if platform.system() != 'Windows':
        return
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            new_mode = mode.value | 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        pass
