#!/usr/bin/env python3
"""The one gate every direct Codex caller passes: slot_allocator's Codex advice, enforced.

CODEX_CALLERS_ENFORCE_DRY_BY_THURSDAY. Only slot_allocator read the Codex runway; gpt_consult and the art-eval GPT
second look called Codex regardless. Owner routing ruling 2026-10-28 (note on GPT_CONSULT_MEASURE_COST_UNLOGGED):
*"please keep using Codex for reviews, to preserve Claude for dev."* -- reviews stay on Codex and are PACED, never
moved to Claude. So, with the advice read the same way the allocator reads it (slot_allocator.ops_inputs + the
`ops.codex_conserve_runway` line in slot_rules.json):

  OK / UNMEASURED  every call runs (no reading is no brake, as in the allocator)
  HOLD             runway < codex_conserve_runway (the allocator's CONSERVE): only a call that names the rule
                   requiring it (`--required "<rule>"` on gpt_consult, or env RM_CODEX_REQUIRED) runs
  EXHAUSTED        runway 0 (the weekly quota is spent): every call is refused, loudly, naming the ops alarm the
                   owner sees (OPS_RUNWAY_RESCUE), and the refusal is appended to <ops watch dir>/codex_refusals.jsonl

The advice uses ops_watch's newest account reading across Linux and Windows session histories; RM_CODEX_SIDE does not split quota.

There is no Claude fallback: a refused caller fails, it does not reroute.

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
import slot_allocator as SA  # noqa: E402

ALARM = "OPS_RUNWAY_RESCUE"     # ops_watch_rules.json: codex.runway < 1.0 -> the owner-facing alarm
EXIT_HOLD = 4
EXIT_EXHAUSTED = 5


def advice(now=None, rules=None) -> dict:
    """-> {"state": OK|HOLD|EXHAUSTED|UNMEASURED, "runway": float|None, "why": str}"""
    if os.environ.get("RM_UNDER_SELFTEST") and not os.environ.get("RM_OPS_WATCH_DIR"):
        # a test child (run_selftests marks every one) never inherits a brake from the live machine: a stubbed Codex
        # spends no quota, and a HOLD today would turn other tests red by the hour. A test of the gate itself points
        # RM_OPS_WATCH_DIR at its own fixture status.json.
        return {"state": "UNMEASURED", "runway": None, "why": "selftest child: the live ops watch is not read"}
    now = now or time.time()
    rules = rules or SA.load_rules()
    ops = SA.ops_inputs(now, rules)
    if not ops.get("ok"):
        return {"state": "UNMEASURED", "runway": None, "why": ops.get("why", "ops watch unreadable")}
    cx = ops.get("codex_runway")
    if cx is None:
        return {"state": "UNMEASURED", "runway": None, "why": "no codex.runway reading in the ops watch status"}
    line = (rules.get("ops") or {})["codex_conserve_runway"]
    if cx <= 0:
        return {"state": "EXHAUSTED", "runway": cx, "why": "Codex runway %.2f: the weekly quota is spent" % cx}
    if cx < line:
        return {"state": "HOLD", "runway": cx,
                "why": "Codex runway %.2f (< %s): only rule-required review rounds run" % (cx, line)}
    return {"state": "OK", "runway": cx, "why": "Codex runway %.2f" % cx}


def refusals_path() -> Path:
    return SA.ops_dir() / "codex_refusals.jsonl"


def _record(adv, caller, required):
    try:
        p = refusals_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "state": adv["state"],
                                "runway": adv["runway"], "caller": caller, "required": required,
                                "alarm": ALARM}) + "\n")
    except OSError as e:          # the refusal itself still stands; say the record failed
        print("codex_advice: could not append the refusal to %s: %s" % (refusals_path(), e), file=sys.stderr)


def gate(caller: str, required: str | None = None, adv: dict | None = None) -> int:
    """0 = go. Otherwise the exit code the caller returns; the refusal is printed and (exhausted) recorded."""
    required = (required or os.environ.get("RM_CODEX_REQUIRED") or "").strip() or None
    adv = adv or advice()
    st = adv["state"]
    if st == "EXHAUSTED":
        print("REFUSED (Codex EXHAUSTED): %s. %s refuses every Codex call, required or not (%s); no Claude "
              "fallback. The owner sees alarm %s; this refusal is in %s." % (
                  adv["why"], caller, required or "not marked required", ALARM, refusals_path()), file=sys.stderr)
        _record(adv, caller, required)
        return EXIT_EXHAUSTED
    if st == "HOLD" and not required:
        print("REFUSED (Codex HOLD): %s. %s is not marked rule-required (--required \"<rule>\" or "
              "RM_CODEX_REQUIRED); no Claude fallback -- retry after the runway recovers." % (adv["why"], caller),
              file=sys.stderr)
        _record(adv, caller, None)
        return EXIT_HOLD
    if st == "HOLD":
        print("[codex] HOLD (%s): running, required by: %s" % (adv["why"], required), file=sys.stderr)
    return 0


if __name__ == "__main__":
    a = advice()
    print("codex %s -- %s" % (a["state"], a["why"]))
