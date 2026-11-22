#!/usr/bin/env python3
"""selftest_mod_next.py: the promises of design/specs/2026-11-22-mod-next/boundary.md, each a test of its name.

    python3 src/RimMandrake/rimflow/selftest_mod_next.py              every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_mod_next.py --only t_x   those alone

Fixtures only: every reader is a stand-in (next_for's src), except t_cli_next_reads_the_one_home, which runs
`maturation.py next` on a temp copy of the blind fixture with its own hold file, tick dir and an empty test control
store. Watched red on the base dfb4ce69bc: mod_next did not exist, and maturation.next_step said "automatic" for a held
mod (acceptance.sh NEXT).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("RM_UNDER_SELFTEST", "1")

import mod_next as MN     # noqa: E402

FAILS = []
NOW = 1795400000.0
AUTO = "NEXT (automatic: the Dispatch tick launches a capped builder): build the missing checks; then advance"


def check(ok, what, got=None):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def rd(mods, age_s=30):
    return {"at": NOW - age_s, "at_pac": "11:00 AM PST", "mods": mods}


def src(holds=None, blocked=None, pause=None, reading=None, nxt=AUTO, stage="offline_build"):
    def gate(root, mod):
        return {"mod": mod, "stage": stage, "refusals": [], "next": nxt}

    def raise_(e):
        raise e
    return {"holds": holds if callable(holds) else (lambda: dict(holds or {})),
            "blocked": blocked if callable(blocked) else (lambda spec: blocked),
            "pause": pause if callable(pause) else (lambda now: dict(pause or {})),
            "reading": (lambda: (reading, "/fx/reading.json", None if reading is not None else "no reading.json yet")),
            "gate": gate, "stage": lambda root, mod: stage}


def nf(s, mod="M", gate=True):
    return MN.next_for("/fx", mod, now=NOW, gate=gate, src=s)


LAUNCHING = rd({"M": {"decision": "would_launch", "klass": "launch", "why": "a builder on 3 bars"}})
HOLD = {"M": {"mod": "M", "date": "2026-11-16", "said": "stop the new biome mods"}}
OFF = {"M": {"mod": "M", "date": "", "said": "slow down", "control": True, "act": "ct_000026", "at_pacific": "x"}}


def t_held_mod_is_never_automatic():
    for g in (True, False):
        r = nf(src(holds=HOLD, reading=LAUNCHING), gate=g)
        check(r["may_run"]["result"] == "held" and not r["next"].startswith("NEXT (automatic"),
              "an owner hold is held, gate=%s" % g, r["next"][:120])
        check("stop the new biome mods" in r["next"] and "mod_owner_hold.py lift M" in r["next"],
              "the held line carries his words and the lift, gate=%s" % g, r["next"][:200])


def t_off_switch_reads_off():
    r = nf(src(holds=OFF, reading=LAUNCHING))
    check(r["may_run"]["result"] == "off" and "ct_000026" in r["may_run"]["why"], "a pipe off <Mod> row is off", r["may_run"])
    seen = []

    def blocked(spec):
        seen.append(spec)
        return "OFF (all, act ct_000099 at x): repairs first" if True else None
    r = nf(src(blocked=blocked, reading=LAUNCHING))
    check(r["may_run"]["result"] == "off" and "ct_000099" in r["may_run"]["why"], "a pipe off all switch is off", r["may_run"])
    check(seen and seen[0].get("stage") == "offline_build" and seen[0].get("mod") == "M",
          "the switch reader is asked for the mod and its stage", seen)
    r = nf(src(blocked="HELD BY OWNER (mod:M, 2026-11-16): stop", reading=LAUNCHING))
    check(r["may_run"]["result"] == "held", "an owner-layer switch in the store reads held", r["may_run"])


def t_pause_reads_paused():
    e = {"why": "repairs", "by": "CONDUCTOR", "at": NOW - 60}
    for pz, what in (({"all": e, "mods": {}}, "all"), ({"all": None, "mods": {"M": dict(e, mod="M")}}, "the mod")):
        r = nf(src(pause=pz, reading=LAUNCHING))
        check(r["may_run"]["result"] == "paused" and "PIPELINE PAUSED" in r["may_run"]["why"],
              "a pause on %s reads paused" % what, r["may_run"])
    r = nf(src(pause={"all": None, "mods": {"Other": dict(e, mod="Other")}}, reading=LAUNCHING))
    check(r["may_run"]["result"] == "yes", "a pause on another mod does not pause this one", r["may_run"])


def t_unreadable_store_is_unmeasured():
    import mod_owner_hold as OH
    import control as C

    def bad_holds():
        raise OH.Unreadable("hold file torn")

    def bad_store(spec):
        raise C.Unreadable("database is locked")
    for s, what in ((src(holds=bad_holds, reading=LAUNCHING), "hold file"),
                    (src(blocked=bad_store, reading=LAUNCHING), "control store"),
                    (src(pause={"error": "pause store unreadable"}, reading=LAUNCHING), "pause store"),
                    (src(holds={"M": {"mod": "M", "said": "x", "date": "", "unreadable": True}}, reading=LAUNCHING),
                     "a hold row marked unreadable")):
        r = nf(s)
        check(r["may_run"]["result"] == "UNMEASURED" and r["may_run"]["result"] != "yes",
              "an unreadable %s is UNMEASURED" % what, r["may_run"])
        check(r["next"].startswith("NEXT (UNMEASURED"), "its NEXT line says UNMEASURED (%s)" % what, r["next"][:100])


def t_stale_or_missing_tick_is_unmeasured():
    for reading, what in ((None, "no reading"), ({"mods": {}}, "a reading with no time"),
                          (rd({"M": {"decision": "would_launch", "klass": "launch"}}, age_s=MN.READING_MAX_AGE_S + 60),
                           "a reading past READING_MAX_AGE_S")):
        r = nf(src(reading=reading))
        check(r["may_run"]["result"] == "UNMEASURED" and "automatic" not in r["by"],
              "an automatic claim on %s is UNMEASURED" % what, (r["may_run"], r["by"]))
    r = nf(src(reading=rd({"M": {"decision": "would_launch", "klass": "launch"}}, age_s=MN.READING_MAX_AGE_S - 60)))
    check(r["may_run"]["result"] == "yes", "a reading just inside READING_MAX_AGE_S still counts", r["may_run"])


def t_ceiling_reads_ceiling():
    why = "the ceiling; release it: python3 src/RimMandrake/rimflow/maturation_dispatch.py release M --stage x"
    r = nf(src(reading=rd({"M": {"decision": "ceiling", "klass": "paused", "why": why, "for_min": 394}})))
    check(r["may_run"]["result"] == "ceiling" and "maturation_dispatch.py release M" in r["next"]
          and "394 min" in r["next"], "a ceiling reads ceiling with its release command and its age", r["next"][:200])


def t_tick_class_decides_an_automatic_claim():
    want = {"launch": "yes", "wait": "waiting", "owner": "waiting", "paused": "paused", "planned": "paused",
            "rested": "waiting"}
    for k, res in want.items():
        r = nf(src(reading=rd({"M": {"decision": "d_" + k, "klass": k, "why": "w"}})))
        check(r["may_run"]["result"] == res, "tick class %s reads %s" % (k, res), r["may_run"])
    r = nf(src(reading=LAUNCHING))
    check(r["next"] == AUTO, "a launching tick keeps the gate's own NEXT line word for word", r["next"])
    # a row written before the tick classed rows: its decision decides
    for dec, res in (("live", "waiting"), ("launched", "yes"), ("pipeline_paused", "paused"), ("hand_step", "paused")):
        r = nf(src(reading=rd({"M": {"decision": dec}})))
        check(r["may_run"]["result"] == res, "an unclassed row with decision %s reads %s" % (dec, res), r["may_run"])
    # an older reading shape: a list of rows
    r = nf(src(reading={"at": NOW, "rows": [{"mod": "M", "decision": "ceiling", "klass": "paused"}]}))
    check(r["may_run"]["result"] == "ceiling", "a reading whose mods is a list of rows is read", r["may_run"])


def t_a_lift_binds_before_the_tick():
    for dec in ("owner_hold", "control_off"):
        r = nf(src(reading=rd({"M": {"decision": dec, "klass": "held", "why": "HELD BY OWNER x"}})))
        check(r["may_run"]["result"] == "waiting", "a tick row %s with nothing held now reads waiting" % dec, r["may_run"])


def t_not_on_the_tick_list_is_hand():
    r = nf(src(reading=rd({"Other": {"decision": "live", "klass": "wait"}})))
    check(r["may_run"]["result"] == "hand" and "not on the Dispatch tick's list" in r["next"],
          "a mod the tick does not list is a hand step", r["next"][:160])


def t_gate_tag_decides_a_non_automatic_step():
    cases = (("NEXT (OWNER, a card in the Conductor log): decide", "waiting"),
             ("NEXT (PAUSED: three cycles, the Conductor decides): x", "paused"),
             ("NEXT (wait on its live run, else PAUSED): visit 2", "waiting"),
             ("NEXT (read again): the stage record moved", "UNMEASURED"))
    for nxt, res in cases:
        r = nf(src(nxt=nxt, reading=None))      # no tick reading: the gate's tag decides alone
        check(r["may_run"]["result"] == res and r["next"] == nxt, "gate tag %r reads %s" % (nxt[:30], res),
              (r["may_run"], r["next"]))


def t_no_gate_runs_no_exit_test():
    s = src(reading=LAUNCHING)

    def boom(root, mod):
        raise AssertionError("gate_step called")
    s["gate"] = boom
    try:
        r = nf(s, gate=False)
        check(r["may_run"]["result"] == "yes" and "maturation.py next M" in r["next_act"],
              "gate=False reads the tick and names maturation.py next", r["next"][:160])
    except AssertionError as e:
        check(False, "gate=False never calls gate_step", str(e))
    r = nf(dict(s, holds=lambda: dict(HOLD)), gate=False)
    check(r["may_run"]["result"] == "held" and "mod_owner_hold.py lift M" in r["next_act"],
          "gate=False on a held mod names the lift", r["next_act"][:160])


def t_next_line_is_by_and_act():
    for s in (src(holds=HOLD, reading=LAUNCHING), src(reading=None), src(reading=LAUNCHING),
              src(reading=rd({"M": {"decision": "ceiling", "klass": "paused"}})), src(nxt="NEXT (OWNER, x): y")):
        for g in (True, False):
            r = nf(s, gate=g)
            check(r["next"] == "NEXT (%s): %s" % (r["by"], r["next_act"]) and r["may_run"]["result"] in MN.RESULTS,
                  "next is NEXT (by): next_act and the result is one of RESULTS (%s, gate=%s)" % (
                      r["may_run"]["result"], g), r["next"][:80])


def t_one_reader_of_the_tick():
    for f in ("control.py", "maturation.py"):
        txt = open(os.path.join(HERE, f), encoding="utf-8").read()
        check("reading.json" not in txt and not re.search(r"def (tick_reading|dispatch_reading|dispatch_overlay)\b", txt),
              "%s has no reader of reading.json of its own" % f)


def t_cli_next_reads_the_one_home():
    """`maturation.py next` as the Conductor runs it: a temp copy of the blind fixture, its own hold file and tick dir."""
    import selftest_maturation as ST
    root = tempfile.mkdtemp(prefix="mod_next_cli_")
    ddir = os.path.join(root, "dispatch")
    os.makedirs(ddir)
    hold = os.path.join(root, "holds.json")
    mod = "GimmeSomeSlack"
    try:
        ST.copy_blind(root)
        with open(os.path.join(ddir, "reading.json"), "w", encoding="utf-8") as f:
            json.dump({"at": time.time(), "at_pac": "now", "mods": {mod: {"decision": "would_launch", "klass": "launch",
                                                                          "why": "x"}}}, f)
        env = dict(os.environ, RM_MATURATION_DISPATCH_DIR=ddir, RM_OWNER_HOLD_FILE=hold, RM_UNDER_SELFTEST="1")
        env.pop("RM_CONTROL_DB", None)
        env.pop("MATURATION_CLOCK", None)
        for holds, want in (([], "NEXT (automatic"), ([{"mod": mod, "said": "stop it", "date": "2026-11-22"}],
                                                       "NEXT (HELD BY OWNER")):
            with open(hold, "w", encoding="utf-8") as f:
                json.dump({"holds": holds}, f)
            r = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "next", mod],
                               capture_output=True, text=True, timeout=300, env=env)
            nl = [x for x in r.stdout.splitlines() if x.startswith("NEXT")]
            check(r.returncode == 0 and nl and nl[-1].startswith(want) and "  may run: " in r.stdout,
                  "maturation.py next prints the one home's line (%s)" % want, (r.returncode, nl[-1:] if nl else
                                                                                r.stderr[-300:]))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main(argv):
    only = argv[argv.index("--only") + 1:] if "--only" in argv else None
    for t in (t_held_mod_is_never_automatic, t_off_switch_reads_off, t_pause_reads_paused,
              t_unreadable_store_is_unmeasured, t_stale_or_missing_tick_is_unmeasured, t_ceiling_reads_ceiling,
              t_tick_class_decides_an_automatic_claim, t_a_lift_binds_before_the_tick, t_not_on_the_tick_list_is_hand,
              t_gate_tag_decides_a_non_automatic_step, t_no_gate_runs_no_exit_test, t_next_line_is_by_and_act,
              t_one_reader_of_the_tick, t_cli_next_reads_the_one_home):
        if only and t.__name__ not in only:
            continue
        print("--", t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001  a test that raises is a failed test, never a dead run
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
