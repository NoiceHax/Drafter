"use client";

import * as React from "react";
import { Plus, Check, Sparkles, Trash2, Tag } from "lucide-react";
import { Panel } from "../panel";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScoreBar } from "@/components/ui/score-bar";
import { EmptyState } from "@/components/ui/empty-state";
import { GeneratingState } from "@/components/ui/skeleton";
import { InlineError } from "@/components/ui/error-state";
import { InstructionInput } from "@/components/ui/instruction-input";
import { cn } from "@/lib/utils";
import {
  KEYWORD_CATEGORIES,
  KEYWORD_CATEGORY_LABELS,
} from "@/lib/constants";
import {
  useRecommendKeywords,
  useSelectKeyword,
  useAddKeyword,
  useDeleteKeyword,
} from "@/hooks/useWorkspace";
import type { KeywordCategory, ProjectDetail } from "@/types";

export function KeywordsPanel({ project }: { project: ProjectDetail }) {
  const recommend = useRecommendKeywords(project.id);
  const selectKw = useSelectKeyword(project.id);
  const addKw = useAddKeyword(project.id);
  const deleteKw = useDeleteKeyword(project.id);

  const [custom, setCustom] = React.useState("");

  const recs = project.recommendations || [];
  const selectedKeywords = (project.keywords || []).filter((k) => k.selected);
  const selectedSet = new Set(
    selectedKeywords.map((k) => k.text.toLowerCase())
  );

  const toggle = (keyword: string, category?: KeywordCategory) => {
    const isSelected = selectedSet.has(keyword.toLowerCase());
    selectKw.mutate({ keyword, category, selected: !isSelected });
  };

  const grouped = KEYWORD_CATEGORIES.reduce(
    (acc, cat) => {
      acc[cat] = recs.filter((r) => r.category === cat);
      return acc;
    },
    {} as Record<KeywordCategory, typeof recs>
  );

  const hasRecs = recs.length > 0;

  return (
    <Panel
      step="02"
      eyebrow="Research the terrain"
      title="Keywords"
      description="Recommendations sorted into semantic relevance, story value, and discovery reach. Keep the ones worth chasing."
      guideKey="keywords"
      guide={[
        "Click Generate recommendations to expand your idea into related keywords across three lenses: Semantic (closely related), Story (narrative angles), and Discovery (adjacent ideas).",
        "Select the keywords that fit your intended direction; they steer the angles, hooks, and research that follow.",
        "Add your own keyword in the input if the copilot missed something, or remove any you don't want.",
        "Use the refine box at the bottom to regenerate with guidance, e.g. 'more technical terms'.",
      ]}
    >
      {/* Selected + custom keyword tray */}
      <Card className="mb-4 p-4">
        <div className="mb-2 flex items-center justify-between">
          <span className="label text-[10px] text-subtle">
            Selected keywords ({selectedKeywords.length})
          </span>
        </div>
        <div className="mb-3 flex flex-wrap gap-1.5">
          {selectedKeywords.length === 0 && (
            <span className="text-xs text-muted">
              None yet. Pull from the recommendations below or add your own.
            </span>
          )}
          {selectedKeywords.map((k) => (
            <span
              key={k.id}
              className="inline-flex items-center gap-1 rounded-sm border border-accent-muted bg-accent-soft px-2 py-0.5 text-xs text-accent"
            >
              {k.text}
              <button
                onClick={() => deleteKw.mutate(k.id)}
                className="text-accent/60 hover:text-accent"
                aria-label={`Remove ${k.text}`}
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
        <form
          className="flex items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (custom.trim()) {
              addKw.mutate(custom.trim());
              setCustom("");
            }
          }}
        >
          <Input
            value={custom}
            onChange={(e) => setCustom(e.target.value)}
            placeholder="Add a custom keyword…"
            className="flex-1"
          />
          <Button type="submit" variant="secondary" loading={addKw.isPending}>
            <Plus className="h-3.5 w-3.5" />
            Add
          </Button>
        </form>
        <InlineError error={addKw.error || deleteKw.error} />
      </Card>

      {recommend.isPending && !hasRecs && (
        <GeneratingState
          message="Generating keyword recommendations…"
          columns={3}
          rows={2}
        />
      )}

      {!recommend.isPending && !hasRecs && (
        <EmptyState
          icon={Tag}
          title="No keyword recommendations yet"
          description="Generate semantic, story, and discovery keywords tailored to your idea."
          action={
            <div className="w-full max-w-md">
              <Button
                variant="generate"
                loading={recommend.isPending}
                onClick={() => recommend.mutate({})}
              >
                <Sparkles className="h-4 w-4" />
                Generate recommendations
              </Button>
            </div>
          }
        />
      )}

      {hasRecs && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {KEYWORD_CATEGORIES.map((cat) => (
              <div key={cat}>
                <div className="mb-2 flex items-center gap-2">
                  <h3 className="label text-[11px] text-subtle">
                    {KEYWORD_CATEGORY_LABELS[cat]}
                  </h3>
                  <span className="font-mono text-[10px] tabular-nums text-muted">
                    {grouped[cat].length}
                  </span>
                  <div className="h-px flex-1 bg-border" />
                </div>
                <div className="space-y-2">
                  {grouped[cat].length === 0 && (
                    <p className="rounded border border-dashed border-border px-3 py-4 text-center text-[11px] text-muted">
                      No {KEYWORD_CATEGORY_LABELS[cat].toLowerCase()} keywords.
                    </p>
                  )}
                  {grouped[cat].map((rec) => {
                    const isSelected = selectedSet.has(
                      rec.keyword.toLowerCase()
                    );
                    return (
                      <button
                        key={rec.id}
                        onClick={() => toggle(rec.keyword, rec.category)}
                        className={cn(
                          "w-full rounded border p-3 text-left transition-colors",
                          isSelected
                            ? "border-accent bg-accent-soft/40"
                            : "border-border bg-panel hover:border-borderStrong"
                        )}
                      >
                        <div className="mb-1 flex items-start justify-between gap-2">
                          <span className="text-sm font-medium text-text">
                            {rec.keyword}
                          </span>
                          <span
                            className={cn(
                              "flex h-4 w-4 shrink-0 items-center justify-center rounded-sm border",
                              isSelected
                                ? "border-accent bg-accent text-bg"
                                : "border-borderStrong text-transparent"
                            )}
                          >
                            <Check className="h-2.5 w-2.5" />
                          </span>
                        </div>
                        <p className="mb-2 text-[11px] leading-relaxed text-muted">
                          {rec.reason}
                        </p>
                        <ScoreBar value={rec.relevance_score} />
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 border-t border-border pt-4">
            <InstructionInput
              buttonLabel="Regenerate"
              placeholder="Refine, e.g. 'more beginner-friendly terms'…"
              loading={recommend.isPending}
              onSubmit={(instruction) =>
                recommend.mutate(instruction ? { instruction } : {})
              }
            />
            <InlineError error={recommend.error} />
          </div>
        </>
      )}
    </Panel>
  );
}
