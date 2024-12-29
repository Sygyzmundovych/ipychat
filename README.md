# ipychat: AI Chat for Jupyter

[![tests](https://github.com/vinayak-mehta/ipychat/actions/workflows/tests.yml/badge.svg)](https://github.com/vinayak-mehta/ipychat/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/ipychat/badge/?version=latest)](https://ipychat.readthedocs.io/en/latest/)
[![codecov](https://codecov.io/gh/vinayak-mehta/ipychat/branch/main/graph/badge.svg)](https://codecov.io/gh/vinayak-mehta/ipychat)
[![PyPI version](https://badge.fury.io/py/ipychat.svg)](https://badge.fury.io/py/ipychat)
[![License](https://img.shields.io/pypi/l/ipychat.svg)](https://pypi.org/project/ipychat/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ipychat.svg)](https://pypi.org/project/ipychat/)

**ipychat** is a Python library that brings context-aware AI chat to your Jupyter notebooks and IPython shells.

---

**Chat with AI about your code in just a few lines:**

```python
# Start ipychat
%load_ext ipychat

# Create a DataFrame
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})

# Ask about your code
%ask How can I optimize this DataFrame?
```

ipychat automatically includes:
- Variable values and types
- DataFrame shapes and samples
- Function definitions and docstrings
- Recent code execution history

## Features

- **Smart Context**: Automatically understands your code environment
- **Multiple Models**:
  - OpenAI (GPT-4)
  - Anthropic (Claude 3)
- **Debug Mode**: See exactly what context is being sent to models
- **Rich Display**: Beautiful formatting with syntax highlighting
- **Easy Configuration**: Simple CLI for managing settings

## Installation

### Using pip

```bash
pip install ipychat
```

### From source

```bash
git clone https://github.com/vinayak-mehta/ipychat.git
cd ipychat
pip install -e ".[dev]"
```

## Quick Start

1. Initialize ipychat:
```bash
ipychat config
```

2. Start using in Jupyter/IPython:
```python
%load_ext ipychat

# Ask questions
%ask How does this function work?

# Configure models
%models
```

## Configuration

### Environment Variables

Set your API keys:
```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

### Debug Mode

Start with debug mode:
```bash
ipychat --debug
```

## Available Models

| Provider  | Model                    | Description            |
|-----------|-------------------------|------------------------|
| OpenAI    | gpt-4o                 | GPT-4 for code assistance |
| Anthropic | claude-3-sonnet-20240229| Claude 3 Sonnet        |

## Development

### Running Tests

```bash
pytest tests/ -v --cov=ipychat
```

### Project Structure

```
ipychat/
├── src/ipychat/
│   ├── providers/     # AI model providers
│   ├── cli.py        # Command-line interface
│   ├── magic.py      # Jupyter magic commands
│   ├── context.py    # Code context extraction
│   └── models.py     # Model configurations
└── tests/            # Test suite
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0

## Author

Created by [Vinayak Mehta](https://github.com/vinayak-mehta)

---

Made with ❤️ for Jupyter users
