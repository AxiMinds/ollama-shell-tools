from modules.user_input_handler import handle_user_input
from modules.llm_input_handler import handle_llm_input
from modules.tool_handler import handle_tool_command

def process_input(user_input, llm_config):
    """Process input from the user and route to the appropriate handler."""

    # Strip any leading/trailing whitespace from the user's input
    command = user_input.strip()

    # 1. Check if the input starts with an LLM prefix (@)
    if command.startswith('@'):
        for model_key, details in llm_config['llms'].items():
            if command.startswith(details['name']):
                # Handle the input as an LLM command with HITL process
                iterations = 1  # Default to 1 iteration
                user_input_parts = command.split()
                if user_input_parts[-1].isdigit():
                    iterations = int(user_input_parts.pop())
                    command = " ".join(user_input_parts)

                handle_llm_input(command, llm_config, max_iterations=iterations)
                return  # Exit after handling the LLM command

        # If no matching LLM prefix is found, inform the user
        print("Error: The input did not match any known LLM prefix.")

    # 2. Check if the input starts with a Tool prefix (/)
    elif command.startswith('/'):
        handle_tool_command(command)
        return  # Exit after handling the tool command

    # 3. If the command doesn't start with @ or /, handle it as a direct shell command
    else:
        handle_user_input(command)
