# 全能宏工具 (Macro Tool)

Macro Tool - lightweight Python macro recorder/player.

基于 Python 的轻量级宏录制与回放工具，支持鼠标轨迹/点击/滚轮和键盘按键的录制、变速回放与循环。

Records mouse move/click/scroll and keyboard keys, with variable-speed looping playback.

## 主要功能 / Features

-   全能录制：鼠标轨迹/点击/滚轮 + 键盘按键。

    Record mouse path/click/scroll plus keyboard keys.

-   回放循环：可循环回放，手动停止即可结束。

    Loop playback until you stop it.

-   速度控制：实时加速/减速，最低 0.1x。

    Live speed control (min 0.1x).

-   彩色界面：ANSI 彩色状态显示。

    ANSI-colored terminal UI.

-   热键控制：全局热键，无需切窗。

    Global hotkeys without switching windows.

-   自定义主题：界面颜色可配置。

    Customizable theme colors.

-   配置持久化：`settings.json` 自定义热键和默认值。

    Persistent settings via `settings.json`.

-   多语言：首启可选语言，语言位于 `lang/`（zh, en, es, fr, ja, ko, zh-TW, ru）。

    Multi-language via `lang/` files (zh, en, es, fr, ja, ko, zh-TW, ru).

-   DPI 感知：适配 Windows 高 DPI。

    DPI awareness on Windows.

## 下载与运行 / Binaries

可从 [Releases](../../releases) 获取可执行文件。

Grab executables from [Releases](../../releases).

-   Windows: `MacroTool-Windows.exe`
-   Linux: `MacroTool-Linux`
-   macOS: `MacroTool-macOS`

首次运行若无 `settings.json` 将提示选择语言。

On first run (no `settings.json`), you will be prompted to choose a language.

## 源码运行 / Run from Source

0. 你需要一个 Python 3.x 环境。 / You need a Python 3.x environment.

1. 安装依赖 / Install dependencies:

```bash
pip install -r requirements.txt
```

2. 运行主程序 / Run the app:

```bash
python src/main.py
```

3. 默认热键 / Default hotkeys：

-   开始/停止录制：F8

    Start/Stop Record: F8

-   开始/停止回放：F9

    Start/Stop Play: F9

-   增加速度：Page Up（+0.5x）

    Speed Up: Page Up (+0.5x)

-   减少速度：Page Down（-0.5x，最低 0.1x）

    Slow Down: Page Down (-0.5x, min 0.1x)

## 配置文件 / settings.json

首次运行自动生成，可手动修改。

Auto-created on first run; you can edit it.

```json
{
    "hotkeys": {
        "record": "f8",
        "play": "f9",
        "speed_up": "page up",
        "speed_down": "page down"
    },
    "default_speed": 1.0,
    "macro_filename": "macro.json",
    "sample_rate": 0.016,
    "language": "zh",
    "theme": {
        "title": "BRIGHT_MAGENTA",
        "border": "BRIGHT_BLACK",
        "label": "CYAN",
        "status_recording": "BRIGHT_RED",
        "status_playing": "BRIGHT_GREEN",
        "progress_bar": "BRIGHT_GREEN",
        "guide_title": "BRIGHT_YELLOW"
    }
}
```

字段说明：

Field notes:

-   `hotkeys.*`: 录制/回放/加速/减速热键。

    `hotkeys.*`: record/play/speed up/speed down hotkeys.

-   `default_speed`: 默认回放倍速。

    `default_speed`: default playback speed multiplier.

-   `macro_filename`: 宏文件保存名。

    `macro_filename`: macro file name.

-   `sample_rate`: 录制采样间隔（秒），默认 0.016（约 60Hz）。

    `sample_rate`: record interval in seconds (default 0.016 ~60Hz).

-   `language`: 语言代码（zh/en/es/fr/ja/ko/zh-TW/ru）。

    `language`: language code (zh/en/es/fr/ja/ko/zh-TW/ru).

-   `theme`: 终端颜色主题，可用 `BRIGHT_*` / 基础色 / `BOLD` / `ENDC`。

    `theme`: terminal colors (`BRIGHT_*`, base colors, `BOLD`, `ENDC`).

## 注意事项 / Notes

-   录制数据默认保存在 `macro.json`。

    Recorded data defaults to `macro.json`.

-   回放时鼠标可能被接管，需停止请按回放热键。

    During playback the mouse may be controlled; stop with the playback hotkey.

-   某些高权限场景可能需要以管理员身份运行终端。

    Some high-privilege contexts may require running the terminal as admin.

## 作者 / Author

作者: gogei (https://gogei.netlify.app/)

Author: gogei (https://gogei.netlify.app/)
