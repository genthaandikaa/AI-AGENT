// Office renderer preference: 3D Agent HQ vs. lightweight 2D pixel scene vs. Retro 3D.
// Persisted in localStorage so the choice survives reloads.

import { detectSoftwareWebGL } from "@/features/retro-office/core/graphicsQuality";

export type OfficeRenderMode = "agent-hq" | "3d" | "2d";

export const OFFICE_RENDER_MODE_STORAGE_KEY = "hermes-office-render-mode-v1";

export const OFFICE_RENDER_MODE_OPTIONS: Array<{
  id: OfficeRenderMode;
  label: string;
  description: string;
}> = [
  {
    id: "agent-hq",
    label: "3D Agent HQ",
    description: "Futuristic isometric Agent HQ with central brain hub and 8 department rooms.",
  },
  {
    id: "2d",
    label: "2D pixel",
    description: "Gather-style pixel office. Great for low-power machines.",
  },
  {
    id: "3d",
    label: "Retro 3D",
    description: "Classic Three.js retro office with desks and furniture.",
  },
];

export const isOfficeRenderMode = (value: unknown): value is OfficeRenderMode =>
  value === "agent-hq" || value === "3d" || value === "2d";

/** The explicit user choice, or null when the user never picked one. */
export const loadStoredOfficeRenderMode = (): OfficeRenderMode | null => {
  if (typeof window === "undefined") return null;
  try {
    const stored = window.localStorage.getItem(OFFICE_RENDER_MODE_STORAGE_KEY);
    if (isOfficeRenderMode(stored)) return stored;
  } catch {
    // Storage unavailable (private mode, etc.) — fall through to default.
  }
  return null;
};

/**
 * The mode the office should boot with: the user's stored choice, or defaults to "agent-hq".
 */
export const resolveInitialOfficeRenderMode = (): OfficeRenderMode =>
  loadStoredOfficeRenderMode() ?? "agent-hq";

export const saveOfficeRenderMode = (mode: OfficeRenderMode) => {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(OFFICE_RENDER_MODE_STORAGE_KEY, mode);
  } catch {
    // Best effort only.
  }
};
