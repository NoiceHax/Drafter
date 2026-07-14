"use client";

import * as React from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  FolderKanban,
  Plus,
  PanelLeftClose,
  PanelLeftOpen,
  ChevronRight,
  FileText,
  LogOut,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useProjects } from "@/hooks/useProjects";
import { useAuth } from "@/hooks/useAuth";

const COLLAPSE_KEY = "drafter.sidebar.collapsed";
const PROJECTS_OPEN_KEY = "drafter.sidebar.projectsOpen";

function usePersistedBool(key: string, fallback: boolean) {
  const [value, setValue] = React.useState(fallback);
  React.useEffect(() => {
    const stored = window.localStorage.getItem(key);
    if (stored !== null) setValue(stored === "1");
  }, [key]);
  const update = React.useCallback(
    (next: boolean) => {
      setValue(next);
      window.localStorage.setItem(key, next ? "1" : "0");
    },
    [key]
  );
  return [value, update] as const;
}

/** The quill mark on its paper chip. Sized by the caller. */
function BrandMark({ size = 28 }: { size?: number }) {
  return (
    <div
      className="flex shrink-0 items-center justify-center overflow-hidden rounded-sm bg-[#f3ede2] ring-1 ring-black/10"
      style={{ width: size, height: size }}
    >
      <Image
        src="/logo.jpg"
        alt="Drafter"
        width={size}
        height={size}
        className="h-full w-full object-cover"
        priority
      />
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = usePersistedBool(COLLAPSE_KEY, false);
  const [projectsOpen, setProjectsOpen] = usePersistedBool(PROJECTS_OPEN_KEY, true);
  const { data: projects } = useProjects();

  const recent = React.useMemo(
    () =>
      (projects ? [...projects] : [])
        .sort(
          (a, b) =>
            new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )
        .slice(0, 8),
    [projects]
  );

  const dashboardActive = pathname === "/dashboard";
  const projectsActive = pathname.startsWith("/projects");

  return (
    <aside
      className={cn(
        "flex h-screen shrink-0 flex-col border-r border-border bg-panel transition-[width] duration-200",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Brand + collapse toggle. Collapsed: stack vertically and center. */}
      <div
        className={cn(
          "flex border-b border-border",
          collapsed
            ? "flex-col items-center gap-2 py-3"
            : "h-14 items-center gap-2.5 px-3"
        )}
      >
        <Link
          href="/"
          className="flex min-w-0 items-center gap-2.5"
          title="Drafter"
        >
          <BrandMark />
          {!collapsed && (
            <div className="min-w-0 leading-tight">
              <div className="serif text-[16px] font-semibold text-text">
                Drafter
              </div>
              <div className="label text-[9px] text-muted">Content Copilot</div>
            </div>
          )}
        </Link>
        <button
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={collapsed ? "Expand" : "Collapse"}
          className={cn(
            "flex h-7 w-7 items-center justify-center rounded-sm text-muted hover:bg-elevated hover:text-text",
            !collapsed && "ml-auto"
          )}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-4 w-4" />
          ) : (
            <PanelLeftClose className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* New project */}
      <div className={cn("p-3", collapsed && "px-2")}>
        <Link href="/projects/new" title="New project">
          <Button
            variant="primary"
            className={cn("w-full", collapsed ? "justify-center px-0" : "justify-center")}
          >
            <Plus className="h-4 w-4" />
            {!collapsed && "New project"}
          </Button>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto overflow-x-hidden px-2">
        <NavItem
          href="/dashboard"
          label="Dashboard"
          icon={LayoutDashboard}
          active={dashboardActive}
          collapsed={collapsed}
        />

        {/* Projects (expandable) */}
        {collapsed ? (
          <NavItem
            href="/projects"
            label="Projects"
            icon={FolderKanban}
            active={projectsActive}
            collapsed
          />
        ) : (
          <div>
            <div
              className={cn(
                "label relative flex items-center gap-2.5 rounded-sm px-2.5 py-2 text-xs",
                projectsActive
                  ? "bg-elevated text-text"
                  : "text-subtle hover:bg-elevated hover:text-text"
              )}
            >
              {projectsActive && (
                <span className="absolute inset-y-1.5 left-0 w-0.5 rounded-full bg-accent" />
              )}
              <Link
                href="/projects"
                className="flex min-w-0 flex-1 items-center gap-2.5"
                title="Projects"
              >
                <FolderKanban className="h-4 w-4 shrink-0" />
                Projects
              </Link>
              <button
                onClick={() => setProjectsOpen(!projectsOpen)}
                aria-label={projectsOpen ? "Collapse projects" : "Expand projects"}
                className="flex h-5 w-5 items-center justify-center rounded-sm text-muted hover:text-text"
              >
                <ChevronRight
                  className={cn(
                    "h-3.5 w-3.5 transition-transform",
                    projectsOpen && "rotate-90"
                  )}
                />
              </button>
            </div>

            {projectsOpen && (
              <div className="ml-3.5 mt-0.5 flex flex-col gap-px border-l border-border pl-2">
                {recent.length === 0 && (
                  <span className="px-2 py-1.5 text-[11px] text-muted">
                    No projects yet
                  </span>
                )}
                {recent.map((p) => {
                  const active = pathname === `/projects/${p.id}`;
                  return (
                    <Link
                      key={p.id}
                      href={`/projects/${p.id}`}
                      title={p.title || p.idea}
                      className={cn(
                        "truncate rounded-sm px-2 py-1.5 text-[12px] transition-colors",
                        active
                          ? "bg-elevated text-text"
                          : "text-subtle hover:bg-elevated hover:text-text"
                      )}
                    >
                      {p.title || p.idea || "Untitled"}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        )}

        <NavItem
          href="/settings"
          label="Settings"
          icon={Settings}
          active={pathname === "/settings"}
          collapsed={collapsed}
        />
      </nav>

      <AccountFooter collapsed={collapsed} />
    </aside>
  );
}

function AccountFooter({ collapsed }: { collapsed: boolean }) {
  const { user, logout } = useAuth();
  const router = useRouter();

  const signOut = () => {
    logout();
    router.replace("/login");
  };

  const initial = (user?.display_name || user?.email || "?")
    .charAt(0)
    .toUpperCase();

  if (collapsed) {
    return (
      <div className="flex flex-col items-center gap-2 border-t border-border py-3">
        <div
          className="flex h-7 w-7 items-center justify-center rounded-sm bg-elevated text-xs font-semibold text-subtle"
          title={user?.email}
        >
          {initial}
        </div>
        <button
          onClick={signOut}
          aria-label="Sign out"
          title="Sign out"
          className="flex h-7 w-7 items-center justify-center rounded-sm text-muted hover:bg-elevated hover:text-text"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 border-t border-border p-3">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-elevated text-xs font-semibold text-subtle">
        {initial}
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[12px] text-text" title={user?.email}>
          {user?.email || "Signed in"}
        </div>
      </div>
      <button
        onClick={signOut}
        aria-label="Sign out"
        title="Sign out"
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm text-muted hover:bg-elevated hover:text-text"
      >
        <LogOut className="h-4 w-4" />
      </button>
    </div>
  );
}

function NavItem({
  href,
  label,
  icon: Icon,
  active,
  collapsed,
}: {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  active: boolean;
  collapsed: boolean;
}) {
  return (
    <Link
      href={href}
      title={label}
      className={cn(
        "label relative flex items-center rounded-sm py-2 text-xs transition-colors",
        collapsed ? "justify-center px-0" : "gap-2.5 px-2.5",
        active ? "bg-elevated text-text" : "text-subtle hover:bg-elevated hover:text-text"
      )}
    >
      {active && !collapsed && (
        <span className="absolute inset-y-1.5 left-0 w-0.5 rounded-full bg-accent" />
      )}
      {active && collapsed && (
        <span className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-accent" />
      )}
      <Icon className="h-4 w-4 shrink-0" />
      {!collapsed && label}
    </Link>
  );
}
