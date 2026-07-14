"use client";

import * as React from "react";
import { Sparkles } from "lucide-react";
import { Input } from "./input";
import { Button } from "./button";

/**
 * A compact "refine with an instruction" row used by every generation panel.
 */
export function InstructionInput({
  placeholder = "Optional instruction to refine…",
  buttonLabel,
  loading,
  onSubmit,
  defaultValue = "",
  icon,
}: {
  placeholder?: string;
  buttonLabel: string;
  loading?: boolean;
  onSubmit: (instruction: string) => void;
  defaultValue?: string;
  icon?: React.ReactNode;
}) {
  const [value, setValue] = React.useState(defaultValue);

  return (
    <form
      className="flex items-center gap-2"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit(value.trim());
      }}
    >
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1"
      />
      <Button type="submit" variant="generate" loading={loading}>
        {!loading && (icon ?? <Sparkles className="h-3.5 w-3.5" />)}
        {buttonLabel}
      </Button>
    </form>
  );
}
