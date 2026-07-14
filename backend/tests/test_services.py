"""Service-layer tests against a rolled-back database transaction."""
from __future__ import annotations

import pytest

from app.models.enums import HookArchetype, ProjectStage
from app.schemas.api import ProjectCreate
from app.services.angle_service import AngleService
from app.services.hook_service import HookService
from app.services.idea_service import IdeaService
from app.services.keyword_service import KeywordService
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService
from app.services.story_service import StoryService
from tests.conftest import FakeLLM


@pytest.fixture
def project(db, user):
    return ProjectService(db, user).create(
        ProjectCreate(
            idea="NVIDIA and the US-China AI chip conflict",
            initial_keywords=["NVIDIA", "China"],
            platform="instagram_reels",
            target_duration_seconds=60,
            tone="investigative",
        )
    )


def _reload(db, project_id, user):
    return ProjectService(db, user).get(project_id, detail=True)


def test_idea_refine_returns_direction_without_mutating_idea(db, project):
    llm = FakeLLM({
        "IdeaRefinementOut": {
            "refined_idea": "A 60-second look at how export bans reshaped the AI chip market.",
            "interpretation": "You want a conflict-driven explainer on chip geopolitics.",
            "directions": [
                {"title": "The Chip Gap", "idea": "Show how bans accelerate China's own chips."},
                {"title": "Money Talks", "idea": "Break down the financial fallout for NVIDIA."},
            ],
            "clarifying_questions": ["Who is the audience?", "What timeframe?"],
        }
    })
    original = project.idea
    out = IdeaService(db, llm).refine(project, rough_idea="nvidia china chips ban")
    assert out.refined_idea.startswith("A 60-second")
    assert len(out.directions) == 2
    assert len(out.clarifying_questions) == 2
    # Refinement must NOT overwrite the project's idea; the creator confirms first.
    assert project.idea == original


def test_keyword_recommend_persists_and_advances_stage(db, project):
    llm = FakeLLM({
        "KeywordRecListOut": {"recommendations": [
            {"keyword": "AI chip war", "category": "story", "reason": "conflict", "relevance_score": 0.94},
            {"keyword": "Jensen Huang", "category": "semantic", "reason": "person", "relevance_score": 0.8},
        ]}
    })
    recs = KeywordService(db, llm).recommend(project)
    assert {r.keyword for r in recs} == {"AI chip war", "Jensen Huang"}
    # persisted scores are within [0,1].
    assert all(0.0 <= r.relevance_score <= 1.0 for r in recs)
    assert project.current_stage == ProjectStage.keywords


def test_keyword_selection_records_interaction(db, project):
    ks = KeywordService(db, FakeLLM())
    kw = ks.set_selection(project, keyword="AI chip war", category=None, selected=True)
    assert kw.selected is True
    kw2 = ks.set_selection(project, keyword="AI chip war", category=None, selected=False)
    assert kw2.selected is False  # same row toggled


def test_angle_generate_and_select(db, project):
    llm = FakeLLM({
        "AngleListOut": {"angles": [
            {"title": "T1", "summary": "s", "style": "investigative", "why_it_works": "w", "estimated_audience_interest": 0.9},
            {"title": "T2", "summary": "s", "style": "mystery", "why_it_works": "w", "estimated_audience_interest": 0.8},
        ]}
    })
    svc = AngleService(db, llm)
    angles = svc.generate(project)
    assert len(angles) == 2
    chosen = svc.select(project, angles[0].id)
    assert chosen.selected is True
    assert project.selected_angle_id == angles[0].id
    assert project.current_stage == ProjectStage.hooks


def test_hook_generation_stores_analysis_and_recommendation(db, project):
    llm = FakeLLM({
        "HookGenerationOut": {
            "analysis": [
                {"archetype": "mystery_curiosity", "suitability_score": 0.9, "reason": "r"},
                {"archetype": "problem", "suitability_score": 0.1, "reason": "r"},
            ],
            "hooks": [
                {"text": "Hook A", "archetype": "mystery_curiosity", "suitability_score": 0.9,
                 "estimated_duration_seconds": 6, "unanswered_question": "q", "story_payoff": "p", "reason": "r"},
            ],
            "recommended_index": 0,
        }
    })
    analysis, hooks, rec_id = HookService(db, llm).generate(project)
    assert len(analysis) == 2
    assert len(hooks) == 1
    assert rec_id == hooks[0].id
    assert hooks[0].analysis is not None  # snapshot stored


def test_hook_regenerate_preserves_archetype(db, project):
    gen_llm = FakeLLM({
        "HookGenerationOut": {
            "analysis": [{"archetype": "threat", "suitability_score": 0.8, "reason": "r"}],
            "hooks": [{"text": "Original", "archetype": "threat", "suitability_score": 0.8,
                       "estimated_duration_seconds": 5}],
            "recommended_index": 0,
        }
    })
    _, hooks, _ = HookService(db, gen_llm).generate(project)
    hook_id = hooks[0].id

    regen_llm = FakeLLM({
        "HookOut": {"text": "Refined", "archetype": "threat", "suitability_score": 0.85,
                    "estimated_duration_seconds": 5}
    })
    project = _reload(db, project.id, project.user)
    refined = HookService(db, regen_llm).regenerate(project, hook_id, instruction="shorter")
    assert refined.text == "Refined"
    assert refined.archetype == HookArchetype.threat


def _seed_outline(db, project):
    llm = FakeLLM({
        "OutlineOut": {"narrative_structure": "conflict-reveal", "estimated_duration_seconds": 60,
                       "sections": [{"type": "hook", "purpose": "p", "summary": "s", "estimated_duration_seconds": 5}]}
    })
    return StoryService(db, llm).generate_outline(project)


def test_script_generation_materializes_scenes_and_estimates(db, project):
    _seed_outline(db, project)
    project = _reload(db, project.id, project.user)
    llm = FakeLLM({
        "ScriptOut": {
            "title": "The Chip War", "estimated_duration_seconds": 58,
            "hook": {"text": "Hook line here.", "duration_seconds": 5},
            "scenes": [
                {"scene_number": 1, "start_time": 0, "end_time": 30, "section_type": "hook",
                 "narration": "First scene narration.", "on_screen_text": "x", "visual_direction": "v"},
                {"scene_number": 2, "start_time": 30, "end_time": 55, "section_type": "reveal",
                 "narration": "Second scene narration.", "on_screen_text": None, "visual_direction": "v"},
            ],
            "cta": {"text": "Follow for more.", "duration_seconds": 4},
        }
    })
    script = ScriptService(db, llm).generate(project)
    assert script.title == "The Chip War"
    assert len(script.scenes) == 2
    # Timeline end (55) + cta (4) dominates the short narration estimate.
    assert script.estimated_duration_seconds >= 55
    assert project.current_stage == ProjectStage.script


def test_scene_regeneration_only_changes_target_field(db, project):
    _seed_outline(db, project)
    project = _reload(db, project.id, project.user)
    gen_llm = FakeLLM({
        "ScriptOut": {
            "title": "T", "estimated_duration_seconds": 30,
            "hook": {"text": "H", "duration_seconds": 5},
            "scenes": [{"scene_number": 1, "start_time": 0, "end_time": 25, "section_type": "hook",
                        "narration": "Original narration.", "on_screen_text": "OST", "visual_direction": "Original visual."}],
            "cta": {"text": "C", "duration_seconds": 3},
        }
    })
    script = ScriptService(db, gen_llm).generate(project)
    scene = script.scenes[0]

    regen_llm = FakeLLM({
        "SceneOut": {"scene_number": 1, "start_time": 0, "end_time": 25, "section_type": "hook",
                     "narration": "NEW narration.", "on_screen_text": "IGNORED", "visual_direction": "IGNORED visual."}
    })
    project = _reload(db, project.id, project.user)
    updated = ScriptService(db, regen_llm).regenerate_scene(scene, project, field="narration")
    assert updated.narration == "NEW narration."
    # visual_direction untouched when field == "narration"
    assert updated.visual_direction == "Original visual."
