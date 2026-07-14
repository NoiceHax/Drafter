"use client";

import * as React from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export function ChipInput({
  value,
  onChange,
  placeholder = "Type and press Enter…",
}: {
  value: string[];
  onChange: (next: string[]) => void;
  placeholder?: string;
}) {
  const [draft, setDraft] = React.useState("");

  const add = (raw: string) => {
    const t = raw.trim().replace(/,$/, "").trim();
    if (!t) return;
    if (value.some((v) => v.toLowerCase() === t.toLowerCase())) {
      setDraft("");
      return;
    }
    onChange([...value, t]);
    setDraft("");
  };

  return (
    <div className="flex min-h-9 flex-wrap items-center gap-1.5 rounded border border-border bg-bg px-2 py-1.5 focus-within:border-accent/70">
      {value.map((chip) => (
        <span
          key={chip}
          className="inline-flex items-center gap-1 rounded-sm bg-elevated px-2 py-0.5 text-xs text-text"
        >
          {chip}
          <button
            type="button"
            onClick={() => onChange(value.filter((v) => v !== chip))}
            className="text-muted hover:text-text"
            aria-label={`Remove ${chip}`}
          >
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            add(draft);
          } else if (e.key === "Backspace" && !draft && value.length) {
            onChange(value.slice(0, -1));
          }
        }}
        onBlur={() => draft && add(draft)}
        placeholder={value.length ? "" : placeholder}
        className={cn(
          "min-w-[8rem] flex-1 bg-transparent text-sm text-text placeholder:text-muted focus:outline-none"
        )}
      />
    </div>
  );
}
