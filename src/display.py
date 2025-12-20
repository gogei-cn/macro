import sys
import threading
import re
import unicodedata

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
        """从主题设置获取颜色代码"""
        color_name = settings.config.get('theme', {}).get(name, 'ENDC')
        return Colors.get(color_name)

    def _visible_len(self, s):
        """计算去除 ANSI 转义码后的字符串视觉长度 (支持中文字符)"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', s)
        length = 0
        for char in text:
            # 'W' (Wide) 和 'F' (Fullwidth) 是 2
            # 'A' (Ambiguous) 通常在终端中显示为 1，除非特殊配置
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                length += 2
            else:
                length += 1
        return length

    def _pad_text(self, text, width, align='left'):
        """支持宽字符的文本填充"""
        v_len = self._visible_len(text)
        padding = max(0, width - v_len)
        if align == 'center':
            left = padding // 2
            right = padding - left
            return " " * left + text + " " * right
        elif align == 'right':
            return " " * padding + text
        else: # left
            return text + " " * padding

    def _center_text(self, text, width):
        """居中包含颜色代码的文本"""
        return self._pad_text(text, width, 'center')

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

    def render(self):
        width = 54  # 增加宽度以容纳长按键名
        # Box characters
        TL, TR, BL, BR = '╭', '╮', '╰', '╯'
        H, V = '─', '│'
        M_L, M_R = '├', '┤'
        
        border_color = self._c('border')
        title_color = self._c('title')
        label_color = self._c('label')
        
        lines = []
        
        # 1. Top Border
        lines.append(f"{border_color}{TL}{H * (width - 2)}{TR}{Colors.ENDC}")
        
        # 2. Title
        title = "MACRO TOOL"
        styled_title = f"{title_color}{Colors.BOLD}{title}{Colors.ENDC}"
        lines.append(f"{border_color}{V}{Colors.ENDC}{self._center_text(styled_title, width - 2)}{border_color}{V}{Colors.ENDC}")
        
        # 3. Separator
        lines.append(f"{border_color}{M_L}{H * (width - 2)}{M_R}{Colors.ENDC}")
        
        # 4. Status & Speed
        if "录制" in self.status:
            status_color = self._c('status_recording')
            symbol = "●"
        elif "回放" in self.status:
            status_color = self._c('status_playing')
            symbol = "▶"
        else:
            status_color = Colors.BRIGHT_WHITE
            symbol = "■"
            
        status_text = f"{label_color}状态:{Colors.ENDC} {status_color}{symbol} {self.status}{Colors.ENDC}"
        speed_text = f"{label_color}速度:{Colors.ENDC} {self.speed:>3.1f}x"
        
        # Combine status and speed on one line with spacing
        # Layout:  │  Status: ● Recording       Speed: 1.0x   │
        content_width = width - 4 # 2 chars padding + 2 borders
        
        # Simple layout: Left aligned Status, Right aligned Speed
        # But we need to calculate padding manually
        s_len = self._visible_len(status_text)
        sp_len = self._visible_len(speed_text)
        gap = content_width - s_len - sp_len
        
        if gap > 0:
            line_content = f" {status_text}{' ' * gap}{speed_text} "
        else:
            line_content = f" {status_text} {speed_text} " # Fallback
            
        lines.append(f"{border_color}{V}{Colors.ENDC}{line_content}{border_color}{V}{Colors.ENDC}")
        
        # 5. Empty line
        lines.append(f"{border_color}{V}{' ' * (width - 2)}{V}{Colors.ENDC}")

        # 6. Progress Bar
        curr, total = self.progress
        if total > 0:
            percent = min(1.0, max(0.0, curr / total))
            bar_len = width - 14 # Adjust for label and percentage
            filled = int(bar_len * percent)
            # Use a cleaner track for empty part
            bar = '█' * filled + '━' * (bar_len - filled)
            bar_color = self._c('progress_bar')
            # Use bright black for the empty track
            empty_color = Colors.BRIGHT_BLACK
            
            # Construct bar with colors
            colored_bar = f"{bar_color}{'█' * filled}{Colors.ENDC}{empty_color}{'━' * (bar_len - filled)}{Colors.ENDC}"
            
            prog_text = f"{label_color}进度:{Colors.ENDC} {colored_bar} {int(percent*100):>3}%"
        else:
            prog_text = f"{label_color}进度:{Colors.ENDC} --"
            
        lines.append(f"{border_color}{V}{Colors.ENDC}{self._pad_text(' ' + prog_text, width - 2)}{border_color}{V}{Colors.ENDC}")

        # 7. Separator
        lines.append(f"{border_color}{M_L}{H * (width - 2)}{M_R}{Colors.ENDC}")

        # 8. Hotkeys
        if self.hotkeys:
            hk = self.hotkeys
            # Helper to format key-desc pair
            def fmt_pair(k, d):
                key_str = f"[{k.upper()}]"
                # Key: 14 chars (enough for PRINT_SCREEN), Desc: 10 chars
                # Total 25 chars (14 + 1 + 10)
                return f"{self._pad_text(key_str, 14)} {self._pad_text(d, 10)}"

            # Row 1
            pair1 = fmt_pair(hk.get('record', ''), "录制/停止")
            pair2 = fmt_pair(hk.get('play', ''), "回放/停止")
            
            # Width 54 -> Inner 52
            # " " + pair1 (25) + " " + pair2 (25) + " " = 52 chars? No, 1+25+1+25 = 52.
            # So we need exactly 1 space padding between and around.
            
            row1 = f" {pair1} {pair2}" 
            row1 = self._pad_text(row1, width - 2)
            lines.append(f"{border_color}{V}{Colors.ENDC}{row1}{border_color}{V}{Colors.ENDC}")
            
            # Row 2
            pair3 = fmt_pair(hk.get('speed_up', ''), "加速")
            pair4 = fmt_pair(hk.get('speed_down', ''), "减速")
            
            row2 = f" {pair3} {pair4}"
            row2 = self._pad_text(row2, width - 2)
            lines.append(f"{border_color}{V}{Colors.ENDC}{row2}{border_color}{V}{Colors.ENDC}")
        else:
            lines.append(f"{border_color}{V}{Colors.ENDC}{self._center_text('加载中...', width - 2)}{border_color}{V}{Colors.ENDC}")

        # 9. Footer (Ctrl+C)
        lines.append(f"{border_color}{M_L}{H * (width - 2)}{M_R}{Colors.ENDC}")
        footer_text = f"{Colors.BRIGHT_BLACK}Ctrl+C 退出{Colors.ENDC}"
        lines.append(f"{border_color}{V}{Colors.ENDC}{self._center_text(footer_text, width - 2)}{border_color}{V}{Colors.ENDC}")

        # 10. Bottom Border
        lines.append(f"{border_color}{BL}{H * (width - 2)}{BR}{Colors.ENDC}")

        # Output
        output = "\033[H" + "\n".join([line + "\033[K" for line in lines]) + "\033[J"
        sys.stdout.write(output)
        sys.stdout.flush()

display = DisplayManager()
