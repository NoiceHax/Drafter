"use client";

import * as React from "react";
import {
  Sparkles,
  Film,
  RefreshCw,
  Pencil,
  Save,
  Zap,
  Megaphone,
  Clock,
} from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { Textarea, Input } from "@/components/ui/input";
import { ScriptExport } from "../script-export";
import { formatTime, humanDuration } from "@/lib/utils";
import {
  useGenerateScript,
  useRegenerateScene,
  useUpdateScene,
  useEditScript,
} from "@/hooks/useWorkspace";
import type { ProjectDetail, ScriptScene } from "@/types";

export function ScriptPanel({ project }: { project: ProjectDetail }) {
  const generate = useGenerateScript(project.id);
  const script = project.script;
  const hasScript = !!script && script.scenes?.length > 0;

  return (
    <Panel
      step="07"
      eyebrow="Write the draft"
      title="Script"
      description="The full draft: scene by scene, timed on the page. Every line is editable."
      guideKey="script"
      guide={[
        "Generate the full script: a hook, timed scenes with narration, on-screen text and visual direction, and a closing CTA.",
        "Edit any line inline with the Edit button on a scene, or regenerate just one scene's narration or visual direction without redoing the whole script.",
        "The hook and CTA are editable too; click Edit on either to adjust the wording.",
        "Use the Export bar to copy or download the finished script as Markdown, plain text, or narration only.",
        "Watch the estimated vs target duration badge to keep the video on length.",
      ]}
    >
      {generate.isPending && !hasScript && (
        <GeneratingState
          message={generate.phase || "Writing the full script…"}
          rows={4}
        />
      )}

      {!generate.isPending && !hasScript && (
        <EmptyState
          icon={Film}
          title="No script yet"
          description="Generate a complete script: hook, scene-by-scene narration with on-screen text and visual directions, and a CTA."
          action={
            <Button
              variant="generate"
              loading={generate.isPending}
              onClick={() => generate.mutate({})}
            >
              <Sparkles className="h-4 w-4" />
              Generate script
            </Button>
          }
        />
      )}

      {hasScript && script && (
        <div className="space-y-3">
          <ScriptMeta script={script} />
          <ScriptExport script={script} />

          {/* Hook (editable) */}
          <EditableScriptBlock
            projectId={project.id}
            scriptId={script.id}
            field="hook_text"
            value={script.hook_text}
            tone="accent"
            label="Hook"
            icon={<Zap className="h-3 w-3" />}
            timing={
              <>
                {formatTime(0)}
                <span className="mx-1.5 text-borderStrong">────</span>
                {formatTime(script.hook_duration_seconds)}
              </>
            }
            quoted
          />

          {/* Scenes */}
          {script.scenes.map((scene) => (
            <SceneCard key={scene.id} scene={scene} projectId={project.id} />
          ))}

          {/* CTA (editable) */}
          <EditableScriptBlock
            projectId={project.id}
            scriptId={script.id}
            field="cta_text"
            value={script.cta_text || ""}
            tone="info"
            label="CTA"
            icon={<Megaphone className="h-3 w-3" />}
            timing={humanDuration(script.cta_duration_seconds)}
            placeholder="Add a closing call to action…"
          />

          <div className="border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Regenerate script"
              placeholder="Refine, e.g. 'more concise narration throughout'…"
              loading={generate.isPending}
              onSubmit={(instruction) =>
                generate.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={generate.error} />
          </div>
        </div>
      )}
    </Panel>
  );
}

function ScriptMeta({
  script,
}: {
  script: NonNullable<ProjectDetail["script"]>;
}) {
  const over = script.estimated_duration_seconds > script.target_duration_seconds;
  return (
    <Card className="flex flex-wrap items-center gap-x-6 gap-y-2 p-3">
      <div className="flex items-center gap-2">
        <Clock className="h-4 w-4 text-muted" />
        <div>
          <div className="label text-[9px] text-muted">Estimated</div>
          <div className="font-mono text-sm tabular-nums text-text">
            {humanDuration(script.estimated_duration_seconds)}
          </div>
        </div>
      </div>
      <div>
        <div className="label text-[9px] text-muted">Target</div>
        <div className="font-mono text-sm tabular-nums text-text">
          {humanDuration(script.target_duration_seconds)}
        </div>
      </div>
      <Badge tone={over ? "danger" : "success"}>
        {over ? "Over target" : "On target"}
      </Badge>
      <span className="ml-auto font-mono text-[11px] tabular-nums text-muted">
        {script.scenes.length} scenes
      </span>
    </Card>
  );
}

function SceneCard({
  scene,
  projectId,
}: {
  scene: ScriptScene;
  projectId: string;
}) {
  const update = useUpdateScene(projectId);
  const regen = useRegenerateScene(projectId);

  const [editing, setEditing] = React.useState(false);
  const [narration, setNarration] = React.useState(scene.narration);
  const [onScreen, setOnScreen] = React.useState(scene.on_screen_text || "");
  const [visual, setVisual] = React.useState(scene.visual_direction || "");

  React.useEffect(() => {
    setNarration(scene.narration);
    setOnScreen(scene.on_screen_text || "");
    setVisual(scene.visual_direction || "");
  }, [scene]);

  const save = async () => {
    await update.mutateAsync({
      sceneId: scene.id,
      narration,
      on_screen_text: onScreen,
      visual_direction: visual,
    });
    setEditing(false);
  };

  const regenField = (field: "narration" | "visual_direction" | "all") =>
    regen.mutate({ sceneId: scene.id, field });

  const isRegenNarration =
    regen.isPending && regen.variables?.field === "narration";
  const isRegenVisual =
    regen.isPending && regen.variables?.field === "visual_direction";

  return (
    <Card className="relative p-4 pl-5">
      {/* Timeline spine */}
      <span className="absolute inset-y-0 left-0 w-0.5 bg-borderStrong" />
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="flex h-6 min-w-6 items-center justify-center rounded-sm border border-borderStrong px-1 font-mono text-[11px] tabular-nums text-subtle">
          {String(scene.scene_number).padStart(2, "0")}
        </span>
        <span className="font-mono text-xs tabular-nums text-subtle">
          {formatTime(scene.start_time)}
          <span className="mx-2 text-borderStrong">────</span>
          {formatTime(scene.end_time)}
        </span>
        <Badge tone="neutral">{scene.section_type}</Badge>
        <div className="ml-auto flex items-center gap-1">
          {!editing ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                loading={isRegenNarration}
                onClick={() => regenField("narration")}
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Narration
              </Button>
              <Button
                variant="ghost"
                size="sm"
                loading={isRegenVisual}
                onClick={() => regenField("visual_direction")}
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Visual
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setEditing(true)}
              >
                <Pencil className="h-3.5 w-3.5" />
                Edit
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="primary"
                size="sm"
                loading={update.isPending}
                onClick={save}
              >
                <Save className="h-3.5 w-3.5" />
                Save
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setNarration(scene.narration);
                  setOnScreen(scene.on_screen_text || "");
                  setVisual(scene.visual_direction || "");
                  setEditing(false);
                }}
              >
                Cancel
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="space-y-3">
        <Field label="Narration">
          {editing ? (
            <Textarea
              rows={2}
              value={narration}
              onChange={(e) => setNarration(e.target.value)}
            />
          ) : (
            <p className="text-sm leading-relaxed text-text">
              {scene.narration}
            </p>
          )}
        </Field>

        <Field label="On-screen text">
          {editing ? (
            <Input
              value={onScreen}
              onChange={(e) => setOnScreen(e.target.value)}
              placeholder="Optional on-screen text…"
            />
          ) : scene.on_screen_text ? (
            <p className="font-mono text-xs text-subtle">
              {scene.on_screen_text}
            </p>
          ) : (
            <p className="text-xs text-muted">-</p>
          )}
        </Field>

        <Field label="Visual direction">
          {editing ? (
            <Textarea
              rows={2}
              value={visual}
              onChange={(e) => setVisual(e.target.value)}
              placeholder="Describe what's on screen…"
            />
          ) : scene.visual_direction ? (
            <p className="text-xs leading-relaxed text-subtle">
              {scene.visual_direction}
            </p>
          ) : (
            <p className="text-xs text-muted">-</p>
          )}
        </Field>
      </div>

      <InlineError error={regen.error || update.error} />
    </Card>
  );
}

/** Editable Hook / CTA block. Shows the text with an Edit button; switches to
 *  a textarea with Save / Cancel. Persists via useEditScript (optimistic). */
function EditableScriptBlock({
  projectId,
  scriptId,
  field,
  value,
  tone,
  label,
  icon,
  timing,
  quoted,
  placeholder,
}: {
  projectId: string;
  scriptId: string;
  field: "hook_text" | "cta_text";
  value: string;
  tone: "accent" | "info";
  label: string;
  icon: React.ReactNode;
  timing: React.ReactNode;
  quoted?: boolean;
  placeholder?: string;
}) {
  const edit = useEditScript(projectId);
  const [editing, setEditing] = React.useState(false);
  const [draft, setDraft] = React.useState(value);

  React.useEffect(() => setDraft(value), [value]);

  const save = async () => {
    await edit.mutateAsync({ scriptId, [field]: draft } as never);
    setEditing(false);
  };

  const borderClass = tone === "accent" ? "border-l-accent" : "border-l-info";

  return (
    <Card className={`border-l-2 ${borderClass} p-4`}>
      <div className="mb-1.5 flex items-center gap-2">
        <Badge tone={tone}>
          {icon}
          {label}
        </Badge>
        <span className="font-mono text-[11px] tabular-nums text-muted">
          {timing}
        </span>
        {!editing && (
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto"
            onClick={() => setEditing(true)}
          >
            <Pencil className="h-3.5 w-3.5" />
            Edit
          </Button>
        )}
      </div>

      {editing ? (
        <div className="space-y-2">
          <Textarea
            rows={2}
            autoFocus
            value={draft}
            placeholder={placeholder}
            onChange={(e) => setDraft(e.target.value)}
          />
          <div className="flex items-center gap-2">
            <Button
              variant="primary"
              size="sm"
              loading={edit.isPending}
              onClick={save}
            >
              <Save className="h-3.5 w-3.5" />
              Save
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setDraft(value);
                setEditing(false);
              }}
            >
              Cancel
            </Button>
          </div>
        </div>
      ) : value ? (
        <p className="text-sm leading-relaxed text-text">
          {quoted ? <>&ldquo;{value}&rdquo;</> : value}
        </p>
      ) : (
        <p className="text-xs text-muted">{placeholder || "Not set"}</p>
      )}
    </Card>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div className="label mb-1 text-[9px] text-muted">{label}</div>
      {children}
    </div>
  );
}
