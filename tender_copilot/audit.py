"""Reject-risk audit: the centerpiece.

Given an extracted tender, the bidder profile, and what was actually assembled,
return a ranked list of the ways this bid gets rejected, plus a safe-to-submit verdict.

The findings that matter most, in order of how often they sink real bids:
  1. A requirement satisfied nowhere in the assembled bundle.
  2. A *self-contradiction*: the bid claims a document is enclosed that isn't.
  3. Falling short of the technical-score gate.
  4. EMD / fee shortfalls or ambiguities.
Anything the extractor was unsure about goes to a human for review.
"""

from __future__ import annotations

from . import evaluate
from .schema import (
    CompanyProfile,
    Finding,
    RiskReport,
    Severity,
    Source,
    Submission,
    Tender,
)

CONFIDENCE_FLOOR = 0.75


def audit(tender: Tender, profile: CompanyProfile, sub: Submission) -> RiskReport:
    findings: list[Finding] = []
    present = sub.documents_present()

    # 1. Hard eligibility gates -------------------------------------------------
    for label, ok, detail in evaluate.eligibility(tender, profile):
        if not ok:
            findings.append(Finding(
                Severity.HIGH, "ELIG", f"Ineligible: {label}",
                f"{detail}. This is a pass/fail gate — the bid cannot win.",
                "Do not bid, or close the gap (e.g. via a JV partner) before submitting.",
            ))

    # 2. Required documents actually present -----------------------------------
    for req in tender.required():
        if req.doc_id is None or req.doc_id in present:
            continue
        on_checklist = req.source is Source.CHECKLIST
        findings.append(Finding(
            Severity.HIGH if on_checklist else Severity.MEDIUM,
            "MISSING",
            f"Missing: {req.description}",
            ("Named on the formal document checklist."
             if on_checklist else
             "Required only in eligibility prose — off the checklist, so easy to "
             "miss and enforcement varies by evaluator."),
            f"Attach the document satisfying '{req.id}' before upload.",
        ))

    # 3. Self-contradictions (claim vs. what's enclosed) -----------------------
    for claim in sub.claims:
        if claim.asserts_doc not in present:
            findings.append(Finding(
                Severity.HIGH, "CONTRADICTION",
                "Bid claims a document that isn't enclosed",
                f"The bid states: “{claim.text}” and points the evaluator to "
                f"{claim.points_to_slot} — but that document is not in the bundle. "
                "The bid also certifies all statements are true, so this invites "
                "the reviewer to look exactly where it's missing.",
                "Either attach the document, or strike the claim from the letter.",
            ))

    # 4. Technical score vs. gate ----------------------------------------------
    total, _rows = evaluate.score(tender, profile)
    if total < tender.gate:
        findings.append(Finding(
            Severity.HIGH, "SCORE",
            f"Below qualification gate ({total} < {tender.gate})",
            "Price bid is opened only for bidders above the gate.",
            "Raise scoring lines (turnover, capacity, tie-ups, methodology) above the gate.",
        ))

    # 5. EMD & document fee -----------------------------------------------------
    if sub.emd_paid < tender.emd:
        findings.append(Finding(
            Severity.HIGH, "EMD",
            f"EMD short: paid {_inr(sub.emd_paid)} of {_inr(tender.emd)}",
            "Bids without the prescribed EMD are rejected as non-responsive.",
            "Pay the full EMD online before the deadline.",
        ))
    if sub.fee_paid < tender.doc_fee:
        findings.append(Finding(
            Severity.MEDIUM, "FEE",
            f"Document-fee proof unclear: {_inr(sub.fee_paid)} vs RFP {_inr(tender.doc_fee)}",
            "The RFP body names a document fee that the payment proofs don't add up to. "
            "Could be a corrigendum for this call, or a missing receipt.",
            "Confirm the fee for this call and ensure the matching receipt is enclosed.",
        ))

    # 6. Fail loud on low-confidence extraction --------------------------------
    for req in tender.requirements:
        if req.confidence < CONFIDENCE_FLOOR:
            findings.append(Finding(
                Severity.LOW, "REVIEW",
                f"Low-confidence extraction: {req.description}",
                f"Parsed at {req.confidence:.0%} confidence.",
                "Have a human confirm this requirement against the source RFP.",
            ))

    findings.sort(key=lambda f: list(Severity).index(f.severity))
    verdict = _verdict(findings)
    return RiskReport(tender, verdict, total, tender.gate, findings)


def _verdict(findings: list[Finding]) -> str:
    """One question: is this bid safe to submit? Any HIGH or MEDIUM flag means no.

    A HIGH/MEDIUM covers every blocking case — an ineligibility or a below-gate
    score each raise a HIGH finding above, so counting the flags is enough.
    """
    unsafe = any(f.severity in (Severity.HIGH, Severity.MEDIUM) for f in findings)
    return "DO NOT SUBMIT" if unsafe else "SUBMIT"


def _inr(n: int) -> str:
    return "₹" + format(n, ",d")
