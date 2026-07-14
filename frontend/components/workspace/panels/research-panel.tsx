"use client";

import {
  Sparkles,
  BookOpen,
  ExternalLink,
  Info,
  Calendar,
} from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { cn } from "@/lib/utils";
import {
  useRunResearch,
  useSelectResearchSource,
} from "@/hooks/useWorkspace";
import type { ProjectDetail } from "@/types";

export function ResearchPanel({ project }: { project: ProjectDetail }) {
  const run = useRunResearch(project.id);
  const selectSource = useSelectResearchSource(project.id);

  const sources = project.research_sources || [];
  const hasSources = sources.length > 0;
  // research_enabled is only meaningful once research has been attempted.
  const researchDisabled = project.research_enabled === false;
  const hasRun = project.research_enabled !== undefined;

  return (
    <Panel
      step="05"
      eyebrow="Check the facts"
      title="Research"
      description="Ground the script in verifiable facts and cited sources."
      guideKey="research"
      guide={[
        "Run research to search the web for real sources, then have the copilot synthesize the relevant facts. Every source links back to where it came from.",
        "The copilot never invents sources; if a claim isn't in the retrieved results, it won't appear here.",
        "If no search provider is configured, you'll see non-researched mode: you can still proceed, but verify facts yourself.",
        "Research is optional. Skip ahead to Story if your topic doesn't need external sources.",
      ]}
    >
      {researchDisabled && (
        <div className="mb-4 flex items-start gap-2.5 rounded border-l-2 border-warning bg-warning/10 p-3">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-warning" />
          <div>
            <div className="label text-[11px] text-warning">
              Non-researched mode
            </div>
            <p className="mt-0.5 text-[11px] leading-relaxed text-subtle">
              No web-search key is configured on the backend, so the copilot is
              working without live sources. You can still proceed to the outline
              and script; just verify any factual claims yourself.
            </p>
          </div>
        </div>
      )}

      {run.isPending && !hasSources && (
        <GeneratingState message="Researching sources…" rows={3} />
      )}

      {!run.isPending && !hasSources && !researchDisabled && (
        <EmptyState
          icon={BookOpen}
          title="No research yet"
          description="Run research to gather sources, publishers, and key facts you can weave into the story."
          action={
            <Button
              variant="generate"
              loading={run.isPending}
              onClick={() => run.mutate({})}
            >
              <Sparkles className="h-4 w-4" />
              Run research
            </Button>
          }
        />
      )}

      {!run.isPending && !hasSources && researchDisabled && (
        <EmptyState
          icon={BookOpen}
          title="No live sources available"
          description="Research ran in non-researched mode. You can proceed to the next stage."
        />
      )}

      {hasSources && (
        <>
          <div className="mb-3 flex items-center justify-between gap-2 text-[11px] text-muted">
            <span>
              Tick the sources to weave into the story and script. Unticked
              sources are ignored.
            </span>
            <span className="shrink-0 font-mono tabular-nums text-subtle">
              {sources.filter((s) => s.selected !== false).length}/{sources.length} selected
            </span>
          </div>
          <div className="space-y-3">
            {sources.map((s) => {
              const on = s.selected !== false;
              return (
              <Card
                key={s.id}
                className={cn(
                  "p-4 transition-opacity",
                  !on && "opacity-50"
                )}
              >
                <div className="mb-1 flex items-start justify-between gap-3">
                  <label className="flex min-w-0 items-start gap-2.5">
                    <input
                      type="checkbox"
                      checked={on}
                      onChange={(e) =>
                        selectSource.mutate({
                          sourceId: s.id,
                          selected: e.target.checked,
                        })
                      }
                      className="mt-1 h-3.5 w-3.5 shrink-0 accent-accent"
                      aria-label={`Include ${s.title}`}
                    />
                    <h3 className="text-sm font-semibold leading-snug text-text">
                      {s.title}
                    </h3>
                  </label>
                  {s.url && (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-0.5 shrink-0 text-muted hover:text-accent"
                      aria-label="Open source"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  )}
                </div>
                <div className="mb-2 flex flex-wrap items-center gap-2 text-[11px] text-muted">
                  {s.publisher && <Badge tone="muted">{s.publisher}</Badge>}
                  {s.published_at && (
                    <span className="inline-flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {new Date(s.published_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <p className="mb-3 text-xs leading-relaxed text-subtle">
                  {s.summary}
                </p>
                {s.key_facts && s.key_facts.length > 0 && (
                  <div className="rounded border border-border bg-bg/50 p-2.5">
                    <div className="label mb-1 text-[9px] text-muted">
                      Key facts
                    </div>
                    <ul className="space-y-1">
                      {s.key_facts.map((f, i) => (
                        <li
                          key={i}
                          className="flex gap-1.5 text-[11px] leading-relaxed text-subtle"
                        >
                          <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-success" />
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </Card>
              );
            })}
          </div>

          <div className="mt-4 border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Re-run"
              placeholder="Refine research, e.g. 'focus on primary sources'…"
              loading={run.isPending}
              onSubmit={(instruction) =>
                run.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={run.error} />
          </div>
        </>
      )}
    </Panel>
  );
}
