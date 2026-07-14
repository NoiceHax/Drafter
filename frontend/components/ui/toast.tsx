"use client";

import * as React from "react";
import { X, AlertTriangle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";

type ToastTone = "error" | "success" | "info";
interface Toast {
  id: number;
  message: string;
  tone: ToastTone;
}

interface ToastContextValue {
  toast: (message: string, tone?: ToastTone) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  const idRef = React.useRef(0);

  const dismiss = React.useCallback((id: number) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const toast = React.useCallback(
    (message: string, tone: ToastTone = "error") => {
      const id = ++idRef.current;
      setToasts((t) => [...t, { id, message, tone }]);
      window.setTimeout(() => dismiss(id), tone === "error" ? 6000 : 3500);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 max-w-[calc(100vw-2rem)] flex-col gap-2">
        {toasts.map((t) => (
          <div
            key={t.id}
            role="status"
            className={cn(
              "pointer-events-auto flex items-start gap-2.5 rounded border bg-elevated p-3 text-xs shadow-xl animate-fade-in",
              t.tone === "error" && "border-danger/40",
              t.tone === "success" && "border-success/40",
              t.tone === "info" && "border-border"
            )}
          >
            {t.tone === "error" ? (
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-danger" />
            ) : t.tone === "success" ? (
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
            ) : null}
            <p className="flex-1 leading-relaxed text-text">{t.message}</p>
            <button
              onClick={() => dismiss(t.id)}
              className="shrink-0 text-muted hover:text-text"
              aria-label="Dismiss"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) {
    // Safe no-op if used outside provider (keeps components decoupled).
    return { toast: () => undefined } as ToastContextValue;
  }
  return ctx;
}
