import time
import json
from typing import List, Dict, Optional, Union
from pynput import mouse, keyboard
try:
    from .settings import settings
    from .display import display
except ImportError:
    from settings import settings
    from display import display

class MacroRecorder:
    def __init__(self) -> None:
        self.mouse_controller = mouse.Controller()
        self.events: List[Dict] = []
        self.start_time: float = 0.0
        self.recording: bool = False
        self.last_record_time: float = 0.0
        self.mouse_listener: Optional[mouse.Listener] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.sample_rate: float = settings.config.get('sample_rate', 0.016)

    def on_move(self, x: int, y: int) -> None:
        if self.recording:
            current_time = time.time()
            if current_time - self.last_record_time < self.sample_rate:
                return
            self.last_record_time = current_time

            elapsed = current_time - self.start_time
            self.events.append(
                {'type': 'move', 'time': elapsed, 'x': x, 'y': y})
            
            # Optional: Update status with event count periodically?
            # Might be too frequent for display refresh, so skip for now.

    def on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
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

    def on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
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

    def on_key_press(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> None:
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

    def on_key_release(self, key: Union[keyboard.Key, keyboard.KeyCode]) -> None:
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

    def start(self) -> None:
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.time()
        self.last_record_time = self.start_time
        
        stop_key = settings.config['hotkeys']['record']
        display.update_status(f"正在录制... (按 {stop_key.upper()} 停止)")

        self.mouse_listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        self.mouse_listener.start()

        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release)
        self.keyboard_listener.start()

    def stop(self) -> None:
        if not self.recording:
            return
        self.recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        display.update_status("正在保存...")
        self.save()
        display.update_status("就绪")

    def save(self, filename: Optional[str] = None) -> None:
        if filename is None:
            filename = settings.config['macro_filename']
        try:
            with open(filename, 'w') as f:
                json.dump(self.events, f)
        except Exception as e:
            pass
