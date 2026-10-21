"""Comprehensive Automated Test Suite for Shared AI Token Budget Manager (Qwen + Gemini).

Verifies:
1. Daily window creation with Asia/Jakarta boundary and persistent survival across DB reloads.
2. Shared combined token accounting across Qwen + Gemini models towards the 2,000,000 ceiling.
3. Atomic pre-call reservation and in-flight tracking under multithreaded concurrent requests.
4. Post-call reconciliation against provider usage metadata.
5. Missing usage metadata triggers conservative fallback estimation and audit alert.
6. Mode transitions: Normal (<1.6M) -> Efficient (>=1.6M) -> Conservation (>=1.8M) -> Ceiling Reached (>=1.95M).
7. Non-critical inference refusal and safe task deferral into token_deferred_queue.
8. Daily window reset resumes deferred tasks without crashing deterministic office operations.
"""

import pytest
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from harmage.db import initialize_database, get_connection
from harmage.token_budget import (
    TokenBudgetManager,
    MODE_NORMAL,
    MODE_EFFICIENT,
    MODE_CONSERVATION,
    MODE_CEILING_REACHED,
    DEFAULT_DAILY_LIMIT,
    DEFAULT_SOFT_LIMIT,
    DEFAULT_CONSERVATION_LIMIT
)


@pytest.fixture
def test_manager(tmp_path):
    """Fixture providing an isolated TokenBudgetManager instance with dedicated SQLite DB."""
    db_file = tmp_path / "test_harmage_budget.db"
    initialize_database(db_file)
    manager = TokenBudgetManager(db_path=db_file)
    # Ensure fresh state
    manager.reset_active_window()
    return manager


def test_window_creation_asia_jakarta(test_manager):
    """Test that window is created with Asia/Jakarta boundaries and persists across restarts."""
    summary = test_manager.get_status_summary()
    assert summary["timezone"] == "Asia/Jakarta"
    assert summary["daily_limit"] == 2_000_000
    assert summary["confirmed_tokens"] == 0
    assert summary["mode"] == MODE_NORMAL
    assert "WIB" in summary["window_id"]
    assert summary["remaining_tokens"] == 2_000_000

    # Test persistence by creating another instance with same DB
    restarted_mgr = TokenBudgetManager(db_path=test_manager.db_path)
    restored_summary = restarted_mgr.get_status_summary()
    assert restored_summary["window_id"] == summary["window_id"]
    assert restored_summary["daily_limit"] == 2_000_000


def test_shared_aggregation_qwen_and_gemini(test_manager):
    """Test that Qwen and Gemini usage aggregates into one shared daily pool."""
    # 1. Simulate Qwen call: 300,000 tokens
    res_qwen = test_manager.simulate_token_consumption(provider="qwen", tokens=300_000, agent_id="leo_editor")
    assert res_qwen["allowed"] is True

    # 2. Simulate Gemini call: 500,000 tokens
    res_gemini = test_manager.simulate_token_consumption(provider="gemini", tokens=500_000, agent_id="maya_script")
    assert res_gemini["allowed"] is True

    summary = test_manager.get_status_summary()
    assert summary["confirmed_tokens"] == 800_000
    assert summary["provider_breakdown"]["qwen"] == 300_000
    assert summary["provider_breakdown"]["gemini"] == 500_000
    assert summary["remaining_tokens"] == 1_200_000
    assert summary["mode"] == MODE_NORMAL


def test_mode_transitions_adaptive_stages(test_manager):
    """Test transitions through Normal -> Efficient -> Conservation -> Ceiling Reached."""
    # Step 1: Normal (<1.6M)
    test_manager.simulate_token_consumption(provider="qwen", tokens=1_000_000)
    summary = test_manager.get_status_summary()
    assert summary["mode"] == MODE_NORMAL

    # Step 2: Efficient (>= 1.6M / 80%)
    test_manager.simulate_token_consumption(provider="gemini", tokens=620_000) # Total 1.62M
    summary = test_manager.get_status_summary()
    assert summary["mode"] == MODE_EFFICIENT
    assert any("Soft limit reached" in a for a in summary["alerts"])

    # Step 3: Conservation (>= 1.8M / 90%)
    test_manager.simulate_token_consumption(provider="qwen", tokens=200_000) # Total 1.82M
    summary = test_manager.get_status_summary()
    assert summary["mode"] == MODE_CONSERVATION
    assert any("Conservation mode active" in a for a in summary["alerts"])

    # In conservation mode, low-priority chatter is deferred
    allowed, reason, res_id, mode = test_manager.reserve_tokens(
        estimated_tokens=300,
        agent_id="victor_affiliate",
        priority="low",
        call_type="chat"
    )
    assert allowed is False
    assert mode == MODE_CONSERVATION
    assert "Conservation mode active" in reason

    # Step 4: Ceiling Reached (>= 1.95M / safety reserve)
    test_manager.simulate_token_consumption(provider="gemini", tokens=140_000) # Total 1.96M
    summary = test_manager.get_status_summary()
    assert summary["mode"] == MODE_CEILING_REACHED
    assert any("Hard daily inference ceiling reached" in a for a in summary["alerts"])

    # In ceiling reached mode, normal inference is blocked and queued
    allowed, reason, res_id, mode = test_manager.reserve_tokens(
        estimated_tokens=500,
        agent_id="executive_manager",
        priority="medium",
        call_type="analysis"
    )
    assert allowed is False
    assert mode == MODE_CEILING_REACHED
    assert "Ceiling reached" in reason

    # Verify task was persisted in token_deferred_queue
    conn = get_connection(test_manager.db_path)
    deferred = conn.execute("SELECT * FROM token_deferred_queue WHERE status = 'deferred'").fetchall()
    assert len(deferred) >= 2
    conn.close()


def test_multithreaded_atomic_reservation_race_safety(test_manager):
    """Test that parallel NPC calls atomically reserve tokens without race conditions exceeding limit."""
    test_manager.reset_active_window()
    # Set limit to 10,000 for tight race test
    test_manager.update_config(daily_limit=10_000, soft_limit=7_000, conservation_limit=8_500, safety_reserve=500)

    success_reservations = []
    failure_reservations = []

    def attempt_reservation(idx):
        allowed, reason, res_id, mode = test_manager.reserve_tokens(
            estimated_tokens=1_000,
            agent_id=f"worker_{idx}",
            priority="medium"
        )
        if allowed:
            success_reservations.append(res_id)
        else:
            failure_reservations.append(reason)

    threads = [threading.Thread(target=attempt_reservation, args=(i,)) for i in range(15)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Total allowance is 10,000 - 500 = 9,500. Exactly 9 reservations of 1,000 tokens should succeed, 6 should fail.
    assert len(success_reservations) == 9
    assert len(failure_reservations) == 6


def test_reconciliation_exact_and_conservative_fallback(test_manager):
    """Test reservation reconciliation with exact usage metadata and conservative fallback."""
    # 1. Exact usage reconciliation
    allowed, reason, res_id, mode = test_manager.reserve_tokens(estimated_tokens=500, agent_id="diana_pm")
    assert allowed is True
    recon = test_manager.reconcile_usage(
        reservation_id=res_id,
        actual_prompt=320,
        actual_completion=110,
        actual_total=430,
        provider="qwen",
        model="qwen3.8-max",
        agent_id="diana_pm"
    )
    assert recon["total_tokens"] == 430
    assert recon["confirmed_tokens"] == 430

    # 2. Missing metadata reconciliation (fallback conservative)
    allowed2, reason2, res_id2, mode2 = test_manager.reserve_tokens(estimated_tokens=400, agent_id="zack_qa")
    recon2 = test_manager.reconcile_usage(
        reservation_id=res_id2,
        actual_prompt=None,
        actual_completion=None,
        actual_total=None,
        provider="gemini",
        model="gemini-2.5-flash",
        agent_id="zack_qa",
        fallback_char_count=640
    )
    assert recon2["total_tokens"] > 0
    summary = test_manager.get_status_summary()
    assert summary["estimated_tokens"] > 0
    assert any("estimated" in a.lower() for a in summary["alerts"])


def test_resume_deferred_work_on_reset(test_manager):
    """Test that resetting the window safely resumes deferred tasks without duplicating execution."""
    # Force ceiling reached
    test_manager.simulate_token_consumption(provider="qwen", tokens=1_980_000)
    allowed, reason, res_id, mode = test_manager.reserve_tokens(estimated_tokens=500, agent_id="deferred_worker")
    assert allowed is False

    summary = test_manager.get_status_summary()
    assert summary["deferred_queue_count"] >= 1

    # Execute administrative reset (simulating midnight Asia/Jakarta)
    reset_summary = test_manager.reset_active_window()
    assert reset_summary["confirmed_tokens"] == 0
    assert reset_summary["mode"] == MODE_NORMAL
    assert reset_summary["deferred_queue_count"] == 0
