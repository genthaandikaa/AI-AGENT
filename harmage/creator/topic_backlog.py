"""YouTube Long-Form Topic Discovery & Rubric Scoring Engine.

Manages persistent topic backlog across:
- Counterfactual science
- Human biology & everyday mysteries
- Space, Earth, climate, physics, and future scenarios
- History and forgotten civilizations
- Religion and comparative religious history
- Thought experiments, myths vs evidence
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from harmage.db import get_connection, log_activity


DEFAULT_LONGFORM_TOPICS = [
    {
        "id": "TOPIC-001",
        "category": "counterfactual",
        "title": "Apa yang Terjadi Jika Oksigen di Bumi Lenyap Selama 5 Detik?",
        "hook_question": "Bayangkan jika kamu menahan napas selama 5 detik, kamu selamat. Tapi jika seluruh molekul oksigen bumi hilang selama 5 detik, bisakah peradaban bertahan?",
        "scores": {
            "curiosity": 9.5,
            "educational_value": 9.0,
            "evidence_availability": 9.2,
            "visual_storytelling": 9.4,
            "audience_relevance": 9.0,
            "novelty": 8.8,
            "feasibility": 9.5,
            "risk_penalty": 0.2
        },
        "editorial_rationale": "Sangat kuat secara visual (langit gelap seketika, semen/beton runtuh karena ikatan oksigen terurai, kerak bumi amblas). Menjelaskan ikatan kimia dengan cara dramatis namun akurat.",
        "source_links": [
            "https://www.usgs.gov/special-topics/water-science-school/science/water-properties",
            "https://earthobservatory.nasa.gov/features/Atmosphere",
            "https://www.britannica.com/science/oxygen"
        ]
    },
    {
        "id": "TOPIC-002",
        "category": "biology",
        "title": "Mengapa Manusia Harus Tidur & Apa yang Terjadi di Otak Saat Bermimpi?",
        "hook_question": "Sepertiga hidup kita dihabiskan dalam keadaan tidak sadar. Kenapa evolusi membiarkan makhluk hidup rentan bahaya saat tidur?",
        "scores": {
            "curiosity": 9.0,
            "educational_value": 9.4,
            "evidence_availability": 9.5,
            "visual_storytelling": 8.8,
            "audience_relevance": 9.6,
            "novelty": 8.2,
            "feasibility": 9.2,
            "risk_penalty": 0.0
        },
        "editorial_rationale": "Sangat relevan untuk audiens umum. Menjelaskan sistem glymphatic (pembersihan racun otak saat fase slow-wave) dan fase REM.",
        "source_links": [
            "https://www.nih.gov/news-events/nih-research-matters/brain-may-flush-out-toxins-during-sleep",
            "https://www.nature.com/articles/nature12603"
        ]
    },
    {
        "id": "TOPIC-003",
        "category": "space_physics",
        "title": "Apa yang Terjadi Jika Kamu Melompat ke Lubang yang Menembus Inti Bumi?",
        "hook_question": "Jika ada terowongan dari kutub utara ke kutub selatan dan kamu melompat ke dalamnya, berapa lama waktu yang dibutuhkan untuk sampai ke sisi lain?",
        "scores": {
            "curiosity": 9.2,
            "educational_value": 9.0,
            "evidence_availability": 9.0,
            "visual_storytelling": 9.2,
            "audience_relevance": 8.6,
            "novelty": 8.8,
            "feasibility": 9.0,
            "risk_penalty": 0.1
        },
        "editorial_rationale": "Eksperimen pikiran gravitasi klasik. Menjelaskan teorema cangkang Gauss, osilasi harmonik sederhana 38-42 menit, dan tantangan tekanan inti bumi 360 GPa.",
        "source_links": [
            "https://en.wikipedia.org/wiki/Gravity_train",
            "https://pubs.aip.org/aapt/ajp/article/83/3/231/1045236/To-fall-through-the-Earth-in-38-minutes"
        ]
    },
    {
        "id": "TOPIC-004",
        "category": "history",
        "title": "Misteri Peradaban Lembah Indus: Kota Megah Tanpa Istana & Monumen Perang",
        "hook_question": "4.500 tahun lalu, kota Mohenjo-Daro memiliki sistem sanitasi dan tata kota lebih maju dari Roma kuno. Namun kenapa peradaban sebesar ini tidak meninggalkan satupun istana raja atau prasasti perang?",
        "scores": {
            "curiosity": 8.8,
            "educational_value": 9.2,
            "evidence_availability": 8.8,
            "visual_storytelling": 8.9,
            "audience_relevance": 8.0,
            "novelty": 9.0,
            "feasibility": 8.8,
            "risk_penalty": 0.2
        },
        "editorial_rationale": "Menyoroti peradaban kuno yang egalitarian, perencanaan kota hidrolik, dan teori kekeringan monsun sebagai penyebab keruntuhannya.",
        "source_links": [
            "https://www.harappa.com",
            "https://www.unesco.org/en/articles/archaeological-ruins-moenjodaro"
        ]
    },
    {
        "id": "TOPIC-005",
        "category": "comparative_religion",
        "title": "Evolusi Konsep Waktu: Dari Siklus Abadi Hingga Garis Lurus Kosmologi",
        "hook_question": "Apakah waktu itu berputar tanpa akhir seperti roda samsara, ataukah garis lurus berawal dari penciptaan menuju titik akhir? Bagaimana tradisi dunia dan fisika modern memandang waktu?",
        "scores": {
            "curiosity": 8.9,
            "educational_value": 9.3,
            "evidence_availability": 8.7,
            "visual_storytelling": 8.6,
            "audience_relevance": 8.2,
            "novelty": 9.2,
            "feasibility": 8.5,
            "risk_penalty": 0.3
        },
        "editorial_rationale": "Pendekatan komparatif historis dan filosofis yang seimbang, menghormati tradisi Abrahamik (linear) dan Dharmik (siklis/kalpa), disandingkan dengan panah waktu termodinamika entropi.",
        "source_links": [
            "https://plato.stanford.edu/entries/time/",
            "https://www.oxfordreference.com/display/10.1093/acref/9780198662440.001.0001/acref-9780198662440"
        ]
    },
    {
        "id": "TOPIC-006",
        "category": "thought_experiment",
        "title": "Paradoks Fermi: Jika Ada Milyaran Planet Layak Huni, Di Mana Semua Orang?",
        "hook_question": "Dengan 100 milyar galaksi dan masing-masing ratusan milyar bintang, alam semesta seharusnya penuh peradaban cerdas. Lalu mengapa saat kita menatap bintang, angkasa begitu hening?",
        "scores": {
            "curiosity": 9.6,
            "educational_value": 9.2,
            "evidence_availability": 9.1,
            "visual_storytelling": 9.5,
            "audience_relevance": 9.2,
            "novelty": 8.5,
            "feasibility": 9.4,
            "risk_penalty": 0.1
        },
        "editorial_rationale": "Topik eksplorasi sains populer nomor satu di dunia edukasi. Mengulas konsep The Great Filter, Dyson Spheres, dan hipotesis planet kebun binatang.",
        "source_links": [
            "https://www.seti.org/fermi-paradox",
            "https://astronomy.com/news/2020/09/the-fermi-paradox-where-are-all-the-aliens"
        ]
    }
]


class TopicBacklogEngine:
    """Manages scoring and persistent topic backlog for YouTube Long-Form."""

    def __init__(self):
        self._ensure_seeded()

    def _calculate_total_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted score from 7 criteria minus risk penalty.
        Max potential score: 70.0 points.
        """
        curiosity = float(scores.get("curiosity", 7.0))
        education = float(scores.get("educational_value", 7.0))
        evidence = float(scores.get("evidence_availability", 7.0))
        visual = float(scores.get("visual_storytelling", 7.0))
        relevance = float(scores.get("audience_relevance", 7.0))
        novelty = float(scores.get("novelty", 7.0))
        feasibility = float(scores.get("feasibility", 7.0))
        risk = float(scores.get("risk_penalty", 0.0))

        total = curiosity + education + evidence + visual + relevance + novelty + feasibility - risk
        return round(total, 2)

    def _ensure_seeded(self) -> None:
        """Seed initial topics if table is empty."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM longform_topics;")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.now(timezone.utc).isoformat()
            for t in DEFAULT_LONGFORM_TOPICS:
                total = self._calculate_total_score(t["scores"])
                cursor.execute("""
                INSERT INTO longform_topics (
                    id, category, title, hook_question, scores, total_score,
                    editorial_rationale, source_links, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'backlog', ?, ?)
                """, (
                    t["id"],
                    t["category"],
                    t["title"],
                    t["hook_question"],
                    json.dumps(t["scores"]),
                    total,
                    t["editorial_rationale"],
                    json.dumps(t["source_links"]),
                    now,
                    now
                ))
            conn.commit()
            log_activity("INFO", "content_researcher", "Seeded 6 initial YouTube Long-Form educational topics with rubric scores")
        conn.close()

    def list_topics(self, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List topics sorted by highest score."""
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id, category, title, hook_question, scores, total_score, editorial_rationale, source_links, status, last_used_at, created_at FROM longform_topics WHERE 1=1"
        params = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY total_score DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r[0],
                "category": r[1],
                "title": r[2],
                "hook_question": r[3],
                "scores": json.loads(r[4]) if r[4] else {},
                "total_score": r[5],
                "editorial_rationale": r[6],
                "source_links": json.loads(r[7]) if r[7] else [],
                "status": r[8],
                "last_used_at": r[9],
                "created_at": r[10]
            })
        return results

    def get_top_candidate(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the highest scoring topic currently in backlog."""
        topics = self.list_topics(category=category, status="backlog")
        return topics[0] if topics else None

    def add_topic(
        self,
        category: str,
        title: str,
        hook_question: str,
        scores: Dict[str, float],
        editorial_rationale: str,
        source_links: List[str]
    ) -> Dict[str, Any]:
        """Score and add a new topic to the backlog."""
        import uuid
        topic_id = f"TOPIC-{uuid.uuid4().hex[:6].upper()}"
        total = self._calculate_total_score(scores)
        now = datetime.now(timezone.utc).isoformat()

        conn = get_connection()
        conn.execute("""
        INSERT INTO longform_topics (
            id, category, title, hook_question, scores, total_score,
            editorial_rationale, source_links, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'backlog', ?, ?)
        """, (
            topic_id, category, title, hook_question,
            json.dumps(scores), total, editorial_rationale,
            json.dumps(source_links), now, now
        ))
        conn.commit()
        conn.close()

        log_activity("INFO", "content_researcher", f"Added topic '{title}' with score {total}/70.0", f"ID: {topic_id}")
        return {
            "id": topic_id,
            "title": title,
            "category": category,
            "total_score": total,
            "status": "backlog"
        }

    def update_topic_status(self, topic_id: str, new_status: str) -> None:
        """Update status of a topic (e.g. selected, in_production, produced)."""
        now = datetime.now(timezone.utc).isoformat()
        conn = get_connection()
        conn.execute(
            "UPDATE longform_topics SET status = ?, updated_at = ?, last_used_at = ? WHERE id = ?",
            (new_status, now, now if new_status in ("in_production", "produced") else None, topic_id)
        )
        conn.commit()
        conn.close()
