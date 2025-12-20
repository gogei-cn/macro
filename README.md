# 全能宏工具 (Macro Tool)

这是一个基于 Python 的轻量级宏录制与回放工具。它可以精确记录您的**鼠标**移动、点击、滚动以及**键盘**按键操作，并支持以不同的速度无限循环回放。非常适合重复性的任务或自动化测试。

## 主要功能

-   **全能录制**: 同时捕获鼠标（轨迹/点击/滚轮）和键盘按键操作。
-   **无限回放**: 支持循环播放录制的宏，直到手动停止。
-   **速度控制**: 支持实时调整回放速度（加速/减速）。
-   **彩色界面**: 终端输出支持 ANSI 彩色显示，状态一目了然。
-   **热键控制**: 全局热键操作，无需切换窗口即可控制录制和回放。
-   **自定义主题**: 支持自定义界面各个部分的颜色。
-   **配置持久化**: 支持通过 `settings.json` 自定义热键和默认设置。
-   **DPI 感知**: 自动处理 Windows 高 DPI 缩放，防止坐标偏移。

## 下载与运行

无需安装 Python 环境，您可以直接从 [Releases](../../releases) 页面下载对应系统的可执行文件：

-   **Windows**: 下载 `MacroTool-Windows.exe`，双击运行。
-   **Linux**: 下载 `MacroTool-Linux`，在终端运行。
    > **注意**: 由于 Linux 发行版环境差异大（如 Wayland/X11、Glibc 版本），如果二进制文件无法运行，请直接使用 [源码运行](#源码运行) 方式。
-   **macOS**: 下载 `MacroTool-macOS`，在终端运行。

首次运行会自动生成 `settings.json` 配置文件。参照下方的热键说明进行操作。

## 源码运行

### 1. 安装依赖

本项目依赖 `keyboard` 和 `mouse` 库。请确保安装了 Python 3.x，并安装必要的依赖库：

```bash
pip install -r requirements.txt
```

> **Linux 用户注意**: 
> 1. 本程序在 Linux 上需要 **Root 权限** 才能访问输入设备。
> 2. 如果遇到 `externally-managed-environment` 错误（常见于 Kali/Debian 12+），请使用虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 运行脚本

在项目根目录下运行：

```bash
# Windows
python src/main.py

# Linux (需要 Root 权限)
sudo python src/main.py
# 如果使用了虚拟环境，请使用虚拟环境中的 python:
sudo ./venv/bin/python src/main.py
```

### 3. 使用热键控制

使用以下默认热键进行控制：

| 功能               | 默认热键    | 说明                                            |
| :----------------- | :---------- | :---------------------------------------------- |
| **开始/停止 录制** | `F8`        | 开始新的录制（鼠标+键盘），再次按下停止并保存。 |
| **开始/停止 回放** | `F9`        | 开始回放当前宏，再次按下停止。                  |
| **增加速度**       | `Page Up`   | 每次增加 0.5x 播放速度。                        |
| **减少速度**       | `Page Down` | 每次减少 0.5x 播放速度 (最低 0.1x)。            |

## 配置文件 (settings.json)

程序首次运行会自动生成 `settings.json`，您可以修改此文件来自定义热键：

```json
{
    "hotkeys": {
        "record": "f8",
        "play": "f9",
        "speed_up": "page_up",
        "speed_down": "page_down"
    },
    "default_speed": 1.0,
    "macro_filename": "macro.json",
    "sample_rate": 0.016,
    "theme": {
        "title": "HEADER",
        "border": "HEADER",
        "label": "BOLD",
        "status_recording": "GREEN",
        "status_playing": "CYAN",
        "progress_bar": "BLUE",
        "guide_title": "BOLD"
    }
}
```

解释：

-   `record`: 录制热键。
-   `play`: 回放热键。
-   `speed_up`: 增加速度热键。
-   `speed_down`: 减少速度热键。
-   `default_speed`: 默认回放速度倍数。
-   `macro_filename`: 录制文件的保存文件。
-   `sample_rate`: 录制采样间隔（秒），越小越精确但文件越大。默认 0.016 (约 60Hz)。
-   `theme`: 界面颜色主题配置。
    -   可用标准颜色: `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`
    -   可用高亮颜色: `BRIGHT_BLACK`, `BRIGHT_RED`, `BRIGHT_GREEN`, `BRIGHT_YELLOW`, `BRIGHT_BLUE`, `BRIGHT_MAGENTA`, `BRIGHT_CYAN`, `BRIGHT_WHITE`
    -   其他: `BOLD`, `ENDC`, `HEADER`

## 注意事项

-   **录制文件**: 录制的数据默认保存在 `macro.json` 中。
-   **停止回放**: 回放过程中，鼠标可能会被程序控制。如果需要停止，请直接按下停止热键 (`F9`)。
-   **管理员权限**: 在某些游戏或高权限应用中使用时，可能需要以管理员身份运行终端。

## 作者

Created by **gogei**
