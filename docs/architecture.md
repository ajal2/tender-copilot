# Architecture

The entire system is **five stages and two human gates**. If you can draw this
from memory you can explain the project cold.

```
        RFP PDF
          │  (1) EXTRACT          per-field confidence
          ▼                       low-confidence → human review queue  ──► gate 2
   ┌──────────────┐
   │ Tender schema│   requirements (ranked by SOURCE) · scoring rubric · EMD/fee/gate
   └──────┬───────┘
          │                 ┌─ CompanyProfile (who you are: turnover, capacity, docs)
          ▼                 │
   (2) EVALUATE ◄───────────┘   → technical score + per-line gap reasons
          │
          ▼
   (3) AUDIT ◄── Submission (what you actually assembled: slots + claims)
          │        · required-doc coverage
          │        · claim ↔ reality contradiction check
          │        · score vs gate · EMD/fee · fail-loud on low confidence
          ▼
   (4) RISK REPORT  →  verdict: BID / CONDITIONAL / NO-BID      ──► gate 1
          │
          ▼
   (5) ASSEMBLE  (downstream, commodity: build & brand the bundle)
```

**Gate 1 — bid / no-bid.** The engine eliminates the obvious (eligibility gates
fail → NO-BID; clean → BID). The genuinely judgemental middle (CONDITIONAL —
eligible and over the gate, but with curable risks) is handed to the team. We do
not automate the decision to risk an EMD.

**Gate 2 — extraction review.** Any field parsed below the confidence floor is
surfaced, never trusted. The fixtures in `fixtures/` are the *reviewed* output of
stage 1.

## The one idea that makes it more than a checklist

Every `Requirement` carries a `source`: `CHECKLIST` (named in the formal document
list / annexure index) or `PROSE` (buried in an eligibility paragraph). The same
missing document is ranked **HIGH** if it's on the checklist and **MEDIUM** if
it's only in prose — because that's how real evaluators behave, and because the
prose-buried clause is the one humans actually miss. This single field is why the
output reads like judgement, not a `grep` for annexure numbers.

## Data model (`schema.py`)

- **`Tender`** — `requirements`, `scoring`, `minimums` (hard gates), `emd`,
  `doc_fee`, `gate`. The structured form of a messy PDF.
- **`Requirement`** — `id`, `description`, `kind`, **`source`**, `doc_id`,
  `confidence`. `doc_id` links a demand to the artifact that satisfies it.
- **`ScoringItem`** — value-driven (`bands`: value → marks) or presence-driven
  (`fixed`). Produces an explainable, line-by-line score.
- **`CompanyProfile`** — `metrics` (turnover, capacity…), `registrations`,
  `documents_available` (what you *hold*).
- **`Submission`** — `slots` (what you *assembled*), `claims`, `emd_paid`,
  `fee_paid`. The gap between `documents_available` and what's in `slots` is
  exactly how "you own the PF challan but didn't attach it" gets caught.
- **`Claim`** — a statement the bid makes about itself; checked against reality.

## Audit logic (`audit.py`) — order matters

1. **Hard eligibility gates** — fail one → `NO-BID` (turnover, capacity…).
2. **Required-doc coverage** — missing → HIGH (checklist) / MEDIUM (prose).
3. **Contradictions** — a claim asserts a doc that isn't enclosed → HIGH.
4. **Score vs gate** — below the gate → HIGH (price bid never opens).
5. **EMD / fee** — shortfall or unreconciled amount → HIGH / MEDIUM.
6. **Fail-loud** — any low-confidence requirement → LOW review item.

Verdict: `NO-BID` if a gate fails or score < gate; else `CONDITIONAL` if any
HIGH/MEDIUM remains; else `BID`.

## Why it generalises

Nothing in `tender_copilot/` mentions JBSS or Sangareddy. A new tender is a new
`*.tender.json`; a new bidder is a new profile. The engine is the deployable
core; the JSON is the per-client/per-tender config — the forward-deployed
pattern of one system adapted to many messy realities.

## Deliberately out of scope

No UI, no multi-tenant SaaS, no autonomous bidding. PDF→schema extraction is the
hard research surface and is left explicit, not faked. Bundle assembly/branding
exists downstream but is commodity and intentionally thin.
