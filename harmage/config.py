"""Harmage Agents Configuration.

Manages filesystem paths, SQLite database settings, and operational limits
for the Harmage virtual enterprise.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database
DB_PATH = DATA_DIR / "harmage_operations.db"

# Executive Manager Limits & Policies
MAX_TASK_RETRIES_DEFAULT = 3
DEFAULT_PRIORITY = "medium"

# Operational Roles
ROLES = {
    "ceo": "CEO / Owner (Human supervisor)",
    "executive_manager": "Executive Manager / Director of Operations (AI)",
    "secretary": "Secretary (Planned)",
    "treasurer": "Treasurer / Finance Manager (Planned)",
    "creator_pm": "Creator Project Manager (Planned)",
    "content_researcher": "Content Researcher (Planned)",
    "scriptwriter": "Scriptwriter (Planned)",
    "video_editor": "Video Editor (Planned)",
    "quality_assurance": "Quality Assurance (Planned)",
    "social_media_specialist": "Publishing & Social Media Specialist (Planned)",
}

# Currently Active Agents (Phase 1)
ACTIVE_ROLES = ["executive_manager"]
