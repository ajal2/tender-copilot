"""Regression + proof: the engine must catch the real Sangareddy defects.

These assertions encode what a human reviewer found on the live bid. If a future
change stops catching the self-contradiction or the buried EPF clause, this fails.

Run:  python -m unittest evals.test_audit      (from the repo root)
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tender_copilot import run  # noqa: E402
from tender_copilot.schema import Severity  # noqa: E402

TENDER = ROOT / "fixtures" / "sangareddy.tender.json"
PROFILE = ROOT / "profiles" / "jbss_jv.example.json"
SUBMISSION = ROOT / "fixtures" / "sangareddy.submission.json"


class SangareddyAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.profile = run(str(TENDER), str(PROFILE), str(SUBMISSION))

    def codes(self, severity=None):
        fs = self.report.findings
        if severity:
            fs = [f for f in fs if f.severity == severity]
        return {f.code for f in fs}

    def test_eligible_and_over_the_gate(self):
        self.assertEqual(self.report.score, 80)
        self.assertGreaterEqual(self.report.score, self.report.gate)
        self.assertEqual(self.report.verdict, "CONDITIONAL")

    def test_catches_self_contradiction(self):
        # the headline finding: bid claims a doc it didn't enclose
        self.assertIn("CONTRADICTION", self.codes(Severity.HIGH))

    def test_catches_buried_prose_requirement(self):
        # EPF challan is required only in prose -> MEDIUM, not silently dropped
        self.assertIn("MISSING", self.codes(Severity.MEDIUM))

    def test_flags_fee_ambiguity(self):
        self.assertIn("FEE", self.codes())

    def test_fails_loud_on_low_confidence(self):
        self.assertIn("REVIEW", self.codes(Severity.LOW))

    def test_no_false_eligibility_block(self):
        # turnover & capacity gates pass, so no NO-BID
        self.assertNotEqual(self.report.verdict, "NO-BID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
