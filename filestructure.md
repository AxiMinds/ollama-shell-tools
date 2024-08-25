/tool-usage/
├── main.py                          # Main entry script
├── modules/                         # Directory for modules
│   ├── commands.py                  # Command-related functions
│   ├── llm_interface.py             # LLM interaction logic
│   ├── tools/                       # Directory for tool modules
│   │   ├── list_tools.py            # Example tool for listing tools
│   │   └── example_tool.py          # Example custom tool
│   ├── utils.py                     # Utility functions (e.g., logging, validation)
│   └── config_loader.py             # Configuration loader for YAML files
├── config/                          # Directory for configuration files
│   ├── llm_config.yaml              # YAML file for LLM configurations
│   ├── prompts.yaml                 # YAML file for prompts
│   └── tools_config.yaml            # YAML file for tool configurations
├── tests/                           # Directory for unit tests
│   ├── test_commands.py             # Unit tests for commands
│   ├── test_llm_interface.py        # Unit tests for LLM interface
│   └── test_tools.py                # Unit tests for tools
└── README.md                        # Documentation
