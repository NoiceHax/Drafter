"use client";

import { Sparkles, ListTree, Clock } from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { humanDuration } from "@/lib/utils";
import { useGenerateOutline } from "@/hooks/useWorkspace";
import type { ProjectDetail } from "@/types";

export function OutlinePanel({ project }: { project: ProjectDetail }) {
  const generate = useGenerateOutline(project.id);
  const outline = project.outline;
  const hasOutline = !!outline && outline.sections?.length > 0;

  return (
    <Panel
      step="06"
      eyebrow="Build the spine"
      title="Story Outline"
      description="The narrative structure: the beat-by-beat skeleton before the full draft."
      guideKey="outline"
      guide={[
        "Generate an outline and the copilot picks a fitting narrative structure (it won't force a fixed template) with a section for each beat.",
        "Each section states its purpose and rough duration, so you can see the shape of the video before any script is written.",
        "Review the flow first; a solid outline makes the full script far stronger.",
        "Use the refine box to reshape it, e.g. 'add a stronger reveal before the payoff'.",
      ]}
    >
      {generate.isPending && !hasOutline && (
        <GeneratingState
          message={generate.phase || "Building the story outline…"}
          rows={4}
        />
      )}

      {!generate.isPending && !hasOutline && (
        <EmptyState
          icon={ListTree}
          title="No outline yet"
          description="Generate a narrative structure with ordered sections and time budgets."
          action={
            <Button
              variant="generate"
              loading={generate.isPending}
              onClick={() => generate.mutate({})}
            >
              <Sparkles className="h-4 w-4" />
              Generate outline
            </Button>
          }
        />
      )}

      {hasOutline && outline && (
        <>
          <Card className="mb-4 flex flex-wrap items-center justify-between gap-2 p-4">
            <div>
              <div className="label text-[9px] text-muted">
                Narrative structure
              </div>
              <div className="text-sm font-medium text-text">
                {outline.narrative_structure}
              </div>
            </div>
            <div className="flex items-center gap-1.5 font-mono text-xs tabular-nums text-subtle">
              <Clock className="h-3.5 w-3.5 text-muted" />
              {humanDuration(outline.estimated_duration_seconds)} est.
            </div>
          </Card>

          <ol className="space-y-2.5">
            {outline.sections.map((section, i) => (
              <li key={i}>
                <Card className="flex gap-3 p-4">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-sm border border-borderStrong font-mono text-[11px] tabular-nums text-subtle">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <Badge tone="neutral">{section.type}</Badge>
                      <span className="font-mono text-[11px] tabular-nums text-muted">
                        {humanDuration(section.estimated_duration_seconds)}
                      </span>
                    </div>
                    <div className="mb-1 text-xs font-medium text-text">
                      {section.purpose}
                    </div>
                    <p className="text-xs leading-relaxed text-subtle">
                      {section.summary}
                    </p>
                  </div>
                </Card>
              </li>
            ))}
          </ol>

          <div className="mt-4 border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Regenerate"
              placeholder="Refine, e.g. 'tighten the middle section'…"
              loading={generate.isPending}
              onSubmit={(instruction) =>
                generate.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={generate.error} />
          </div>
        </>
      )}
    </Panel>
  );
}
