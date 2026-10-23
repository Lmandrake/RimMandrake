#!/usr/bin/env python3
"""Launcher for the art-eval tools, which live in src/RimMandrake/Utils/art_eval/ (one copy, imported by the repo):

    python3 skills/rimworld-art-evaluation/scripts/art_eval.py runner run --pilot RM_Ssurr:B --run-id x --test
    python3 skills/rimworld-art-evaluation/scripts/art_eval.py shadow build <run id>
    python3 skills/rimworld-art-evaluation/scripts/art_eval.py ledger list
    python3 skills/rimworld-art-evaluation/scripts/art_eval.py cards pilot RM_Huldu:C --out <dir>
    python3 skills/rimworld-art-evaluation/scripts/art_eval.py selftest
"""
import runpy
import sys
from pathlib import Path

TOOLS = {"runner": "runner.py", "shadow": "shadow.py", "ledger": "ledger.py", "cards": "cards.py",
         "selftest": "selftest_art_eval.py"}
SRC = Path(__file__).resolve().parents[3] / "src/RimMandrake/Utils/art_eval"

if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
    sys.exit(__doc__)
tool = SRC / TOOLS[sys.argv[1]]
sys.argv = [str(tool)] + sys.argv[2:]
sys.path.insert(0, str(SRC))
runpy.run_path(str(tool), run_name="__main__")
