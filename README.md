<div align="center">
  <img src="assets/icon.png" alt="Logo" width="120" height="120" />

# 全能宏工具 (Macro Tool)

**基于 Python 的轻量级宏录制与回放工具**

支持鼠标轨迹/点击/滚轮和键盘按键的录制、变速回放与循环。

[中文版](README.md) | [English](README_EN.md)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

  <br/>
  
  ![Demo](assets/demo.gif)
</div>

## ✨ 主要功能

| 功能              | 说明                                              |
| :---------------- | :------------------------------------------------ |
| 🖱️ **全能录制**   | 支持鼠标轨迹、点击、滚轮以及键盘按键的完整录制。  |
| 🔄 **回放循环**   | 支持无限循环回放，随时手动停止。                  |
| ⏩ **速度控制**   | 实时加速/减速回放，最低支持 0.1x 倍速。           |
| 🎨 **彩色界面**   | 基于 ANSI 的彩色终端界面，状态一目了然。          |
| ⌨️ **热键控制**   | 全局热键支持，无需切换窗口即可控制。              |
| 🛠️ **高度定制**   | 支持自定义主题颜色、热键及默认配置。              |
| 💾 **配置持久化** | 所有配置通过 `settings.json` 保存，重启不丢失。   |
| 🌐 **多语言支持** | 内置多种语言（简/繁中、英、西、法、日、韩、俄）。 |
| 🖥️ **DPI 感知**   | 完美适配 Windows 高 DPI 显示器。                  |

## 🚀 快速开始

### 📦 下载与运行

您可以直接从 [Releases](../../releases) 页面下载对应系统的可执行文件，无需安装 Python 环境。

-   **Windows**: `MacroTool-Windows.exe`
-   **Linux**: `MacroTool-Linux`
-   **macOS**: `MacroTool-macOS`

> 首次运行若无 `settings.json`，程序将提示您选择语言。

### 🐍 源码运行

如果您更喜欢从源码运行，请确保已安装 Python 3.x 环境。

1.  **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

2.  **运行主程序**

    ```bash
    python src/main.py
    ```

3.  **默认热键**

    | 动作     | 热键        | 说明                            |
    | :------- | :---------- | :------------------------------ |
    | **录制** | `F8`        | 开始 / 停止录制                 |
    | **回放** | `F9`        | 开始 / 停止回放                 |
    | **加速** | `Page Up`   | 增加回放速度 (+0.5x)            |
    | **减速** | `Page Down` | 减少回放速度 (-0.5x, 最低 0.1x) |

## ⚙️ 配置文件

配置文件 `settings.json` 会在首次运行时自动生成。您可以手动修改它来定制工具。

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

### 字段说明

-   **`hotkeys`**: 自定义录制、回放及速度控制的热键。
-   **`default_speed`**: 默认的回放倍速。
-   **`macro_filename`**: 录制数据的保存文件名。
-   **`sample_rate`**: 录制采样间隔（秒），默认 `0.016` (约 60Hz)。
-   **`language`**: 界面语言代码 (`zh`, `en`, `es`, `fr`, `ja`, `ko`, `zh-TW`, `ru`)。
-   **`theme`**: 终端颜色主题配置，支持 `BRIGHT_*`、基础颜色、`BOLD` 及 `ENDC`。

## ⚠️ 注意事项

-   **数据保存**: 录制的数据默认保存在当前目录下的 `macro.json` 文件中。
-   **鼠标接管**: 回放期间鼠标会被程序接管，如需停止请直接按下 **回放热键** (默认 F9)。
-   **权限问题**: 在某些高权限场景（如游戏或系统设置页面）下，可能需要以 **管理员身份** 运行终端。

## 📝 许可证

本项目采用 [MIT License](./LICENSE) 许可证。
