import curses
import time
from collections import OrderedDict

class NCursesDisplay:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_RED, -1)
        self.height, self.width = self.stdscr.getmaxyx()
        self.model_progress = OrderedDict()
        self.messages = []
        self.input_window = curses.newwin(1, self.width, self.height-1, 0)

    def update_progress(self, model_name, status, elapsed_time):
        self.model_progress[model_name] = (status, elapsed_time)
        self._redraw()

    def show_message(self, message):
        self.messages.extend(message.split('\n'))
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
        for i, message in enumerate(self.messages[-self.height+start_line+1:], start=start_line):
            self.stdscr.addstr(i, 0, message[:self.width-1])

        self.stdscr.refresh()

    def get_input(self, prompt):
        self.input_window.clear()
        self.input_window.addstr(0, 0, prompt)
        self.input_window.refresh()
        curses.echo()
        user_input = self.input_window.getstr().decode('utf-8')
        curses.noecho()
        return user_input

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

def cleanup_display(display):
    if display:
        display.cleanup()

def display_progress(model_name, status, elapsed_time):
    # This function will be called from other modules, but we can't use it directly
    # Instead, we'll pass the display object to those modules
    pass

def show_message(message):
    # This function will be called from other modules, but we can't use it directly
    # Instead, we'll pass the display object to those modules
    pass

def get_input(prompt):
    # This function will be called from other modules, but we can't use it directly
    # Instead, we'll pass the display object to those modules
    pass
