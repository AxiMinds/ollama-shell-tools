import re
import logging
import subprocess
import time
import sys

def clean_and_validate_command(command):
    """Cleans and validates the generated shell command."""
    # Remove any leading/trailing whitespace and quotes
    command = command.strip().strip("'\"")
    
    # Remove code block formatting
    command = re.sub(r'```\w*\n?|\n?```', '', command)
    
    # Remove any leading 'bash' or '$' prompts
    command = re.sub(r'^(bash\s+|\$\s*)', '', command, flags=re.MULTILINE)
    
    # Remove comments
    command = re.sub(r'#.*$', '', command, flags=re.MULTILINE)
    
    # Replace "/path/to/directory" with "."
    command = command.replace("/path/to/directory", ".")
    
    # Basic set of allowed characters for shell commands (more permissive)
    allowed_pattern = r'^[a-zA-Z0-9\s\.\-_/|><&;()\[\]{}$=+*?!@#%^,:`"]+$'
    
    if re.match(allowed_pattern, command):
        # Additional check for common dangerous commands
        dangerous_commands = ['rm -rf /', 'mkfs', 'dd if=/dev/zero', ':(){ :|:& };:']
        if any(dc in command for dc in dangerous_commands):
            logging.warning(f"Potentially dangerous command detected: {command}")
            return None
        return command
    else:
        logging.warning(f"Invalid characters in command: {command}")
        return None

def execute_shell_command(command):
    """Execute a shell command and return the output and error (if any)."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash')
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command}")
        logging.error(f"Error: {e.stderr}")
        return "", f"Error: {e.stderr.strip()}"

def display_progress(start_time, model_name, active=True):
    """Display a progress indicator with elapsed time for a specific model."""
    elapsed_time = time.time() - start_time
    indicators = ['-', '/', '|', '\\']
    indicator = indicators[int(elapsed_time * 10) % len(indicators)] if active else ' '
    status = "Processing" if active else "Completed"
    sys.stdout.write(f"\r{model_name:<5} {status:<10} {indicator} Elapsed time: {elapsed_time:.2f}s ")
    sys.stdout.flush()
