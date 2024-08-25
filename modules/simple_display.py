import time
from collections import OrderedDict

class SimpleDisplay:
    def __init__(self):
        self.model_progress = OrderedDict()

    def update_progress(self, model_name, status, elapsed_time):
        self.model_progress[model_name] = (status, elapsed_time)
        self._redraw()

    def _redraw(self):
        print("\nModel Progress:")
        for model, (status, elapsed_time) in self.model_progress.items():
            print(f"{model:<10} {status:<10} Elapsed time: {elapsed_time:.2f}s")
        print()  # Add an extra newline for separation

    def show_message(self, message):
        print(message)

display = SimpleDisplay()

def display_progress(start_time, model_name, active=True):
    elapsed_time = time.time() - start_time
    status = "Processing" if active else "Completed"
    display.update_progress(model_name, status, elapsed_time)

def show_message(message):
    display.show_message(message)
