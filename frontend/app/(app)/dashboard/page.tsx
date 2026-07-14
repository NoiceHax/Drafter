"use client";

import Link from "next/link";
import { Plus, FolderPlus, Sparkles } from "lucide-react";
import { useProjects } from "@/hooks/useProjects";
import { PageHeader } from "@/components/page-header";
import { ProjectCard } from "@/components/project-card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ErrorState } from "@/components/ui/error-state";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { data: projects, isLoading, isError, error, refetch } = useProjects();

  const recent = projects
    ? [...projects]
        .sort(
          (a, b) =>
            new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )
        .slice(0, 6)
    : [];

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:px-8">
      <PageHeader
        eyebrow="The writing bench"
        title="Every script starts as a rough idea."
        description="Shape a few keywords into an angle, a hook, a researched story, and a marked-up scene-by-scene script, one beat at a time."
        actions={
          <Link href="/projects/new">
            <Button variant="primary">
              <Plus className="h-4 w-4" />
              New project
            </Button>
          </Link>
        }
      />

      <section className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="label text-xs text-subtle">Recent projects</h2>
          {projects && projects.length > 6 && (
            <Link
              href="/projects"
              className="text-xs text-accent hover:text-accent-hover"
            >
              View all ({projects.length})
            </Link>
          )}
        </div>

        {isLoading && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="rounded border border-border bg-panel p-4"
              >
                <Skeleton className="mb-2 h-4 w-2/3" />
                <Skeleton className="mb-1 h-3 w-full" />
                <Skeleton className="mb-3 h-3 w-4/5" />
                <Skeleton className="h-1 w-full" />
              </div>
            ))}
          </div>
        )}

        {isError && <ErrorState error={error} onRetry={() => refetch()} />}

        {!isLoading && !isError && recent.length === 0 && (
          <EmptyState
            icon={FolderPlus}
            title="A blank page, for now"
            description="Turn a rough idea into a full scene-by-scene script with visual directions. Start your first project and it lands here."
            action={
              <Link href="/projects/new">
                <Button variant="primary">
                  <Sparkles className="h-4 w-4" />
                  Create your first project
                </Button>
              </Link>
            }
          />
        )}

        {!isLoading && !isError && recent.length > 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {recent.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

