"use client";

import * as React from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { ArrowRight, ArrowLeft } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";

type Step = "email" | "password" | "alpha";

export default function LoginPage() {
  const router = useRouter();
  const { login, user } = useAuth();

  const [step, setStep] = React.useState<Step>("email");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Already signed in? Go to the bench.
  React.useEffect(() => {
    if (user) router.replace("/dashboard");
  }, [user, router]);

  const submitEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { mode } = await api.checkEmail(email.trim());
      if (mode === "alpha") setStep("alpha");
      else if (mode === "password") setStep("password");
      else
        setError(
          "That email isn't on the list yet. Drafter is invite-only during alpha."
        );
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const doLogin = async (withPassword: boolean) => {
    setError(null);
    setLoading(true);
    try {
      const res = await api.login({
        email: email.trim(),
        password: withPassword ? password : undefined,
      });
      login(res.token, res.user);
      router.replace("/dashboard");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Could not sign you in."
      );
    } finally {
      setLoading(false);
    }
  };

  const back = () => {
    setStep("email");
    setPassword("");
    setError(null);
  };

  return (
    <div className="ruled flex min-h-screen items-center justify-center bg-bg px-4">
      <span className="margin-rule pointer-events-none fixed inset-y-0 left-8 hidden w-px sm:block" />
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-md bg-[#f3ede2] ring-1 ring-black/10">
            <Image src="/logo.jpg" alt="Drafter" width={48} height={48} className="h-full w-full object-cover" />
          </div>
          <div>
            <div className="serif text-2xl font-semibold text-text">Drafter</div>
            <div className="label mt-1 text-[9px] text-muted">The writing bench</div>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-panel p-6">
          {step === "email" && (
            <form onSubmit={submitEmail} className="space-y-4">
              <div>
                <h1 className="serif text-lg font-semibold text-text">Sign in</h1>
                <p className="mt-1 text-xs text-muted">
                  Enter your email to continue.
                </p>
              </div>
              <div>
                <Label>Email</Label>
                <Input
                  type="email"
                  autoFocus
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@studio.com"
                />
              </div>
              {error && <p className="text-xs leading-relaxed text-danger">{error}</p>}
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                className="w-full justify-center"
              >
                Continue
                {!loading && <ArrowRight className="h-4 w-4" />}
              </Button>
            </form>
          )}

          {step === "password" && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                doLogin(true);
              }}
              className="space-y-4"
            >
              <button
                type="button"
                onClick={back}
                className="inline-flex items-center gap-1 text-[11px] text-muted hover:text-text"
              >
                <ArrowLeft className="h-3 w-3" />
                {email}
              </button>
              <div>
                <Label>Password</Label>
                <Input
                  type="password"
                  autoFocus
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Your password"
                />
              </div>
              {error && <p className="text-xs leading-relaxed text-danger">{error}</p>}
              <Button
                type="submit"
                variant="primary"
                loading={loading}
                className="w-full justify-center"
              >
                Sign in
              </Button>
            </form>
          )}

          {step === "alpha" && (
            <div className="space-y-4">
              <button
                type="button"
                onClick={back}
                className="inline-flex items-center gap-1 text-[11px] text-muted hover:text-text"
              >
                <ArrowLeft className="h-3 w-3" />
                Use a different email
              </button>
              <div>
                <div className="label mb-1 text-[9px] text-accent">Alpha access</div>
                <p className="text-sm leading-relaxed text-subtle">
                  You&rsquo;re on the alpha list. No password needed.
                </p>
              </div>
              {error && <p className="text-xs leading-relaxed text-danger">{error}</p>}
              <Button
                variant="primary"
                loading={loading}
                onClick={() => doLogin(false)}
                className="w-full justify-center"
              >
                Continue as {email}
                {!loading && <ArrowRight className="h-4 w-4" />}
              </Button>
            </div>
          )}
        </div>

        <p className="mt-6 text-center text-[11px] text-muted">
          Drafter is invite-only during alpha.
        </p>
      </div>
    </div>
  );
}
