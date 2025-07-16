# AI-Researcher Semi-Auto

## Overview
This project is an automated research workflow system that generates a full research paper from a topic, using LLMs and tool APIs.

## Requirements
- Python 3.8+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py "Your research topic here"
```

- The generated paper will be saved as `code_workspace/final_paper.tex`.
- You can change the workspace directory in `main.py` or `workflow.py` if needed.

## Project Structure
- `main.py`: Entry point, takes topic from command line.
- `workflow.py`: Main workflow logic, orchestrates all agents.
- `agents/`: All agent modules (query, search, idea, method, code, experiment, writing, etc.)
- `llm_utils/`: LLM utility functions.
- `requirements.txt`: Python dependencies.

## Troubleshooting
- Ensure all dependencies are installed.
- If you see import errors, check your PYTHONPATH and package structure.
- If tool server APIs are not reachable, check the tool server is running and accessible at the configured URL (default: http://localhost:8001).
- For LLM API issues, ensure your API key in `config.py` is valid.

## Extending
- You can add new agents in the `agents/` directory and integrate them in `workflow.py`.
- Prompts and system messages can be customized in each agent.

## License
MIT 