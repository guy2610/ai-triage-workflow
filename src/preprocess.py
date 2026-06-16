from src.models import RawIssue, PreprocessedIssue


def preprocess_issue(issue: RawIssue) -> PreprocessedIssue:
    text = f"{issue.title}\n{issue.body}".strip()
    normalized = " ".join(text.lower().split())

    return PreprocessedIssue(
        title=issue.title.strip(),
        body=issue.body.strip(),
        normalized_text=normalized,
        has_reproduction_steps="steps to reproduce" in normalized or "repro" in normalized,
        has_expected_behavior="expected" in normalized,
        has_actual_behavior="actual" in normalized or "got" in normalized,
    )
