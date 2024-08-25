import concurrent.futures
import time
import re
from modules.llm_interface import get_llm_command
from modules.ncurses_display import display_progress, show_message

def get_multi_model_command(instruction, llm_config, multi_model_config, start_time, display, use_cache=True):
    """Run concurrent requests to multiple models and choose the best response."""
    model_commands = {}
    model_errors = {}
    
    def get_model_command(model_name):
        model_details = llm_config['llms'][model_name]
        model_start_time = time.time()
        try:
            command = get_llm_command(instruction, model_details, model_start_time, display, use_cache=use_cache)
            model_commands[model_name] = command
        except Exception as e:
            error = str(e)
            model_errors[model_name] = error
            show_message(f"Error in {model_name} command generation: {error}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(multi_model_config['models'])) as executor:
        future_to_model = {executor.submit(get_model_command, model): model for model in multi_model_config['models']}
        
        while future_to_model:
            done, not_done = concurrent.futures.wait(future_to_model, timeout=0.1, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                model = future_to_model.pop(future)
                display_progress(model, "Completed", time.time() - start_time)
            for model in future_to_model:
                display_progress(model, "Processing", time.time() - start_time)

    show_message("\nAll models have responded.")
    
    valid_commands = {model: cmd for model, cmd in model_commands.items() if cmd and not cmd.startswith("Error:")}
    
    if len(valid_commands) >= 2:
        show_message("Selecting the best command...")
        decision_prompt = multi_model_config['decision_prompt'].format(
            instruction=instruction,
            commands="\n".join([f"{i+1}. {cmd}" for i, cmd in enumerate(valid_commands.values())])
        )
        
        decision_model_details = llm_config['llms'][multi_model_config['decision_model']]
        decision = get_llm_command(decision_prompt, decision_model_details, time.time(), display, use_cache=use_cache)
        
        show_message(f"Decision model response: {decision}")
        
        match = re.search(r'(\d)\s*```(.+?)```', decision, re.DOTALL)
        if match:
            chosen_number = int(match.group(1))
            chosen_command = match.group(2).strip()
            chosen_model = list(valid_commands.keys())[chosen_number - 1]
            show_message(f"{chosen_model} command chosen.")
            return chosen_command
        
        show_message("Error: Unable to decide between commands. Please try again.")
        return "Error: Unable to decide between commands. Please try again."
    elif len(valid_commands) == 1:
        model, command = next(iter(valid_commands.items()))
        show_message(f"Using {model} command as others failed or timed out.")
        return command
    else:
        error_message = "Error: All models failed to generate valid commands.\n"
        for model, error in model_errors.items():
            error_message += f"{model} error: {error}\n"
        error_message += "Please try again."
        show_message(error_message)
        return error_message
