import os
import atexit
import curses
from dotenv import load_dotenv
from modules.llm_input_handler import handle_llm_input
from modules.utils import execute_shell_command
from modules.config_loader import load_config
from modules.ncurses_display import NCursesDisplay, cleanup_display

# Load environment variables
load_dotenv()

# Load LLM configuration
llm_config = load_config('config/llm_config.yaml')

def main(stdscr):
    try:
        # Initialize the ncurses display
        display = NCursesDisplay(stdscr)
        
        # Register cleanup function
        atexit.register(cleanup_display, display)

        display.show_message("Enter a command or use LLM shortcuts to convert natural language to a command:")
        display.show_message("Type 'exit' or 'quit' to end the program.")

        while True:
            try:
                user_input = display.get_input("> ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                # Check if the input is for an LLM or a special command
                if user_input.startswith(('@', '--')):
                    handle_llm_input(user_input, llm_config, display)
                else:
                    # Direct shell command execution
                    output, error = execute_shell_command(user_input)
                    if output:
                        display.show_message(f"Output:\n{output}")
                    if error:
                        display.show_message(f"Error:\n{error}")
            except KeyboardInterrupt:
                display.show_message("\nSession interrupted. You can start a new query or exit.")
                continue
            except Exception as e:
                display.show_message(f"An error occurred: {str(e)}")
                continue

    except Exception as e:
        cleanup_display(display)
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    curses.wrapper(main)
