import unittest
from unittest.mock import patch, MagicMock
from modules.commands import process_input

class TestCommandProcessing(unittest.TestCase):
    def setUp(self):
        self.llm_config = {
            'llms': {
                'llama3.1': {
                    'name': '@l',
                    'model': 'llama3.1',
                    'url': 'http://127.0.0.1',
                    'port': '11434',
                    'api_key': 'test_api_key',
                    'prompts': {
                        'default': 'Test default prompt',
                        'list_files': 'Test list files prompt'
                    }
                }
            }
        }

    @patch('modules.commands.get_llm_command')
    def test_process_input_valid_command(self, mock_get_llm_command):
        mock_get_llm_command.return_value = 'ls -l'
        process_input('@l list files', self.llm_config)
        mock_get_llm_command.assert_called_once()

    @patch('modules.commands.get_llm_command')
    def test_process_input_invalid_command(self, mock_get_llm_command):
        mock_get_llm_command.return_value = ''
        process_input('@l list files', self.llm_config)
        mock_get_llm_command.assert_called_once()

if __name__ == '__main__':
    unittest.main()
