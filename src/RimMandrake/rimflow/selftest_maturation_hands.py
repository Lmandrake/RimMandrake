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
CFG = {"enabled": True, "advancing": ["A"], "cap_usd": 15, "max_live": 4, "stage_ceiling_usd": 100, "settle_s": 180,
       "blind_enabled": True, "blind_cap_usd": 20, "blind_auto_cycles_per_visit": 3, "launch_tries": 3,
       "ingame_enabled": True, "ingame_cap_usd": 30, "ingame_auto_runs_per_visit": 1}


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
                  "live_units": list(live), "last_end": last_end, "owed": owed, "stage_runs": {}, "run_usd": {},
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

    st = {}
    MD.decide(CFG, st, offline(["a", "b"], live=["rm-builder"]), NOW)
    rows, _ = MD.decide(CFG, st, offline(["a", "b"], last_end=NOW - 600), NOW + 60)
    ok(row_of(rows)["decision"] == "stopped" and "none resolved" in row_of(rows)["why"],
       "stop 2 (control): a builder seen with 2 refused bars that resolved none still stops", row_of(rows))

    st = {"mods": {"A": {"stopped": {"ids": [], "at": NOW - 900,
                                     "why": "run rm-hand-fix ended and the refused bars went 0 -> 0, none resolved"}}}}
    rows, launches = MD.decide(CFG, st, offline(["a"]), NOW)
    ok(row_of(rows)["decision"] == "launch" and launches == ["A"],
       "stop 3: a stop already written on an empty refused set lifts itself and build work launches", row_of(rows))
    ok("no refused bars" in str(row_of(rows).get("stop_lifted")), "stop 3: the reading says what lifted it",
       row_of(rows).get("stop_lifted"))

    st = {"mods": {"A": {"stopped": {"ids": ["a"], "at": NOW - 900,
                                     "why": "run rm-builder ended and the refused bars went 1 -> 1, none resolved"}}}}
    rows, launches = MD.decide(CFG, st, offline(["a"]), NOW)
    ok(row_of(rows)["decision"] == "stopped" and not launches,
       "stop 4 (control): a stop on the same non-empty refusals stays", row_of(rows)["decision"])

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
    ok(not sa.get("stopped") and [x.get("book") for x in sa.get("system_faults") or []] == ["launches"]
       and "a rule said no" in sa["system_faults"][0]["cause"],
       "retry 8: a failed Stage 3 launch writes no stop: a system fault naming its cause", sa.get("system_faults"))
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


# ---- refund -----------------------------------------------------------------------------------------------------------

def blind(usd_other, killed_usd, killed=True, word=None, refunds=None):
    col = M.COL["blind_challenge"]
    f = {"A": {"mod": "A", "stage": "blind_challenge", "version": "0.1.0", "cycle": 3, "visit_first": 1, "exit": {},
               "live_units": [], "last_end": None, "owed": "cycle", "blind_runs": ["rm-k"],
               "killed": {"rm-k": {"why": "killed with no result JSON", "state": "finished", "returned": True}}
               if killed else {},
               "box_runs": {col: {"rm-old": usd_other, "rm-k": killed_usd}}, "run_usd": {"rm-k": killed_usd}}}
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
    ok(r["decision"] == "launch" and launches == ["A"] and not r.get("refund") and r.get("stage_usd") == 66.0
       and r.get("void_usd") == 20.0,
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
    ok(row_of(rows)["decision"] == "ceiling" and not launches and row_of(rows).get("stage_usd") == 95.0,
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
    ok(row_of(rows).get("void_usd") == 20.0 and row_of(rows).get("stage_usd") == 66.0,
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
        ok(rc == 2, "acts 12: fold refuses an act id that was never recorded", text)
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
        return f, AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_usd=8), st, f, rows, launches,
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
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_usd=8), st, f2, rows, launches,
                                 NOW + 600, fx)
    ok(row_of(rows)["decision"] == "steward_spent" and not launches,
       "stalled 4 (control): the same stall never gets a second steward run", row_of(rows)["decision"])

    st = {"mods": {"A": {"stopped": {"ids": ["a"], "at": NOW, "why": "USD 99.00 spent, at the ceiling",
                                     "ceiling": True}}}}
    f3 = offline(["a"])
    f3["A"].update(version="0.1.0", stage_runs={"rm-old": 99.0})
    rows, launches = MD.decide(CFG, st, f3, NOW)
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_usd=8), st, f3, rows, launches, NOW, fx)
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
                "box_runs": {col: {}}, "run_usd": {}}}
    stb = {}
    rows, launches = MD.decide(CFG, stb, fb, NOW)
    ok(row_of(rows)["decision"] == "cycle_unfinished", "stalled 9 (setup): decide reads the cycle as unfinished",
       row_of(rows)["decision"])
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_usd=8), stb, fb, rows, launches,
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
    rows, launches = AUT.resolve(REPO, dict(CFG, steward_enabled=True, steward_cap_usd=8), sti, fi, rows, launches,
                                 NOW, fx)
    ok(row_of(rows).get("steward_kind") != "cycle_unfinished" and not launches,
       "stalled 11 (control): an unfinished in-game visit stays a hand (the game it left needs a look)",
       row_of(rows).get("decision"))
    name = AUT.item_name({"mod": "A", "steward_kind": "builder_stalled", "stage": "offline_build"}, set())
    ok(name == "RIMMANDRAKE_TRIAGE_A_BUILDER_RESOLVED_NOTHING",
       "stalled 8: its item is named for what it does (the first live one was filed as ..._HAND_STEP)", name)
    src = inspect.getsource(AUT._execute_one)
    ok('"builder_stalled"' in src, "stalled 7: what the stalled-builder steward files is a road back, so fixers run it")


SECTIONS = (("stalled", stalled_main), ("stop", stop_main), ("retry", retry_main), ("refund", refund_main), ("briefs", briefs_main),
            ("acts", acts_main), ("chores", chores_main))

if __name__ == "__main__":
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    for name, fn in SECTIONS:
        if only in (None, name):
            guard(fn, "%s: the section ran to its end" % name)
    print("%d FAIL" % len(FAILS) if FAILS else "all PASS")
    sys.exit(1 if FAILS else 0)
