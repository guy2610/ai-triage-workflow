from src.models import (
    Category,
    IssueClassification,
    PreprocessedIssue,
    Route,
    Sentiment,
    Urgency,
)


def classify_issue_mock(issue: PreprocessedIssue) -> IssueClassification:
    text = issue.normalized_text
    missing_info: list[str] = []

    if any(word in text for word in ["security", "vulnerability", "token", "password", "auth bypass", "injection"]):
        category = Category.SECURITY
        urgency = Urgency.HIGH
        sentiment = Sentiment.NEUTRAL
        route = Route.SECURITY_REVIEW
        needs_human = True
    elif any(word in text for word in ["crash", "broken", "error", "fails", "bug"]):
        category = Category.BUG
        urgency = Urgency.MEDIUM
        sentiment = Sentiment.FRUSTRATED if any(word in text for word in ["frustrated", "urgent", "blocked"]) else Sentiment.NEUTRAL
        route = Route.BACKLOG
        needs_human = False
    elif any(word in text for word in ["feature", "request", "support"]):
        category = Category.FEATURE
        urgency = Urgency.LOW
        sentiment = Sentiment.NEUTRAL
        route = Route.BACKLOG
        needs_human = False
    else:
        category = Category.UNCLEAR
        urgency = Urgency.LOW
        sentiment = Sentiment.NEUTRAL
        route = Route.ASK_MORE_INFO
        needs_human = False

    if category == Category.BUG:
        if not issue.has_reproduction_steps:
            missing_info.append("steps_to_reproduce")
        if not issue.has_expected_behavior:
            missing_info.append("expected_behavior")
        if not issue.has_actual_behavior:
            missing_info.append("actual_behavior")

    if missing_info:
        route = Route.ASK_MORE_INFO

    return IssueClassification(
        category=category,
        urgency=urgency,
        sentiment=sentiment,
        missing_info=missing_info,
        needs_human=needs_human,
        recommended_route=route,
    )
