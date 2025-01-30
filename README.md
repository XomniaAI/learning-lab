# Trello Agent

A simple agent that can interact with your Trello boards using natural language. Built with [smolagents](https://github.com/smol-ai/smolagents) - a lightweight framework for building AI agents that can use tools and run code.

## Repository Structure

```
.
├── code/
│   ├── tools.py           # Trello API tool implementations
│   └── trello_agent.py    # Agent setup and configuration
├── documentation/         # Documentation for smolagents and Trello API
├── .env.example           # Template for environment variables
└── README.md
```

## Setup

### Prerequisites
- Python 3.10+
- Trello account
- HuggingFace account

### Installation

1. Install `uv` (Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Copy the environment variables file and fill in your credentials:
```bash
cp .env.example .env
```

Required environment variables:
- `TRELLO_API_KEY` & `TRELLO_TOKEN`: If you can access [Trello](https://trello.com/w/xomnia3) you will get these during the training (you'll get a link to make your personal TRELLO_TOKEN with our shared TRELLO_API_KEY: https://trello.com/1/authorize?expiration=1day&scope=read,write&response_type=token&key={TRELLO_API_KEY})
- `HF_TOKEN`: Create at [HuggingFace Settings](https://huggingface.co/settings/tokens) with inference permissions

3. Install dependencies and run:
```bash
uv run code/trello_agent.py
```
This command will create a virtual environment and run the agent with an example prompt.

Alternatively, you can install dependencies separately:
```bash
uv sync
source .venv/bin/activate
python code/trello_agent.py
```

The agent can help you with tasks like:
- Listing your Trello boards, lists, and cards
- Creating new tickets
- Finding tasks to work on

You can use the `code/test_trello_client.ipynb` Jupyter notebook to test the Trello API directly:

## How it Works

This project uses:
- `smolagents`: A lightweight framework for building AI agents
- `py-trello`: Python wrapper for the Trello API

The agent is structured into two main components:
1. `tools.py`: Contains all the Trello API interactions (creating cards, listing boards, etc.)
2. `trello_agent.py`: Sets up the AI agent with the tools and handles natural language processing


## Documentation

Check the `documentation/` folder for detailed information about:
- smolagents library usage and features
- Trello API documentation and examples