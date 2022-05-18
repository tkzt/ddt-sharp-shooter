# -*- coding: utf-8 -*-
"""
To coordinate GUI、Keyboard & Mouse IO

Created by Allen Tao at 2022/5/9 15:22
"""
import pickle
import io
import multiprocessing
import threading
import time
import pathlib
import screeninfo
from PIL import ImageGrab
from queue import Queue
from force import get_force
from km import space_press_and_release, key_press_and_release, run as km_run
from gui import run as gui_run
from ocr import recognize_digits

_W_D_POINTS_DUMP_NAME = 'wind_degree_points.list'
_PRESS_DURATION_PER_FORCE = 4.1 / 100
_screen_size: tuple
_command_flag = 0
_direct_force_typing = ''
_wind_direction = -1
_distance_unit = 0  # 用于像素与屏距转换
_distance_points = []  # 用于计算 _distance_unit 以及 屏距
_wind_degree_points = []  # 用于配置角度、风力 屏幕截取位置的点
_gui_process: multiprocessing.Process
_km_queue = Queue()
_gui_queue = multiprocessing.Queue()


def km_listen_queue():
    while True:
        inputs = _km_queue.get()
        if inputs is None:  # poison bill
            if len(_wind_degree_points) > 0:
                with open(_W_D_POINTS_DUMP_NAME, 'wb') as f:
                    pickle.dump(_wind_degree_points, f)
            _gui_process.terminate()
            break
        else:  # handle inputs
            handle_inputs(inputs)


def gui_check_alive():
    while True:
        gui_alive = _gui_process.is_alive()
        if not gui_alive:
            _km_queue.put(None)
            break
        else:
            time.sleep(1)


def grab_box(box: tuple) -> bytes:
    import tkinter
    screen = tkinter.Tk()
    bytes_io = io.BytesIO()
    image = ImageGrab.grab().resize((screen.winfo_screenwidth(), screen.winfo_screenheight() )).crop(box)
    image.save(bytes_io, format='png')
    return bytes_io.getvalue()


def analyse_distance():
    global _distance_unit
    distance_points_len = len(_distance_points)
    if distance_points_len >= 4:
        _distance_unit = 10 / abs(_distance_points[2][0]-_distance_points[3][0])

    if _distance_unit and distance_points_len >= 2:
        return _distance_unit * abs(_distance_points[0][0]-_distance_points[1][0])
    return 0


def analyse_direct_force():
    if _direct_force_typing:
        try:
            direct_force = float(_direct_force_typing)
            _gui_queue.put(f'Direct force:\n  {direct_force}')
            return direct_force
        except ValueError:
            _gui_queue.put(f'Failed to analyse direct force.')
    return 0


def analyse_wind():
    if len(_wind_degree_points) == 2:
        try:
            wind_center = _wind_degree_points[1]
            wind_box = (wind_center[0]-20, wind_center[1]-10, wind_center[0]+20, wind_center[1]+10)
            print(wind_box)
            digits = recognize_digits(grab_box(wind_box))
            digits_len = len(digits)
            if digits_len >= 3:
                return float(f'{digits[0]}.{digits[2]}')
            elif digits_len == 2:
                return float(f'{digits[0]}.{digits[1]}')
            elif digits_len == 1:
                return float(digits)
        except ValueError:
            return 0
    return 0


def analyse_degree():
    if len(_wind_degree_points) == 2:
        try:
            degree_center = _wind_degree_points[0]
            degree_box = (degree_center[0]-15, degree_center[1]-15, degree_center[0]+15, degree_center[1]+15)
            digits = recognize_digits(grab_box(degree_box))
            digits_len = len(digits)
            if digits_len >= 1:
                return int(digits[:2])
        except ValueError:
            return 0
    return 0


def reset_inputs():
    global _command_flag, _direct_force_typing, _distance_points
    _command_flag = 0
    _direct_force_typing = ''
    _distance_points.clear()
    _gui_queue.put("指令输入关闭🔒")


def handle_inputs(inputs):
    """To handle inputs"""
    global _command_flag, _direct_force_typing, _wind_direction
    inputs_type = type(inputs)
    if inputs_type==str:
        # press ESC to cancel
        if inputs == 'esc':
            reset_inputs()
        elif inputs == '-':
            _wind_direction = -1
        elif inputs == '=':
            _wind_direction = 1
        # press the key 't' twice to enable command mode
        elif inputs == 't':
            _command_flag += 1
            _command_flag %= 4
            if _command_flag == 2:
                _gui_queue.put("指令输入开启💡")
            elif _command_flag == 0:
                _gui_queue.put("指令输入关闭🔒")
        elif _command_flag == 2:
            # press enter to submit command and fire
            if inputs == 'enter':
                direct_force = analyse_direct_force()
                if direct_force > 0:
                    fire(force=direct_force)
                else:
                    wind, degree, distance = analyse_wind(), analyse_degree(), analyse_distance()
                    reset_inputs()  # reset immediately, in case that degree adjusting fire keyboard events
                    fire(wind, degree, distance)
            # edit command
            elif inputs == 'delete':
                _direct_force_typing = _direct_force_typing[:-1]
            else:
                _direct_force_typing += inputs
        # when not in command mode
        # any key except 't' will reset mode flag
        # which means only consecutive 't' input can enable command mode
        elif _command_flag == 1:
            reset_inputs()
    elif inputs_type == tuple:
        if _command_flag == 2:
            _distance_points.append(inputs)
        if _command_flag == 3:
            if len(_wind_degree_points) == 2:
                _wind_degree_points.clear()
            _wind_degree_points.append(inputs)
            if len(_wind_degree_points) == 1:
                _gui_queue.put('角度位置已标记📐️')
            else:
                _gui_queue.put('风力位置已标记🌪️')


def calc_duration(force): return _PRESS_DURATION_PER_FORCE*force


def fire(wind=None, degree=None, distance=None, force=None):
    """Steps to fire:
        - Calculate force
        - Press space to store force,
        and then release to fire
    """
    if force:
        time.sleep(1.5)
        _gui_queue.put(f'👊直接指定发射力度: {force}')
        _gui_queue.put('🚀发射!')
        space_press_and_release(calc_duration(force))
    elif wind is not None and degree and distance:
        _gui_queue.put(
            f'🌪当前风力: {"顺" if _wind_direction>0 else ("逆" if _wind_direction<0 else "")} {abs(wind)}\n'
            f'📐当前角度: {degree}°'
        )
        force = get_force(degree, distance)
        time.sleep(1.5)
        if degree == 65:
            times = round(wind * 2)
            _gui_queue.put(f'调整角度: 65° -> {65+times}°')
            for _ in range(times):
                key_press_and_release('w' if times > 0 else 's')
                time.sleep(0.185)
        else:
            force += -round(wind)
        _gui_queue.put(f'👊发射力度: {force}')
        _gui_queue.put('🎯发射!')
        space_press_and_release(calc_duration(force))
    else:
        _gui_queue.put(f'- wind: {"None" if wind is None else wind}')
        _gui_queue.put(f'- degree: {degree}')
        _gui_queue.put(f'- distance: {distance}')
        _gui_queue.put('💔参数缺失, 力度计算失败')


def run():
    global _gui_process, _km_queue, _wind_degree_points, _screen_size

    monitors = screeninfo.get_monitors()
    if len(monitors) > 0:
        _screen_size = (monitors[0].width, monitors[0].height)

        _gui_process = multiprocessing.Process(target=gui_run, args=(_gui_queue,))
        _gui_process.start()

        km_run(_km_queue)

        threading.Thread(target=km_listen_queue).start()
        threading.Thread(target=gui_check_alive).start()

        wind_degree_path = pathlib.Path(_W_D_POINTS_DUMP_NAME)
        if wind_degree_path.exists():
            with open(wind_degree_path, 'rb') as f:
                _wind_degree_points = pickle.load(f)
                if len(_wind_degree_points) == 2:
                    _gui_queue.put('角度、风力位置已加载:')
                    _gui_queue.put(f'📐角度位置: {_wind_degree_points[0]}')
                    _gui_queue.put(f'🌪️风力位置: {_wind_degree_points[1]}')
                else:
                    _wind_degree_points.clear()
                    _gui_queue.put('角度、风力位置加载失败❌')
        if len(_wind_degree_points) == 0:
            _gui_queue.put('按下三次 t 而后点击屏幕以设置角度、风力位置，而后按下 ESC 退出、完成设置')

        _gui_queue.put('DSS is ready!🚀')
    else:
        _gui_queue.put('获取屏幕信息失败❌')


if __name__ == '__main__':
    run()
