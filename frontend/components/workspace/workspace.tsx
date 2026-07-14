"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { StageProgress } from "./stage-progress";
import { PlatformBadge } from "@/components/platform-badge";
import { Badge } from "@/components/ui/badge";
import { IdeaPanel } from "./panels/idea-panel";
import { KeywordsPanel } from "./panels/keywords-panel";
import { AnglesPanel } from "./panels/angles-panel";
import { HooksPanel } from "./panels/hooks-panel";
import { ResearchPanel } from "./panels/research-panel";
import { OutlinePanel } from "./panels/outline-panel";
import { ScriptPanel } from "./panels/script-panel";
import { VisualsPanel } from "./panels/visuals-panel";
import { humanDuration } from "@/lib/utils";
import { stageIndex } from "@/lib/constants";
import type { ProjectDetail, ProjectStage } from "@/types";

/** Derive which stages have real completed data (drives the checkmarks). */
function deriveCompleted(p: ProjectDetail): Record<ProjectStage, boolean> {
  const idx = stageIndex(p.current_stage);
  return {
    idea: !!p.idea,
    keywords:
      (p.keywords || []).some((k) => k.selected) || idx > 1,
    angles: !!p.selected_angle_id || (p.angles || []).some((a) => a.selected),
    hooks: !!p.selected_hook_id || (p.hooks || []).some((h) => h.selected),
    research: p.research_enabled !== undefined || (p.research_sources || []).length > 0,
    outline: !!p.outline && (p.outline.sections?.length ?? 0) > 0,
    script: !!p.script && (p.script.scenes?.length ?? 0) > 0,
    visuals: !!p.script?.scenes?.some(
      (s) =>
        (s.visual_recommendations?.length ?? 0) > 0 ||
        (s.visual_assets?.length ?? 0) > 0
    ),
  };
}

export function Workspace({ project }: { project: ProjectDetail }) {
  const [active, setActive] = React.useState<ProjectStage>(
    project.current_stage || "idea"
  );

  // When the server advances the stage, follow it (only forward).
  const lastStage = React.useRef(project.current_stage);
  React.useEffect(() => {
    if (project.current_stage !== lastStage.current) {
      lastStage.current = project.current_stage;
    }
  }, [project.current_stage]);

  const completed = deriveCompleted(project);

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-b border-border bg-panel/80 px-4 pt-4 backdrop-blur sm:px-8">
        <Link
          href="/projects"
          className="label mb-2 inline-flex items-center gap-1.5 text-[10px] text-muted hover:text-text"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          All projects
        </Link>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h1 className="serif text-xl font-semibold text-text">
            {project.title || project.idea.slice(0, 70) || "Untitled project"}
          </h1>
          <PlatformBadge platform={project.platform} />
          <Badge tone="muted">
            {humanDuration(project.target_duration_seconds)}
          </Badge>
        </div>
        <div className="pb-3">
          <StageProgress
            currentStage={project.current_stage}
            activeStage={active}
            completed={completed}
            onSelect={setActive}
          />
        </div>
      </div>

      {/* Active panel */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-8">
        <div className="mx-auto max-w-4xl">
          <StagePanel stage={active} project={project} />
        </div>
      </div>
    </div>
  );
}

function StagePanel({
  stage,
  project,
}: {
  stage: ProjectStage;
  project: ProjectDetail;
}) {
  switch (stage) {
    case "idea":
      return <IdeaPanel project={project} />;
    case "keywords":
      return <KeywordsPanel project={project} />;
    case "angles":
      return <AnglesPanel project={project} />;
    case "hooks":
      return <HooksPanel project={project} />;
    case "research":
      return <ResearchPanel project={project} />;
    case "outline":
      return <OutlinePanel project={project} />;
    case "script":
      return <ScriptPanel project={project} />;
    case "visuals":
      return <VisualsPanel project={project} />;
    default:
      return <IdeaPanel project={project} />;
  }
}
