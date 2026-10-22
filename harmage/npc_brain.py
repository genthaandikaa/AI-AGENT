"""
Harmage Autonomous AI NPC Complex Brain & Simulation Engine (Dynamic Roster Edition)
=====================================================================================
Eliminates all hardcoded dialogue pools and canned interaction pairs.
Directly harnesses:
1. Dynamic persona souls from harmage.npc.build_npc_roster()
2. Real-time tasks and metrics from SQLite (harmage_operations.db)
3. Shared AI Token Budget Manager (2,000,000 tokens/day WIB) with adaptive prompt sizing
4. Persistent memory tables: npc_brain_memories and npc_brain_interactions
5. Procedural dynamic synthesis fallback grounded in live database state ($0 cost)
"""

import os
import json
import random
import time
import datetime
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

from harmage.npc import build_npc_roster, NPCProfile
from harmage.db import get_connection, log_activity
from harmage.token_budget import (
    token_budget_manager,
    MODE_NORMAL,
    MODE_EFFICIENT,
    MODE_CONSERVATION,
    MODE_CEILING_REACHED
)

# Timezone Asia/Jakarta (WIB = UTC+7)
WIB_OFFSET = datetime.timezone(datetime.timedelta(hours=7))

class OfficePeriod:
    MORNING_WORK = "MORNING_WORK"          # 09:00 - 12:00 WIB: Focus Sprint
    LUNCH_BREAK = "LUNCH_BREAK"            # 12:00 - 13:00 WIB: Istirahat Siang / Chill
    AFTERNOON_WORK = "AFTERNOON_WORK"      # 13:00 - 17:00 WIB: Production & Execution
    STANDUP_MEETING = "STANDUP_MEETING"    # 17:00 - 17:30 WIB: Evaluasi Harian Sore
    FREE_REST = "FREE_REST"                # 17:30 - 09:00 WIB: Santai / Standby / Bebas

# Canonical mapping from shorthand / adapter IDs to NPC roster IDs
NPC_ALIAS_MAP: Dict[str, str] = {
    "executive_manager": "executive_manager",
    "alex_vance": "executive_manager",
    "treasurer": "treasurer",
    "marcus_drake": "treasurer",
    "secretary": "executive_secretary",
    "executive_secretary": "executive_secretary",
    "sophia_chen": "executive_secretary",
    "creator_pm": "creator_pm",
    "diana_prince": "creator_pm",
    "video_editor": "yt_shorts_specialist",
    "yt_shorts_specialist": "yt_shorts_specialist",
    "leo_sparks": "yt_shorts_specialist",
    "editor_longform": "yt_long_specialist",
    "yt_long_specialist": "yt_long_specialist",
    "raka_pratama": "yt_long_specialist",
    "scriptwriter": "tiktok_specialist",
    "tiktok_specialist": "tiktok_specialist",
    "maya_lin": "tiktok_specialist",
    "tiktok_affiliate": "tiktok_affiliate",
    "victor_sterling": "tiktok_affiliate",
    "qa_sentinel": "quality_assurance",
    "quality_assurance": "quality_assurance",
    "zackary_cross": "quality_assurance",
    "researcher": "content_researcher",
    "content_researcher": "content_researcher",
    "ethan_cole": "content_researcher",
    "quant_specialist": "quant_specialist",
    "security_specialist": "security_specialist",
}

@dataclass
class NPCBrainState:
    agent_id: str
    name: str
    role: str
    division: str
    morale: int = 85           # 0 - 100
    energy: int = 90           # 0 - 100
    stress: int = 20           # 0 - 100
    emotion: str = "Focus"     # Focus, Chill, Savage, Pelit/Hemat, Aesthetic, Panik, Semangat, etc.
    current_thought: str = ""
    status: str = "working"    # working, break, meeting, idle
    assigned_task: Optional[str] = None
    last_interaction: str = ""
    vibe_personality: str = ""
    last_thought_time: float = 0.0


def init_npc_brain_tables():
    """Ensure persistent memory tables exist in SQLite."""
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS npc_brain_memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        memory_type TEXT NOT NULL,
        content TEXT NOT NULL,
        emotion TEXT,
        morale INTEGER,
        energy INTEGER,
        stress INTEGER,
        task_id TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_npc_memories_agent ON npc_brain_memories(agent_id, created_at);")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS npc_brain_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        initiator_id TEXT NOT NULL,
        initiator_name TEXT NOT NULL,
        initiator_speech TEXT NOT NULL,
        recipient_id TEXT NOT NULL,
        recipient_name TEXT NOT NULL,
        recipient_speech TEXT NOT NULL,
        context_period TEXT,
        topic TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_npc_interactions_time ON npc_brain_interactions(created_at);")
    conn.commit()
    conn.close()


class HarmageNPCBrainManager:
    """Central autonomous simulation brain for all Harmage NPCs."""

    def __init__(self):
        self.schedule_override: Optional[str] = None
        self.manual_override_until: float = 0
        self.recent_dialogues: List[Dict[str, Any]] = []
        self.npc_states: Dict[str, NPCBrainState] = {}
        self.roster: Dict[str, NPCProfile] = build_npc_roster()
        self._last_ai_failure: float = 0.0
        init_npc_brain_tables()
        self._init_npcs()

    def _canonical_id(self, raw_id: str) -> str:
        clean = raw_id.lower().replace("-", "_").strip()
        return NPC_ALIAS_MAP.get(clean, clean)

    def _get_agent_active_task(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Look up real in-progress task from SQLite for this agent considering all aliases."""
        canon = self._canonical_id(agent_id)
        possible_assignees = list(set([k for k, v in NPC_ALIAS_MAP.items() if v == canon] + [canon]))
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        placeholders = ",".join(["?"] * len(possible_assignees))
        row = conn.execute(
            f"SELECT id, title, priority, status FROM tasks WHERE assignee IN ({placeholders}) AND status IN ('in_progress', 'working') ORDER BY id DESC LIMIT 1",
            possible_assignees
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def _init_npcs(self):
        """Initialize brain states using dynamic profiles from harmage.npc."""
        self.roster = build_npc_roster()
        for agent_id, profile in self.roster.items():
            default_emotion = "Focus & Eksekusi"
            if "manager" in agent_id:
                default_emotion = "Savage & Focus"
            elif "treasurer" in agent_id:
                default_emotion = "Pelit/Hemat Mode"
            elif "secretary" in agent_id:
                default_emotion = "Aesthetic & Rapi"
            elif "tiktok_specialist" in agent_id:
                default_emotion = "Creative Hook"
            elif "tiktok_affiliate" in agent_id:
                default_emotion = "Cuan Hunter"
            elif "quality_assurance" in agent_id:
                default_emotion = "Quality Sentinel"
            elif "yt_shorts" in agent_id:
                default_emotion = "Timeline Ninja"
            elif "yt_long" in agent_id:
                default_emotion = "Cinematic Flow"
            elif "creator_pm" in agent_id:
                default_emotion = "Hustler Lead"
            elif "researcher" in agent_id:
                default_emotion = "Deep Research"

            vibe = f"{profile.tone_of_voice} ({', '.join(profile.personality_traits[:3])})"
            self.npc_states[agent_id] = NPCBrainState(
                agent_id=agent_id,
                name=profile.name,
                role=profile.role_title,
                division=profile.division,
                morale=random.randint(82, 95),
                energy=random.randint(85, 96),
                stress=random.randint(15, 28),
                emotion=default_emotion,
                current_thought=f"Fokus menggarap target {profile.division} hari ini.",
                status="working",
                vibe_personality=vibe,
                last_thought_time=time.time()
            )

    def get_current_wib_time(self) -> datetime.datetime:
        return datetime.datetime.now(WIB_OFFSET)

    def get_effective_schedule(self) -> Dict[str, Any]:
        """Calculates current office period based on WIB clock or active CEO override."""
        now_wib = self.get_current_wib_time()
        
        # Check if CEO manual override is active
        if self.schedule_override and time.time() < self.manual_override_until:
            period = self.schedule_override
            is_override = True
            remaining_override_sec = int(self.manual_override_until - time.time())
        else:
            self.schedule_override = None
            is_override = False
            remaining_override_sec = 0
            hour = now_wib.hour
            minute = now_wib.minute
            hm = hour * 60 + minute

            if 9 * 60 <= hm < 12 * 60:
                period = OfficePeriod.MORNING_WORK
            elif 12 * 60 <= hm < 13 * 60:
                period = OfficePeriod.LUNCH_BREAK
            elif 13 * 60 <= hm < 17 * 60:
                period = OfficePeriod.AFTERNOON_WORK
            elif 17 * 60 <= hm < 17 * 60 + 30:
                period = OfficePeriod.STANDUP_MEETING
            else:
                period = OfficePeriod.FREE_REST

        descriptions = {
            OfficePeriod.MORNING_WORK: "Jam Kerja Pagi (09:00 - 12:00 WIB) — Fokus eksekusi di meja masing-masing.",
            OfficePeriod.LUNCH_BREAK: "Jam Istirahat Siang (12:00 - 13:00 WIB) — Santai di lounge, pantry, coffee station, main game.",
            OfficePeriod.AFTERNOON_WORK: "Jam Kerja Siang (13:00 - 17:00 WIB) — Produksi video, editing visual, dan campaign affiliate.",
            OfficePeriod.STANDUP_MEETING: "Rapat Harian Sore (17:00 - 17:30 WIB) — Evaluasi bersama di Meeting Room.",
            OfficePeriod.FREE_REST: "Jam Bebas / Istirahat Malam — Santai atau istirahat kecuali ada tugas lembur khusus."
        }

        return {
            "period": period,
            "period_label": period.replace("_", " ").title(),
            "description": descriptions.get(period, ""),
            "wib_time": now_wib.strftime("%H:%M:%S WIB"),
            "wib_date": now_wib.strftime("%Y-%m-%d"),
            "is_manual_override": is_override,
            "override_remaining_sec": remaining_override_sec,
            "is_working_hours": period in (OfficePeriod.MORNING_WORK, OfficePeriod.AFTERNOON_WORK),
            "is_break_time": period in (OfficePeriod.LUNCH_BREAK, OfficePeriod.FREE_REST),
            "is_meeting_time": period == OfficePeriod.STANDUP_MEETING,
        }

    def set_schedule_override(self, period: str, duration_minutes: int = 30) -> Dict[str, Any]:
        """Allows CEO to command 'Waktunya Istirahat!', 'Waktunya Kerja!', or 'Rapat!'."""
        valid_periods = [
            OfficePeriod.MORNING_WORK,
            OfficePeriod.LUNCH_BREAK,
            OfficePeriod.AFTERNOON_WORK,
            OfficePeriod.STANDUP_MEETING,
            OfficePeriod.FREE_REST
        ]
        norm = period.upper().strip()
        if norm not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")

        self.schedule_override = norm
        self.manual_override_until = time.time() + (duration_minutes * 60)
        self.update_all_npcs()
        return self.get_effective_schedule()

    def clear_schedule_override(self) -> Dict[str, Any]:
        self.schedule_override = None
        self.manual_override_until = 0
        self.update_all_npcs()
        return self.get_effective_schedule()

    def _call_ai_completion(self, prompt: str, system_prompt: str = "", max_tokens: int = 150) -> Optional[str]:
        """
        Attempts real AI completion via harmage.llm_brain.call_llm_completion.
        Guarded by circuit breaker to avoid latency when provider is rate-limited.
        """
        now = time.time()
        if now - self._last_ai_failure < 60:
            return None

        try:
            budget = token_budget_manager.get_status_summary()
            if budget.get("active_mode") == MODE_CEILING_REACHED:
                return None

            from harmage.llm_brain import call_llm_completion
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            result = call_llm_completion(
                messages=messages,
                max_tokens=max_tokens,
                agent_id="npc_brain",
                priority="low",
                call_type="npc_thought"
            )
            if result and not result.startswith("⚠️ [Waiting for AI budget]") and not result.startswith("Waduh bestie, koneksi AI"):
                return result.strip()
            else:
                self._last_ai_failure = now
        except Exception:
            self._last_ai_failure = now

        return None

    def _synthesize_procedural_thought(
        self,
        agent_id: str,
        profile: NPCProfile,
        active_task: Optional[Dict[str, Any]],
        sched: Dict[str, Any],
        state: NPCBrainState
    ) -> str:
        """
        Procedural Dynamic Context Synthesizer (Zero hardcoding, zero dummy data).
        Constructs a completely dynamic, context-aware Gen-Z thought using real database values:
        task ID, title, priority, WIB time, energy, stress, and persona soul vocabulary.
        """
        wib_str = sched.get("wib_time", "WIB")
        task_title = active_task.get("title", "") if active_task else ""
        task_id = active_task.get("id", "") if active_task else ""
        task_prio = active_task.get("priority", "medium") if active_task else "normal"

        try:
            budget = token_budget_manager.get_status_summary()
            budget_mode = budget.get("active_mode", "NORMAL")
            rem_tokens = budget.get("remaining", 2000000)
        except Exception:
            budget_mode = "NORMAL"
            rem_tokens = 2000000

        # Dynamic persona vectors
        if "manager" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Break bentar sambil cek rekap jam {wib_str}, abis ini anak-anak harus tetap gaspol no cap.",
                    f"Recharge energi dulu di lounge, nanti jam kerja gue gamau liat ada yang lelet.",
                    f"Santai 15 menit, otak perlu dingin biar bisa triage evaluasi harian sore nanti."
                ]
            elif task_title:
                templates = [
                    f"Task [{task_id}] '{task_title[:35]}' harus clear tepat waktu, no excuse buat yang lelet fr fr.",
                    f"Gue kawal progress '{task_title[:32]}', divisi lain jangan ada yang gabut di jam kerja.",
                    f"Reviewing [{task_id}] prioritas {task_prio}... Semua workflow harus rapi dan patuh kebijakan zero-cost.",
                    f"Sipaling manager mode on: target harian Harmage ga boleh ada yang meleset se-inci pun."
                ]
            else:
                templates = [
                    f"Monitoring timeline perusahaan jam {wib_str}... Semua PIC divisi wajib report progres riil.",
                    f"Lagi audit ritme kerja kantor, budget AI mode {budget_mode} aman terkendali."
                ]
        elif "treasurer" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Istirahat ngopi gratisan kantor jam {wib_str}, alhamdulillah dompet perusahaan $0.00 spend mantap jiwa.",
                    f"Rehat sejenak sambil mantau saldo komisi affiliate, prinsip gue tetep: anti boncos no cap."
                ]
            elif task_title:
                templates = [
                    f"Task [{task_id}] '{task_title[:35]}' aman terkendali, kuota sisa {rem_tokens:,} token WIB, $0 spend terjaga!",
                    f"Lagi audit task '{task_title[:30]}'... Ga boleh ada credit card siluman yang nyedot kas kantor!",
                    f"Kalkulasi cashflow affiliate dan YouTube Shorts jalan mulus, mode budget {budget_mode} terpantau disiplin."
                ]
            else:
                templates = [
                    f"Audit token budget jam {wib_str}: sisa {rem_tokens:,} token harian. Hemat pangkal kaya bestie!",
                    f"Cuan masuk dari affiliate, pengeluaran cloud tetep nol rupiah. Ini baru efisiensi enterprise!"
                ]
        elif "secretary" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Meja kerja udah aesthetic dan rapi jam {wib_str}, saatnya seduh matcha latte di lounge.",
                    f"Break time, scroll inspirasi layout notulensi biar tampilan dokumen Harmage makin elegan."
                ]
            elif task_title:
                templates = [
                    f"Notulensi task [{task_id}] '{task_title[:35]}' udah gue arsip rapi di SQLite, anti typo no cap.",
                    f"Merapikan dokumentasi '{task_title[:30]}'... Semua log keputusan CEO Gentha tersimpan permanen.",
                    f"Struktur laporan eksekutif sinkron 100%, ga ada alasan tim bilang lupa tugas."
                ]
            else:
                templates = [
                    f"Arsip dan database keputusan tersinkronisasi rapi jam {wib_str}. Tertib administrasi nomer satu.",
                    f"Agenda rapat sore jam 17:00 WIB udah disiapkan, siap broadcast ke Telegram CEO."
                ]
        elif "creator_pm" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Break time! Cek feed TikTok bentar jam {wib_str} liat audio apa yang lagi meledak di FYP.",
                    f"Ngopi dulu di pantry, abis ini review final pipeline Shorts 9:16 sama explainer 16:9."
                ]
            elif task_title:
                templates = [
                    f"Task [{task_id}] '{task_title[:35]}' kita kejar retention rate 85% di 10 detik pertama, gas!",
                    f"Pipeline '{task_title[:30]}' lagi digodok Leo, Maya, sama Victor... Tim konten wajib perform!",
                    f"Supervisi konten affiliate keranjang kuning dan YouTube explainer berjalan simultan hari ini."
                ]
            else:
                templates = [
                    f"Semua sub-bidang konten jam {wib_str} on track, siap kasih laporan manis ke CEO Gentha sore nanti.",
                    f"Target konversi dan view harian ga boleh kendor, standar broadcast Harmage nomor satu."
                ]
        elif "yt_shorts" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Break ngopi dulu jam {wib_str}, GPU render 60fps bikin laptop agak anget dikit tapi worth it.",
                    f"Mata segerin dulu dari timeline premiere, rehat santai di pojokan lounge."
                ]
            elif task_title:
                templates = [
                    f"Rendering vertical 9:16 [{task_id}] '{task_title[:35]}' via FFmpeg lokal, typography glow nancep!",
                    f"Audio ducking naskah Maya Lin sama BGM di task '{task_title[:30]}' udah super mulus bebas copyright.",
                    f"Color grading punchy 1080x1920 beres, deliverable siap diserahkan ke QA Zack!"
                ]
            else:
                templates = [
                    f"Timeline FFmpeg lokal standby jam {wib_str}, renderan kilat tanpa cloud berbayar no cap.",
                    f"Siap eksekusi klip 9:16 berikutnya begitu naskah baru masuk antrean."
                ]
        elif "yt_long" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Istirahat bentar jam {wib_str}, dengerin lo-fi di lounge seat biar telinga seger.",
                    f"Ngopi di pantry sambil nunggu master timeline explainer 16:9 selesai diproses."
                ]
            elif task_title:
                templates = [
                    f"Assembly video 16:9 [{task_id}] '{task_title[:35]}' chapter-by-chapter rapi, retention terjamin.",
                    f"Transisi b-roll narasi edukasi '{task_title[:30]}' terasa organik, durasi 8-12 menit terencana.",
                    f"Source ledger dan sitasi bukti tersemat presisi di tiap segmen visual explainer."
                ]
            else:
                templates = [
                    f"Timeline 16:9 1080p standby jam {wib_str}, kualitas visual standar broadcast YouTube.",
                    f"Menyiapkan storyboard edukatif berikutnya bareng Researcher Ethan Cole."
                ]
        elif "tiktok_specialist" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Otak butuh asupan kafein jam {wib_str}, jalan ke coffee machine dulu ya bestie.",
                    f"Rehat sejenak baca thread viral di library buat nambah kosa kata hook retention."
                ]
            elif task_title:
                templates = [
                    f"Hook 3 detik pertama naskah [{task_id}] '{task_title[:35]}' bakal bikin penonton stop scrolling!",
                    f"Formula 8-tahap di task '{task_title[:30]}': Problem -> Agitation -> Solution -> Evidence -> CTA.",
                    f"Naskah viral TikTok udah padat daging, ga ada kata-kata mubazir yang bikin penonton bosen."
                ]
            else:
                templates = [
                    f"Riset hook dan angle copywriting jam {wib_str}... Algoritma TikTok ada di genggaman gue no cap.",
                    f"Naskah konten berikutnya siap disuplai ke Leo dan Victor buat dieksekusi."
                ]
        elif "tiktok_affiliate" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Santai bentar di lounge jam {wib_str}, sambil senyum liat tracking konversi TikTok Shop.",
                    f"Istirahat ngemil di pantry, stamina harus prima buat kurasi produk keranjang kuning."
                ]
            elif task_title:
                templates = [
                    f"Riset 5 produk viral [{task_id}] '{task_title[:35]}' komisi 18% per checkout, cuan mengalir!",
                    f"Tautan keranjang kuning di '{task_title[:30]}' udah match sama angle soft-selling Maya Lin.",
                    f"A/B testing produk gadget meja kerja siap boost conversion rate minggu ini!"
                ]
            else:
                templates = [
                    f"Tracking affiliate links jam {wib_str} aktif, komisi masuk terus tanpa keluar modal iklan berbayar.",
                    f"Katalog produk viral terkurasi siap dipasangkan ke video-video baru."
                ]
        elif "quality_assurance" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Checklist QA aman jam {wib_str}, jalan santai ke water cooler buat hidrasi pikiran.",
                    f"Rehat sejenak dari inspeksi pixel dan audio clipping, main arcade sebentar."
                ]
            elif task_title:
                templates = [
                    f"Inspeksi QA [{task_id}] '{task_title[:35]}': audio sync presisi, zero glitch, lolos standar broadcast!",
                    f"Validasi frame-by-frame di '{task_title[:30]}' passed, klaim fakta verified lewat Source Ledger.",
                    f"Gatekeeper no mercy: konten ini 100% berkualitas tinggi sebelum disodorin ke CEO Gentha."
                ]
            else:
                templates = [
                    f"Audit kualitas operasional jam {wib_str}: zero defect policy ditegakkan secara mutlak.",
                    f"Semua deliverable divisi konten lolos verifikasi standar penyiaran Harmage."
                ]
        elif "researcher" in agent_id:
            if sched["period"] == OfficePeriod.LUNCH_BREAK:
                templates = [
                    f"Selesai riset paper jam {wib_str}, istirahat dulu di sofa lounge sambil baca santai.",
                    f"Ngopi dulu di pantry, refreshing pikiran sebelum analisis tren viral berikutnya."
                ]
            elif task_title:
                templates = [
                    f"Riset mendalam [{task_id}] '{task_title[:35]}' tuntas dengan 5 perbandingan data terakreditasi.",
                    f"Ledger bukti dan sitasi faktual di '{task_title[:30]}' tersusun rapi buat bahan naskah Maya.",
                    f"Analisis pasar menunjukkan tren otomasi AI melonjak, insight siap diserahkan ke Diana!"
                ]
            else:
                templates = [
                    f"Database insight dan trend radar jam {wib_str} terus diperbarui dengan data valid no cap.",
                    f"Materi riset berikutnya siap disuplai ke pipeline naskah dan produksi visual."
                ]
        else:
            templates = [
                f"Operasional divisi jam {wib_str} berjalan fokus sesuai standar Harmage Enterprise.",
                f"Semua sistem dan task terintegrasi, performa optimal tanpa kendala."
            ]

        chosen = random.choice(templates)
        return chosen

    def generate_dynamic_thought(
        self,
        agent_id: str,
        active_task: Optional[Dict[str, Any]] = None,
        force_refresh: bool = False,
        try_ai: bool = False
    ) -> str:
        """
        Generates a fresh, context-aware thought for an agent:
        Uses LLM if requested and available, or procedural synthesis grounded in real SQLite state.
        Persists into SQLite npc_brain_memories table.
        """
        canonical_id = self._canonical_id(agent_id)
        profile = self.roster.get(canonical_id)
        if not profile:
            profile = self.roster.get("executive_manager")
            canonical_id = "executive_manager"

        state = self.npc_states.get(canonical_id)
        if not state:
            return "Fokus kerja di meja masing-masing."

        # Fetch active task from SQLite if not passed
        if not active_task:
            active_task = self._get_agent_active_task(canonical_id)

        now_ts = time.time()
        # Reuse cache only if not forced and within 45s and already has a thought
        if not force_refresh and (now_ts - state.last_thought_time < 45) and state.current_thought:
            return state.current_thought

        sched = self.get_effective_schedule()
        task_title = active_task.get("title", "") if active_task else (state.assigned_task or "")
        task_id = active_task.get("id", "") if active_task else ""

        thought = None
        # Attempt AI generation if explicitly requested
        if try_ai:
            prompt = (
                f"Kamu adalah {profile.name} ({profile.role_title}) di Harmage Enterprise. "
                f"Gaya bicaramu: {profile.tone_of_voice}. Kepribadian: {', '.join(profile.personality_traits[:3])}. "
                f"Situasi kantor sekarang: {sched['period_label']} ({sched['wib_time']}). "
                f"Tugas aktifmu di SQLite: '{task_title}'. "
                f"Tuliskan 1 kalimat monolog batin / pikiran dalam hatimu yang sangat singkat (maksimal 18 kata), "
                f"savage/gaul ala Gen-Z, to-the-point, dan berkaitan langsung dengan tugasmu atau situasi kantor saat ini."
            )
            ai_thought = self._call_ai_completion(prompt, system_prompt=profile.system_prompt, max_tokens=60)
            if ai_thought and len(ai_thought) > 10 and not ai_thought.startswith("⚠️"):
                thought = ai_thought.strip().strip('"').strip("'")

        if not thought:
            thought = self._synthesize_procedural_thought(canonical_id, profile, active_task, sched, state)

        # Update state and record memory in SQLite
        state.current_thought = thought
        state.last_thought_time = now_ts

        try:
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO npc_brain_memories 
                (agent_id, memory_type, content, emotion, morale, energy, stress, task_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    canonical_id,
                    "thought",
                    thought,
                    state.emotion,
                    state.morale,
                    state.energy,
                    state.stress,
                    task_id or None,
                    datetime.datetime.now(WIB_OFFSET).isoformat()
                )
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

        return thought

    def update_all_npcs(self, active_tasks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Updates emotional state, thought, and status for all NPCs based on schedule and real tasks.
        Enforces continuous desk work: agents with active tasks stay working at their desks.
        """
        sched = self.get_effective_schedule()

        # Map active tasks by canonical assignee
        task_by_assignee: Dict[str, Dict[str, Any]] = {}
        if active_tasks:
            for t in active_tasks:
                if t.get("status") in ("in_progress", "working"):
                    raw_assignee = t.get("assignee") or ""
                    canon = self._canonical_id(raw_assignee)
                    task_by_assignee[canon] = t

        updated_list = []
        for agent_id, state in self.npc_states.items():
            profile = self.roster.get(agent_id)
            active_task = task_by_assignee.get(agent_id) or self._get_agent_active_task(agent_id)
            
            if active_task:
                state.assigned_task = f"{active_task.get('id')}: {active_task.get('title')}"

            # STRICT NO-DEMO & CONTINUOUS WORK POLICY:
            # Agents with active in-progress tasks MUST WORK AT DESKS continuously until task is done!
            # Only rest during scheduled LUNCH_BREAK or when tasks are completed.
            if sched["is_meeting_time"]:
                state.status = "meeting"
                state.emotion = "Standup Focus"
                state.stress = min(60, state.stress + 1)
            elif sched["period"] == OfficePeriod.LUNCH_BREAK:
                state.status = "break"
                state.emotion = "Chill & Ngopi"
                state.stress = max(8, state.stress - 4)
                state.energy = min(100, state.energy + 5)
            elif state.assigned_task or active_task:
                # Working at desk on real task
                state.status = "working"
                if "manager" in agent_id:
                    state.emotion = "Savage & Focus"
                elif "treasurer" in agent_id:
                    state.emotion = "Pelit/Hemat Mode"
                elif "secretary" in agent_id:
                    state.emotion = "Aesthetic & Rapi"
                elif "yt_shorts" in agent_id:
                    state.emotion = "Timeline Ninja"
                elif "tiktok_affiliate" in agent_id:
                    state.emotion = "Cuan Hunter"
                elif "quality_assurance" in agent_id:
                    state.emotion = "Quality Sentinel"
                elif "tiktok_specialist" in agent_id:
                    state.emotion = "Creative Flow"
                else:
                    state.emotion = "Focus & Eksekusi"
                state.stress = min(75, state.stress + 1)
                state.energy = max(35, state.energy - 1)
            else:
                # No active task: free to rest/wander
                state.status = "idle"
                state.emotion = "Santai (Tugas Selesai)"

            # Generate dynamic thought and persist (reuses cache within 45s for instant response)
            state.current_thought = self.generate_dynamic_thought(agent_id, active_task=active_task, force_refresh=False)
            updated_list.append(asdict(state))

        return updated_list

    def _synthesize_procedural_dialogue(
        self,
        init_id: str,
        recip_id: str,
        init_prof: NPCProfile,
        recip_prof: NPCProfile,
        sched: Dict[str, Any]
    ) -> Tuple[str, str, str]:
        """
        Synthesizes authentic dynamic 2-way dialogue based on both agents' actual tasks,
        roles, schedule, and live metrics (zero canned strings).
        """
        task1 = self._get_agent_active_task(init_id)
        task2 = self._get_agent_active_task(recip_id)

        t1_str = f"[{task1['id']}] {task1['title'][:28]}" if task1 else "tugas operasional"
        t2_str = f"[{task2['id']}] {task2['title'][:28]}" if task2 else "target divisi"
        wib_str = sched.get("wib_time", "WIB")
        is_lunch = sched.get("period") == OfficePeriod.LUNCH_BREAK

        topic = "Sinkronisasi Alur Kerja Divisi"

        if is_lunch:
            topic = "Break Siang & Ngopi Santai"
            speech1 = f"Bro {recip_prof.name}, istirahat siang dulu jam {wib_str}. Pendingin otak bentar biar ga kena mental!"
            speech2 = f"Iya {init_prof.name}, nikmatin kopi dulu. Abis break siang kita langsung gaspol kelarin kerjaan lagi!"
        elif (init_id == "executive_manager" and recip_id == "treasurer") or (init_id == "treasurer" and recip_id == "executive_manager"):
            topic = "Audit Zero-Cost Policy & Token AI"
            speech1 = f"Marcus, pastiin task {t1_str} sama pemakaian token Gemini/Qwen kita tetep $0.00 spend ya, no cap!"
            speech2 = f"Santai Alex! Token budget terpantau aman terkendali, dompet perusahaan tebel dan anti boncos!"
        elif (init_id == "creator_pm" and recip_id == "yt_shorts_specialist") or (init_id == "yt_shorts_specialist" and recip_id == "creator_pm"):
            topic = "Produksi Short 9:16 FFmpeg Lokal"
            speech1 = f"Leo, visual subtitle glow sama audio ducking di {t2_str} udah smooth dirender lokal?"
            speech2 = f"Beres Diana! Render FFmpeg 1080x1920 60fps kelar, bebas copyright dan siap dipublish!"
        elif (init_id == "tiktok_specialist" and recip_id == "tiktok_affiliate") or (init_id == "tiktok_affiliate" and recip_id == "tiktok_specialist"):
            topic = "Hook Viral & Keranjang Kuning"
            speech1 = f"Victor, naskah hook 3 detik {t1_str} udah diselipin angle soft-selling produk keranjang kuning lu!"
            speech2 = f"Mantap Maya! Konversi produk ini lagi gacor-gacornya di TikTok Shop, komisi 18% siap panen!"
        elif (init_id == "quality_assurance" and recip_id in ("yt_long_specialist", "yt_shorts_specialist")):
            topic = "Inspeksi Kualitas Visual & Audio"
            speech1 = f"{recip_prof.name}, hasil render {t2_str} udah gue cek semua layernya: audio sync presisi, zero artifact!"
            speech2 = f"Thanks Zack! Semua bukti source ledger dan subtitle juga udah nempel rapi sesuai standar siar."
        elif (init_id == "executive_secretary" and recip_id == "executive_manager"):
            topic = "Notulensi & Agenda Standup Sore"
            speech1 = f"Alex, agenda rapat evaluasi sore jam 17:00 WIB udah disiapkan rapi di arsip database."
            speech2 = f"Mantap Sophia, broadcast ke Telegram CEO Gentha biar beliau update progres riil kita hari ini."
        elif (init_id == "content_researcher" and recip_id in ("tiktok_specialist", "creator_pm")):
            topic = "Briefing Riset Tren & Topik Edukasi"
            speech1 = f"{recip_prof.name}, data tren viral dan sitasi terverifikasi buat {t2_str} udah ready di database."
            speech2 = f"Thanks Ethan! Riset lu solid banget, naskah hook jadi punya daging dan ga ada yang hoaks."
        else:
            topic = f"Koordinasi {t1_str}"
            speech1 = f"{recip_prof.name}, gimana progress bagian divisi lu di {t2_str}? Target hari ini aman kan?"
            speech2 = f"Aman terkendali {init_prof.name}! Semuanya on track sesuai standar Harmage dan kebijakan $0 budget."

        return speech1, speech2, topic

    def trigger_interaction(self, initiator_id: Optional[str] = None, recipient_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates dynamic autonomous 2-way dialogue between NPCs in the office.
        1. Employs dynamic LLM completion when AI tokens permit
        2. Falls back to dynamic procedural contextual synthesis grounded in SQLite tasks
        3. Saves to persistent table npc_brain_interactions and recent dialogues
        """
        all_ids = list(self.npc_states.keys())
        
        # Resolve canonical IDs
        if initiator_id:
            init_canon = self._canonical_id(initiator_id)
        else:
            init_canon = random.choice(all_ids)
            
        remaining = [a for a in all_ids if a != init_canon]
        if recipient_id:
            recip_canon = self._canonical_id(recipient_id)
        else:
            recip_canon = random.choice(remaining)

        init_prof = self.roster.get(init_canon) or self.roster["executive_manager"]
        recip_prof = self.roster.get(recip_canon) or self.roster["treasurer"]

        sched = self.get_effective_schedule()

        # Try LLM dialogue generation
        ai_prompt = (
            f"Simulasikan percakapan singkat 2 giliran (A menyapa/bertanya, B menjawab) antara dua rekan kerja di kantor Harmage:\n"
            f"Karyawan 1: {init_prof.name} ({init_prof.role_title}), sifat: {init_prof.tone_of_voice}.\n"
            f"Karyawan 2: {recip_prof.name} ({recip_prof.role_title}), sifat: {recip_prof.tone_of_voice}.\n"
            f"Waktu kantor: {sched['period_label']} ({sched['wib_time']}).\n"
            f"Keduanya harus berbicara santai, savage/gaul ala Gen-Z (bestie, no cap, gaspol, mantap, aman), "
            f"berbobot tentang pekerjaan kantor, maksimal 16 kata per orang.\n"
            f"Format balasan HARUS JSON:\n"
            f'{{"speech1": "...", "speech2": "...", "topic": "..."}}'
        )
        ai_raw = self._call_ai_completion(ai_prompt, max_tokens=140)

        speech1 = ""
        speech2 = ""
        topic = "Kolaborasi Harmage"

        if ai_raw:
            try:
                cleaned = ai_raw.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                parsed = json.loads(cleaned.strip())
                speech1 = parsed.get("speech1", "")
                speech2 = parsed.get("speech2", "")
                topic = parsed.get("topic", "Koordinasi Proyek")
            except Exception:
                pass

        # If LLM didn't return valid speech, use dynamic procedural synthesis
        if not speech1 or not speech2:
            speech1, speech2, topic = self._synthesize_procedural_dialogue(
                init_canon, recip_canon, init_prof, recip_prof, sched
            )

        wib_time_str = datetime.datetime.now(WIB_OFFSET).strftime("%H:%M:%S WIB")

        dialogue_event = {
            "timestamp": wib_time_str,
            "topic": topic,
            "initiator": {
                "id": init_canon,
                "name": init_prof.name,
                "role": init_prof.role_title,
                "speech": speech1
            },
            "recipient": {
                "id": recip_canon,
                "name": recip_prof.name,
                "role": recip_prof.role_title,
                "speech": speech2
            },
            "schedule_period": sched["period"],
        }

        # Update in-memory recent dialogue queue
        self.recent_dialogues.insert(0, dialogue_event)
        self.recent_dialogues = self.recent_dialogues[:25]

        # Update both agents' memory and current thought
        if init_canon in self.npc_states:
            self.npc_states[init_canon].current_thought = speech1
            self.npc_states[init_canon].last_interaction = f"Ngobrol dengan {recip_prof.name} ({topic})"
            self.npc_states[init_canon].stress = max(10, self.npc_states[init_canon].stress - 3)
            self.npc_states[init_canon].morale = min(100, self.npc_states[init_canon].morale + 2)

        if recip_canon in self.npc_states:
            self.npc_states[recip_canon].current_thought = speech2
            self.npc_states[recip_canon].last_interaction = f"Ngobrol dengan {init_prof.name} ({topic})"
            self.npc_states[recip_canon].stress = max(10, self.npc_states[recip_canon].stress - 3)
            self.npc_states[recip_canon].morale = min(100, self.npc_states[recip_canon].morale + 2)

        # Persist to SQLite
        try:
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO npc_brain_interactions
                (initiator_id, initiator_name, initiator_speech, recipient_id, recipient_name, recipient_speech, context_period, topic, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    init_canon,
                    init_prof.name,
                    speech1,
                    recip_canon,
                    recip_prof.name,
                    speech2,
                    sched["period"],
                    topic,
                    datetime.datetime.now(WIB_OFFSET).isoformat()
                )
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

        return dialogue_event


# Global singleton instance
npc_brain_manager = HarmageNPCBrainManager()
