"""Load a tender / profile / submission from JSON, and (eventually) from a PDF.

Honest boundary: turning a 100-page scanned RFP into the structured `Tender`
above is the hard, unreliable part. We do NOT pretend it is solved. The pipeline
treats extraction as a human-reviewed stage: every field carries a confidence,
and anything below the floor is surfaced, never silently trusted. The JSON
fixtures in `fixtures/` are the *reviewed* output of that stage.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import (
    Claim,
    CompanyProfile,
    Requirement,
    ScoringItem,
    Source,
    Submission,
    Tender,
)


def load_tender(path: str | Path) -> Tender:
    d = json.loads(Path(path).read_text())
    reqs = tuple(
        Requirement(
            id=r["id"], description=r["description"],
            source=Source(r["source"]), mandatory=r.get("mandatory", True),
            doc_id=r.get("doc_id"), confidence=r.get("confidence", 1.0),
        )
        for r in d["requirements"]
    )
    scoring = tuple(
        ScoringItem(
            id=s["id"], name=s["name"], max_marks=s["max_marks"],
            metric=s.get("metric"),
            bands=tuple(tuple(b) for b in s.get("bands", [])),
            fixed=s.get("fixed"),
        )
        for s in d["scoring"]
    )
    return Tender(
        id=d["id"], title=d["title"], authority=d["authority"],
        estimated_cost=d["estimated_cost"], emd=d["emd"], doc_fee=d["doc_fee"],
        gate=d["gate"], requirements=reqs, scoring=scoring,
        notes=tuple(d.get("notes", [])),
        minimums=tuple(tuple(m) for m in d.get("minimums", [])),
    )


def load_profile(path: str | Path) -> CompanyProfile:
    d = json.loads(Path(path).read_text())
    return CompanyProfile(
        name=d["name"],
        metrics=d.get("metrics", {}),
        documents_available=set(d.get("documents_available", [])),
    )


def load_submission(path: str | Path) -> Submission:
    d = json.loads(Path(path).read_text())
    claims = tuple(
        Claim(text=c["text"], asserts_doc=c["asserts_doc"],
              points_to_slot=c["points_to_slot"])
        for c in d.get("claims", [])
    )
    return Submission(
        slots=d.get("slots", {}), claims=claims,
        emd_paid=d.get("emd_paid", 0), fee_paid=d.get("fee_paid", 0),
    )


def extract_from_pdf(pdf_path: str | Path) -> Tender:  # pragma: no cover
    """Parse a raw RFP PDF into a Tender. Intentionally not implemented here.

    This is the research surface of the project: layout-aware parsing of messy,
    inconsistent government PDFs, with per-field confidence and a human-review
    queue. Treat the JSON fixtures as the reviewed output of this stage.
    """
    raise NotImplementedError(
        "PDF extraction is the human-reviewed research stage; "
        "load the reviewed fixture with load_tender() instead."
    )
