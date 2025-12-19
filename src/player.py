import time
import json
import threading
from typing import List, Dict, Optional, Union, Any
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
try:
    from .settings import settings
    from .display import display
except ImportError:
    from settings import settings
    from display import display

class MacroPlayer:
    def __init__(self) -> None:
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.playing: bool = False
        self.stop_event = threading.Event()
        self.speed: float = settings.config['default_speed']
        self.play_thread: Optional[threading.Thread] = None
        self.events: List[Dict[str, Any]] = []

    def _prepare_events(self):
        """Pre-process events to avoid parsing overhead during playback"""
        prepared = []
        for event in self.events:
            new_event = event.copy()
            if event['type'] == 'click':
                btn_name = event['button'].split('.')[-1]
                new_event['parsed_button'] = getattr(Button, btn_name, Button.left)
            elif event['type'] in ('key_press', 'key_release'):
                new_event['parsed_key'] = self._parse_key(event['key'])
            prepared.append(new_event)
        return prepared

    def start(self, filename: Optional[str] = None) -> None:
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
            
            # Pre-process events
            self.prepared_events = self._prepare_events()
            
        except FileNotFoundError:
            display.update_status("未找到宏文件")
            return
        except json.JSONDecodeError:
            display.update_status("宏文件格式错误")
            return

        self.playing = True
        self.stop_event.clear()
        
        display.update_status("正在回放")
        display.update_speed(self.speed)

        self.play_thread = threading.Thread(target=self._play_loop)
        self.play_thread.start()

    def stop(self) -> None:
        if not self.playing:
            return
        self.playing = False
        self.stop_event.set()
        display.update_status("正在停止")
        if hasattr(self, 'play_thread') and self.play_thread:
            self.play_thread.join()

    def _parse_key(self, key_str: str) -> Union[Key, str, None]:
        if key_str.startswith('Key.'):
            try:
                return getattr(Key, key_str.split('.')[1])
            except AttributeError:
                return None
        elif len(key_str) == 1:
            return key_str
        else:
            return None

    def _handle_move(self, event: Dict[str, Any]) -> None:
        self.mouse_controller.position = (event['x'], event['y'])

    def _handle_click(self, event: Dict[str, Any]) -> None:
        button = event.get('parsed_button', Button.left)
        if event['pressed']:
            self.mouse_controller.press(button)
        else:
            self.mouse_controller.release(button)

    def _handle_scroll(self, event: Dict[str, Any]) -> None:
        self.mouse_controller.scroll(event['dx'], event['dy'])

    def _handle_key(self, event: Dict[str, Any], press: bool) -> None:
        key = event.get('parsed_key')
        if key:
            if press:
                self.keyboard_controller.press(key)
            else:
                self.keyboard_controller.release(key)

    def _play_loop(self) -> None:
        total_events = len(self.prepared_events)
        total_duration = self.prepared_events[-1]['time'] if self.prepared_events else 0.0
        
        while self.playing and not self.stop_event.is_set():
            # Use perf_counter for high precision timing
            start_time = time.perf_counter()
            last_progress_update = 0.0

            for i, event in enumerate(self.prepared_events):
                if self.stop_event.is_set():
                    break

                current_time = time.perf_counter()
                target_time = start_time + (event['time'] / self.speed)
                wait_time = target_time - current_time

                if wait_time > 0:
                    # Break long waits into chunks to update progress bar
                    while wait_time > 0.1:
                        if self.stop_event.wait(0.1):
                            break
                        
                        # Update progress
                        elapsed = (time.perf_counter() - start_time) * self.speed
                        display.update_progress(min(elapsed, total_duration), total_duration)
                        
                        current_time = time.perf_counter()
                        wait_time = target_time - current_time
                        
                    if self.stop_event.is_set():
                        break
                        
                    if wait_time > 0:
                        if self.stop_event.wait(wait_time):
                            break

                # Update progress at event execution
                if i == total_events - 1:
                     display.update_progress(total_duration, total_duration)
                elif time.perf_counter() - last_progress_update > 0.1:
                    display.update_progress(event['time'], total_duration)
                    last_progress_update = time.perf_counter()

                try:
                    if event['type'] == 'move':
                        self._handle_move(event)
                    elif event['type'] == 'click':
                        self._handle_click(event)
                    elif event['type'] == 'scroll':
                        self._handle_scroll(event)
                    elif event['type'] == 'key_press':
                        self._handle_key(event, press=True)
                    elif event['type'] == 'key_release':
                        self._handle_key(event, press=False)
                except Exception as e:
                    pass
        
        self.playing = False
        display.update_status("就绪")
        display.update_progress(0, 0)
