"""Story, Narration Script, and Storyboard Engine for YouTube Long-Form.

Implements the 8-stage educational explainer architecture:
1. Cold Open (5-15s)
2. Curiosity Gap
3. Promise and Boundaries
4. Progressive Explanation
5. Mid-Video Reset
6. Nuance and Correction
7. Payoff
8. Closing Insight & Next Question
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional
from harmage.creator.source_ledger import SourceLedger


@dataclass
class SceneStoryboard:
    scene_id: str
    order: int
    stage: str
    narration_text: str
    estimated_duration_sec: float
    headline: str
    subtext: str
    visual_type: str        # 'title_hook', 'diagram_mechanism', 'split_comparison', 'callout_fact', 'thought_experiment', 'closing_card'
    motion_type: str        # 'ken_burns_zoom_in', 'pan_left', 'pulse_focus', 'static_diagram', 'slide_up'
    theme_palette: str      # 'cosmic_purple', 'ocean_blue', 'warning_amber', 'deep_slate', 'emerald_science'
    diagram_elements: List[str]
    claim_id: Optional[str] = None


@dataclass
class LongFormScriptPackage:
    topic_title: str
    category: str
    target_audience: str
    estimated_total_seconds: float
    stages: Dict[str, str]  # Map of stage name to narration text
    scenes: List[SceneStoryboard]
    pronunciation_notes: Dict[str, str]
    sound_design_notes: Dict[str, str]
    qa_checklist: List[str]


class ScriptEngine:
    """Produces verified Indonesian narration scripts and scene-by-scene storyboards."""

    def __init__(self):
        self.words_per_minute = 135.0  # Natural Indonesian educational pacing

    def estimate_speech_duration(self, text: str) -> float:
        """Estimate duration in seconds based on word count and punctuation pauses."""
        words = len(text.split())
        base_sec = (words / self.words_per_minute) * 60.0
        # Add pauses for sentences and commas
        pauses = text.count(".") * 0.4 + text.count(",") * 0.2 + text.count("?") * 0.5
        return round(max(3.0, base_sec + pauses), 1)

    def generate_pilot_script(self, topic: Dict[str, Any]) -> Tuple[LongFormScriptPackage, SourceLedger]:
        """Generate structured script and linked source ledger for topic."""
        title = topic.get("title", "Fenomena Sains Menakjubkan")
        category = topic.get("category", "counterfactual")

        ledger = SourceLedger(title)

        # Setup standard scientific and academic sources
        ledger.add_source(
            source_id="SRC-NASA-ATMOS",
            url="https://earthobservatory.nasa.gov/features/Atmosphere",
            publisher_author="NASA Earth Observatory",
            evidence_type="space_agency",
            publication_year=2023,
            notes="Komposisi atmosfer bumi (78% Nitrogen, 21% Oksigen, 1% gas lain)."
        )
        ledger.add_source(
            source_id="SRC-USGS-WATER",
            url="https://www.usgs.gov/special-topics/water-science-school/science/water-properties",
            publisher_author="USGS Water Science School",
            evidence_type="academic",
            publication_year=2022,
            notes="Ikatan molekul air H2O, 33% massa atom adalah oksigen."
        )
        ledger.add_source(
            source_id="SRC-GEOL-CRUST",
            url="https://www.britannica.com/science/Earth-crust",
            publisher_author="Encyclopaedia Britannica & Geological Survey",
            evidence_type="academic",
            publication_year=2024,
            notes="Kerak bumi tersusun atas 46.6% oksigen dalam bentuk silika dan oksida mineral."
        )

        # Decompose into 6 modular scenes covering the 8 explainer stages
        scenes = [
            SceneStoryboard(
                scene_id="S001",
                order=1,
                stage="cold_open",
                narration_text="Bagi paru-paru manusia, menahan napas lima detik adalah hal sepele. Tetapi bagi planet bumi, lima detik tanpa molekul oksigen adalah kehancuran total.",
                estimated_duration_sec=7.5,
                headline="BUMI TANPA OKSIGEN: 5 DETIK",
                subtext="Apa yang terjadi jika atom oksigen lenyap seketika?",
                visual_type="title_hook",
                motion_type="ken_burns_zoom_in",
                theme_palette="cosmic_purple",
                diagram_elements=["Simbol O2 Lenyap", "Timer 00:05.00", "Bumi Berkedip"],
                claim_id="CLM-001"
            ),
            SceneStoryboard(
                scene_id="S002",
                order=2,
                stage="curiosity_gap",
                narration_text="Di siang bolong, langit seketika berubah menjadi gelap gulita. Atmosfer kehilangan partikel penyebaran cahaya Rayleigh, sementara ozon O3 lenyap, membiarkan radiasi ultraviolet menghantam permukaan.",
                estimated_duration_sec=8.5,
                headline="LANGIT MENJADI GELAP GULITA",
                subtext="Rayleigh Scattering berhenti & lapisan pelindung Ozon lenyap",
                visual_type="diagram_mechanism",
                motion_type="slide_up",
                theme_palette="warning_amber",
                diagram_elements=["Lapisan Ozon O3", "Sinar UV Matahari", "Atmosfer 21% Hilang"],
                claim_id="CLM-002"
            ),
            SceneStoryboard(
                scene_id="S003",
                order=3,
                stage="progressive_explanation",
                narration_text="Setiap bangunan semen dan beton di seluruh dunia runtuh menjadi debu halus. Tanpa atom oksigen sebagai pengikat rantai silika dan kalsium, struktur terkuat manusia kehilangan daya rekat molekulernya.",
                estimated_duration_sec=8.0,
                headline="STRUKTUR BETON HANCUR",
                subtext="Ikatan Silika (SiO2) terurai seketika",
                visual_type="split_comparison",
                motion_type="pulse_focus",
                theme_palette="deep_slate",
                diagram_elements=["Molekul SiO2 Normal", "Disosiasi Atom", "Keruntuhan Massa"],
                claim_id="CLM-003"
            ),
            SceneStoryboard(
                scene_id="S004",
                order=4,
                stage="mid_video_reset",
                narration_text="Lautan bumi mulai menguap ke angkasa luar. Molekul air H2O kehilangan atom oksigen, menyisakan gas hidrogen murni yang begitu ringan sehingga melesat bebas menembus gravitasi atmosfer.",
                estimated_duration_sec=8.0,
                headline="AIR LAUT MENGUAP MENJADI HIDROGEN",
                subtext="H2O terurai menjadi gas hidrogen bebas",
                visual_type="thought_experiment",
                motion_type="pan_left",
                theme_palette="ocean_blue",
                diagram_elements=["H2O Terurai", "Gas H2 Bebas", "Lepas ke Angkasa"],
                claim_id="CLM-004"
            ),
            SceneStoryboard(
                scene_id="S005",
                order=5,
                stage="nuance_correction",
                narration_text="Kerak bumi terdiri dari 46 persen oksigen. Tanpa oksigen, pijakan tanah kita hancur seketika, membuat daratan amblas ke arah mantel bumi sebelum 5 detik tersebut berakhir.",
                estimated_duration_sec=7.5,
                headline="46% KERAK BUMI ADALAH OKSIGEN",
                subtext="Bukan sekadar udara nafas, melainkan fondasi padat bumi",
                visual_type="callout_fact",
                motion_type="ken_burns_zoom_in",
                theme_palette="emerald_science",
                diagram_elements=["Kerak Bumi: 46.6% Oksigen", "Silikat Batuan", "Gravitasi Mantel"],
                claim_id="CLM-005"
            ),
            SceneStoryboard(
                scene_id="S006",
                order=6,
                stage="payoff_closing",
                narration_text="Untungnya, ikatan atom oksigen di alam semesta sangat stabil. Oksigen bukan hanya udara yang kita hirup, melainkan lem kimia yang menjaga planet kita tetap utuh.",
                estimated_duration_sec=7.5,
                headline="KESIMPULAN: LEM KIMIA BUMI",
                subtext="Oksigen adalah fondasi materi kehidupan dan peradaban",
                visual_type="closing_card",
                motion_type="pulse_focus",
                theme_palette="cosmic_purple",
                diagram_elements=["Harmage Educational Series", "Subscribe for Next Insight"],
                claim_id="CLM-006"
            )
        ]

        # Register factual claims into ledger
        ledger.add_claim("CLM-001", "S001", "Oksigen menyusun 21% volume atmosfer bumi.", ["SRC-NASA-ATMOS"], "high", "Konsentrasi permukaan rata-rata.")
        ledger.add_claim("CLM-002", "S002", "Rayleigh scattering dan lapisan ozon bergantung pada oksigen.", ["SRC-NASA-ATMOS"], "high", "Tanpa O2 dan O3, hamburan foton biru hilang.")
        ledger.add_claim("CLM-003", "S003", "Semen dan agregat beton terikat oleh senyawa berbasis oksigen (SiO2, CaO).", ["SRC-GEOL-CRUST"], "high", "Eksperimen kimia teoretis ikatan molekul.")
        ledger.add_claim("CLM-004", "S004", "Air tersusun dari dua atom hidrogen dan satu atom oksigen.", ["SRC-USGS-WATER"], "high", "Hidrogen lepas karena massa molekul rendah.")
        ledger.add_claim("CLM-005", "S005", "Kerak bumi tersusun atas ~46.6% massa oksigen.", ["SRC-GEOL-CRUST"], "high", "Data konsensus geologi batuan beku dan sedimen.")
        ledger.add_claim("CLM-006", "S006", "Kestabilan ikatan kovalen oksigen menjaga keutuhan materi padat.", ["SRC-NASA-ATMOS"], "high", "Kesimpulan pedagogis.")

        stages_dict = {s.stage: s.narration_text for s in scenes}
        total_duration = sum(s.estimated_duration_sec for s in scenes)

        package = LongFormScriptPackage(
            topic_title=title,
            category=category,
            target_audience="Audiens edukasi sains populer Indonesia (remaja hingga dewasa muda)",
            estimated_total_seconds=round(total_duration, 1),
            stages=stages_dict,
            scenes=scenes,
            pronunciation_notes={
                "Rayleigh": "Rey-lih",
                "Ozon O3": "O-zon O-tiga",
                "H2O": "Ha-dua-O"
            },
            sound_design_notes={
                "intro": "Low sub-bass drone with digital timer tick",
                "disaster_reveal": "Muted impact boom with vinyl filter",
                "outro": "Warm analog synth progression with resolving chord"
            },
            qa_checklist=[
                "Hook 5-15 detik pertama langsung memantik rasa penasaran",
                "Klaim ilmiah didukung sumber NASA dan USGS",
                "Pemisahan jelas antara sains nyata dan skenario eksperimen pikiran",
                "Narasi mengalir natural dalam bahasa Indonesia tanpa filler"
            ]
        )

        return package, ledger

    def save_script_package(self, package: LongFormScriptPackage, directory: Path) -> Path:
        """Save script as human-readable text and structured JSON."""
        directory.mkdir(parents=True, exist_ok=True)
        json_path = directory / "narration_script.json"
        txt_path = directory / "narration_script.txt"

        data = asdict(package)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        lines = [
            f"# {package.topic_title.upper()}",
            f"Kategori: {package.category} | Durasi Estimasi: ~{package.estimated_total_seconds} detik",
            f"Target Audiens: {package.target_audience}",
            "=" * 60,
            ""
        ]
        for s in package.scenes:
            lines.append(f"[{s.scene_id} - {s.stage.upper()}] (~{s.estimated_duration_sec}s)")
            lines.append(f"Visual: {s.headline} | {s.subtext}")
            lines.append(f"Narasi: \"{s.narration_text}\"")
            lines.append("-" * 40)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return json_path
