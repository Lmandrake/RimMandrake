#!/usr/bin/env python3
"""selftest_maturation_autonomy_review_findings.py - one case per finding of the 2026-11-17 Codex review of
maturation_autonomy.py (parent RIMMANDRAKE_FIX_MATURATION_AUTONOMY_CODEX_REVIEW_FINDINGS; raw
/mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_ma_0.txt, r_ma_1.txt), each named after the child that fixes it. Every
case failed on the base it was written against. Hermetic: temp dirs only; every land, launch and ledger call is a
fake, so no git, systemd or Dispatcher state is touched."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402
import maturation_autonomy as MA  # noqa: E402
import maturation_dispatch as MD  # noqa: E402

FAILS = []


def check(name, ok, got=""):
    print("%s %s%s" % ("ok  " if ok else "FAIL", name, "" if ok else "  got: %s" % (got,)))
    if not ok:
        FAILS.append(name)


class patched:
    """Set attributes for the length of a with-block, then put the originals back."""
    def __init__(self, *triples):
        self.triples, self.was = triples, []

    def __enter__(self):
        for obj, name, val in self.triples:
            self.was.append((obj, name, getattr(obj, name)))
            setattr(obj, name, val)

    def __exit__(self, *a):
        for obj, name, val in reversed(self.was):
            setattr(obj, name, val)


def seed_timeout_leaves_no_record(tmp):
    """RIMMANDRAKE_CLEAN_SEED_RECORD_WHEN_LANDING_TIMES_OUT (finding 1)."""
    root = os.path.join(tmp, "seed")
    rec = os.path.join(M.mod_dir(root, "A"), M.RECORD)

    def seed(root_, mod, **k):
        os.makedirs(os.path.dirname(rec), exist_ok=True)
        with open(rec, "w") as f:
            f.write("{}\n")
        return {}, True
    real_run = subprocess.run

    def run(argv, *a, **k):
        if argv and str(argv[0]).endswith("land.sh"):
            raise subprocess.TimeoutExpired(argv, k.get("timeout"))
        return real_run(argv, *a, **k)
    with patched((M, "seed_mod", seed), (MA.subprocess, "run", run)):
        try:
            MA.seed_and_land(root, "A")
            raised = None
        except Exception as e:  # noqa: BLE001
            raised = e
    check("seed: a landing that times out raises (the tick books it as refused)", raised is not None, raised)
    check("seed: a landing that times out leaves no local record, so the next tick seeds again",
          not os.path.exists(rec), os.path.exists(rec))


def autolock_failure_before_landing_rolls_back(tmp):
    """RIMMANDRAKE_ROLL_BACK_AUTOLOCK_WHEN_RECORD_DIR_FAILS (finding 2)."""
    root = os.path.join(tmp, "lock")
    os.makedirs(M.mod_dir(root, "B"))
    os.makedirs(os.path.join(root, "infrastructure", "state"))
    with open(os.path.join(root, "infrastructure", "state", "delegated"), "w") as f:
        f.write("a file where the delegated folder should be\n")      # makedirs of the record's folder fails
    landed = []
    try:
        MA.autolock_and_land(root, "B", now=1.8e9, land=lambda subj, paths: landed.append(paths) or "PUBLISHED x")
        raised = None
    except Exception as e:  # noqa: BLE001
        raised = e
    vpath = os.path.join(M.mod_dir(root, "B"), "version", "VERSION.json")
    check("autolock: a failure writing the delegated record raises", raised is not None and not landed, (raised, landed))
    check("autolock: a failure writing the delegated record leaves no VERSION.json locked behind",
          not os.path.exists(vpath) and not MA.version_locked(root, "B"),
          (os.path.exists(vpath), MA.version_locked(root, "B")))


def road_back_retries_transient_fixer(tmp):
    """RIMMANDRAKE_RETRY_ROAD_BACK_FIXER_AFTER_TRANSIENT_LAUNCH_FAIL (finding 3)."""
    s = {"road_back": {"caused_by": "STEW_ITEM", "at": 1}, "steward": {},
         "fixers": {"FIX_ITEM": {"item": "FIX_ITEM", "unit": None, "failed": "TimeoutExpired: timed out", "tries": 1}}}
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "FIX_ITEM", "needs": "offline"}])
    check("road back: a fixer whose launch failed on a transient fault is routed to the gate again, not spent",
          row.get("decision") == "fixer" and row.get("fix_item") == "FIX_ITEM", row)
    s["fixers"]["FIX_ITEM"].update(unit="rm-unit-1", failed=None)
    row = {"mod": "C", "stage": "blind_challenge"}
    MA._road_back(s, row, lambda ids: [{"id": "FIX_ITEM", "needs": "offline"}])
    check("road back: a fixer that ran is still spent", row.get("decision") == "fixer_spent", row)


def _fixer_row():
    return {"mod": "D", "aut": "fixer", "fix_item": "FIX_D", "stage": "blind_challenge", "cap": 5}


def ledger_after_failure_keeps_the_run(tmp):
    """RIMMANDRAKE_KEEP_LAUNCHED_UNIT_WHEN_LEDGER_AFTER_FAILS (finding 4)."""
    st = {"mods": {"D": {}}}

    def after(*a, **k):
        raise RuntimeError("land_ledger refused")
    fx = {"launch_brief": lambda item, brief, model, cap, seat, env=None: (0, "started", "rm-unit-d"),
          "known": lambda: set(), "file": None, "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: True),
                 (MD, "ledger_open", lambda root, mod, role, brief, stage=None, now=None: {"brief": brief, "env": {}}),
                 (MD, "ledger_after", after), (M, "game_takeable", lambda stage: False)):
        row = _fixer_row()
        MA.execute(tmp, {}, st, [row], {"D"}, 1.8e9, fx=fx)
    e = st["mods"]["D"].get("fixers", {}).get("FIX_D") or {}
    check("ledger_after: a run that started keeps its unit when the ledger step after it fails",
          e.get("unit") == "rm-unit-d" and not e.get("failed") and row.get("decision") == "launched", (e, row))


def launch_exception_books_code(tmp):
    """RIMMANDRAKE_BOOK_CODE_ON_LAUNCH_EXCEPTION_FRESH_FIX_SEEN (finding 5)."""
    st = {"mods": {"D": {}}}

    def boom(*a, **k):
        raise ValueError("brief template broken")
    fx = {"launch_brief": boom, "known": lambda: set(), "file": None, "publish": None}
    with patched((MD, "pilot_ledger", lambda root, mod: False), (M, "game_takeable", lambda stage: False)):
        MA.execute(tmp, {"_code": "code-v1"}, st, [_fixer_row()], {"D"}, 1.8e9, fx=fx)
    e = st["mods"]["D"].get("fixers", {}).get("FIX_D") or {}
    check("launch exception: the book entry carries the code it failed on", e.get("code") == "code-v1", e)
    row = dict(_fixer_row())
    go, why = MA._gate({"_code": "code-v2", "fix_cap_usd": 5, "max_live": 2}, st["mods"]["D"], row, 0, "0.1.0")
    check("launch exception: once the code changed, the gate tries it again", go is True, (go, why))


# each child's section joins once its fix lands (every one was watched failing on base first)
SECTIONS = [
    seed_timeout_leaves_no_record,
    autolock_failure_before_landing_rolls_back,
]


def main():
    tmp = tempfile.mkdtemp(prefix="mat_aut_findings_")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
    os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
    try:
        for run in SECTIONS:
            run(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    if "--all" in sys.argv:      # every case, landed or not: the red-on-base run
        SECTIONS[:] = [seed_timeout_leaves_no_record, autolock_failure_before_landing_rolls_back,
                       road_back_retries_transient_fixer, ledger_after_failure_keeps_the_run,
                       launch_exception_books_code]
    sys.exit(main())
