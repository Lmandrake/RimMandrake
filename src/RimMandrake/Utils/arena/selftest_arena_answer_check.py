#!/usr/bin/env python3
"""selftest_arena_answer_check: the plain answer-store check (arena_answer_check.py) passes on the real sandbox and
FAILS when the sandbox stops masking /home and /mnt (proof the instrument can see a readable store)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import arena_answer_check as AC  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    rows, ctl = AC.run()
    check(ctl, "control file in the arm scratch is readable inside the sandbox")
    bad = [r["what"] for r in rows if r["result"] in ("FAIL", "VOID")]
    check(not bad, "no answer store readable from inside the arm sandbox (%s)" % bad)
    must = {"arena harness event token", "live clone foundry"}
    measured = {r["what"] for r in rows if r["result"] == "PASS"}
    check(must <= measured, "token and live clone are measured, not skipped (%s)" % sorted(must - measured))
    rows, ctl = AC.run(_drop=("/home", "/mnt"))
    leaked = {r["what"] for r in rows if r["result"] == "FAIL"}
    check(ctl and must <= leaked, "mutation: /home and /mnt unmasked -> the check FAILS on them (%s)" % sorted(leaked))
    check("D:\\ mirror" in leaked or not Path("/mnt/d/Luke/dev/RimMandrake/CLAUDE.md").exists(),
          "mutation: the D:\\ mirror row turns FAIL too")
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
