"""
Harmage Autonomous AI NPC Complex Brain & Simulation Engine
============================================================
Provides autonomous emotional simulation, schedule management (WIB),
decision-making, and dynamic inter-agent interactions for the 10 Harmage personas.
"""

import datetime
import random
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

# Timezone Asia/Jakarta (WIB = UTC+7)
WIB_OFFSET = datetime.timezone(datetime.timedelta(hours=7))

class OfficePeriod:
    MORNING_WORK = "MORNING_WORK"          # 09:00 - 12:00 WIB: Focus Sprint
    LUNCH_BREAK = "LUNCH_BREAK"            # 12:00 - 13:00 WIB: Istirahat Siang / Chill
    AFTERNOON_WORK = "AFTERNOON_WORK"      # 13:00 - 17:00 WIB: Production & Execution
    STANDUP_MEETING = "STANDUP_MEETING"    # 17:00 - 17:30 WIB: Evaluasi Harian Sore
    FREE_REST = "FREE_REST"                # 17:30 - 09:00 WIB: Santai / Standby / Bebas

@dataclass
class NPCBrainState:
    agent_id: str
    name: str
    role: str
    division: str
    morale: int = 85           # 0 - 100
    energy: int = 90           # 0 - 100
    stress: int = 20           # 0 - 100
    emotion: str = "Focus"     # Focus, Chill, Savage, Pelit/Hemat, Aesthetic, Panik, Semangat
    current_thought: str = ""
    status: str = "working"    # working, break, meeting, idle
    assigned_task: Optional[str] = None
    last_interaction: str = ""
    vibe_personality: str = ""

# Persona seed profiles matching Harmage Enterprise
PERSONA_PROFILES: Dict[str, Dict[str, Any]] = {
    "executive_manager": {
        "name": "Alex Vance",
        "role": "Executive Manager & Director of Operations",
        "division": "Executive Suite",
        "vibe": "Savage, toxic Gen-Z boss, decisive, anti-gabut, no cap",
        "default_emotion": "Savage & Focus",
        "dialogue_pool": [
            "Target harian 3 campaign affiliate sama 1 video 16:9 hari ini jangan lelet ya bestie, no cap.",
            "Semua divisi gaspol, gue gamau liat ada yang gabut di jam kerja.",
            "Marcus, cek token budget Gemini kita, jangan sampe kena charge sepeserpun!",
            "Rapat sore jam 17:00 WIB wajib hadir semua di meeting room, jangan ada yang ngilang."
        ],
        "break_dialogue": [
            "Gue ngopi dulu 15 menit, awas aja kalo ada yang kendor pas gue balik.",
            "Waktunya istirahat, recharge otak bentar biar ga kena mental."
        ]
    },
    "treasurer": {
        "name": "Marcus Drake",
        "role": "Treasurer & Financial Controller",
        "division": "Executive Suite",
        "vibe": "Pelit akut, kalkulatif, zero-dollar hawk, anti boncos",
        "default_emotion": "Pelit/Hemat Mode",
        "dialogue_pool": [
            "Audit token aman: kita tetep $0.00 cloud spend berkat Gemini 2.5 Flash free tier!",
            "Jangan ada yang coba-coba request API berbayar ya, dompet perusahaan harus tetep tebel.",
            "Alhamdulillah cashflow affiliate keranjang kuning mulai naik, pengeluaran tetep nol dolar.",
            "Alex, gue pantau kuota harian kita masih sisa banyak, hemat pangkal kaya!"
        ],
        "break_dialogue": [
            "Istirahat dulu, minum kopi gratisan kantor. Ga keluar duit sepeserpun, mantap jiwa.",
            "Waktunya rehat, pendingin otak dari hitung-hitungan rupiah."
        ]
    },
    "secretary": {
        "name": "Sophia Chen",
        "role": "Executive Secretary & Notetaker",
        "division": "Executive Suite",
        "vibe": "Rapi, gercep, aesthetic, judes ke yang berantakan, typo-police",
        "default_emotion": "Aesthetic & Rapi",
        "dialogue_pool": [
            "Semua notulensi keputusan CEO dan task log udah gue arsipin rapi di database.",
            "Tolong kalau submit laporan jangan ada typo ya, sakit mata liatnya.",
            "Agenda rapat evaluasi sore jam 17:00 WIB udah di-broadcast ke Telegram CEO.",
            "Struktur dokumen kantor Harmage 100% konsisten dan tersinkronisasi."
        ],
        "break_dialogue": [
            "Meja kerja udah aesthetic dan rapi, saatnya seduh matcha latte di lounge.",
            "Break time, scroll Pinterest bentar cari inspirasi layout laporan."
        ]
    },
    "creator_pm": {
        "name": "Diana Prince",
        "role": "PIC Divisi Konten Kreator & Affiliate",
        "division": "Creator & Affiliate",
        "vibe": "Hustler, ambisius, savage project manager, FYP-obsessed",
        "default_emotion": "FYP Hustler",
        "dialogue_pool": [
            "Pipeline YouTube 16:9 sama TikTok Affiliate berjalan simultan hari ini!",
            "Leo, visual explainer-nya udah match sama timeline naskah Maya Lin kan?",
            "Victor, pastiin produk keranjang kuning yang diriset komisi di atas 15% ya!",
            "Kita kejar retention rate 85% di 10 detik pertama, gas!"
        ],
        "break_dialogue": [
            "Break time! Cek feed TikTok bentar liat sound apa yang lagi trending.",
            "Istirahat siang dulu, abis ini kita review final render video 16:9."
        ]
    },
    "video_editor": {
        "name": "Leo Sparks",
        "role": "Editor Shorts (9:16 Vertical Specialist)",
        "division": "Creator & Affiliate",
        "vibe": "Genius visual editor, perfectionist timeline, timeline ninja",
        "default_emotion": "Focus Timeline",
        "dialogue_pool": [
            "Rendering vertical 9:16 pake Cheat Clip PRO lokal beres, typography glow terpasang.",
            "Audio ducking antara BGM sama voiceover udah smooth banget, bebas copyright strike.",
            "Color grading punchy biar visual pop-out di layar HP audiens.",
            "Shorts udah siap masuk approval gate CEO Gentha!"
        ],
        "break_dialogue": [
            "Mata segerin dulu dari timeline premiere, mau main pingpong di pojokan.",
            "Break ngopi dulu, rendering FFmpeg 60fps bikin GPU anget."
        ]
    },
    "editor_longform": {
        "name": "Raka Pratama",
        "role": "Editor Panjang (16:9 YouTube Specialist)",
        "division": "Creator & Affiliate",
        "vibe": "Cinematic storyteller, pacing master, detail-oriented",
        "default_emotion": "Cinematic Focus",
        "dialogue_pool": [
            "Assembly video panjang 16:9 scene-by-scene pake FFmpeg lancar jaya.",
            "Transisi chapter narasi edukasi terasa organik, durasi total 8-12 menit terencana.",
            "Source ledger bukti dan sitasi terverifikasi disematkan di tiap segmen visual.",
            "Tinggal render master explainer 1080p, kualitas siar televisi!"
        ],
        "break_dialogue": [
            "Istirahat bentar, dengerin lo-fi di lounge seat biar telinga istirahat.",
            "Ngopi dulu di pantry sambil nunggu master timeline assembly."
        ]
    },
    "scriptwriter": {
        "name": "Maya Lin",
        "role": "Scriptwriter & Viral Hook Specialist",
        "division": "Creator & Affiliate",
        "vibe": "Storyteller jenius, psikolog retensi audiens, hook specialist",
        "default_emotion": "Creative Flow",
        "dialogue_pool": [
            "Hook 3 detik pertama naskah ini bakal bikin penonton ga bisa skip!",
            "Formula 8-tahap edukasi: Problem -> Agitation -> Solution -> Evidence -> Call to Action.",
            "Gaya bahasa naskah kita padat, ga bertele-tele, langsung ke inti solusi.",
            "Naskah video explainer AI Automation udah kelar dan diserahkan ke Diana!"
        ],
        "break_dialogue": [
            "Otak butuh kafein, jalan ke coffee machine dulu ya bestie.",
            "Rehat sejenak baca-baca buku di library buat nambah kosa kata hook."
        ]
    },
    "tiktok_affiliate": {
        "name": "Victor Sterling",
        "role": "Affiliate TikTok Lead (Keranjang Kuning)",
        "division": "Creator & Affiliate",
        "vibe": "Data-driven seller, conversion hawk, trend sniffer",
        "default_emotion": "Cuan Hunter",
        "dialogue_pool": [
            "5 produk gadget meja kerja viral udah gue kurasi, checkout rate-nya gokil!",
            "Komisi 18% per checkout, estimasi komisi masuk minggu ini bakal melonjak.",
            "Keranjang kuning udah di-link dengan naskah hook buatan Maya Lin.",
            "A/B testing thumbnail produk affiliate siap diuji sore ini."
        ],
        "break_dialogue": [
            "Santai bentar di lounge, sambil mantau saldo komisi TikTok Shop.",
            "Istirahat ngemil di pantry, stamina harus on terus buat riset produk."
        ]
    },
    "qa_sentinel": {
        "name": "Zackary Cross",
        "role": "Quality Assurance Sentinel",
        "division": "Creator & Affiliate",
        "vibe": "Zero-defect zealot, teliti, anti-glitch, quality gatekeeper",
        "default_emotion": "Quality Sentinel",
        "dialogue_pool": [
            "Inspeksi frame 1920x1080 passed: audio sync presisi, zero glitch artifact.",
            "Semua klaim fakta video longform sudah lolos validasi Source Ledger.",
            "Checklist QA 100% hijau, deliverable aman diserahkan ke CEO Gentha.",
            "Standar broadcast Harmage terpenuhi, tidak ada toleransi untuk kualitas rendah."
        ],
        "break_dialogue": [
            "QA checklist selesai, jalan santai ke water cooler buat hidrasi.",
            "Rehat sejenak dari inspeksi pixel, main arcade sebentar."
        ]
    },
    "researcher": {
        "name": "Ethan Cole",
        "role": "Content & Market Researcher",
        "division": "Creator & Affiliate",
        "vibe": "Deep researcher, data archivist, trend forecaster",
        "default_emotion": "Deep Research",
        "dialogue_pool": [
            "Riset topik video panjang AI Autonomous Office lengkap dengan 5 perbandingan tools.",
            "Semua sumber terakreditasi dan ledger sitasi terarsip secara transparan.",
            "Analisis pasar menunjukkan minat audiens terhadap otomasi bisnis melonjak 45%.",
            "Data briefing riset sudah siap diserahkan ke Scriptwriter Maya Lin."
        ],
        "break_dialogue": [
            "Selesai riset 3 paper, istirahat dulu di sofa lounge sambil baca santai.",
            "Ngopi dulu di pantry, refreshing pikiran sebelum analisis data berikutnya."
        ]
    }
}

class HarmageNPCBrainManager:
    """Central autonomous simulation brain for all Harmage NPCs."""

    def __init__(self):
        self.schedule_override: Optional[str] = None
        self.manual_override_until: float = 0
        self.recent_dialogues: List[Dict[str, Any]] = []
        self.npc_states: Dict[str, NPCBrainState] = {}
        self._init_npcs()

    def _init_npcs(self):
        for agent_id, prof in PERSONA_PROFILES.items():
            self.npc_states[agent_id] = NPCBrainState(
                agent_id=agent_id,
                name=prof["name"],
                role=prof["role"],
                division=prof["division"],
                morale=random.randint(80, 95),
                energy=random.randint(85, 95),
                stress=random.randint(15, 30),
                emotion=prof["default_emotion"],
                current_thought=prof["dialogue_pool"][0],
                status="working",
                vibe_personality=prof["vibe"]
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
                # Outside main office hours: free rest / standby
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
        
        # Trigger NPC state updates according to new schedule
        self.update_all_npcs()

        return self.get_effective_schedule()

    def clear_schedule_override(self) -> Dict[str, Any]:
        self.schedule_override = None
        self.manual_override_until = 0
        self.update_all_npcs()
        return self.get_effective_schedule()

    def update_all_npcs(self, active_tasks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Updates emotional state, thought, and status for all 10 NPCs based on schedule and real tasks."""
        sched = self.get_effective_schedule()
        period = sched["period"]

        # Map active tasks by assignee if provided
        task_by_assignee = {}
        if active_tasks:
            for t in active_tasks:
                if t.get("status") in ("in_progress", "working"):
                    task_by_assignee[t.get("assignee")] = t

        updated_list = []
        for agent_id, state in self.npc_states.items():
            prof = PERSONA_PROFILES.get(agent_id, {})
            dialogue_pool = prof.get("dialogue_pool", ["Kerja lancar no cap."])
            break_pool = prof.get("break_dialogue", ["Istirahat sejenak di pantry."])
            
            # Check if has real active task
            active_task = task_by_assignee.get(agent_id)
            if active_task:
                state.assigned_task = f"{active_task.get('id')}: {active_task.get('title')}"
            
            # Behavior determination:
            if sched["is_meeting_time"]:
                # Everyone goes to meeting table
                state.status = "meeting"
                state.emotion = "Standup Focus"
                state.current_thought = f"{state.name}: Hadir rapat evaluasi harian sore di meeting room."
            elif sched["is_break_time"]:
                # Break time: even if task exists, they take a break unless it's critical
                state.status = "break"
                state.emotion = "Chill & Ngopi"
                state.stress = max(5, state.stress - 5)
                state.energy = min(100, state.energy + 8)
                state.current_thought = random.choice(break_pool)
            elif sched["is_working_hours"]:
                # Working hours:
                # If they have an in-progress task, THEY WORK AT DESK UNTIL DONE!
                if state.assigned_task or not active_tasks:
                    state.status = "working"
                    state.emotion = prof.get("default_emotion", "Focus")
                    state.stress = min(75, state.stress + 2)
                    state.energy = max(30, state.energy - 2)
                    state.current_thought = random.choice(dialogue_pool)
                else:
                    # Task completed or no task: free to rest/wander
                    state.status = "idle"
                    state.emotion = "Santai (Tugas Selesai)"
                    state.current_thought = "Semua tugas beres, standby di lounge kalau ada arahan CEO."
            else:
                state.status = "idle"
                state.emotion = "Standby"
                state.current_thought = "Jam operasional selesai, sistem mode hemat token $0."

            updated_list.append(asdict(state))

        return updated_list

    def trigger_interaction(self, initiator_id: Optional[str] = None, recipient_id: Optional[str] = None) -> Dict[str, Any]:
        """Generates dynamic autonomous dialogue between NPCs in the office."""
        agent_ids = list(PERSONA_PROFILES.keys())
        if not initiator_id or initiator_id not in PERSONA_PROFILES:
            initiator_id = random.choice(agent_ids)
        
        remaining = [a for a in agent_ids if a != initiator_id]
        if not recipient_id or recipient_id not in PERSONA_PROFILES or recipient_id == initiator_id:
            recipient_id = random.choice(remaining)

        init_prof = PERSONA_PROFILES[initiator_id]
        recip_prof = PERSONA_PROFILES[recipient_id]

        sched = self.get_effective_schedule()
        is_break = sched["is_break_time"]

        # Contextual conversation generation
        if is_break:
            speech1 = f"Bro {recip_prof['name']}, ngopi dulu santai di lounge. Seharian fokus monitor kerjaan biar ga pusing."
            speech2 = f"Iya {init_prof['name']}, nikmatin break time dulu. Abis ini lanjut gaspol lagi!"
        else:
            speech1 = f"{recip_prof['name']}, gimana progres bagian divisi lu? Target konten dan validasi sistem aman kan?"
            speech2 = f"Aman terkendali {init_prof['name']}! Semuanya on track sesuai standar Harmage dan kebijakan $0 budget."

        # Specific dynamic interaction pairs
        if initiator_id == "executive_manager" and recipient_id == "treasurer":
            speech1 = "Marcus, pastiin token AI kita hari ini ga ada yang bocor ke tier berbayar ya!"
            speech2 = "Santai Alex! Token budget 2M WIB terpantau aman $0.00 spend. Dompet perusahaan terjaga ketat!"
        elif initiator_id == "creator_pm" and recipient_id == "video_editor":
            speech1 = "Leo, visual subtitle sama audio ducking short 9:16 udah kelar di-render?"
            speech2 = "Udah beres Diana! Render FFmpeg 1080x1920 60fps super mulus, siap dipublish!"
        elif initiator_id == "scriptwriter" and recipient_id == "tiktok_affiliate":
            speech1 = "Victor, naskah hook 3 detik yang baru udah diselipin CTA keranjang kuning produk viral lu."
            speech2 = "Mantap Maya! Conversion rate produk ini lagi tinggi-tingginya, komisi 18% siap panen!"
        elif initiator_id == "qa_sentinel" and recipient_id == "editor_longform":
            speech1 = "Raka, hasil render video explainer 16:9 udah gue cek semua layer audio dan resolusinya."
            speech2 = "Thanks Zack! Semua bukti source ledger juga udah nempel di tiap chapter narasi."

        dialogue_event = {
            "timestamp": datetime.datetime.now(WIB_OFFSET).strftime("%H:%M:%S WIB"),
            "initiator": {
                "id": initiator_id,
                "name": init_prof["name"],
                "role": init_prof["role"],
                "speech": speech1
            },
            "recipient": {
                "id": recipient_id,
                "name": recip_prof["name"],
                "role": recip_prof["role"],
                "speech": speech2
            },
            "schedule_period": sched["period"],
        }

        self.recent_dialogues.insert(0, dialogue_event)
        self.recent_dialogues = self.recent_dialogues[:20]

        # Update thoughts on actors
        if initiator_id in self.npc_states:
            self.npc_states[initiator_id].current_thought = speech1
            self.npc_states[initiator_id].last_interaction = f"Ngobrol dengan {recip_prof['name']}"
        if recipient_id in self.npc_states:
            self.npc_states[recipient_id].current_thought = speech2
            self.npc_states[recipient_id].last_interaction = f"Ngobrol dengan {init_prof['name']}"

        return dialogue_event

# Global singleton instance
npc_brain_manager = HarmageNPCBrainManager()
