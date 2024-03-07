import queue
import time
from pynput import keyboard, mouse

_queue: queue.Queue


def on_click(x, y, btn_type, down):
    if btn_type == mouse.Button.left and down:
        _queue.put((int(x), int(y)))


def on_press(event):
    try:
        _queue.put(event.char)
    except AttributeError:
        if event == keyboard.Key.esc:
            _queue.put('esc')
        elif event == keyboard.Key.enter:
            _queue.put('enter')
        elif event == keyboard.Key.space:
            _queue.put(' ')
        elif event == keyboard.Key.backspace:
            _queue.put('delete')


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
    k.release(key)
    time.sleep(0.37)


def run(km_queue):
    global _queue
    _queue = km_queue

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    time.sleep(.5)
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()


if __name__ == '__main__':
    run(None)
    while True:
        time.sleep(1)
