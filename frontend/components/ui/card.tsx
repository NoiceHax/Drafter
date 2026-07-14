import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({
  className,
  selected,
  interactive,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  selected?: boolean;
  interactive?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded border bg-panel",
        interactive && "transition-colors hover:border-borderStrong",
        selected
          ? "border-accent ring-1 ring-accent/40"
          : "border-border",
        className
      )}
      {...props}
    />
  );
}
