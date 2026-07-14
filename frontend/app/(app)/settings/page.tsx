"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { KeyRound, Check, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import { API_URL } from "@/lib/api";
import { useToast } from "@/components/ui/toast";
import { PageHeader } from "@/components/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";

export default function SettingsPage() {
  const { toast } = useToast();
  const { data: status, refetch } = useQuery({
    queryKey: ["user-keys"],
    queryFn: api.getKeys,
  });

  const [nvidiaKey, setNvidiaKey] = React.useState("");
  const [nvidiaModel, setNvidiaModel] = React.useState("");
  const [tavilyKey, setTavilyKey] = React.useState("");
  const [pexelsKey, setPexelsKey] = React.useState("");
  const [saving, setSaving] = React.useState(false);

  // Prefill the model (non-secret); secret fields stay blank and show "set" state.
  React.useEffect(() => {
    if (status?.nvidia_model) setNvidiaModel(status.nvidia_model);
  }, [status?.nvidia_model]);

  const save = async () => {
    setSaving(true);
    try {
      // Only send fields the user typed; blank secret = leave unchanged.
      const body: Record<string, string> = {};
      if (nvidiaKey) body.nvidia_api_key = nvidiaKey;
      if (nvidiaModel) body.nvidia_model = nvidiaModel;
      if (tavilyKey) body.tavily_api_key = tavilyKey;
      if (pexelsKey) body.pexels_api_key = pexelsKey;
      await api.updateKeys(body);
      setNvidiaKey("");
      setTavilyKey("");
      setPexelsKey("");
      await refetch();
      toast("Keys saved.", "success");
    } catch {
      toast("Could not save your keys.", "error");
    } finally {
      setSaving(false);
    }
  };

  const clearKey = async (
    field: "nvidia_api_key" | "tavily_api_key" | "pexels_api_key"
  ) => {
    await api.updateKeys({ [field]: "" } as never);
    await refetch();
    toast("Key cleared.", "success");
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-6 sm:px-8">
      <PageHeader
        eyebrow="Your keys"
        title="Settings"
        description="Bring your own API keys. When set, they override the shared server keys for your generations. Keys are stored on your account and never shown again."
      />

      <div className="mt-6 space-y-4">
        <Card className="space-y-5 p-5">
          <div className="flex items-center gap-2">
            <KeyRound className="h-4 w-4 text-accent" />
            <h2 className="serif text-lg font-semibold text-text">API keys</h2>
          </div>

          <KeyField
            label="NVIDIA NIM API key"
            hint="Used for all AI generation."
            getUrl="https://build.nvidia.com"
            getLabel="Get a key at build.nvidia.com"
            isSet={status?.nvidia_api_key_set}
            value={nvidiaKey}
            onChange={setNvidiaKey}
            onClear={() => clearKey("nvidia_api_key")}
            placeholder="nvapi-…"
          />

          <div>
            <Label>NVIDIA model</Label>
            <Input
              value={nvidiaModel}
              onChange={(e) => setNvidiaModel(e.target.value)}
              placeholder="mistralai/mistral-small-4-119b-2603"
            />
            <p className="mt-1 text-[11px] text-muted">
              Model id to use. Leave blank to use the server default.{" "}
              <a
                href="https://build.nvidia.com/models"
                target="_blank"
                rel="noreferrer"
                className="text-accent hover:text-accent-hover"
              >
                Browse models
              </a>
            </p>
          </div>

          <KeyField
            label="Tavily API key"
            hint="Enables research mode with your own search quota."
            getUrl="https://app.tavily.com/home"
            getLabel="Get a key at tavily.com"
            isSet={status?.tavily_api_key_set}
            value={tavilyKey}
            onChange={setTavilyKey}
            onClear={() => clearKey("tavily_api_key")}
            placeholder="tvly-…"
          />

          <KeyField
            label="Pexels API key"
            hint="Discovers real, licensable footage for scenes."
            getUrl="https://www.pexels.com/api/new/"
            getLabel="Get a key at pexels.com/api"
            isSet={status?.pexels_api_key_set}
            value={pexelsKey}
            onChange={setPexelsKey}
            onClear={() => clearKey("pexels_api_key")}
            placeholder="Pexels key"
          />

          <div className="border-t border-border pt-4">
            <Button variant="primary" loading={saving} onClick={save}>
              Save keys
            </Button>
          </div>
        </Card>

        <Card className="p-4">
          <h2 className="label mb-1 text-xs text-text">API endpoint</h2>
          <code className="block rounded border border-border bg-bg px-3 py-2 font-mono text-xs tabular-nums text-subtle">
            {API_URL}
          </code>
        </Card>
      </div>
    </div>
  );
}

function KeyField({
  label,
  hint,
  getUrl,
  getLabel,
  isSet,
  value,
  onChange,
  onClear,
  placeholder,
}: {
  label: string;
  hint: string;
  getUrl?: string;
  getLabel?: string;
  isSet?: boolean;
  value: string;
  onChange: (v: string) => void;
  onClear: () => void;
  placeholder?: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between">
        <Label>{label}</Label>
        {isSet && (
          <span className="label inline-flex items-center gap-1 text-[9px] text-success">
            <Check className="h-3 w-3" />
            Set
          </span>
        )}
      </div>
      <Input
        type="password"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={isSet ? "•••••••• (unchanged)" : placeholder}
      />
      <div className="mt-1 flex items-center justify-between gap-3">
        <p className="text-[11px] text-muted">
          {hint}
          {getUrl && (
            <>
              {" "}
              <a
                href={getUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-0.5 text-accent hover:text-accent-hover"
              >
                {getLabel || "Get a key"}
                <ExternalLink className="h-3 w-3" />
              </a>
            </>
          )}
        </p>
        {isSet && (
          <button
            onClick={onClear}
            className="shrink-0 text-[11px] text-muted hover:text-danger"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
