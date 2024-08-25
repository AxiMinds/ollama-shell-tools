def list_tools(tools_config):
    """List all available tools."""
    print("Available Tools:")
    for tool_name, tool_details in tools_config['tools'].items():
        print(f"- {tool_name}: {tool_details['description']}")
