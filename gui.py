import multiprocessing
import threading
import time
import tkinter

_tk: tkinter.Tk
_text: tkinter.Text
_terminate = False
_queue: multiprocessing.Queue
_terminate_queue: multiprocessing.Queue


def on_destroy(_):
    global _terminate
    _terminate = True


def update_text():
    while not _terminate:
        if not _queue.empty():
            text = _queue.get(False)
            append_text(text)
        else:
            time.sleep(1)


def append_text(text):
    _text.config(state='normal')
    _text.insert('end', f'\n{text}')
    _text.see('end')
    _text.config(state='disabled')


def run(gui_queue):
    global _tk, _text, _queue
    _queue = gui_queue

    _tk = tkinter.Tk()
    _tk.title('DSS')
    _tk.geometry('300x200')
    _tk.wm_attributes('-topmost', 1, '-alpha', .618)
    _tk.bind('<Destroy>', on_destroy)

    _text = tkinter.Text(_tk)
    _text.config(
        highlightthickness=0,
        font=('', 12, 'bold'),
        padx=12,
        pady=8,
    )
    _text.pack()
    _text.insert('end', 'GUI 初始化完毕!🎆')
    _text.config(state='disabled')

    threading.Thread(target=update_text).start()

    _tk.mainloop()


if __name__ == '__main__':
    run(None)

