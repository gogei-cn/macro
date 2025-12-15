import time
import json
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Listener as KeyboardListener
import ctypes
import os

# 启用 Windows 终端 ANSI 颜色支持
os.system('')

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# 尝试设置 Windows DPI 感知，解决高分屏下的坐标偏差问题
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class Settings:
    def __init__(self, filename='settings.json'):
        self.filename = filename
        self.config = {
            "hotkeys": {
                "record": "f8",
                "play": "f9",
                "speed_up": "page_up",
                "speed_down": "page_down"
            },
            "default_speed": 1.0,
            "macro_filename": "macro.json"
        }
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # Deep update for nested dictionaries
                if 'hotkeys' in data:
                    self.config['hotkeys'].update(data['hotkeys'])
                if 'default_speed' in data:
                    self.config['default_speed'] = data['default_speed']
                if 'macro_filename' in data:
                    self.config['macro_filename'] = data['macro_filename']
        except FileNotFoundError:
            print(f"未找到配置文件 {self.filename}，生成默认配置。")
            self.save()

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_key(self, action):
        key_str = self.config['hotkeys'].get(action)
        if not key_str:
            return None

        try:
            # Try to get from Key enum (e.g., 'f8', 'f9')
            return getattr(Key, key_str.lower())
        except AttributeError:
            # If not in Key enum, assume it's a character code (e.g., 'a', '1')
            try:
                return keyboard.KeyCode.from_char(key_str)
            except:
                return None


settings = Settings()


class MouseMacro:
    def __init__(self):
        self.mouse_controller = MouseController()
        self.events = []
        self.start_time = 0
        self.recording = False
        self.playing = False
        self.stop_event = threading.Event()
        self.last_record_time = 0
        self.speed = settings.config['default_speed']

    def on_move(self, x, y):
        if self.recording:
            current_time = time.time()
            # 优化：限制录制频率 (约 60Hz)，减少资源占用和文件体积
            if current_time - self.last_record_time < 0.016:
                return
            self.last_record_time = current_time

            elapsed = current_time - self.start_time
            self.events.append(
                {'type': 'move', 'time': elapsed, 'x': x, 'y': y})

    def on_click(self, x, y, button, pressed):
        if self.recording:
            elapsed = time.time() - self.start_time
            self.events.append({
                'type': 'click',
                'time': elapsed,
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed
            })

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            elapsed = time.time() - self.start_time
            self.events.append({
                'type': 'scroll',
                'time': elapsed,
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy
            })

    def start_recording(self):
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.time()
        self.last_record_time = self.start_time
        # 获取按键名称用于提示
        stop_key = settings.config['hotkeys']['record']
        print(f"\n{Colors.GREEN}[录制] 开始... (按 {stop_key.upper()} 停止){Colors.ENDC}")

        # 非阻塞启动鼠标监听
        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        self.mouse_listener.start()

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            self.mouse_listener.stop()
        print(f"{Colors.YELLOW}[录制] 结束。{Colors.ENDC}")
        self.save_macro()

    def save_macro(self, filename=None):
        if filename is None:
            filename = settings.config['macro_filename']
        with open(filename, 'w') as f:
            json.dump(self.events, f)
        print(f"{Colors.CYAN}宏已保存到 {filename}{Colors.ENDC}")

    def start_playing(self, filename=None, repeats=0):
        if filename is None:
            filename = settings.config['macro_filename']
        if self.playing:
            return
        try:
            with open(filename, 'r') as f:
                self.events = json.load(f)
        except FileNotFoundError:
            print(f"{Colors.RED}未找到宏文件。请先录制。{Colors.ENDC}")
            return

        self.playing = True
        self.stop_event.clear()
        # 获取按键名称用于提示
        stop_key = settings.config['hotkeys']['play']
        print(f"\n{Colors.GREEN}[回放] 开始... (按 {stop_key.upper()} 停止){Colors.ENDC}")

        # 在新线程中运行回放，避免阻塞键盘监听
        self.play_thread = threading.Thread(
            target=self._play_loop, args=(repeats,))
        self.play_thread.start()

    def stop_playing(self):
        if not self.playing:
            return
        self.playing = False
        self.stop_event.set()
        print(f"{Colors.YELLOW}[回放] 正在停止...{Colors.ENDC}")
        if hasattr(self, 'play_thread') and self.play_thread:
            self.play_thread.join()
        print(f"{Colors.YELLOW}[回放] 已停止。{Colors.ENDC}")

    def _play_loop(self, repeats):
        count = 0
        while self.playing and not self.stop_event.is_set():
            if repeats > 0 and count >= repeats:
                break

            count += 1
            if repeats == 0:
                pass
            elif repeats > 1:
                print(f"{Colors.CYAN}正在执行第 {count}/{repeats} 次循环...{Colors.ENDC}")

            start_time = time.time()

            for event in self.events:
                if self.stop_event.is_set():
                    break

                # 计算需要等待的时间
                # 使用 self.speed 调整等待时间
                target_time = start_time + (event['time'] / self.speed)
                current_time = time.time()
                wait_time = target_time - current_time

                if wait_time > 0:
                    # 优化：使用 Event.wait 代替 sleep，实现毫秒级响应中断
                    if self.stop_event.wait(wait_time):
                        break

                if event['type'] == 'move':
                    self.mouse_controller.position = (event['x'], event['y'])
                elif event['type'] == 'click':
                    # 处理 Button.left 这种字符串
                    btn_name = event['button'].split('.')[-1]
                    button = getattr(Button, btn_name, Button.left)
                    if event['pressed']:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                elif event['type'] == 'scroll':
                    self.mouse_controller.scroll(event['dx'], event['dy'])

        self.playing = False
        print(f"{Colors.YELLOW}[回放] 结束。{Colors.ENDC}")


macro = MouseMacro()


def on_press(key):
    if key == settings.get_key('record'):
        if macro.recording:
            macro.stop_recording()
        else:
            if macro.playing:
                print(f"{Colors.RED}正在回放中，请先停止回放。{Colors.ENDC}")
            else:
                macro.start_recording()
    elif key == settings.get_key('play'):
        if macro.playing:
            macro.stop_playing()
        else:
            if macro.recording:
                print(f"{Colors.RED}正在录制中，请先停止录制。{Colors.ENDC}")
            else:
                # 默认无限循环
                macro.start_playing(repeats=0)
    elif key == settings.get_key('speed_up'):
        macro.speed += 0.5
        print(f"\n{Colors.BLUE}[设置] 播放速度已增加至: {macro.speed:.1f}x{Colors.ENDC}")
    elif key == settings.get_key('speed_down'):
        macro.speed = max(0.1, macro.speed - 0.5)
        print(f"\n{Colors.BLUE}[设置] 播放速度已降低至: {macro.speed:.1f}x{Colors.ENDC}")


def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== 鼠标宏工具 (by gogei) ==={Colors.ENDC}")
    hk = settings.config['hotkeys']
    print(f"{Colors.GREEN}{hk['record'].upper():<8}{Colors.ENDC} : 开始/停止 录制")
    print(f"{Colors.GREEN}{hk['play'].upper():<8}{Colors.ENDC} : 开始/停止 回放 (无限循环)")
    print(f"{Colors.GREEN}{hk['speed_up'].upper():<8}{Colors.ENDC} : 增加回放速度 (+0.5)")
    print(f"{Colors.GREEN}{hk['speed_down'].upper():<8}{Colors.ENDC} : 减少回放速度 (-0.5)")
    print(f"{Colors.CYAN}当前配置文件: {settings.filename}{Colors.ENDC}")

    # 阻塞监听键盘
    with KeyboardListener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
