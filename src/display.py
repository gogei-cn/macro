import sys
import threading
import re
import unicodedata

try:
    from .utils import Colors
    from .settings import settings
    from .i18n import t
except ImportError:
    from utils import Colors
    from settings import settings
    from i18n import t

class DisplayManager:
    def __init__(self):
        self.status = t('status.ready')
        self.speed = 1.0
        self.progress = (0, 0)
        self.lock = threading.Lock()
        self.hotkeys = {}

    def _c(self, name):
        # 从主题设置获取颜色代码
        color_name = settings.config.get('theme', {}).get(name, 'ENDC')
        return Colors.get(color_name)

    def _visible_len(self, s):
        # 计算去除 ANSI 转义码后的字符串视觉长度（支持中文字符）
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        text = ansi_escape.sub('', s)
        length = 0
        for char in text:
            # 'W'（全角）和 'F'（全宽）长度为 2
            # 'A'（不确定宽度）通常在终端中显示为 1，除非特殊配置
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                length += 2
            else:
                length += 1
        return length

    def _pad_text(self, text, width, align='left'):
        # 支持宽字符的文本填充
        v_len = self._visible_len(text)
        padding = max(0, width - v_len)
        if align == 'center':
            left = padding // 2
            right = padding - left
            return " " * left + text + " " * right
        elif align == 'right':
            return " " * padding + text
        else: # 左对齐
            return text + " " * padding

    def _center_text(self, text, width):
        # 居中包含颜色代码的文本
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
        key_width = 14
        desc_candidates = [
            t('hotkey.record'),
            t('hotkey.play'),
            t('hotkey.speed_up'),
            t('hotkey.speed_down')
        ]
        desc_width = max(10, max(self._visible_len(d) for d in desc_candidates))
        pair_len = key_width + 1 + desc_width
        # 计算整体宽度，确保两组快捷键在一行内对齐
        width = max(54, 2 * pair_len + 4)
        # 边框字符
        TL, TR, BL, BR = '╭', '╮', '╰', '╯'
        H, V = '─', '│'
        M_L, M_R = '├', '┤'
        
        border_color = self._c('border')
        title_color = self._c('title')
        label_color = self._c('label')
        
        lines = []
        
        # 1. 顶部边框
        lines.append(f"{border_color}{TL}{H * (width - 2)}{TR}{Colors.ENDC}")
        
        # 2. 标题
        title = t('title')
        styled_title = f"{title_color}{Colors.BOLD}{title}{Colors.ENDC}"
        lines.append(f"{border_color}{V}{Colors.ENDC}{self._center_text(styled_title, width - 2)}{border_color}{V}{Colors.ENDC}")
        
        # 3. 分隔线
        lines.append(f"{border_color}{M_L}{H * (width - 2)}{M_R}{Colors.ENDC}")
        
        # 4. 状态与速度
        status_value = self.status
        recording_states = {t('status.recording'), t('status.saving')}
        playing_states = {t('status.playing'), t('status.stopping')}
        if status_value in recording_states:
            status_color = self._c('status_recording')
            symbol = "●"
        elif status_value in playing_states:
            status_color = self._c('status_playing')
            symbol = "▶"
        else:
            status_color = Colors.BRIGHT_WHITE
            symbol = "■"
            
        status_text = f"{label_color}{t('label.status')}:{Colors.ENDC} {status_color}{symbol} {self.status}{Colors.ENDC}"
        speed_text = f"{label_color}{t('label.speed')}:{Colors.ENDC} {self.speed:>3.1f}x"
        
        # 状态与速度同一行展示
        # 布局示例: │ 状态: ● 录制中       速度: 1.0x │
        content_width = width - 4 # 左右各 1 个空格加上两侧边框
        
        # 简单布局：状态左对齐，速度右对齐
        # 需要手动计算填充长度
        s_len = self._visible_len(status_text)
        sp_len = self._visible_len(speed_text)
        gap = content_width - s_len - sp_len
        
        if gap > 0:
            line_content = f" {status_text}{' ' * gap}{speed_text} "
        else:
            line_content = f" {status_text} {speed_text} " # 间距不足时的回退方案
            
        lines.append(f"{border_color}{V}{Colors.ENDC}{line_content}{border_color}{V}{Colors.ENDC}")
        
        # 5. 空行
        lines.append(f"{border_color}{V}{' ' * (width - 2)}{V}{Colors.ENDC}")

        # 6. 进度条
        curr, total = self.progress
        if total > 0:
            percent = min(1.0, max(0.0, curr / total))
            # 根据标签与百分比长度动态计算进度条长度，避免溢出
            label_part = f"{label_color}{t('label.progress')}:{Colors.ENDC}"
            percent_part = f"{int(percent*100):>3}%"
            inner_width = width - 2
            reserved = 1 + self._visible_len(label_part) + 1 + self._visible_len(percent_part) + 1
            bar_len = max(0, inner_width - reserved)
            filled = int(bar_len * percent)
            # 空槽使用更简洁的轨迹符号
            bar = '█' * filled + '━' * (bar_len - filled)
            bar_color = self._c('progress_bar')
            # 空槽使用亮黑色
            empty_color = Colors.BRIGHT_BLACK
            
            # 构造带颜色的进度条
            colored_bar = f"{bar_color}{'█' * filled}{Colors.ENDC}{empty_color}{'━' * (bar_len - filled)}{Colors.ENDC}"
            prog_text = f"{label_part} {colored_bar} {percent_part}"
        else:
            prog_text = f"{label_color}{t('label.progress')}:{Colors.ENDC} --"
            
        lines.append(f"{border_color}{V}{Colors.ENDC}{self._pad_text(' ' + prog_text, width - 2)}{border_color}{V}{Colors.ENDC}")

        # 7. 分隔线
        lines.append(f"{border_color}{M_L}{H * (width - 2)}{M_R}{Colors.ENDC}")

        # 8. 快捷键
        if self.hotkeys:
            hk = self.hotkeys
            # 格式化按键与说明
            def fmt_pair(k, d):
                key_str = f"[{k.upper()}]"
                # 按键固定宽度，说明宽度按当前语言最长文本自适应
                return f"{self._pad_text(key_str, key_width)} {self._pad_text(d, desc_width)}"

            # 第一行
            pair1 = fmt_pair(hk.get('record', ''), t('hotkey.record'))
            pair2 = fmt_pair(hk.get('play', ''), t('hotkey.play'))
            
            # 总宽 54 -> 内部宽度 52
            # " " + pair1 (25) + " " + pair2 (25) + " " = 52，空格数量正好为 1
            
            row1 = f" {pair1} {pair2}" 
            row1 = self._pad_text(row1, width - 2)
            lines.append(f"{border_color}{V}{Colors.ENDC}{row1}{border_color}{V}{Colors.ENDC}")
            
            # 第二行
            pair3 = fmt_pair(hk.get('speed_up', ''), t('hotkey.speed_up'))
            pair4 = fmt_pair(hk.get('speed_down', ''), t('hotkey.speed_down'))
            
            row2 = f" {pair3} {pair4}"
            row2 = self._pad_text(row2, width - 2)
            lines.append(f"{border_color}{V}{Colors.ENDC}{row2}{border_color}{V}{Colors.ENDC}")
        else:
            lines.append(f"{border_color}{V}{Colors.ENDC}{self._center_text(t('loading.hotkeys'), width - 2)}{border_color}{V}{Colors.ENDC}")

        # 9. 底部边框
        lines.append(f"{border_color}{BL}{H * (width - 2)}{BR}{Colors.ENDC}")

        # 输出渲染结果，移动到左上角后逐行覆盖，并清理行尾
        output = "\033[H" + "\n".join([line + "\033[K" for line in lines]) + "\033[J"
        sys.stdout.write(output)
        sys.stdout.flush()

display = DisplayManager()
