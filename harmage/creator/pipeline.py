"""Production Pipeline orchestrating Harmage Creator Division."""

import json
from pathlib import Path
from typing import Dict, List, Optional
from harmage.creator.video_engine import VideoEngine
from harmage.models import TaskPriority, TaskStatus
from harmage.task_manager import TaskManager


class VideoProductionPipeline:
    def __init__(self, task_manager: Optional[TaskManager] = None):
        self.task_manager = task_manager or TaskManager()
        self.video_engine = VideoEngine()

    def produce_short_video(
        self,
        topic: str,
        headline: str,
        script_sentences: List[str],
        output_name: str = "harmage_pilot_short.mp4",
    ) -> Dict[str, any]:
        """Execute end-to-end local automated video creation pipeline."""
        output_dir = Path("E:/AI Agent/harmage/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        voiceover_file = output_dir / f"{Path(output_name).stem}_voice.wav"
        srt_file = output_dir / f"{Path(output_name).stem}_subtitles.srt"
        final_video_file = output_dir / output_name

        full_text = " ".join(script_sentences)

        # 1. Generate Voiceover TTS
        self.video_engine.generate_voiceover_tts(full_text, voiceover_file)
        duration = self.video_engine.get_media_duration(voiceover_file)

        # 2. Generate Timed Subtitles (.srt)
        self.video_engine.create_synced_srt(script_sentences, duration, srt_file)

        # 3. Render Final Video (1080x1920 9:16)
        self.video_engine.render_short_video(
            voiceover_path=voiceover_file,
            srt_path=srt_file,
            hook_headline=headline,
            output_mp4=final_video_file,
        )

        # 4. QA Verification
        file_size_kb = final_video_file.stat().st_size / 1024
        qa_passed = file_size_kb > 10 and duration > 1.0

        return {
            "topic": topic,
            "headline": headline,
            "duration_seconds": round(duration, 2),
            "file_size_kb": round(file_size_kb, 1),
            "output_path": str(final_video_file),
            "voiceover_path": str(voiceover_file),
            "srt_path": str(srt_file),
            "qa_passed": qa_passed,
        }

    def run_full_cycle(self) -> Dict[str, any]:
        """Execute creator production run and return task report."""
        import uuid
        task_id = f"TASK-CR-{uuid.uuid4().hex[:6].upper()}"
        res = self.produce_short_video(
            topic="Harmage AI Autonomous Operations",
            headline="AI OFFICE RUNNING 100% OFFLINE",
            script_sentences=[
                "Kantor virtual Harmage kini beroperasi penuh secara mandiri.",
                "Sepuluh agen AI aktif bekerja di divisinya masing-masing.",
                "Seluruh rendering video dan kontrol token diawasi secara ketat no cap."
            ],
            output_name=f"creator_cycle_{task_id}.mp4"
        )
        res["task_id"] = task_id
        return res


# Backward-compatible alias for server endpoints
CreatorPipeline = VideoProductionPipeline
