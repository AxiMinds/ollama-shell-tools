import yaml

def load_config(file_path):
    """Load a YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def get_llm_details(model, llm_config):
    """Retrieve LLM details from the configuration."""
    return llm_config['llms'].get(model, {})
