import json
import csv
import time
import datetime
import os
import sys

# Try to import psutil for memory tracking
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Memory tracking disabled. Run: pip install psutil")

# --------------------------------------------------------------------------
# Inline prompt dataset (~100 prompts across 5 categories)
# --------------------------------------------------------------------------
PROMPTS = [
    # ── Simple Facts (20 prompts) ──────────────────────────────────────────
    {"id": 1,  "category": "simple_facts", "prompt": "What is the capital of France?"},
    {"id": 2,  "category": "simple_facts", "prompt": "What is 15 multiplied by 13?"},
    {"id": 3,  "category": "simple_facts", "prompt": "Name 3 planets in the solar system."},
    {"id": 4,  "category": "simple_facts", "prompt": "What is the chemical symbol for gold?"},
    {"id": 5,  "category": "simple_facts", "prompt": "How many continents are there on Earth?"},
    {"id": 6,  "category": "simple_facts", "prompt": "What is the speed of light in km/s?"},
    {"id": 7,  "category": "simple_facts", "prompt": "Who wrote Romeo and Juliet?"},
    {"id": 8,  "category": "simple_facts", "prompt": "What year did World War II end?"},
    {"id": 9,  "category": "simple_facts", "prompt": "What is the largest ocean on Earth?"},
    {"id": 10, "category": "simple_facts", "prompt": "How many sides does a hexagon have?"},
    {"id": 11, "category": "simple_facts", "prompt": "What is the boiling point of water in Celsius?"},
    {"id": 12, "category": "simple_facts", "prompt": "Who painted the Mona Lisa?"},
    {"id": 13, "category": "simple_facts", "prompt": "What is the square root of 144?"},
    {"id": 14, "category": "simple_facts", "prompt": "What is the capital of Japan?"},
    {"id": 15, "category": "simple_facts", "prompt": "How many bones are in the adult human body?"},
    {"id": 16, "category": "simple_facts", "prompt": "What gas do plants absorb during photosynthesis?"},
    {"id": 17, "category": "simple_facts", "prompt": "What is the currency of the United Kingdom?"},
    {"id": 18, "category": "simple_facts", "prompt": "Name the four blood types in the ABO system."},
    {"id": 19, "category": "simple_facts", "prompt": "What planet is known as the Red Planet?"},
    {"id": 20, "category": "simple_facts", "prompt": "How many zeros are in one million?"},

    # ── Reasoning (20 prompts) ─────────────────────────────────────────────
    {"id": 21, "category": "reasoning", "prompt": "If a train travels 60km/hr for 2.5 hours, how far does it travel? Show steps."},
    {"id": 22, "category": "reasoning", "prompt": "Why is the sky blue? Explain step by step."},
    {"id": 23, "category": "reasoning", "prompt": "A farmer has 17 sheep. All but 9 die. How many are left? Explain."},
    {"id": 24, "category": "reasoning", "prompt": "If you have a 3-litre jug and a 5-litre jug, how do you measure exactly 4 litres?"},
    {"id": 25, "category": "reasoning", "prompt": "What comes next in this sequence: 2, 4, 8, 16, ___? Why?"},
    {"id": 26, "category": "reasoning", "prompt": "A store sells apples for $0.50 each. You buy 7. How much change from $5?"},
    {"id": 27, "category": "reasoning", "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude all roses fade quickly? Explain."},
    {"id": 28, "category": "reasoning", "prompt": "A bat and ball cost $1.10 total. The bat costs $1 more than the ball. How much does the ball cost?"},
    {"id": 29, "category": "reasoning", "prompt": "Why do heavier objects and lighter objects fall at the same speed in a vacuum?"},
    {"id": 30, "category": "reasoning", "prompt": "If today is Wednesday and a meeting is in 10 days, what day is the meeting?"},
    {"id": 31, "category": "reasoning", "prompt": "You flip a fair coin 3 times and get heads each time. What is the probability of heads on the 4th flip? Why?"},
    {"id": 32, "category": "reasoning", "prompt": "A snail climbs 3 metres up a wall each day but slides back 2 metres each night. How many days to climb 10 metres?"},
    {"id": 33, "category": "reasoning", "prompt": "Explain why -1 × -1 = 1 using a real-world analogy."},
    {"id": 34, "category": "reasoning", "prompt": "If a pizza is cut into 8 slices and you eat 3, what percentage remains?"},
    {"id": 35, "category": "reasoning", "prompt": "Two trains 200km apart travel toward each other at 80km/h and 70km/h. When do they meet?"},
    {"id": 36, "category": "reasoning", "prompt": "Is it possible for a number to be both even and odd? Explain why or why not."},
    {"id": 37, "category": "reasoning", "prompt": "If you put $1000 in a bank at 5% annual interest, how much will you have after 2 years?"},
    {"id": 38, "category": "reasoning", "prompt": "Why does ice float on water? What would happen to aquatic life if it didn't?"},
    {"id": 39, "category": "reasoning", "prompt": "A room has 4 corners. In each corner sits a cat. Each cat sees 3 other cats. How many cats are there?"},
    {"id": 40, "category": "reasoning", "prompt": "Explain the trolley problem and what it reveals about moral reasoning."},

    # ── Summarization (20 prompts) ─────────────────────────────────────────
    {"id": 41, "category": "summarization", "prompt": "Summarize the concept of machine learning in 2 sentences."},
    {"id": 42, "category": "summarization", "prompt": "Explain cloud computing to a 10-year-old."},
    {"id": 43, "category": "summarization", "prompt": "Summarize the theory of evolution in 3 sentences."},
    {"id": 44, "category": "summarization", "prompt": "Explain what the internet is in simple terms."},
    {"id": 45, "category": "summarization", "prompt": "Summarize the main causes of World War I in 2 sentences."},
    {"id": 46, "category": "summarization", "prompt": "Explain blockchain technology to a non-technical person."},
    {"id": 47, "category": "summarization", "prompt": "Summarize what DNA is and why it matters in 2 sentences."},
    {"id": 48, "category": "summarization", "prompt": "Explain the water cycle to a child."},
    {"id": 49, "category": "summarization", "prompt": "Summarize the concept of supply and demand in economics."},
    {"id": 50, "category": "summarization", "prompt": "Explain what a black hole is in simple terms."},
    {"id": 51, "category": "summarization", "prompt": "Summarize the French Revolution in 3 sentences."},
    {"id": 52, "category": "summarization", "prompt": "Explain artificial intelligence to someone who has never heard of it."},
    {"id": 53, "category": "summarization", "prompt": "Summarize how vaccines work in 2 sentences."},
    {"id": 54, "category": "summarization", "prompt": "Explain what inflation is using a simple everyday example."},
    {"id": 55, "category": "summarization", "prompt": "Summarize the plot of Romeo and Juliet in 3 sentences."},
    {"id": 56, "category": "summarization", "prompt": "Explain what photosynthesis is to a 10-year-old."},
    {"id": 57, "category": "summarization", "prompt": "Summarize the key ideas of democracy in 2 sentences."},
    {"id": 58, "category": "summarization", "prompt": "Explain what a CPU does inside a computer in simple terms."},
    {"id": 59, "category": "summarization", "prompt": "Summarize the life cycle of a star in 3 sentences."},
    {"id": 60, "category": "summarization", "prompt": "Explain the concept of gravity to a child."},

    # ── Code Generation (20 prompts) ───────────────────────────────────────
    {"id": 61, "category": "code_generation", "prompt": "Write a Python function to reverse a string."},
    {"id": 62, "category": "code_generation", "prompt": "Write a Python function to check if a number is prime."},
    {"id": 63, "category": "code_generation", "prompt": "Write a Python function to calculate the factorial of a number."},
    {"id": 64, "category": "code_generation", "prompt": "Write a Python function to find the largest number in a list."},
    {"id": 65, "category": "code_generation", "prompt": "Write a Python function that returns the Fibonacci sequence up to n terms."},
    {"id": 66, "category": "code_generation", "prompt": "Write a Python function to count the vowels in a string."},
    {"id": 67, "category": "code_generation", "prompt": "Write a Python function to check if a string is a palindrome."},
    {"id": 68, "category": "code_generation", "prompt": "Write a Python function to flatten a nested list."},
    {"id": 69, "category": "code_generation", "prompt": "Write a Python function to remove duplicates from a list while preserving order."},
    {"id": 70, "category": "code_generation", "prompt": "Write a Python function to merge two sorted lists into one sorted list."},
    {"id": 71, "category": "code_generation", "prompt": "Write a Python class for a simple stack with push, pop, and peek methods."},
    {"id": 72, "category": "code_generation", "prompt": "Write a Python function to perform binary search on a sorted list."},
    {"id": 73, "category": "code_generation", "prompt": "Write a Python function to convert Celsius to Fahrenheit."},
    {"id": 74, "category": "code_generation", "prompt": "Write a Python decorator that measures the execution time of a function."},
    {"id": 75, "category": "code_generation", "prompt": "Write a Python function to count word frequency in a sentence."},
    {"id": 76, "category": "code_generation", "prompt": "Write a Python function that rotates a list by k positions."},
    {"id": 77, "category": "code_generation", "prompt": "Write a Python context manager that logs when a block of code starts and ends."},
    {"id": 78, "category": "code_generation", "prompt": "Write a Python generator that yields prime numbers indefinitely."},
    {"id": 79, "category": "code_generation", "prompt": "Write a Python function using recursion to solve the Tower of Hanoi problem."},
    {"id": 80, "category": "code_generation", "prompt": "Write a Python function to validate an email address using regex."},

    # ── Creative / Open-ended (20 prompts) ────────────────────────────────
    {"id": 81,  "category": "creative", "prompt": "Write a 3-sentence story about a robot learning to cook."},
    {"id": 82,  "category": "creative", "prompt": "List 5 creative uses for an empty cardboard box."},
    {"id": 83,  "category": "creative", "prompt": "Write a short poem about the ocean at night."},
    {"id": 84,  "category": "creative", "prompt": "Describe an alien civilisation that communicates through colour."},
    {"id": 85,  "category": "creative", "prompt": "Write a motivational speech for someone starting their first job."},
    {"id": 86,  "category": "creative", "prompt": "Invent a new sport that can be played indoors by two people. Describe the rules."},
    {"id": 87,  "category": "creative", "prompt": "Write a letter from the perspective of the last tree in a forest."},
    {"id": 88,  "category": "creative", "prompt": "Describe a city in the year 2200 in 4 sentences."},
    {"id": 89,  "category": "creative", "prompt": "Write a dialogue between the Sun and the Moon meeting for the first time."},
    {"id": 90,  "category": "creative", "prompt": "List 5 unusual but practical inventions the world needs."},
    {"id": 91,  "category": "creative", "prompt": "Write a short mystery story that ends with an unexpected twist in 5 sentences."},
    {"id": 92,  "category": "creative", "prompt": "Describe what music would look like if it were visible."},
    {"id": 93,  "category": "creative", "prompt": "Write a bedtime story for a child who is afraid of the dark."},
    {"id": 94,  "category": "creative", "prompt": "Invent a new holiday and describe how people would celebrate it."},
    {"id": 95,  "category": "creative", "prompt": "Write a product review for a time machine."},
    {"id": 96,  "category": "creative", "prompt": "Describe what it would feel like to live on Mars in 4 sentences."},
    {"id": 97,  "category": "creative", "prompt": "Write a conversation between a smartphone and a typewriter."},
    {"id": 98,  "category": "creative", "prompt": "List 5 things that would be different if humans had no sense of smell."},
    {"id": 99,  "category": "creative", "prompt": "Write a news headline from 100 years in the future."},
    {"id": 100, "category": "creative", "prompt": "Describe the most interesting job that doesn't exist yet."},
]


# --------------------------------------------------------------------------
# Ollama client (inline — no external src.ollama_client needed)
# --------------------------------------------------------------------------
def query_model(model: str, prompt: str, temperature: float = 0.0) -> dict:
    """
    Query a local Ollama model and return timing + text metrics.
    Returns a dict with keys: response_text, response_time_s,
    words_per_second, word_count, memory_mb, error
    """
    import urllib.request

    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }).encode()

    start_mem = _get_memory_mb()
    start_time = time.perf_counter()
    error = None
    response_text = ""

    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read().decode()
            data = json.loads(raw)
            response_text = data.get("response", "")
    except Exception as exc:
        error = str(exc)

    elapsed = time.perf_counter() - start_time
    end_mem = _get_memory_mb()

    word_count = len(response_text.split()) if response_text else 0
    wps = round(word_count / elapsed, 2) if elapsed > 0 else 0.0

    return {
        "response_text": response_text[:500],   # truncate for CSV readability
        "response_time_s": round(elapsed, 3),
        "words_per_second": wps,
        "word_count": word_count,
        "memory_mb": round(end_mem - start_mem, 2),
        "error": error or "",
    }


def _get_memory_mb() -> float:
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    return 0.0


# --------------------------------------------------------------------------
# Main benchmark runner
# --------------------------------------------------------------------------
def run_benchmark():
    models = ["llama3.2:3b", "phi3.5", "mistral"]

    os.makedirs("results", exist_ok=True)
    output_path = "results/benchmark_results.csv"

    fieldnames = [
        "model", "category", "prompt_id", "prompt",
        "response_time_s", "words_per_second", "word_count",
        "memory_mb", "error", "timestamp", "response_text",
    ]

    total = len(PROMPTS)
    all_results = []

    for model in models:
        print(f"\nBenchmarking {model}...")
        for i, prompt_data in enumerate(PROMPTS):
            print(f"  Prompt {i + 1}/{total}  [{prompt_data['category']}]", end="", flush=True)
            result = query_model(model, prompt_data["prompt"], temperature=0.0)

            row = {
                "model": model,
                "category": prompt_data["category"],
                "prompt_id": prompt_data["id"],
                "prompt": prompt_data["prompt"],
                "timestamp": datetime.datetime.now().isoformat(),
                **result,
            }
            all_results.append(row)

            status = "✓" if not result["error"] else f"✗ {result['error'][:40]}"
            print(f"  →  {result['response_time_s']}s  {result['words_per_second']} wps  {status}")

    # Save to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\nBenchmark complete! Results saved to {output_path}")
    print(f"Total rows: {len(all_results)}  ({len(models)} models × {total} prompts)")


if __name__ == "__main__":
    run_benchmark()