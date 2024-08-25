# user_input_handler.py

from modules.utils import execute_shell_command

def handle_user_input(command):
    """Handles direct shell commands from the user."""
    command = command.strip()
    if command:
        output = execute_shell_command(command)
        print(f"Command: {command}")
        print(f"Output:\n{output}")
    else:
        print("Error: No command provided.")
