"use client";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CreateProjectBody, Project } from "@/types";

export const qk = {
  projects: ["projects"] as const,
  project: (id: string) => ["project", id] as const,
};

export function useProjects() {
  return useQuery({
    queryKey: qk.projects,
    queryFn: api.listProjects,
  });
}

export function useProject(id: string) {
  return useQuery({
    queryKey: qk.project(id),
    queryFn: () => api.getProject(id),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateProjectBody) => api.createProject(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projects });
    },
  });
}

export function useUpdateProject(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Partial<CreateProjectBody> & Record<string, unknown>) =>
      api.updateProject(id, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.project(id) });
      qc.invalidateQueries({ queryKey: qk.projects });
    },
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.deleteProject(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: qk.projects });
    },
  });
}
