import sys
import os
import time
import platform

# Linux 环境下的 Root 权限检查
if platform.system() == 'Linux':
    if os.geteuid() != 0:
        print("\n错误: 权限不足。")
        print("在 Linux 上，此程序需要 Root 权限才能访问输入设备 (/dev/input/)。")
        print("请尝试使用 sudo 运行: sudo python src/main.py")
        sys.exit(1)

try:
    import keyboard
    import mouse
except ImportError as e:
    print("\n错误: 无法加载输入控制模块 (keyboard/mouse)。")
    print(f"详细错误信息: {e}\n")
    sys.exit(1)

# Add the current directory to sys.path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from settings import settings
from utils import Colors, setup_dpi_awareness
from recorder import MacroRecorder
from player import MacroPlayer
from display import display

class MacroApp:
    def __init__(self):
        self.setup_environment()
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.last_speed_change = 0
        self.speed_cooldown = 0.2

    def setup_environment(self):
        setup_dpi_awareness()
        # Clear screen on startup
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def handle_record_toggle(self):
        if self.recorder.recording:
            self.recorder.stop()
        else:
            if self.player.playing:
                display.update_status("正在回放中，请先停止回放。")
            else:
                self.recorder.start()

    def handle_play_toggle(self):
        if self.player.playing:
            self.player.stop()
        else:
            if self.recorder.recording:
                display.update_status("正在录制中，请先停止录制。")
            else:
                self.player.start()

    def handle_speed_change(self, delta):
        current_time = time.time()
        if current_time - self.last_speed_change > self.speed_cooldown:
            new_speed = self.player.speed + delta
            
            # Special handling for 0.1 -> 0.5 step
            if delta > 0 and self.player.speed < 0.5:
                new_speed = 0.5
            
            self.player.speed = max(0.1, new_speed)
            display.update_speed(self.player.speed)
            self.last_speed_change = current_time

    def on_press(self, event):
        try:
            key = event.name.lower()
            if key == settings.get_key('record'):
                self.handle_record_toggle()
            elif key == settings.get_key('play'):
                self.handle_play_toggle()
            elif key == settings.get_key('speed_up'):
                self.handle_speed_change(0.5)
            elif key == settings.get_key('speed_down'):
                self.handle_speed_change(-0.5)
        except Exception:
            pass

    def run(self):
        # Initialize display with hotkeys
        display.set_hotkeys(settings.config['hotkeys'])
        display.render()
        
        # Register the callback
        keyboard.on_press(self.on_press)
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass

def main():
    app = MacroApp()
    app.run()


if __name__ == "__main__":
    main()
