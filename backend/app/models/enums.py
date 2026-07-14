"""Enumerations used across models and schemas."""
from __future__ import annotations

import enum


class Platform(str, enum.Enum):
    instagram_reels = "instagram_reels"
    youtube_shorts = "youtube_shorts"
    tiktok = "tiktok"
    youtube_long = "youtube_long"
    generic = "generic"


class Tone(str, enum.Enum):
    educational = "educational"
    dramatic = "dramatic"
    conversational = "conversational"
    documentary = "documentary"
    humorous = "humorous"
    investigative = "investigative"
    custom = "custom"


class ProjectStage(str, enum.Enum):
    idea = "idea"
    keywords = "keywords"
    angles = "angles"
    hooks = "hooks"
    research = "research"
    outline = "outline"
    script = "script"
    visuals = "visuals"


class KeywordCategory(str, enum.Enum):
    semantic = "semantic"
    story = "story"
    discovery = "discovery"


class KeywordStatus(str, enum.Enum):
    """Lifecycle of a keyword within a project (drives future recommendation intelligence)."""

    original = "original"      # entered by the creator up front
    recommended = "recommended"  # suggested by the LLM, not yet acted on
    selected = "selected"      # creator kept it
    rejected = "rejected"      # creator removed a recommendation
    custom = "custom"          # creator added manually after recommendations


class HookArchetype(str, enum.Enum):
    mystery_curiosity = "mystery_curiosity"
    threat = "threat"
    cold_open = "cold_open"
    contrarian = "contrarian"
    problem = "problem"
    # Additional narrative opening strategies.
    statistic = "statistic"              # open on a striking, real number
    story_open = "story_open"            # drop into a specific in-media-res moment
    direct_question = "direct_question"  # pose a compelling question to the viewer
    comparison = "comparison"            # an unexpected juxtaposition of two things
    pattern_interrupt = "pattern_interrupt"  # a jarring, counterintuitive statement


class VisualType(str, enum.Enum):
    real_image = "real_image"
    historical_photo = "historical_photo"
    person = "person"
    event = "event"
    location = "location"
    product = "product"
    news_headline = "news_headline"
    map = "map"
    chart = "chart"
    screenshot = "screenshot"
    b_roll = "b_roll"
    generated_image = "generated_image"
    text_animation = "text_animation"


class VisualPriority(str, enum.Enum):
    high = "high"
    medium = "medium"
    low = "low"


class RevisionTarget(str, enum.Enum):
    idea = "idea"
    keyword_recommendations = "keyword_recommendations"
    angles = "angles"
    angle = "angle"
    hooks = "hooks"
    hook = "hook"
    research = "research"
    outline = "outline"
    script = "script"
    scene_narration = "scene_narration"
    scene_visual_direction = "scene_visual_direction"
    scene_visuals = "scene_visuals"
