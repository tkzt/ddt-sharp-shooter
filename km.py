# -*- coding: utf-8 -*-
"""
Keyboard and mouse input/output,
and ScreenGrabbing

Created by Allen Tao at 2022/5/9 15:22
"""
import queue
import time
from pynput import keyboard

_terminate_queue: queue.Queue


def on_press(event):
    from main import handle_inputs
    try:
        if event.char == 'q':
            _terminate_queue.put(None)
        else:
            handle_inputs(event.char)
    except AttributeError:
        if event == keyboard.Key.esc:
            handle_inputs('esc')
        elif event == keyboard.Key.enter:
            handle_inputs('enter')
        elif event == keyboard.Key.space:
            handle_inputs(' ')
        elif event == keyboard.Key.backspace:
            handle_inputs('delete')


def space_press_and_release(duration):
    """Press the key 'space' down for a while,
    and then release"""
    k = keyboard.Controller()
    k.press(keyboard.Key.space)
    time.sleep(duration)
    k.release(keyboard.Key.space)


def key_press_and_release(key):
    """Press certain key several times down,
    and then release immediately"""
    k = keyboard.Controller()
    k.press(key)
    time.sleep(0.185)
    k.release(key)


def run(terminate_queue):
    global _terminate_queue
    _terminate_queue = terminate_queue

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()


if __name__ == '__main__':
    run(None)
    while True:
        time.sleep(1)
