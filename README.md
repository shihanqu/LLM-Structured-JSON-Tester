
# LLM JSON Output & Logic Tester

Needed to figure out which Local models I could count on to consistently follow json SCHEMA. Hence this Python script designed to test and validate the ability of LLMs to generate structured JSON output. 

It is pre-configured to work with local LLM servers like [LM Studio](https://lmstudio.ai/), but can be easily adapted for any OpenAI-compatible API.

Here's an example output on an 96gb M3 Max for the script as shown:

```text
========================================
           FINAL TEST SUMMARY
========================================

❌ openai/gpt-oss-20b: 0/10 passed (0.0%) | Avg Speed: 45.07 tok/s
  6 Incomplete Response Errors
  1 Schema Violation Error
  3 Timeout Error Errors

❌ openai/gpt-oss-120b: 0/10 passed (0.0%) | Avg Speed: 17.03 tok/s
  5 Incomplete Response Errors
  5 Timeout Error Errors

✅ qwen/qwen3-next-80b: 10/10 passed (100.0%) | Avg Speed: 31.55 tok/s

❌ qwen/qwen3-vl-30b: 9/10 passed (90.0%) | Avg Speed: 45.93 tok/s
  1 Incomplete Response Error

✅ qwen/qwen3-30b-a3b-2507: 10/10 passed (100.0%) | Avg Speed: 45.92 tok/s

✅ qwen/qwen3-4b-thinking-2507: 10/10 passed (100.0%) | Avg Speed: 36.06 tok/s

✅ mistralai/magistral-small-2509: 10/10 passed (100.0%) | Avg Speed: 13.78 tok/s

❌ mradermacher/apriel-1.5-15b-thinker: 0/10 passed (0.0%) | Avg Speed: 25.30 tok/s
  10 Incomplete Response Errors

❌ glm-4.5-air: 5/10 passed (50.0%) | Avg Speed: 25.45 tok/s
  5 Incomplete Response Errors

❌ deepseek-r1-0528-qwen3-8b-mlx: 8/10 passed (80.0%) | Avg Speed: 22.57 tok/s
  2 Incomplete Response Errors
```

## 🚀 Features

This checks syntax and validates LLM reliability on several levels:

*   **JSON Schema Validation**: Ensures the output strictly adheres to a predefined structure (using `jsonschema`).
*   **Logical Completeness**: Verifies that the model actually processed the entire prompt (e.g., if you asked for 10 items, it ensures 10 items were returned).
*   **Sanity Checks**: Uses heuristic regex checks to fail runs that produce "gibberish" or repetitious loops, even if technically valid JSON.
*   **Performance Metrics**: Tracks and averages generation speed (tokens/second) for every run.
*   **Detailed Error Reporting**: Categorizes failures (Timeout, HTTP Error, Invalid JSON, Schema Violation, Incomplete Response, Nonsensical Output).

## 📋 Prerequisites

You need Python 3 installed along with a few dependencies:

```bash
pip install requests jsonschema
```

## ⚙️ Configuration

Open the script and edit the constants at the top to match your setup:

```python
# Add the specific model strings used by your local server
MODEL_NAMES = ["your-local-model-v1", "another-model-v2"]

# How many times to test each model
TEST_RUNS = 5

# Your local endpoint (default LM Studio example shown)
API_URL = "http://localhost:1234/v1/chat/completions"

# Time to wait for a complete response before marking as a Timeout failure
REQUEST_TIMEOUT = 30
```

### Advanced Configuration
You can modify the `PROMPT` and `SCHEMA` variables to test different scenarios.
*   **`SCHEMA`**: Defines the expected JSON structure.
*   **`PROMPT`**: The instructions given to the LLM.
*   *Note: The script dynamically counts expected items based on numbered lists in the prompt. If you change the prompt format, you may need to adjust how `EXPECTED_JOKES_COUNT` is calculated.*
