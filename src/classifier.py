import os

from dotenv import load_dotenv
from google import genai
from pydantic import ValidationError

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


def build_classifier_prompt(issue: PreprocessedIssue) -> str:
    return f"""
You are an issue triage agent inside a deterministic workflow.

Classify the following GitHub issue.

Allowed category values:
- bug
- feature
- question
- security
- unclear

Allowed urgency values:
- low
- medium
- high

Allowed sentiment values:
- neutral
- frustrated
- angry

Allowed recommended_route values:
- security_review
- human_review
- ask_more_info
- backlog

Routing guidance:
- Security issues must go to security_review.
- Angry or risky issues should go to human_review.
- Bugs missing reproduction steps, expected behavior, or actual behavior should go to ask_more_info.
- Clear non-urgent issues should go to backlog.

Issue title:
{issue.title}

Issue body:
{issue.body}

Preprocessing facts:
- has_reproduction_steps: {issue.has_reproduction_steps}
- has_expected_behavior: {issue.has_expected_behavior}
- has_actual_behavior: {issue.has_actual_behavior}
""".strip()


def classify_issue_with_gemini(issue: PreprocessedIssue) -> IssueClassification:
    load_dotenv()

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    client = genai.Client()

    response = client.models.generate_content(
        model=model,
        contents=build_classifier_prompt(issue),
        config={
            "response_format": {
                "text": {
                    "mime_type": "application/json",
                    "schema": IssueClassification.model_json_schema(),
                }
            }
        },
    )

    return IssueClassification.model_validate_json(response.text)


def classify_issue(issue: PreprocessedIssue) -> IssueClassification:
    load_dotenv()

    if not os.getenv("GEMINI_API_KEY"):
        return classify_issue_mock(issue)

    try:
        return classify_issue_with_gemini(issue)
    except (ValidationError, ValueError, RuntimeError) as exc:
        print(f"agent_classifier_failed: {exc}")
        print("falling_back_to_mock_classifier")
        return classify_issue_mock(issue)
