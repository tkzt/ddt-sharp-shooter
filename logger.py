import logging
import tkinter as tk


logger = logging.getLogger(__name__)


def setup_logger(text_widget):
    """
    Set up the logger for the application.
    """
    logger.setLevel(logging.INFO)
    logger.addHandler(redirect_output_to_text_widget(text_widget))


def redirect_output_to_text_widget(text_widget):
    class TextHandler(logging.Handler):
        def __init__(self, text_widget):
            logging.Handler.__init__(self)
            self.text_widget = text_widget

        def emit(self, record):
            msg = self.format(record)

            def append():
                self.text_widget.configure(state="normal")
                self.text_widget.insert(tk.END, msg + "\n")
                self.text_widget.see(tk.END)
                self.text_widget.configure(state="disabled")

            self.text_widget.after(0, append)

    return TextHandler(text_widget)
