# Evals

Two things are measured here: **does the engine catch the defects a human found
on real bids**, and (as the corpus grows) **how accurately does extraction turn a
raw RFP into the schema**.

## Reject-risk regression (live now)

`test_audit.py` runs the full audit on the Sangareddy fixture and asserts the
real findings: the self-contradiction, the buried-prose EPF clause, the fee
ambiguity, the fail-loud review item, and the 80/100 score over the 70 gate. If a
change ever stops catching these, CI goes red.

```bash
python -m unittest evals.test_audit -v      # from repo root
```

## Back-test corpus

| Tender | Value | Labelled | Defects engine caught that a checklist pass missed |
|---|---|---|---|
| Sangareddy 50 TPD C&D | ₹3.0 Cr | yes | self-contradiction · buried EPF clause · fee gap |
| Mathura 50 TPD C&D | n/a | planned | n/a |
| Bidar 50 TPD C&D | n/a | planned | n/a |

**Honest status:** N = 1 fully labelled today. The harness is built to add past
JBSS tenders as labelled fixtures; each new one measures both reject-risk recall
and extraction precision/recall against a hand-labelled gold schema. No accuracy
number is claimed beyond what's in the table. Extraction over messy scanned PDFs
is the open research surface, and inflating it would defeat the point.
