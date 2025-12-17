import sys
import threading
import time
from .utils import Colors

class DisplayManager:
    def __init__(self):
        self.status = "就绪"
        self.speed = 1.0
        self.progress = (0, 0)
        self.logs = []
        self.lock = threading.Lock()
        self.hotkeys = {}

    def set_hotkeys(self, hotkeys):
        self.hotkeys = hotkeys

    def update_status(self, status):
        with self.lock:
            self.status = status
        self.render()

    def update_speed(self, speed):
        with self.lock:
            self.speed = speed
        self.render()

    def update_progress(self, current, total):
        with self.lock:
            self.progress = (current, total)
        self.render()

    def add_log(self, message, level="INFO"):
        with self.lock:
            timestamp = time.strftime("%H:%M:%S")
            
            color = Colors.ENDC
            if level == "WARNING": color = Colors.YELLOW
            elif level == "ERROR": color = Colors.RED
            elif level == "INFO": color = Colors.GREEN
            elif level == "DEBUG": color = Colors.CYAN
            
            formatted_msg = f"{timestamp} - {color}[{level:<7}]{Colors.ENDC} - {message}"
            self.logs.append(formatted_msg)
            if len(self.logs) > 5: # Keep last 5 logs
                self.logs.pop(0)
        self.render()

    def render(self):
        lines = []
        # Title
        lines.append(f"{Colors.HEADER}{Colors.BOLD}================ 全能宏工具 (Macro Tool) ================{Colors.ENDC}")
        lines.append("")
        
        # Status & Speed
        status_color = Colors.GREEN if "录制" in self.status else (Colors.CYAN if "回放" in self.status else Colors.ENDC)
        lines.append(f"{Colors.BOLD}当前状态:{Colors.ENDC} {status_color}{self.status}{Colors.ENDC}")
        lines.append(f"{Colors.BOLD}播放速度:{Colors.ENDC} {self.speed:.1f}x")
        
        # Progress Bar
        curr, total = self.progress
        if total > 0:
            percent = curr / total
            bar_len = 40
            filled = int(bar_len * percent)
            bar = '=' * filled + '-' * (bar_len - filled)
            lines.append(f"{Colors.BOLD}回放进度:{Colors.ENDC} |{Colors.BLUE}{bar}{Colors.ENDC}| {percent:.1%} ({curr}/{total})")
        else:
            lines.append(f"{Colors.BOLD}回放进度:{Colors.ENDC} --/--")
            
        lines.append("")
        lines.append(f"{Colors.BOLD}=== 操作指南 ==={Colors.ENDC}")
        if self.hotkeys:
            hk = self.hotkeys
            # Format hotkeys nicely
            keys_info = [
                f"[{hk.get('record', '').upper()}] 录制",
                f"[{hk.get('play', '').upper()}] 回放",
                f"[{hk.get('speed_up', '').upper()}] 加速",
                f"[{hk.get('speed_down', '').upper()}] 减速"
            ]
            lines.append(" | ".join(keys_info))
        else:
            lines.append("加载中...")
            
        lines.append(f"{Colors.HEADER}======================================================={Colors.ENDC}")

        # Clear screen and move to top
        # \033[2J clears screen, \033[H moves cursor to top-left
        output = "\033[2J\033[H" + "\n".join(lines)
        sys.stdout.write(output)
        sys.stdout.flush()

display = DisplayManager()
