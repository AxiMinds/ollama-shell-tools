ANTHROPIC_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("Warning: Anthropic module is not available. Some features may be limited.")

import time
from modules.utils import display_progress, clean_and_validate_command

def get_anthropic_command(instruction, llm_details, start_time, max_retries=3, use_cache=True, timeout=180):
    if not ANTHROPIC_AVAILABLE:
        return "Error: Anthropic module is not available. Please install it to use this feature."

    client = anthropic.Client(api_key=llm_details['api_key'])
    
    for attempt in range(max_retries):
        try:
            response = client.completions.create(
                model=llm_details['model'],
                prompt=f"{llm_details['prompts']['system']}\n\n{llm_details['prompts']['default']} {instruction}",
                max_tokens_to_sample=100,
                temperature=0
            )
            
            command = response.completion.strip()
            command = clean_and_validate_command(command)
            
            if command:
                return command
            
        except Exception as e:
            print(f"Error in Anthropic API call: {str(e)}")
        
        display_progress(start_time, "Anthropic")
        time.sleep(1)
    
    return "Error: Unable to generate a valid command. Please try again."
