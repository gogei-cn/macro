import time
import json
from pynput import mouse, keyboard
from .settings import settings
from .utils import Colors

class MacroRecorder:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.events = []
        self.start_time = 0
        self.recording = False
        self.last_record_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None

    def on_move(self, x, y):
        if self.recording:
            current_time = time.time()
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

    def on_key_press(self, key):
        if self.recording:
            stop_key = settings.get_key('record')
            if key == stop_key:
                return

            elapsed = time.time() - self.start_time
            try:
                key_data = key.char
            except AttributeError:
                key_data = str(key)
            
            self.events.append({
                'type': 'key_press',
                'time': elapsed,
                'key': key_data
            })

    def on_key_release(self, key):
        if self.recording:
            stop_key = settings.get_key('record')
            if key == stop_key:
                return

            elapsed = time.time() - self.start_time
            try:
                key_data = key.char
            except AttributeError:
                key_data = str(key)
            
            self.events.append({
                'type': 'key_release',
                'time': elapsed,
                'key': key_data
            })

    def start(self):
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.time()
        self.last_record_time = self.start_time
        
        stop_key = settings.config['hotkeys']['record']
        print(f"\n{Colors.GREEN}[录制] 开始... (按 {stop_key.upper()} 停止){Colors.ENDC}")

        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release)
        self.keyboard_listener.start()

    def stop(self):
        if not self.recording:
            return
        self.recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        print(f"{Colors.YELLOW}[录制] 结束。{Colors.ENDC}")
        self.save()

    def save(self, filename=None):
        if filename is None:
            filename = settings.config['macro_filename']
        with open(filename, 'w') as f:
            json.dump(self.events, f)
        print(f"{Colors.CYAN}宏已保存到 {filename}{Colors.ENDC}")
