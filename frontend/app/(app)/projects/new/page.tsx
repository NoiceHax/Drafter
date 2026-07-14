"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Input,
  Textarea,
  Select,
  Label,
} from "@/components/ui/input";
import { ChipInput } from "@/components/chip-input";
import { InlineError } from "@/components/ui/error-state";
import { useCreateProject } from "@/hooks/useProjects";
import {
  PLATFORM_OPTIONS,
  TONE_OPTIONS,
  DURATION_OPTIONS,
} from "@/lib/constants";
import type { Platform, Tone } from "@/types";

export default function NewProjectPage() {
  const router = useRouter();
  const create = useCreateProject();

  const [title, setTitle] = React.useState("");
  const [idea, setIdea] = React.useState("");
  const [keywords, setKeywords] = React.useState<string[]>([]);
  const [platform, setPlatform] = React.useState<Platform>("generic");
  const [tone, setTone] = React.useState<Tone>("conversational");
  const [customTone, setCustomTone] = React.useState("");
  const [duration, setDuration] = React.useState(60);
  const [useCustomDuration, setUseCustomDuration] = React.useState(false);
  const [customDuration, setCustomDuration] = React.useState(120);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!idea.trim()) return;
    const target = useCustomDuration ? customDuration : duration;
    try {
      const project = await create.mutateAsync({
        title: title.trim() || undefined,
        idea: idea.trim(),
        initial_keywords: keywords.length ? keywords : undefined,
        platform,
        target_duration_seconds: target,
        tone,
        custom_tone: tone === "custom" ? customTone.trim() || undefined : undefined,
      });
      router.push(`/projects/${project.id}`);
    } catch {
      // error surfaced inline below
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-6 sm:px-8">
      <Link
        href="/projects"
        className="mb-4 inline-flex items-center gap-1.5 text-xs text-muted hover:text-text"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to projects
      </Link>

      <PageHeader
        title="New project"
        description="Describe your idea. The copilot will take it from keywords to a full script."
      />

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <div>
          <Label htmlFor="title">Title (optional)</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Why the Roman Empire really fell"
          />
        </div>

        <div>
          <Label htmlFor="idea">Idea *</Label>
          <Textarea
            id="idea"
            required
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            rows={4}
            placeholder="Describe the rough idea, story, or topic you want to make a video about…"
          />
          <p className="mt-1 text-[11px] text-muted">
            The more context you give, the sharper the recommendations.
          </p>
        </div>

        <div>
          <Label>Initial keywords (optional)</Label>
          <ChipInput
            value={keywords}
            onChange={setKeywords}
            placeholder="Add a keyword and press Enter…"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="platform">Platform</Label>
            <Select
              id="platform"
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
            <Label htmlFor="tone">Tone</Label>
            <Select
              id="tone"
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
        </div>

        {tone === "custom" && (
          <div>
            <Label htmlFor="customTone">Custom tone</Label>
            <Input
              id="customTone"
              value={customTone}
              onChange={(e) => setCustomTone(e.target.value)}
              placeholder="Describe the tone in your own words…"
            />
          </div>
        )}

        <div>
          <Label>Target duration</Label>
          {!useCustomDuration ? (
            <div className="flex items-center gap-2">
              <Select
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="flex-1"
              >
                {DURATION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </Select>
              <Button
                type="button"
                variant="outline"
                onClick={() => setUseCustomDuration(true)}
              >
                Custom
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Input
                type="number"
                min={5}
                max={3600}
                value={customDuration}
                onChange={(e) => setCustomDuration(Number(e.target.value))}
                className="flex-1"
              />
              <span className="text-xs text-muted">seconds</span>
              <Button
                type="button"
                variant="outline"
                onClick={() => setUseCustomDuration(false)}
              >
                Presets
              </Button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 border-t border-border pt-5">
          <Button
            type="submit"
            variant="primary"
            loading={create.isPending}
            disabled={!idea.trim()}
          >
            {!create.isPending && <Sparkles className="h-4 w-4" />}
            Create project
          </Button>
          <Link href="/projects">
            <Button type="button" variant="ghost">
              Cancel
            </Button>
          </Link>
        </div>
        <InlineError error={create.error} />
      </form>
    </div>
  );
}
