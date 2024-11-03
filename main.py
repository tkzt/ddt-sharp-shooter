import json
import pickle
import re
import threading
import time
import tkinter
from queue import Queue

import ddddocr
import pyautogui
from cv import cap_screen, left_side_more_dark, recog_digit
from force import calc_force
from km import space_press_and_release, setup as setup_km

_PRESS_DURATION_PER_FORCE = 4.1 / 100
_DEFAULT_POS_CONFIG = {
    "wind": (0, 0),
    "deg": (0, 0)
}
_aiming = False
_cmd_flag = 0
_cmd_typing = ""
_key_queue = Queue()
_mouse_queue = Queue()
_gui_queue = Queue()
_text: tkinter.Text
_stop_signal = False
_pos_config = _DEFAULT_POS_CONFIG
_map_info = {
    "view_box": (0, 0), # left and right border of the view box
    "enemy": (0, 0),
    "player": (0, 0),
}
_ocr: ddddocr.DdddOcr


def key_listen_queue():
    global _stop_signal
    while not _stop_signal:
        inputs = _key_queue.get()
        handle_inputs(inputs)


def mouse_listen_queue():
    global _stop_signal
    while not _stop_signal:
        if not _aiming:
            continue
        event_str = _mouse_queue.get()
        try:
            down, x, y = json.loads(event_str)
            if down:
                _map_info["player"] = (x, y)
            else:
                _map_info["enemy"] = (x, y)
        except:
            _gui_queue.put("坐标标记失败")
        finally:
            force = resolve_force()
            if force:
                fire(force=force)
            else:
                _gui_queue.put("力度计算失败。")
            reset_inputs()


def resolve_force():
    # Try to resolve from _cmd_typing firstly
    if _cmd_typing:
        var_val = {"w": 0, "x": 0, "y": 0, "d": 0, "f": 0}
        try:
            for var, val in re.findall(r"([fwxyd])(-?\d+.?\d+)", _cmd_typing):
                var_val[var] = float(val)
            if var_val["f"]:
                _gui_queue.put(f"Direct force:\n {var_val['f']}")
                return var_val["f"]
            _gui_queue.put(
                f"Wind: {var_val['w']}，Delta X: {var_val['x']=}，"
                f"Delta Y: {var_val['y']=}，Degree: {var_val['d']}"
            )
            return calc_force(var_val["d"], var_val["w"], var_val["x"], var_val["y"])
        except ValueError:
            _gui_queue.put("输入无效，请检查输入格式。")
            return 0
    # Or else try cv recognizing
    if not any(wind:=_pos_config["wind"]) or not any(deg:=_pos_config["deg"]):
        _gui_queue.put("风力、角度位置未标记。")
        return 0
    if not any(enemy:=_map_info["enemy"]) or not any(player:=_map_info["player"]):
        _gui_queue.put("敌我位置未标记。")
        return 0
    wind_img = cap_screen(wind, 60, 30)
    wind_num = recog_digit(wind_img, _ocr)
    if not wind_num or wind_num == -1:
        _gui_queue.put("风力识别失败:(")
        return 0
    left_dark = left_side_more_dark(wind_img)
    wind_direction = -1 if (
        left_dark and player[0] < enemy[0]
        or not left_dark and player[0] > enemy[0]
    ) else 1
    deg_img = cap_screen(deg)
    deg_value = recog_digit(deg_img)
    if not deg_value or deg_value == -1:
        _gui_queue.put("角度识别失败:(")
        return 0
    delta_x = abs(player[0] - enemy[0])
    delta_y = player[1] - enemy[1]
    return calc_force(deg_value, wind_num/10 * wind_direction, delta_x, delta_y)


def reset_inputs():
    global _cmd_flag, _cmd_typing
    _cmd_flag = 0
    _cmd_typing = ""
    _gui_queue.put("指令输入关闭。")


def handle_inputs(inputs: str):
    """To handle inputs"""
    global _cmd_flag, _cmd_typing, _map_info, _aiming

    # press ESC to cancel
    if inputs == "esc":
        reset_inputs()
    # press the key 't' twice to enable command mode
    elif inputs == "t":
        _cmd_flag += 1
        _cmd_flag %= 3
        if _cmd_flag == 2:
            _gui_queue.put("指令输入开启.。")
        elif _cmd_flag == 0:
            _gui_queue.put("指令输入关闭。")
    elif _cmd_flag == 2:
        if inputs == "d":
            pos = pyautogui.position()
            _pos_config['deg'] = (pos.x, pos.y)
            save_config()
        elif inputs == "w":
            pos = pyautogui.position()
            _pos_config['wind'] = (pos.x, pos.y)
            save_config()
        elif inputs == "l":
            pos = pyautogui.position()
            border = _map_info["view_box"]
            _map_info["view_box"] = (pos.x, border[1])
        elif inputs == "r":
            pos = pyautogui.position()
            border = _map_info["view_box"]
            _map_info["view_box"] = (border[0], pos.x)
        elif inputs == "a":
            # Puts something to trigger aiming.
            _mouse_queue.put("aiming")
            _aiming = True
        elif inputs == "delete":
            _cmd_typing = _cmd_typing[:-1]
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
    _gui_queue.put(f"发射力度: {force}")
    _gui_queue.put("发射!")
    space_press_and_release(calc_duration(force))


def on_destroy(_):
    global _stop_signal
    _stop_signal = True
    # put something to break the km_queue blocking
    _key_queue.put("stop")


def update_text():
    while not _stop_signal:
        if not _gui_queue.empty():
            text = _gui_queue.get(False)
            append_text(text)
        time.sleep(1)


def append_text(text):
    _text.config(state="normal")
    _text.insert("end", f"\n{text}")
    _text.see("end")
    _text.config(state="disabled")


def load_config():
    global _config
    with open("config.dict", "r") as f:
        try:
            _config = pickle.load(f)
        except:
            _config = _DEFAULT_POS_CONFIG


def save_config():
    with open("config.dict", "w") as f:
        pickle.dump(_config, f)


def run():
    global _text, _ocr

    load_config()
    
    _ocr = ddddocr.DdddOcr(show_ad=False)

    tk = tkinter.Tk()
    tk.title("DSS")
    tk.geometry("300x200")
    tk.wm_attributes("-topmost", 1, "-alpha", 0.37)
    tk.bind("<Destroy>", on_destroy)

    _text = tkinter.Text(tk)
    _text.config(
        highlightthickness=0,
        font=("", 12, "bold"),
        padx=12,
        pady=8,
    )
    _text.pack()
    _text.config(state="disabled")

    setup_km(_key_queue, _mouse_queue, _stop_signal)
    threading.Thread(target=update_text).start()
    threading.Thread(target=key_listen_queue).start()
    threading.Thread(target=mouse_listen_queue).start()
    time.sleep(1)

    _gui_queue.put("DSS 初始化完毕!")

    tk.mainloop()


if __name__ == "__main__":
    run()
