"use client";

import * as React from "react";
import { HelpCircle, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export function Panel({
  step,
  eyebrow,
  title,
  description,
  guide,
  guideKey,
  actions,
  children,
}: {
  /** Beat number in the running order (e.g. "03"); reinforces the sequence. */
  step?: string;
  eyebrow?: string;
  title: string;
  description?: string;
  /** Longer how-to-use instructions for this section (bullet lines). */
  guide?: string[];
  /** Stable key so the guide's open/closed state persists per section. */
  guideKey?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="animate-fade-in">
      <div className="mb-5 border-b border-border pb-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex min-w-0 items-start gap-3">
            {step && (
              <span className="mt-0.5 font-mono text-[11px] tabular-nums text-accent">
                {step}
              </span>
            )}
            <div className="min-w-0">
              {eyebrow && (
                <div className="label mb-1 text-[10px] text-muted">{eyebrow}</div>
              )}
              <h2 className="serif text-[22px] font-semibold leading-none text-text">
                {title}
              </h2>
              {description && (
                <p className="mt-2 text-sm text-muted">{description}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {guide && guide.length > 0 && (
              <SectionGuide items={guide} storageKey={guideKey} />
            )}
            {actions}
          </div>
        </div>
      </div>
      {children}
    </section>
  );
}

/** Collapsible "How this works" instructions for a workspace section. */
function SectionGuide({
  items,
  storageKey,
}: {
  items: string[];
  storageKey?: string;
}) {
  const key = storageKey ? `draftsmith.guide.${storageKey}` : undefined;
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    if (key) {
      const stored = window.localStorage.getItem(key);
      if (stored !== null) setOpen(stored === "1");
    }
  }, [key]);

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (key) window.localStorage.setItem(key, next ? "1" : "0");
  };

  return (
    <div className="relative">
      <button
        onClick={toggle}
        aria-expanded={open}
        className={cn(
          "flex items-center gap-1.5 rounded-sm border px-2.5 py-1.5 text-[11px] transition-colors",
          open
            ? "border-borderStrong bg-elevated text-text"
            : "border-border text-muted hover:bg-elevated hover:text-subtle"
        )}
      >
        <HelpCircle className="h-3.5 w-3.5" />
        How this works
        <ChevronDown
          className={cn("h-3 w-3 transition-transform", open && "rotate-180")}
        />
      </button>
      {open && (
        <div className="absolute right-0 z-20 mt-2 w-80 max-w-[calc(100vw-3rem)] rounded border border-border bg-elevated p-3.5 shadow-xl animate-fade-in">
          <div className="label mb-2 text-[9px] text-accent">
            How to use this section
          </div>
          <ul className="flex flex-col gap-1.5">
            {items.map((item, i) => (
              <li
                key={i}
                className="flex gap-2 text-[12px] leading-relaxed text-subtle"
              >
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-accent" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
