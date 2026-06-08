"""CLI:  python -m tender_copilot [tender.json profile.json submission.json]

With no args it runs the bundled Sangareddy fixture — so a reviewer can clone
and see the hero output in one command, zero install.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import run
from .report import render

_ROOT = Path(__file__).resolve().parent.parent
_DEFAULTS = (
    _ROOT / "fixtures" / "sangareddy.tender.json",
    _ROOT / "profiles" / "jbss_jv.example.json",
    _ROOT / "fixtures" / "sangareddy.submission.json",
)


def main(argv: list[str]) -> int:
    paths = argv[1:] if len(argv) == 4 else [str(p) for p in _DEFAULTS]
    report, profile = run(*paths)
    print(render(report, profile))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
