import sys
import os
import time
import platform

# 将当前目录添加到 sys.path 以确保导入正常工作
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from settings import settings

import pynput
from pynput import keyboard as pynput_keyboard

from utils import Colors, setup_dpi_awareness, enable_vt_mode
from recorder import MacroRecorder
from player import MacroPlayer
from display import display
from i18n import t, list_languages

class MacroApp:
    def __init__(self):
        self.old_settings = None
        self.setup_environment()
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.last_speed_change = 0
        self.speed_cooldown = 0.2

    def setup_environment(self):
        setup_dpi_awareness()
        enable_vt_mode()
        # 启动时清空屏幕并隐藏光标
        sys.stdout.write("\033[2J\033[H\033[?25l")
        sys.stdout.flush()
        
        # 在 Linux 上禁用终端回显以防止按键泄露
        if platform.system() == 'Linux':
            try:
                import termios
                self.fd = sys.stdin.fileno()
                self.old_settings = termios.tcgetattr(self.fd)
                new_settings = termios.tcgetattr(self.fd)
                # 禁用回显
                new_settings[3] = new_settings[3] & ~termios.ECHO
                termios.tcsetattr(self.fd, termios.TCSADRAIN, new_settings)
            except Exception:
                pass

    def cleanup(self):
        # 显示光标
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

        # 恢复终端设置
        if self.old_settings:
            import termios
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def handle_record_toggle(self):
        if self.recorder.recording:
            self.recorder.stop()
        else:
            if self.player.playing:
                display.update_status(t('prompt.stop_play_first'))
            else:
                self.recorder.start()

    def handle_play_toggle(self):
        if self.player.playing:
            self.player.stop()
        else:
            if self.recorder.recording:
                display.update_status(t('prompt.stop_record_first'))
            else:
                self.player.start()

    def handle_speed_change(self, delta):
        current_time = time.time()
        if current_time - self.last_speed_change > self.speed_cooldown:
            new_speed = self.player.speed + delta
            
            # 特殊处理 0.1 -> 0.5 的步长
            if delta > 0 and self.player.speed < 0.5:
                new_speed = 0.5
            
            self.player.speed = max(0.1, new_speed)
            display.update_speed(self.player.speed)
            self.last_speed_change = current_time


    def on_press(self, key):
        try:
            # 将 pynput 按键转换为匹配设置的字符串格式
            key_name = None
            try:
                key_name = key.char
            except AttributeError:
                key_name = str(key).replace('Key.', '')
            
            if not key_name:
                return

            # 标准化 (例如 page_up -> page up)
            key_name = key_name.replace('_', ' ').lower()

            if key_name == settings.get_key('record'):
                self.handle_record_toggle()
            elif key_name == settings.get_key('play'):
                self.handle_play_toggle()
            elif key_name == settings.get_key('speed_up'):
                self.handle_speed_change(0.5)
            elif key_name == settings.get_key('speed_down'):
                self.handle_speed_change(-0.5)
        except Exception:
            pass

    def run(self):
        # 初始化显示热键
        display.set_hotkeys(settings.config['hotkeys'])
        display.render()
        
        # 使用 pynput 注册回调
        with pynput_keyboard.Listener(on_press=self.on_press) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass

def main():
    # 首次运行（无 settings.json）时提供语言提示
    if getattr(settings, 'first_run', False):
        try:
            langs = list_languages()
            hint = "/".join(langs)
            choice = input(f"首次运行：请选择语言 ({hint})，直接回车默认 zh: ").strip().lower()
            if choice in langs:
                settings.config['language'] = choice
            settings.save()
        except Exception:
            pass

    app = None
    try:
        app = MacroApp()
        app.run()
    except Exception:
        import traceback
        traceback.print_exc()
        input(f"\n{t('fatal_error_prompt')}")
    finally:
        if app:
            app.cleanup()

if __name__ == "__main__":
    main()
