import time
import json
from typing import List, Dict, Optional, Union
import mouse
import keyboard
from settings import settings
from display import display

class MacroRecorder:
    def __init__(self) -> None:
        self.events: List[Dict] = []
        self.start_time: float = 0.0
        self.recording: bool = False
        self.last_record_time: float = 0.0
        self.sample_rate: float = settings.config.get('sample_rate', 0.016)

    def _mouse_callback(self, event):
        if not self.recording:
            return

        current_time = time.perf_counter()
        elapsed = current_time - self.start_time

        if isinstance(event, mouse.MoveEvent):
            if current_time - self.last_record_time < self.sample_rate:
                return
            self.last_record_time = current_time
            self.events.append({
                'type': 'move',
                'time': elapsed,
                'x': event.x,
                'y': event.y
            })
        elif isinstance(event, mouse.ButtonEvent):
            pressed = (event.event_type == 'down' or event.event_type == 'double')
            x, y = mouse.get_position()
            self.events.append({
                'type': 'click',
                'time': elapsed,
                'x': x,
                'y': y,
                'button': event.button,
                'pressed': pressed
            })
        elif isinstance(event, mouse.WheelEvent):
            x, y = mouse.get_position()
            self.events.append({
                'type': 'scroll',
                'time': elapsed,
                'x': x,
                'y': y,
                'dx': 0,
                'dy': int(event.delta)
            })

    def _keyboard_callback(self, event):
        if not self.recording:
            return
        
        # Don't record the stop key
        if self.stop_key and event.name.lower() == self.stop_key:
            return

        elapsed = time.perf_counter() - self.start_time
        event_type = 'key_press' if event.event_type == 'down' else 'key_release'
        
        self.events.append({
            'type': event_type,
            'time': elapsed,
            'key': event.name
        })

    def start(self) -> None:
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.perf_counter()
        self.last_record_time = self.start_time
        
        self.stop_key = settings.get_key('record')
        
        display.update_status("正在录制")

        mouse.hook(self._mouse_callback)
        keyboard.hook(self._keyboard_callback)

    def stop(self) -> None:
        if not self.recording:
            return
        self.recording = False
        
        mouse.unhook(self._mouse_callback)
        keyboard.unhook(self._keyboard_callback)
            
        display.update_status("正在保存")
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
