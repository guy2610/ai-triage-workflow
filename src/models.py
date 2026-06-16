from enum import Enum
from pydantic import BaseModel, Field


class Category(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    SECURITY = "security"
    UNCLEAR = "unclear"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Sentiment(str, Enum):
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class Route(str, Enum):
    SECURITY_REVIEW = "security_review"
    HUMAN_REVIEW = "human_review"
    ASK_MORE_INFO = "ask_more_info"
    BACKLOG = "backlog"


class RawIssue(BaseModel):
    title: str
    body: str


class PreprocessedIssue(BaseModel):
    title: str
    body: str
    normalized_text: str
    has_reproduction_steps: bool
    has_expected_behavior: bool
    has_actual_behavior: bool


class IssueClassification(BaseModel):
    category: Category
    urgency: Urgency
    sentiment: Sentiment
    missing_info: list[str] = Field(default_factory=list)
    needs_human: bool
    recommended_route: Route


class RoutedIssue(BaseModel):
    route: Route
    reason: str
    classification: IssueClassification
