import type {
  Project,
  ProjectDetail,
  CreateProjectBody,
  IdeaRefinement,
  KeywordRecommendation,
  Keyword,
  ContentAngle,
  Hook,
  HooksGenerateResponse,
  ResearchResponse,
  ResearchSource,
  StoryOutline,
  Script,
  ScriptScene,
  VisualRecommendation,
  VisualAsset,
  ApiErrorShape,
  User,
  EmailCheckResponse,
  AuthResponse,
  UserKeysStatus,
  UserKeysUpdate,
} from "@/types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const TOKEN_KEY = "drafter.token";

// ── auth token store ────────────────────────────────────────────────────
let authToken: string | null =
  typeof window !== "undefined" ? window.localStorage.getItem(TOKEN_KEY) : null;
let onUnauthorized: (() => void) | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
  if (typeof window !== "undefined") {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  }
}

export function getAuthToken() {
  return authToken;
}

/** Register a callback fired when the server rejects the token (401). */
export function setUnauthorizedHandler(fn: (() => void) | null) {
  onUnauthorized = fn;
}

export class ApiError extends Error {
  code: string;
  status: number;
  constructor(message: string, code: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

function authHeaders(): Record<string, string> {
  return authToken ? { Authorization: `Bearer ${authToken}` } : {};
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
        ...(options.headers || {}),
      },
    });
  } catch (e) {
    throw new ApiError(
      "Could not reach the server. Is the backend running?",
      "network_error",
      0
    );
  }

  // Handle empty bodies (e.g. 204 for DELETE).
  const text = await res.text();
  let data: unknown = undefined;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = undefined;
    }
  }

  if (!res.ok) {
    if (res.status === 401) {
      setAuthToken(null);
      onUnauthorized?.();
    }
    const shape = data as ApiErrorShape | undefined;
    const message =
      shape?.error?.message ||
      `Request failed with status ${res.status}`;
    const code = shape?.error?.code || "unknown_error";
    throw new ApiError(message, code, res.status);
  }

  return data as T;
}

const jsonBody = (body: unknown): RequestInit => ({
  body: JSON.stringify(body ?? {}),
});

// ---------------------------------------------------------------------------
// SSE streaming (progress events for the heavier generation stages)
// ---------------------------------------------------------------------------

export interface StreamPhase {
  phase: string;
  label: string;
}

/**
 * POST to an SSE endpoint and stream progress. Calls `onPhase` for each phase
 * event and `onHeartbeat` with elapsed ms; resolves with the `done` payload or
 * rejects with an ApiError on an `error` event / network failure.
 */
export async function streamStage<T>(
  path: string,
  body: unknown,
  handlers: {
    onPhase?: (p: StreamPhase) => void;
    onHeartbeat?: (elapsedMs: number) => void;
    signal?: AbortSignal;
  } = {}
): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
        ...authHeaders(),
      },
      body: JSON.stringify(body ?? {}),
      signal: handlers.signal,
    });
  } catch {
    throw new ApiError(
      "Could not reach the server. Is the backend running?",
      "network_error",
      0
    );
  }

  if (!res.ok || !res.body) {
    throw new ApiError(
      `Request failed with status ${res.status}`,
      "stream_error",
      res.status
    );
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let result: T | undefined;
  let done = false;

  const dispatch = (event: string, data: string) => {
    let parsed: unknown = undefined;
    try {
      parsed = JSON.parse(data);
    } catch {
      /* ignore malformed */
    }
    if (event === "phase") handlers.onPhase?.(parsed as StreamPhase);
    else if (event === "heartbeat")
      handlers.onHeartbeat?.((parsed as { elapsed_ms: number })?.elapsed_ms ?? 0);
    else if (event === "done") {
      result = parsed as T;
      done = true;
    } else if (event === "error") {
      const e = parsed as { code?: string; message?: string };
      throw new ApiError(e?.message || "Generation failed", e?.code || "error", 502);
    }
  };

  while (true) {
    const { value, done: streamDone } = await reader.read();
    if (streamDone) break;
    buffer += decoder.decode(value, { stream: true });

    // Parse complete SSE records (separated by a blank line).
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const record = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      let event = "message";
      const dataLines: string[] = [];
      for (const line of record.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
      }
      if (dataLines.length) dispatch(event, dataLines.join("\n"));
    }
    if (done) break;
  }

  if (!done || result === undefined) {
    throw new ApiError("The generation stream ended unexpectedly.", "stream_incomplete", 0);
  }
  return result;
}

// ---------------------------------------------------------------------------
// API surface
// ---------------------------------------------------------------------------

export const api = {
  // Auth
  checkEmail: (email: string) =>
    request<EmailCheckResponse>("/auth/check-email", {
      method: "POST",
      ...jsonBody({ email }),
    }),

  login: (body: { email: string; password?: string }) =>
    request<AuthResponse>("/auth/login", { method: "POST", ...jsonBody(body) }),

  me: () => request<User>("/auth/me"),

  // Projects
  listProjects: () => request<Project[]>("/projects"),

  getProject: (id: string) => request<ProjectDetail>(`/projects/${id}`),

  createProject: (body: CreateProjectBody) =>
    request<Project>("/projects", { method: "POST", ...jsonBody(body) }),

  updateProject: (id: string, body: Partial<CreateProjectBody> & Record<string, unknown>) =>
    request<Project>(`/projects/${id}`, { method: "PATCH", ...jsonBody(body) }),

  deleteProject: (id: string) =>
    request<void>(`/projects/${id}`, { method: "DELETE" }),

  // Idea refinement
  refineIdea: (
    id: string,
    body: { rough_idea?: string; instruction?: string; answers?: string }
  ) =>
    request<IdeaRefinement>(`/projects/${id}/idea/refine`, {
      method: "POST",
      ...jsonBody(body),
    }),

  // Keywords
  recommendKeywords: (
    id: string,
    body: { instruction?: string; category?: string }
  ) =>
    request<KeywordRecommendation[]>(`/projects/${id}/keywords/recommend`, {
      method: "POST",
      ...jsonBody(body),
    }),

  selectKeyword: (
    id: string,
    body: { keyword: string; category?: string; selected: boolean }
  ) =>
    request<Keyword>(`/projects/${id}/keywords/select`, {
      method: "POST",
      ...jsonBody(body),
    }),

  addKeyword: (id: string, body: { text: string }) =>
    request<Keyword>(`/projects/${id}/keywords`, {
      method: "POST",
      ...jsonBody(body),
    }),

  deleteKeyword: (id: string, keywordId: string) =>
    request<void>(`/projects/${id}/keywords/${keywordId}`, {
      method: "DELETE",
    }),

  // Angles
  generateAngles: (id: string, body: { instruction?: string }) =>
    request<ContentAngle[]>(`/projects/${id}/angles/generate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  selectAngle: (id: string, angleId: string) =>
    request<ContentAngle>(`/projects/${id}/angles/${angleId}/select`, {
      method: "POST",
      ...jsonBody({}),
    }),

  // Hooks
  generateHooks: (id: string, body: { instruction?: string }) =>
    request<HooksGenerateResponse>(`/projects/${id}/hooks/generate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  selectHook: (id: string, hookId: string) =>
    request<Hook>(`/projects/${id}/hooks/${hookId}/select`, {
      method: "POST",
      ...jsonBody({}),
    }),

  regenerateHook: (
    id: string,
    hookId: string,
    body: { instruction?: string; archetype?: string }
  ) =>
    request<Hook>(`/projects/${id}/hooks/${hookId}/regenerate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  // Research
  runResearch: (id: string, body: { instruction?: string }) =>
    request<ResearchResponse>(`/projects/${id}/research`, {
      method: "POST",
      ...jsonBody(body),
    }),

  selectResearchSource: (id: string, sourceId: string, selected: boolean) =>
    request<ResearchSource>(`/projects/${id}/research/${sourceId}/select`, {
      method: "POST",
      ...jsonBody({ selected }),
    }),

  // User API keys
  getKeys: () => request<UserKeysStatus>("/auth/keys"),
  updateKeys: (body: Partial<UserKeysUpdate>) =>
    request<UserKeysStatus>("/auth/keys", { method: "PATCH", ...jsonBody(body) }),

  // Outline
  generateOutline: (id: string, body: { instruction?: string }) =>
    request<StoryOutline>(`/projects/${id}/outline/generate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  // Script
  generateScript: (id: string, body: { instruction?: string }) =>
    request<Script>(`/projects/${id}/script/generate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  // Script-level edits (hook / CTA / title)
  editScript: (
    scriptId: string,
    body: { title?: string; hook_text?: string; cta_text?: string }
  ) =>
    request<Script>(`/scripts/${scriptId}`, {
      method: "PATCH",
      ...jsonBody(body),
    }),

  // Scenes
  regenerateScene: (
    sceneId: string,
    body: { instruction?: string; field?: "narration" | "visual_direction" | "all" }
  ) =>
    request<ScriptScene>(`/scenes/${sceneId}/regenerate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  updateScene: (
    sceneId: string,
    body: {
      narration?: string;
      on_screen_text?: string;
      visual_direction?: string;
    }
  ) =>
    request<ScriptScene>(`/scenes/${sceneId}`, {
      method: "PATCH",
      ...jsonBody(body),
    }),

  // Streaming variants (SSE progress) for the heavier stages.
  streamHooks: (
    id: string,
    body: { instruction?: string },
    handlers?: Parameters<typeof streamStage>[2]
  ) => streamStage<HooksGenerateResponse>(`/projects/${id}/hooks/generate/stream`, body, handlers),

  streamOutline: (
    id: string,
    body: { instruction?: string },
    handlers?: Parameters<typeof streamStage>[2]
  ) => streamStage<StoryOutline>(`/projects/${id}/outline/generate/stream`, body, handlers),

  streamScript: (
    id: string,
    body: { instruction?: string },
    handlers?: Parameters<typeof streamStage>[2]
  ) => streamStage<Script>(`/projects/${id}/script/generate/stream`, body, handlers),

  generateSceneVisuals: (sceneId: string, body: { instruction?: string }) =>
    request<VisualRecommendation[]>(`/scenes/${sceneId}/visuals/generate`, {
      method: "POST",
      ...jsonBody(body),
    }),

  searchSceneAssets: (sceneId: string, body: { query?: string }) =>
    request<VisualAsset[]>(`/scenes/${sceneId}/assets/search`, {
      method: "POST",
      ...jsonBody(body),
    }),
};
