"""Core data model for tender-copilot.

A tender is modelled as a set of *requirements* a bidder must satisfy, a
*scoring rubric* that gates progression, and the commercial facts (EMD, fee,
deadline). The interesting field is `source`: where in the RFP a requirement
actually appears. Government RFPs hide hard disqualifiers in prose, off the
official checklist, and that distinction drives how we rank risk.

Pure stdlib on purpose: the repo must run anywhere with `python` and no install.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    HIGH = "HIGH"      # bid-killing if a strict evaluator catches it
    MEDIUM = "MEDIUM"  # real risk, usually curable via a clarification
    LOW = "LOW"        # cosmetic / needs-a-human review
    INFO = "INFO"


class Source(str, Enum):
    """Where in the RFP a requirement appears. This is the crux."""
    CHECKLIST = "checklist"  # named in the formal document list / annexure index
    PROSE = "prose"          # buried in an eligibility paragraph, on no checklist


class Kind(str, Enum):
    DOCUMENT = "document"
    ELIGIBILITY = "eligibility"
    EMD = "emd"
    FEE = "fee"


@dataclass(frozen=True)
class Requirement:
    """A single thing the RFP demands. `doc_id` links it to a deliverable."""
    id: str
    description: str
    kind: Kind
    source: Source
    mandatory: bool = True
    doc_id: Optional[str] = None     # the artifact that satisfies it
    confidence: float = 1.0          # extractor confidence; < 0.75 => human review


@dataclass(frozen=True)
class ScoringItem:
    """One row of the technical-evaluation matrix.

    `bands` maps a measured value to marks, e.g. turnover -> marks.
    Use either `bands` (value-driven) or `fixed` (presence-driven, e.g. a tie-up).
    """
    id: str
    name: str
    max_marks: int
    metric: Optional[str] = None                 # key looked up on the profile
    bands: tuple[tuple[float, float, int], ...] = ()  # (low, high, marks)
    fixed: Optional[int] = None


@dataclass(frozen=True)
class Tender:
    id: str
    title: str
    authority: str
    estimated_cost: int
    emd: int
    doc_fee: int
    gate: int                                   # min technical score to open price bid
    requirements: tuple[Requirement, ...]
    scoring: tuple[ScoringItem, ...]
    notes: tuple[str, ...] = ()
    # hard eligibility gates: (metric, minimum, human label). Fail one => NO-BID.
    minimums: tuple[tuple[str, float, str], ...] = ()

    def required(self) -> tuple[Requirement, ...]:
        return tuple(r for r in self.requirements if r.mandatory)


@dataclass
class CompanyProfile:
    """What the bidder (or JV) actually is and holds."""
    name: str
    is_jv: bool = False
    # metric -> value (e.g. avg_turnover_cr, cumulative_capacity_tpd)
    metrics: dict[str, float] = field(default_factory=dict)
    registrations: set[str] = field(default_factory=set)
    documents_available: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Claim:
    """A statement the bid makes about itself (e.g. in a compliance letter).

    If a claim asserts a document is enclosed and it isn't, that is a
    self-inflicted contradiction, the highest-value thing this engine finds.
    """
    text: str
    asserts_doc: str
    points_to_slot: str


@dataclass
class Submission:
    """What was actually assembled for upload, vs. what was claimed."""
    slots: dict[str, list[str]] = field(default_factory=dict)  # slot -> [doc_id]
    claims: tuple[Claim, ...] = ()
    emd_paid: int = 0
    fee_paid: int = 0

    def documents_present(self) -> set[str]:
        return {doc for docs in self.slots.values() for doc in docs}


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    title: str
    detail: str
    fix: str


@dataclass
class RiskReport:
    tender: Tender
    verdict: str            # BID / CONDITIONAL / NO-BID
    score: int
    gate: int
    findings: list[Finding]

    @property
    def margin(self) -> int:
        return self.score - self.gate

    def by_severity(self, sev: Severity) -> list[Finding]:
        return [f for f in self.findings if f.severity == sev]
