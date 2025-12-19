import sys
import threading
try:
    from .utils import Colors
    from .settings import settings
except ImportError:
    from utils import Colors
    from settings import settings

class DisplayManager:
    def __init__(self):
        self.status = "就绪"
        self.speed = 1.0
        self.progress = (0, 0)
        self.lock = threading.Lock()
        self.hotkeys = {}

    def _c(self, name):
        """Get color code from theme settings"""
        color_name = settings.config.get('theme', {}).get(name, 'ENDC')
        return Colors.get(color_name)

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

    def _render_header(self, width, border_char):
        lines = []
        title_color = self._c('title')
        border_color = self._c('border')
        
        lines.append(f"{border_color}{border_char * width}{Colors.ENDC}")
        title = " MACRO TOOL "
        lines.append(f"{title_color}{Colors.BOLD}{title.center(width)}{Colors.ENDC}")
        lines.append(f"{border_color}{border_char * width}{Colors.ENDC}")
        return lines

    def _render_status(self, label_color):
        if "录制" in self.status:
            status_color = self._c('status_recording')
            symbol = "●"
        elif "回放" in self.status:
            status_color = self._c('status_playing')
            symbol = "▶"
        else:
            status_color = Colors.BRIGHT_WHITE
            symbol = "■"
        
        return f" {label_color}速度:{Colors.ENDC} {self.speed:>4.1f}x   {label_color}状态:{Colors.ENDC} {status_color}{symbol} {self.status}{Colors.ENDC}"

    def _render_progress(self, label_color):
        curr, total = self.progress
        if total > 0:
            percent = min(1.0, max(0.0, curr / total))
            bar_len = 25
            filled = int(bar_len * percent)
            bar = '█' * filled + '░' * (bar_len - filled)
            bar_color = self._c('progress_bar')
            return f" {label_color}进度:{Colors.ENDC} {bar_color}{bar}{Colors.ENDC} {percent:>4.0%}"
        else:
            return f" {label_color}进度:{Colors.ENDC} --"

    def _render_hotkeys(self):
        lines = []
        if self.hotkeys:
            hk = self.hotkeys
            r_key = f"[{hk.get('record', '').upper()}]"
            p_key = f"[{hk.get('play', '').upper()}]"
            su_key = f"[{hk.get('speed_up', '').upper()}]"
            sd_key = f"[{hk.get('speed_down', '').upper()}]"
            
            lines.append(f" {r_key:<13} 录制/停止    {p_key:<13} 回放/停止")
            lines.append(f" {su_key:<13} 加速         {sd_key:<13} 减速")
        else:
            lines.append("  加载中...")
        return lines

    def render(self):
        width = 50
        border_char = "="
        label_color = self._c('label')
        border_color = self._c('border')
        
        lines = []
        lines.extend(self._render_header(width, border_char))
        lines.append(self._render_status(label_color))
        lines.append(self._render_progress(label_color))
        
        lines.append(f"{border_color}{'-' * width}{Colors.ENDC}")
        lines.extend(self._render_hotkeys())
        lines.append(f"{border_color}{border_char * width}{Colors.ENDC}")

        # Move to top-left, print content, then clear rest of screen
        # \033[H moves cursor to home
        # \033[K clears to end of line (added to each line to remove artifacts)
        # \033[J clears from cursor to end of screen
        output = "\033[H" + "\n".join([line + "\033[K" for line in lines]) + "\033[J"
        sys.stdout.write(output)
        sys.stdout.flush()

display = DisplayManager()
