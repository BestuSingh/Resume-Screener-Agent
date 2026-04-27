import argparse
import json
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test the Resume Screener API.")
    parser.add_argument("--url", default="http://127.0.0.1:8000/screen")
    args = parser.parse_args()

    payload = {
        "job_description": (PROJECT_ROOT / "samples" / "job_description.txt").read_text(encoding="utf-8"),
        "resumes": [
            str(PROJECT_ROOT / "samples" / "resume_alex_morgan.txt"),
            str(PROJECT_ROOT / "samples" / "resume_jamie_lee.txt"),
        ],
        "top_k": 4,
    }
    response = requests.post(args.url, json=payload, timeout=180)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()

