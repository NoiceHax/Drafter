"use client";

import * as React from "react";
import {
  Sparkles,
  ImageIcon,
  Search,
  ExternalLink,
  Wand2,
  Camera,
  Film,
} from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { Input } from "@/components/ui/input";
import { formatTime, cn } from "@/lib/utils";
import { PRIORITY_ORDER } from "@/lib/constants";
import {
  useGenerateSceneVisuals,
  useSearchSceneAssets,
} from "@/hooks/useWorkspace";
import type {
  ProjectDetail,
  ScriptScene,
  VisualPriority,
  VisualRecommendation,
} from "@/types";

const priorityTone: Record<VisualPriority, "danger" | "warning" | "muted"> = {
  high: "danger",
  medium: "warning",
  low: "muted",
};

export function VisualsPanel({ project }: { project: ProjectDetail }) {
  const script = project.script;
  const hasScenes = !!script && script.scenes?.length > 0;

  return (
    <Panel
      step="08"
      eyebrow="Mark the visuals"
      title="Visuals"
      description="Per scene: AI direction on what to show, plus real footage discovered from stock and media providers."
      guideKey="visuals"
      guide={[
        "Work scene by scene. For each, generate visual recommendations: specific briefs and search queries for what to show.",
        "Recommendations are directions, not images. They tell you what to find and why it fits the scene.",
        "Click Search assets to pull real, licensable media from the image provider. These are actual discovered files with a source link and license.",
        "The legend at the top distinguishes recommendations (what to show) from discovered assets (real media you can use).",
      ]}
    >
      {!hasScenes ? (
        <EmptyState
          icon={Film}
          title="Generate the script first"
          description="Visual recommendations and asset discovery work scene-by-scene, so you'll need a script before this step."
        />
      ) : (
        <div className="space-y-3">
          {/* Legend clarifying the two distinct concepts */}
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 rounded border border-border bg-panel/60 px-3 py-2.5 text-[11px]">
            <span className="label text-[9px] text-muted">Legend</span>
            <span className="inline-flex items-center gap-1.5 text-subtle">
              <span className="h-2.5 w-2.5 rounded-sm border border-accent-muted bg-accent-soft" />
              <Wand2 className="h-3.5 w-3.5 text-accent" />
              <strong className="font-semibold text-text">Recommendation</strong>{" "}
              : what to show (text brief, not an image)
            </span>
            <span className="inline-flex items-center gap-1.5 text-subtle">
              <span className="h-2.5 w-2.5 rounded-sm border border-info/40 bg-info/15" />
              <Camera className="h-3.5 w-3.5 text-info" />
              <strong className="font-semibold text-text">Discovered asset</strong>{" "}
              : real, licensable media from a provider
            </span>
          </div>

          {script!.scenes.map((scene) => (
            <SceneVisuals
              key={scene.id}
              scene={scene}
              projectId={project.id}
            />
          ))}
        </div>
      )}
    </Panel>
  );
}

function SceneVisuals({
  scene,
  projectId,
}: {
  scene: ScriptScene;
  projectId: string;
}) {
  const genVisuals = useGenerateSceneVisuals(projectId);
  const searchAssets = useSearchSceneAssets(projectId);
  const [assetQuery, setAssetQuery] = React.useState("");

  const recs: VisualRecommendation[] = [...(scene.visual_recommendations || [])].sort(
    (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]
  );
  const assets = scene.visual_assets || [];
  const hasRecs = recs.length > 0;
  const hasAssets = assets.length > 0;

  const isGenActive =
    genVisuals.isPending && genVisuals.variables?.sceneId === scene.id;
  const isSearchActive =
    searchAssets.isPending && searchAssets.variables?.sceneId === scene.id;

  return (
    <Card className="relative p-4 pl-5">
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
      </div>

      {scene.narration && (
        <p className="mb-4 line-clamp-2 text-xs italic leading-relaxed text-muted">
          {scene.narration}
        </p>
      )}

      {/* --- AI Recommendations --------------------------------------- */}
      <div className="mb-4">
        <div className="mb-2 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Wand2 className="h-3.5 w-3.5 text-accent" />
            <h4 className="label text-[11px] text-text">
              Visual recommendations
            </h4>
          </div>
          <Button
            variant="generate"
            size="sm"
            loading={isGenActive}
            onClick={() => genVisuals.mutate({ sceneId: scene.id })}
          >
            <Sparkles className="h-3.5 w-3.5" />
            {hasRecs ? "Regenerate" : "Generate"}
          </Button>
        </div>

        {isGenActive && !hasRecs && (
          <GeneratingState
            message="Generating visual recommendations…"
            columns={2}
            rows={1}
          />
        )}

        {!isGenActive && !hasRecs && (
          <p className="rounded border border-dashed border-border px-3 py-4 text-center text-[11px] text-muted">
            No recommendations yet. Generate ideas for what to show in this scene.
          </p>
        )}

        {hasRecs && (
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {recs.map((rec) => (
              <div
                key={rec.id}
                className="rounded border-l-2 border-l-accent border-y border-r border-accent-muted/40 bg-accent-soft/20 p-3"
              >
                <div className="mb-1.5 flex flex-wrap items-center gap-1.5">
                  <Badge tone="accent">{rec.type.replace(/_/g, " ")}</Badge>
                  <Badge tone={priorityTone[rec.priority]}>
                    {rec.priority} priority
                  </Badge>
                  <span className="label ml-auto text-[8px] text-accent/70">
                    recommendation · not an image
                  </span>
                </div>
                <div className="label mb-0.5 text-[8px] text-muted">
                  Search query
                </div>
                <code className="mb-1.5 block break-words rounded-sm bg-bg/60 px-1.5 py-1 font-mono text-[11px] tabular-nums text-subtle">
                  {rec.query}
                </code>
                <p className="text-[11px] leading-relaxed text-text">
                  {rec.description}
                </p>
                {rec.reason && (
                  <p className="mt-1 text-[11px] leading-relaxed text-muted">
                    {rec.reason}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
        <InlineError error={isGenActive ? null : genVisuals.error} />
      </div>

      {/* --- Discovered assets ---------------------------------------- */}
      <div className="border-t border-border pt-3">
        <div className="mb-2 flex items-center justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <Camera className="h-3.5 w-3.5 text-info" />
            <h4 className="label text-[11px] text-text">
              Discovered assets
            </h4>
          </div>
        </div>
        <form
          className="mb-3 flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            searchAssets.mutate({
              sceneId: scene.id,
              query: assetQuery.trim() || undefined,
            });
          }}
        >
          <Input
            value={assetQuery}
            onChange={(e) => setAssetQuery(e.target.value)}
            placeholder="Search assets (defaults to scene context)…"
            className="flex-1"
          />
          <Button type="submit" variant="secondary" loading={isSearchActive}>
            <Search className="h-3.5 w-3.5" />
            Search assets
          </Button>
        </form>

        {isSearchActive && !hasAssets && (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div
                key={i}
                className="skeleton aspect-video rounded"
              />
            ))}
          </div>
        )}

        {!isSearchActive && !hasAssets && (
          <p className="rounded border border-dashed border-border px-3 py-4 text-center text-[11px] text-muted">
            No assets discovered yet. Search to find real, licensable media.
          </p>
        )}

        {hasAssets && (
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
            {assets.map((asset) => (
              <div
                key={asset.id}
                className="group overflow-hidden rounded border border-border bg-bg"
              >
                <div className="relative aspect-video overflow-hidden bg-elevated">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={asset.thumbnail_url || asset.url}
                    alt={asset.title || "Discovered asset"}
                    className="h-full w-full object-cover"
                    loading="lazy"
                  />
                  {asset.source_url && (
                    <a
                      href={asset.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="absolute right-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded bg-black/70 text-white opacity-0 transition-opacity group-hover:opacity-100"
                      aria-label="Open source"
                    >
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </div>
                <div className="p-2">
                  {asset.title && (
                    <div className="mb-1 line-clamp-1 text-[11px] text-text">
                      {asset.title}
                    </div>
                  )}
                  <div className="flex flex-wrap items-center gap-1">
                    <Badge tone="info">{asset.provider}</Badge>
                    {asset.license && (
                      <span className="font-mono text-[10px] tabular-nums text-muted">
                        {asset.license}
                      </span>
                    )}
                  </div>
                  {asset.creator && (
                    <div className="mt-0.5 text-[10px] text-muted">
                      by {asset.creator}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
        <InlineError error={isSearchActive ? null : searchAssets.error} />
      </div>
    </Card>
  );
}
