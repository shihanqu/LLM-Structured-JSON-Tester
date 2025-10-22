import requests
import json
from jsonschema import validate, ValidationError
import re
from collections import defaultdict

# ========================================
# CONFIGURE YOUR TEST HERE (EDIT THESE VALUES)
# ========================================
MODEL_NAMES = ["openai/gpt-oss-20b", "openai/gpt-oss-120b","qwen/qwen3-next-80b","qwen/qwen3-vl-30b","qwen/qwen3-30b-a3b-2507","qwen/qwen3-4b-thinking-2507","mistralai/magistral-small-2509","mlx-community/apriel-1.5-15b-thinker","kimi-vl-a3b-thinking@8bit"]  # Add/remove models as needed
TEST_RUNS = 10  # Number of test runs per model
API_URL = "http://localhost:1234/v1/chat/completions"  # LM Studio endpoint
REQUEST_TIMEOUT = 40  # Seconds to wait for a response before failing

# ========================================
# TEST SPECIFICATIONS (DON'T EDIT UNLESS KNOWING SCHEMA)
# ========================================
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Joke Rating Schema",
    "type": "object",
    "properties": {
        "jokes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "Joke ID (1, 2 or 3)"},
                    "rating": {"type": "number", "minimum": 1, "maximum": 10},
                    "explanation": {"type": "string", "minLength": 10}
                },
                "required": ["id", "rating", "explanation"],
                "additionalProperties": False  # Prevent extra fields
            }
        }
    },
    "required": ["jokes"],
    "additionalProperties": False
}

PROMPT = """
Judge and rate every one of these jokes on a scale of 1-10, and provide a short explanation:

1. I’m reading a book on anti‑gravity—it’s impossible to put it down!  
2. Why did the scarecrow win an award? Because he was outstanding in his field!  
3. Parallel lines have so much in common… It’s a shame they’ll never meet.  
4. Why don’t skeletons fight each other? They just don’t have the guts.  
5. The roundest knight at King Arthur’s table is Sir Cumference.  
6. Did you hear about the claustrophobic astronaut? He needed a little space.  
7. I’d tell you a chemistry joke, but I wouldn’t get a reaction.  
8. I used to play piano by ear, but now I just use my hands.  
9. I tried to catch some fog yesterday… I mist.  
10. I told my wife she was drawing her eyebrows too high—she looked surprised! 
"""
# Dynamically count the number of jokes in the prompt
EXPECTED_JOKES_COUNT = len([line for line in PROMPT.strip().split('\n') if line.strip() and line.strip()[0].isdigit()])


# ========================================
# CORE TEST LOGIC
# ========================================
def test_model(model_name, runs, results):
    """Runs tests for a single model and stores results in the provided dictionary."""

    # Initialize results structure for the current model
    if model_name not in results:
        results[model_name] = {
            'pass_count': 0,
            'fail_count': 0,
            'errors': defaultdict(int)
        }

    print(f"\nTesting model: {model_name} (x{runs} runs)")

    for run in range(1, runs + 1):
        print(f"\nRun {run}/{runs}:", end=" ")
        run_failed = False
        error_type = "Unexpected Error"  # Default error type

        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": PROMPT}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "joke_rating_output",
                    "schema": SCHEMA
                }
            }
        }

        try:
            response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(payload),
                                     timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(f"❌ HTTP Error {response.status_code}: {response.text[:100]}...")
                error_type = "HTTP Error"
                raise ConnectionError("HTTP status was not 200")  # Treat as a failure and skip to except block

            json_response = response.json()
            content = json_response["choices"][0]["message"]["content"]

            print("\n--- Model Output ---")
            try:
                parsed_content = json.loads(content)
                print(json.dumps(parsed_content, indent=2))
            except json.JSONDecodeError:
                print(f"(Invalid JSON)\n{content}")
            print("--------------------")

            # 1. Parse JSON
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Test Result: ❌ Invalid JSON: {str(e)}")
                error_type = "Invalid JSON"
                raise  # Re-raise to be caught by the main exception handler

            # 2. Validate Schema
            try:
                validate(instance=json_data, schema=SCHEMA)
            except ValidationError as e:
                print(f"Test Result: ❌ Schema Violation: {e.message}")
                error_type = "Schema Violation"
                raise

            # 3. Validate Completeness
            jokes_array = json_data.get("jokes", [])
            if len(jokes_array) != EXPECTED_JOKES_COUNT:
                print(
                    f"Test Result: ❌ Incomplete Response: Expected {EXPECTED_JOKES_COUNT} jokes, but received {len(jokes_array)}.")
                error_type = "Incomplete Response"
                raise ValueError("Incorrect number of jokes")

            # 4. Sanity-check Explanations
            for joke in jokes_array:
                explanation = joke.get("explanation", "")
                if not re.search(r'[a-zA-Z]{2}', explanation):
                    print(f"Test Result: ❌ Nonsensical Explanation for joke ID {joke.get('id', 'N/A')}.")
                    error_type = "Nonsensical Explanation"
                    raise ValueError("Explanation seems nonsensical")

            # If all checks pass
            print("Test Result: ✅ Success")
            results[model_name]['pass_count'] += 1

        except Exception as e:
            # Determine error type if not already set
            if isinstance(e, requests.exceptions.Timeout):
                print(f"❌ Timeout Error: Model took longer than {REQUEST_TIMEOUT} seconds to respond.")
                error_type = "Timeout Error"
            elif isinstance(e, requests.exceptions.RequestException):
                print(f"❌ Connection Error: {str(e)}")
                error_type = "Connection Error"

            # Record the failure
            results[model_name]['fail_count'] += 1
            results[model_name]['errors'][error_type] += 1


def print_final_summary(results):
    """Prints a consolidated summary of all test runs."""
    print("\n========================================")
    print("           FINAL TEST SUMMARY")
    print("========================================")

    if not results:
        print("No tests were run.")
        return

    for model_name, data in results.items():
        total = data['pass_count'] + data['fail_count']
        if total > 0:
            pass_rate = (data['pass_count'] / total) * 100
            print(f"\nSummary for {model_name}: {data['pass_count']}/{total} passed ({pass_rate:.1f}%)")

            # Print error details if there were any failures
            if data['fail_count'] > 0:
                for error_type, count in sorted(data['errors'].items()):
                    if count > 0:
                        error_str = "Error" if count == 1 else "Errors"
                        print(f"  {count} {error_type} {error_str}")
        else:
            print(f"\nSummary for {model_name}: No tests were completed.")


# ========================================
# EXECUTION
# ========================================
if __name__ == "__main__":
    all_results = {}
    for model in MODEL_NAMES:
        test_model(model, TEST_RUNS, all_results)

    print_final_summary(all_results)
