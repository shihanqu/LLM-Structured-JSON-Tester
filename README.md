# LLM JSON Output & Logic Tester

A Python script designed to test and validate the ability of Large Language Models (LLMs) to generate structured JSON output that is not only syntactically correct but also logically complete and sensible.

This tool is ideal for developers who need reliable, predictable JSON from models for their applications. It is pre-configured to work with local LLM servers like [LM Studio](https://lmstudio.ai/), but can be easily adapted for any OpenAI-compatible API.

## Key Features

-   **✅ JSON Schema Validation**: Ensures the model's output strictly conforms to a predefined JSON schema.
-   **⏱️ Request Timeout**: Fails any model that takes too long to generate a response, preventing indefinite hangs.
-   **📦 Content Completeness Check**: Verifies that the model completed the entire task (e.g., processed all 10 items in a list, not just 2).
-   **🤔 Content Sanity-Check**: Includes a basic heuristic to detect and fail responses containing nonsensical or garbled text.
-   **🔄 Multi-Model Testing**: Easily configure and run tests against multiple models in a single execution.
-   **📊 Consolidated Final Summary**: At the end of the run, it provides a clean, comparative summary of each model's performance and a breakdown of its specific errors.

## How It Works

The script operates in a simple loop for each model you define:
1.  **Constructs a Payload**: It combines a user-defined `PROMPT` with a `SCHEMA` that describes the desired JSON structure.
2.  **Sends Request**: It sends the payload to a running LLM API endpoint.
3.  **Receives Response**: It captures the model's output.
4.  **Validates the Output**: The response is subjected to a series of checks:
    -   Was it received within the timeout?
    -   Is it valid JSON?
    -   Does it conform to the schema?
    -   Is the content complete?
    -   Does the content make sense?
5.  **Records Results**: It tracks the pass/fail counts and the specific reason for each failure.
6.  **Generates a Final Report**: After all tests are done, it prints a final summary for easy comparison.

---

## Getting Started

### Prerequisites

1.  **Python 3.7+** and `pip`.
2.  A running instance of an **OpenAI-compatible API server**. [LM Studio](https://lmstudio.ai/) is highly recommended for local testing.
    -   Download and install LM Studio.
    -   From the app's search tab, download the models you wish to test (e.g., `gpt-oss-20b`, `Qwen/qwen3-30b`).
    -   Navigate to the local server tab (looks like `<->`), select a model, and **start the server**.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Install the required Python packages:**
    A `requirements.txt` file is included for convenience.
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have a `requirements.txt`, create one with the contents: `requests` and `jsonschema`)*

### Configuration

Open the `test_llm_json.py` script and edit the configuration variables at the top:

```python
# ========================================
# CONFIGURE YOUR TEST HERE (EDIT THESE VALUES)
# ========================================
MODEL_NAMES = ["openai/gpt-oss-20b", "qwen/qwen3-30b-a3b-2507"]  # Add/remove models as needed
TEST_RUNS = 5  # Number of test runs per model
API_URL = "http://localhost:1234/v1/chat/completions"  # LM Studio endpoint
REQUEST_TIMEOUT = 30 # Seconds to wait for a response before failing
```

-   `MODEL_NAMES`: A list of model identifiers. **Important:** In LM Studio, the exact model identifier is shown at the top of the server console after you start it.
-   `TEST_RUNS`: The number of times to run the test for each model.
-   `API_URL`: The endpoint for your local server. The default is correct for LM Studio.
-   `REQUEST_TIMEOUT`: The maximum time (in seconds) to wait for a response.

---

## Running the Script

With your local server running and the configuration set, execute the script from your terminal:

```bash
python test_llm_json.py
```

## Understanding the Output

The script will first print the detailed output for each run, showing the model's raw JSON response and the test result (`✅ Success` or `❌ Failure Reason`).

After all models have been tested, it will display the final summary:

```
========================================
           FINAL TEST SUMMARY
========================================

Summary for openai/gpt-oss-20b: 0/5 passed (0.0%)
  3 Incomplete Response Errors
  2 Nonsensical Explanation Errors

Summary for qwen/qwen3-30b-a3b-2507: 5/5 passed (100.0%)
```

This summary provides a clear, at-a-glance view of which models are most reliable for your specific task.

## Customizing Your Own Tests

This script is a framework. You can easily adapt it for your own use cases by modifying two key components:

1.  **`PROMPT`**: Change the prompt to reflect the task you want the LLM to perform.
2.  **`SCHEMA`**: Modify the JSON schema to define the exact output structure you need for your application. You can use an online tool like [jsonschema.net](https://www.jsonschema.net/) to help build your own schemas.

By customizing the prompt and schema, you can test a model's ability to generate anything from tool-use instructions to structured data extraction from text.

## Contributing

Contributions are welcome! If you have ideas for new features or improvements, feel free to open an issue or submit a pull request.
