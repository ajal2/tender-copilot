# tender-copilot

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-zero-success)
![License](https://img.shields.io/badge/license-MIT-green)
[![CI](https://github.com/ajal2/tender-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/ajal2/tender-copilot/actions/workflows/ci.yml)

> Indian government bids run to a hundred pages, and a single buried clause gets
> you rejected. **tender-copilot audits a bid before it goes out and answers one
> question: is this safe to submit?** It returns SUBMIT / DO NOT SUBMIT, your
> score against the qualification gate, and the exact clauses you're about to be
> rejected on. Validated on a live ₹3 Cr bid.

Plenty of tools *write* tender documents. This one is the deterministic safety
check at the end — the reject-risk audit that catches what a tired human misses.

---

## The hero output (real bid, zero install)

```text
PRE-SUBMISSION AUDIT  ·  704474-E1-168-MCS-2026-27
50 TPD C&D Waste Processing Plant + 10-yr O&M — Sangareddy Cluster (11 ULBs)
==============================================================================
SAFE TO SUBMIT?   NO — fix the flags below before this goes out
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

Full output, with the score breakdown and eligibility gates, is in **[examples/sangareddy_risk_report.md](examples/sangareddy_risk_report.md)**.
Every one of those four was a real defect on the actual submitted bid.

```bash
git clone https://github.com/ajal2/tender-copilot.git && cd tender-copilot
python -m tender_copilot          # prints the report above. no deps, no keys.
```

---

## Why this is hard (and not just templating)

- The RFP works against you: 100+ pages, formatting that changes by department,
  obligations scattered across prose, tables, and annex indices.
- The clause that sinks you is rarely on the checklist, which is why every
  requirement gets ranked by where it appears (checklist vs. buried prose).
  That placement changes the real risk.
- The most catchable defect isn't even a missing file. It's the bid *claiming*
  a file it didn't attach, so the engine checks every claim against what was
  actually assembled.
- Wrong answers cost money here. A rejected bid wastes the non-refundable
  tender fee and days of senior time, so
  the extractor carries per-field confidence and anything it's unsure of goes
  to a human queue instead of a guess.

---

## How a bid flows through it

```mermaid
flowchart TB
    A[RFP] --> B[AI reads into a requirements list]
    B --> C[Human verifies]
    C --> D[Assemble the bundle]
    D --> E[Audit ①: what's still missing?]
    E --> F[Compile]
    F --> G[Audit ②: safe to submit?]
```

The same deterministic audit runs at two moments: **early**, on a half-built
bundle, to show what's still missing while there's time to fix it; and **final**,
as the safety gate before anything goes out. The AI only sits at the front —
reading the RFP into structured facts a human verifies; anything low-confidence
goes to the human. No model touches the verdict.

One configurable core; JBSS is just a profile + fixture. Point it at another
company or another tender by swapping JSON. Nothing in the engine is hardcoded
to one bidder. Full walkthrough in **[docs/architecture.md](docs/architecture.md)**.

---

## Built from a real bid

The test case is the **Sangareddy 50 TPD C&D tender** (Tender ID 704474), a
live ₹3 Cr municipal contract bid as a JBSS LLP + Lochab Stone joint venture.
The engine was built after that bid went in, encoding it as the first labelled
fixture: it matches the 80/100 score we computed by hand (gate 70), and it
reproduces, under test, the four compliance defects that human review caught
on the real bid. Future bids get from the engine what this one got by hand.
*(The bid won. The engine takes no credit for that: it did not exist when the
bid went in.)*
The story is in **[docs/case-study-sangareddy.md](docs/case-study-sangareddy.md)**
and the economics in **[docs/business-case.md](docs/business-case.md)**.

---

## Repo map

```
tender_copilot/      the engine
  schema.py            data model (the core idea: requirements ranked by where they appear)
  evaluate.py          rubric → score + gap reasons
  audit.py        ★    the six checks → SAFE TO SUBMIT / DO NOT SUBMIT
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
