import json
import os
from pathlib import Path

from src.models import RawIssue
from src.workflow import run_issue_triage


def main() -> None:
    sample_path = Path("examples/sample_issues.json")
    issues = json.loads(sample_path.read_text())

    max_samples = int(os.getenv("MAX_SAMPLE_ISSUES", str(len(issues))))
    issues = issues[:max_samples]

    for index, item in enumerate(issues, start=1):
        print(f"\n=== Sample issue #{index}: {item['title']} ===")

        issue = RawIssue(**item)

        for event_type, data in run_issue_triage(issue):
            print(event_type)
            if event_type == "output":
                print(data.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
