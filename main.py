import re
import sys
import threading
import time
import tkinter
from queue import Queue

from pyautogui import Point
from config import dump_config, load_config
from logger import logger, setup_logger
from force import calc_force
from km import (
    get_curr_mouse_pos,
    space_press_and_release,
    setup as setup_km,
    stop_listen as km_stop_listen,
)
from ocr import recognize, recognize_ten_units, recognize_wind

_GAME_CONFIG_PATH = "game_config.json"
_PRESS_DURATION_PER_FORCE = 4.2 / 100
_REF_GAME_REGION_WIDTH = 1500
_WIND_REGION = (709, 22, 84, 54)  # (x, y, w, h)
_DEG_REGION = (43, 835, 64, 36)  # (x, y, w, h)
_MINIMAP_REGION = (1240, 45, 245, 140)  # (x, y, w, h)
_cmd_flag = 0
_cmd_typing = ""
_km_queue = Queue()
_stop_signal = False
_game_config = {
    "region": (0, 0, 0, 0),  # (x, y, w, h)
}
_ten_units_pixels = 0
_enemy_pos: tuple[int, int, int] | None = None  # dx, dy, enemy_left_side
_tmp_pos: Point = None
_tk: tkinter.Tk


def km_listen_queue():
    global _stop_signal
    while not _stop_signal:
        inputs = _km_queue.get()
        handle_inputs(inputs)


def resolve_force():
    """Valid cmds will be like:
    - directly give one force: `l30`
    - calculate force from wind, distance: `x12,y1,w-2,d65`
        means: dx=12, dy=1, wind=-2, degree=65
    """
    var_val = {"w": 0, "x": 0, "y": 0, "d": 0, "l": 0}
    try:
        for var, val in re.findall(r"([lwxyd])(-?\d+.?\d+)", _cmd_typing):
            var_val[var] = float(val)
        if var_val["l"]:
            logger.info(f"Direct force:\n {var_val['l']}")
            return var_val["l"]
        logger.info(
            f"Wind: {var_val['w']}, Delta X: {var_val['x']=}, "
            f"Delta Y: {var_val['y']=}, Degree: {var_val['d']}"
        )
        return calc_force(var_val["d"], var_val["w"], var_val["x"], var_val["y"])
    except ValueError:
        logger.info("输入无效: 请检查输入格式.")


def recognize_and_fire():
    global _ten_units_pixels
    dx, dy, enemy_left_side = _enemy_pos
    x, y, w, _ = _game_config["region"]
    pos_adjust_ratio = w / _REF_GAME_REGION_WIDTH

    if not _ten_units_pixels:
        logger.info("十屏距离未标记，尝试自动识别...")
        rect_res = recognize_ten_units(
            (
                int((x + _MINIMAP_REGION[0]) * pos_adjust_ratio),
                int((y + _MINIMAP_REGION[1]) * pos_adjust_ratio),
                int(_MINIMAP_REGION[2] * pos_adjust_ratio),
                int(_MINIMAP_REGION[3] * pos_adjust_ratio),
            )
        )
        _ten_units_pixels = rect_res

    dx = dx / _ten_units_pixels * 10
    dy = dy / _ten_units_pixels * 10
    logger.info(f"十屏距离: {_ten_units_pixels}, dx: {dx}, dy: {dy}")

    wind, left_more_dark = recognize_wind(
        (
            int(x + _WIND_REGION[0] * pos_adjust_ratio),
            int(y + _WIND_REGION[1] * pos_adjust_ratio),
            int(_WIND_REGION[2] * pos_adjust_ratio),
            int(_WIND_REGION[3] * pos_adjust_ratio),
        )
    )
    wind = wind * (
        -1
        if left_more_dark
        and not enemy_left_side
        or not left_more_dark
        and enemy_left_side
        else 1
    )
    logger.info(f"风速: {wind}")
    deg = recognize(
        (
            int(x + _DEG_REGION[0] * pos_adjust_ratio),
            int(y + _DEG_REGION[1] * pos_adjust_ratio),
            int(_DEG_REGION[2] * pos_adjust_ratio),
            int(_DEG_REGION[3] * pos_adjust_ratio),
        )
    )
    force = calc_force(int(deg), wind, dx, dy)
    fire(force)
    reset_inputs()


def reset_inputs(new_game=False):
    global _cmd_flag, _cmd_typing, _tmp_pos, _ten_units_pixels, _enemy_pos
    if new_game:
        _cmd_flag = 0
        _ten_units_pixels = 0
    _enemy_pos = None
    _cmd_typing = ""
    _tmp_pos = None
    logger.info("指令输入关闭.")


def handle_inputs(inputs: str):
    """To handle inputs"""
    global _cmd_flag, _cmd_typing, _tmp_pos, _ten_units_pixels, _enemy_pos

    if not inputs:
        return

    # press ESC to cancel
    if inputs == "esc":
        reset_inputs(True)
    elif inputs == "q":
        # press 'q' to quit
        logger.info("退出.")
        _tk.quit()
        sys.exit()
    # press the key 't' twice to enable command mode
    elif inputs == "t":
        if _cmd_flag == 2:
            if _enemy_pos or _cmd_typing:
                if _enemy_pos:
                    try:
                        recognize_and_fire()
                    except Exception:
                        logger.info("关键参数识别失败，炸膛！")
                        time.sleep(1)
                elif _cmd_typing:
                    direct_force = resolve_force()
                    if direct_force and direct_force > 0:
                        fire(force=direct_force)
                    else:
                        logger.info("输入无效: 请检查输入格式.")
                        time.sleep(1)
                reset_inputs()
                return
        _cmd_flag += 1
        _cmd_flag %= 3
        if _cmd_flag == 2:
            logger.info("指令输入开启..")
        elif _cmd_flag == 0:
            reset_inputs()
    elif _cmd_flag == 2:
        if inputs == "delete":
            _cmd_typing = _cmd_typing[:-1]
        elif (
            inputs == "r"
        ):  # press and release 'r' to set game region (cooperated with mouse position)
            if _tmp_pos:
                pos = get_curr_mouse_pos()
                _game_config["region"] = (
                    _tmp_pos.x,
                    _tmp_pos.y,
                    pos.x - _tmp_pos.x,
                    pos.y - _tmp_pos.y,
                )
                dump_config(_game_config, _GAME_CONFIG_PATH)
                logger.info(f"游戏区域: {_game_config['region']}")
                _tmp_pos = None
                return
            logger.info("设置游戏区域.")
            _tmp_pos = get_curr_mouse_pos()
        elif inputs == "e":
            if _tmp_pos:
                pos = get_curr_mouse_pos()
                _ten_units_pixels = abs(pos.y - _tmp_pos.y)
                logger.info(f"十屏距离: {_ten_units_pixels}")
                _tmp_pos = None
                return
            logger.info("标记十屏距离.")
            _tmp_pos = get_curr_mouse_pos()
        elif inputs == "w":
            if _tmp_pos:
                pos = get_curr_mouse_pos()
                _enemy_pos = (
                    abs(pos.x - _tmp_pos.x),
                    (_tmp_pos.y - pos.y),
                    _tmp_pos.x > pos.x,
                )
                _tmp_pos = None
                logger.info("标记完成.")
                return
            logger.info("标记敌我.")
            _tmp_pos = get_curr_mouse_pos()
        else:
            _cmd_typing += inputs

    # when not in command mode
    # any key except 't' will reset mode flag
    # which means only consecutive 't' input can enable command mode
    elif _cmd_flag == 1:
        reset_inputs()


def calc_duration(force):
    return _PRESS_DURATION_PER_FORCE * force


def fire(force: int):
    """Steps to fire:
    - Calculate force
    - Press space to store force,
    and then release to fire
    """
    time.sleep(1.5)
    logger.info(f"发射力度: {force}")
    logger.info("发射!")
    space_press_and_release(calc_duration(force))


def on_destroy(_):
    global _stop_signal
    _stop_signal = True
    # put something to break the km_queue blocking
    _km_queue.put("stop")
    km_stop_listen()


def run():
    global _game_config, _tk

    _tk = tkinter.Tk()
    _tk.title("DSS")
    _tk.geometry("370x42")
    _tk.wm_attributes("-topmost", 1, "-alpha", 0.618)
    _tk.bind("<Destroy>", on_destroy)
    _tk.configure(bg="#333333")

    text_widget = tkinter.Text(_tk, border=0, bg="#333333", fg="white")
    text_widget.place(y=10, x=10, height=42)
    text_widget.config(state="disabled")

    setup_logger(text_widget)
    setup_km(_km_queue)
    threading.Thread(target=km_listen_queue).start()

    config = load_config(_GAME_CONFIG_PATH)
    if config:
        _game_config = config

    logger.info(f"DSS 初始化完毕!{'（配置已加载）' if config else ''}")
    _tk.mainloop()


if __name__ == "__main__":
    run()
