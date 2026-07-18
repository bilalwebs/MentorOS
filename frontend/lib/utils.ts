import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Standard shadcn/ui class-merging helper: combines conditional classes and resolves Tailwind conflicts. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Formats an ISO date string into a short, readable label (e.g. "Jul 16, 2026"). */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

/** Formats an ISO date string into a relative "time ago" label for activity feeds. */
export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "—";
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

  const units: [number, string][] = [
    [60, "second"],
    [60, "minute"],
    [24, "hour"],
    [7, "day"],
    [4.345, "week"],
    [12, "month"],
    [Number.POSITIVE_INFINITY, "year"],
  ];

  let value = seconds;
  let unitLabel = "second";
  for (const [amount, label] of units) {
    if (value < amount) {
      unitLabel = label;
      break;
    }
    value = Math.floor(value / amount);
    unitLabel = label;
  }
  if (value <= 1 && unitLabel === "second") return "just now";
  return `${value} ${unitLabel}${value !== 1 ? "s" : ""} ago`;
}

/** Capitalizes and de-slugs enum-style values coming from the API (e.g. "career_goal" -> "Career Goal"). */
export function humanizeEnum(value: string): string {
  return value
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
