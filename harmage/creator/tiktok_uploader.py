"""Harmage TikTok Uploader Adapter.

Integrates with the IvanBBaev/tiktok-mcp architecture to upload
videos as drafts or direct posts using plan-then-execute safety.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class TikTokUploader:
    """Manages TikTok video drafting and publishing specs."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("E:/AI Agent/harmage/output")

    def prepare_tiktok_draft_spec(
        self,
        video_path: Path,
        title: str,
        hashtags: Optional[List[str]] = None,
        privacy_level: str = "SELF_ONLY",  # Upload as draft / private review first
    ) -> Dict[str, any]:
        """Prepare a structured upload payload conforming to IvanBBaev/tiktok-mcp schema."""
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        tags = hashtags or ["#shorts", "#harmage", "#tech"]
        full_title = f"{title} {' '.join(tags)}"

        return {
            "platform": "tiktok_mcp",
            "source": "file",
            "file_path": str(video_path),
            "file_size_mb": round(video_path.stat().st_size / (1024 * 1024), 2),
            "post_info": {
                "title": full_title[:150],  # TikTok caption limit
                "privacy_level": privacy_level,
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
                "video_cover_timestamp_ms": 1000,
            },
            "upload_target": "tiktok_upload_video_draft",  # Target inbox draft
            "status": "ready_for_dispatch",
        }
