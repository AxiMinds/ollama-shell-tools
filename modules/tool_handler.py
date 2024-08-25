# tool_handler.py

def handle_tool_command(command):
    """Handles commands prefixed with '/tool'."""
    tool_command = command.split()[0][6:]  # Extracts the specific tool command
    if tool_command == "list":
        print("Available tools:")
        # List available tools
    elif tool_command == "toolname":
        print("Running toolname...")
        # Execute the specific tool's functionality
    else:
        print(f"Unknown tool command: {tool_command}")
