import time
import json
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key, KeyCode
from .settings import settings
from .utils import Colors

class MacroPlayer:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.playing = False
        self.stop_event = threading.Event()
        self.speed = settings.config['default_speed']
        self.play_thread = None
        self.events = []

    def start(self, filename=None, repeats=0):
        if filename is None:
            filename = settings.config['macro_filename']
        if self.playing:
            return
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.events = data
                elif isinstance(data, dict):
                    self.events = data.get('events', [])
        except FileNotFoundError:
            print(f"{Colors.RED}未找到宏文件。请先录制。{Colors.ENDC}")
            return

        self.playing = True
        self.stop_event.clear()
        
        stop_key = settings.config['hotkeys']['play']
        print(f"\n{Colors.GREEN}[回放] 开始... (按 {stop_key.upper()} 停止){Colors.ENDC}")

        self.play_thread = threading.Thread(
            target=self._play_loop, args=(repeats,))
        self.play_thread.start()

    def stop(self):
        if not self.playing:
            return
        self.playing = False
        self.stop_event.set()
        print(f"{Colors.YELLOW}[回放] 正在停止...{Colors.ENDC}")
        if hasattr(self, 'play_thread') and self.play_thread:
            self.play_thread.join()
        print(f"{Colors.YELLOW}[回放] 已停止。{Colors.ENDC}")

    def _parse_key(self, key_str):
        if key_str.startswith('Key.'):
            try:
                return getattr(Key, key_str.split('.')[1])
            except AttributeError:
                return None
        elif len(key_str) == 1:
            return key_str
        else:
            return None

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

                target_time = start_time + (event['time'] / self.speed)
                current_time = time.time()
                wait_time = target_time - current_time

                if wait_time > 0:
                    if self.stop_event.wait(wait_time):
                        break

                if event['type'] == 'move':
                    self.mouse_controller.position = (event['x'], event['y'])
                elif event['type'] == 'click':
                    btn_name = event['button'].split('.')[-1]
                    button = getattr(Button, btn_name, Button.left)
                    if event['pressed']:
                        self.mouse_controller.press(button)
                    else:
                        self.mouse_controller.release(button)
                elif event['type'] == 'scroll':
                    self.mouse_controller.scroll(event['dx'], event['dy'])
                elif event['type'] == 'key_press':
                    key = self._parse_key(event['key'])
                    if key:
                        self.keyboard_controller.press(key)
                elif event['type'] == 'key_release':
                    key = self._parse_key(event['key'])
                    if key:
                        self.keyboard_controller.release(key)

        self.playing = False
        print(f"{Colors.YELLOW}[回放] 结束。{Colors.ENDC}")
