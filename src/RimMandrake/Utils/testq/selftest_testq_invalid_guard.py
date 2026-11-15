#!/usr/bin/env python3
"""selftest_testq_invalid_guard.py - the INVALID-waste guards (RIMMANDRAKE_STOP_STEVEDESKTOP_INVALID_RUNS_REPEATING_UNFIXED).

  python3 selftest_testq_invalid_guard.py               every check; exit 1 on any failure
  python3 selftest_testq_invalid_guard.py --mutant M    the same checks with guard M reverted to the old behaviour:
                                                        must exit 1 (the check sees the guard)
  python3 selftest_testq_invalid_guard.py --mutants     run every mutant; exit 0 only if each one is caught

No queue, ledger, git or game is touched: fakes stand in for each.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="invalid_guard_")
os.environ.setdefault("TESTQ_QUEUE", os.path.join(TMP, "q"))
os.environ["RIMFLOW_ITEMS"] = os.path.join(TMP, "items")

import invalid_class as IC  # noqa: E402
import repeat_guard as G  # noqa: E402
import retest as R  # noqa: E402
import testq as T  # noqa: E402
import ingest  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []


def check(ok, msg):
    print("%s  %s" % ("ok  " if ok else "FAIL", msg))
    if not ok:
        FAILS.append(msg)


# real runner notes, shortened (testq done/ 2026-11-06..14)
N = {
    "swap_a": "modset_builder --tier gimmesomeslack --apply failed:  marker names before-copy /x/ModsConfig.before-tier-flowworks.xml but it is mis",
    "swap_b": "ed:  marker names before-copy /y/ModsConfig.before-tier-pyrelands.xml but it is missing; stop",
    "nostart_a": "ted) stopped (graceful) 2026-11-12T01:02:19Z $ rw_game.sh up --wait\nFAILED: no RimWorldWin64 process 5 s after Start-Process",
    "nostart_b": "h init && rw_game.sh up --wait host_guard: RUNNER holds gen 1682\nFAILED: no RimWorldWin64 process 5 s after Start-Process",
    "world": "modcheck exit 1 and no sheet JSON: imWorld readiness 'mapData'.) [bridge split] 371.6 s wall",
    "gate": "modcheck exit 1 and no sheet JSON: RuntimeError: launch gate REFUSES to start a map: 1 missing type(s) of our own: X.Y",
    "mustshow": "modcheck exit 1 and no sheet JSON: Graffiti REFUSED validated must-show lines no component claims: a, b",
    "companion": "companion STALE JawaBench.BridgeTools.dll not built from this job's sources (embedded 49f1, want 7539)",
    "died": "the game loaded as pid 39192 is gone; pid 28776 runs now; modcheck exit 0, sheet {'PASS': 12}",
    "opaque": "modcheck exit 1 and no sheet JSON: _themselves, fights_have_people_and_reasons, raid_mark_tro",
}
CAUSE = {"swap_a": "LOAD", "swap_b": "LOAD", "nostart_a": "LOAD", "nostart_b": "LOAD", "world": "HARNESS",
         "gate": "HARNESS", "mustshow": "HARNESS", "companion": "DEPLOY", "died": "GAME_DIED", "opaque": "HARNESS"}


def res(k, outcome="INVALID", fin="2026-11-14T10:00:00Z", att="J1.a1"):
    return {"outcome": outcome, "cause": CAUSE[k] if outcome == "INVALID" else None, "note": N[k] if outcome ==
            "INVALID" else "", "rows": [], "attempt": att, "finished": fin, "host": "stevedesktop"}


def rec(jid, k, chains=("c1", "c2"), outcome="INVALID", sha="aaaa", fin="2026-11-14T10:00:00Z", mod="Mock"):
    return {"job": {"id": jid, "mod": mod, "selector": {"chains": list(chains)}, "source_sha": sha,
                    "submitted": fin, "purpose": "guard", "requested_by": T.FILLER, "item": None, "row_items": {}},
            "result": res(k, outcome, fin, jid + ".a1"), "finished": fin}


def classify_checks():
    want = {"swap_a": ("DELIVERY", "swap_marker_stale"), "nostart_a": ("GAME", "game_would_not_start"),
            "world": ("GAME", "world_start_no_map"), "gate": ("DELIVERY", "launch_gate_missing_type"),
            "mustshow": ("TEST", "must_show_unclaimed"), "companion": ("DELIVERY", "companion_stale"),
            "died": ("GAME", "game_died"), "opaque": ("UNKNOWN", None)}
    for k, w in want.items():
        got = IC.classify(res(k))
        check(got == w, "classify %s -> %s (got %s)" % (k, w, got))
    check(IC.classify(res("swap_a", "DONE")) == (None, None), "a DONE result has no INVALID class")


def cause_checks():
    a, b = R.job_cause(res("swap_a")), R.job_cause(res("swap_b"))
    check(a == b == "DELIVERY: swap_marker_stale", "one fault, two log tails -> ONE cause: %r / %r" % (a, b))
    a, b = R.job_cause(res("nostart_a")), R.job_cause(res("nostart_b"))
    check(a == b and R.repair_base(a) == R.repair_base(b), "the game that would not start files under one item: %r" % a)
    w, g = R.job_cause(res("world")), R.job_cause(res("gate"))
    check(w != g, "two faults behind 'modcheck exit 1, no sheet' are two causes: %r / %r" % (w, g))
    check(R.job_cause(res("companion")) is None, "a stale companion still files no repair (the stager owns it)")
    check(IC.class_of_cause("TEST: must_show_unclaimed") == "TEST" and IC.class_of_cause("HARNESS: x") is None,
          "class_of_cause reads the new keys and ignores the old free text")


def ingest_checks():
    """A TEST/DELIVERY cause inside a fault window is filed; a GAME cause inside one is still ENVIRONMENT."""
    calls = []
    saved = (ingest.rimflow, ingest.note_once, ingest.env_window, ingest.spawned_for, ingest.T.log)
    ingest.rimflow = lambda *a: calls.append(a) or (0, "ok")
    ingest.note_once = lambda it, needle, text: calls.append(("note", it)) or True
    ingest.env_window = lambda r: ({"id": "F1"}, "inside fault window F1")
    ingest.spawned_for = lambda base, att: False
    ingest.T.log = lambda *a: None
    try:
        for k, filed in (("swap_a", True), ("mustshow", True), ("nostart_a", False), ("died", False)):
            ingest._REPAIR_ITEMS[0] = {}
            ingest._REPAIRED.clear()
            del calls[:]
            r = rec("J%s" % k, k)
            cause = R.job_cause(r["result"])
            err = ingest.repair(r["job"], r["result"], cause, r)
            spawned = [c for c in calls if c and c[0] == "spawn"]
            check(err is None and bool(spawned) == filed, "%s inside a fault window: %s (spawn calls %d)" % (
                k, "filed, a %s fault is code" % IC.class_of_cause(cause) if filed else "ENVIRONMENT, nothing filed",
                len(spawned)))
        p = os.path.join(os.environ["RIMFLOW_ITEMS"], R.repair_base(R.job_cause(res("mustshow"))) + ".md")
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        check("the test's author" in text or "last written by commit" in text,
              "a TEST repair names who wrote the test (or says unknown)")
        check("repeat_guard.py" in text, "an owned repair says the filler will not re-run it unchanged")
    finally:
        ingest.rimflow, ingest.note_once, ingest.env_window, ingest.spawned_for, ingest.T.log = saved


class Item:
    def __init__(self, state):
        self.state = state


def fake_git(diff=""):
    def g(*a):
        if a[0] == "cat-file":
            return None if "dead" in a[2] else ""
        if a[0] == "rev-parse":
            return "head"
        if a[0] == "diff":
            return diff
        return None
    return g


def hold_checks():
    recs = [rec("J1", "swap_a")]
    h = G.hold("Mock", None, recs, {}, fake_git(""))
    check(set(h) == {"c1", "c2"} and "runs again after a commit" in h.get("c1", ""),
          "a DELIVERY death with nothing changed holds its chains, saying what releases them: %s" % h.get("c1"))
    check(G.hold("Mock", None, recs, {}, fake_git("src/RimMandrake/Mock/Source/A.cs")) == {},
          "a change to the mod releases the hold")
    check(set(G.hold("Mock", None, recs, {}, fake_git("infrastructure/stevedesktop/selftest_worker.py"))) == {"c1", "c2"},
          "a changed selftest cures nothing: still held")
    check(set(G.hold("Mock", None, [rec("J1", "mustshow")], {}, fake_git(""))) == {"c1", "c2"}, "a TEST death holds")
    check(G.hold("Mock", None, [rec("J1", "nostart_a")], {}, fake_git("")) == {}, "a GAME death never holds")
    one = [rec("J1", "opaque")]
    two = one + [rec("J2", "opaque", fin="2026-11-14T11:00:00Z")]
    check(G.hold("Mock", None, one, {}, fake_git("")) == {}, "one UNKNOWN death does not hold")
    check(set(G.hold("Mock", None, two, {}, fake_git(""))) == {"c1", "c2"}, "two UNKNOWN deaths in a row hold")
    later = recs + [rec("J2", "swap_a", chains=("c1",), outcome="DONE", fin="2026-11-14T12:00:00Z")]
    check(set(G.hold("Mock", None, later, {}, fake_git(""))) == {"c2"}, "a chain DONE since is free; the other stays held")
    base = R.repair_base(R.job_cause(res("swap_a")))
    check(G.hold("Mock", None, recs, {base: Item("done")}, fake_git("")) == {}, "its repair item closed: released")
    check(set(G.hold("Mock", None, recs, {base: Item("proposed")}, fake_git(""))) == {"c1", "c2"},
          "its repair item open: still held")
    check(G.hold("Mock", None, [rec("J1", "swap_a", sha="dead")], {}, fake_git("")) == {},
          "a sha this checkout cannot read holds nothing (blind, never a silent stop)")


def testq_checks():
    saved = T.repeat_holds
    T.repeat_holds = lambda mod, chains, recs=None: {c: "%s held" % c for c in (chains or ["c1", "c2"]) if c != "c3"}
    try:
        r = T.repeat_refusal("Mock", {"chains": ["c1", "c2"]})
        check(bool(r) and "c1 held" in r, "submit of a wholly held selection is refused: %r" % r)
        check(T.repeat_refusal("Mock", {"chains": ["c1", "c3"]}) is None, "a selection with a fresh chain is not")
        import gaps
        seen = {}
        saved_rank, saved_rec, saved_hist = gaps.rank, T.records, T.chain_history
        gaps.rank = lambda mod, n, now, recs, dry, exclude=(): seen.update(exclude=set(exclude)) or {
            "rank": None, "purpose": None, "row_items": {}, "dry": [], "held": [], "ident": None, "counts":
            {"never_run": 0}, "flaky": [], "blind": [], "why": {}, "all_dry": False, "text": "nothing"}
        T.records, T.chain_history = (lambda state: []), (lambda mod, recs: {})
        try:
            plan = T.fill_rank("Mock", 4, 0)
        finally:
            gaps.rank, T.records, T.chain_history = saved_rank, saved_rec, saved_hist
        check({"c1", "c2"} <= seen.get("exclude", set()), "the filler never ranks a held chain: %s" % seen)
        check("held, not re-run unchanged" in plan.get("text", ""), "and its plan says so: %r" % plan.get("text"))
    finally:
        T.repeat_holds = saved
    out = "REFUSED: validated must-show lines no component claims: x, y\n"
    saved_run = T.subprocess.run
    T.subprocess.run = lambda *a, **k: subprocess.CompletedProcess(a, 2, out, "")
    try:
        p = T.preview("Mock", {"chains": ["c1"]})
    finally:
        T.subprocess.run = saved_run
    check(bool(p["refusal"]) and "must-show" in p["refusal"],
          "submit refuses a selection modcheck's preview refuses on the visual floor: %r" % p["refusal"])


def ops_checks():
    d = [rec("J%d" % i, "died" if i < 3 else "swap_a", outcome="INVALID" if i < 4 else "DONE") for i in range(10)]
    p = OW.invalid_share(d)
    check(p.get("m") == "MEASURED" and p.get("v") == 0.4 and (p.get("x") or {}).get("game") == 3
          and (p.get("x") or {}).get("delivery") == 1, "the share reads 4 of 10, split by fault: %s" % p)
    check(OW.invalid_share(d[:4]).get("m") == "ESTIMATE", "4 jobs are too few for a MEASURED share")
    check(OW.invalid_share([]).get("m") == "UNMEASURED", "no job is UNMEASURED, never 0")
    rules = json.load(open(os.path.join(os.path.dirname(HERE), "ops_watch_rules.json"), encoding="utf-8"))
    tg = [t for t in rules["targets"] if t["key"] == "steve.invalid_share_24h"]
    check(len(tg) == 1 and tg[0].get("alarm") is True and tg[0]["op"] == ">=" and tg[0]["value"] <= 0.15,
          "the share has an alarm line at 15 %% or tighter: %s" % (tg[0] if tg else None))


MUTANTS = {
    "no_stable_key": lambda: setattr(IC, "cause_key", lambda res: None),
    "env_excuses_all": lambda: setattr(ingest.IC, "class_of_cause", lambda c: None),
    "no_repeat_guard": lambda: setattr(G, "hold", lambda *a, **k: {}),
    "selftest_cures": lambda: setattr(G, "inert", lambda p: False),
    "game_holds": lambda: setattr(IC, "GAME", "GAME_OFF"),
    "no_preview_phrase": lambda: setattr(T, "SELECTION_REFUSALS", T.SELECTION_REFUSALS[:5]),
    "no_share_reading": lambda: setattr(OW, "invalid_share", lambda d: OW.U("off")),
}


def main():
    if "--mutants" in sys.argv:
        bad = []
        for m in MUTANTS:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--mutant", m], capture_output=True,
                               text=True, timeout=300)
            n = r.stdout.count("\nFAIL") + r.stdout.startswith("FAIL")
            print("%s  mutant %s: exit %d, %d check(s) failed" % ("ok  " if r.returncode == 1 else "FAIL", m,
                                                                   r.returncode, n))
            if r.returncode != 1:
                bad.append(m)
        print("%d of %d mutants caught" % (len(MUTANTS) - len(bad), len(MUTANTS)))
        return 1 if bad else 0
    if "--mutant" in sys.argv:
        MUTANTS[sys.argv[sys.argv.index("--mutant") + 1]]()
    for f in (classify_checks, cause_checks, ingest_checks, hold_checks, testq_checks, ops_checks):
        f()
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
