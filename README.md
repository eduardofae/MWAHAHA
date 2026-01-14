# MWAHAHA
Project for SemEval 2026 Task 1: MWAHAHA - Competition on Humor Generation.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. (Optional) Configure Fuelix API access:
   - Create a `.env` file in the project root
   - Add your API credentials:
   ```
   FUELIX_API_TOKEN=your_api_token_here
   FUELIX_API_URL=https://api.fuelix.ai/v1/chat/completions
   ```

## Usage

The system supports two backends:
- **Ollama** (default): Local model execution with `gemma3:4b`
- **Fuelix**: Private API with models like `claude-sonnet-4-5`, `gpt-5`, `gemini-2.5-flash`

You can configure models independently for the comedian and reviewer agents in `src/run.py`.

### Example: Using Fuelix API
```python
agent = MultiAgent(
    THRESHOLD, TRIES,
    comedian_model='claude-sonnet-4-5',
    comedian_backend='fuelix',
    reviewer_model='gpt-5',
    reviewer_backend='fuelix'
)
```

### Example: Mixing backends
```python
agent = MultiAgent(
    THRESHOLD, TRIES,
    comedian_model='gemini-2.5-flash',
    comedian_backend='fuelix',
    reviewer_model='gemma3:4b',
    reviewer_backend='ollama'
)
```
