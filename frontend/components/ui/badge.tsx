import * as React from "react";
import { cn } from "@/lib/utils";

type Tone =
  | "neutral"
  | "accent"
  | "success"
  | "warning"
  | "danger"
  | "muted"
  | "info";

const tones: Record<Tone, string> = {
  neutral: "bg-elevated text-subtle border-border",
  accent: "bg-accent-soft text-accent border-accent-muted",
  success: "bg-success-soft text-success border-success/30",
  warning: "bg-warning/10 text-warning border-warning/25",
  danger: "bg-danger/10 text-danger border-danger/25",
  info: "bg-info/10 text-info border-info/25",
  muted: "bg-transparent text-muted border-border",
};

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: React.ReactNode;
  tone?: Tone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "label inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[10px] leading-none",
        tones[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
