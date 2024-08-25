import requests
import json
import logging
import time
import threading
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from modules.utils import display_progress, clean_and_validate_command
from modules.cache_manager import cache_manager
from modules.config import DEBUG

def get_llm_command(instruction, llm_details, start_time, max_retries=3, use_cache=True, timeout=180):
    """Send instruction to a model via Ollama API and stream the shell command."""
    if use_cache:
        try:
            cached_response, metadata = cache_manager.get_from_cache(llm_details['model'], instruction)
            if cached_response:
                print(f"Using cached response for {llm_details['model']} (execution time: {metadata['execution_time']:.2f}s)")
                return cached_response
        except Exception as e:
            logging.error(f"Error accessing cache: {str(e)}")

    base_delay = 0.1
    command = ""
    
    def process_stream():
        nonlocal command
        try:
            url = f"{llm_details['url']}:{llm_details['port']}/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            
            messages = [
                {"role": "system", "content": llm_details['prompts']['system']},
                {"role": "user", "content": f"{llm_details['prompts']['default']} {instruction}"}
            ]
            
            payload = {
                "model": llm_details['model'],
                "messages": messages,
                "stream": True
            }
            
            if llm_details.get('use_json', False):
                payload["response_format"] = {"type": "json_object"}
                messages.append({"role": "system", "content": "Respond with a JSON object containing a 'command' key with the shell command as its value."})

            response = requests.post(url, headers=headers, json=payload, stream=True)
            response.raise_for_status()

            for chunk in response.iter_lines():
                if chunk:
                    try:
                        chunk_data = json.loads(chunk.decode('utf-8').replace("data: ", ""))
                        if chunk_data == "[DONE]":
                            break
                        if 'choices' in chunk_data:
                            delta_content = chunk_data['choices'][0]['delta'].get('content', '')
                            if delta_content:
                                command += delta_content
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get command from {llm_details['model']}: {str(e)}")
            command = f"Error: Failed to get a response from {llm_details['model']}"

    for attempt in range(max_retries):
        command = ""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(process_stream)
            try:
                future.result(timeout=timeout)
            except TimeoutError:
                print(f"\n{llm_details['model']} request timed out after {timeout} seconds.")
                return f"Error: {llm_details['model']} request timed out"

        print(f"\nResponse received from {llm_details['model']}.")
        
        if command.startswith("Error:"):
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying in {base_delay:.1f} seconds...")
                time.sleep(base_delay)
                base_delay += 0.3
                continue
            else:
                return command

        command = clean_and_validate_command(command)
        
        if llm_details.get('use_json', False):
            try:
                # Try to parse the entire response as JSON
                command_json = json.loads(command)
                if isinstance(command_json, dict) and 'command' in command_json:
                    command = command_json['command']
                else:
                    # If parsing succeeds but structure is incorrect, try to extract command
                    command_match = re.search(r'"command"\s*:\s*"([^"]+)"', command)
                    if command_match:
                        command = command_match.group(1)
                    else:
                        raise ValueError("Unexpected JSON structure")
            except (json.JSONDecodeError, ValueError) as e:
                if attempt < max_retries - 1:
                    print(f"Failed to parse JSON response: {e}. Retrying in {base_delay:.1f} seconds...")
                    time.sleep(base_delay)
                    base_delay += 0.3
                    continue
                else:
                    logging.error(f"Failed to parse JSON response after {max_retries} attempts: {command}")
                    return 'Error: Failed to parse JSON response'
        
        if command:
            execution_time = time.time() - start_time
            if use_cache:
                try:
                    cache_manager.add_to_cache(llm_details['model'], instruction, command, {"execution_time": execution_time})
                except Exception as e:
                    logging.error(f"Error adding to cache: {str(e)}")
            return command
        
        if attempt < max_retries - 1:
            print(f"Invalid response. Retrying in {base_delay:.1f} seconds...")
            time.sleep(base_delay)
            base_delay += 0.3

    return "Error: Unable to generate a valid command. Please revise your prompt."

def get_multi_model_command(instruction, llm_config, decision_model, start_time, use_cache=True):
    """Run concurrent requests to multiple models and choose the best response."""
    llama_details = llm_config['llms']['llama3.1']
    phi_details = llm_config['llms']['phi3']
    
    llama_command = None
    phi_command = None
    llama_error = None
    phi_error = None
    
    def get_model_command(model_details, model_name):
        nonlocal llama_command, phi_command, llama_error, phi_error
        model_start_time = time.time()
        try:
            command = get_llm_command(instruction, model_details, model_start_time, use_cache=use_cache)
            if model_name == 'llama3.1':
                llama_command = command
            else:
                phi_command = command
        except Exception as e:
            error = str(e)
            if model_name == 'llama3.1':
                llama_error = error
            else:
                phi_error = error
            logging.error(f"Error in {model_name} command generation: {error}")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        llama_future = executor.submit(get_model_command, llama_details, 'llama3.1')
        phi_future = executor.submit(get_model_command, phi_details, 'phi3')
        
        while not (llama_future.done() and phi_future.done()):
            display_progress(start_time, "LLaMA", not llama_future.done())
            display_progress(start_time, "Phi", not phi_future.done())
            time.sleep(0.1)
    
    print("\nBoth models have responded.")
    
    if DEBUG:
        print(f"LLaMA command: {llama_command}")
        print(f"Phi command: {phi_command}")
    
    if llama_command and not llama_command.startswith("Error:") and phi_command and not phi_command.startswith("Error:"):
        print("Selecting the best command...")
        decision_prompt = f"""Compare these two shell commands and choose the most correct one for the instruction '{instruction}':
1. {llama_command}
2. {phi_command}
Respond with only the number (1 or 2) of the best command, followed by '```' and the chosen command. For example:
1
```ls -l```"""
        
        decision = get_llm_command(decision_prompt, llm_config['llms'][decision_model], time.time(), use_cache=use_cache)
        
        if DEBUG:
            print(f"Decision model response: {decision}")
        
        match = re.search(r'(\d)\s*```(.+?)```', decision, re.DOTALL)
        if match:
            chosen_number = match.group(1)
            chosen_command = match.group(2).strip()
            if chosen_number == "1":
                print("LLaMA command chosen.")
                return chosen_command
            elif chosen_number == "2":
                print("Phi command chosen.")
                return chosen_command
        
        return "Error: Unable to decide between commands. Please try again."
    elif llama_command and not llama_command.startswith("Error:"):
        print("Using LLaMA command as Phi failed or timed out.")
        return llama_command
    elif phi_command and not phi_command.startswith("Error:"):
        print("Using Phi command as LLaMA failed or timed out.")
        return phi_command
    else:
        error_message = "Error: Both models failed to generate valid commands.\n"
        if llama_error:
            error_message += f"LLaMA error: {llama_error}\n"
        if phi_error:
            error_message += f"Phi error: {phi_error}\n"
        error_message += "Please try again."
        return error_message
