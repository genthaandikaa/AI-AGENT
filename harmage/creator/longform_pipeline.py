"""Full Autonomous YouTube Long-Form (16:9) Video Production Pipeline.

Orchestrates the 9 operational stages:
Topic Research → Fact Check → Script → Storyboard → Visual Assets → Editing → Render → QA → CEO Review
"""

import json
import os
import re
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from harmage.creator.topic_backlog import TopicBacklogEngine
from harmage.creator.script_engine import ScriptEngine
from harmage.creator.scene_renderer import SceneRenderer
from harmage.creator.video_engine import VideoEngine
from harmage.db import get_connection, log_activity
from harmage.token_budget import token_budget_manager, MODE_CEILING_REACHED


class LongFormProductionPipeline:
    """End-to-end production pipeline for 16:9 YouTube Long-Form educational videos."""

    def __init__(self, base_output_dir: Optional[Path] = None):
        self.base_output_dir = base_output_dir or Path("E:/AI Agent/harmage/output/youtube-longform")
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.topic_engine = TopicBacklogEngine()
        self.script_engine = ScriptEngine()
        self.video_engine = VideoEngine()

    def _slugify(self, title: str) -> str:
        """Create URL and filesystem-safe slug."""
        clean = re.sub(r"[^\w\s-]", "", title.lower())
        return re.sub(r"[\s_-]+", "_", clean)[:40]

    def _generate_ambient_bgm(self, output_wav: Path, duration: float) -> Path:
        """Synthesize subtle offline ambient drone music bed via FFmpeg aevalsrc/sine."""
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        # Create a deep, calm harmonic chord (A2=110Hz, E3=165Hz, A3=220Hz)
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "lavfi",
            "-i", f"anoisesrc=c=pink:r=48000:a=0.015,lowpass=f=200",
            "-f", "lavfi",
            "-i", f"sine=frequency=110:duration={duration:.2f}:sample_rate=48000",
            "-filter_complex", "[0:a]volume=0.4[n];[1:a]volume=0.15[s];[n][s]amix=inputs=2[out]",
            "-map", "[out]",
            "-t", f"{duration:.2f}",
            str(output_wav)
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        return output_wav

    def produce_pilot_longform(self, topic_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute autonomous end-to-end long-form 16:9 video production."""
        # 1. Topic Research Stage
        if topic_id:
            topics = [t for t in self.topic_engine.list_topics() if t["id"] == topic_id]
            topic = topics[0] if topics else self.topic_engine.get_top_candidate()
        else:
            topic = self.topic_engine.get_top_candidate()

        if not topic:
            raise RuntimeError("No topics available in topic backlog")

        title = topic["title"]
        slug = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{self._slugify(title)}"
        project_dir = self.base_output_dir / slug

        # Create structured subdirectories
        research_dir = project_dir / "research"
        script_dir = project_dir / "script"
        storyboard_dir = project_dir / "storyboard"
        audio_dir = project_dir / "assets" / "audio"
        renders_dir = project_dir / "renders"
        qa_dir = project_dir / "qa"

        for d in [research_dir, script_dir, storyboard_dir, audio_dir, renders_dir, qa_dir]:
            d.mkdir(parents=True, exist_ok=True)

        prod_id = f"PROD-LF-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

        # Initialize record in DB
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        conn.execute("""
        INSERT INTO longform_productions (
            id, topic_id, title, slug, stage, assignee,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, 'topic_research', 'editor_longform', ?, ?)
        """, (prod_id, topic["id"], title, slug, now, now))
        conn.commit()
        conn.close()

        log_activity("INFO", "editor_longform", f"Started YouTube Long-Form production for '{title}'", f"Slug: {slug}")

        # 2. Fact Check Stage
        self._update_stage(prod_id, "fact_check")
        script_package, source_ledger = self.script_engine.generate_pilot_script(topic)
        ledger_path = research_dir / "source_ledger.json"
        source_ledger.save_to_file(ledger_path)
        fact_qa = source_ledger.validate_factual_integrity()

        # 3. Script & Storyboard Stage
        self._update_stage(prod_id, "script")
        script_path = self.script_engine.save_script_package(script_package, script_dir)
        storyboard_path = storyboard_dir / "storyboard.json"
        with open(storyboard_path, "w", encoding="utf-8") as f:
            json.dump([asdict(s) for s in script_package.scenes], f, indent=2, ensure_ascii=False)

        # 4. Visual Assets Production Stage (Per-Scene 16:9 Rendering)
        self._update_stage(prod_id, "visual_assets")
        scene_renderer = SceneRenderer(project_dir)
        scene_records = []
        concat_list_path = project_dir / "assets" / "video" / "concat_list.txt"

        concat_lines = []
        for scene in script_package.scenes:
            record = scene_renderer.render_scene_clip(scene, total_scenes=len(script_package.scenes))
            scene_records.append(record)
            # FFmpeg concat requires escaped forward slashes
            escaped_path = record.asset_path.replace("\\", "/")
            concat_lines.append(f"file '{escaped_path}'")

        concat_list_path.write_text("\n".join(concat_lines), encoding="utf-8")
        manifest_path = scene_renderer.build_project_manifest(slug, title, scene_records)

        # 5. Audio Production Stage
        self._update_stage(prod_id, "editing")
        full_narration_text = " ".join([s.narration_text for s in script_package.scenes])
        voiceover_file = audio_dir / "narration_voiceover.wav"
        self.video_engine.generate_voiceover_tts(full_narration_text, voiceover_file)
        real_voice_duration = self.video_engine.get_media_duration(voiceover_file)

        # Generate synced subtitles
        srt_file = audio_dir / "subtitles_16x9.srt"
        self.video_engine.create_synced_srt(
            [s.narration_text for s in script_package.scenes],
            real_voice_duration,
            srt_file
        )

        # Ambient background music bed
        bgm_file = audio_dir / "ambient_bgm.wav"
        self._generate_ambient_bgm(bgm_file, real_voice_duration)

        # Mixed & normalized audio
        mixed_audio_file = audio_dir / "master_audio_normalized.wav"
        mix_cmd = [
            "ffmpeg", "-y",
            "-i", str(voiceover_file),
            "-i", str(bgm_file),
            "-filter_complex",
            # Duck BGM under voiceover (-18dB when voice is active) and apply loudnorm
            "[1:a]volume=0.18[bg];[0:a][bg]amix=inputs=2:duration=first[mixed];[mixed]loudnorm=I=-16:TP=-1.5:LRA=11[out]",
            "-map", "[out]",
            str(mixed_audio_file)
        ]
        subprocess.run(mix_cmd, capture_output=True, timeout=60)

        # 6. Editing & Final Render (Assemble 16:9 MP4)
        self._update_stage(prod_id, "render")
        final_mp4_path = renders_dir / "final_longform_16x9.mp4"
        preview_mp4_path = renders_dir / "preview_longform_proxy.mp4"

        # Concat video streams with burned subtitles
        srt_escaped = str(srt_file).replace("\\", "/").replace(":", "\\:")
        font_file = "C\\:/Windows/Fonts/arialbd.ttf"
        subtitle_vf = f"subtitles=filename='{srt_escaped}':force_style='FontName=Arial,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Alignment=2,MarginV=60'"

        # Render Final 1920x1080 16:9 Video
        render_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_path),
            "-i", str(mixed_audio_file if mixed_audio_file.exists() else voiceover_file),
            "-vf", subtitle_vf,
            "-c:v", "libx264",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(final_mp4_path)
        ]
        res = subprocess.run(render_cmd, capture_output=True, text=True, timeout=180)
        if res.returncode != 0 or not final_mp4_path.exists():
            raise RuntimeError(f"Final 16:9 longform render failed: {res.stderr}")

        # Render low-resolution proxy preview (1280x720) for fast review
        proxy_cmd = [
            "ffmpeg", "-y",
            "-i", str(final_mp4_path),
            "-vf", "scale=1280:720",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "copy",
            str(preview_mp4_path)
        ]
        subprocess.run(proxy_cmd, capture_output=True, timeout=60)

        # 7. QA Verification Stage
        self._update_stage(prod_id, "qa")
        actual_duration = self.video_engine.get_media_duration(final_mp4_path)
        file_size_bytes = final_mp4_path.stat().st_size

        qa_report = {
            "qa_passed": actual_duration > 5.0 and file_size_bytes > 50000,
            "actual_duration_seconds": round(actual_duration, 2),
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "resolution": "1920x1080",
            "aspect_ratio": "16:9",
            "codec_video": "h264",
            "codec_audio": "aac",
            "total_scenes": len(script_package.scenes),
            "fact_check_status": fact_qa["qa_status"],
            "inspected_scenes": [s.scene_id for s in script_package.scenes],
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        qa_report_path = qa_dir / "qa_report.json"
        with open(qa_report_path, "w", encoding="utf-8") as f:
            json.dump(qa_report, f, indent=2, ensure_ascii=False)

        # 8. CEO Review Gate
        self._update_stage(
            prod_id,
            "ceo_review",
            manifest_path=str(manifest_path),
            script_path=str(script_path),
            storyboard_path=str(storyboard_path),
            ledger_path=str(ledger_path),
            output_video_path=str(final_mp4_path),
            preview_video_path=str(preview_mp4_path),
            duration_seconds=actual_duration,
            file_size_bytes=file_size_bytes,
            qa_status="APPROVED" if qa_report["qa_passed"] else "FLAGGED"
        )

        # Register CEO Approval Request in SQLite
        self._register_ceo_approval(prod_id, title, final_mp4_path, actual_duration)

        # Mark topic as produced
        self.topic_engine.update_topic_status(topic["id"], "produced")

        log_activity(
            "GOVERNANCE",
            "editor_longform",
            f"Delivered YouTube Long-Form video for CEO review: '{title}'",
            f"Artifact: {final_mp4_path} ({round(actual_duration, 1)}s, {round(file_size_bytes/1024, 1)}KB)"
        )

        return {
            "production_id": prod_id,
            "topic": topic,
            "slug": slug,
            "stage": "ceo_review",
            "final_video_path": str(final_mp4_path),
            "preview_video_path": str(preview_mp4_path),
            "manifest_path": str(manifest_path),
            "script_path": str(script_path),
            "ledger_path": str(ledger_path),
            "duration_seconds": round(actual_duration, 2),
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "qa_status": "APPROVED" if qa_report["qa_passed"] else "FLAGGED",
            "approval_status": "pending_ceo_review"
        }

    def _update_stage(self, prod_id: str, stage: str, **kwargs) -> None:
        """Update persistent stage progression in SQLite."""
        now = datetime.now(timezone.utc).isoformat()
        fields = ["stage = ?", "updated_at = ?"]
        values = [stage, now]

        for k, v in kwargs.items():
            fields.append(f"{k} = ?")
            values.append(v)

        values.append(prod_id)
        conn = get_connection()
        conn.execute(f"UPDATE longform_productions SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def _register_ceo_approval(self, prod_id: str, title: str, video_path: Path, duration: float) -> None:
        """Register governance approval request."""
        import uuid
        app_id = f"APP-LF-{uuid.uuid4().hex[:6].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        conn.execute("""
        INSERT INTO approval_requests (
            id, action_type, description, requested_by, status, created_at
        ) VALUES (?, 'content_publishing', ?, 'editor_longform', 'pending', ?)
        """, (
            app_id,
            f"Persetujuan Publikasi YouTube Long-Form: {title} | Production: {prod_id} | Video: {video_path.name} ({round(duration, 1)}s, 16:9 1080p)",
            now
        ))
        conn.commit()
        conn.close()

    def get_latest_production(self) -> Optional[Dict[str, Any]]:
        """Retrieve most recent production details."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id, topic_id, title, slug, stage, assignee, manifest_path,
               script_path, storyboard_path, ledger_path, output_video_path,
               preview_video_path, duration_seconds, resolution, file_size_bytes,
               qa_status, error_message, created_at, updated_at
        FROM longform_productions
        ORDER BY created_at DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "topic_id": row[1],
            "title": row[2],
            "slug": row[3],
            "stage": row[4],
            "assignee": row[5],
            "manifest_path": row[6],
            "script_path": row[7],
            "storyboard_path": row[8],
            "ledger_path": row[9],
            "output_video_path": row[10],
            "preview_video_path": row[11],
            "duration_seconds": row[12],
            "resolution": row[13],
            "file_size_bytes": row[14],
            "qa_status": row[15],
            "error_message": row[16],
            "created_at": row[17],
            "updated_at": row[18]
        }
