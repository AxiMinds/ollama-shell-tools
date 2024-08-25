import subprocess
import logging
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(filename='tool-proxy.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# API Configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")
base_url = "http://127.0.0.1:11434/v1"  # Use local IP

# Debugging mode
DEBUG = True

# Known shell commands for validation
KNOWN_COMMANDS = {"ls", "cd", "pwd", "echo", "cat", "mkdir", "rm", "uname", "df", "ps", "top", "whoami", "ifconfig", "ip", "du", "sort", "grep", "find", "chmod", "chown"}

# Function to execute shell commands with color output
def execute_shell_command(command):
    """Execute a shell command and return the output, preserving color formatting."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash')
        logging.info(f"Command executed: {command}")
        logging.info(f"Output: {result.stdout}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}")
        logging.error(f"Error: {e.stderr}")
        return f"Error: {e.stderr.strip()}"

# Function to interact with a model via OpenAI-compatible Ollama server with streaming
def get_model_command(instruction, model):
    """Send instruction to a model via Ollama API and stream the shell command."""
    system_prompt = (
        "You are a command-line assistant. Your task is to convert natural language instructions into a single-line shell command. "
        "The command should be executable directly in a Unix-like terminal. Do not provide explanations, comments, or multiple commands. "
        "Just output the command itself. If you're unsure, provide the closest possible command."
    )
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": instruction}
                ],
                "stream": True  # Enable streaming
            },
            stream=True
        )

        response.raise_for_status()

        command = ""
        print("Streaming response:")
        for chunk in response.iter_lines():
            if chunk:
                try:
                    # Parse the JSON data
                    chunk_data = json.loads(chunk.decode('utf-8').replace("data: ", ""))
                    # Extract the content field if it exists
                    if 'choices' in chunk_data:
                        delta_content = chunk_data['choices'][0]['delta'].get('content', '').strip()
                        if delta_content:
                            print(f"{delta_content} ", end="", flush=True)
                            command += delta_content
                except json.JSONDecodeError:
                    logging.error(f"Failed to decode JSON chunk: {chunk}")
                    continue

        print("\n")
        return command.strip()

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to get command from {model}: {str(e)}")
        if DEBUG:
            print(f"Debug: Exception during API call - {str(e)}")
        return f"Error: Failed to get a response from {model}"

# Function to process user input
def process_input(user_input):
    """Process input from the user and execute the appropriate shell command."""
    if user_input.startswith('@l '):
        instruction = user_input[3:]
        command = get_model_command(instruction, "llama3.1")
    elif user_input.startswith('@p '):
        instruction = user_input[3:]
        command = get_model_command(instruction, "phi3")
    else:
        command = user_input
    
    if command and not command.startswith("Error"):
        if command.split()[0] in KNOWN_COMMANDS or command.startswith("#"):  # Allow for comments or script headers
            print(f"\nCommand: {command}\n")
            confirm = input("Press Enter to execute or type 'n' to cancel: ")
            if confirm.lower() != 'n':
                output = execute_shell_command(command)
                print(f"Output:\n{output}")
            else:
                print("Command execution cancelled.")
        else:
            print(f"Error: The response did not return a valid shell command: {command}")
    else:
        print(f"Error: {command}")

# Main loop to accept user input
def main():
    """Main loop to accept user input."""
    print("Enter a command or use @l for LLaMA 3.1 or @p for Phi 3 to convert natural language to a command:")
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            process_input(user_input)
        except KeyboardInterrupt:
            print("\nSession interrupted. You can start a new query or exit.")
            continue

if __name__ == "__main__":
    main()
