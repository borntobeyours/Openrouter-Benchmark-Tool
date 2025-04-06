# OpenRouter Simple Benchmark Tool

A benchmarking tool for comparing multiple language models via OpenRouter API with automated response evaluation using LLMs.

## Features

- Benchmark multiple LLMs (OpenAI, Anthropic, Google, Mistral, Llama, etc.)
- Automated evaluator scoring using GPT-4 or other LLMs
- Cost estimation per 1K tokens
- Streamlit-based UI for easy interaction
- Supports adding custom prompts and models
- Saves detailed logs of benchmark results

## Setup

### 1. Clone the repository

```bash
git clone https://your-repo-url.git
cd openrouter-benchmark
```

### 2. Create and activate a virtual environment (optional but recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set API keys

Create a `.env` file in the root directory with your OpenRouter API key:

```
OPENROUTER_API_KEY=your_openrouter_api_key
```

For UI-side evaluation (optional), set your OpenAI API key as environment variable or within your code.

### 5. Prepare prompts

Edit or add prompts in `prompts/default_prompts.json`.

## Usage

### Run the Streamlit UI

```bash
streamlit run app/ui.py
```

### Benchmarking

- Select models and prompt categories in the UI.
- Click **Run Benchmark**.
- View latency, response length, estimated cost, and evaluator scores.
- Results are saved in the `logs/` directory as JSON files.

## Evaluation

- The tool uses an LLM (e.g., GPT-4) to automatically rate each response from 1 to 10.
- Scores are saved and displayed in the UI.
- You can customize the evaluation prompt or logic in `src/utils.py` and `app/ui.py`.

## File Structure

- `src/` - Core benchmarking and evaluation logic
- `app/` - Streamlit UI
- `logs/` - Saved benchmark results
- `prompts/` - Prompt templates
- `.env` - API keys (not committed)

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- [OpenRouter](https://openrouter.ai)
- [Streamlit](https://streamlit.io)
- OpenAI, Anthropic, Google, Mistral, Meta for their models