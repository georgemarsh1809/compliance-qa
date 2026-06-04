import datetime
import json
from pathlib import Path

import httpx

URL = "http://localhost:8000/query"

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "dataset.json"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

RESULTS_DIR = BASE_DIR / "results" / f"results_{timestamp}.json"

REFUSAL_SIGNALS = [
    "I cannot answer",
    "I can't answer",
    "provided sources do not contain",
    "The sources provided do not contain information",
    "I cannot find information",
    "the provided sources do not",
    "not covered in the provided sources",
    "not included in the sources",
    "outside the scope",
    "not addressed in",
    "there is no information",
    "The sources do not contain information",
    "I cannot find",
]

results = []

with open(DATA_PATH) as f:
    data = json.load(f)

for question_object in data:
    payload = {"question": question_object["question"]}

    response = httpx.post(URL, json=payload, timeout=60.0)
    answer = response.json()

    result = {
        "id": question_object["id"],
        "category": question_object["category"],
        "question": question_object["question"],
        "answer": answer,
        "passed": any(sig.lower() in answer["answer"].lower() for sig in REFUSAL_SIGNALS)
        if question_object["category"] == "out_of_corpus"
        else None,
    }

    results.append(result)

passed_count = sum(1 for r in results if r["passed"] is True)

with open(RESULTS_DIR, "w") as f:
    json.dump(results, f, indent=2)

print(f"Out-of-corpus refusal check: {passed_count}/6 passed")
print("Happy path (manual review): 12 questions")
print("Oblique (manual review): 3 questions")
print(f"Results saved to: evals/results/results_{timestamp}.json.json")
