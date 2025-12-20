import json

class Settings:
    def __init__(self, filename='settings.json'):
        self.filename = filename
        self.config = {
            "hotkeys": {
                "record": "f8",
                "play": "f9",
                "speed_up": "page up",
                "speed_down": "page down"
            },
            "default_speed": 1.0,
            "macro_filename": "macro.json",
            "sample_rate": 0.016,
            "theme": {
                "title": "BRIGHT_CYAN",
                "border": "BRIGHT_BLUE",
                "label": "BRIGHT_WHITE",
                "status_recording": "BRIGHT_RED",
                "status_playing": "BRIGHT_GREEN",
                "progress_bar": "BRIGHT_CYAN",
                "guide_title": "BRIGHT_YELLOW"
            }
        }
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                if 'hotkeys' in data:
                    self.config['hotkeys'].update(data['hotkeys'])
                if 'theme' in data:
                    self.config['theme'].update(data['theme'])
                for key in ['default_speed', 'macro_filename', 'sample_rate']:
                    if key in data:
                        self.config[key] = data[key]
        except FileNotFoundError:
            print(f"未找到配置文件 {self.filename}，生成默认配置。")
            self.save()

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.config, f, indent=4)
        except PermissionError:
            print(f"警告: 无法保存配置文件 {self.filename} (权限不足)。请检查文件所有权。")
        except Exception as e:
            print(f"警告: 无法保存配置文件 {self.filename} ({e})。")

    def get_key(self, action):
        key_str = self.config['hotkeys'].get(action)
        if not key_str:
            return None
        # Normalize for keyboard library (e.g. page_up -> page up)
        return key_str.replace('_', ' ').lower()

settings = Settings()
