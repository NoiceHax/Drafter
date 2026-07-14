"use client";

import * as React from "react";
import { Save, Pencil, Sparkles, Check, Wand2, HelpCircle } from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Textarea, Select, Label } from "@/components/ui/input";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { PlatformBadge } from "@/components/platform-badge";
import { Badge } from "@/components/ui/badge";
import { useUpdateProject } from "@/hooks/useProjects";
import { useRefineIdea } from "@/hooks/useWorkspace";
import {
  PLATFORM_OPTIONS,
  TONE_OPTIONS,
  TONE_LABELS,
} from "@/lib/constants";
import { humanDuration } from "@/lib/utils";
import type { Platform, ProjectDetail, Tone } from "@/types";

export function IdeaPanel({ project }: { project: ProjectDetail }) {
  const [editing, setEditing] = React.useState(false);
  const update = useUpdateProject(project.id);

  const [title, setTitle] = React.useState(project.title || "");
  const [idea, setIdea] = React.useState(project.idea);
  const [platform, setPlatform] = React.useState<Platform>(project.platform);
  const [tone, setTone] = React.useState<Tone>(project.tone);
  const [customTone, setCustomTone] = React.useState(project.custom_tone || "");
  const [duration, setDuration] = React.useState(
    project.target_duration_seconds
  );

  React.useEffect(() => {
    setTitle(project.title || "");
    setIdea(project.idea);
    setPlatform(project.platform);
    setTone(project.tone);
    setCustomTone(project.custom_tone || "");
    setDuration(project.target_duration_seconds);
  }, [project]);

  const save = async () => {
    await update.mutateAsync({
      title: title.trim() || undefined,
      idea: idea.trim(),
      platform,
      tone,
      custom_tone: tone === "custom" ? customTone.trim() || undefined : undefined,
      target_duration_seconds: duration,
    });
    setEditing(false);
  };

  return (
    <Panel
      step="01"
      eyebrow="The brief"
      title="Idea & Brief"
      description="A rough idea is enough to start. Refine it with AI to sharpen the direction before the rest of the pipeline builds on it."
      guideKey="idea"
      guide={[
        "Give a rough idea, even a few words. It's a starting seed, not the final brief.",
        "Click Refine with AI: the copilot proposes a sharper premise, explains what it assumed, and offers alternative directions and questions.",
        "Accept the refinement, pick a different direction, or steer it further until it's the direction you meant. Then it becomes your idea.",
        "Set platform, duration, and tone so everything downstream is written for the right format and voice.",
      ]}
      actions={
        !editing ? (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <Pencil className="h-3.5 w-3.5" />
            Edit
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={() => setEditing(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              loading={update.isPending}
              onClick={save}
            >
              <Save className="h-3.5 w-3.5" />
              Save
            </Button>
          </div>
        )
      }
    >
      <Card className="p-5">
        {!editing ? (
          <div className="space-y-4">
            <div>
              <div className="label text-[10px] text-muted">Title</div>
              <div className="mt-0.5 text-sm text-text">
                {project.title || <span className="text-muted">Untitled</span>}
              </div>
            </div>
            <div>
              <div className="label text-[10px] text-muted">Idea</div>
              <p className="mt-0.5 whitespace-pre-wrap text-sm leading-relaxed text-text">
                {project.idea || (
                  <span className="text-muted">No idea yet.</span>
                )}
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2 border-t border-border pt-4">
              <PlatformBadge platform={project.platform} />
              <Badge tone="muted">
                {humanDuration(project.target_duration_seconds)}
              </Badge>
              <Badge tone="neutral">
                {project.tone === "custom" && project.custom_tone
                  ? project.custom_tone
                  : TONE_LABELS[project.tone]}
              </Badge>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Untitled"
              />
            </div>
            <div>
              <Label>Idea</Label>
              <Textarea
                rows={4}
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
              />
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <Label>Platform</Label>
                <Select
                  value={platform}
                  onChange={(e) => setPlatform(e.target.value as Platform)}
                >
                  {PLATFORM_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </Select>
              </div>
              <div>
                <Label>Target duration (s)</Label>
                <Input
                  type="number"
                  min={5}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                />
              </div>
            </div>
            <div>
              <Label>Tone</Label>
              <Select
                value={tone}
                onChange={(e) => setTone(e.target.value as Tone)}
              >
                {TONE_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </Select>
            </div>
            {tone === "custom" && (
              <div>
                <Label>Custom tone</Label>
                <Input
                  value={customTone}
                  onChange={(e) => setCustomTone(e.target.value)}
                />
              </div>
            )}
            <InlineError error={update.error} />
          </div>
        )}
      </Card>

      {!editing && <IdeaRefiner project={project} />}
    </Panel>
  );
}

/**
 * The refinement loop. The creator's rough idea is a seed; the copilot proposes
 * a sharper premise, alternative directions, and clarifying questions. The
 * creator accepts one, steers with an instruction, or answers a question, and
 * only then does it become the project's idea.
 */
function IdeaRefiner({ project }: { project: ProjectDetail }) {
  const refine = useRefineIdea(project.id);
  const update = useUpdateProject(project.id);
  const result = refine.data;

  const accept = (nextIdea: string) =>
    update.mutate({ idea: nextIdea.trim() });

  const accepted = update.isSuccess && !update.isPending;

  return (
    <div className="mt-3">
      {!result && (
        <div className="flex items-center justify-between rounded border border-dashed border-borderStrong bg-panel/50 px-4 py-3">
          <div className="flex items-center gap-2 text-xs text-subtle">
            <Wand2 className="h-4 w-4 text-accent" />
            Not sure the idea is sharp enough? Let the copilot refine it and check
            the direction with you.
          </div>
          <Button
            variant="generate"
            size="sm"
            loading={refine.isPending}
            onClick={() => refine.mutate({})}
          >
            <Sparkles className="h-3.5 w-3.5" />
            Refine with AI
          </Button>
        </div>
      )}

      {refine.isPending && !result && (
        <p className="mt-2 text-[11px] text-muted">
          Reading your idea and thinking through the strongest direction…
        </p>
      )}

      <InlineError error={refine.error || update.error} />

      {result && (
        <Card className="mt-3 space-y-4 border-l-2 border-l-accent p-4">
          <div className="flex items-center gap-2">
            <Wand2 className="h-4 w-4 text-accent" />
            <span className="label text-[10px] text-accent">
              Proposed direction
            </span>
            {accepted && (
              <span className="label ml-auto inline-flex items-center gap-1 text-[9px] text-success">
                <Check className="h-3 w-3" />
                Applied
              </span>
            )}
          </div>

          {/* Refined idea */}
          <div>
            <div className="label mb-1 text-[9px] text-muted">
              Refined idea
            </div>
            <p className="text-sm leading-relaxed text-text">
              {result.refined_idea}
            </p>
            <div className="mt-2">
              <Button
                variant="primary"
                size="sm"
                loading={update.isPending}
                onClick={() => accept(result.refined_idea)}
              >
                <Check className="h-3.5 w-3.5" />
                Use this idea
              </Button>
            </div>
          </div>

          {/* Interpretation */}
          <div className="rounded border border-border bg-bg/40 p-2.5">
            <div className="label mb-0.5 text-[9px] text-muted">
              What the copilot understood
            </div>
            <p className="text-[11px] leading-relaxed text-subtle">
              {result.interpretation}
            </p>
          </div>

          {/* Alternative directions */}
          {result.directions.length > 0 && (
            <div>
              <div className="label mb-1.5 text-[9px] text-muted">
                Or take it a different way
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                {result.directions.map((d, i) => (
                  <div
                    key={i}
                    className="flex flex-col rounded border border-border bg-bg/40 p-2.5"
                  >
                    <div className="mb-1 text-xs font-semibold text-text">
                      {d.title}
                    </div>
                    <p className="mb-2 flex-1 text-[11px] leading-relaxed text-subtle">
                      {d.idea}
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      className="justify-center"
                      loading={update.isPending}
                      onClick={() => accept(d.idea)}
                    >
                      Use this
                    </Button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Clarifying questions */}
          {result.clarifying_questions.length > 0 && (
            <div className="rounded border border-border bg-bg/40 p-2.5">
              <div className="label mb-1 flex items-center gap-1.5 text-[9px] text-muted">
                <HelpCircle className="h-3 w-3" />
                To sharpen it further, answer any of these
              </div>
              <ul className="flex flex-col gap-1">
                {result.clarifying_questions.map((q, i) => (
                  <li
                    key={i}
                    className="flex gap-2 text-[11px] leading-relaxed text-subtle"
                  >
                    <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
                    <span>{q}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Steer / answer to refine again */}
          <div className="border-t border-border pt-3">
            <InstructionInput
              buttonLabel="Refine again"
              placeholder="Answer a question or steer it, e.g. 'focus on the 1970s, for beginners'…"
              loading={refine.isPending}
              onSubmit={(text) =>
                refine.mutate(text ? { answers: text } : {})
              }
            />
          </div>
        </Card>
      )}
    </div>
  );
}
