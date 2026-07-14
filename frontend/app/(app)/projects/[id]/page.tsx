"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useProject } from "@/hooks/useProjects";
import { Workspace } from "@/components/workspace/workspace";
import { ErrorState } from "@/components/ui/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { EmptyState } from "@/components/ui/empty-state";
import { FileQuestion } from "lucide-react";

export default function ProjectWorkspacePage() {
  const params = useParams();
  const id = String(params.id);
  const { data: project, isLoading, isError, error, refetch } = useProject(id);

  if (isLoading) {
    return (
      <div className="flex h-full flex-col">
        <div className="border-b border-border px-4 py-4 sm:px-8">
          <Skeleton className="mb-3 h-6 w-64" />
          <Skeleton className="h-8 w-full max-w-3xl" />
        </div>
        <div className="mx-auto w-full max-w-4xl px-4 py-6 sm:px-8">
          <Skeleton className="mb-4 h-6 w-48" />
          <Skeleton className="h-40 w-full" />
        </div>
      </div>
    );
  }

  if (isError) {
    const notFound = error instanceof ApiError && error.status === 404;
    if (notFound) {
      return (
        <div className="mx-auto max-w-lg px-4 py-16 sm:px-8">
          <EmptyState
            icon={FileQuestion}
            title="Project not found"
            description="This project may have been deleted."
            action={
              <Link href="/projects">
                <Button variant="primary">Back to projects</Button>
              </Link>
            }
          />
        </div>
      );
    }
    return (
      <div className="mx-auto max-w-lg px-8 py-16">
        <ErrorState error={error} onRetry={() => refetch()} />
      </div>
    );
  }

  if (!project) return null;

  return <Workspace project={project} />;
}
