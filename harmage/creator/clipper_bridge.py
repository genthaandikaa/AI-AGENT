"""Bridge integrating the user's existing local Cheat Clip PRO video clipper into Harmage Agents."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add cheat-clip-pro to sys.path
CLIPPER_DIR = Path(r"E:\cheat-clip-pro")
if str(CLIPPER_DIR) not in sys.path and CLIPPER_DIR.exists():
    sys.path.append(str(CLIPPER_DIR))

try:
    from backend.video_engine import (
        get_video_file_metadata,
        render_clip_to_mp4,
        is_valid_mp4,
        detect_hardware_support
    )
    CLIPPER_AVAILABLE = True
except Exception as e:
    CLIPPER_AVAILABLE = False
    CLIPPER_ERROR = str(e)


class ClipperBridge:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(r"E:\AI Agent\harmage\output\clipped_renders")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def inspect_source(self, video_path: str) -> Dict[str, Any]:
        """Inspect video file metadata using the clipper's engine."""
        if not CLIPPER_AVAILABLE:
            return {"error": "Clipper engine unavailable"}
        return get_video_file_metadata(video_path)

    def produce_clip(
        self,
        source_video_path: str,
        output_filename: str,
        aspect_ratio: str = "9:16",
        clip_duration: float = 15.0,
        title_text: Optional[str] = None,
        background_style: str = "black"
    ) -> Dict[str, Any]:
        """Clip and render a video using cheat-clip-pro engine."""
        if not CLIPPER_AVAILABLE:
            raise RuntimeError(f"Clipper engine import failed: {CLIPPER_ERROR}")

        out_path = self.output_dir / output_filename
        render_clip_to_mp4(
            video_path=source_video_path,
            output_mp4_path=str(out_path),
            aspect_ratio=aspect_ratio,
            clip_duration=clip_duration,
            title_text=title_text,
            background_style=background_style
        )

        valid = is_valid_mp4(out_path)
        size_bytes = out_path.stat().st_size if out_path.exists() else 0

        return {
            "success": valid,
            "output_path": str(out_path),
            "file_size_bytes": size_bytes,
            "file_size_mb": round(size_bytes / (1024 * 1024), 2),
            "duration": clip_duration,
            "aspect_ratio": aspect_ratio,
            "title": title_text
        }
