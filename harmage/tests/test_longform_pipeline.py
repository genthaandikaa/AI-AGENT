"""Comprehensive Automated Test Suite for YouTube Long-Form Pipeline.

Tests:
1. Topic Backlog & Transparent Rubric Scoring
2. Factual Integrity & Source Ledger Verification
3. 8-Stage Explainer Script & Storyboard Decomposition
4. Google Veo Availability & Fallback Ladder Verification
5. End-to-End 16:9 Pilot Video Render & Media Validation (ffprobe)
6. CEO Review Approval Gate & Task Registration
"""

import json
import subprocess
from pathlib import Path
from harmage.creator.topic_backlog import TopicBacklogEngine
from harmage.creator.source_ledger import SourceLedger
from harmage.creator.script_engine import ScriptEngine
from harmage.creator.scene_renderer import SceneRenderer
from harmage.creator.longform_pipeline import LongFormProductionPipeline
from harmage.db import get_connection


def test_topic_backlog_and_scoring():
    print("--- 1. Testing Topic Backlog & Rubric Scoring ---")
    engine = TopicBacklogEngine()
    topics = engine.list_topics()
    assert len(topics) >= 6, f"Expected at least 6 topics, got {len(topics)}"

    # Check top candidate
    top = engine.get_top_candidate()
    assert top is not None, "Top candidate should exist"
    assert top["total_score"] > 50.0, f"Expected score > 50.0, got {top['total_score']}"
    assert "scores" in top
    print(f"PASS: Backlog has {len(topics)} topics. Top: '{top['title']}' (Score: {top['total_score']}/70.0)")

    # Test adding new topic
    new_topic = engine.add_topic(
        category="history",
        title="Uji Coba: Arkeologi Bawah Laut Atlantis",
        hook_question="Apakah mitos Atlantis Plato memiliki dasar sejarah geologi nyata?",
        scores={
            "curiosity": 8.5,
            "educational_value": 8.0,
            "evidence_availability": 8.0,
            "visual_storytelling": 9.0,
            "audience_relevance": 8.0,
            "novelty": 7.5,
            "feasibility": 8.5,
            "risk_penalty": 0.5
        },
        editorial_rationale="Klarifikasi ilmiah mitos vs letusan Santorini Minoa.",
        source_links=["https://www.nature.com/articles/santorini_eruption"]
    )
    assert new_topic["total_score"] == round(8.5+8+8+9+8+7.5+8.5-0.5, 2)
    print(f"PASS: Added topic '{new_topic['title']}' with score {new_topic['total_score']}/70.0")


def test_source_ledger_integrity():
    print("\n--- 2. Testing Source Ledger & Factual Integrity ---")
    ledger = SourceLedger("Test Scientific Explainer")
    src = ledger.add_source(
        source_id="SRC-001",
        url="https://nasa.gov/atmosphere",
        publisher_author="NASA",
        evidence_type="space_agency",
        publication_year=2024
    )
    assert src.source_id == "SRC-001"

    # Add valid claim
    claim = ledger.add_claim(
        claim_id="CLM-001",
        scene_id="S001",
        claim_text="Oksigen merupakan gas reaktif yang mengikat kerak bumi.",
        source_ids=["SRC-001"],
        confidence_level="high"
    )
    assert claim.claim_id == "CLM-001"

    qa = ledger.validate_factual_integrity()
    assert qa["passed"] is True, f"QA failed: {qa}"
    print(f"PASS: Source Ledger verified with {qa['total_claims']} claims and status {qa['qa_status']}")


def test_script_engine_storyboard():
    print("\n--- 3. Testing 8-Stage Explainer Script & Storyboard ---")
    engine = ScriptEngine()
    topic = {
        "title": "Apa yang Terjadi Jika Oksigen di Bumi Lenyap Selama 5 Detik?",
        "category": "counterfactual"
    }
    pkg, ledger = engine.generate_pilot_script(topic)
    assert len(pkg.scenes) >= 5, f"Expected at least 5 scenes, got {len(pkg.scenes)}"
    assert pkg.estimated_total_seconds > 20.0
    assert "cold_open" in pkg.stages
    assert "nuance_correction" in pkg.stages

    print(f"PASS: Generated {len(pkg.scenes)} storyboard scenes across 8 stages. Est duration: {pkg.estimated_total_seconds}s")


def test_scene_renderer_and_veo_check():
    print("\n--- 4. Testing Scene Renderer & Veo Fallback Ladder ---")
    test_dir = Path("E:/AI Agent/harmage/output/youtube-longform/_test_sandbox")
    renderer = SceneRenderer(test_dir)

    # Verify honest Veo check
    veo_check = renderer.check_veo_availability()
    print("Veo Check Status:", veo_check)
    assert "available" in veo_check
    if not veo_check["available"]:
        assert veo_check["provider"] == "ffmpeg_motion_canvas"
        print("PASS: Fallback ladder properly active (Option 2: 16:9 Animated Motion Canvas)")


def test_end_to_end_production():
    print("\n--- 5. Testing End-to-End Pilot Long-Form Video Production ---")
    pipeline = LongFormProductionPipeline()

    # Produce pilot longform video using TOPIC-001
    print("Running autonomous long-form video production...")
    result = pipeline.produce_pilot_longform(topic_id="TOPIC-001")

    assert result is not None
    assert result["qa_status"] == "APPROVED"
    assert result["approval_status"] == "pending_ceo_review"

    final_mp4 = Path(result["final_video_path"])
    assert final_mp4.exists(), f"Final video file not found at {final_mp4}"
    assert final_mp4.stat().st_size > 100000, f"Video size too small: {final_mp4.stat().st_size} bytes"

    # Validate with ffprobe
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name,duration",
        "-of", "json",
        str(final_mp4)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    probe_data = json.loads(res.stdout)
    v_stream = probe_data["streams"][0]

    width = int(v_stream["width"])
    height = int(v_stream["height"])
    duration = float(v_stream["duration"])
    codec = v_stream["codec_name"]

    print(f"PASS: Rendered MP4 validated: {width}x{height} (Aspect ratio: {width/height:.2f}), Duration: {duration:.2f}s, Codec: {codec}")
    assert width == 1920, f"Expected width 1920, got {width}"
    assert height == 1080, f"Expected height 1080, got {height}"
    assert codec == "h264", f"Expected h264, got {codec}"
    assert duration > 10.0, f"Expected duration > 10.0s, got {duration}"

    # Check database approval request
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, status FROM approval_requests WHERE requested_by = 'editor_longform' ORDER BY created_at DESC LIMIT 1")
    app_row = cursor.fetchone()
    conn.close()

    assert app_row is not None, "CEO approval request must be registered in SQLite"
    print(f"PASS: CEO Governance approval registered: ID {app_row[0]} | Desc: '{app_row[1]}' | Status: {app_row[2]}")


if __name__ == "__main__":
    test_topic_backlog_and_scoring()
    test_source_ledger_integrity()
    test_script_engine_storyboard()
    test_scene_renderer_and_veo_check()
    test_end_to_end_production()
    print("\n==========================================")
    print("ALL LONG-FORM PIPELINE TESTS PASSED 100%!")
    print("==========================================")
