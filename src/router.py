from src.models import IssueClassification, Route, RoutedIssue


def route_issue(classification: IssueClassification) -> RoutedIssue:
    if classification.category == "security":
        return RoutedIssue(
            route=Route.SECURITY_REVIEW,
            reason="Security-related issues require manual security review.",
            classification=classification,
        )

    if classification.needs_human or classification.sentiment == "angry":
        return RoutedIssue(
            route=Route.HUMAN_REVIEW,
            reason="The issue requires human review due to risk or user sentiment.",
            classification=classification,
        )

    if classification.missing_info:
        return RoutedIssue(
            route=Route.ASK_MORE_INFO,
            reason="The issue is missing required information before triage can continue.",
            classification=classification,
        )

    return RoutedIssue(
        route=Route.BACKLOG,
        reason="The issue is clear enough and can be added to the normal backlog.",
        classification=classification,
    )
