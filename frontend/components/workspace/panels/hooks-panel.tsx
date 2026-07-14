"use client";

import * as React from "react";
import {
  Check,
  Sparkles,
  Zap,
  Star,
  RefreshCw,
  Pencil,
  Save,
  HelpCircle,
  Gift,
} from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScoreBar } from "@/components/ui/score-bar";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { Input, Textarea, Select } from "@/components/ui/input";
import { cn, humanDuration } from "@/lib/utils";
import { HOOK_ARCHETYPES, HOOK_ARCHETYPE_LABELS } from "@/lib/constants";
import {
  useGenerateHooks,
  useSelectHook,
  useRegenerateHook,
} from "@/hooks/useWorkspace";
import type { Hook, HookArchetype, ProjectDetail } from "@/types";

export function HooksPanel({ project }: { project: ProjectDetail }) {
  const generate = useGenerateHooks(project.id);
  const select = useSelectHook(project.id);
  const regenerate = useRegenerateHook(project.id);

  const hooks = project.hooks || [];
  const analysis = project.hook_analysis || [];
  const recommendedId = project.recommended_hook_id;
  const hasHooks = hooks.length > 0;

  const grouped = HOOK_ARCHETYPES.reduce(
    (acc, a) => {
      acc[a] = hooks.filter((h) => h.archetype === a);
      return acc;
    },
    {} as Record<HookArchetype, Hook[]>
  );

  return (
    <Panel
      step="04"
      eyebrow="Write the open"
      title="Hook"
      description="The first three seconds. Pick the opening line that stops the scroll."
      guideKey="hooks"
      guide={[
        "The copilot scores all ten hook archetypes for how well they fit your story, then writes hooks only for the ones that genuinely work.",
        "Hooks are grouped by archetype; the recommended pick is highlighted. Read the unanswered question and payoff to judge each.",
        "Select a hook to lock it in. You can edit its text inline, generate another variation in the same archetype, or switch archetypes.",
        "Use a hook's refine box for targeted changes, e.g. 'make it shorter' or 'raise the stakes without inventing facts'.",
      ]}
    >
      {generate.isPending && !hasHooks && (
        <GeneratingState
          message={generate.phase || "Analyzing archetypes and generating hooks…"}
          rows={4}
        />
      )}

      {!generate.isPending && !hasHooks && (
        <EmptyState
          icon={Zap}
          title="No hooks yet"
          description="Generate hooks across ten proven archetypes, with a suitability analysis and a recommended pick."
          action={
            <Button
              variant="generate"
              loading={generate.isPending}
              onClick={() => generate.mutate({})}
            >
              <Sparkles className="h-4 w-4" />
              Generate hooks
            </Button>
          }
        />
      )}

      {hasHooks && (
        <div className="space-y-5">
          {/* Archetype suitability analysis */}
          {analysis.length > 0 && (
            <Card className="p-4">
              <h3 className="label mb-3 text-[11px] text-subtle">
                Archetype suitability
              </h3>
              <div className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2">
                {analysis.map((a) => (
                  <div key={a.archetype}>
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <span className="text-xs font-medium text-text">
                        {HOOK_ARCHETYPE_LABELS[a.archetype] ?? a.archetype}
                      </span>
                    </div>
                    <ScoreBar value={a.suitability_score} className="mb-1" />
                    <p className="text-[11px] leading-relaxed text-muted">
                      {a.reason}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Hooks grouped by archetype */}
          <div className="space-y-5">
            {HOOK_ARCHETYPES.filter((a) => grouped[a].length > 0).map((a) => (
              <div key={a}>
                <div className="mb-2 flex items-center gap-2">
                  <h3 className="label text-[11px] text-subtle">
                    {HOOK_ARCHETYPE_LABELS[a]}
                  </h3>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <div className="space-y-2.5">
                  {grouped[a].map((hook) => (
                    <HookCard
                      key={hook.id}
                      hook={hook}
                      recommended={hook.id === recommendedId}
                      onSelect={() => select.mutate(hook.id)}
                      selecting={
                        select.isPending && select.variables === hook.id
                      }
                      onRegenerate={(args) =>
                        regenerate.mutate({ hookId: hook.id, ...args })
                      }
                      regenerating={
                        regenerate.isPending &&
                        regenerate.variables?.hookId === hook.id
                      }
                      projectId={project.id}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Regenerate all"
              placeholder="Refine, e.g. 'punchier, more provocative'…"
              loading={generate.isPending}
              onSubmit={(instruction) =>
                generate.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={generate.error || select.error} />
          </div>
        </div>
      )}
    </Panel>
  );
}

function HookCard({
  hook,
  recommended,
  onSelect,
  selecting,
  onRegenerate,
  regenerating,
  projectId,
}: {
  hook: Hook;
  recommended: boolean;
  onSelect: () => void;
  selecting: boolean;
  onRegenerate: (args: { instruction?: string; archetype?: string }) => void;
  regenerating: boolean;
  projectId: string;
}) {
  const [editing, setEditing] = React.useState(false);
  const [refineOpen, setRefineOpen] = React.useState(false);
  const [refine, setRefine] = React.useState("");
  const [draft, setDraft] = React.useState(hook.text);

  // Inline edit persists via regenerate with an explicit instruction so the
  // backend records the exact text. (No dedicated PATCH hook endpoint.)
  const saveEdit = () => {
    onRegenerate({ instruction: `Use exactly this hook text: "${draft}"` });
    setEditing(false);
  };

  return (
    <Card
      selected={hook.selected}
      className={cn("p-4", recommended && !hook.selected && "border-accent/50")}
    >
      <div className="mb-2 flex flex-wrap items-center gap-1.5">
        {recommended && (
          <Badge tone="accent">
            <Star className="h-3 w-3" />
            Recommended
          </Badge>
        )}
        <Badge tone="neutral">
          {HOOK_ARCHETYPE_LABELS[hook.archetype] ?? hook.archetype}
        </Badge>
        <Badge tone="muted">
          {humanDuration(hook.estimated_duration_seconds)}
        </Badge>
        <div className="ml-auto flex w-28 items-center gap-1.5">
          <span className="label text-[9px] text-muted">fit</span>
          <ScoreBar value={hook.suitability_score} />
        </div>
      </div>

      {!editing ? (
        <p className="mb-3 text-sm font-medium leading-relaxed text-text">
          &ldquo;{hook.text}&rdquo;
        </p>
      ) : (
        <div className="mb-3">
          <Textarea
            rows={2}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
          <div className="mt-2 flex gap-2">
            <Button
              variant="primary"
              size="sm"
              loading={regenerating}
              onClick={saveEdit}
            >
              <Save className="h-3.5 w-3.5" />
              Save
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setDraft(hook.text);
                setEditing(false);
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {(hook.unanswered_question || hook.story_payoff) && (
        <div className="mb-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {hook.unanswered_question && (
            <div className="rounded border border-border bg-bg/50 p-2.5">
              <div className="label mb-0.5 flex items-center gap-1 text-[9px] text-muted">
                <HelpCircle className="h-3 w-3" />
                Open question
              </div>
              <p className="text-[11px] leading-relaxed text-subtle">
                {hook.unanswered_question}
              </p>
            </div>
          )}
          {hook.story_payoff && (
            <div className="rounded border border-border bg-bg/50 p-2.5">
              <div className="label mb-0.5 flex items-center gap-1 text-[9px] text-muted">
                <Gift className="h-3 w-3" />
                Payoff
              </div>
              <p className="text-[11px] leading-relaxed text-subtle">
                {hook.story_payoff}
              </p>
            </div>
          )}
        </div>
      )}

      {!editing && (
        <div className="flex flex-wrap items-center gap-2">
          {hook.selected ? (
            <Button
              variant="secondary"
              size="sm"
              className="border-accent text-accent"
              disabled
            >
              <Check className="h-3.5 w-3.5" />
              Selected
            </Button>
          ) : (
            <Button
              variant="primary"
              size="sm"
              loading={selecting}
              onClick={onSelect}
            >
              Select
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setEditing(true)}
          >
            <Pencil className="h-3.5 w-3.5" />
            Edit
          </Button>
          <Button
            variant="ghost"
            size="sm"
            loading={regenerating}
            onClick={() => onRegenerate({ archetype: hook.archetype })}
            title="Another variation in the same archetype"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Another variation
          </Button>
          <Select
            value={hook.archetype}
            onChange={(e) =>
              onRegenerate({ archetype: e.target.value })
            }
            className="h-7 w-auto text-xs"
            title="Change archetype"
          >
            {HOOK_ARCHETYPES.map((a) => (
              <option key={a} value={a}>
                {HOOK_ARCHETYPE_LABELS[a]}
              </option>
            ))}
          </Select>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setRefineOpen((v) => !v)}
          >
            <Sparkles className="h-3.5 w-3.5" />
            Refine
          </Button>
        </div>
      )}

      {refineOpen && !editing && (
        <form
          className="mt-2 flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            onRegenerate({
              instruction: refine.trim() || undefined,
              archetype: hook.archetype,
            });
            setRefine("");
            setRefineOpen(false);
          }}
        >
          <Input
            value={refine}
            onChange={(e) => setRefine(e.target.value)}
            placeholder="Custom refinement instruction…"
            className="flex-1"
            autoFocus
          />
          <Button type="submit" variant="primary" size="sm" loading={regenerating}>
            Apply
          </Button>
        </form>
      )}
    </Card>
  );
}
