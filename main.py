# -*- coding: utf-8 -*-
"""
To coordinate GUI、Keyboard & Mouse IO

Created by Allen Tao at 2022/5/9 15:22
"""
import time
from queue import Queue
from force import get_force
from km import space_press_and_release, key_press_and_release, run as km_run

_PRESS_DURATION_PER_FORCE = 4 / 100
_terminate = False
_terminate_queue = Queue()
_parameters = {}
_command_flag = -1
_typing = ''


def resolve_inputs():
    """Resolve inputs to parameters"""
    global _parameters
    print(f'Inputs typed in: {_typing}. resolving..')
    wind_deg_list = _typing.split(' ')
    params = {}

    # wind and degree
    for item in wind_deg_list:
        try:
            if item.startswith('m'):
                params['mode'] = int(item[1:])
            elif item.startswith('d'):
                params['dis'] = float(item[1:])
            elif item.startswith('w'):
                params['wind'] = float(item[1:])
            elif item.startswith('f'):
                params['force'] = float(item[1:])
        except ValueError:
            continue

    # update
    _parameters.update(params)
    print(f'Current parameters: {_parameters}')


def reset_inputs():
    global _command_flag, _typing
    _command_flag = -1
    _typing = ''


def handle_inputs(inputs):
    """To handle inputs"""
    global _command_flag, _typing
    # press ESC to cancel
    if inputs == 'esc':
        reset_inputs()
    # press the key 't' twice to enable command mode
    elif inputs == 't':
        _command_flag += 1
    elif _command_flag == 1:
        # press enter to submit command and fire
        if inputs == 'enter':
            resolve_inputs()
            fire()
            reset_inputs()
        # edit command
        elif inputs == 'delete':
            _typing = _typing[:-1]
        else:
            _typing += inputs
    # when not in command mode
    # any key except 't' will reset mode flag
    # which means only consecutive 't' input can enable command mode
    elif _command_flag == 0:
        _command_flag = -1


def calc_duration(force): return _PRESS_DURATION_PER_FORCE*force


def fire():
    """Steps to fire:
        - Calculate force
        - Press space to store force,
        and then release to fire
    """
    if 'force' in _parameters:
        force = _parameters.get('force')
        time.sleep(1.5)
        print(f'👊 直接指定发射力度: {force}')
        print('🚀 发射!')
        space_press_and_release(calc_duration(force))
        _parameters.pop('force')
    else:
        if 'dis' in _parameters and 'wind' in _parameters and 'mode' in _parameters:
            dis, wind, mode = _parameters.get('dis'), _parameters.get('wind'), _parameters.get('mode')
            # append text
            print(f'🌪️ 当前风力: {"顺" if wind>0 else ("逆" if wind<0 else "")} {abs(wind)}\n📐 当前模式: {mode}°')
            force = get_force(mode, dis)
            time.sleep(1.5)
            if mode == 65:
                times = round(wind * 2)
                print(f'调整角度: 65° -> {65+times}°')
                for _ in range(times):
                    key_press_and_release('w' if times > 0 else 's')
                    time.sleep(0.185)
            else:
                force += -round(wind)

            print(f'👊 发射力度: {force}')
            print('🚀 发射!')
            space_press_and_release(calc_duration(force))
        else:
            print('💔 参数缺失, 力度计算失败')


def run():
    km_run(_terminate_queue)
    time.sleep(1)
    _terminate_queue.get()


if __name__ == '__main__':
    run()
