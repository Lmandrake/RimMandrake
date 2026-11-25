#!/usr/bin/env python3
"""The one gate every direct Codex caller passes: the account plan's answer to `./acct can-use codex`.

Codex's leave line is a step of the one plan file (`./acct plan`; `./acct line codex N --until-reset --why "..."`
changes it), with its reset-day rule (the line is lifted on the day of Codex's reset). The runway brake that stood
here until 2026-11-24 is gone: on a reset day a runway under 1 is the plan's goal, and the brake refused it.
Owner routing ruling 2026-10-28: reviews stay on Codex and are never moved to Claude, so a refused caller fails; it
does not reroute.

  OK           Codex is over its line: the call runs
  LINE         Codex is at or under its line: every call is refused with that line, exit 4, and the refusal is
               appended to <ops watch dir>/codex_refusals.jsonl. A call marked required is refused too: the line is the
               owner's reserve, and one command of his or the Conductor's changes it
  UNMEASURED   the plan or the meter could not be read: the call runs, and the gate says COULD NOT LOOK

    python3 src/RimMandrake/Utils/codex_advice.py            # print the advice line
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import account_plan as AP  # noqa: E402
import slot_allocator as SA  # noqa: E402  (the ops watch folder, where the refusals are kept)

EXIT_LINE = 4       # art_eval/runner.py reads 4 as "refused before Codex ran"
EXIT_HOLD = EXIT_LINE


def advice(now=None, slow=True) -> dict:
    """-> {"state": OK|LINE|UNMEASURED, "why": the plan's one line}. slow: read Codex's meter now (about 2 s)."""
    if os.environ.get("RM_UNDER_SELFTEST") and not os.environ.get("RM_ACCOUNT_PLAN_DIR"):
        # a test child (run_selftests marks every one) never inherits a refusal from the live machine: a stubbed Codex
        # spends no quota. A test of the gate itself names its own plan folder.
        return {"state": "UNMEASURED", "why": "selftest child: the live account plan is not read"}
    try:
        rc, line = AP.meter_answer("codex", now, slow=slow)
    except Exception as e:  # noqa: BLE001  a gate that broke is could not look, by name
        return {"state": "UNMEASURED", "why": "COULD NOT LOOK: the account plan broke (%s: %s)" % (type(e).__name__, e)}
    return {"state": {AP.OK: "OK", AP.NO: "LINE"}.get(rc, "UNMEASURED"), "why": line}


def refusals_path() -> Path:
    return SA.ops_dir() / "codex_refusals.jsonl"


def _record(adv, caller, required):
    try:
        p = refusals_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "state": adv["state"],
                                "why": adv["why"], "caller": caller, "required": required}) + "\n")
    except OSError as e:          # the refusal itself still stands; say the record failed
        print("codex_advice: could not append the refusal to %s: %s" % (refusals_path(), e), file=sys.stderr)


def gate(caller: str, required: str | None = None, adv: dict | None = None) -> int:
    """0 = go. Otherwise the exit code the caller returns; the refusal is printed and recorded."""
    required = (required or os.environ.get("RM_CODEX_REQUIRED") or "").strip() or None
    adv = adv or advice()
    if adv["state"] == "LINE":
        print("REFUSED (Codex at its leave line): %s. %s sends no Codex job%s; no Claude fallback. The line is a step "
              "of the account plan: `./acct line codex <percent> --until-reset --why \"...\"` changes it. This refusal "
              "is in %s." % (adv["why"], caller, " (marked required: %s; the line binds it too)" % required
                             if required else "", refusals_path()), file=sys.stderr)
        _record(adv, caller, required)
        return EXIT_LINE
    if adv["state"] == "UNMEASURED":
        print("[codex] %s; the job is sent" % (adv["why"] if adv["why"].startswith("COULD NOT LOOK") else
                                              "COULD NOT LOOK: " + adv["why"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    a = advice()
    print("codex %s -- %s" % (a["state"], a["why"]))
