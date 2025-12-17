import time
import json
import threading
import sys
from typing import List, Dict, Optional, Union, Any
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key, KeyCode
try:
    from .settings import settings
    from .logger import logger
    from .display import display
except ImportError:
    from settings import settings
    from logger import logger
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

    def start(self, filename: Optional[str] = None, repeats: int = 0) -> None:
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
            logger.error("未找到宏文件。请先录制。")
            return
        except json.JSONDecodeError:
            logger.error("宏文件格式错误。")
            return

        self.playing = True
        self.stop_event.clear()
        
        stop_key = settings.config['hotkeys']['play']
        display.update_status(f"正在回放... (按 {stop_key.upper()} 停止)")
        display.update_speed(self.speed)
        logger.info(f"开始回放")

        self.play_thread = threading.Thread(
            target=self._play_loop, args=(repeats,))
        self.play_thread.start()

    def stop(self) -> None:
        if not self.playing:
            return
        self.playing = False
        self.stop_event.set()
        display.update_status("正在停止...")
        if hasattr(self, 'play_thread') and self.play_thread:
            self.play_thread.join()
        display.update_status("就绪")
        display.update_progress(0, 0)
        logger.info("回放已停止")

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
        btn_name = event['button'].split('.')[-1]
        button = getattr(Button, btn_name, Button.left)
        if event['pressed']:
            self.mouse_controller.press(button)
        else:
            self.mouse_controller.release(button)

    def _handle_scroll(self, event: Dict[str, Any]) -> None:
        self.mouse_controller.scroll(event['dx'], event['dy'])

    def _handle_key(self, event: Dict[str, Any], press: bool) -> None:
        key = self._parse_key(event['key'])
        if key:
            if press:
                self.keyboard_controller.press(key)
            else:
                self.keyboard_controller.release(key)

    def _play_loop(self, repeats: int) -> None:
        count = 0
        total_events = len(self.events)
        
        while self.playing and not self.stop_event.is_set():
            if repeats > 0 and count >= repeats:
                break

            count += 1
            if repeats == 0:
                display.update_status(f"正在回放 (无限循环)")
            elif repeats > 1:
                display.update_status(f"正在回放 (循环 {count}/{repeats})")

            start_time = time.time()
            last_progress_update = 0.0

            for i, event in enumerate(self.events):
                if self.stop_event.is_set():
                    break

                # 更新进度条 (每0.1秒更新一次，避免IO瓶颈)
                current_time = time.time()
                if current_time - last_progress_update > 0.1 or i == total_events - 1:
                    display.update_progress(i + 1, total_events)
                    last_progress_update = current_time

                target_time = start_time + (event['time'] / self.speed)
                wait_time = target_time - current_time

                if wait_time > 0:
                    if self.stop_event.wait(wait_time):
                        break

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
                    logger.error(f"执行事件失败: {e}")
        
        self.playing = False
        display.update_status("就绪")
        display.update_progress(0, 0)

    def _print_progress(self, current: int, total: int) -> None:
        # Deprecated: Handled by display.update_progress
        pass
