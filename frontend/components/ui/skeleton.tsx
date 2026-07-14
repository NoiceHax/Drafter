"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("skeleton rounded", className)} />;
}

/** Live elapsed-seconds counter; starts on mount. */
function useElapsed() {
  const [ms, setMs] = React.useState(0);
  React.useEffect(() => {
    const start = Date.now();
    const id = window.setInterval(() => setMs(Date.now() - start), 100);
    return () => window.clearInterval(id);
  }, []);
  return ms;
}

/**
 * Stage-specific loading block with a message like "Generating hooks…".
 * The pulsing red dot is the proofreader's live mark. A live elapsed timer
 * makes it obvious the request is working (not frozen); after a threshold it
 * adds a gentle "still working" note so a slow model never reads as stuck.
 */
export function GeneratingState({
  message,
  rows = 3,
  columns = 1,
  slowAfterSeconds = 20,
}: {
  message: string;
  rows?: number;
  columns?: number;
  slowAfterSeconds?: number;
}) {
  const ms = useElapsed();
  const secs = ms / 1000;
  const slow = secs >= slowAfterSeconds;

  return (
    <div className="animate-fade-in">
      <div className="mb-4 flex items-center gap-2">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-60" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
        </span>
        <span className="label text-xs text-subtle">{message}</span>
        <span className="ml-auto font-mono text-xs tabular-nums text-muted">
          {secs.toFixed(1)}s
        </span>
      </div>
      {slow && (
        <p className="mb-4 text-[11px] leading-relaxed text-warning">
          Still working. The model is taking longer than usual. This can happen
          when the provider is under load; it will finish or time out shortly.
        </p>
      )}
      <div
        className="grid gap-3"
        style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
      >
        {Array.from({ length: rows * columns }).map((_, i) => (
          <div key={i} className="rounded border border-border bg-panel p-4">
            <Skeleton className="mb-3 h-4 w-1/3" />
            <Skeleton className="mb-2 h-3 w-full" />
            <Skeleton className="mb-2 h-3 w-5/6" />
            <Skeleton className="h-3 w-2/3" />
          </div>
        ))}
      </div>
    </div>
  );
}
