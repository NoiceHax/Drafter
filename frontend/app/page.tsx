import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  Feather,
  Search,
  Frame,
  Zap,
  BookOpen,
  Film,
  Camera,
} from "lucide-react";

export const metadata = {
  title: "Drafter - From a rough idea to a shot-ready script",
};

const STAGES = [
  { n: "01", label: "Idea", icon: Feather, note: "Refine a rough line into a sharp premise." },
  { n: "02", label: "Keywords", icon: Search, note: "Expand it into semantic, story, and discovery terms." },
  { n: "03", label: "Angle", icon: Frame, note: "Pick the frame that fits your voice." },
  { n: "04", label: "Hook", icon: Zap, note: "Ten archetypes, scored for the story." },
  { n: "05", label: "Story", icon: BookOpen, note: "A researched, structured outline." },
  { n: "06", label: "Script", icon: Film, note: "Timed, scene-by-scene, every line editable." },
  { n: "07", label: "Visuals", icon: Camera, note: "Directions plus real, licensable footage." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg text-text">
      {/* Nav */}
      <header className="sticky top-0 z-30 border-b border-border bg-bg/85 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-5 sm:px-8">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center overflow-hidden rounded-sm bg-[#f3ede2] ring-1 ring-black/10">
              <Image src="/logo.jpg" alt="Drafter" width={28} height={28} className="h-full w-full object-cover" />
            </div>
            <span className="serif text-[17px] font-semibold">Drafter</span>
          </div>
          <nav className="flex items-center gap-5 text-xs text-subtle">
            <a href="#how" className="hidden hover:text-text sm:inline">How it works</a>
            <a href="#pipeline" className="hidden hover:text-text sm:inline">The pipeline</a>
            <Link
              href="/dashboard"
              className="rounded-sm bg-accent px-3 py-1.5 font-semibold text-text transition-colors hover:bg-accent-hover"
            >
              Open the bench
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="ruled relative overflow-hidden">
        <span className="margin-rule pointer-events-none absolute inset-y-0 left-8 hidden w-px sm:block" />
        <div className="mx-auto max-w-6xl px-5 py-24 sm:px-8 sm:py-32">
          <div className="max-w-3xl">
            <div className="label mb-5 text-[11px] text-accent">The writing bench for short-form video</div>
            <h1 className="serif text-4xl font-semibold leading-[1.05] text-text sm:text-6xl">
              A rough idea is not
              <br />
              a script. <span className="text-accent">Yet.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-relaxed text-subtle sm:text-lg">
              Give Drafter ten words. Leave with a researched, scene-by-scene
              script: a chosen angle, a scored hook, timed narration, and real
              footage to shoot against.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-sm bg-accent px-5 py-2.5 text-sm font-semibold text-text transition-colors hover:bg-accent-hover"
              >
                Start a draft
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#pipeline"
                className="inline-flex items-center gap-2 rounded-sm border border-borderStrong px-5 py-2.5 text-sm text-subtle transition-colors hover:bg-elevated hover:text-text"
              >
                See the pipeline
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Problem / thesis */}
      <section id="how" className="border-t border-border bg-panel/40">
        <div className="mx-auto grid max-w-6xl gap-8 px-5 py-20 sm:grid-cols-3 sm:px-8">
          <div className="sm:col-span-1">
            <div className="label text-[10px] text-muted">The problem</div>
            <h2 className="serif mt-2 text-2xl font-semibold leading-tight">
              The idea was there. The script wasn&rsquo;t.
            </h2>
          </div>
          <div className="grid gap-6 sm:col-span-2 sm:grid-cols-2">
            <p className="text-sm leading-relaxed text-subtle">
              A blank page turns a good idea into an afternoon of second-guessing:
              what&rsquo;s the angle, what&rsquo;s the hook, is any of this true,
              what do we even show on screen?
            </p>
            <p className="text-sm leading-relaxed text-subtle">
              Drafter treats your rough input as a seed, not the brief. It sharpens
              the direction with you, then builds every downstream piece in order,
              so nothing starts from zero.
            </p>
          </div>
        </div>
      </section>

      {/* Pipeline centerpiece */}
      <section id="pipeline" className="border-t border-border">
        <div className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
          <div className="mb-10 flex flex-wrap items-end justify-between gap-3">
            <div>
              <div className="label text-[10px] text-accent">The running order</div>
              <h2 className="serif mt-2 text-3xl font-semibold">
                Seven beats, idea to shot list.
              </h2>
            </div>
            <p className="max-w-xs text-xs leading-relaxed text-muted">
              Each stage is its own step: reviewable, editable, and regeneratable
              on its own without redoing the rest.
            </p>
          </div>

          <ol className="grid gap-px overflow-hidden rounded border border-border bg-border sm:grid-cols-2 lg:grid-cols-4">
            {STAGES.map((s) => {
              const Icon = s.icon;
              return (
                <li key={s.n} className="flex flex-col gap-3 bg-panel p-5">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] tabular-nums text-accent">{s.n}</span>
                    <Icon className="h-4 w-4 text-muted" />
                  </div>
                  <div className="serif text-lg font-semibold text-text">{s.label}</div>
                  <p className="text-[12px] leading-relaxed text-subtle">{s.note}</p>
                </li>
              );
            })}
            <li className="flex flex-col justify-center gap-3 bg-accent-soft p-5">
              <div className="serif text-lg font-semibold text-text">Ready to shoot</div>
              <p className="text-[12px] leading-relaxed text-subtle">
                Copy or download the script. Every scene has narration, on-screen
                text, visual direction, and sourced footage.
              </p>
            </li>
          </ol>
        </div>
      </section>

      {/* Proof points */}
      <section className="border-t border-border bg-panel/40">
        <div className="mx-auto grid max-w-6xl gap-px overflow-hidden rounded border border-border bg-border px-0 sm:grid-cols-3 sm:mx-auto sm:my-20 sm:max-w-6xl">
          {[
            { k: "Grounded", v: "Research with real, cited sources. Nothing fabricated." },
            { k: "Honest visuals", v: "AI directions stay separate from real, licensed footage." },
            { k: "Yours to edit", v: "Every hook, scene, and CTA is editable and regeneratable." },
          ].map((c) => (
            <div key={c.k} className="bg-panel p-6">
              <div className="serif text-lg font-semibold text-text">{c.k}</div>
              <p className="mt-1.5 text-sm leading-relaxed text-subtle">{c.v}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="border-t border-border">
        <div className="mx-auto max-w-6xl px-5 py-24 text-center sm:px-8">
          <h2 className="serif mx-auto max-w-2xl text-3xl font-semibold leading-tight sm:text-4xl">
            Stop staring at the blank page.
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-sm text-subtle">
            Bring the rough idea. Drafter takes it the rest of the way.
          </p>
          <Link
            href="/dashboard"
            className="mt-8 inline-flex items-center gap-2 rounded-sm bg-accent px-6 py-3 text-sm font-semibold text-text transition-colors hover:bg-accent-hover"
          >
            Start a draft
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-5 py-8 text-xs text-muted sm:flex-row sm:px-8">
          <div className="flex items-center gap-2">
            <Feather className="h-3.5 w-3.5 text-accent" />
            <span className="serif text-sm text-subtle">Drafter</span>
          </div>
          <span>
            Made by{" "}
            <a
              href="https://noicehax.dev"
              target="_blank"
              rel="noreferrer"
              className="text-subtle underline decoration-borderStrong underline-offset-2 hover:text-accent"
            >
              NoiceHax
            </a>
          </span>
        </div>
      </footer>
    </div>
  );
}
