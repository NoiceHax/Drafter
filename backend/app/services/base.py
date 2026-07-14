"""Shared service helpers: context assembly and revision logging."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.enums import RevisionTarget
from app.models.models import ContentProject, Hook, Keyword, Revision
from app.prompts.common import context_block, tone_label


def selected_keywords(project: ContentProject) -> list[str]:
    return [k.text for k in project.keywords if k.selected]


def selected_angle(project: ContentProject):
    if project.selected_angle_id:
        for a in project.angles:
            if a.id == project.selected_angle_id:
                return a
    for a in project.angles:
        if a.selected:
            return a
    return None


def selected_hook(project: ContentProject) -> Hook | None:
    if project.selected_hook_id:
        for h in project.hooks:
            if h.id == project.selected_hook_id:
                return h
    for h in project.hooks:
        if h.selected:
            return h
    return None


def research_summary(project: ContentProject) -> str | None:
    # Only sources the creator kept selected feed the story/script context.
    sources = [s for s in project.research_sources if getattr(s, "selected", True)]
    if not sources:
        return None
    lines = []
    for src in sources:
        facts = "; ".join(src.key_facts or [])
        lines.append(f"  • [{src.title}]({src.url}): {src.summary} Facts: {facts}")
    return "\n".join(lines)


def build_context(
    project: ContentProject,
    *,
    include_angle: bool = True,
    include_hook: bool = True,
    include_research: bool = True,
) -> str:
    angle = selected_angle(project) if include_angle else None
    hook = selected_hook(project) if include_hook else None
    return context_block(
        idea=project.idea,
        platform=project.platform,
        tone_label=tone_label(project.tone, project.custom_tone),
        target_duration_seconds=project.target_duration_seconds,
        selected_keywords=selected_keywords(project),
        angle_title=angle.title if angle else None,
        angle_summary=angle.summary if angle else None,
        hook_text=hook.text if hook else None,
        research_summary=research_summary(project) if include_research else None,
    )


def log_revision(
    db: Session,
    *,
    project_id: uuid.UUID,
    target: RevisionTarget,
    entity_id: uuid.UUID | None = None,
    instruction: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
) -> None:
    db.add(
        Revision(
            project_id=project_id,
            target=target,
            entity_id=entity_id,
            instruction=instruction,
            before=before,
            after=after,
        )
    )
