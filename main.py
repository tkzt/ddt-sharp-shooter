# -*- coding: utf-8 -*-
"""
To coordinate GUI、Keyboard & Mouse IO

Created by Allen Tao at 2022/5/9 15:22
"""
import multiprocessing
import threading
import time
from queue import Queue
from force import get_force
from km import space_press_and_release, key_press_and_release, run as km_run
from gui import run as gui_run


_PRESS_DURATION_PER_FORCE = 4 / 100
_parameters = {}
_command_flag = -1
_typing = ''
_points = []
_gui_process: multiprocessing.Process
_km_queue = Queue()
_gui_queue = multiprocessing.Queue()


def km_listen_queue():
    while True:
        inputs = _km_queue.get()
        if inputs is None:  # poison bill
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


def resolve_inputs():
    """Resolve inputs to parameters"""
    global _parameters
    _gui_queue.put(f'Inputs typed in: {_typing}')
    _gui_queue.put(f'Points marked: {_points}')
    _gui_queue.put('Resolving..')
    wind_deg_list = _typing.split(' ')
    params = {}

    # wind and degree
    for item in wind_deg_list:
        try:
            if item.startswith('dg'):
                params['deg'] = int(item[2:])
            elif item.startswith('ds'):
                params['dis'] = float(item[2:])
            elif item.startswith('w'):
                params['wind'] = float(item[1:])
            elif item.startswith('f'):
                params['force'] = float(item[1:])
        except ValueError:
            continue

    # points
    points_len = len(_points)
    if points_len == 2 and 'unit' in params:
        params['dis'] = params['unit']*abs(_points[0][0]-_points[1][0])
    elif points_len == 4:
        p1, p2, p3, p4 = _points
        params['unit'] = 10 / abs(p3[0] - p4[0])
        params['dis'] = params['unit']*abs(p1[0]-p2[0])

    # update
    _parameters.update(params)
    _gui_queue.put(f'Parameters :\n  {_parameters}')


def reset_inputs():
    global _command_flag, _typing
    _command_flag = -1
    _typing = ''
    _points.clear()
    _gui_queue.put("输入模式关闭🔒")


def handle_inputs(inputs):
    """To handle inputs"""
    global _command_flag, _typing
    inputs_type = type(inputs)
    if inputs_type==str:
        # press ESC to cancel
        if inputs == 'esc':
            reset_inputs()
        # press the key 't' twice to enable command mode
        elif inputs == 't':
            _command_flag += 1
            if _command_flag == 1:
                _gui_queue.put("指令输入模式开启💡")
        elif _command_flag == 1:
            # press enter to submit command and fire
            if inputs == 'enter':
                resolve_inputs()
                reset_inputs()
                fire()
            # edit command
            elif inputs == 'delete':
                _typing = _typing[:-1]
            else:
                _typing += inputs
        # when not in command mode
        # any key except 't' will reset mode flag
        # which means only consecutive 't' input can enable command mode
        elif _command_flag == 0:
            reset_inputs()
    elif inputs_type == tuple and _command_flag == 1:
        _points.append(inputs)


def calc_duration(force): return _PRESS_DURATION_PER_FORCE*force


def calc_distance():
    p1, p2, p3, p4 = _parameters['points']
    return abs(p1[0]-p2[0])*10/abs(p3[0]-p4[0])


def fire():
    """Steps to fire:
        - Calculate force
        - Press space to store force,
        and then release to fire
    """
    if 'force' in _parameters:
        force = _parameters.get('force')
        time.sleep(1.5)
        _gui_queue.put(f'👊直接指定发射力度: {force}')
        _gui_queue.put('🚀发射!')
        space_press_and_release(calc_duration(force))
        _parameters.pop('force')
    else:
        if 'dis' in _parameters and 'wind' in _parameters and 'deg' in _parameters:
            dis, wind, deg = _parameters.get('dis'), _parameters.get('wind'), _parameters.get('deg')
            # append text
            _gui_queue.put(f'🌪当前风力: {"顺" if wind>0 else ("逆" if wind<0 else "")} {abs(wind)}\n📐当前角度: {deg}°')
            force = get_force(deg, dis)
            time.sleep(1.5)
            if deg == 65:
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
            _gui_queue.put('💔参数缺失, 力度计算失败')


def run():
    global _gui_process, _km_queue
    _gui_process = multiprocessing.Process(target=gui_run, args=(_gui_queue,))
    _gui_process.start()
    time.sleep(1)

    km_run(_km_queue)
    time.sleep(1)

    threading.Thread(target=km_listen_queue).start()
    threading.Thread(target=gui_check_alive).start()


if __name__ == '__main__':
    run()
