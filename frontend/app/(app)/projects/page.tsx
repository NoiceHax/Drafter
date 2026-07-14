"use client";

import Link from "next/link";
import * as React from "react";
import { Plus, FolderPlus, Search } from "lucide-react";
import { useProjects } from "@/hooks/useProjects";
import { PageHeader } from "@/components/page-header";
import { ProjectCard } from "@/components/project-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProjectsPage() {
  const { data: projects, isLoading, isError, error, refetch } = useProjects();
  const [q, setQ] = React.useState("");

  const filtered = React.useMemo(() => {
    if (!projects) return [];
    const term = q.trim().toLowerCase();
    const sorted = [...projects].sort(
      (a, b) =>
        new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    );
    if (!term) return sorted;
    return sorted.filter(
      (p) =>
        (p.title || "").toLowerCase().includes(term) ||
        p.idea.toLowerCase().includes(term)
    );
  }, [projects, q]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-8">
      <PageHeader
        eyebrow="Your desk"
        title="Projects"
        description="Every draft on the bench."
        actions={
          <Link href="/projects/new">
            <Button variant="primary">
              <Plus className="h-4 w-4" />
              New project
            </Button>
          </Link>
        }
      />

      {projects && projects.length > 0 && (
        <div className="mt-5 flex items-center gap-2">
          <div className="relative w-full sm:w-72">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search projects…"
              className="pl-8"
            />
          </div>
          <span className="label text-[10px] text-muted">
            {filtered.length} / {projects.length}
          </span>
        </div>
      )}

      <section className="mt-5">
        {isLoading && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="rounded border border-border bg-panel p-4"
              >
                <Skeleton className="mb-2 h-4 w-2/3" />
                <Skeleton className="mb-1 h-3 w-full" />
                <Skeleton className="h-3 w-4/5" />
              </div>
            ))}
          </div>
        )}

        {isError && <ErrorState error={error} onRetry={() => refetch()} />}

        {!isLoading && !isError && filtered.length === 0 && (
          <EmptyState
            icon={FolderPlus}
            title={q ? "Nothing matches that" : "An empty desk"}
            description={
              q
                ? "No draft matches your search. Try another term."
                : "Start a project and it takes its place on the bench."
            }
            action={
              !q && (
                <Link href="/projects/new">
                  <Button variant="primary">
                    <Plus className="h-4 w-4" />
                    New project
                  </Button>
                </Link>
              )
            }
          />
        )}

        {!isLoading && !isError && filtered.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
