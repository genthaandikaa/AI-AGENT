"""Scene-by-Scene Visual Production & Asset Manifest Engine for YouTube Long-Form.

Enforces 16:9 landscape aspect ratio (1920x1080).
Produces scene-specific kinetic graphics, scientific diagrams, and motion cards
via FFmpeg, and maintains a strict machine-readable project manifest.
"""

import json
import os
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from harmage.creator.script_engine import SceneStoryboard


PALETTE_CONFIGS = {
    "cosmic_purple": {"bg": "0x0B0A1A", "accent": "0x7C3AED", "card": "0x1E1B4B", "text_primary": "0xFFFFFF", "text_accent": "0xA78BFA"},
    "warning_amber": {"bg": "0x1A0F05", "accent": "0xF59E0B", "card": "0x451A03", "text_primary": "0xFFFFFF", "text_accent": "0xFCD34D"},
    "deep_slate": {"bg": "0x0F172A", "accent": "0x38BDF8", "card": "0x1E293B", "text_primary": "0xFFFFFF", "text_accent": "0x7DD3FC"},
    "ocean_blue": {"bg": "0x031B2E", "accent": "0x0EA5E9", "card": "0x0C4A6E", "text_primary": "0xFFFFFF", "text_accent": "0x38BDF8"},
    "emerald_science": {"bg": "0x022417", "accent": "0x10B981", "card": "0x064E3B", "text_primary": "0xFFFFFF", "text_accent": "0x6EE7B7"}
}


@dataclass
class SceneAssetRecord:
    scene_id: str
    order: int
    stage: str
    duration_sec: float
    visual_type: str
    motion_type: str
    prompt_or_query: str
    provider: str            # 'google_veo' (if authorized), 'ffmpeg_motion_canvas', 'stock_public_domain'
    license_status: str      # 'original_generated', 'public_domain', 'licensed'
    asset_path: str
    resolution: str
    aspect_ratio: str
    qa_status: str           # 'PASSED', 'PENDING', 'FLAGGED'
    technical_metadata: Dict[str, Any]


class SceneRenderer:
    """Renders 16:9 landscape video assets scene-by-scene."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.assets_video_dir = project_dir / "assets" / "video"
        self.assets_images_dir = project_dir / "assets" / "images"
        self.project_meta_dir = project_dir / "project"
        self.renders_dir = project_dir / "renders"

        for d in [self.assets_video_dir, self.assets_images_dir, self.project_meta_dir, self.renders_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.font_file = "C\\:/Windows/Fonts/arialbd.ttf"  # Arial Bold on Windows

    def check_veo_availability(self) -> Dict[str, Any]:
        """Check whether Google Veo / Google Flow is authorized and available.
        Under the strict $0 budget policy, returns False unless owner API keys are configured.
        """
        veo_key = os.getenv("VEO_API_KEY") or os.getenv("FLOW_API_KEY")
        if veo_key:
            return {
                "available": True,
                "provider": "google_veo",
                "quota_status": "configured",
                "note": "Veo API key detected"
            }
        return {
            "available": False,
            "provider": "ffmpeg_motion_canvas",
            "fallback_used": "Option 2: Original 16:9 High-Fidelity Animated Motion Canvas",
            "reason": "Google Veo API key not configured ($0 Cloud Budget Policy). Fallback ladder activated."
        }

    def _clean_text(self, s: str) -> str:
        """Sanitize text strings for safe FFmpeg drawtext filtering on Windows."""
        return (
            s.replace("'", "")
            .replace(":", " - ")
            .replace("%", " persen")
            .replace("|", " - ")
            .replace("\n", " ")
        )

    def render_scene_clip(self, scene: SceneStoryboard, total_scenes: int = 6) -> SceneAssetRecord:
        """Render a single 1920x1080 16:9 animated explanatory clip for this scene."""
        output_filename = f"{scene.scene_id}_{scene.stage}.mp4"
        output_path = self.assets_video_dir / output_filename
        duration = max(3.0, scene.estimated_duration_sec)

        palette = PALETTE_CONFIGS.get(scene.theme_palette, PALETTE_CONFIGS["cosmic_purple"])
        bg_color = palette["bg"]
        accent_color = palette["accent"]
        card_color = palette["card"]

        safe_headline = self._clean_text(scene.headline)
        safe_subtext = self._clean_text(scene.subtext)
        scene_counter = self._clean_text(f"SCENE {scene.order:02d} OF {total_scenes:02d}  -  HARMAGE EXPLAINER")
        diagram_labels = self._clean_text("  -  ".join(scene.diagram_elements[:3]))

        # 16:9 (1920x1080) Video Filter Graph:
        # 1. Base 1920x1080 solid background
        # 2. Top Header Category / Scene Badge: y=70, w=1720, h=60
        # 3. Central Graphic Glass Card: y=160, w=1720, h=780 with subtle accent border
        # 4. Big Headline text: y=230, font size 58
        # 5. Explanatory subtext / diagram card: y=320, font size 32
        # 6. Inner diagram box with key scientific/historical points: y=400
        # 7. Progress line at bottom of card
        vf_filters = [
            f"drawbox=x=100:y=70:w=1720:h=60:color={card_color}@0.9:t=fill",
            f"drawtext=fontfile='{self.font_file}':text='{scene_counter}':fontsize=24:fontcolor={accent_color}:x=140:y=88",
            f"drawbox=x=100:y=150:w=1720:h=780:color={card_color}@0.7:t=fill",
            f"drawbox=x=100:y=150:w=1720:h=780:color={accent_color}@0.4:t=3",
            f"drawtext=fontfile='{self.font_file}':text='{safe_headline}':fontsize=56:fontcolor=0xFFFFFF:x=160:y=230",
            f"drawtext=fontfile='{self.font_file}':text='{safe_subtext}':fontsize=30:fontcolor={accent_color}:x=160:y=320",
            f"drawbox=x=160:y=400:w=1600:h=380:color=0x0F172A@0.85:t=fill",
            f"drawbox=x=160:y=400:w=1600:h=380:color={accent_color}@0.3:t=2",
            f"drawtext=fontfile='{self.font_file}':text='DIAGRAM DAN BUKTI FISIK -':fontsize=24:fontcolor=0x94A3B8:x=200:y=440",
            f"drawtext=fontfile='{self.font_file}':text='{diagram_labels}':fontsize=34:fontcolor=0xFFFFFF:x=200:y=500",
            f"drawbox=x=100:y=926:w=1720:h=4:color={accent_color}:t=fill"
        ]

        vf = ",".join(vf_filters)

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg_color}:s=1920x1080:d={duration:.2f}:r=30",
            "-vf", vf,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-t", f"{duration:.2f}",
            str(output_path)
        ]

        res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if res.returncode != 0 or not output_path.exists():
            raise RuntimeError(f"Scene {scene.scene_id} render failed: {res.stderr}")

        file_size = output_path.stat().st_size
        qa_status = "PASSED" if file_size > 10000 else "FLAGGED"

        record = SceneAssetRecord(
            scene_id=scene.scene_id,
            order=scene.order,
            stage=scene.stage,
            duration_sec=duration,
            visual_type=scene.visual_type,
            motion_type=scene.motion_type,
            prompt_or_query=f"{scene.headline} - {scene.subtext}",
            provider="ffmpeg_motion_canvas",
            license_status="original_generated",
            asset_path=str(output_path),
            resolution="1920x1080",
            aspect_ratio="16:9",
            qa_status=qa_status,
            technical_metadata={
                "file_size_bytes": file_size,
                "fps": 30,
                "codec": "h264",
                "color_palette": scene.theme_palette
            }
        )
        return record

    def build_project_manifest(
        self,
        video_slug: str,
        topic_title: str,
        scene_records: List[SceneAssetRecord]
    ) -> Path:
        """Create machine-readable project manifest JSON."""
        manifest_path = self.project_meta_dir / "manifest.json"
        total_duration = sum(r.duration_sec for r in scene_records)

        manifest = {
            "project_slug": video_slug,
            "topic_title": topic_title,
            "aspect_ratio": "16:9",
            "resolution": "1920x1080",
            "total_scenes": len(scene_records),
            "total_duration_seconds": round(total_duration, 2),
            "veo_check": self.check_veo_availability(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "scenes": [asdict(r) for r in scene_records],
            "qa_summary": {
                "total_scenes": len(scene_records),
                "passed_scenes": sum(1 for r in scene_records if r.qa_status == "PASSED"),
                "all_16x9": True,
                "ready_for_assembly": all(r.qa_status == "PASSED" for r in scene_records)
            }
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest_path
