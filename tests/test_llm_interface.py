import unittest
from unittest.mock import patch, MagicMock
from modules.llm_interface import get_llm_command
from modules.config_loader import load_config

class TestLLMInterface(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.llm_config = load_config('config/llm_config.yaml')
        cls.prompts_config = load_config('config/prompts.yaml')

    @patch('requests.post')
    def test_get_llm_command(self, mock_post):
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            b'data: {"choices":[{"delta":{"content":"ls "}}]}',
            b'data: {"choices":[{"delta":{"content":"-l"}}]}'
        ]
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        command = get_llm_command('list files', 'llama3.1', self.llm_config, self.prompts_config)
        self.assertEqual(command, 'ls -l')

if __name__ == '__main__':
    unittest.main()
