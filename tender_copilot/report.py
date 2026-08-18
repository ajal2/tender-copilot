"""Render a RiskReport as a terminal/markdown block (the hero output)."""

from __future__ import annotations

from . import evaluate
from .schema import CompanyProfile, RiskReport, Severity, Tender

_ICON = {Severity.HIGH: "●", Severity.MEDIUM: "◐", Severity.LOW: "○", Severity.INFO: "·"}
_ANSWER = {
    "SUBMIT": "YES — no blocking flags",
    "DO NOT SUBMIT": "NO — fix the flags below before this goes out",
}


def render(report: RiskReport, profile: CompanyProfile) -> str:
    t = report.tender
    L: list[str] = []
    L.append(f"PRE-SUBMISSION AUDIT  ·  {t.id}")
    L.append(f"{t.title}")
    L.append(f"Authority: {t.authority}   Est. value: ₹{t.estimated_cost:,}")
    L.append("=" * 78)
    L.append(f"SAFE TO SUBMIT?   {_ANSWER[report.verdict]}")
    L.append(
        f"SCORE:    {report.score}/{sum(s.max_marks for s in t.scoring)}  "
        f"(gate {report.gate}; margin {report.margin:+d})"
    )
    counts = ", ".join(
        f"{len(report.by_severity(s))} {s.value}"
        for s in (Severity.HIGH, Severity.MEDIUM, Severity.LOW)
        if report.by_severity(s)
    )
    L.append(f"RISKS:    {counts or 'none'}")
    L.append("=" * 78)

    L.append("\nELIGIBILITY GATES")
    for label, ok, detail in evaluate.eligibility(t, profile):
        L.append(f"  [{'PASS' if ok else 'FAIL'}] {label}  ({detail})")

    L.append("\nSCORE BREAKDOWN")
    _total, rows = evaluate.score(t, profile)
    for name, marks, reason in rows:
        L.append(f"  {marks:>3}  {name:<34} {reason}")

    L.append("\nREJECT RISKS  (●HIGH ◐MEDIUM ○LOW)")
    if not report.findings:
        L.append("  none")
    for i, f in enumerate(report.findings, 1):
        L.append(f"  {_ICON[f.severity]} [{f.severity.value}] {f.title}")
        L.append(f"      why: {f.detail}")
        L.append(f"      fix: {f.fix}")
    return "\n".join(L)
