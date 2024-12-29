# ipychat: The AI IPython

[![Version](https://img.shields.io/pypi/v/ipychat.svg)](https://pypi.org/project/ipychat/) [![Python Versions](https://img.shields.io/pypi/pyversions/ipychat.svg)](https://pypi.org/project/ipychat/) [![License](https://img.shields.io/pypi/l/ipychat.svg)](https://pypi.org/project/ipychat/)

**ipychat** is an AI IPython REPL that lets you understand, debug, and write better code faster.

<p align="center">
   <img src="https://raw.githubusercontent.com/vinayak-mehta/present/main/demo.gif" width="640">
</p>

## Features

- **Context-Aware**: Automatically uses relevant context from your IPython session
- **Rich Output**: Markdown-formatted responses with syntax highlighting
- **Multiple AI Models**: Supports GPT-4o and Claude 3.5 Sonnet. Local models coming soon.
- **Interactive Configuration**: Easy model switching and configuration through magic commands

## Installation

You can install `ipychat` using pip:

```python
$ pip install ipychat
```

## Usage

You can start the REPL by running the `ipychat` command:

```
$ ipychat
Welcome to ipychat! Use %ask to chat with gpt-4o.
You can change models using %models.

In [1]:
```

Alternatively, you can load the `ipychat` extension in an IPython session:

```
In [1]: %load_ext ipychat
```

You can then start asking the model any question using the `%ask` magic.

```
In [1]: %ask what can I do with the cities dataframe
```

You can change the current model using the `%models` magic.

```
In [1]: %models
```

## Configuration

Based on the model you want to use, either set `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`, or both environment variables. You can also run `ipychat config` to configure `ipychat` interactively.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## Versioning

`ipychat` uses [Semantic Versioning](https://semver.org/). For the available versions, see the tags on the GitHub repository.

## License

This project is licensed under the Apache License, see the [LICENSE](https://github.com/vinayak-mehta/ipychat/blob/master/LICENSE) file for details.
