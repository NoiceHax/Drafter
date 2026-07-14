"""ResearchService → LLMProvider + SearchProvider.

If no search provider is configured, the project continues in a clearly-marked
non-researched mode (no fabricated sources are ever created).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enums import ProjectStage, RevisionTarget
from app.models.models import ContentProject, ResearchSource
from app.prompts import research_synthesis
from app.providers.llm import ChatMessage, LLMProvider
from app.providers.search import SearchProvider
from app.schemas.llm import ResearchOut
from app.services.base import build_context, log_revision, selected_angle, selected_keywords


class ResearchService:
    def __init__(self, db: Session, llm: LLMProvider, search: SearchProvider | None):
        self.db = db
        self.llm = llm
        self.search = search

    @property
    def enabled(self) -> bool:
        return self.search is not None

    def set_selected(self, project: ContentProject, source_id, selected: bool):
        from app.core.errors import NotFoundError

        src = next((s for s in project.research_sources if s.id == source_id), None)
        if src is None:
            raise NotFoundError("Research source not found.")
        src.selected = selected
        self.db.commit()
        self.db.refresh(src)
        return src

    def run(
        self, project: ContentProject, *, instruction: str | None = None
    ) -> tuple[bool, list[ResearchSource], str | None]:
        # Advance stage regardless; research is optional.
        if project.current_stage in (ProjectStage.hooks, ProjectStage.research):
            project.current_stage = ProjectStage.research

        if not self.enabled:
            self.db.commit()
            return (
                False,
                list(project.research_sources),
                "No search provider configured. Continuing in non-researched mode; "
                "the script will be generated without external sources.",
            )

        queries = self._build_queries(project)
        raw_results = []
        seen_urls: set[str] = set()
        for q in queries:
            for r in self.search.search(q, max_results=5):
                if r.url and r.url not in seen_urls:
                    seen_urls.add(r.url)
                    raw_results.append(r)

        if not raw_results:
            self.db.commit()
            return (True, list(project.research_sources), "No relevant sources found.")

        raw_block = "\n\n".join(
            f"URL: {r.url}\nTitle: {r.title}\nPublisher: {r.publisher or ''}\n"
            f"Date: {r.published_at or ''}\nContent: {(r.content or r.snippet)[:1500]}"
            for r in raw_results
        )
        prompt = research_synthesis.build(
            context=build_context(project, include_hook=False),
            raw_results=raw_block,
        )

        valid_urls = {r.url for r in raw_results}
        message: str | None = None

        # Try LLM synthesis. If it fails, fall back to the raw (already-paid-for)
        # search results rather than returning an error and wasting the search
        # credits. We never fabricate; the fallback uses only real Tavily data.
        try:
            synthesized = self.llm.generate_structured(
                [ChatMessage(role="user", content=prompt)], ResearchOut
            )
            synth_sources = [
                {
                    "title": s.title,
                    "url": s.url,
                    "publisher": s.publisher,
                    "published_at": s.published_at,
                    "summary": s.summary,
                    "key_facts": s.key_facts,
                }
                for s in synthesized.sources
                if s.url in valid_urls  # only URLs actually retrieved
            ]
        except Exception:
            synth_sources = [
                {
                    "title": r.title,
                    "url": r.url,
                    "publisher": r.publisher,
                    "published_at": r.published_at,
                    "summary": (r.snippet or r.content or "")[:600],
                    "key_facts": None,
                }
                for r in raw_results
            ]
            message = (
                "Sources were retrieved but AI synthesis was unavailable, so raw "
                "search results are shown. You can retry synthesis anytime."
            )

        # Replace prior sources on re-run.
        for s in list(project.research_sources):
            self.db.delete(s)
        self.db.flush()

        created: list[ResearchSource] = []
        for src in synth_sources:
            row = ResearchSource(
                project_id=project.id,
                title=src["title"],
                url=src["url"],
                publisher=src["publisher"],
                published_at=src["published_at"],
                summary=src["summary"] or "",
                key_facts=src["key_facts"],
            )
            self.db.add(row)
            created.append(row)

        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.research,
            instruction=instruction,
            after={"count": len(created), "synthesized": message is None},
        )
        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return (True, created, message)

    def _build_queries(self, project: ContentProject) -> list[str]:
        angle = selected_angle(project)
        keywords = selected_keywords(project)
        queries: list[str] = []
        if project.idea:
            queries.append(project.idea)
        if angle:
            queries.append(angle.title)
        if keywords:
            queries.append(" ".join(keywords[:4]))
        return queries[:3] or ["general background"]
