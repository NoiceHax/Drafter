"use client";

import * as React from "react";
import {
  useMutation,
  useQueryClient,
  type QueryClient,
} from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api";
import { qk } from "./useProjects";
import { useToast } from "@/components/ui/toast";
import type { ProjectDetail } from "@/types";

/**
 * All stage-mutation hooks for the project workspace. Each invalidates the
 * project detail query so panels re-render with fresh server state.
 */

function useInvalidateProject(projectId: string) {
  const qc = useQueryClient();
  return () => qc.invalidateQueries({ queryKey: qk.project(projectId) });
}

type Ctx = { previous?: ProjectDetail };

/**
 * Shared optimistic-update machinery for fast selection/edit mutations.
 * `apply` mutates a draft copy of the cached project detail so the UI reflects
 * the change instantly; on error we roll back to the snapshot and toast; on
 * settle we invalidate to reconcile with the server.
 */
function useOptimisticProject(projectId: string) {
  const qc = useQueryClient();
  const { toast } = useToast();

  return function optimistic<V>(
    apply: (draft: ProjectDetail, vars: V) => void,
    failMessage: string
  ) {
    return {
      onMutate: async (vars: V): Promise<Ctx> => {
        await qc.cancelQueries({ queryKey: qk.project(projectId) });
        const previous = qc.getQueryData<ProjectDetail>(qk.project(projectId));
        if (previous) {
          const draft: ProjectDetail = structuredClone(previous);
          apply(draft, vars);
          qc.setQueryData(qk.project(projectId), draft);
        }
        return { previous };
      },
      onError: (err: unknown, _vars: V, ctx?: Ctx) => {
        if (ctx?.previous) {
          qc.setQueryData(qk.project(projectId), ctx.previous);
        }
        const msg = err instanceof ApiError ? err.message : failMessage;
        toast(`${failMessage}: ${msg}`, "error");
      },
      onSettled: () => {
        qc.invalidateQueries({ queryKey: qk.project(projectId) });
      },
    };
  };
}

// ---- Idea refinement ------------------------------------------------------

export function useRefineIdea(projectId: string) {
  // Returns a proposed refinement; does not mutate the project until accepted.
  return useMutation({
    mutationFn: (body: {
      rough_idea?: string;
      instruction?: string;
      answers?: string;
    }) => api.refineIdea(projectId, body),
  });
}

// ---- Keywords -------------------------------------------------------------

export function useRecommendKeywords(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (body: { instruction?: string; category?: string }) =>
      api.recommendKeywords(projectId, body),
    onSuccess: invalidate,
  });
}

export function useSelectKeyword(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  type V = { keyword: string; category?: string; selected: boolean };
  return useMutation({
    mutationFn: (body: V) => api.selectKeyword(projectId, body),
    ...optimistic<V>((draft, vars) => {
      const kw = draft.keywords?.find(
        (k) => k.text.toLowerCase() === vars.keyword.toLowerCase()
      );
      if (kw) {
        kw.selected = vars.selected;
        kw.status = vars.selected ? "selected" : "rejected";
      } else if (vars.selected) {
        draft.keywords = [
          ...(draft.keywords || []),
          {
            id: `optimistic-${vars.keyword}`,
            text: vars.keyword,
            status: "selected",
            category: vars.category as never,
            selected: true,
          },
        ];
      }
    }, "Couldn't update keyword"),
  });
}

export function useAddKeyword(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  return useMutation({
    mutationFn: (text: string) => api.addKeyword(projectId, { text }),
    ...optimistic<string>((draft, text) => {
      const exists = draft.keywords?.some(
        (k) => k.text.toLowerCase() === text.toLowerCase()
      );
      if (!exists) {
        draft.keywords = [
          ...(draft.keywords || []),
          {
            id: `optimistic-${text}`,
            text,
            status: "custom",
            selected: true,
          },
        ];
      }
    }, "Couldn't add keyword"),
  });
}

export function useDeleteKeyword(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  return useMutation({
    mutationFn: (keywordId: string) => api.deleteKeyword(projectId, keywordId),
    ...optimistic<string>((draft, keywordId) => {
      draft.keywords = (draft.keywords || []).filter((k) => k.id !== keywordId);
    }, "Couldn't remove keyword"),
  });
}

// ---- Angles ---------------------------------------------------------------

export function useGenerateAngles(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (body: { instruction?: string }) =>
      api.generateAngles(projectId, body),
    onSuccess: invalidate,
  });
}

export function useSelectAngle(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  return useMutation({
    mutationFn: (angleId: string) => api.selectAngle(projectId, angleId),
    ...optimistic<string>((draft, angleId) => {
      draft.selected_angle_id = angleId;
      for (const a of draft.angles || []) a.selected = a.id === angleId;
    }, "Couldn't select angle"),
  });
}

// ---- Hooks ----------------------------------------------------------------

export function useGenerateHooks(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  const [phase, setPhase] = React.useState<string | null>(null);
  const m = useMutation({
    mutationFn: (body: { instruction?: string }) =>
      api.streamHooks(projectId, body, {
        onPhase: (p) => setPhase(p.label),
      }),
    onSuccess: invalidate,
    onSettled: () => setPhase(null),
  });
  return Object.assign(m, { phase });
}

export function useSelectHook(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  return useMutation({
    mutationFn: (hookId: string) => api.selectHook(projectId, hookId),
    ...optimistic<string>((draft, hookId) => {
      draft.selected_hook_id = hookId;
      for (const h of draft.hooks || []) h.selected = h.id === hookId;
    }, "Couldn't select hook"),
  });
}

export function useRegenerateHook(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (args: {
      hookId: string;
      instruction?: string;
      archetype?: string;
    }) =>
      api.regenerateHook(projectId, args.hookId, {
        instruction: args.instruction,
        archetype: args.archetype,
      }),
    onSuccess: invalidate,
  });
}

// ---- Research -------------------------------------------------------------

export function useRunResearch(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (body: { instruction?: string }) =>
      api.runResearch(projectId, body),
    onSuccess: invalidate,
  });
}

export function useSelectResearchSource(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  type V = { sourceId: string; selected: boolean };
  return useMutation({
    mutationFn: (v: V) =>
      api.selectResearchSource(projectId, v.sourceId, v.selected),
    ...optimistic<V>((draft, v) => {
      const s = draft.research_sources?.find((x) => x.id === v.sourceId);
      if (s) s.selected = v.selected;
    }, "Couldn't update the source"),
  });
}

// ---- Outline --------------------------------------------------------------

export function useGenerateOutline(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  const [phase, setPhase] = React.useState<string | null>(null);
  const m = useMutation({
    mutationFn: (body: { instruction?: string }) =>
      api.streamOutline(projectId, body, { onPhase: (p) => setPhase(p.label) }),
    onSuccess: invalidate,
    onSettled: () => setPhase(null),
  });
  return Object.assign(m, { phase });
}

// ---- Script ---------------------------------------------------------------

export function useGenerateScript(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  const [phase, setPhase] = React.useState<string | null>(null);
  const m = useMutation({
    mutationFn: (body: { instruction?: string }) =>
      api.streamScript(projectId, body, { onPhase: (p) => setPhase(p.label) }),
    onSuccess: invalidate,
    onSettled: () => setPhase(null),
  });
  return Object.assign(m, { phase });
}

// ---- Scenes ---------------------------------------------------------------

export function useRegenerateScene(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (args: {
      sceneId: string;
      instruction?: string;
      field?: "narration" | "visual_direction" | "all";
    }) =>
      api.regenerateScene(args.sceneId, {
        instruction: args.instruction,
        field: args.field,
      }),
    onSuccess: invalidate,
  });
}

export function useUpdateScene(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  type V = {
    sceneId: string;
    narration?: string;
    on_screen_text?: string;
    visual_direction?: string;
  };
  return useMutation({
    mutationFn: (args: V) =>
      api.updateScene(args.sceneId, {
        narration: args.narration,
        on_screen_text: args.on_screen_text,
        visual_direction: args.visual_direction,
      }),
    ...optimistic<V>((draft, vars) => {
      const scene = draft.script?.scenes?.find((s) => s.id === vars.sceneId);
      if (scene) {
        if (vars.narration !== undefined) scene.narration = vars.narration;
        if (vars.on_screen_text !== undefined)
          scene.on_screen_text = vars.on_screen_text;
        if (vars.visual_direction !== undefined)
          scene.visual_direction = vars.visual_direction;
      }
    }, "Couldn't save scene edit"),
  });
}

export function useEditScript(projectId: string) {
  const optimistic = useOptimisticProject(projectId);
  type V = { scriptId: string; hook_text?: string; cta_text?: string; title?: string };
  return useMutation({
    mutationFn: (args: V) =>
      api.editScript(args.scriptId, {
        title: args.title,
        hook_text: args.hook_text,
        cta_text: args.cta_text,
      }),
    ...optimistic<V>((draft, vars) => {
      if (!draft.script) return;
      if (vars.title !== undefined) draft.script.title = vars.title;
      if (vars.hook_text !== undefined) draft.script.hook_text = vars.hook_text;
      if (vars.cta_text !== undefined) draft.script.cta_text = vars.cta_text;
    }, "Couldn't save script edit"),
  });
}

export function useGenerateSceneVisuals(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (args: { sceneId: string; instruction?: string }) =>
      api.generateSceneVisuals(args.sceneId, {
        instruction: args.instruction,
      }),
    onSuccess: invalidate,
  });
}

export function useSearchSceneAssets(projectId: string) {
  const invalidate = useInvalidateProject(projectId);
  return useMutation({
    mutationFn: (args: { sceneId: string; query?: string }) =>
      api.searchSceneAssets(args.sceneId, { query: args.query }),
    onSuccess: invalidate,
  });
}
