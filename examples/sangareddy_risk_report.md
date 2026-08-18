# Hero output — pre-submission audit on a real bid

This is the **verbatim output** of `python -m tender_copilot` against the bundled
Sangareddy fixture (a live ₹3 Cr government tender). No install, no API key.

```text
PRE-SUBMISSION AUDIT  ·  704474-E1-168-MCS-2026-27
50 TPD C&D Waste Processing Plant + 10-yr O&M — Sangareddy Cluster (11 ULBs)
Authority: Sangareddy Municipality (MCS), Telangana   Est. value: ₹30,000,000
==============================================================================
SAFE TO SUBMIT?   NO — fix the flags below before this goes out
SCORE:    80/100  (gate 70; margin +10)
RISKS:    1 HIGH, 2 MEDIUM, 1 LOW
==============================================================================

ELIGIBILITY GATES
  [PASS] Avg annual turnover >= Rs 5 Cr (5-yr, CA-certified)  (11.33 vs min 5)
  [PASS] C&D processing capacity >= 50 TPD (route i(b), cumulative)  (100 vs min 50)

SCORE BREAKDOWN
   25  Annual turnover (Rs Cr)            avg_turnover_cr=11.33 -> 25/30; reach ≥ 15 (30 marks) for full 30
   30  C&D technical capacity (TPD)       cumulative_capacity_tpd=100 -> 30/45; reach ≥ 150 (45 marks) for full 45
    5  Tie-ups / MoUs                     present
   20  Approach & methodology (presentation) present

REJECT RISKS  (●HIGH ◐MEDIUM ○LOW)
  ● [HIGH] Bid claims a document that isn't enclosed
      why: The bid states: “Lead Member holds EPF & ESIC registration; recent paid PF challan enclosed.” and points the evaluator to Slot 2 - GST & PAN — but that document is not in the bundle. The bid also certifies all statements are true, so this invites the reviewer to look exactly where it's missing.
      fix: Either attach the document, or strike the claim from the letter.
  ◐ [MEDIUM] Missing: EPF account + copy of recent PAID PF challan
      why: Required only in eligibility prose — off the checklist, so easy to miss and enforcement varies by evaluator.
      fix: Attach the document satisfying 'epf_challan' before upload.
  ◐ [MEDIUM] Document-fee proof unclear: ₹2,000 vs RFP ₹11,800
      why: The RFP body names a document fee that the payment proofs don't add up to. Could be a corrigendum for this call, or a missing receipt.
      fix: Confirm the fee for this call and ensure the matching receipt is enclosed.
  ○ [LOW] Low-confidence extraction: Positive net worth in last audited FY
      why: Parsed at 65% confidence.
      fix: Have a human confirm this requirement against the source RFP.
```

## Why each finding matters

- **The HIGH is a self-contradiction, not just a missing file.** The bid's own
  compliance letter says the PF challan is enclosed and points to Slot 2 — where
  it isn't. Since the bid also certifies every statement is true, that's the
  single most catchable defect a human evaluator looks for. The engine finds it
  by cross-checking *claims* against *what was actually assembled*.
- **The buried-prose disqualifier.** The EPF challan is required in one
  eligibility paragraph, on no checklist and in no annexure index — exactly the
  kind of line that sinks otherwise-strong bids. The engine ranks it by *where
  in the RFP it appears*, not just whether it's present.
- **The fee ambiguity** surfaces a number that doesn't reconcile, and says so,
  instead of guessing.
- **Fail-loud.** The net-worth line was parsed at 65% confidence, so it's flagged
  for a human rather than silently trusted. In a domain where a wrong call costs
  a forfeited EMD, the system never pretends to be sure when it isn't.

All four were real findings on the actual bid.
