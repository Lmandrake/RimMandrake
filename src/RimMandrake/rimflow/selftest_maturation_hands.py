#!/usr/bin/env python3
"""selftest_maturation_hands.py: the Conductor's hand judgements built into the Maturation Pipeline, offline, in a temp
state dir. Item RIMMANDRAKE_BUILD_CONDUCTOR_INTERVENTIONS_INTO_PIPELINE_ITSELF (census:
design/RimMandrake/pipeline_interventions_census_2026-11-15.md). Written before the code and watched failing on the base.

    python3 src/RimMandrake/rimflow/selftest_maturation_hands.py            exit 0 when every check prints PASS
    python3 src/RimMandrake/rimflow/selftest_maturation_hands.py --only stalled|stop|retry|refund|briefs|acts|chores

What it proves, one section per child item:
  stop     a run first seen with no refused bars is never judged as a builder; a stop already written on an empty set
           lifts itself; a real builder that resolved nothing still stops
  retry    a launch that failed on a defect remembers the pipeline code it failed on and is retried once that code
           changes, within launch_tries; the same code, a spent count and an older entry are not retried
  refund   a run killed from outside gives its own dollars back at the stage ceiling, once, when the stage is not
           DIVERGING, as a release record marked automatic; a plain overspend, a larger excess, a DIVERGING stage and a
           second refund stay paused
  briefs   the steward's rules carry the re-pin rule and the neutral-fixer triage; the judge and in-game briefs tell the
           run to read its own record with the pipeline's reader before it stops
  acts     every hand act is recorded once (a ceiling release, a clear, a coverage release, a hand run doing a stage's
           work, a hand move, a hand close, a settings edit, a gap in the tick); one whose reason names a ledger item is
           folded; one with no follow-up after a day is overdue, with a Needs Conductor line; `fold` refuses an unknown
           item and an unknown census row; ops_watch reads the count and its rule has a fixed alarm name
  stalled  a builder that resolved none of its refused bars gets one steward run that finds out why (it stopped early, the
           work is not a builder's, a pipeline defect, too big for one run) and files it, never a second one for the same
           stall, never on a ceiling stop; every detached run is told it ends with its turn
  chores   the tick reads back run dollars every 30 minutes and finishes a run dead for 10 minutes or more whose
           finish never ran; a killed blind or in-game run is left to its retry path; a failing chore is reported
  his_walk a move off his_walk by OWNER (his walk verdict, one of his five acts) folds by itself; a move off his_walk by
           a program, and a move by OWNER from another stage, stay open
"""
import inspect
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

import maturation as M              # noqa: E402
import maturation_autonomy as AUT   # noqa: E402
import maturation_dispatch as MD    # noqa: E402

try:
    import maturation_hands as MH   # noqa: E402
except ImportError:
    MH = None

NOW = 1794790000.0      # pinned, after the census baseline
FAILS = []
CFG = {"enabled": True, "advancing": ["A"], "cap_tokens": 3_750_000, "max_live": 4, "stage_ceiling_tokens": 25_000_000, "settle_s": 180,
       "blind_enabled": True, "blind_cap_tokens": 5_000_000, "blind_auto_cycles_per_visit": 3, "launch_tries": 3,
       "ingame_enabled": True, "ingame_cap_tokens": 7_500_000, "ingame_auto_runs_per_visit": 1}


def ok(cond, what, read=""):
    print("%s  %s%s" % ("PASS" if cond else "FAIL", what, (" (read %s)" % str(read)[:260]) if read != "" else ""))
    if not cond:
        FAILS.append(what)


def guard(fn, what):
    """A check that cannot even run on the base is a FAIL with its error, never a crash of the whole file."""
    try:
        fn()
    except Exception as e:      # noqa: BLE001
        ok(False, what, "%s: %s" % (e.__class__.__name__, e))


def offline(refused, live=(), last_end=None, owed="build"):
    return {"A": {"mod": "A", "stage": "offline_build", "refused_bars": list(refused), "build_refusals": [],
                  "live_units": list(live), "last_end": last_end, "owed": owed, "stage_runs": {}, "run_tokens": {},
                  "bar_fp": {b: "fp-" + b for b in refused}}}


def row_of(rows):
    return rows[0]


# ---- stop -------------------------------------------------------------------------------------------------------------

def stop_main():
    st = {}
    MD.decide(CFG, st, offline([], live=["rm-hand-fix"], owed="hand step"), NOW)
    rows, _ = MD.decide(CFG, st, offline([], last_end=NOW - 600, owed="hand step"), NOW + 60)
    s = st["mods"]["A"]
    ok(not s.get("stopped"), "stop 1: a run first seen with 0 refused bars writes no stop when it ends",
       s.get("stopped"))
    ok(row_of(rows)["decision"] == "hand_step", "stop 1: the mod goes on to its own next decision",
       row_of(rows)["decision"])
    ok("no build work" in str((s.get("last_run") or {}).get("not_judged")),
       "stop 1: the last-run record says why it was not judged", s.get("last_run"))

    own = [{"unit": "rm-builder", "item": "X", "at": NOW - 900, "stage": "offline_build"}]
    st = {"mods": {"A": {"launches": list(own)}}}
    MD.decide(CFG, st, offline(["a", "b"], live=["rm-builder"]), NOW)
    rows, _ = MD.decide(CFG, st, offline(["a", "b"], last_end=NOW - 600), NOW + 60)
    ok(row_of(rows)["decision"] == "stopped" and "none resolved" in row_of(rows)["why"],
       "stop 2 (control): the tick's own builder seen with 2 refused bars that resolved none still stops", row_of(rows))
    st = {"mods": {"A": {"pilot_launches": list(own)}}}
    MD.decide(CFG, st, offline(["a", "b"], live=["rm-builder"]), NOW)
    rows, _ = MD.decide(CFG, st, offline(["a", "b"], last_end=NOW - 600), NOW + 60)
    ok(row_of(rows)["decision"] == "stopped",
       "stop 2 (control): a builder launched through pilot-launch is a builder too and still stops", row_of(rows))

    # RIMMANDRAKE_SPARE_HAND_RUNS_FROM_BUILDER_STOP_REWORD_RAN: ExplosiveKnockback 2026-11-25, a hand-launched
    # design run (a bar reword and an exam retake) ended at the offline build with the 14 new bars unbuilt, and the tick
    # judged it a builder that "resolved none": the Stage 3 builder never launched and a triage steward ran instead
    st = {}
    MD.decide(CFG, st, offline(["a", "b"], live=["rm-hand-design"]), NOW)
    rows, launches = MD.decide(CFG, st, offline(["a", "b"], last_end=NOW - 600), NOW + 60)
    s = st["mods"]["A"]
    ok(not s.get("stopped") and row_of(rows)["decision"] == "launch" and launches == ["A"],
       "stop 2b: a run the tick did not launch as a builder writes no stop when it ends; the builder launches",
       (row_of(rows)["decision"], s.get("stopped")))
    ok("not a builder" in str((s.get("last_run") or {}).get("not_judged")),
       "stop 2b: the last-run record says why it was not judged", s.get("last_run"))

    st = {"mods": {"A": {"stopped": {"ids": [], "at": NOW - 900,
                                     "why": "run rm-hand-fix ended and the refused bars went 0 -> 0, none resolved"}}}}
    rows, launches = MD.decide(CFG, st, offline(["a"]), NOW)
    ok(row_of(rows)["decision"] == "launch" and launches == ["A"],
       "stop 3: a stop already written on an empty refused set lifts itself and build work launches", row_of(rows))
    ok("no refused bars" in str(row_of(rows).get("stop_lifted")), "stop 3: the reading says what lifted it",
       row_of(rows).get("stop_lifted"))

    st = {"mods": {"A": {"launches": list(own), "stopped": {
        "ids": ["a"], "at": NOW - 900, "why": "run rm-builder ended and the refused bars went 1 -> 1, none resolved"}}}}
    rows, launches = MD.decide(CFG, st, offline(["a"]), NOW)
    ok(row_of(rows)["decision"] == "stopped" and not launches,
       "stop 4 (control): a stop on the same non-empty refusals stays", row_of(rows)["decision"])

    st = {"mods": {"A": {"launches": list(own), "stopped": {
        "ids": ["a"], "at": NOW - 900,
        "why": "run rm-hand-design ended and the refused bars went 1 -> 1, none resolved"}}}}
    rows, launches = MD.decide(CFG, st, offline(["a"]), NOW)
    ok(row_of(rows)["decision"] == "launch" and launches == ["A"]
       and "not a builder" in str(row_of(rows).get("stop_lifted")),
       "stop 4b: a stop already written on a run the tick did not launch as a builder lifts itself", row_of(rows))

    st = {"mods": {"A": {"stopped": {"ids": [], "at": NOW - 900, "why": "USD 99.00 spent, at the ceiling",
                                     "ceiling": True}}}}
    f = offline(["a"])
    f["A"]["stage_runs"] = {"rm-old": 99.0}
    rows, launches = MD.decide(CFG, st, f, NOW)
    ok(row_of(rows)["decision"] == "stopped" and not launches,
       "stop 5 (control): a ceiling stop with an empty id list is not lifted by this rule", row_of(rows)["decision"])


# ---- retry ------------------------------------------------------------------------------------------------------------

def retry_main():
    cfg = dict(CFG, _code="code-B")
    fail = {"failed": "REFUSED: RUNNER may not spawn an item that needs game-up", "never_started": True, "tries": 1,
            "unit": None, "code": "code-A"}
    ok(MD.retriable(cfg, dict(fail)) is True,
       "retry 1: a launch that failed on a defect is retriable once the pipeline's code changed")
    ok(MD.retriable(cfg, dict(fail, code="code-B")) is False, "retry 2 (control): the same code is not retried")
    ok(MD.retriable(cfg, dict(fail, tries=3)) is False, "retry 3 (control): launch_tries bounds it")
    old = dict(fail)
    old.pop("code")
    ok(MD.retriable(cfg, old) is False, "retry 4 (control): an entry that recorded no code is not retried")
    ok(MD.retriable(dict(CFG), dict(fail)) is False, "retry 5 (control): an unreadable current code retries nothing")
    ok(MD.retriable(cfg, {"unit": "rm-x", "failed": None, "tries": 1, "code": "code-A"}) is False,
       "retry 6 (control): a run that started is never retried by a code change")

    s, row = {}, {"mod": "A", "cap": 20}
    okk, item, unit, text, entry = MD.launch_counted(
        dict(CFG, _code="code-A"), s, row, NOW, "blind_auto", {"visit_id": "0.1.0#1", "cycle": 1},
        lambda: "ITEM_X", lambda it: (False, "REFUSED: a rule said no"), lambda it: (True, "published"),
        lambda it: (0, "DETACHED rm-x", "rm-x"))
    ok(entry.get("code") == "code-A" and not okk, "retry 7: a failed launch records the code it failed on", entry)

    # Stage 3: a failed launch writes no stop (RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT, the owner 2026-11-18:
    # no turn is spent by a failed system call). These read "the stop carries its code / stays on the same code / lifts
    # once it changes"; the launch is void_system now, a system fault, and the next tick launches on any code.
    st = {}
    f = offline(["a"])
    rows, launches = MD.decide(dict(CFG, _code="code-A"), st, f, NOW)
    MD.execute(REPO, dict(CFG, _code="code-A"), st, rows, launches, NOW,
               fx={"file": lambda *a, **k: (False, "REFUSED: a rule said no"), "known": lambda: set(),
                   "launch": lambda *a, **k: (0, "DETACHED rm-x", "rm-x"), "publish": lambda it: (True, "published")})
    sa = st["mods"]["A"]
    # a launch that never started is a fault of form (form_fault, 2026-11-21): no stop, no fault, one repair owed
    ok(not sa.get("stopped") and not sa.get("system_faults")
       and [r.get("what") for r in sa.get("form_repairs") or []] == ["REFUSED: a rule said no"]
       and row_of(rows)["decision"] == "repairing",
       "retry 8: a failed Stage 3 launch writes no stop and no fault: it owes a repair naming its cause",
       sa.get("form_repairs"))
    rows, launches = MD.decide(dict(CFG, _code="code-A"), st, f, NOW + 60)
    ok(row_of(rows)["decision"] == "launch", "retry 9: on the same code the next tick launches (no turn spent)",
       row_of(rows)["decision"])
    stop = {"ids": ["a"], "at": NOW, "why": "the launch failed: x", "launch_failed": True, "code": "code-A"}
    st["mods"]["A"]["stopped"] = dict(stop)
    rows, launches = MD.decide(dict(CFG, _code="code-B"), st, f, NOW + 120)
    ok(row_of(rows)["decision"] == "launch" and "code changed" in str(row_of(rows).get("stop_lifted")),
       "retry 10: a stop an older build wrote still lifts once the pipeline's code changes", row_of(rows))
    st["mods"]["A"]["stopped"] = dict(stop, tries=3)
    rows, launches = MD.decide(dict(CFG, _code="code-C"), st, f, NOW + 180)
    ok(row_of(rows)["decision"] == "stopped", "retry 11 (control): three failed tries end the retries",
       row_of(rows)["decision"])


T = 250_000     # weighted_v2 tokens per list dollar (role_launch.WT_PER_LIST_USD)


# ---- refund -----------------------------------------------------------------------------------------------------------

def blind(usd_other, killed_usd, killed=True, word=None, refunds=None):
    """usd_other, killed_usd: list dollars, as these checks were first written; the facts carry weighted tokens."""
    col = M.COL["blind_challenge"]
    usd_other, killed_usd = int(round(usd_other * T)), int(round(killed_usd * T))
    f = {"A": {"mod": "A", "stage": "blind_challenge", "version": "0.1.0", "cycle": 3, "visit_first": 1, "exit": {},
               "live_units": [], "last_end": None, "owed": "cycle", "blind_runs": ["rm-k"],
               "killed": {"rm-k": {"why": "killed with no result JSON", "state": "finished", "returned": True}}
               if killed else {},
               "box_runs": {col: {"rm-old": usd_other, "rm-k": killed_usd}}, "run_tokens": {"rm-k": killed_usd}}}
    s = {"blind_auto": [{"visit_id": "0.1.0#1", "cycle": 3, "unit": "rm-k", "item": "ITEM_K", "tries": 1,
                         "failed": None}]}
    if refunds:
        s["refunds"] = refunds
    if word:
        s["convergence"] = {"4+5": word}
    return {"mods": {"A": s}}, f


def refund_main():
    """The owner, by card 2026-11-18 11:06 AM PST (design/specs/2026-11-18-pipeline-control-surface/03-merged.md,
    Rulings 1): a void run's spend "Does not count" toward the stage ceiling. These checks read "the killed cycle's
    dollars are refunded once past the ceiling" (RIMMANDRAKE_REFUND_KILLED_RUN_DOLLARS_AT_THE_CEILING): a killed run's
    dollars are now never charged, so nothing is refunded and none is given back twice (item
    RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT)."""
    st, f = blind(66.0, 20.0)
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    r = row_of(rows)
    ok(r["decision"] == "launch" and launches == ["A"] and not r.get("refund") and r.get("stage_tokens") == 66 * T
       and r.get("void_tokens") == 20 * T,
       "refund 1: USD 86 with the killed cycle's USD 20 in it: the 20 is void spend, off the ceiling (66 counted), "
       "the cycle relaunches with no refund", r)
    d = tempfile.mkdtemp(prefix="mat_refund_")
    try:
        p = os.path.join(d, "releases.jsonl")
        r["decision"], r["unit"] = "launched", "rm-k2"
        MD.book_refunds(st, rows, NOW, path=p)
        recs, bad = MD.read_releases(p)
        ok(recs == [] and not st["mods"]["A"].get("refunds"),
           "refund 2: no release record is written: there is nothing to give back", recs)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    st, f = blind(86.0, 0.0, killed=False)
    f["A"]["blind_runs"] = []
    st["mods"]["A"]["blind_auto"] = []
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    ok(row_of(rows)["decision"] == "ceiling" and not launches,
       "refund 4 (control): a plain overspend with no killed run pauses at the ceiling", row_of(rows)["decision"])
    st, f = blind(95.0, 5.0)
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    ok(row_of(rows)["decision"] == "ceiling" and not launches and row_of(rows).get("stage_tokens") == 95 * T,
       "refund 5 (control): the counted spend alone (95) still pauses at the ceiling", row_of(rows)["decision"])
    st, f = blind(66.0, 20.0, word="DIVERGING")
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    ok(row_of(rows)["decision"] == "launch" and launches == ["A"],
       "refund 6: a DIVERGING stage no longer holds a void run's dollars: they are off the ceiling", row_of(rows))
    st, f = blind(66.0, 20.0, refunds={"rm-k": {"at": NOW - 60}})
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    ok(row_of(rows)["decision"] == "launch" and not row_of(rows).get("refund"),
       "refund 7: a run refunded under the old rule is not counted again either", row_of(rows)["decision"])
    st, f = blind(66.0, 20.0, killed=False)
    st["mods"]["A"]["voided"] = [{"book": "blind_auto", "unit": "rm-k", "class": "void_hand",
                                  "entry": st["mods"]["A"].pop("blind_auto")[0]}]     # as sync_dispatch moves it
    f["A"]["blind_runs"] = []
    rows, launches = MD.decide(CFG, st, f, NOW, releases=([], 0))
    ok(row_of(rows).get("void_tokens") == 20 * T and row_of(rows).get("stage_tokens") == 66 * T,
       "refund 8: a hand-voided run's dollars are void spend too", row_of(rows))


# ---- briefs -----------------------------------------------------------------------------------------------------------

def briefs_main():
    rules = AUT.STEWARD_RULES
    ok("re-pin" in rules.lower() and "never re-pinned" in rules,
       "briefs 1: the steward's rules carry the re-pin rule (test text or bookkeeping only; a changed bar never)")
    ok(all(w in rules for w in ("RECORD GAP", "CRITERION FLAW", "REAL MISS")),
       "briefs 2: the steward's rules carry the neutral-fixer triage of a not-met reason")
    ok("tests_edited.json" in rules and "weakened" in rules,
       "briefs 3: the steward reads the judge's test edits for a weakened assertion")
    rule = getattr(M, "SELF_CHECK_RULE", "")
    ok("maturation.py next" in rule and "format" in rule and "never a verdict" in rule,
       "briefs 4: one rule tells a judging run to read its own record with the pipeline's reader before it stops", rule)
    users = [n for n, fn in inspect.getmembers(M, inspect.isfunction) if "SELF_CHECK_RULE" in inspect.getsource(fn)]
    ok(len(users) >= 2, "briefs 5: the blind judge's and the in-game driver's briefs both carry it", users)


# ---- acts -------------------------------------------------------------------------------------------------------------

def acts_main():
    if MH is None:
        ok(False, "acts: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        sd = MD.sdir()
        cdir = os.path.join(root, "design", "concepts", "A")
        os.makedirs(os.path.join(cdir, "version"))
        os.makedirs(os.path.join(root, "design", "RimMandrake"))
        with open(os.path.join(root, "design", "RimMandrake", "pipeline_interventions_census_2026-11-15.md"), "w") as f:
            f.write("| A killed run is not a failed run | 3 | ... |\n")
        t0 = NOW - 3 * 3600
        iso = MH.iso
        with open(os.path.join(cdir, "stage.json"), "w") as f:
            json.dump({"coverage_releases": [{"at": iso(t0 + 60), "why": "one more look after the fixes"}]}, f)
        with open(os.path.join(cdir, "version", "stage_record.json"), "w") as f:
            json.dump({"moves": [
                {"from": "offline_build", "to": "blind_challenge", "at": iso(t0 + 400), "by": "BENCH", "why": "by hand"},
                {"from": "blind_challenge", "to": "in_game", "at": iso(t0 + 420), "by": "BENCH", "why": "steward",
                 "unit": "rm-detached-steward-1"}]}, f)
        with open(MD.releases_path(), "w") as f:
            f.write(json.dumps({"id": "rel-hand", "ts": iso(t0 + 10), "mod": "A", "stage": "blind_challenge",
                                "by": "BENCH", "read_usd": 86.0, "release_usd": 20.0,
                                "why": "the mod is converging"}) + "\n")
            f.write(json.dumps({"id": "rel-auto", "ts": iso(t0 + 20), "mod": "A", "stage": "blind_challenge",
                                "by": "RUNNER", "read_usd": 86.0, "release_usd": 20.0, "auto": True,
                                "why": "delegated: killed-run refund"}) + "\n")
        st = {"hands": {"since": t0 - 10, "last_tick": NOW - 60},
              "mods": {"A": {
                  "cleared": [{"at": t0 + 30, "why": "fixed by RIMMANDRAKE_KNOWN_FOLLOW_UP_ITEM, retry", "was": None}],
                  "blind_auto": [{"unit": "rm-tick-judge", "item": "RIMMANDRAKE_JUDGE_A_BLIND_CYCLE_ONE"}],
                  "steward": {"k": {"unit": "rm-steward", "item": "RIMMANDRAKE_ROUTE_A_BACK"}},
                  "fixers": {"RIMMANDRAKE_FIX_A_ROW": {"unit": None, "item": "RIMMANDRAKE_FIX_A_ROW"}},
                  "watch": {"unit": "rm-hand-builder", "ours": False, "at": t0 + 200, "refused": 2}}}}
        facts = {"A": {"stage": "offline_build", "runs_seen": [
            {"unit": "rm-tick-judge", "item": "RIMMANDRAKE_JUDGE_A_BLIND_CYCLE_ONE", "at": t0 + 40, "end": t0 + 45},
            {"unit": "rm-hand-judge", "item": "RIMMANDRAKE_CHALLENGE_A_BLIND_BY_HAND", "at": t0 + 50},
            {"unit": "rm-hand-fixer", "item": "RIMMANDRAKE_FIX_A_ROW", "at": t0 + 55},
            {"unit": "rm-feature", "item": "RIMMANDRAKE_BUILD_A_NEW_FEATURE", "at": t0 + 56},
            {"unit": "rm-hand-builder", "item": "RIMMANDRAKE_BUILD_A_CHECKS", "at": t0 + 200},
            {"unit": "rm-before", "item": "RIMMANDRAKE_CHALLENGE_A_BLIND_OLD", "at": t0 - 500}]}}
        events = [
            {"event": "close", "id": "RIMMANDRAKE_ROUTE_A_BACK", "seat": "BENCH", "ts": iso(t0 + 300)},
            {"event": "close", "id": "RIMMANDRAKE_JUDGE_A_BLIND_CYCLE_ONE", "seat": "BENCH", "ts": iso(t0 + 310),
             "role_unit": "rm-tick-judge"},
            {"event": "close", "id": "RIMMANDRAKE_SOMETHING_ELSE", "seat": "BENCH", "ts": iso(t0 + 320)}]
        known = {"RIMMANDRAKE_KNOWN_FOLLOW_UP_ITEM"}
        fx = {"events": lambda: events, "known": lambda: known}
        cfg = dict(CFG)
        rd = {"needs_conductor": []}
        MH.observe(root, cfg, st, facts, NOW, rd, fx)
        acts = {a["id"]: a for a in MH.read_acts()}
        kinds = sorted(a["kind"] for a in acts.values())
        ok(kinds == sorted(["ceiling_release", "clear", "coverage_release", "hand_run", "hand_run", "hand_run",
                            "hand_move", "hand_close"]),
           "acts 1: one act each for the hand release, the clear, the coverage release, three hand runs doing a "
           "stage's work (a blind judge, a road-back fix, a builder the tick did not launch), the hand move and the "
           "hand close", kinds)
        ok("rel-auto" not in acts and not any("rm-tick-judge" in a["id"] or "rm-feature" in a["id"] or
                                              "rm-before" in a["id"] for a in acts.values()),
           "acts 2 (control): the pipeline's own refund, its own judge, a feature build and a run from before the "
           "recorder started are not hand acts", sorted(acts))
        ok(not any(a["kind"] == "hand_move" and "in_game" in a["what"] for a in acts.values()),
           "acts 3 (control): a move a run made (it carries its unit) is not a hand move")
        ok(sum(1 for a in acts.values() if a["kind"] == "hand_close") == 1,
           "acts 4 (control): a close by the item's own run, and a close of an item the tick never launched, are not "
           "hand closes")
        MH.observe(root, cfg, st, facts, NOW + 60, {"needs_conductor": []}, fx)
        ok(len(MH.read_acts()) == len(acts), "acts 5: a second pass records nothing twice", len(MH.read_acts()))

        folds = MH.read_folds()
        clear_id = [i for i, a in acts.items() if a["kind"] == "clear"][0]
        ok(clear_id in folds and "RIMMANDRAKE_KNOWN_FOLLOW_UP_ITEM" in str(folds[clear_id]),
           "acts 6: an act whose reason names a ledger item is folded by that item", folds.get(clear_id))
        ok("rel-hand" not in folds, "acts 7 (control): an act whose reason names no ledger item stays unfolded")
        h = rd.get("hand_acts") or {}
        ok(h.get("open") == len(acts) - 1 and h.get("overdue") == 0,
           "acts 8: three hours on, the unfolded acts are open and none is overdue", h)

        rd2 = {"needs_conductor": []}
        MH.observe(root, cfg, st, facts, NOW + 26 * 3600, rd2, dict(fx, quiet_gap=True))
        h2 = rd2.get("hand_acts") or {}
        ok(h2.get("overdue") == len(acts) - 1 and any("fold" in x and "rel-hand" in x for x in rd2["needs_conductor"]),
           "acts 9: a day on, every unfolded act is overdue and a Needs Conductor line names the act and the fold "
           "command", (h2, rd2["needs_conductor"][:1]))

        rc, text = MH.fold(root, "rel-hand", item="RIMMANDRAKE_NOT_A_REAL_ITEM", fx=fx)
        ok(rc == 2 and "REFUSED" in text, "acts 10: fold refuses an item that is not on the ledger", text)
        rc, text = MH.fold(root, "rel-hand", census="A row nobody wrote", fx=fx)
        ok(rc == 2 and "REFUSED" in text, "acts 11: fold refuses a census row that no census file holds", text)
        rc, text = MH.fold(root, "no-such-act", item="RIMMANDRAKE_KNOWN_FOLLOW_UP_ITEM", fx=fx)
        # an id the tick has not recorded yet (clear printed it seconds before the tick ran) is kept, never refused
        # (RIMMANDRAKE_NEVER_REFUSE_THE_CONDUCTOR_SEVEN_REFUSALS_ONE_NIGHT); it applies when the act is recorded
        ok(rc == 0 and "KEPT" in text and MH.read_folds().get("no-such-act", {}).get("pending_act"),
           "acts 12: a fold of an act id not yet recorded is kept, marked pending_act", text)
        rc, text = MH.fold(root, "rel-hand", census="A killed run is not a failed run", fx=fx)
        ok(rc == 0 and "rel-hand" in MH.read_folds(), "acts 13: fold accepts a row the census holds", text)
        rd3 = {"needs_conductor": []}
        MH.observe(root, cfg, st, facts, NOW + 26 * 3600 + 60, rd3, fx)
        ok((rd3.get("hand_acts") or {}).get("overdue") == len(acts) - 2, "acts 14: a folded act stops being overdue",
           rd3.get("hand_acts"))

        # a settings edit and a gap in the tick
        st2 = {"mods": {}}
        MH.observe(root, cfg, st2, {}, NOW, {"needs_conductor": []}, fx)
        n0 = len(MH.read_acts())
        MH.observe(root, dict(cfg, _blind_doc="words only"), st2, {}, NOW + 60, {"needs_conductor": []}, fx)
        ok(len(MH.read_acts()) == n0, "acts 15 (control): the first reading of the settings and a doc-only edit are "
           "no act", len(MH.read_acts()) - n0)
        MH.observe(root, dict(cfg, max_live=6), st2, {}, NOW + 120, {"needs_conductor": []}, fx)
        new = [a for a in MH.read_acts() if a["kind"] == "settings_edit"]
        ok(len(new) == 1 and "max_live" in new[0]["what"] and "4" in new[0]["what"] and "6" in new[0]["what"],
           "acts 16: a changed setting is one act naming the key and both values", new)
        MH.observe(root, dict(cfg, max_live=6), st2, {}, NOW + 120 + 45 * 60, {"needs_conductor": []}, fx)
        gaps = [a for a in MH.read_acts() if a["kind"] == "tick_gap"]
        ok(len(gaps) == 1 and "45 min" in gaps[0]["what"], "acts 17: a tick that did not run for 45 minutes is one act",
           gaps)
        # RIMMANDRAKE_KEY_SETTINGS_EDITS_BY_OCCURRENCE_ABAB_LOST_ONE: 4 -> 6 (above), 6 -> 4, 4 -> 6 is three edits
        t_ = NOW + 120 + 45 * 60
        for k_, v_ in enumerate((4, 6)):
            MH.observe(root, dict(cfg, max_live=v_), st2, {}, t_ + 60 * (k_ + 1), {"needs_conductor": []}, fx)
        edits = [a for a in MH.read_acts() if a["kind"] == "settings_edit"]
        ok(len(edits) == 3, "acts 17b: a setting changed 4 -> 6, back to 4, then to 6 again is three settings edits",
           [a["what"] for a in edits])

        # an act from before the census is recorded folded by it
        st3 = {"hands": {"since": MH.BASELINE_TS - 7200, "last_tick": NOW - 60},
               "mods": {"A": {"cleared": [{"at": MH.BASELINE_TS - 3600, "why": "old", "was": None}]}}}
        for n in (MH.ACTS, MH.FOLDS):
            if os.path.exists(os.path.join(sd, n)):
                os.remove(os.path.join(sd, n))
        os.remove(MD.releases_path())
        os.remove(os.path.join(cdir, "stage.json"))
        os.remove(os.path.join(cdir, "version", "stage_record.json"))
        MH.observe(root, cfg, st3, {}, NOW, {"needs_conductor": []}, fx)
        a3 = MH.read_acts()
        ok(len(a3) == 1 and a3[0]["id"] in MH.read_folds() and "census" in str(MH.read_folds()[a3[0]["id"]]),
           "acts 18: an act older than the census is recorded as folded by the census", (a3, MH.read_folds()))

        # the alarm: ops_watch reads the count; the rule has a fixed name
        with open(os.path.join(REPO, "src", "RimMandrake", "Utils", "ops_watch_rules.json"), encoding="utf-8") as f:
            targets = json.load(f).get("targets") or []
        rule = [t for t in targets if t.get("key") == "maturation.hand_acts_overdue"]
        ok(len(rule) == 1 and rule[0].get("name") == "OPS_MATURATION_HAND_ACT_UNFOLDED" and rule[0].get("alarm") is True
           and rule[0].get("op") == ">" and rule[0].get("value") == 0,
           "acts 19: ops_watch_rules.json alarms on maturation.hand_acts_overdue > 0 under one fixed name", rule)
        import ops_watch as OW
        with open(os.path.join(sd, "reading.json"), "w") as f:
            json.dump({"at": NOW, "hand_acts": {"open": 3, "overdue": 2, "oldest_h": 30.0, "ids": ["x", "y"]}}, f)
        got = OW.c_maturation(NOW + 30, {}, {})
        m = got.get("maturation.hand_acts_overdue")
        ok(isinstance(m, dict) and m.get("v") == 2 and m.get("m") == "MEASURED",
           "acts 20: ops_watch's maturation family reads the overdue count", m)
        with open(os.path.join(sd, "reading.json"), "w") as f:
            json.dump({"at": NOW}, f)
        m = OW.c_maturation(NOW + 30, {}, {}).get("maturation.hand_acts_overdue")
        ok(isinstance(m, dict) and m.get("m") == "UNMEASURED" and m.get("v") is None,
           "acts 21 (control): a reading with no hand-act block is UNMEASURED, never 0", m)
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)
    src = inspect.getsource(M)
    ok('"unit": os.environ.get("RM_ROLE_UNIT") or None' in src,
       "acts 22: maturation.py's advance writes the run's unit into the move, so a move without one is a hand's")


# ---- chores -----------------------------------------------------------------------------------------------------------

def chores_main():
    calls = []
    fx = {"backfill": lambda: calls.append("backfill") or "backfilled 2", "reap": lambda u: calls.append(u) or "reaped"}
    facts = {"A": {"dead_unfinished": ["rm-dead"], "killed": {}}, "B": {"dead_unfinished": [], "killed": {}}}
    st = {}
    out = MD.slow_chores(st, facts, NOW, fx)
    ok(calls == ["backfill"] and out, "chores 1: the first pass reads back run dollars; a run only just seen dead is "
       "left (its own finish may be running)", calls)
    MD.slow_chores(st, facts, NOW + 600, fx)
    ok(calls == ["backfill"], "chores 2 (control): ten minutes on, nothing runs again", calls)
    MD.slow_chores(st, facts, NOW + 1900, fx)
    ok(calls == ["backfill", "backfill", "rm-dead"], "chores 3: thirty minutes on, the dollars are read again and the "
       "run dead all that time is finished", calls)
    facts["A"]["killed"] = {"rm-dead": {"why": "killed"}}
    MD.slow_chores(st, facts, NOW + 4000, fx)
    ok(calls[-1] == "backfill", "chores 4 (control): a killed blind or in-game run is left to its own retry path",
       calls[-2:])

    def boom():
        raise RuntimeError("disk")
    out = MD.slow_chores({}, {}, NOW, {"backfill": boom, "reap": lambda u: "x"})
    ok("failed" in str(out), "chores 5: a chore that fails is reported and never costs the tick", out)


# ---- stalled ----------------------------------------------------------------------------------------------------------

def stalled_main():
    import detached_helper as DH
    fx = {"open_items": lambda ids: [], "designer_state": lambda m: {}, "version_locked": lambda m: True,
          "version_evidence": lambda m: None, "designer_unit": lambda m: None, "designer_chain": lambda m: None,
          "exam_gate": lambda m: None}

    def stalled(st, launches_book=True):
        f = offline(["a", "b"], live=["rm-builder"])
        f["A"]["version"] = "0.1.0"
        MD.decide(CFG, st, f, NOW)
        if launches_book:
            st["mods"]["A"]["launches"] = [{"unit": "rm-builder", "item": "RIMMANDRAKE_AUTOBUILD_A_TWO_BARS_LEFT",
                                            "stage": "offline_build"}]
        f = offline(["a", "b"], last_end=NOW - 600)
        f["A"]["version"] = "0.1.0"
        rows, launches = MD.decide(CFG, st, f, NOW + 60)
        return f, AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_tokens=2_000_000), st, f, rows, launches,
                              NOW + 60, fx)

    st = {}
    f, (rows, launches) = stalled(st)
    r = row_of(rows)
    ok(r.get("aut") == "steward" and r.get("steward_kind") == "builder_stalled" and launches == ["A"],
       "stalled 1: a builder that resolved none of its refused bars gets one steward run that finds out why, not a "
       "pause", {k: r.get(k) for k in ("decision", "aut", "steward_kind", "why")})
    ok("RIMMANDRAKE_AUTOBUILD_A_TWO_BARS_LEFT" in str(r.get("steward_need")) and "rm-builder" in str(r.get("steward_need")),
       "stalled 2: the steward is told the builder's unit and item", r.get("steward_need"))
    brief = AUT.steward_brief(REPO, "A", dict(r, stage="offline_build")) if r.get("steward_kind") else ""
    ok(all(w in brief for w in ("STOPPED EARLY", "WRONG KIND OF WORK", "PIPELINE DEFECT", "TOO BIG"))
       and "never run `maturation_dispatch.py clear`" in brief.lower().replace("never run", "never run"),
       "stalled 3: its brief names the four causes and forbids clearing the stop", brief[-900:])
    st["mods"]["A"].setdefault("steward", {})[r.get("steward_key")] = {"item": "X", "unit": "rm-s", "at": NOW,
                                                                         "failed": None, "tries": 1}
    f2 = offline(["a", "b"], last_end=NOW - 900)
    f2["A"]["version"] = "0.1.0"
    rows, launches = MD.decide(CFG, st, f2, NOW + 600)
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_tokens=2_000_000), st, f2, rows, launches,
                                 NOW + 600, fx)
    ok(row_of(rows)["decision"] == "steward_spent" and not launches,
       "stalled 4 (control): the same stall never gets a second steward run", row_of(rows)["decision"])

    st = {"mods": {"A": {"stopped": {"ids": ["a"], "at": NOW, "why": "USD 99.00 spent, at the ceiling",
                                     "ceiling": True}}}}
    f3 = offline(["a"])
    f3["A"].update(version="0.1.0", stage_runs={"rm-old": 99.0})
    rows, launches = MD.decide(CFG, st, f3, NOW)
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_tokens=2_000_000), st, f3, rows, launches, NOW, fx)
    ok(row_of(rows).get("steward_kind") != "builder_stalled" and not launches,
       "stalled 5 (control): a ceiling stop gets no such steward", row_of(rows).get("decision"))

    ok("ends when your turn ends" in DH.FOOTER and "foreground" in DH.FOOTER,
       "stalled 6: every detached run is told it ends with its turn and that helpers run in the foreground "
       "(Graffiti's builder ended 'waiting for the helpers to report', 2026-11-15)")
    # a blind cycle whose record has no exit block: the night's reconcile, as a steward run
    col = M.COL["blind_challenge"]
    fb = {"A": {"mod": "A", "stage": "blind_challenge", "version": "0.1.0", "cycle": 2, "visit": 1, "visit_first": 1,
                "exit": {"record": "design/concepts/A/version/blind_challenge/cycle_2"}, "live_units": [],
                "last_end": NOW - 900, "owed": "no exit block", "blind_runs": [], "killed": {},
                "box_runs": {col: {}}, "run_tokens": {}}}
    stb = {}
    rows, launches = MD.decide(CFG, stb, fb, NOW)
    ok(row_of(rows)["decision"] == "cycle_unfinished", "stalled 9 (setup): decide reads the cycle as unfinished",
       row_of(rows)["decision"])
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_tokens=2_000_000), stb, fb, rows, launches,
                                 NOW, fx)
    r9 = row_of(rows)
    ok(r9.get("aut") == "steward" and r9.get("steward_kind") == "cycle_unfinished" and launches == ["A"],
       "stalled 9: a blind cycle record with no exit block gets one steward run, not a pause",
       {k: r9.get(k) for k in ("decision", "aut", "steward_kind")})
    b9 = AUT.steward_brief(REPO, "A", dict(r9, stage="blind_challenge")) if r9.get("steward_kind") else ""
    ok("RECORD GAP" in b9 and "never write a verdict the files do not hold" in b9 and "lanes are not all there" in b9,
       "stalled 10: its brief completes the record from the files only, and stops when the judging itself is missing",
       b9[-600:])
    fi = {"A": dict(fb["A"], stage="in_game", owed="no exit block", visit=1, ingame_live=[], ingame_runs=[])}
    sti = {}
    rows, launches = MD.decide(CFG, sti, fi, NOW, bridge=lambda p: (True, "free"))
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_tokens=2_000_000), sti, fi, rows, launches,
                                 NOW, fx)
    ok(row_of(rows).get("steward_kind") != "cycle_unfinished" and not launches,
       "stalled 11 (control): an unfinished in-game visit stays a hand (the game it left needs a look)",
       row_of(rows).get("decision"))
    name = AUT.item_name({"mod": "A", "steward_kind": "builder_stalled", "stage": "offline_build"}, set())
    ok(name == "RIMMANDRAKE_TRIAGE_A_BUILDER_RESOLVED_NOTHING",
       "stalled 8: its item is named for what it does (the first live one was filed as ..._HAND_STEP)", name)
    src = inspect.getsource(AUT._execute_one)
    ok('"builder_stalled"' in src, "stalled 7: what the stalled-builder steward files is a road back, so fixers run it")


def false_hands_main():
    """RIMMANDRAKE_BOOK_FAILED_TICK_LAUNCHES_THREE_FALSE_HANDS, measured 2026-11-17: three of 13 open hand acts were not
    hands. Gimme Some Slack's in-game launches 1794831340 and 1794834319 failed (the tick booked unit=None, the launch
    record exists under the unit it tried) and read as hand launches; a builder on a pipeline-fix item whose id holds
    BLIND read as a blind judge. Written before the fix and watched failing on the base."""
    if MH is None:
        ok(False, "false hands: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_false_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "G", "version"))
        t0 = NOW - 3 * 3600
        tried = "rm-detached-bench-rimmandrake-drive-g-in-game-1794831340"
        ticket = "RIMMANDRAKE_DRIVE_G_IN_GAME_ACCEPTANCE_VISIT_ONE"
        st = {"hands": {"since": t0 - 10, "last_tick": NOW - 60},
              "mods": {"G": {"ingame_auto": [
                  {"visit_id": "0.1.0#1", "visit": 1, "unit": None, "item": ticket, "at": t0 + 10, "tries": 1,
                   "filed": True, "never_started": True, "tried": tried,
                   "failed": "filed; LAUNCH FAILED %s: systemd-run did not answer (OSError)" % tried}],
                  "blind_auto": [{"unit": "rm-tick-judge", "item": "RIMMANDRAKE_JUDGE_G_BLIND_CYCLE_ONE"}]}}}
        facts = {"G": {"stage": "in_game", "runs_seen": [
            {"unit": tried, "item": ticket, "at": t0 + 11, "end": None, "ran": False},
            {"unit": "rm-unstick", "item": "RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS", "at": t0 + 20},
            {"unit": "rm-hand-on-ticket", "item": "RIMMANDRAKE_JUDGE_G_BLIND_CYCLE_ONE", "at": t0 + 30}]}}
        fx = {"events": lambda: [], "known": lambda: set()}
        MH.observe(root, dict(CFG, advancing=["G"]), st, facts, NOW, {"needs_conductor": []}, fx)
        acts = [a for a in MH.read_acts() if a["kind"] == "hand_run"]
        ok(not any(tried in a["id"] for a in acts),
           "false hands 1: the tick's own failed launch (booked unit=None, its record under the unit it tried) is no "
           "hand act", [a["id"] for a in acts])
        ok(not any("rm-unstick" in a["id"] for a in acts),
           "false hands 2: a run on a non-ticket item whose id holds BLIND is no hand act", [a["id"] for a in acts])
        ok(sum(1 for a in acts if "rm-hand-on-ticket" in a["id"]) == 1,
           "false hands 3 (control): a hand launch on the tick's own blind ticket is still one hand act",
           [a["id"] for a in acts])
        # Codex review 2026-11-18: an unconfirmed launch booked `tried` that then ran is the tick's own, not a hand's;
        # and a failed launch (never ran, end None) hides no later hand move
        ok(not any("rm-tick-judge" in a["id"] for a in acts), "false hands 3b (control): the tick's own judge is no act")
        # RIMMANDRAKE_OWN_VOIDED_TICK_RUNS_ARCHIVE_HID_THEM: a tick run whose book entry run_void moved to `voided`
        # is still the tick's own, never a hand
        st_v = {"hands": {"since": t0 - 10, "last_tick": NOW - 60},
                "mods": {"V": {"voided": [{"book": "blind_auto", "key": 0, "unit": "rm-v", "class": "void_hand",
                                           "entry": {"unit": "rm-v", "item": "RIMMANDRAKE_JUDGE_V_BLIND_CYCLE_ONE"}},
                                          {"book": "fixers", "key": "FIX_V", "unit": None, "class": "void_system",
                                           "entry": {"unit": None, "tried": "rm-v-fix", "item": "FIX_V"}}]}}}
        os.makedirs(os.path.join(root, "design", "concepts", "V", "version"), exist_ok=True)
        facts_v = {"V": {"stage": "blind_challenge", "runs_seen": [
            {"unit": "rm-v", "item": "RIMMANDRAKE_JUDGE_V_BLIND_CYCLE_ONE", "at": t0 + 60},
            {"unit": "rm-v-fix", "item": "FIX_V", "at": t0 + 70}]}}
        n_v = len(MH.read_acts())
        MH.observe(root, dict(CFG, advancing=["V"]), st_v, facts_v, NOW, {"needs_conductor": []}, fx)
        ok(len(MH.read_acts()) == n_v, "false hands 3c: a voided tick run (its entry moved to `voided`, booked unit or "
           "tried) is no hand act", [a["id"] for a in MH.read_acts()][n_v:])
        facts_v["V"]["runs_seen"].append({"unit": "rm-v-hand-fix", "item": "FIX_V", "at": t0 + 90})
        MH.observe(root, dict(CFG, advancing=["V"]), st_v, facts_v, NOW + 30, {"needs_conductor": []}, fx)
        ok([a["id"] for a in MH.read_acts()][n_v:] == ["run-rm-v-hand-fix"],
           "false hands 3d: a later hand fix on a fixer ticket whose entry was voided is still one hand act",
           [a["id"] for a in MH.read_acts()][n_v:])
        # RIMMANDRAKE_OWN_CLEARED_TICK_RUNS_ALARM_CRIED_FIVE: `clear` moves ended entries to cleared[*].released
        u_c, i_c = MH.tick_units({"blind_auto": [], "cleared": [{"at": 1, "released": {
            "blind_auto": [{"unit": "U1", "item": "I1"}], "ingame_auto": [{"unit": "U3", "item": "I3"}],
            "steward": {"k": {"unit": "U2", "item": "I2"}}, "fixers": {"f": {"tried": "U4"}}}}]})
        ok({"U1", "U2", "U3", "U4"} <= u_c and {"I1", "I2", "I3"} <= i_c,
           "false hands 3e: a tick run whose entry sits in cleared[*].released is the tick's own", (u_c, i_c))
        e_c, _ = MH.tick_units({"cleared": [{"at": 1, "released": {}}, {"at": 2}, "x", {"released": []},
                                            {"released": {"blind_auto": None, "steward": [1], "fixers": {"a": 3}}}]})
        ok(e_c == set(), "false hands 3f: an empty or malformed `cleared` adds nothing", e_c)
        os.remove(os.path.join(MD.sdir(), MH.ACTS)) if os.path.exists(os.path.join(MD.sdir(), MH.ACTS)) else None
        late = "rm-detached-bench-rimmandrake-drive-g-in-game-1794834319"
        st["mods"]["G"]["ingame_auto"].append(
            {"visit_id": "0.1.0#2", "visit": 2, "unit": None, "item": ticket + "_TWO", "at": t0 + 40, "tries": 1,
             "filed": True, "never_started": True, "tried": late,
             "failed": "filed; LAUNCH UNCONFIRMED %s: systemd-run did not answer" % late})
        facts["G"]["runs_seen"].append({"unit": late, "item": ticket + "_TWO", "at": t0 + 41, "end": t0 + 900})
        with open(os.path.join(root, "design", "concepts", "G", "version", "stage_record.json"), "w") as f:
            json.dump({"moves": [{"from": "in_game", "to": "offline_build", "at": MH.iso(t0 + 1200), "by": "BENCH",
                                  "why": "by hand"}]}, f)
        MH.observe(root, dict(CFG, advancing=["G"]), st, facts, NOW + 30, {"needs_conductor": []}, fx)
        acts2 = MH.read_acts()
        ok(not any(late in a["id"] for a in acts2),
           "false hands 6: an unconfirmed launch booked `tried` that then ran is the tick's own run, no hand act",
           [a["id"] for a in acts2])
        ok(any(a["kind"] == "hand_move" for a in acts2),
           "false hands 7: a failed launch that never ran hides no later hand move", [a["kind"] for a in acts2])
        b = {"failed": "x; LAUNCH FAILED %s: pool full" % tried}
        ok(MD.tried_unit(b["failed"]) == tried if hasattr(MD, "tried_unit") else False,
           "false hands 4: the unit a failed launch tried is read from its failure text")
        ok((MD.tried_unit("LAUNCH UNCONFIRMED %s: systemd-run did not answer" % tried) == tried
            and MD.tried_unit("no free item name") is None and MD.tried_unit(None) is None)
           if hasattr(MD, "tried_unit") else False,
           "false hands 5: an unconfirmed launch's unit is read too; a failure that names none reads None")
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def road_back_main():
    """RIMMANDRAKE_COUNT_HAND_FIX_ON_UNBOOKED_ROAD_BACK_TICKET: the tick writes road_back as {caused_by, at, from}, so a
    hand fixer on an item the steward filed, before the tick books a fixer on it, read as no hand act. Written before
    the fix and watched failing on the base."""
    if MH is None:
        ok(False, "road back: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_rb_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "R", "version"))
        t0 = NOW - 3 * 3600
        st = {"hands": {"since": t0 - 10, "last_tick": NOW - 60},
              "mods": {"R": {"road_back": {"caused_by": "ROUTE_X", "at": t0, "from": "blind_challenge"},
                             "steward": {"k": {"unit": "rm-steward", "item": "ROUTE_X"}}}}}
        facts = {"R": {"stage": "offline_build", "runs_seen": [
            {"unit": "rm-steward", "item": "ROUTE_X", "at": t0 + 5, "end": t0 + 9},
            {"unit": "rm-hand-fix-me", "item": "FIX_ME", "at": t0 + 20},
            {"unit": "rm-feature-r", "item": "BUILD_R_FEATURE", "at": t0 + 30}]}}
        asked = []

        def caused_by(ids):
            asked.append(list(ids))
            return ["FIX_ME"] if "ROUTE_X" in ids else []
        fx = {"events": lambda: [], "known": lambda: set(), "caused_by": caused_by}
        MH.observe(root, dict(CFG, advancing=["R"]), st, facts, NOW, {"needs_conductor": []}, fx)
        acts = [a for a in MH.read_acts() if a["kind"] == "hand_run"]
        ok([a["id"] for a in acts] == ["run-rm-hand-fix-me"],
           "road back 1: a hand fixer on an item the road back's steward filed (no fixer booked) is one hand act; the "
           "steward's own run and a feature build are none", [a["id"] for a in acts])
        ok(len(asked) == 1, "road back 1b: the ledger is asked once per mod, only for a run nothing else classes", asked)
        os.remove(os.path.join(MD.sdir(), MH.ACTS)) if os.path.exists(os.path.join(MD.sdir(), MH.ACTS)) else None
        boom = dict(fx, caused_by=lambda ids: (_ for _ in ()).throw(OSError("ledger unreadable (selftest)")))
        st["hands"].pop("road_back_error", None)
        MH.observe(root, dict(CFG, advancing=["R"]), st, facts, NOW + 30, {"needs_conductor": []}, boom)
        ok("ledger unreadable" in str(st["hands"].get("road_back_error") or ""),
           "road back 2: a ledger read that fails costs only this source and is kept as could-not-look, never read "
           "as no items", st["hands"].get("road_back_error"))
        # the production reader: an item the steward filed and a fixer already closed still counts
        ldir = os.path.join(root, "infrastructure", "state", "ledger", "events")
        os.makedirs(ldir)
        with open(os.path.join(ldir, "BENCH.jsonl"), "w") as f:
            f.write(json.dumps({"event": "file", "id": "FIX_ME", "caused_by": "ROUTE_X", "title": "t"}) + "\n")
            f.write(json.dumps({"event": "close", "id": "FIX_ME"}) + "\n")
        os.remove(os.path.join(MD.sdir(), MH.ACTS)) if os.path.exists(os.path.join(MD.sdir(), MH.ACTS)) else None
        real = {k: v for k, v in fx.items() if k != "caused_by"}
        MH.observe(root, dict(CFG, advancing=["R"]), st, facts, NOW + 60, {"needs_conductor": []}, real)
        acts = [a for a in MH.read_acts() if a["kind"] == "hand_run"]
        ok([a["id"] for a in acts] == ["run-rm-hand-fix-me"] and not st["hands"].get("road_back_error"),
           "road back 3: the ledger reader finds a steward-filed item even after it closed", [a["id"] for a in acts])
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def fold_later_main():
    """RIMMANDRAKE_FOLD_RECORDED_HAND_ACTS_AFTER_KNOWN_FAILS: the automatic fold ran only on acts collected that tick, so
    an act appended on a tick whose ledger read failed (or a `record --why` naming an item) stayed open forever.
    Written before the fix and watched failing on the base."""
    if MH is None:
        ok(False, "fold later: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_fold_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "F", "version"))
        t0 = NOW - 3 * 3600
        # a sweep just ran: the retry must come from the failed read, not from a sweep falling due
        st = {"hands": {"since": t0 - 10, "last_tick": NOW - 60, "fold_at": NOW - 10},
              "mods": {"F": {"cleared": [{"at": t0 + 30, "why": "fixed by RIMMANDRAKE_FOLLOW_UP_F_ITEM, retry"}]}}}

        def blind():
            raise OSError("ledger unreadable (selftest)")
        try:
            MH.observe(root, dict(CFG, advancing=["F"]), st, {}, NOW, {"needs_conductor": []},
                       {"events": lambda: [], "known": blind})
        except Exception:   # noqa: BLE001  the base let a failed read out (the tick's guard caught it)
            pass
        acts = MH.read_acts()
        ok(len(acts) == 1 and acts[0]["id"] not in MH.read_folds(),
           "fold later 1: on a tick whose ledger read fails the act is recorded and not folded",
           [(a["id"], a["id"] in MH.read_folds()) for a in acts])
        rd = {"needs_conductor": []}
        MH.observe(root, dict(CFG, advancing=["F"]), st, {}, NOW + 60, rd,
                   {"events": lambda: [], "known": lambda: set()})
        ok(acts and acts[0]["id"] not in MH.read_folds(),
           "fold later 2: a ledger read of no items at all is blind, never a verdict: nothing folds", MH.read_folds())
        MH.observe(root, dict(CFG, advancing=["F"]), st, {}, NOW + 120, {"needs_conductor": []},
                   {"events": lambda: [], "known": lambda: {"RIMMANDRAKE_FOLLOW_UP_F_ITEM"}})
        f = MH.read_folds().get(acts[0]["id"]) if acts else None
        ok(bool(f) and f.get("item") == "RIMMANDRAKE_FOLLOW_UP_F_ITEM",
           "fold later 3: a later tick that reads the ledger folds the act its reason names", f)
        # RIMMANDRAKE_SPLIT_MANUAL_HAND_ACT_IDS_WITHIN_ONE_SECOND: two `record` calls in one second are two acts
        real_time = MH.time.time
        MH.time.time = lambda: NOW + 300.25
        try:
            import contextlib
            import io
            with contextlib.redirect_stdout(io.StringIO()):
                for why in ("same words", "same words"):
                    MH.main(["--root", root, "record", "--mod", "F", "--what", "timer paused by hand", "--why", why])
        finally:
            MH.time.time = real_time
        man = [a for a in MH.read_acts() if a["kind"] == "manual"]
        ok(len(man) == 2 and len({a["id"] for a in man}) == 2,
           "record 1: two record calls in the same second with the same kind, mod and what are two acts",
           [(a["id"], a["why"]) for a in man])
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def reclass_main():
    """RIMMANDRAKE_FOLD_HAND_RUNS_THE_BOOKS_NOW_OWN: an act recorded as a hand run before a tick_units fix (voided
    11-18, cleared 11-20) stayed open for good, although the current books class its unit as the tick's own. Seven
    such acts held maturation.hand_acts_overdue over 0 at his rung on 11-21. Written before the fix and watched
    failing on the base."""
    if MH is None:
        ok(False, "reclass: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_reclass_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "F", "version"))
        t0 = NOW - 2 * 86400
        for u in ("rm-detached-own-1", "rm-detached-hand-2"):
            MH._append(MH.ACTS, MH._act("run-" + u, t0, "hand_run", "F", "an in-game driver launched by hand: " + u)
                       | {"recorded": t0 + 60})
        st = {"hands": {"since": t0 - 10, "last_tick": NOW - 60, "fold_at": NOW - 10},
              "mods": {"F": {"cleared": [{"at": t0 + 30, "released": {
                  "ingame_auto": [{"unit": "rm-detached-own-1", "item": "RIMMANDRAKE_DRIVE_F_VISIT_TWO"}]}}]}}}
        rd = {"needs_conductor": []}
        MH.observe(root, dict(CFG, advancing=["F"]), st, {}, NOW, rd,
                   {"events": lambda: [], "known": lambda: {"RIMMANDRAKE_DRIVE_F_VISIT_TWO"}})
        folds = MH.read_folds()
        f = folds.get("run-rm-detached-own-1")
        ok(bool(f) and f.get("by") == "maturation_hands",
           "reclass 1: an open hand-run act whose unit the current books hold is folded as the tick's own", f)
        ok("run-rm-detached-hand-2" not in folds,
           "reclass 2: an open hand-run act whose unit no book holds stays open", folds.get("run-rm-detached-hand-2"))
        h = rd.get("hand_acts") or {}
        ok(h.get("overdue") == 1 and h.get("ids") == ["run-rm-detached-hand-2"],
           "reclass 3: the overdue count and its ids carry only the real hand run", h)
        rd2 = {"needs_conductor": []}
        MH.observe(root, dict(CFG, advancing=["F"]), st, {}, NOW + 60, rd2,
                   {"events": lambda: [], "known": lambda: {"RIMMANDRAKE_DRIVE_F_VISIT_TWO"}})
        n = sum(1 for line in open(os.path.join(MD.sdir(), MH.FOLDS)) if "rm-detached-own-1" in line)
        ok(n == 1, "reclass 4: a second tick folds the act no second time", n)
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def continued_main():
    """A run that left_open_continue.py started is a program's launch. Until 2026-11-23 each one was recorded as a hand
    launch: 7 of the 17 open hand runs of that day were the pipeline continuing itself."""
    if MH is None:
        ok(False, "continued: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_continued_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    recs = {"rm-detached-cont": {"continued_from": "rm-detached-first"}, "rm-detached-hand": {"continued_from": None},
            "rm-detached-old-cont": {"continued_from": "rm-detached-first"}}
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "F", "version"))
        item = "RIMMANDRAKE_DRIVE_F_IN_GAME_VISIT_TWO"
        MH._append(MH.ACTS, MH._act("run-rm-detached-old-cont", NOW - 2 * 86400, "hand_run", "F", "x") | {"recorded": NOW})
        st = {"hands": {"since": NOW - 3600, "last_tick": NOW - 60, "fold_at": NOW - 10}, "mods": {"F": {}}}
        facts = {"F": {"runs_seen": [{"unit": u, "item": item, "at": NOW - 600, "end": NOW - 60}
                                     for u in ("rm-detached-cont", "rm-detached-hand", "rm-detached-no-record")]}}
        MH.observe(root, dict(CFG, advancing=["F"]), st, facts, NOW, {"needs_conductor": []},
                   {"events": lambda: [], "known": lambda: {item}, "record": recs.get})
        ids = {a["id"] for a in MH.read_acts()}
        ok("run-rm-detached-cont" not in ids, "continued 1: a continuation is no hand run", ids)
        ok("run-rm-detached-hand" in ids, "continued 2: a run with no parent run is a hand run", ids)
        ok("run-rm-detached-no-record" in ids, "continued 3: a run whose record cannot be read stays a hand run", ids)
        f = MH.read_folds().get("run-rm-detached-old-cont")
        ok(bool(f) and "left_open_continue" in f.get("why", ""),
           "continued 4: one already recorded as a hand run folds by itself, with its reason", f)
        ok("run-rm-detached-hand" not in MH.read_folds(), "continued 5: the real hand run stays open")
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def his_walk_main():
    """RIMMANDRAKE_FOLD_HIS_WALK_VERDICT_NOT_A_HAND_ACT, measured 2026-11-26: his own walk pass of Pyrelands 0.1.0
    (his_walk -> passed by OWNER, 2026-11-24) was recorded as a hand move and read overdue for 43 h at his rung on
    maturation-20261121225203. The walk verdict is his act (one of his five: the pass at his walk); no run makes it, so
    there is no hand judgement to build into the pipeline. Written before the fix and watched failing on the base."""
    if MH is None:
        ok(False, "his walk: maturation_hands.py exists")
        return
    root = tempfile.mkdtemp(prefix="mat_hands_walk_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    try:
        MD.sdir()
        os.makedirs(os.path.join(root, "design", "concepts", "W", "version"))
        t0 = NOW - 3 * 3600
        # one recorded before the fix, still open
        MH._append(MH.ACTS, MH._act("move-W-1", NOW - 2 * 86400, "hand_move", "W",
                                    "moved his_walk -> passed by OWNER, naming no run", "his walk of W") | {"recorded": NOW})
        with open(os.path.join(root, "design", "concepts", "W", "version", "stage_record.json"), "w") as f:
            json.dump({"moves": [
                {"from": "his_walk", "to": "passed", "at": MH.iso(t0 + 100), "by": "OWNER", "why": "his walk of W"},
                {"from": "his_walk", "to": "offline_build", "at": MH.iso(t0 + 200), "by": "OWNER", "why": "walk 2"},
                {"from": "his_walk", "to": "in_game", "at": MH.iso(t0 + 300), "by": "DISPATCH", "why": "checks owed"},
                {"from": "in_game", "to": "passed", "at": MH.iso(t0 + 400), "by": "OWNER", "why": "skip"}]}, f)
        st = {"hands": {"since": t0 - 10, "last_tick": NOW + 2 * 86400 - 60}, "mods": {"W": {}}}
        fx = {"events": lambda: [], "known": lambda: set()}
        rd = {"needs_conductor": []}
        MH.observe(root, dict(CFG, advancing=["W"]), st, {"W": {"stage": "passed", "runs_seen": []}},
                   NOW + 2 * 86400, rd, fx)
        folds = MH.read_folds()
        acts = [(a["what"], a["id"]) for a in MH.read_acts() if a["mod"] == "W"]
        walk = [i for w, i in acts if w.startswith("moved his_walk -> ") and " by OWNER," in w]
        ok(len(walk) == 3 and all(i in folds for i in walk),
           "his walk 1: each move off his_walk by OWNER (pass or road back, recorded before or after the fix) folds by "
           "itself", (walk, sorted(folds)))
        ok(all("five acts" in (folds.get(i) or {}).get("why", "") for i in walk),
           "his walk 2: the fold names why (his act, one of his five)", [folds.get(i) for i in walk])
        others = [i for w, i in acts if i not in walk]
        ok(len(others) == 2 and not any(i in folds for i in others),
           "his walk 3 (control): a move off his_walk by DISPATCH, and a move by OWNER from another stage, stay open",
           (others, sorted(folds)))
        ok(rd["hand_acts"]["overdue"] == 2, "his walk 4: only the two real hand moves read overdue", rd["hand_acts"])
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


SECTIONS = (("stalled", stalled_main), ("stop", stop_main), ("retry", retry_main), ("refund", refund_main), ("briefs", briefs_main),
            ("acts", acts_main), ("chores", chores_main), ("false_hands", false_hands_main),
            ("road_back", road_back_main), ("fold_later", fold_later_main), ("reclass", reclass_main),
            ("continued", continued_main), ("his_walk", his_walk_main))

if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    for name, fn in SECTIONS:
        if only in (None, name):
            guard(fn, "%s: the section ran to its end" % name)
    print("%d FAIL" % len(FAILS) if FAILS else "all PASS")
    sys.exit(1 if FAILS else 0)
