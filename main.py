import re
import threading
import time
import tkinter
from queue import Queue
from force import calc_force
from km import space_press_and_release, setup as setup_km

_PRESS_DURATION_PER_FORCE = 4.1 / 100
_cmd_flag = 0
_cmd_typing = ""
_km_queue = Queue()
_gui_queue = Queue()
_text: tkinter.Text
_stop_signal = False


def km_listen_queue():
    global _stop_signal
    while not _stop_signal:
        if _km_queue.empty():
            return
        inputs = _km_queue.get(block=False)
        handle_inputs(inputs)


def resolve_force():
    """Valid cmds will be like:
    - directly give one force: `f30`
    - calculate force from wind, distance: `x12,y1,w-2,d65`
        means: dx=12, dy=1, wind=-2, degree=65
    """
    if _cmd_typing:
        var_val = {"w": 0, "x": 0, "y": 0, "d": 0, "f": 0}
        try:
            for var, val in re.findall(r"([fwxyd])(-?\d+.?\d+)", _cmd_typing):
                var_val[var] = float(val)
            if var_val["f"]:
                _gui_queue.put(f"Direct force:\n {var_val['f']}")
                return var_val["f"]
            _gui_queue.put(
                f"Wind: {var_val['w']}, Delta X: {var_val['x']=}, "
                f"Delta Y: {var_val['y']=}, Degree: {var_val['d']}"
            )
            return calc_force(var_val["d"], var_val["w"], var_val["x"], var_val["y"])
        except ValueError:
            _gui_queue.put("输入无效: 请检查输入格式.")
    else:
        _gui_queue.put(f"输入无效: {_cmd_typing}")
    return 0


def reset_inputs():
    global _cmd_flag, _cmd_typing
    _cmd_flag = 0
    _cmd_typing = ""
    _gui_queue.put("指令输入关闭.")


def handle_inputs(inputs: str):
    """To handle inputs"""
    global _cmd_flag, _cmd_typing

    # press ESC to cancel
    if inputs == "esc":
        reset_inputs()
    # press the key 't' twice to enable command mode
    elif inputs == "t":
        _cmd_flag += 1
        _cmd_flag %= 3
        if _cmd_flag == 2:
            _gui_queue.put("指令输入开启..")
        elif _cmd_flag == 0:
            _gui_queue.put("指令输入关闭.")
    elif _cmd_flag == 2:
        # press enter to submit command and fire
        if inputs == "enter":
            direct_force = resolve_force()
            if direct_force > 0:
                fire(force=direct_force)
            else:
                _gui_queue.put("力度计算失败.")
            reset_inputs()
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


def run():
    global _text

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

    setup_km(_km_queue, _stop_signal)
    threading.Thread(target=update_text).start()
    threading.Thread(target=km_listen_queue).start()
    time.sleep(1)

    _gui_queue.put("DSS 初始化完毕!")

    tk.mainloop()


if __name__ == "__main__":
    run()
