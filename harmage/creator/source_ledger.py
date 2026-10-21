"""Research & Source Ledger for YouTube Long-Form Factual Integrity.

Maintains verifiable, traceable evidence linked directly to script claims:
- Scientific institutions, peer-reviewed data, and space agencies
- Historical evidence vs popular misconceptions
- Respectful comparative religious traditions
- Clear separation between established science and thought experiment fiction
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


@dataclass
class SourceEntry:
    source_id: str
    url: str
    publisher_author: str
    publication_year: Optional[int]
    access_date: str
    evidence_type: str  # e.g., 'academic', 'space_agency', 'historical_archaeology', 'peer_reviewed'
    credibility_rating: str  # 'tier_1_institution', 'academic_journal', 'historical_record'
    notes: str


@dataclass
class FactualClaim:
    claim_id: str
    scene_id: str
    claim_text: str
    source_ids: List[str]
    confidence_level: str  # 'high', 'moderate', 'theoretical'
    nuance_note: str       # Boundaries, caveats, or thought experiment conditions


class SourceLedger:
    """Manages fact-check evidence ledger for a specific long-form video production."""

    def __init__(self, topic_title: str):
        self.topic_title = topic_title
        self.sources: Dict[str, SourceEntry] = {}
        self.claims: List[FactualClaim] = []

    def add_source(
        self,
        source_id: str,
        url: str,
        publisher_author: str,
        evidence_type: str,
        publication_year: Optional[int] = None,
        credibility_rating: str = "tier_1_institution",
        notes: str = ""
    ) -> SourceEntry:
        entry = SourceEntry(
            source_id=source_id,
            url=url,
            publisher_author=publisher_author,
            publication_year=publication_year,
            access_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            evidence_type=evidence_type,
            credibility_rating=credibility_rating,
            notes=notes
        )
        self.sources[source_id] = entry
        return entry

    def add_claim(
        self,
        claim_id: str,
        scene_id: str,
        claim_text: str,
        source_ids: List[str],
        confidence_level: str = "high",
        nuance_note: str = ""
    ) -> FactualClaim:
        # Validate that referenced sources exist
        for sid in source_ids:
            if sid not in self.sources:
                raise ValueError(f"Source ID '{sid}' not found in ledger")
        claim = FactualClaim(
            claim_id=claim_id,
            scene_id=scene_id,
            claim_text=claim_text,
            source_ids=source_ids,
            confidence_level=confidence_level,
            nuance_note=nuance_note
        )
        self.claims.append(claim)
        return claim

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic_title": self.topic_title,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_sources": len(self.sources),
            "total_claims": len(self.claims),
            "sources": {k: asdict(v) for k, v in self.sources.items()},
            "claims": [asdict(c) for c in self.claims]
        }

    def save_to_file(self, filepath: Path) -> Path:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        return filepath

    def validate_factual_integrity(self) -> Dict[str, Any]:
        """Run QA check on fact-checking integrity before visual production."""
        missing_sources = []
        low_confidence_unnuanced = []

        for claim in self.claims:
            if not claim.source_ids:
                missing_sources.append(claim.claim_id)
            if claim.confidence_level in ("moderate", "theoretical") and not claim.nuance_note:
                low_confidence_unnuanced.append(claim.claim_id)

        passed = len(missing_sources) == 0 and len(low_confidence_unnuanced) == 0
        return {
            "passed": passed,
            "total_claims": len(self.claims),
            "verified_claims": len(self.claims) - len(missing_sources),
            "missing_sources": missing_sources,
            "unnuanced_claims": low_confidence_unnuanced,
            "qa_status": "APPROVED" if passed else "REVISION_REQUIRED"
        }
