"use client";

import { Check, Sparkles, Compass } from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreBar } from "@/components/ui/score-bar";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { useGenerateAngles, useSelectAngle } from "@/hooks/useWorkspace";
import type { ProjectDetail } from "@/types";

export function AnglesPanel({ project }: { project: ProjectDetail }) {
  const generate = useGenerateAngles(project.id);
  const select = useSelectAngle(project.id);

  const angles = project.angles || [];
  const hasAngles = angles.length > 0;

  return (
    <Panel
      step="03"
      eyebrow="Find the frame"
      title="Content Angle"
      description="Distinct ways to frame the story. Pick the one that fits your voice."
      guideKey="angles"
      guide={[
        "Generate 5 to 8 angles: distinct ways to frame the same topic (investigative, comparison, hidden history, and more).",
        "Each card shows why the angle works and an estimated audience-interest score to compare at a glance.",
        "Pick one angle. It anchors the hook, story outline, and script that follow.",
        "Not seeing the right frame? Use the refine box to regenerate, e.g. 'more contrarian takes'.",
      ]}
    >
      {generate.isPending && !hasAngles && (
        <GeneratingState message="Generating content angles…" columns={2} rows={3} />
      )}

      {!generate.isPending && !hasAngles && (
        <EmptyState
          icon={Compass}
          title="No angles yet"
          description="Generate 5 to 8 framing options with a rationale and estimated audience interest for each."
          action={
            <Button
              variant="generate"
              loading={generate.isPending}
              onClick={() => generate.mutate({})}
            >
              <Sparkles className="h-4 w-4" />
              Generate angles
            </Button>
          }
        />
      )}

      {hasAngles && (
        <>
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            {angles.map((angle) => (
              <Card
                key={angle.id}
                selected={angle.selected}
                interactive
                className="flex flex-col p-4"
              >
                <div className="mb-1.5 flex items-start justify-between gap-2">
                  <h3 className="text-sm font-semibold text-text">
                    {angle.title}
                  </h3>
                  <Badge tone="neutral">{angle.style}</Badge>
                </div>
                <p className="mb-3 text-xs leading-relaxed text-subtle">
                  {angle.summary}
                </p>
                <div className="mb-3 rounded border border-border bg-bg/50 p-2.5">
                  <div className="label mb-0.5 text-[9px] text-muted">
                    Why it works
                  </div>
                  <p className="text-[11px] leading-relaxed text-subtle">
                    {angle.why_it_works}
                  </p>
                </div>
                <div className="mb-3">
                  <div className="label mb-1 text-[9px] text-muted">
                    Audience interest
                  </div>
                  <ScoreBar value={angle.estimated_audience_interest} />
                </div>
                <div className="mt-auto">
                  {angle.selected ? (
                    <Button
                      variant="secondary"
                      size="sm"
                      className="w-full justify-center border-accent text-accent"
                      disabled
                    >
                      <Check className="h-3.5 w-3.5" />
                      Selected
                    </Button>
                  ) : (
                    <Button
                      variant="primary"
                      size="sm"
                      className="w-full justify-center"
                      loading={
                        select.isPending && select.variables === angle.id
                      }
                      onClick={() => select.mutate(angle.id)}
                    >
                      Select this angle
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>

          <div className="mt-4 border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Regenerate"
              placeholder="Refine, e.g. 'more contrarian takes'…"
              loading={generate.isPending}
              onSubmit={(instruction) =>
                generate.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={generate.error || select.error} />
          </div>
        </>
      )}
    </Panel>
  );
}
