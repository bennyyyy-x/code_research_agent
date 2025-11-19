# Code Research Agent

A lightweight **local codebase exploration agent** built using the **Model Context Protocol (MCP)**.

This tool allows an AI model to inspect, search, and analyze your local repositories through a controlled tool interface.

---

## Installation

Clone this repository:

```bash
git clone https://github.com/bennyyyy-x/code_research_agent.git
cd code_research_agent
```

Create and sync your Python environment:

```bash
uv sync
```

Activate the environment:

```bash
source .venv/bin/activate
```

---

## Running the Agent

Before running, add your OpenAI API key to `.env` file

```bash
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

Start the interactive CLI agent:

```bash
python src/client_agent.py
```

You’ll see:

```
Code Research Agent
Type your question about the repo, or 'exit' to quit.
```

Example questions:

- “Set the repo to GitPython”
- “List all files”
- “Search for ‘clone’”
- “Which file handles GPIO toggling in pigpio?”

---

## MCP Tools Implemented

This agent exposes several MCP tools:

| Tool | Description |
|------|-------------|
| `list_projects` | Lists folders under `~/Projects` |
| `set_repo(path)` | Selects the active repository |
| `list_all_files()` | Returns all files in that repo |
| `read_file(path)` | Reads a file’s contents |
| `search_in_repo(query)` | Grep-style search |
| `find_files(name_substring, extension)` | File discovery |

