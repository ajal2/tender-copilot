# Business case

## The problem

Indian MSMEs that build and operate municipal infrastructure live or die by
government tenders. Each bid means reading a 100+ page RFP, decoding scattered
eligibility rules, assembling 10+ annexures and proofs, and staking a real
Earnest Money Deposit. The work is manual, slow, and unforgiving: one missed
clause is an outright rejection, and the EMD plus the effort are gone.

Most small firms cope by paying tender consultants per bid, or by burning senior
time. Both scale badly — so firms bid on *fewer* tenders than they're eligible
for, and still get knocked out on technicalities.

## Where the value is (and isn't)

tender-copilot does **not** claim to make you win a tender — you win on price
(L1) and eligibility. It moves two levers that a small team actually controls:

1. **Throughput.** Bid/no-bid triage drops from a day of reading to minutes, so a
   two-person team can pursue the tenders they're eligible for instead of
   cherry-picking three.
2. **Rejection-avoidance.** The reject-risk audit catches the technical defects
   that forfeit an EMD and a month of work — buried-prose requirements, missing
   proofs, and the bid contradicting itself.

## Illustrative unit economics

*Plug your real numbers — these are a model, not a claim.*

| Item | Manual | With copilot |
|---|---|---|
| RFP read + eligibility triage | ~0.5–1 day | minutes |
| Consultant / senior time per bid | ₹25k–₹1L | mostly avoided |
| Tenders pursued per quarter (2-person team) | ~3 | 3× more, same headcount |
| Technical-rejection rate | a real, recurring loss | caught pre-submission |
| EMD at risk per bid (Sangareddy) | ₹3,00,000 | protected by the audit |

The system pays for itself by **preventing a single avoidable rejection**: one
forfeited ₹3,00,000 EMD, or one wasted ₹3 Cr-scale bid effort, dwarfs its cost.
Everything above that — the extra tenders pursued — is upside.

## Market

Every Indian municipality, ULB, and PSU runs tenders through e-procurement
portals (Telangana eProc, GeM, state portals) with the same structure: an
adversarial RFP, an eligibility gate, an EMD, a technical score. The core
generalises across them by swapping config, which is why this is a *product*
shape, not a one-client script.
