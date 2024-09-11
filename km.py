import queue
import time
import pyautogui as auto_gui
from pynput import keyboard

_queue: queue.Queue
_keyboard_listener: keyboard.Listener
_stop_signal = False


def on_press(event):
    try:
        _queue.put(event.char)
    except AttributeError:
        if event == keyboard.Key.esc:
            _queue.put("esc")
        elif event == keyboard.Key.enter:
            _queue.put("enter")
        elif event == keyboard.Key.backspace:
            _queue.put("delete")


def space_press_and_release(duration):
    """Press the key 'space' down for a while,
    and then release"""
    auto_gui.keyDown("space")
    time.sleep(duration)
    auto_gui.keyUp("space")


def wait_for_stop():
    while not _stop_signal:
        time.sleep(1)
    _keyboard_listener.stop()


def setup(km_queue, stop_signal):
    global _queue, _keyboard_listener, _stop_signal
    _queue = km_queue
    _stop_signal = stop_signal

    _keyboard_listener = keyboard.Listener(on_press=on_press)
    _keyboard_listener.start()
