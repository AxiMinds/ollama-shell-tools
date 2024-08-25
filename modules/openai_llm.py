OPENAI_AVAILABLE = False
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI module is not available. Some features may be limited.")

import time
from modules.utils import display_progress, clean_and_validate_command

def get_openai_command(instruction, llm_details, start_time, max_retries=3, use_cache=True, timeout=180):
    if not OPENAI_AVAILABLE:
        return "Error: OpenAI module is not available. Please install it to use this feature."

    openai.api_key = llm_details['api_key']
    
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=llm_details['model'],
                messages=[
                    {"role": "system", "content": llm_details['prompts']['system']},
                    {"role": "user", "content": f"{llm_details['prompts']['default']} {instruction}"}
                ],
                temperature=0
            )
            
            command = response.choices[0].message.content.strip()
            command = clean_and_validate_command(command)
            
            if command:
                return command
            
        except Exception as e:
            print(f"Error in OpenAI API call: {str(e)}")
        
        display_progress(start_time, "OpenAI")
        time.sleep(1)
    
    return "Error: Unable to generate a valid command. Please try again."
