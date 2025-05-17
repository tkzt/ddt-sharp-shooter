import queue
import time
import pyautogui
from pynput import keyboard


RELEASE_CHAR_PREFIX = "r_"
_queue: queue.Queue
_keyboard_listener: keyboard.Listener


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
    pyautogui.keyDown("space")
    time.sleep(duration)
    pyautogui.keyUp("space")


def stop_listen() -> None:
    _keyboard_listener.stop()


def setup(km_queue):
    global _queue, _keyboard_listener
    _queue = km_queue

    _keyboard_listener = keyboard.Listener(on_press=on_press)
    _keyboard_listener.start()


def get_curr_mouse_pos():
    """Get the current mouse position"""
    return pyautogui.position()
