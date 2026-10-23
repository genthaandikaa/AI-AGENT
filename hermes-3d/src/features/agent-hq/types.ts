export interface DepartmentConfig {
  id: string;
  name: string;
  color: string;
  glowColor: string;
  iconName: string;
  position: [number, number, number]; // [x, y, z] in 3D space
  roles: string[];
  description: string;
}

export const DEPARTMENTS: DepartmentConfig[] = [
  {
    id: "research",
    name: "Research",
    color: "#2563eb", // Blue
    glowColor: "#60a5fa",
    iconName: "Search",
    position: [0, 0, -22], // Top / North
    roles: ["researcher", "content_researcher"],
    description: "Market analysis, fact-checking & trend discovery"
  },
  {
    id: "scripts_coding",
    name: "Scripts & Coding",
    color: "#eab308", // Yellow / Gold
    glowColor: "#fde047",
    iconName: "Code",
    position: [16, 0, -16], // Top-Right / North-East
    roles: ["scriptwriter", "antigravity_engineer", "developer"],
    description: "Scriptwriting, viral hooks & software engineering"
  },
  {
    id: "social",
    name: "Social",
    color: "#ec4899", // Pink / Magenta
    glowColor: "#f472b6",
    iconName: "Share2",
    position: [22, 0, 0], // Right / East
    roles: ["social_media_specialist", "publisher"],
    description: "Multi-platform distribution & audience engagement"
  },
  {
    id: "creative",
    name: "Creative",
    color: "#8b5cf6", // Purple / Violet
    glowColor: "#c084fc",
    iconName: "Sparkles",
    position: [16, 0, 16], // Bottom-Right / South-East
    roles: ["video_editor", "creator_pm", "designer"],
    description: "16:9 explainer videos, animation & rendering"
  },
  {
    id: "analytics",
    name: "Analytics",
    color: "#14b8a6", // Teal / Cyan
    glowColor: "#2dd4bf",
    iconName: "BarChart3",
    position: [0, 0, 22], // Bottom / South
    roles: ["treasurer", "financial_analyst"],
    description: "Token budget health, burn rate & ROI auditing"
  },
  {
    id: "trading_shop",
    name: "Trading & Shop",
    color: "#ef4444", // Red
    glowColor: "#f87171",
    iconName: "ShoppingBag",
    position: [-16, 0, 16], // Bottom-Left / South-West
    roles: ["tiktok_affiliate", "ecommerce_specialist"],
    description: "TikTok shop keranjang kuning & affiliate conversion"
  },
  {
    id: "dev_sysops",
    name: "Dev & SysOps",
    color: "#10b981", // Emerald / Green
    glowColor: "#34d399",
    iconName: "Terminal",
    position: [-22, 0, 0], // Left / West
    roles: ["qa_sentinel", "sysops", "security"],
    description: "Continuous testing, infrastructure & quality assurance"
  },
  {
    id: "executive_inbox",
    name: "Executive & HQ",
    color: "#f97316", // Orange
    glowColor: "#fb923c",
    iconName: "Briefcase",
    position: [-16, 0, -16], // Top-Left / North-West
    roles: ["executive_manager", "secretary", "ceo"],
    description: "Strategic coordination, standup approvals & scheduling"
  }
];
