from collections.abc import Iterator
from src.classifier import classify_issue_mock
from src.models import RawIssue, RoutedIssue
from src.preprocess import preprocess_issue
from src.router import route_issue


def run_issue_triage(issue: RawIssue) -> Iterator[tuple[str, object]]:
    preprocessed = preprocess_issue(issue)
    yield "executor_completed: preprocess_issue", preprocessed

    classification = classify_issue_mock(preprocessed)
    yield "executor_completed: classify_issue_agent", classification

    routed = route_issue(classification)
    yield "executor_completed: route_issue", routed

    yield "output", routed
