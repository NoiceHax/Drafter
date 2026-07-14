import type {
  Platform,
  Tone,
  ProjectStage,
  KeywordCategory,
  HookArchetype,
  VisualPriority,
} from "@/types";

export const PLATFORM_LABELS: Record<Platform, string> = {
  instagram_reels: "Instagram Reels",
  youtube_shorts: "YouTube Shorts",
  tiktok: "TikTok",
  youtube_long: "YouTube (Long)",
  generic: "Generic",
};

export const PLATFORM_OPTIONS: { value: Platform; label: string }[] = (
  Object.keys(PLATFORM_LABELS) as Platform[]
).map((value) => ({ value, label: PLATFORM_LABELS[value] }));

export const TONE_LABELS: Record<Tone, string> = {
  educational: "Educational",
  dramatic: "Dramatic",
  conversational: "Conversational",
  documentary: "Documentary",
  humorous: "Humorous",
  investigative: "Investigative",
  custom: "Custom",
};

export const TONE_OPTIONS: { value: Tone; label: string }[] = (
  Object.keys(TONE_LABELS) as Tone[]
).map((value) => ({ value, label: TONE_LABELS[value] }));

export const DURATION_OPTIONS: { value: number; label: string }[] = [
  { value: 15, label: "15s" },
  { value: 30, label: "30s" },
  { value: 60, label: "60s" },
  { value: 90, label: "90s" },
  { value: 180, label: "3 min" },
  { value: 300, label: "5 min" },
  { value: 600, label: "10 min" },
];

// Ordered stages for the progress indicator.
export const STAGE_ORDER: ProjectStage[] = [
  "idea",
  "keywords",
  "angles",
  "hooks",
  "research",
  "outline",
  "script",
  "visuals",
];

export const STAGE_LABELS: Record<ProjectStage, string> = {
  idea: "Idea",
  keywords: "Keywords",
  angles: "Angle",
  hooks: "Hook",
  research: "Research",
  outline: "Story",
  script: "Script",
  visuals: "Visuals",
};

export function stageIndex(stage: ProjectStage): number {
  const i = STAGE_ORDER.indexOf(stage);
  return i < 0 ? 0 : i;
}

export const KEYWORD_CATEGORY_LABELS: Record<KeywordCategory, string> = {
  semantic: "Semantic",
  story: "Story",
  discovery: "Discovery",
};

export const KEYWORD_CATEGORIES: KeywordCategory[] = [
  "semantic",
  "story",
  "discovery",
];

export const HOOK_ARCHETYPE_LABELS: Record<HookArchetype, string> = {
  mystery_curiosity: "Mystery / Curiosity",
  threat: "Threat",
  cold_open: "Cold Open",
  contrarian: "Contrarian",
  problem: "Problem",
  statistic: "Striking Statistic",
  story_open: "Story Open",
  direct_question: "Direct Question",
  comparison: "Comparison",
  pattern_interrupt: "Pattern Interrupt",
};

export const HOOK_ARCHETYPES: HookArchetype[] = [
  "mystery_curiosity",
  "threat",
  "cold_open",
  "contrarian",
  "problem",
  "statistic",
  "story_open",
  "direct_question",
  "comparison",
  "pattern_interrupt",
];

export const PRIORITY_ORDER: Record<VisualPriority, number> = {
  high: 0,
  medium: 1,
  low: 2,
};
