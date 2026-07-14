import { cn } from "@/lib/utils";

type BarTone = "neutral" | "accent" | "success" | "graded";

const fills: Record<Exclude<BarTone, "graded">, string> = {
  neutral: "bg-subtle",
  accent: "bg-accent",
  success: "bg-success",
};

/** Grade by value: low → muted, mid → info, high → success teal. */
function gradedFill(pct: number): string {
  if (pct >= 70) return "bg-success";
  if (pct >= 40) return "bg-info";
  return "bg-muted";
}

/**
 * Slim horizontal meter for relevance / suitability / interest.
 * `value` may be 0-1 or 0-100; we normalize.
 */
export function ScoreBar({
  value,
  label,
  tone = "graded",
  className,
}: {
  value: number;
  label?: string;
  tone?: BarTone;
  className?: string;
}) {
  const pct = normalize(value);
  const fill = tone === "graded" ? gradedFill(pct) : fills[tone];
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="h-1 flex-1 overflow-hidden rounded-sm bg-elevated">
        <div
          className={cn("h-full rounded-sm transition-all", fill)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-6 shrink-0 text-right font-mono text-[11px] tabular-nums text-subtle">
        {label ?? `${Math.round(pct)}`}
      </span>
    </div>
  );
}

export function normalize(value: number): number {
  if (value == null || Number.isNaN(value)) return 0;
  const v = value <= 1 ? value * 100 : value;
  return Math.max(0, Math.min(100, v));
}
