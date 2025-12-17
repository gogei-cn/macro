import json
from pynput import keyboard
from pynput.keyboard import Key

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
            "macro_filename": "macro.json",
            "sample_rate": 0.016,
            "log_level": "INFO",
            "log_file": "macro.log"
        }
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if 'hotkeys' in data:
                    self.config['hotkeys'].update(data['hotkeys'])
                for key in ['default_speed', 'macro_filename', 'sample_rate', 'log_level', 'log_file']:
                    if key in data:
                        self.config[key] = data[key]
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
            return getattr(Key, key_str.lower())
        except AttributeError:
            try:
                return keyboard.KeyCode.from_char(key_str)
            except:
                return None

settings = Settings()
