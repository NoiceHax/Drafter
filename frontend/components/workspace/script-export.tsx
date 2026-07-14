"use client";

import * as React from "react";
import { Copy, Check, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  formatScript,
  scriptFilename,
  type ExportFormat,
} from "@/lib/export-script";
import type { Script } from "@/types";

const FORMATS: { value: ExportFormat; label: string }[] = [
  { value: "markdown", label: "Markdown" },
  { value: "plain", label: "Plain" },
  { value: "narration", label: "Narration" },
];

/**
 * Export toolbar for a finished script: pick a format, then copy to clipboard
 * or download as a file. Sits beside the script so what's made is portable.
 */
export function ScriptExport({ script }: { script: Script }) {
  const [format, setFormat] = React.useState<ExportFormat>("markdown");
  const [copied, setCopied] = React.useState(false);

  const text = React.useMemo(() => formatScript(script, format), [script, format]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard blocked, ignore */
    }
  };

  const download = () => {
    const blob = new Blob([text], {
      type: format === "markdown" ? "text/markdown" : "text/plain",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = scriptFilename(script, format);
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-wrap items-center gap-2 rounded border border-border bg-panel p-2.5">
      <span className="label text-[9px] text-muted">Export</span>

      {/* Format toggle */}
      <div className="flex overflow-hidden rounded-sm border border-border">
        {FORMATS.map((f) => (
          <button
            key={f.value}
            onClick={() => setFormat(f.value)}
            className={cn(
              "px-2.5 py-1 text-[11px] transition-colors",
              format === f.value
                ? "bg-elevated text-text"
                : "text-muted hover:bg-elevated hover:text-subtle"
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="ml-auto flex items-center gap-2">
        <Button variant="secondary" size="sm" onClick={copy}>
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 text-success" />
              Copied
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5" />
              Copy
            </>
          )}
        </Button>
        <Button variant="primary" size="sm" onClick={download}>
          <Download className="h-3.5 w-3.5" />
          Download
        </Button>
      </div>
    </div>
  );
}
