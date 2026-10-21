import type {
  RemovableSkillSource,
  SkillStatusEntry,
} from "@/lib/skills/types";

export type PackagedSkillId = "soundhermes" | "task-manager" | "todo-board";

export type PackagedSkillDefinition = {
  packageId: PackagedSkillId;
  skillKey: string;
  name: string;
  description: string;
  installSource: RemovableSkillSource;
  creatorName?: string;
  creatorUrl?: string;
};

const EMPTY_REQUIREMENTS = {
  bins: [],
  anyBins: [],
  env: [],
  config: [],
  os: [],
};

const PACKAGED_SKILLS: PackagedSkillDefinition[] = [
  {
    packageId: "todo-board",
    skillKey: "todo-board",
    name: "todo",
    description: "Maintain a shared workspace TODO list with blocked tasks.",
    installSource: "hermes-workspace",
    creatorName: "iamlukethedev",
    creatorUrl: "http://x.com/iamlukethedev/",
  },
  {
    packageId: "task-manager",
    skillKey: "task-manager",
    name: "task-manager",
    description:
      "Capture actionable requests as persistent tasks and keep a shared Kanban task store in sync.",
    installSource: "hermes-workspace",
    creatorName: "iamlukethedev",
    creatorUrl: "https://github.com/iamlukethedev",
  },
  {
    packageId: "soundhermes",
    skillKey: "soundhermes",
    name: "soundhermes",
    description: "Control Spotify playback, search music, and return shareable music links.",
    installSource: "hermes-workspace",
    creatorName: "iamlukethedev",
    creatorUrl: "https://github.com/iamlukethedev",
  },
];

export const listPackagedSkills = (): PackagedSkillDefinition[] => [
  ...PACKAGED_SKILLS,
];

export const getPackagedSkillById = (
  packageId: string,
): PackagedSkillDefinition | null =>
  PACKAGED_SKILLS.find((skill) => skill.packageId === packageId) ?? null;

export const getPackagedSkillBySkillKey = (
  skillKey?: string | null,
): PackagedSkillDefinition | null => {
  const normalized = typeof skillKey === "string" ? skillKey.trim() : "";
  if (!normalized) return null;
  return PACKAGED_SKILLS.find((skill) => skill.skillKey === normalized) ?? null;
};

export const buildPackagedSkillStatusEntry = (
  skill: PackagedSkillDefinition,
): SkillStatusEntry => ({
  name: skill.name ?? "(Unnamed Skill)",
  description: skill.description ?? "(No description)",
  source: "hermes-extra",
  bundled: false,
  filePath: "",
  baseDir: "",
  skillKey: skill.skillKey,
  always: false,
  disabled: false,
  blockedByAllowlist: false,
  eligible: false,
  requirements: { ...EMPTY_REQUIREMENTS },
  missing: { ...EMPTY_REQUIREMENTS },
  configChecks: [],
  install: [],
});

export const appendPackagedSkillsToMarketplace = (
  skills?: SkillStatusEntry[] | null,
): SkillStatusEntry[] => {
  const safeSkills = Array.isArray(skills) ? skills.filter(Boolean) : [];
  const presentKeys = new Set(
    safeSkills
      .map((skill) => {
        const key = typeof skill?.skillKey === "string" && skill.skillKey.trim()
          ? skill.skillKey.trim()
          : typeof skill?.name === "string"
            ? skill.name.trim()
            : "";
        return key;
      })
      .filter(Boolean),
  );
  const additions = PACKAGED_SKILLS.filter(
    (skill) => !presentKeys.has(skill.skillKey),
  ).map(buildPackagedSkillStatusEntry);
  if (additions.length === 0) {
    return safeSkills;
  }
  return [...additions, ...safeSkills];
};
