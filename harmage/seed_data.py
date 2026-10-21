"""Seed database with realistic initial tasks, approvals, meetings, and schedules."""

import json
from datetime import datetime, timezone, timedelta
from harmage.db import get_connection

def seed_harmage_demo():
    conn = get_connection()
    now = datetime.now(timezone.utc)

    # 1. Tasks
    tasks = [
        ("TSK-YT-01", "Render 9:16 Short: Rahasia Cuan TikTok Affiliate", "leo_sparks", "high", "in_progress", "Render vertical video with FFmpeg and subtitles"),
        ("TSK-YT-02", "Riset Topik Long-Form: AI Agent Otomatisasi Bisnis", "ethan_cole", "medium", "completed", "Riset 5 tools AI open-source teratas"),
        ("TSK-TT-01", "Script 3-Second Hook: Jangan Mau Boncos Bayar API", "maya_lin", "critical", "completed", "Naskah viral retensi tinggi 45 detik"),
        ("TSK-AF-01", "Riset 5 Produk Viral Keranjang Kuning Komisi >15%", "victor_sterling", "high", "completed", "Kategori gadget & setup meja kerja"),
        ("TSK-QA-01", "Inspeksi Kualitas Pilot Short (Audio Sync & Typography)", "quality_assurance", "critical", "completed", "QA Checklist verifikasi 1080x1920 passed"),
        ("TSK-MG-01", "Jadwal Rapat Harian Sore & Evaluasi Progres", "executive_manager", "medium", "queued", "Koordinasi standup divisi konten jam 17.00 WIB"),
        ("TSK-SC-01", "Rekap Notulensi Evaluasi Mingguan & Pengarsipan", "executive_secretary", "low", "queued", "Arsip log keputusan CEO"),
        ("TSK-TR-01", "Audit Penggunaan Token LLM ($0 Policy Check)", "treasurer", "high", "completed", "Verifikasi $0.00 spent pada xkiro & Gemini free tier"),
    ]

    for tid, title, assignee, priority, status, desc in tasks:
        conn.execute(
            """
            INSERT OR REPLACE INTO tasks (id, title, description, assignee, priority, status, retry_count, max_retries, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, 3, ?, ?)
            """,
            (tid, title, desc, assignee, priority, status, now.isoformat(), now.isoformat())
        )

    # 2. Approvals
    approvals = [
        ("APR-PUB-01", "PUBLIC_PUBLISH", "Izin Publikasi Draf Video TikTok Affiliate #01 ke Publik", "Diana Prince (PIC)", "pending"),
        ("APR-PUB-02", "PUBLIC_PUBLISH", "Izin Publikasi Draf YouTube Shorts ke Publik", "Leo Sparks", "pending"),
        ("APR-EXP-01", "FINANCIAL_EXPENSE", "Permintaan Pembelian Domain / Cloud (Ditolak Marcus Drake)", "Treasurer", "rejected"),
    ]
    for aid, atype, desc, req_by, status in approvals:
        conn.execute(
            """
            INSERT OR REPLACE INTO approval_requests (id, action_type, description, requested_by, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (aid, atype, desc, req_by, status, now.isoformat())
        )

    # 3. Meetings
    conn.execute(
        """
        INSERT OR REPLACE INTO meetings (id, title, meeting_type, agenda, participants, discussion, action_items, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "MTG-STANDUP-PAGI",
            "Kickoff Operasional Pagi Divisi Konten",
            "internal_evaluation",
            "Sinkronisasi target konten TikTok, Shorts, dan Affiliate produk hari ini.",
            json.dumps(["Alex Vance", "Diana Prince", "Leo Sparks", "Maya Lin", "Victor Sterling"]),
            "Alex: Hari ini kita push 1 shorts dan 1 affiliate video. Leo tolong render lokal FFmpeg, jangan sampe laptop lu overheat. Maya naskahnya jangan garing. Maya: Santai bos, hook gue udah 10/10.",
            json.dumps(["Render pilot short selesai", "Pilih produk affiliate"]),
            now.isoformat()
        )
    )

    # 4. Reports
    conn.execute(
        """
        INSERT OR REPLACE INTO reports (id, report_type, title, summary, metrics, content_markdown, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "REP-OFFICIAL-01",
            "daily_executive",
            "Laporan Operasional Harmage Agents — Divisi Konten & Affiliate",
            "Operasional berjalan 100% mandiri di Windows VPS lokal, $0 pengeluaran, 1 video pilot dirender, 3 produk affiliate siap.",
            json.dumps({"tasks_completed": 4, "tasks_in_progress": 2, "budget_spent": "$0.00", "videos_ready": 1}),
            "### Laporan Ringkasan Eksekutif\n\n- Seluruh infrastruktur lokal berjalan stabil.\n- Video render FFmpeg vertikal 9:16 selesai dan disimpan di `harmage/output/harmage_pilot_short.mp4`.\n- Kebijakan anggaran $0.00 terjaga 100% tanpa biaya cloud.",
            now.isoformat()
        )
    )

    conn.commit()
    conn.close()
    print("Database seeded with rich operational data!")

if __name__ == "__main__":
    seed_harmage_demo()
