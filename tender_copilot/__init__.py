"""tender-copilot: audit a government bid before it goes out — is it safe to
submit? Returns a SUBMIT / DO NOT SUBMIT verdict, the score against the
qualification gate, and the exact clauses you're about to be rejected on.

Public API:
    from tender_copilot import run
    report, profile = run(tender_json, profile_json, submission_json)
"""

from __future__ import annotations

from .audit import audit
from .extract import load_profile, load_submission, load_tender
from .report import render
from .schema import RiskReport, CompanyProfile

__version__ = "0.1.0"
__all__ = ["run", "audit", "render", "RiskReport", "CompanyProfile"]


def run(tender_json: str, profile_json: str, submission_json: str):
    """Load the three inputs, run the audit, return (RiskReport, CompanyProfile)."""
    tender = load_tender(tender_json)
    profile = load_profile(profile_json)
    submission = load_submission(submission_json)
    return audit(tender, profile, submission), profile
