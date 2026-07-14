"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { KeyRound, ArrowRight, X } from "lucide-react";
import { api } from "@/lib/api";

/**
 * Prompt shown across the app when the signed-in user has not added their own
 * NVIDIA key. Generation falls back to the shared server key if one is set, but
 * we still nudge users to bring their own. Dismissible per session; hidden on
 * the settings page itself.
 */
export function KeysBanner() {
  const pathname = usePathname();
  const [dismissed, setDismissed] = React.useState(false);
  const { data } = useQuery({ queryKey: ["user-keys"], queryFn: api.getKeys });

  if (dismissed || pathname === "/settings") return null;
  if (!data || data.nvidia_api_key_set) return null;

  return (
    <div className="flex items-center gap-3 border-b border-accent-muted/40 bg-accent-soft px-4 py-2.5 text-xs sm:px-8">
      <KeyRound className="h-4 w-4 shrink-0 text-accent" />
      <span className="min-w-0 flex-1 text-subtle">
        <span className="font-semibold text-text">Add your API keys to start generating.</span>{" "}
        Drafter needs an NVIDIA NIM key for AI generation (plus optional Tavily
        and Pexels keys for research and footage).
      </span>
      <Link
        href="/settings"
        className="inline-flex shrink-0 items-center gap-1 rounded-sm bg-accent px-2.5 py-1.5 font-semibold text-text transition-colors hover:bg-accent-hover"
      >
        Add keys
        <ArrowRight className="h-3.5 w-3.5" />
      </Link>
      <button
        onClick={() => setDismissed(true)}
        aria-label="Dismiss"
        className="shrink-0 text-muted hover:text-text"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
