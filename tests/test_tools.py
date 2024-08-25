import unittest
from io import StringIO
from unittest.mock import patch
from modules.tools.list_tools import list_tools
from modules.config_loader import load_config

class TestTools(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.tools_config = load_config('config/tools_config.yaml')

    @patch('sys.stdout', new_callable=StringIO)
    def test_list_tools(self, mock_stdout):
        list_tools(self.tools_config)
        output = mock_stdout.getvalue()
        self.assertIn("Available Tools:", output)
        self.assertIn("list_tools", output)
        self.assertIn("example_tool", output)

if __name__ == '__main__':
    unittest.main()
