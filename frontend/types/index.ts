// ---------------------------------------------------------------------------
// Enums / unions
// ---------------------------------------------------------------------------

export type Platform =
  | "instagram_reels"
  | "youtube_shorts"
  | "tiktok"
  | "youtube_long"
  | "generic";

export type Tone =
  | "educational"
  | "dramatic"
  | "conversational"
  | "documentary"
  | "humorous"
  | "investigative"
  | "custom";

export type ProjectStage =
  | "idea"
  | "keywords"
  | "angles"
  | "hooks"
  | "research"
  | "outline"
  | "script"
  | "visuals";

export type KeywordCategory = "semantic" | "story" | "discovery";

export type HookArchetype =
  | "mystery_curiosity"
  | "threat"
  | "cold_open"
  | "contrarian"
  | "problem"
  | "statistic"
  | "story_open"
  | "direct_question"
  | "comparison"
  | "pattern_interrupt";

export type VisualType =
  | "real_image"
  | "historical_photo"
  | "person"
  | "event"
  | "location"
  | "product"
  | "news_headline"
  | "map"
  | "chart"
  | "screenshot"
  | "b_roll"
  | "generated_image"
  | "text_animation";

export type VisualPriority = "high" | "medium" | "low";

export type KeywordStatus = "recommended" | "custom" | "selected";

// ---------------------------------------------------------------------------
// Entities
// ---------------------------------------------------------------------------

export interface KeywordRecommendation {
  id: string;
  keyword: string;
  category: KeywordCategory;
  reason: string;
  relevance_score: number;
  accepted?: boolean;
}

export interface Keyword {
  id: string;
  text: string;
  status: KeywordStatus | string;
  category?: KeywordCategory;
  selected: boolean;
}

export interface ContentAngle {
  id: string;
  title: string;
  summary: string;
  style: string;
  why_it_works: string;
  estimated_audience_interest: number;
  selected: boolean;
}

export interface HookAnalysis {
  archetype: HookArchetype;
  suitability_score: number;
  reason: string;
}

export interface Hook {
  id: string;
  text: string;
  archetype: HookArchetype;
  suitability_score: number;
  estimated_duration_seconds: number;
  unanswered_question?: string;
  story_payoff?: string;
  reason?: string;
  selected: boolean;
}

export interface ResearchSource {
  id: string;
  title: string;
  url: string;
  publisher?: string;
  published_at?: string;
  summary: string;
  key_facts?: string[];
  selected?: boolean;
}

export interface OutlineSection {
  type: string;
  purpose: string;
  summary: string;
  estimated_duration_seconds: number;
}

export interface StoryOutline {
  id: string;
  narrative_structure: string;
  estimated_duration_seconds: number;
  sections: OutlineSection[];
}

export interface VisualRecommendation {
  id: string;
  type: VisualType;
  query: string;
  description: string;
  reason?: string;
  priority: VisualPriority;
}

export interface VisualAsset {
  id: string;
  url: string;
  thumbnail_url?: string;
  source_url?: string;
  provider: string;
  title?: string;
  creator?: string;
  license?: string;
}

export interface ScriptScene {
  id: string;
  scene_number: number;
  start_time: number;
  end_time: number;
  section_type: string;
  narration: string;
  on_screen_text?: string;
  visual_direction?: string;
  visual_recommendations: VisualRecommendation[];
  visual_assets: VisualAsset[];
}

export interface Script {
  id: string;
  title: string;
  platform: Platform;
  target_duration_seconds: number;
  estimated_duration_seconds: number;
  hook_text: string;
  hook_duration_seconds: number;
  cta_text?: string;
  cta_duration_seconds: number;
  scenes: ScriptScene[];
}

export interface Project {
  id: string;
  title?: string;
  idea: string;
  platform: Platform;
  target_duration_seconds: number;
  tone: Tone;
  custom_tone?: string;
  current_stage: ProjectStage;
  selected_angle_id?: string;
  selected_hook_id?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends Project {
  keywords: Keyword[];
  recommendations: KeywordRecommendation[];
  angles: ContentAngle[];
  hooks: Hook[];
  hook_analysis?: HookAnalysis[];
  recommended_hook_id?: string;
  research_sources: ResearchSource[];
  research_enabled?: boolean;
  outline?: StoryOutline | null;
  script?: Script | null;
}

// ---------------------------------------------------------------------------
// Request payloads
// ---------------------------------------------------------------------------

export interface User {
  id: string;
  email: string;
  display_name?: string | null;
}

export interface EmailCheckResponse {
  mode: "alpha" | "password" | "signup";
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface UserKeysStatus {
  nvidia_api_key_set: boolean;
  nvidia_model?: string | null;
  tavily_api_key_set: boolean;
  pexels_api_key_set: boolean;
}

export interface UserKeysUpdate {
  nvidia_api_key: string;
  nvidia_model: string;
  tavily_api_key: string;
  pexels_api_key: string;
}

export interface IdeaDirection {
  title: string;
  idea: string;
}

export interface IdeaRefinement {
  refined_idea: string;
  interpretation: string;
  directions: IdeaDirection[];
  clarifying_questions: string[];
}

export interface CreateProjectBody {
  title?: string;
  idea: string;
  initial_keywords?: string[];
  platform: Platform;
  target_duration_seconds: number;
  tone: Tone;
  custom_tone?: string;
}

export interface HooksGenerateResponse {
  analysis: HookAnalysis[];
  hooks: Hook[];
  recommended_hook_id: string;
}

export interface ResearchResponse {
  research_enabled: boolean;
  sources: ResearchSource[];
}

// ---------------------------------------------------------------------------
// API error shape
// ---------------------------------------------------------------------------

export interface ApiErrorShape {
  error: { code: string; message: string };
}
