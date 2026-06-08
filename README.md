# tender-copilot

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-zero-success)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI](https://github.com/ajal2/tender-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/ajal2/tender-copilot/actions/workflows/ci.yml)

> Indian government RFPs are 100-page documents where a single buried clause
> disqualifies you. **tender-copilot reads one and returns: bid or skip, your
> score against the qualification gate, and the exact clauses you're about to be
> rejected on.** Validated on a live ₹3 Cr bid.

It is **not** a document generator. The PDFs are the boring byproduct. The
product is the *decision* — and the risk model that catches what a tired human,
or a one-shot LLM, misses.

---

## The hero output (real bid, zero install)

```text
BID REJECT-RISK REPORT  ·  704474-E1-168-MCS-2026-27
50 TPD C&D Waste Processing Plant + 10-yr O&M — Sangareddy Cluster (11 ULBs)
==============================================================================
VERDICT:  CONDITIONAL BID — eligible & over the gate, but fix the risks below first
SCORE:    80/100  (gate 70; margin +10)
RISKS:    1 HIGH, 2 MEDIUM, 1 LOW
==============================================================================
REJECT RISKS  (●HIGH ◐MEDIUM ○LOW)
  ● [HIGH]  Bid claims a document that isn't enclosed
            The compliance letter says "PF challan enclosed" and points to Slot 2
            — but it isn't there. The bid also certifies all statements true.
  ◐ [MEDIUM] Missing: recent PAID PF challan
            Required only in eligibility prose — off the checklist, easy to miss.
  ◐ [MEDIUM] Document-fee proof unclear: ₹2,000 vs RFP ₹11,800
  ○ [LOW]    Low-confidence extraction: positive net worth — needs a human
```

Full output, with the score breakdown and eligibility gates → **[examples/sangareddy_risk_report.md](examples/sangareddy_risk_report.md)**.
Every one of those four was a real defect on the actual submitted bid.

```bash
git clone <repo> && cd tender-copilot
python -m tender_copilot          # prints the report above. no deps, no keys.
```

---

## Why this is hard (and not just templating)

- **The RFP is adversarial.** 100+ pages, inconsistent formatting per department,
  obligations scattered across prose, tables, and annex indices.
- **Disqualifiers hide in prose.** The clause that sinks you is rarely on the
  checklist. The model ranks every requirement by *where it appears* (checklist
  vs. buried prose), because that changes the real risk.
- **Cross-document consistency.** The most catchable defect isn't a missing file
  — it's the bid *claiming* a file it didn't attach. The engine checks claims
  against what was actually assembled.
- **Wrong answers cost money.** A bad eligibility call forfeits the EMD. So the
  extractor carries per-field **confidence** and **fails loud** — anything it's
  unsure of goes to a human queue, never a silent guess.

---

## Architecture (the whole thing is five boxes + two human gates)

```
            RFP PDF
              │   extract.py   ── per-field confidence; low-confidence ─┐
              ▼                                                         │
        ┌───────────────┐     profile (who you are)                    │
        │ Tender schema │◄──────────────┐                              │
        └──────┬────────┘               │                              ▼
               │                  ┌──────────────┐              [ human gate 2 ]
               ▼                  │ evaluate.py  │  score + per-line gaps
        ┌───────────────┐        └──────┬───────┘
        │  audit.py     │◄── what you actually assembled (slots + claims)
        │  (the star)   │
        └──────┬────────┘
               ▼
     Reject-risk report  →  BID  /  CONDITIONAL  /  NO-BID
               ▲
        [ human gate 1 ]  bid / no-bid decision stays with the team
```

One configurable core; JBSS is just a profile + fixture. Point it at another
company or another tender by swapping JSON — nothing in the engine is hardcoded
to one bidder. Full walkthrough → **[docs/architecture.md](docs/architecture.md)**.

---

## Validated on a real bid

Run end-to-end against the **Sangareddy 50 TPD C&D tender** (Tender ID 704474),
a live ₹3 Cr municipal contract bid as a JBSS LLP + Lochab Stone joint venture.
The engine reproduced the qualification score (80/100, clearing the 70 gate) and
caught the compliance defects above before the deadline.
*(Bid submitted; award pending — this repo claims a validated **process**, not a win.)*
Story → **[docs/case-study-sangareddy.md](docs/case-study-sangareddy.md)** ·
Economics → **[docs/business-case.md](docs/business-case.md)**.

---

## Repo map

```
tender_copilot/      the engine
  schema.py            data model (the IP: requirements ranked by source)
  evaluate.py          rubric → score + gap reasons
  audit.py        ★    reject-risk + cross-doc contradiction + fail-loud
  extract.py           JSON loaders; PDF→schema is the documented research stage
  report.py            renders the hero output
fixtures/            Sangareddy tender + submission (reviewed extraction output)
profiles/            synthetic, public-safe company capability profile
evals/               back-test: run on real tenders, assert the catches
docs/                architecture · business case · case study
```

## Scope & honesty

Public-safe by design: **no PANs, signatures, financial statements, or
notarised documents** live here. The profile is synthetic; fixtures carry only
eligibility-relevant facts from the public tender. PDF extraction is the open
research surface and is deliberately left as a human-reviewed stage rather than
faked. See [evals/](evals/) for what's actually measured.

MIT licensed.
