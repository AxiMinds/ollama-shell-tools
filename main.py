import os
from dotenv import load_dotenv
from modules.llm_input_handler import handle_llm_input
from modules.utils import execute_shell_command
from modules.config_loader import load_config

# Load environment variables
load_dotenv()

# Load LLM configuration
llm_config = load_config('config/llm_config.yaml')

def main():
    print("Enter a command or use LLM shortcuts to convert natural language to a command:")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Check if the input is for an LLM (including @ml and @mp)
            if any(user_input.startswith(details['name']) for details in llm_config['llms'].values()):
                handle_llm_input(user_input, llm_config)
            else:
                # Direct shell command execution
                output, error = execute_shell_command(user_input)
                if output:
                    print(f"Output:\n{output}")
                if error:
                    print(f"Error:\n{error}")
        except KeyboardInterrupt:
            print("\nSession interrupted. You can start a new query or exit.")
            continue

if __name__ == "__main__":
    main()
