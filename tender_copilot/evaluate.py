"""Scoring engine: company profile + RFP rubric -> marks, with gap reasons.

Deliberately boring and deterministic. The score must be explainable line by
line, because an evaluator (and an interviewer) will ask "why 25 and not 30?".
"""

from __future__ import annotations

from .schema import CompanyProfile, ScoringItem, Tender


def _band_marks(item: ScoringItem, value: float) -> tuple[int, str]:
    for low, high, marks in item.bands:
        if low <= value < high:
            nxt = _next_band(item, marks)
            reason = f"{item.metric}={value:g} -> {marks}/{item.max_marks}"
            if nxt:
                reason += f"; reach {nxt} for full {item.max_marks}"
            return marks, reason
    return 0, f"{item.metric}={value:g} -> 0/{item.max_marks} (below first band)"


def _next_band(item: ScoringItem, current: int) -> str | None:
    higher = [b for b in item.bands if b[2] > current]
    if not higher:
        return None
    low, _, marks = min(higher, key=lambda b: b[2])
    return f"≥ {low:g} ({marks} marks)"


def score(tender: Tender, profile: CompanyProfile) -> tuple[int, list[tuple[str, int, str]]]:
    """Return (total, [(item_name, marks, reason)])."""
    rows: list[tuple[str, int, str]] = []
    total = 0
    for item in tender.scoring:
        if item.fixed is not None:
            has = item.id in profile.documents_available or item.metric in profile.metrics
            marks = item.fixed if has else 0
            reason = "present" if has else "missing (0)"
        else:
            value = profile.metrics.get(item.metric, 0.0)
            marks, reason = _band_marks(item, value)
        total += marks
        rows.append((item.name, marks, reason))
    return total, rows


def eligibility(tender: Tender, profile: CompanyProfile) -> list[tuple[str, bool, str]]:
    """Check the hard gates. Failing any one means the bid cannot win."""
    out: list[tuple[str, bool, str]] = []
    for metric, minimum, label in tender.minimums:
        value = profile.metrics.get(metric, 0.0)
        out.append((label, value >= minimum, f"{value:g} vs min {minimum:g}"))
    return out
