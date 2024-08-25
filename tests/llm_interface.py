import requests
import json
from modules.config_loader import get_llm_details

def get_llm_command(instruction, model, llm_config, prompts_config):
    """Send instruction to a model via API and stream the shell command."""
    llm_details = get_llm_details(model, llm_config)
    system_prompt = prompts_config['prompts'].get('default', {}).get('system_prompt', '')

    response = requests.post(
        f"{llm_details['url']}:{llm_details['port']}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ],
            "stream": True
        },
        stream=True
    )

    response.raise_for_status()
    command = ""
    last_char = ""
    for chunk in response.iter_lines():
        if chunk:
            chunk_str = chunk.decode('utf-8').replace("data: ", "").strip()
            if chunk_str:
                try:
                    chunk_data = json.loads(chunk_str)
                    if 'choices' in chunk_data:
                        delta_content = chunk_data['choices'][0]['delta'].get('content', '').strip()
                        if delta_content:
                            if not last_char or last_char.endswith(' '):
                                command += delta_content
                            else:
                                command += ' ' + delta_content
                            last_char = delta_content
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON chunk: {chunk_str}")
                    continue
    return command.strip()
