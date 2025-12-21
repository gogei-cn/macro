import json
import os

try:
    from .settings import settings
except ImportError:
    from settings import settings

# 默认内置翻译，文件缺失或键缺失时作为兜底
DEFAULT_TRANSLATIONS = {
    "zh": {
        "title": "MACRO TOOL",
        "label.status": "状态",
        "label.speed": "速度",
        "label.progress": "进度",
        "label.hotkeys": "快捷键",
        "status.ready": "就绪",
        "status.playing": "正在回放",
        "status.stopping": "正在停止",
        "status.recording": "正在录制",
        "status.saving": "正在保存",
        "status.saved": "已保存: {filename}",
        "status.save_failed": "保存失败: {error}",
        "status.save_failed_detail": "保存失败详细信息: {error}",
        "error.macro_missing": "未找到宏文件",
        "error.macro_invalid": "宏文件格式错误",
        "error.playback": "回放错误: {error}",
        "prompt.stop_play_first": "正在回放中，请先停止回放。",
        "prompt.stop_record_first": "正在录制中，请先停止录制。",
        "loading.hotkeys": "加载中...",
        "hotkey.record": "录制/停止",
        "hotkey.play": "回放/停止",
        "hotkey.speed_up": "加速",
        "hotkey.speed_down": "减速",
        "hotkey.toggle_language": "切换语言",
        "fatal_error_prompt": "程序发生严重错误，按回车键退出..."
    },
    "en": {
        "title": "MACRO TOOL",
        "label.status": "Status",
        "label.speed": "Speed",
        "label.progress": "Progress",
        "label.hotkeys": "Hotkeys",
        "status.ready": "Ready",
        "status.playing": "Playing",
        "status.stopping": "Stopping",
        "status.recording": "Recording",
        "status.saving": "Saving",
        "status.saved": "Saved: {filename}",
        "status.save_failed": "Save failed: {error}",
        "status.save_failed_detail": "Save failed detail: {error}",
        "error.macro_missing": "Macro file not found",
        "error.macro_invalid": "Macro file invalid",
        "error.playback": "Playback error: {error}",
        "prompt.stop_play_first": "Playback in progress, stop it first.",
        "prompt.stop_record_first": "Recording in progress, stop it first.",
        "loading.hotkeys": "Loading...",
        "hotkey.record": "Record/Stop",
        "hotkey.play": "Play/Stop",
        "hotkey.speed_up": "Speed Up",
        "hotkey.speed_down": "Slow Down",
        "hotkey.toggle_language": "Toggle Language",
        "fatal_error_prompt": "A critical error occurred. Press Enter to exit..."
    }
}

_cache = {}
_base_dir = os.path.dirname(os.path.abspath(__file__))
_lang_dir = os.path.normpath(os.path.join(_base_dir, "..", "lang"))


def _load_lang_file(lang):
    # 从 lang 目录加载指定语言的 JSON 文件
    path = os.path.join(_lang_dir, f"{lang}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        return None
    return None


def _get_lang_map(lang):
    # 获取指定语言的翻译映射，带缓存和兜底
    if lang in _cache:
        return _cache[lang]
    file_map = _load_lang_file(lang)
    if file_map:
        _cache[lang] = file_map
    else:
        _cache[lang] = DEFAULT_TRANSLATIONS.get(lang)
    return _cache[lang]


def list_languages():
    # 列出可用语言代码（lang 目录 + 内置默认）
    langs = set(DEFAULT_TRANSLATIONS.keys())
    try:
        for name in os.listdir(_lang_dir):
            if name.lower().endswith('.json'):
                langs.add(os.path.splitext(name)[0])
    except Exception:
        pass
    return sorted(langs)


def t(key: str, **kwargs) -> str:
    # 翻译入口：优先使用外部 lang 文件，其次使用内置默认 zh 兜底
    lang = settings.config.get("language", "zh")
    lang_map = _get_lang_map(lang) or DEFAULT_TRANSLATIONS.get(lang) or {}
    fallback = DEFAULT_TRANSLATIONS.get("zh", {})
    template = lang_map.get(key) or fallback.get(key) or key
    try:
        return template.format(**kwargs)
    except Exception:
        return template
