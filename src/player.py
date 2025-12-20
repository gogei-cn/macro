import time
import json
import threading
from typing import List, Dict, Optional, Union, Any
import mouse
import keyboard
from settings import settings
from display import display

class MacroPlayer:
    def __init__(self) -> None:
        self.playing: bool = False
        self.stop_event = threading.Event()
        self.speed: float = settings.config['default_speed']
        self.play_thread: Optional[threading.Thread] = None
        self.events: List[Dict[str, Any]] = []

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

    def _handle_move(self, event: Dict[str, Any]) -> None:
        mouse.move(event['x'], event['y'])

    def _handle_click(self, event: Dict[str, Any]) -> None:
        button = event.get('button', 'left')
        if event['pressed']:
            mouse.press(button)
        else:
            mouse.release(button)

    def _handle_scroll(self, event: Dict[str, Any]) -> None:
        # mouse library uses wheel(delta)
        # Try to use dy if available, otherwise 0
        dy = event.get('dy', 0)
        if dy != 0:
            mouse.wheel(dy)

    def _handle_key(self, event: Dict[str, Any]) -> None:
        key = event.get('key')
        if not key:
            return
        
        try:
            if event['type'] == 'key_press':
                keyboard.press(key)
            else:
                keyboard.release(key)
        except ValueError:
            # Handle unknown keys gracefully
            pass

    def _play_loop(self) -> None:
        if not self.events:
            self.playing = False
            display.update_status("就绪")
            return

        while self.playing:
            start_time = time.perf_counter()
            event_start_time = self.events[0]['time']
            
            for event in self.events:
                if self.stop_event.is_set():
                    break

                # Calculate target time
                target_time = (event['time'] - event_start_time) / self.speed
                current_elapsed = time.perf_counter() - start_time
                
                wait_time = target_time - current_elapsed
                if wait_time > 0:
                    time.sleep(wait_time)

                if event['type'] == 'move':
                    self._handle_move(event)
                elif event['type'] == 'click':
                    self._handle_click(event)
                elif event['type'] == 'scroll':
                    self._handle_scroll(event)
                elif event['type'] in ('key_press', 'key_release'):
                    self._handle_key(event)

            # Loop check (if implemented) or just stop
            # For now, let's assume single run or loop based on settings?
            # The original code didn't show the loop logic clearly in the snippet, 
            # but the README says "Infinite playback".
            # Let's assume we loop until stopped.
            if not self.stop_event.is_set():
                time.sleep(0.1) # Small pause between loops
            else:
                break
        
        self.playing = False
        display.update_status("就绪")


