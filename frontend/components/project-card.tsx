"use client";

import Link from "next/link";
import { Clock, MoreHorizontal, Trash2 } from "lucide-react";
import * as React from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { PlatformBadge } from "@/components/platform-badge";
import { Button } from "@/components/ui/button";
import { humanDuration, relativeTime } from "@/lib/utils";
import { STAGE_LABELS, stageIndex, STAGE_ORDER } from "@/lib/constants";
import { useDeleteProject } from "@/hooks/useProjects";
import type { Project } from "@/types";

export function ProjectCard({ project }: { project: Project }) {
  const del = useDeleteProject();
  const [menuOpen, setMenuOpen] = React.useState(false);
  const idx = stageIndex(project.current_stage);
  const progress = Math.round(((idx + 1) / STAGE_ORDER.length) * 100);

  return (
    <Card interactive className="group relative flex flex-col p-4">
      <Link href={`/projects/${project.id}`} className="flex flex-1 flex-col">
        <div className="mb-2 flex items-start justify-between gap-2">
          <h3 className="serif line-clamp-1 pr-6 text-[15px] font-semibold text-text">
            {project.title || project.idea.slice(0, 60) || "Untitled project"}
          </h3>
        </div>
        <p className="mb-3 line-clamp-2 flex-1 text-xs leading-relaxed text-muted">
          {project.idea}
        </p>

        <div className="mb-3 flex flex-wrap items-center gap-1.5">
          <PlatformBadge platform={project.platform} />
          <Badge tone="muted">
            {humanDuration(project.target_duration_seconds)}
          </Badge>
          <Badge tone="accent">{STAGE_LABELS[project.current_stage]}</Badge>
        </div>

        <div className="mb-2 flex items-center gap-2">
          <div className="h-1 flex-1 overflow-hidden rounded-sm bg-elevated">
            <div
              className="h-full rounded-sm bg-success"
              style={{ width: `${progress}%` }}
            />
          </div>
          <span className="font-mono text-[10px] tabular-nums text-muted">
            {idx + 1}/{STAGE_ORDER.length}
          </span>
        </div>

        <div className="flex items-center gap-1 text-[11px] text-muted">
          <Clock className="h-3 w-3" />
          {relativeTime(project.updated_at)}
        </div>
      </Link>

      <div className="absolute right-2 top-2">
        <button
          className="flex h-6 w-6 items-center justify-center rounded text-muted opacity-0 transition-opacity hover:bg-elevated hover:text-text group-hover:opacity-100"
          onClick={(e) => {
            e.preventDefault();
            setMenuOpen((v) => !v);
          }}
          aria-label="Project actions"
        >
          <MoreHorizontal className="h-4 w-4" />
        </button>
        {menuOpen && (
          <div
            className="absolute right-0 top-7 z-10 w-36 rounded border border-border bg-elevated p-1 shadow-xl"
            onMouseLeave={() => setMenuOpen(false)}
          >
            <button
              className="flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-xs text-danger hover:bg-danger/10"
              onClick={(e) => {
                e.preventDefault();
                if (confirm("Delete this project? This cannot be undone.")) {
                  del.mutate(project.id);
                }
                setMenuOpen(false);
              }}
            >
              <Trash2 className="h-3.5 w-3.5" />
              Delete
            </button>
          </div>
        )}
      </div>
    </Card>
  );
}
