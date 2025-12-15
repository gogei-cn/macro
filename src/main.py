import sys
import os
import platform
from pynput import keyboard
from .settings import settings
from .utils import Colors, setup_dpi_awareness
from .recorder import MacroRecorder
from .player import MacroPlayer

# 仅在 Windows 上启用 ANSI 颜色修复
if platform.system() == 'Windows':
    os.system('')

setup_dpi_awareness()

recorder = MacroRecorder()
player = MacroPlayer()


def on_press(key):
    if key == settings.get_key('record'):
        if recorder.recording:
            recorder.stop()
        else:
            if player.playing:
                print(f"{Colors.RED}正在回放中，请先停止回放。{Colors.ENDC}")
            else:
                recorder.start()
    elif key == settings.get_key('play'):
        if player.playing:
            player.stop()
        else:
            if recorder.recording:
                print(f"{Colors.RED}正在录制中，请先停止录制。{Colors.ENDC}")
            else:
                player.start(repeats=0)
    elif key == settings.get_key('speed_up'):
        player.speed += 0.5
        print(
            f"\n{Colors.BLUE}[设置] 播放速度已增加至: {player.speed:.1f}x{Colors.ENDC}")
    elif key == settings.get_key('speed_down'):
        player.speed = max(0.1, player.speed - 0.5)
        print(
            f"\n{Colors.BLUE}[设置] 播放速度已降低至: {player.speed:.1f}x{Colors.ENDC}")


def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== 全能宏工具 (by gogei) ==={Colors.ENDC}")
    hk = settings.config['hotkeys']
    print(
        f"{Colors.GREEN}{hk['record'].upper():<8}{Colors.ENDC} : 开始/停止 录制 (鼠标+键盘)")
    print(
        f"{Colors.GREEN}{hk['play'].upper():<8}{Colors.ENDC} : 开始/停止 回放 (无限循环)")
    print(
        f"{Colors.GREEN}{hk['speed_up'].upper():<8}{Colors.ENDC} : 增加回放速度 (+0.5)")
    print(
        f"{Colors.GREEN}{hk['speed_down'].upper():<8}{Colors.ENDC} : 减少回放速度 (-0.5)")

    print(f"{Colors.CYAN}当前配置文件: {settings.filename}{Colors.ENDC}")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
