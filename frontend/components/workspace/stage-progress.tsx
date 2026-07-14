"use client";

import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { STAGE_ORDER, STAGE_LABELS, stageIndex } from "@/lib/constants";
import type { ProjectStage } from "@/types";

/**
 * The beat sheet. Each production stage is a numbered beat in the running order
 * of a script. Completed beats are marked in the approved-margin sage; the beat
 * being worked reads in proofreader's red with a "drafting" tag; beats still
 * ahead stay muted. Honestly numbered because the pipeline genuinely is a
 * sequence. Clicking a beat jumps to it (behavior unchanged).
 */
export function StageProgress({
  currentStage,
  activeStage,
  completed,
  onSelect,
}: {
  currentStage: ProjectStage;
  activeStage: ProjectStage;
  completed: Record<ProjectStage, boolean>;
  onSelect: (stage: ProjectStage) => void;
}) {
  const progressIdx = stageIndex(currentStage);

  return (
    <div className="overflow-x-auto rounded border border-border bg-panel">
      <div className="flex items-center gap-2 border-b border-border px-3 py-1.5">
        <span className="label text-[9px] text-muted">Running order</span>
        <span className="h-px flex-1 bg-border" />
        <span className="font-mono text-[9px] tabular-nums text-muted">
          {String(Math.min(progressIdx + 1, STAGE_ORDER.length)).padStart(2, "0")}/
          {String(STAGE_ORDER.length).padStart(2, "0")}
        </span>
      </div>
      <div className="flex items-stretch">
        {STAGE_ORDER.map((stage, i) => {
          const isDone = completed[stage];
          const isActive = stage === activeStage;
          const isReached = i <= progressIdx || isDone;

          return (
            <button
              key={stage}
              onClick={() => onSelect(stage)}
              aria-current={isActive ? "step" : undefined}
              className={cn(
                "group relative flex min-w-[104px] flex-1 flex-col items-start gap-2 border-r border-border px-3 py-3 text-left transition-colors last:border-r-0",
                isActive ? "bg-accent/[0.07]" : "hover:bg-elevated"
              )}
            >
              {/* Proofreader's mark down the left edge of the active beat */}
              {isActive && (
                <span className="absolute inset-y-0 left-0 w-[3px] bg-accent" />
              )}
              <div className="flex w-full items-center gap-2">
                <span
                  className={cn(
                    "flex h-6 w-6 shrink-0 items-center justify-center rounded-sm border font-mono text-[10px] tabular-nums",
                    isDone
                      ? "border-success bg-success/20 text-success"
                      : isActive
                        ? "border-accent bg-accent text-text font-semibold"
                        : "border-borderStrong text-muted"
                  )}
                >
                  {isDone ? (
                    <Check className="h-3.5 w-3.5" strokeWidth={2.5} />
                  ) : (
                    String(i + 1).padStart(2, "0")
                  )}
                </span>
                {isActive && (
                  <span className="label ml-auto text-[8px] text-accent">
                    drafting
                  </span>
                )}
              </div>
              <span
                className={cn(
                  "serif whitespace-nowrap text-[13px] leading-none",
                  isActive
                    ? "text-text"
                    : isReached
                      ? "text-subtle"
                      : "text-muted"
                )}
              >
                {STAGE_LABELS[stage]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
