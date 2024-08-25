import sys
import time
from collections import OrderedDict

class ANSIDisplay:
    def __init__(self):
        self.model_progress = OrderedDict()
        self.last_update = time.time()

    def update_progress(self, model_name, status, elapsed_time):
        self.model_progress[model_name] = (status, elapsed_time)
        self._redraw()

    def _redraw(self):
        if time.time() - self.last_update < 0.1:  # Limit updates to 10 per second
            return
        self.last_update = time.time()

        # ANSI escape codes for colors
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        # Move cursor to the bottom of the screen
        sys.stdout.write('\033[s')  # Save cursor position
        sys.stdout.write('\033[9999B')  # Move to bottom

        # Clear the last few lines
        for _ in range(len(self.model_progress) + 2):
            sys.stdout.write('\033[A\033[K')

        sys.stdout.write(f"{BOLD}Model Progress:{RESET}\n")
        for model, (status, elapsed_time) in self.model_progress.items():
            color = GREEN if status == "Completed" else YELLOW
            sys.stdout.write(f"{color}{model:<10} {status:<10} Elapsed time: {elapsed_time:.2f}s{RESET}\n")

        sys.stdout.write('\033[u')  # Restore cursor position
        sys.stdout.flush()

    def show_message(self, message):
        print(message)

display = ANSIDisplay()

def display_progress(start_time, model_name, active=True):
    elapsed_time = time.time() - start_time
    status = "Processing" if active else "Completed"
    display.update_progress(model_name, status, elapsed_time)

def show_message(message):
    display.show_message(message)
