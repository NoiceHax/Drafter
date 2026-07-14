"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type Variant =
  | "primary"
  | "generate"
  | "secondary"
  | "ghost"
  | "outline"
  | "danger";
type Size = "sm" | "md" | "icon";

const variants: Record<Variant, string> = {
  primary:
    "bg-accent text-text font-semibold hover:bg-accent-hover disabled:bg-accent/50",
  // Darker accent shade for process-starting actions (Generate / Regenerate).
  // Uses arbitrary values so the dev server hot-reloads without a config reload.
  generate:
    "bg-[#a83545] text-text font-semibold hover:bg-[#bd3e50] disabled:bg-[#a83545]/50",
  secondary:
    "bg-elevated text-text border border-border hover:border-borderStrong hover:bg-raised",
  ghost: "text-subtle hover:text-text hover:bg-elevated",
  outline:
    "border border-border text-text hover:border-borderStrong hover:bg-elevated",
  danger:
    "text-danger hover:bg-danger/10 hover:text-danger border border-transparent hover:border-danger/30",
};

const sizes: Record<Size, string> = {
  sm: "h-7 px-2.5 text-xs gap-1.5",
  md: "h-9 px-3.5 text-sm gap-2",
  icon: "h-8 w-8 justify-center",
};

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { className, variant = "secondary", size = "md", loading, children, disabled, ...props },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center rounded transition-colors duration-100 focus-visible:outline-2 disabled:cursor-not-allowed disabled:opacity-60 whitespace-nowrap",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
