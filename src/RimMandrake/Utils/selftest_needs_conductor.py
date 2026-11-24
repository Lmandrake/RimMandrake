#!/usr/bin/env python3
"""selftest_needs_conductor.py: the promises of design/specs/2026-11-22-needs-conductor-list/boundary.md.

    python3 src/RimMandrake/Utils/selftest_needs_conductor.py

Fixture mods and a fixture Dispatch reading, no ledger, no network. `needs()` calls the one home
(maturation_now.conductor_needs); on code from before it, it rebuilds the old list (reactions() plus every Dispatch
line), so each promise is seen RED there for the reported reason: history lines listed as needs.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_now as M  # noqa: E402

NOW = 1_800_000_000.0
H = 3600.0


def run(unit, at, stage, ok=False, outcome="ended in a model error", over=False, item="RIMMANDRAKE_FOO_OPEN",
        live=False):
    return {"unit": unit, "item": item, "model": "opus", "at": at, "end": None if live else at + 600,
            "start": M.pac_time(at, NOW), "stop": "" if live else M.pac_time(at + 600, NOW), "live": live,
            "state": "running" if live else "done", "outcome": "running now" if live else
            ("finished OK" if ok else outcome), "ok": None if live else ok,
            "wall_s": (NOW - at) if live else 600, "wall": "10 min", "tokens": "UNMEASURED", "usd": "UNMEASURED",
            "said_usd": None, "cap": 5.0, "over_cap": over, "stages": [stage] if stage else [],
            "placed": "its launch record" if stage else "no stage recorded at launch", "notes": [], "last": "x"}


def mod(name, column, runs, held=False, ivs=(), jq=(), disagree=(), iv_bad=()):
    m = {"name": name, "label": name + " Label", "column": column, "held": held, "runs": runs, "his": [],
         "jquestions": list(jq), "disagree": list(disagree), "iv_bad": list(iv_bad), "unread": []}
    m["boxes"] = M.stage_boxes(m, runs, list(ivs), column)
    return m


def reading(needs=(), voids=(), klass=None, hand=None):
    return {"at": NOW - 60, "at_pac": "now", "needs_conductor": list(needs), "voids": list(voids),
            "mods": {k: {"klass": v} for k, v in (klass or {}).items()}, "hand_acts": hand}


def needs(mods, rd=None, owed=(), closed=None):
    """-> (the Needs Conductor lines, records {mod: [line]}, page defects [line])."""
    if hasattr(M, "conductor_needs"):
        r = M.conductor_needs(mods, rd, NOW, owed=owed, closed=closed)
        return r["conductor"], r["records"], r["defects"]
    co = M.reactions(mods, NOW)["conductor"]
    co += ["Dispatch step, now: %s" % x for x in ((rd or {}).get("needs_conductor") or []) + ((rd or {}).get("voids") or [])]
    return co + list(owed), {}, []


def joined(L):
    return " | ".join(L)


def t_ended_run_superseded_is_history():
    runs = [run("u-old6", NOW - 50 * H, "6"),                       # a later run on Stage 6 came after it
            run("u-new6", NOW - 10 * H, "6", ok=True),
            run("u-s3", NOW - 90 * H, "3", outcome="killed at its time limit"),   # the mod moved past Stage 3
            run("u-nostage", NOW - 80 * H, None, outcome="ended: killed: unknown (- -)")]  # a later run on the mod
    closed_m = mod("ClosedMod", "6", [run("u-closed", NOW - 5 * H, "6", item="RIMMANDRAKE_FOO_DONE")])
    void_m = mod("VoidMod", "6", [run("u-void", NOW - 5 * H, "6")])
    rd = reading(voids=["VoidMod: VOID system u-void (pilot): it timed out"])
    co, rec, _ = needs([mod("FooMod", "6", runs), closed_m, void_m], rd, closed={"RIMMANDRAKE_FOO_DONE"})
    for u, when in (("u-old6", runs[0]["start"]), ("u-s3", runs[2]["start"]), ("u-nostage", runs[3]["start"]),
                    ("closed", closed_m["runs"][0]["start"]), ("void", void_m["runs"][0]["start"])):
        assert when not in joined(co), "history run %s (%s) is listed as a need: %s" % (u, when, joined(co))
    assert "no stage recorded" not in joined(co), co
    # still reachable: the run with no stage is on its mod's card, and the void on its records row
    if hasattr(M, "conductor_needs"):
        foo = mod("FooMod", "6", runs)
        foo["records"] = rec.get("FooMod", [])
        assert runs[3]["start"] in " ".join(M.history_rows(foo)), "the run on no stage is not on the card"
        void_m["records"] = rec.get("VoidMod", [])
        assert "VOID system u-void" in " ".join(M.history_rows(void_m)), "the void is not on the card"


def t_open_need_stays():
    runs = [run("u-a", NOW - 30 * H, "6", ok=True), run("u-b", NOW - 2 * H, "6", outcome="killed at its time limit"),
            run("u-live", NOW - 3 * H, "6", live=True)]
    jq = [{"n": 1, "who": "conductor", "text": "Which weight for g4", "answered": False}]
    m = mod("FooMod", "6", runs, jq=jq, disagree=["VERSION.json counts 43 bars; the test table has 44"])
    rd = reading(needs=["FooMod: the in-game launch failed (exit 2); the step will not retry it on its own"],
                 klass={"FooMod": "wait"})
    co, _, _ = needs([m], rd, owed=["a run ended success and left RIMMANDRAKE_FOO_OPEN open"], closed=set())
    s = joined(co)
    assert runs[1]["start"] in s and "killed at its time limit" in s, "the open ended run is gone: " + s
    for want in ("Which weight for g4", "has been live", "files disagree", "the in-game launch failed",
                 "left RIMMANDRAKE_FOO_OPEN open"):
        assert want in s, "%r is not a need: %s" % (want, s)


def t_spend_and_void_lines_are_records():
    runs = [run("u-ok", NOW - 40 * H, "6", ok=True, over=True), run("u-ok2", NOW - 20 * H, "6", ok=True, over=True)]
    rd = reading(voids=["FooMod: VOID hand u-x (steward): launched without his authorization",
                        "FooMod: void spend ≈883k weighted tokens (true spend, shown apart); system faults 0"])
    co, rec, _ = needs([mod("FooMod", "6", runs)], rd)
    s = joined(co)
    assert "spend cap" not in s and "VOID" not in s and "void spend" not in s, "a record is listed as a need: " + s
    assert any("VOID hand u-x" in x for x in rec.get("FooMod", [])), rec
    assert "over its spend cap" in M.run_line(runs[0], 1), M.run_line(runs[0], 1)


def t_held_mod_lines_wait():
    ivs = M.parse_interventions("- CONDUCTOR INTERVENED (stage 6, 2026-11-14 12:15 PST, kind hold): planted hold", "j")[0]
    runs = [run("u-%d" % k, NOW - (50 - k) * H, "6") for k in range(4)]
    held_m = mod("HeldMod", "6", runs, ivs=ivs)
    off_m = mod("OffMod", "3", [run("u-off", NOW - 4 * H, "3")])
    jh = mod("JournalHeld", "3", [run("u-jh", NOW - 4 * H, "3")], held=True)
    rd = reading(needs=["HeldMod Stage 6 (In game) DIVERGING, open rising: open 1 -> 2. Conductor decides",
                        "OffMod Stage 3 (Offline build) DIVERGING, open rising: open 6 -> 7. Conductor decides"],
                 klass={"HeldMod": "held", "OffMod": "held"})
    co, rec, _ = needs([held_m, off_m, jh], rd)
    s = joined(co)
    for bad in ("DIVERGING", "is HELD", "has run 4 times", "HeldMod", "OffMod", "JournalHeld"):
        assert bad not in s, "a held mod's line %r is a need: %s" % (bad, s)
    assert any("DIVERGING" in x for x in rec.get("HeldMod", [])), rec


def t_hand_acts_one_line():
    lines = ["hand act run-u%d (hand_run on FooMod: an in-game driver launched by hand) has had no follow-up item "
             "for 30 h: build ..." % k for k in range(5)]
    rd = reading(needs=lines, hand={"recorded": 96, "open": 11, "overdue": 9, "oldest_h": 42.0, "ids": []})
    co, _, _ = needs([], rd)
    hand = [x for x in co if "hand act" in x]
    assert len(hand) == 1, "hand acts are %d lines: %s" % (len(hand), hand)
    assert "9" in hand[0] and "maturation_hands.py list" in hand[0], hand[0]
    co2, _, _ = needs([], reading(hand={"recorded": 96, "open": 2, "overdue": 0, "oldest_h": 3.0, "ids": []}))
    assert not [x for x in co2 if "hand act" in x], co2


def t_unreadable_intervention_is_a_page_defect():
    text = ("DECIDED (option c): my note quotes the phrase CONDUCTOR INTERVENED in a sentence.\n"
            "- CONDUCTOR INTERVENED (stage three, yesterday): a malformed line\n")
    good, bad = M.parse_interventions(text, "ledger note on X")
    assert not good and len(bad) == 1 and "stage three" in bad[0]["line"], (good, bad)
    co, _, defects = needs([mod("FooMod", "3", [], iv_bad=bad)], reading())
    assert "cannot read" not in joined(co) and "stage three" not in joined(co), co
    assert any("stage three" in x for x in defects), defects


def t_repeats_collapse():
    text = "\n".join("- CONDUCTOR INTERVENED (stage %s, 2026-11-14 12:15 PST, kind hold): one planted reason" % c
                      for c in ("3", "4+5", "6"))
    ivs = M.parse_interventions(text, "j")[0]
    m = mod("FooMod", "3", [], ivs=ivs)
    co, _, _ = needs([m], reading(needs=["stale_clone: nothing launched"] * 2, klass={"FooMod": "wait"}))
    held = [x for x in co if "HELD" in x]
    assert len(held) == 1 and "one planted reason" in held[0], "one hold on three stages is %d lines: %s" % (
        len(held), held)
    assert len([x for x in co if "stale_clone" in x]) == 1 and "×2" in joined(co), co


def t_answered_journal_question_is_not_a_need():
    """The journal's own answer (three forms) hides the question; see selftest_journal_answered.py (11 checks)."""
    import selftest_journal_answered as J
    assert J.main() == 0, "selftest_journal_answered failed: %s" % J.BAD


def main():
    tests = [t_answered_journal_question_is_not_a_need, t_ended_run_superseded_is_history, t_open_need_stays, t_spend_and_void_lines_are_records,
             t_held_mod_lines_wait, t_hand_acts_one_line, t_unreadable_intervention_is_a_page_defect, t_repeats_collapse]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception as e:  # noqa: BLE001
            failed += 1
            print("FAIL", t.__name__, "%s: %s" % (type(e).__name__, str(e)[:400]))
    print("FAILED %d of %d" % (failed, len(tests)) if failed else "ALL PASS (%d)" % len(tests))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
