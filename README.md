# Jarvis

A minimal AI coding agent built while working through the [boot.dev](https://boot.dev) AI agent course. Jarvis takes a natural-language prompt, figures out which tools it needs, and calls them in a loop until it can give you a final answer — the same basic pattern behind tools like Claude Code or Cursor's agent mode, just stripped down to its essentials.

> **⚠️ Learning project — not production-ready.** Jarvis doesn't have the full security and safety hardening a real AI agent needs. Don't hand this to other people to run against directories you care about.

## How it works

Jarvis runs a simple agentic loop:

1. Send the system prompt + your request to the LLM, along with a list of tools it's allowed to call.
2. The model replies with either a final text answer, or a request to call one or more tools.
3. If it's a final answer, print it and stop.
4. If it's a tool request, run the tool(s) locally, feed the result(s) back into the conversation, and go back to step 1.

This repeats for up to 20 iterations, which is a safety cap in case the model gets stuck asking for tools without ever converging on an answer.

```
system prompt + user prompt
        │
        ▼
   ┌─────────┐   tool call    ┌──────────────┐
   │   LLM   │ ─────────────► │  run locally │
   └─────────┘                └──────────────┘
        ▲                            │
        │        tool result         │
        └────────────────────────────┘
        │
        ▼ (no more tool calls)
   final answer printed
```

## Tools

Jarvis can call four tools, all scoped to a single sandboxed working directory (`./calculator` by default):

| Tool | What it does |
|---|---|
| `get_files_info` | Lists files/directories with size and type info |
| `get_file_content` | Reads a file's contents (truncated at 10,000 characters) |
| `write_file` | Writes or overwrites a file, creating parent directories as needed |
| `run_python_file` | Executes a `.py` file with optional CLI args (30s timeout) |

**Sandboxing:** every tool resolves the requested path against the working directory, collapses any `..` segments, and verifies the result still lives inside the sandbox *before* touching the filesystem. Paths that try to escape the working directory are rejected with an error instead of being followed.

## Project structure

```
jarvis/
├── main.py                   # entry point: CLI args, the agent loop
├── call_function.py          # dispatches tool calls, injects the working directory
├── prompts.py                 # system prompt for the agent
├── config.py                    # shared constants (e.g. MAX_CHARS)
├── functions/
│   ├── get_files_info.py
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python_file.py
├── tests/                      # unit tests for each tool function
└── calculator/                  # sandboxed demo app the agent operates on
```

## Setup

Requires Python 3.13+ and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Abdo-N/Jarvis.git
cd Jarvis
uv sync
```

Create a `.env` file in the project root with your [OpenRouter](https://openrouter.ai/) API key:

```
OPENROUTER_API_KEY=your_key_here
```

## Usage

```bash
uv run main.py "your prompt here"
```

Add `--verbose` to see prompt/response token counts and the exact arguments each tool call is made with:

```bash
uv run main.py "list the files in the working directory" --verbose
```

### Example

```bash
uv run main.py "what does main.py in the calculator app do?"
```

Jarvis will call `get_files_info` to see what's there, then `get_file_content` to read `main.py`, and finally respond with a summary — all without you specifying any file paths by hand.

## Running tests

```bash
uv run python -m tests.test_get_files_info
uv run python -m tests.test_get_file_content
uv run python -m tests.test_write_file
uv run python -m tests.test_run_python_file
```

(Run from the project root — not from inside `tests/` — since that's how `sys.path` gets set up correctly.)
