import time
import json
import os
import sys
from typing import List, Dict, Optional, Union

try:
    from pynput import mouse as pynput_mouse
    from pynput import keyboard as pynput_keyboard
except ImportError:
    pynput_mouse = None
    pynput_keyboard = None

from settings import settings
from display import display

class MacroRecorder:
    def __init__(self) -> None:
        self.events: List[Dict] = []
        self.start_time: float = 0.0
        self.recording: bool = False
        self.last_record_time: float = 0.0
        self.sample_rate: float = settings.config.get('sample_rate', 0.016)
        self.pynput_mouse_listener = None
        self.pynput_keyboard_listener = None

    # Pynput callbacks
    def _pynput_on_move(self, x, y):
        if not self.recording: return
        current_time = time.perf_counter()
        if current_time - self.last_record_time < self.sample_rate:
            return
        self.last_record_time = current_time
        elapsed = current_time - self.start_time
        self.events.append({'type': 'move', 'time': elapsed, 'x': x, 'y': y})

    def _pynput_on_click(self, x, y, button, pressed):
        if not self.recording: return
        elapsed = time.perf_counter() - self.start_time
        self.events.append({
            'type': 'click', 'time': elapsed, 'x': x, 'y': y,
            'button': str(button).replace('Button.', ''), 'pressed': pressed
        })

    def _pynput_on_scroll(self, x, y, dx, dy):
        if not self.recording: return
        elapsed = time.perf_counter() - self.start_time
        self.events.append({
            'type': 'scroll', 'time': elapsed, 'x': x, 'y': y, 'dx': dx, 'dy': dy
        })

    def _pynput_on_press(self, key):
        if not self.recording: return
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '')
        
        # Stop key check (simplified)
        if k == self.stop_key: return

        elapsed = time.perf_counter() - self.start_time
        self.events.append({'type': 'key_press', 'time': elapsed, 'key': k})

    def _pynput_on_release(self, key):
        if not self.recording: return
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '')
            
        if k == self.stop_key: return

        elapsed = time.perf_counter() - self.start_time
        self.events.append({'type': 'key_release', 'time': elapsed, 'key': k})

    def start(self) -> None:
        if self.recording:
            return
        self.events = []
        self.recording = True
        self.start_time = time.perf_counter()
        self.last_record_time = self.start_time
        
        self.stop_key = settings.get_key('record')
        display.update_status("正在录制")

        if pynput_mouse and pynput_keyboard:
            self.pynput_mouse_listener = pynput_mouse.Listener(
                on_move=self._pynput_on_move,
                on_click=self._pynput_on_click,
                on_scroll=self._pynput_on_scroll)
            self.pynput_mouse_listener.start()
            
            self.pynput_keyboard_listener = pynput_keyboard.Listener(
                on_press=self._pynput_on_press,
                on_release=self._pynput_on_release)
            self.pynput_keyboard_listener.start()
        else:
            print("Error: pynput modules not found.")
            self.recording = False

    def stop(self) -> None:
        if not self.recording:
            return
        self.recording = False
        
        if self.pynput_mouse_listener:
            self.pynput_mouse_listener.stop()
            self.pynput_mouse_listener = None
        if self.pynput_keyboard_listener:
            self.pynput_keyboard_listener.stop()
            self.pynput_keyboard_listener = None
            
        display.update_status("正在保存")
        self.save()
        display.update_status("就绪")

    def save(self, filename: Optional[str] = None) -> None:
        if filename is None:
            filename = settings.config['macro_filename']
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.events, f)
            display.update_status(f"已保存: {filename}")
        except Exception as e:
            # Try saving to the directory of the script/executable if relative path fails
            try:
                if getattr(sys, 'frozen', False):
                    base_dir = os.path.dirname(sys.executable)
                else:
                    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                    # If running from src, maybe go up one level? 
                    # But let's just try the script dir first or the CWD.
                
                abs_path = os.path.join(base_dir, os.path.basename(filename))
                with open(abs_path, 'w') as f:
                    json.dump(self.events, f)
                display.update_status(f"已保存: {os.path.basename(abs_path)}")
            except Exception as e2:
                display.update_status(f"保存失败: {e}")
                print(f"\n保存失败详细信息: {e}")
