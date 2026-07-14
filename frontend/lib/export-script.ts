import type { Script } from "@/types";
import { formatTime, humanDuration } from "@/lib/utils";

export type ExportFormat = "markdown" | "plain" | "narration";

/** Render a finished script to text in one of several export formats. */
export function formatScript(script: Script, format: ExportFormat): string {
  if (format === "narration") return narrationOnly(script);
  if (format === "plain") return plain(script);
  return markdown(script);
}

function narrationOnly(s: Script): string {
  const lines: string[] = [];
  if (s.hook_text) lines.push(s.hook_text);
  for (const scene of s.scenes) if (scene.narration) lines.push(scene.narration);
  if (s.cta_text) lines.push(s.cta_text);
  return lines.join("\n\n").trim() + "\n";
}

function plain(s: Script): string {
  const out: string[] = [];
  out.push(s.title);
  out.push(
    `${s.platform} · target ${humanDuration(s.target_duration_seconds)} · est. ${humanDuration(
      s.estimated_duration_seconds
    )}`
  );
  out.push("");
  out.push(`[HOOK] ${formatTime(0)}–${formatTime(s.hook_duration_seconds)}`);
  out.push(s.hook_text);
  out.push("");
  for (const sc of s.scenes) {
    out.push(
      `[${sc.section_type.toUpperCase()}] Scene ${sc.scene_number} · ${formatTime(
        sc.start_time
      )}–${formatTime(sc.end_time)}`
    );
    out.push(`Narration: ${sc.narration}`);
    if (sc.on_screen_text) out.push(`On-screen: ${sc.on_screen_text}`);
    if (sc.visual_direction) out.push(`Visual: ${sc.visual_direction}`);
    out.push("");
  }
  if (s.cta_text) {
    out.push(`[CTA] ${humanDuration(s.cta_duration_seconds)}`);
    out.push(s.cta_text);
  }
  return out.join("\n").trim() + "\n";
}

function markdown(s: Script): string {
  const out: string[] = [];
  out.push(`# ${s.title}`);
  out.push("");
  out.push(
    `**Platform:** ${s.platform}  ·  **Target:** ${humanDuration(
      s.target_duration_seconds
    )}  ·  **Estimated:** ${humanDuration(s.estimated_duration_seconds)}  ·  **Scenes:** ${
      s.scenes.length
    }`
  );
  out.push("");
  out.push(`## Hook \`${formatTime(0)}–${formatTime(s.hook_duration_seconds)}\``);
  out.push("");
  out.push(`> ${s.hook_text}`);
  out.push("");
  for (const sc of s.scenes) {
    out.push(
      `## Scene ${sc.scene_number} - ${sc.section_type} \`${formatTime(
        sc.start_time
      )}–${formatTime(sc.end_time)}\``
    );
    out.push("");
    out.push(`**Narration**`);
    out.push("");
    out.push(sc.narration);
    out.push("");
    if (sc.on_screen_text) {
      out.push(`**On-screen text:** ${sc.on_screen_text}`);
      out.push("");
    }
    if (sc.visual_direction) {
      out.push(`**Visual direction:** ${sc.visual_direction}`);
      out.push("");
    }
  }
  if (s.cta_text) {
    out.push(`## CTA \`${humanDuration(s.cta_duration_seconds)}\``);
    out.push("");
    out.push(`> ${s.cta_text}`);
    out.push("");
  }
  return out.join("\n").trim() + "\n";
}

export function scriptFilename(script: Script, format: ExportFormat): string {
  const slug =
    (script.title || "script")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "")
      .slice(0, 60) || "script";
  const ext = format === "markdown" ? "md" : "txt";
  return `${slug}.${ext}`;
}
