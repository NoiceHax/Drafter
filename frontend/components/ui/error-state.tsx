import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "./button";
import { ApiError } from "@/lib/api";

export function errorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong.";
}

export function ErrorState({
  error,
  onRetry,
  className,
}: {
  error: unknown;
  onRetry?: () => void;
  className?: string;
}) {
  return (
    <div
      className={
        "flex flex-col items-center justify-center rounded border border-danger/25 bg-danger/5 px-6 py-10 text-center " +
        (className || "")
      }
    >
      <AlertTriangle className="mb-2 h-5 w-5 text-danger" />
      <p className="text-sm text-danger">{errorMessage(error)}</p>
      {onRetry && (
        <Button variant="outline" size="sm" className="mt-4" onClick={onRetry}>
          <RotateCcw className="h-3.5 w-3.5" />
          Retry
        </Button>
      )}
    </div>
  );
}

/** Inline error line, e.g. under a mutation button. */
export function InlineError({ error }: { error: unknown }) {
  if (!error) return null;
  return (
    <p className="mt-2 flex items-center gap-1.5 text-xs text-danger">
      <AlertTriangle className="h-3.5 w-3.5" />
      {errorMessage(error)}
    </p>
  );
}
