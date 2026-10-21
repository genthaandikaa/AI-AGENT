"""Harmage YouTube Studio Local Browser Uploader.

Automates video uploading directly through YouTube Studio Web (studio.youtube.com)
using the local Playwright Chromium browser.
NO Google Cloud Console, NO API Quotas, NO OAuth Client Secrets needed.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class YouTubeBrowserUploader:
    """Manages YouTube uploads via local browser session."""

    def __init__(self, browser_profile_dir: Optional[Path] = None):
        self.profile_dir = browser_profile_dir or Path(
            os.getenv("LOCALAPPDATA", "")
        ) / "hermes" / "browser_profiles" / "youtube_creator"
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def prepare_upload_spec(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: List[str],
        visibility: str = "unlisted",  # 'unlisted', 'private', 'public'
    ) -> Dict[str, any]:
        """Prepare an audited upload specification without sending network requests."""
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        return {
            "platform": "youtube_studio_web",
            "video_path": str(video_path),
            "file_size_mb": round(video_path.stat().st_size / (1024 * 1024), 2),
            "title": title[:100],  # YouTube max 100 chars
            "description": description[:5000],
            "tags": tags[:15],
            "made_for_kids": False,
            "visibility": visibility,
            "browser_profile_path": str(self.profile_dir),
            "status": "ready_for_browser_automation",
        }
