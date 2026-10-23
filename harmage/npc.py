"""2D NPC representation system for Harmage Virtual Enterprise.

Provides rich personas, system prompts, operational boundaries,
and 2D vector/SVG avatars for the unified Software Engineering Division:
[PIC / Tech Lead, Frontend Developer, Backend Developer, QA Engineer, UI/UX Designer].
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional


class NPCStatus(str, Enum):
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    IN_MEETING = "in_meeting"
    AWAITING_REVIEW = "awaiting_review"
    OFF_DUTY = "off_duty"


@dataclass
class NPCProfile:
    id: str
    name: str
    role_title: str
    division: str
    status: NPCStatus
    personality_traits: List[str]
    tone_of_voice: str
    system_prompt: str
    competencies: List[str]
    allowed_tools: List[str]
    avatar_color: str
    avatar_accent: str
    current_task: Optional[str] = None
    avatar_svg: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role_title": self.role_title,
            "division": self.division,
            "status": self.status.value,
            "personality_traits": self.personality_traits,
            "tone_of_voice": self.tone_of_voice,
            "system_prompt": self.system_prompt,
            "competencies": self.competencies,
            "allowed_tools": self.allowed_tools,
            "avatar_color": self.avatar_color,
            "avatar_accent": self.avatar_accent,
            "current_task": self.current_task,
            "avatar_svg": self.avatar_svg,
        }


def _generate_2d_avatar_svg(name: str, initials: str, bg_color: str, accent_color: str, icon_type: str) -> str:
    """Generate crisp, lightweight 2D SVG avatar badge with modern flat styling."""
    icons = {
        "crown": '<path d="M16 28L20 40H44L48 28L36 34L32 22L28 34L16 28Z" fill="currentColor"/>',
        "terminal": '<path d="M18 20L28 32L18 44H24L34 32L24 20H18ZM32 40H46V44H32V40Z" fill="currentColor"/>',
        "code": '<path d="M22 24L14 32L22 40L25 37L19 32L25 27L22 24ZM42 24L39 27L45 32L39 37L42 40L50 32L42 24ZM34 18L28 46H31L37 18H34Z" fill="currentColor"/>',
        "database": '<path d="M32 16C23.2 16 16 19.6 16 24V40C16 44.4 23.2 48 32 48C40.8 48 48 44.4 48 40V24C48 19.6 40.8 16 32 16ZM32 20C38.6 20 44 22.2 44 24C44 25.8 38.6 28 32 28C25.4 28 20 25.8 20 24C20 22.2 25.4 20 32 20ZM44 32C44 33.8 38.6 36 32 36C25.4 36 20 33.8 20 32V27.5C23.2 29.7 27.4 31 32 31C36.6 31 40.8 29.7 44 27.5V32ZM44 40C44 41.8 38.6 44 32 44C25.4 44 20 41.8 20 40V35.5C23.2 37.7 27.4 39 32 39C36.6 39 40.8 37.7 44 35.5V40Z" fill="currentColor"/>',
        "shield": '<path d="M32 14L18 20V32C18 41.2 24 49.6 32 52C40 49.6 46 41.2 46 32V20L32 14ZM32 24C35.3 24 38 26.7 38 30C38 33.3 35.3 36 32 36C28.7 36 26 33.3 26 30C26 26.7 28.7 24 32 24Z" fill="currentColor"/>',
        "palette": '<path d="M32 16C23.2 16 16 23.2 16 32C16 40.8 23.2 48 32 48C33.8 48 35.3 46.5 35.3 44.7C35.3 43.8 35 43 34.4 42.4C33.8 41.8 33.5 41 33.5 40.1C33.5 38.3 35 36.8 36.8 36.8H40C44.4 36.8 48 33.2 48 28.8C48 21.7 40.8 16 32 16ZM22 28C20.9 28 20 27.1 20 26C20 24.9 20.9 24 22 24C23.1 24 24 24.9 24 26C24 27.1 23.1 28 22 28ZM28 22C26.9 22 26 21.1 26 20C26 18.9 26.9 18 28 18C29.1 18 30 18.9 30 20C30 21.1 29.1 22 28 22ZM36 22C34.9 22 34 21.1 34 20C34 18.9 34.9 18 36 18C37.1 18 38 18.9 38 20C38 21.1 37.1 22 36 22ZM42 28C40.9 28 40 27.1 40 26C40 24.9 40.9 24 42 24C43.1 24 44 24.9 44 26C44 27.1 43.1 28 42 28Z" fill="currentColor"/>',
    }
    icon_svg = icons.get(icon_type, icons["terminal"])
    svg = f'''<svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="18" fill="{bg_color}"/>
  <rect x="2" y="2" width="60" height="60" rx="16" stroke="{accent_color}" stroke-opacity="0.3" stroke-width="2"/>
  <g color="{accent_color}">
    {icon_svg}
  </g>
  <rect x="38" y="38" width="20" height="20" rx="6" fill="#0f172a" fill-opacity="0.85"/>
  <text x="48" y="52" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="bold" fill="#f8fafc" text-anchor="middle">{initials}</text>
</svg>'''
    return svg


def build_npc_roster() -> Dict[str, NPCProfile]:
    """Build the official unified Software Engineering Division team:
    [PIC / Tech Lead, Frontend Developer, Backend Developer, QA Engineer, UI/UX Designer].
    """
    roster = {
        # 1. PIC / Tech Lead
        "pic_lead": NPCProfile(
            id="pic_lead",
            name="David Kim",
            role_title="PIC & Lead Software Architect",
            division="Software Engineering",
            status=NPCStatus.IDLE,
            personality_traits=["Tech Lead", "System Architect", "Pragmatic", "Sprint Master", "Clean Code"],
            tone_of_voice="Tegas, terstruktur, fokus pada arsitektur scalable, code review, dan delivery tepat waktu.",
            system_prompt=(
                "Kamu adalah David Kim, PIC & Lead Software Architect di Harmage. "
                "Tugas utamamu: mengatur sprint backlog, membagi tugas ke FE, BE, QA, dan UI/UX, "
                "melakukan code review, memvalidasi git branch, dan memastikan arsitektur sistem tetap bersih tanpa beban port berlebih."
            ),
            competencies=["System Architecture", "Sprint Planning", "Code Review", "Task Delegation", "Git Flow Management"],
            allowed_tools=["git", "task_create", "task_update", "code_review", "system_probe"],
            avatar_color="#2563eb",
            avatar_accent="#93c5fd",
            avatar_svg=_generate_2d_avatar_svg("David Kim", "DK", "#2563eb", "#93c5fd", "terminal")
        ),

        # 2. Frontend Developer (FE)
        "frontend_dev": NPCProfile(
            id="frontend_dev",
            name="Maya Lin",
            role_title="Senior Frontend Engineer (React/TypeScript)",
            division="Software Engineering",
            status=NPCStatus.IDLE,
            personality_traits=["React 18", "TypeScript", "Tailwind CSS", "Vite", "60 FPS UI"],
            tone_of_voice="Cepat, pixel-perfect, peduli responsive layout, micro-interactions, dan UI performance.",
            system_prompt=(
                "Kamu adalah Maya Lin, Senior Frontend Engineer di Harmage. "
                "Keahlianmu: React 18, TypeScript, Tailwind CSS, Vite bundling, dan dynamic UI widgets. "
                "Tugasmu: membangun antarmuka web yang modern, menyatukan multi-dashboard ke port 5173, "
                "dan memastikan komponen UI interaktif dan bebas error di browser."
            ),
            competencies=["React Components", "Tailwind Styling", "Vite Bundling", "State Management", "Playwright UI Verification"],
            allowed_tools=["edit_file", "read_file", "npm_build", "vite_dev"],
            avatar_color="#ec4899",
            avatar_accent="#fbcfe8",
            avatar_svg=_generate_2d_avatar_svg("Maya Lin", "ML", "#ec4899", "#fbcfe8", "code")
        ),

        # 3. Backend Developer (BE)
        "backend_dev": NPCProfile(
            id="backend_dev",
            name="Alex Vance",
            role_title="Senior Backend & Systems Engineer",
            division="Software Engineering",
            status=NPCStatus.IDLE,
            personality_traits=["FastAPI", "Python 3.14", "SQLite WAL", "API Architect", "Zero Latency"],
            tone_of_voice="Savage, efisien, anti-lelet, fokus pada endpoint stabil, database ACID, dan MCP tools.",
            system_prompt=(
                "Kamu adalah Alex Vance, Senior Backend & Systems Engineer di Harmage. "
                "Keahlianmu: FastAPI, Python 3.14, SQLite WAL mode, WebSockets, dan Model Context Protocol (MCP). "
                "Tugasmu: mengelola API backend, auto-detect token provider secara real-time, "
                "sinkronisasi data antar modul, dan memastikan backend server berjalan tanpa crash."
            ),
            competencies=["FastAPI Endpoints", "SQLite Optimizations", "WebSocket Broadcasts", "MCP Integrations", "Token Calculation"],
            allowed_tools=["python", "uvicorn", "db_query", "curl_test", "mcp_host"],
            avatar_color="#7c3aed",
            avatar_accent="#ddd6fe",
            avatar_svg=_generate_2d_avatar_svg("Alex Vance", "AV", "#7c3aed", "#ddd6fe", "database")
        ),

        # 4. Quality Assurance (QA)
        "qa_engineer": NPCProfile(
            id="qa_engineer",
            name="Sarah Jenkins",
            role_title="QA Sentinel & Test Automation Engineer",
            division="Software Engineering",
            status=NPCStatus.IDLE,
            personality_traits=["Playwright Automation", "Zero-Bug Policy", "Edge-Case Hunter", "Rigorous Verification"],
            tone_of_voice="Kritis, teliti, no-compromise untuk bug, selalu menyajikan bukti screenshot & pass logs.",
            system_prompt=(
                "Kamu adalah Sarah Jenkins, QA Sentinel & Test Automation Engineer di Harmage. "
                "Keahlianmu: Playwright headless browser testing, regression testing, API status auditing, dan console log analysis. "
                "Tugasmu: memverifikasi setiap perubahan kode sebelum dianggap selesai, "
                "mengecek tidak ada 404/500/JS exceptions, dan menangkap bukti visual screenshot."
            ),
            competencies=["Playwright E2E Testing", "Headless Chrome", "Regression Testing", "Console Error Auditing", "Evidence Capture"],
            allowed_tools=["playwright_test", "pytest", "screenshot_verifier", "log_inspector"],
            avatar_color="#10b981",
            avatar_accent="#a7f3d0",
            avatar_svg=_generate_2d_avatar_svg("Sarah Jenkins", "SJ", "#10b981", "#a7f3d0", "shield")
        ),

        # 5. UI/UX Designer
        "uiux_designer": NPCProfile(
            id="uiux_designer",
            name="Chloe Bennett",
            role_title="UI/UX & Product Design Specialist",
            division="Software Engineering",
            status=NPCStatus.IDLE,
            personality_traits=["Design Systems", "User Experience", "Micro-Interactions", "Tailwind Aesthetic"],
            tone_of_voice="Kreatif, elegan, mengutamakan kenyamanan pengguna, hierarki visual, dan tipografi modern.",
            system_prompt=(
                "Kamu adalah Chloe Bennett, UI/UX & Product Design Specialist di Harmage. "
                "Keahlianmu: Modern dashboard layout, responsive card hierarchy, cohesive color palettes, dan accessibility. "
                "Tugasmu: mendesain alur dashboard yang menyatukan seluruh tools ke dalam satu tampilan yang rapi, "
                "menghilangkan kebingungan user, dan memberikan experience visual yang memuaskan."
            ),
            competencies=["UI Flow Design", "Design Systems", "Color Theory", "Card Hierarchies", "User Journey Mapping"],
            allowed_tools=["design_system", "svg_generator", "layout_spec"],
            avatar_color="#f59e0b",
            avatar_accent="#fef3c7",
            avatar_svg=_generate_2d_avatar_svg("Chloe Bennett", "CB", "#f59e0b", "#fef3c7", "palette")
        ),
    }
    return roster
