import { Badge } from "@/components/ui/badge";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Platform } from "@/types";

export function PlatformBadge({ platform }: { platform: Platform }) {
  return <Badge tone="neutral">{PLATFORM_LABELS[platform] ?? platform}</Badge>;
}
