import json
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = WORKSPACE_ROOT / "resume_screener"
sys.path.insert(0, str(WORKSPACE_ROOT))

from resume_screener.app.agent import ResumeScreenerAgent  # noqa: E402


def main() -> None:
    jd = (PROJECT_ROOT / "samples" / "job_description.txt").read_text(encoding="utf-8")
    resumes = [
        str(PROJECT_ROOT / "samples" / "resume_alex_morgan.txt"),
        str(PROJECT_ROOT / "samples" / "resume_jamie_lee.txt"),
    ]

    agent = ResumeScreenerAgent()
    response = agent.run(job_description=jd, resume_inputs=resumes, top_k=4)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()

