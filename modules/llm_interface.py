import curses
import time
from collections import OrderedDict

class NCursesDisplay:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        self.height, self.width = self.stdscr.getmaxyx()
        self.model_progress = OrderedDict()
        self.messages = []

    def update_progress(self, model_name, status, elapsed_time):
        self.model_progress[model_name] = (status, elapsed_time)
        self._redraw()

    def show_message(self, message):
        self.messages.append(message)
        self._redraw()

    def _redraw(self):
        self.stdscr.clear()
        
        # Draw model progress
        self.stdscr.addstr(0, 0, "Model Progress:", curses.A_BOLD)
        for i, (model, (status, elapsed_time)) in enumerate(self.model_progress.items(), start=1):
            color = curses.color_pair(1) if status == "Completed" else curses.color_pair(2)
            self.stdscr.addstr(i, 0, f"{model:<10} {status:<10} Elapsed time: {elapsed_time:.2f}s", color)

        # Draw messages
        start_line = len(self.model_progress) + 2
        for i, message in enumerate(self.messages[-10:], start=start_line):
            self.stdscr.addstr(i, 0, message[:self.width-1])

        self.stdscr.refresh()

    def get_input(self, prompt):
        self.stdscr.addstr(self.height-1, 0, prompt)
        curses.echo()
        user_input = self.stdscr.getstr(self.height-1, len(prompt)).decode('utf-8')
        curses.noecho()
        return user_input

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

display = NCursesDisplay()

def display_progress(model_name, status, elapsed_time):
    display.update_progress(model_name, status, elapsed_time)

def show_message(message):
    display.show_message(message)

def get_input(prompt):
    return display.get_input(prompt)

def cleanup_display():
    display.cleanup()
