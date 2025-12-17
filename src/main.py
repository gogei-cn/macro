import sys
import os
import platform
from pynput import keyboard

# Handle imports whether running as a package or a script
if __package__:
    from .settings import settings
    from .utils import Colors, setup_dpi_awareness
    from .recorder import MacroRecorder
    from .player import MacroPlayer
    from .logger import logger
    from .display import display
else:
    # Add the current directory to sys.path to ensure imports work
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    from settings import settings
    from utils import Colors, setup_dpi_awareness
    from recorder import MacroRecorder
    from player import MacroPlayer
    from logger import logger
    from display import display

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
                logger.warning("正在回放中，请先停止回放。")
            else:
                recorder.start()
    elif key == settings.get_key('play'):
        if player.playing:
            player.stop()
        else:
            if recorder.recording:
                logger.warning("正在录制中，请先停止录制。")
            else:
                player.start(repeats=0)
    elif key == settings.get_key('speed_up'):
        player.speed += 0.5
        display.update_speed(player.speed)
        logger.info(f"播放速度已增加至: {player.speed:.1f}x")
    elif key == settings.get_key('speed_down'):
        player.speed = max(0.1, player.speed - 0.5)
        display.update_speed(player.speed)
        logger.info(f"播放速度已降低至: {player.speed:.1f}x")


def main():
    # Initialize display with hotkeys
    display.set_hotkeys(settings.config['hotkeys'])
    display.render()
    
    logger.info(f"程序已启动，配置文件: {settings.filename}")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
