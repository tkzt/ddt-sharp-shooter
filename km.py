import json
import queue
import time
import pyautogui as auto_gui
from pynput import keyboard, mouse

_key_queue: queue.Queue
_mouse_queue: queue.Queue
_keyboard_listener: keyboard.Listener
_mouse_listener: mouse.Listener
_stop_signal = False
_listen_mouse_down_up = False


def on_key_press(key: keyboard.KeyCode):
    try:
        _key_queue.put(key.char)
    except AttributeError:
        if key == keyboard.Key.esc:
            _key_queue.put("esc")
        elif key == keyboard.Key.enter:
            _key_queue.put("enter")
        elif key == keyboard.Key.backspace:
            _key_queue.put("delete")


def on_mouse_click(x: int, y: int, button: mouse.Button, pressed: bool):
    global _listen_mouse_down_up

    if not _listen_mouse_down_up:
        return
    click_info = (pressed, x, y)
    _mouse_queue.put(json.dumps(click_info))

    # Once mouse up, stop listening
    if not pressed:
        _listen_mouse_down_up = False


def space_press_and_release(duration):
    """Press the key 'space' down for a while,
    and then release"""
    auto_gui.keyDown("space")
    time.sleep(duration)
    auto_gui.keyUp("space")


def wait_for_stop():
    global _listen_mouse_down_up
    while not _stop_signal:
        if _listen_mouse_down_up:
            time.sleep(1)
            continue
        # Let's say any input emitted from mouse queue
        # will trigger mouse clicking recording
        _mouse_queue.get()
        _listen_mouse_down_up = True
    _keyboard_listener.stop()
    _mouse_listener.stop()



def setup(key_queue, mouse_queue, stop_signal):
    global _queue, _keyboard_listener, _stop_signal, _mouse_listener
    _key_queue = key_queue
    _mouse_queue = mouse_queue
    _stop_signal = stop_signal

    _keyboard_listener = keyboard.Listener(on_press=on_key_press)
    _keyboard_listener.start()

    _mouse_listener = mouse.Listener(on_click=on_mouse_click)
    _mouse_listener.start()
