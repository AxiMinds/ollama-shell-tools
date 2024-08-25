import curses
import time

class CursesDisplay:
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
        self.model_progress = {}
        self.progress_window = curses.newwin(5, self.width, self.height - 5, 0)
        self.progress_window.scrollok(True)

    def update_progress(self, model_name, status, elapsed_time):
        self.model_progress[model_name] = (status, elapsed_time)
        self._redraw()

    def _redraw(self):
        self.progress_window.clear()
        self.progress_window.addstr(0, 0, "Model Progress:", curses.A_BOLD)
        for i, (model, (status, elapsed_time)) in enumerate(self.model_progress.items(), start=1):
            color = curses.color_pair(1) if status == "Completed" else curses.color_pair(2)
            self.progress_window.addstr(i, 0, f"{model:<10} {status:<10} Elapsed time: {elapsed_time:.2f}s", color)
        self.progress_window.refresh()

    def cleanup(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

display = CursesDisplay()

def display_progress(start_time, model_name, active=True):
    elapsed_time = time.time() - start_time
    status = "Processing" if active else "Completed"
    display.update_progress(model_name, status, elapsed_time)

def show_message(message):
    print(message)  # Use regular print for messages

def cleanup_display():
    display.cleanup()
