#!/usr/bin/env python3
"""Selftest: a live or checker failure is EXPLAINED, not labelled (LIVE_FAILURES_EXPLAIN_MORE_THAN_A_LABEL).

Owner, 2026-11-04: "it needs to write a coherent explanation of failures, not just indicate them. Then there needs to be
follow-up work to address them." Pins, on the supervisor's own transitions (FakeWorld from selftest_relentless):
  * a DIAGNOSE ending (game_fail) leaves the next worker briefed to EXPLAIN it, with every field named;
  * a CLASSIFY label no longer pays that debt, and `finish` is refused until an explanation is recorded;
  * an explanation missing expected/observed/mechanism, a step without its evidence, a theory without its reason, a
    pasted <placeholder>, or no ruled-out theory is refused; so is a SITE/HARNESS cause named as the item itself, a
    cause never filed, and a CLOSED cause (never reopened: the refusal names the file-new-with --caused-by road);
  * a good one is kept on the item (explanations.jsonl whole, learned.md rendered, an attempt line), noted on the
    item and on its follow-up item, read back in the next brief's ending history, and it pays the debt;
  * a second item explained by the same cause joins it (one cause, two items on the book, the cause noted once per
    item); the cause book reaches the next diagnosing brief, and a closed cause drops off it;
  * the diagnostician's `attribute` carries the same explanation: refused without it, kept on the item with it, and
    the builder's brief line quotes its mechanism.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                       # noqa: E402
import relentless_attrib as A                # noqa: E402
import relentless_explain as E               # noqa: E402
import selftest_relentless as SR             # noqa: E402
import selftest_relentless_attrib as SA      # noqa: E402

FAILS = []
REPAIR = "BRIDGE_MAP_FIX_WRONG_MAP"
CLOSED = "BRIDGE_OLD_FIX_DONE_ALREADY"
STATES = {REPAIR: "doing", CLOSED: "done"}


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def state_of(i):
    return STATES.get(i, "doing" if i.startswith("I") else None)


def refused(fn):
    try:
        fn()
    except ValueError as e:
        return str(e)
    return None


def live_failed(x, i):
    """A worker runs, then its build reads FAIL on the running game; the next worker is leased."""
    x.run_one(i)
    st = x.st(i)
    if not st.get("contract"):
        R.contract(x.s, i, st["gen"], "python3 selftest_x.py")
    with x.s.lock():
        cur = x.s.load(i)
        R.fail(x.s, cur, "game_fail", "A2 FAIL on the running game (/l/%s.log)" % i, x.r, x.now)
    x.w.up[x.st(i)["run"]["unit"]] = False
    x.tick()
    x.run_one(i)
    return x.st(i)


def good(**kw):
    return dict(E.sample(), **dict({"cause": REPAIR}, **kw))


def t_worker_explains():
    x = SR.Rig(n=2, share=1.0, max_workers=2, same_failure_limit=50, unchanged_returns_limit=500, snag_again_wait_h=0)
    x.tick()
    st = live_failed(x, "I0")
    ok(bool(st.get("diagnose_owed")), "a game_fail leaves the next worker owing an explanation")
    brief = [z for z in x.w.launches if z[0] == "I0"][-1][2]
    ok(all(f in brief for f in ("explain --item I0", "--expected", "--observed", "--mechanism", "--step", "--ruled-out",
                                "--cause")), "the brief asks for the explanation with every field")
    ok("EXPLAIN it, not to rerun it" in brief, "the brief says the job is to explain, not to rerun")
    g = st["gen"]
    R.learn(x.s, "I0", g, "CLASSIFY: SITE - prepare_site read back a roof in the rect: roofed=12")
    ok(x.st("I0").get("diagnose_owed"), "a CLASSIFY label does not pay the debt")
    why = refused(lambda: R.finish(x.s, "I0", g, "c" * 40, "e"))
    ok(why and "explain --item I0" in why and "not an explanation" in why, "finish is refused until it is explained: %s" % why)

    cases = [
        ("no mechanism", dict(good(), mechanism="")),
        ("a one-word observed", dict(good(), observed="broke")),
        ("a step without its evidence", dict(good(), step=["the pump never ticked"])),
        ("a step with an empty side", dict(good(), step=["the pump never ticked :: "])),
        ("a theory without its reason", dict(good(), ruled_out=["the bridge read the wrong map"])),
        ("no ruled-out theory", dict(good(), ruled_out=[])),
        ("the template pasted back", dict(good(), mechanism="<how the one led to the other>")),
        ("a cause that is no id", dict(good(), cause="fix it")),
        ("a cause never filed", dict(good(), cause="NOBODY_FILED_THIS_ONE")),
    ]
    for what, a in cases:
        ok(refused(lambda: R.explain(x.s, "I0", g, "SITE", a, now=x.now, state_of=state_of)) is not None,
           "explain refuses %s" % what)
    why = refused(lambda: R.explain(x.s, "I0", g, "SITE", good(cause="I0"), now=x.now, state_of=state_of))
    ok(why and "outside this item" in why, "a SITE cause is never the item itself: %s" % why)
    why = refused(lambda: R.explain(x.s, "I0", g, "SITE", good(cause=CLOSED), now=x.now, state_of=state_of))
    ok(why and "never reopened" in why and "--caused-by %s" % CLOSED in why,
       "a closed cause is refused with the file-new road: %s" % why)
    ok(E.validate(good(mechanism="GetComps<CompPump>() returned an empty List<Thing> on the Plant"), ["MOD"], "I0", "I0")
       ["mechanism"].startswith("GetComps<"), "code in angle brackets is not a pasted placeholder")
    ok(refused(lambda: R.explain(x.s, "I0", g, "PRODUCT", good(), now=x.now, state_of=state_of)),
       "a worker's class is MOD|SITE|HARNESS|CONTRACT")
    ok(x.st("I0").get("diagnose_owed"), "no refused explanation paid the debt")

    notes = []
    cause = R.explain(x.s, "I0", g, "SITE", good(), now=x.now, state_of=state_of, note=lambda i, t: notes.append((i, t)))
    st = x.st("I0")
    ok(cause == REPAIR and not st.get("diagnose_owed") and st["diagnosed"]["class"] == "SITE"
       and st["diagnosed"]["cause"] == REPAIR, "the explanation pays the debt and names its follow-up")
    ex = E.explanations(x.s, "I0")
    ok(len(ex) == 1 and all(ex[0].get(k) for k in ("expected", "observed", "mechanism", "steps", "ruled_out", "cause"))
       and ex[0]["ending"] == "game_fail" and len(ex[0]["steps"]) == 2 and ex[0]["steps"][1]["evidence"].startswith("Player.log"),
       "kept on the item whole: %s" % (ex[:1],))
    learned = x.s.learned("I0")
    ok("EXPLAINED game_fail" in learned and "mechanism: the pump comp" in learned and "ruled out: the bridge read"
       in learned and "follow-up: %s" % REPAIR in learned, "rendered into the item's learned record")
    hist = R.ending_history(x.s.attempts("I0"))
    ok(any("explained it SITE" in h and "only calls TickLong" in h and REPAIR in h for h in hist),
       "the next brief's history carries the mechanism and its follow-up: %s" % hist[-2:])
    ok([n[0] for n in notes] == ["I0", REPAIR] and "Mechanism:" in notes[1][1] and "Steps:" in notes[1][1],
       "noted on the item and on its follow-up item: %s" % [n[0] for n in notes])
    R.learn(x.s, "I0", g, "WARRANT: the site fix lands first | A2 still 0 on a sound site means the mod")
    R.finish(x.s, "I0", g, "c" * 40, "e")
    ok(x.s.read_receipt("I0", g), "finish is taken once it is explained")

    # a second item with the same cause joins it
    st1 = live_failed(x, "I1")
    leased = [z for z in x.w.launches if z[0] == "I1"][-1][2]
    ok(st1.get("diagnose_owed") and "Cause book" in leased and REPAIR in leased,
       "the brief lease() actually launched for a second diagnosing item carries the cause book and I0's cause")
    notes1 = []
    R.explain(x.s, "I1", st1["gen"], "HARNESS", good(), now=x.now, state_of=state_of, note=lambda i, t: notes1.append((i, t)))
    R.explain(x.s, "I1", st1["gen"], "HARNESS", good(), now=x.now, state_of=state_of, note=lambda i, t: notes1.append((i, t)))
    b = E.book(x.s)
    ok(list(b) == [REPAIR] and sorted(b[REPAIR]["items"]) == ["I0", "I1"], "one cause, two items on the book: %s" % b)
    ok([n[0] for n in notes1].count(REPAIR) == 1, "the cause item is noted once per item: %s" % [n[0] for n in notes1])
    rows = E.open_causes(x.s, state_of)
    ok(len(rows) == 1 and REPAIR in rows[0] and "2 items" in rows[0], "the cause book lists it once: %s" % rows)
    STATES[REPAIR] = "done"
    ok(E.open_causes(x.s, state_of) == [], "a closed cause drops off the book")
    ok(len(E.open_causes(x.s, lambda i: 1 / 0)) == 1, "an unreadable ledger keeps the cause listed, never kills the brief")
    STATES[REPAIR] = "doing"
    # the cause book reaches the next diagnosing brief (lease passes it through Effects.state_of when it has one)
    brief = R.worker_prompt(dict(x.st("I1"), diagnose_owed={"class": "game_fail"}), "item", "", x.r, x.s.attempts("I1"),
                            E.open_causes(x.s, state_of))
    ok("Cause book" in brief and REPAIR in brief, "the cause book reaches the diagnosing brief")
    x.done()


def t_attribute_explains():
    x = SA.rig([SA.STEVE, SA.BOX_FIX])
    SA.checked(x, SA.STEVE, "FAIL", "df shows 40G left on C: but the item measures D:, which this box does not mount")
    ok(x.st(SA.STEVE)["status"] == "held", "STEVE is held for attribution")
    base = {"evidence": "proof reads Player-prev.log"}
    why = refused(lambda: A.answer(x.s, SA.STEVE, None, ["PROOF"], dict(base), x.r, x.now, R))
    ok(why and "--expected" in why, "an attribution without its explanation is refused: %s" % why)
    ok(x.st(SA.STEVE)["status"] == "held", "and nothing moved")
    notes = []
    route = A.answer(x.s, SA.STEVE, None, ["PROOF"], dict(E.sample(), **base), x.r, x.now, R,
                     note=lambda i, t: notes.append((i, t)))
    st = x.st(SA.STEVE)
    ex = E.explanations(x.s, SA.STEVE)
    ok(route == "proof" and len(ex) == 1 and ex[0]["cause"] == SA.STEVE and ex[0]["by"] == "operator"
       and ex[0]["ending"] == "blind_fail", "with it, the attribution is kept on the item: %s %s" % (route, ex[:1]))
    ok(st["attribution"].get("mechanism", "").startswith("the pump comp"), "the attribution record carries the mechanism")
    ok("Mechanism: the pump comp" in A.brief_line(st["attribution"]), "the proof worker's brief quotes the mechanism")
    ok([n[0] for n in notes] == [SA.STEVE], "PROOF's follow-up is the item itself: one note, on it")
    p = A.prompt(dict(st, wait={"class": "blind_fail", "sha": "s" * 40, "detail": "d"}), "item", [], "n", x.r)
    ok("EXPLAIN the failure, not to rerun it" in p and "--ruled-out" in p and "causes" in p,
       "the diagnostician is briefed to explain and to join an open cause")
    x.done()


def t_instrument_attribution_follow_up():
    x = SA.rig([SA.STEVE, SA.BOX_FIX])
    SA.checked(x, SA.STEVE, "FAIL", "df shows 40G left on C: but the item measures D:, which this box does not mount")
    root = tempfile.mkdtemp(prefix="rl-explain-")
    with open(os.path.join(root, "speaks.py"), "w", encoding="utf-8") as f:
        f.write("import sys\nprint('FIXTURE_VERDICT: ' + ('FAIL' if sys.argv[1:] else 'PASS'))\nsys.exit(len(sys.argv) - 1)\n")
    a = dict(E.sample(), evidence="df -h on the box lists C: only", repair=SA.BOX_FIX, fixture_good="python3 speaks.py",
             fixture_bad="python3 speaks.py --bad")
    why = refused(lambda: A.answer(x.s, SA.STEVE, None, ["SITE"], a, x.r, x.now, R, known=lambda i: True, root=root,
                                   state_of=lambda i: "done" if i == SA.BOX_FIX else "doing"))
    ok(why and "never reopened" in why, "an instrument's repair that is closed is refused: %s" % why)
    route = A.answer(x.s, SA.STEVE, None, ["SITE"], a, x.r, x.now, R, known=lambda i: True, root=root,
                     state_of=lambda i: "doing")
    ok(route == "wait:" + SA.BOX_FIX and E.explanations(x.s, SA.STEVE)[0]["cause"] == SA.BOX_FIX
       and SA.STEVE in E.book(x.s)[SA.BOX_FIX]["items"], "the repair item is the explained cause's follow-up: %s" % route)
    x.done()


def main():
    for t in (t_worker_explains, t_attribute_explains, t_instrument_attribution_follow_up):
        print("--", t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_relentless_explain: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
