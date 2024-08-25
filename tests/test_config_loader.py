import unittest
from modules.config_loader import get_llm_details, load_config

class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.config_data = {
            'llms': {
                'llama3.1': {
                    'name': '@l',
                    'model': 'llama3.1',
                    'url': 'http://127.0.0.1',
                    'port': '11434',
                    'api_key': 'test_api_key',
                    'prompts': {
                        'default': 'Test default prompt'
                    }
                }
            }
        }

    def test_get_llm_details(self):
        llm_details = get_llm_details('llama3.1', self.config_data)
        self.assertEqual(llm_details['port'], '11434')  # Port comparison as string

if __name__ == '__main__':
    unittest.main()
