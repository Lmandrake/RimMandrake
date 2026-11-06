#!/usr/bin/env python3
"""PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED: a built item owing a live criterion with no `live-proof` line is enrolled as
a proof-lines job (relentless_prooflines). A1 the eligible sibling admits it and refuses one fully lined; A2 its lease
issues no `rimflow start` and its checked PASS no `close`/`implemented` (the ledger stays built); A3 rules
`proof_lines_per_tick` bounds how many enrol in one tick. Runs on selftest_relentless's FakeWorld: no ledger, no units.
Each clause carries a control that shows the instrument can see (a proposed item DOES get a start; cap 0 enrols none)."""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_live_round as LR  # noqa: E402
import relentless_prooflines as P  # noqa: E402
import selftest_relentless as T  # noqa: E402

FAILS = []


def ok(cond, what):
    print("  %s %s" % ("ok  " if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def row(state="built", sha="abc", outstanding=("A1", "A2"), levels=None):
    levels = levels or {"A1": "L2", "A2": "L1", "A3": "L0"}
    return {"id": "X", "state": state, "built_sha": sha, "outstanding": list(outstanding),
            "criteria": [{"id": k, "level": v} for k, v in levels.items()]}


def item(**kw):
    return types.SimpleNamespace(**dict({"owner": "BENCH", "state": "built", "needs": "offline"}, **kw))


def t_a1_eligible():
    r = {"pool_seats": ["BENCH"], "proof_lines_per_tick": 1}
    one = "live-proof A1: python3 x.py\n"
    both = one + "- `live-proof A2: python3 y.py`\n"
    ok(P.owed_lines(row(), "", LR.proof_lines) == ["A1", "A2"], "A1: no file -> both live criteria owed")
    ok(P.owed_lines(row(), one, LR.proof_lines) == ["A2"], "A1: a file missing one line owes that line")
    ok(P.owed_lines(row(), both, LR.proof_lines) == [], "A1: every line present owes nothing")
    ok(P.lined(both) == P.lined(both, LR.proof_lines), "A1: the module's own reader agrees with the live round's")
    ok(P.owed_lines(row(outstanding=("A3",)), "", LR.proof_lines) == [], "A1: an L0 criterion owes no live line")
    ok(P.owed_lines(row(state="proposed"), "", LR.proof_lines) == [], "A1: a proposed item is no lines job")
    ok(P.owed_lines(row(sha=None), "", LR.proof_lines) == [], "A1: no built_sha, no lines job")
    owed = P.owed_lines(row(), one, LR.proof_lines)
    ok(P.eligible(item(), owed, r), "A1: eligible admits a built item owing a line")
    ok(P.eligible(item(state="validated"), owed, r), "A1: and a validated one")
    ok(not P.eligible(item(), P.owed_lines(row(), both, LR.proof_lines), r), "A1: refuses one whose lines are all present")
    ok(not P.eligible(item(owner="CONDUCTOR"), owed, r), "A1: refuses an item outside the pool seats")
    ok(not P.eligible(item(needs="owner"), owed, r), "A1: refuses an owner item")
    ok(not P.eligible(item(), owed, r, blocked=True), "A1: refuses a blocked item")
    ok(not P.eligible(item(), owed, r, leased=True), "A1: refuses a leased item")
    ok(not P.eligible(item(), owed, dict(r, proof_lines_per_tick=0)), "A1: cap 0 is the off switch")
    got = P.stranded([dict(row(), id="S1"), dict(row(), id="S2")], {"S1": both, "S2": one}.get, LR.proof_lines)
    ok(got == [("S2", ["A2"])], "A1: stranded() lists only the item still owing a line")
    ok(not R.eligible(types.SimpleNamespace(owner="BENCH", state="built", blocked=False, needs="offline", kind="task",
                                             id="Z", lease=None), dict(R.rules(), pool_needs=["offline"])),
       "A1 control: the build pool's eligible() still refuses a built item (the gap this closes)")


def rig(n_built, **rules):
    x = T.Rig(n=0, **dict({"share": 1.0, "max_workers": 2}, **rules))
    for k in range(n_built):
        x.w.items["B%d" % k] = "built"
    starts, impl = [], []
    real_start = x.w.ledger_start

    def ledger_start(i):
        starts.append(i)
        return real_start(i)
    x.w.ledger_start = ledger_start
    x.w.game_implement = lambda *a, **k: impl.append(a) or None
    x.w.proof_lines_order = lambda r: [(i, ["A1"]) for i in sorted(x.w.items) if x.w.items[i] == "built"]
    return x, starts, impl


def t_a2_no_start_no_close():
    x, starts, impl = rig(1, proof_lines_per_tick=1)
    x.w.items["I0"] = "proposed"        # control: a build item beside it DOES get a start
    x.run_one("B0")
    st = x.st("B0")
    ok(P.is_job(st) and st[P.FLAG]["owed"] == ["A1"], "A2: the built item enrolled as a proof-lines job")
    ok("B0" not in starts and x.w.items["B0"] == "built", "A2: its lease issued no `rimflow start`; the ledger stays built")
    ok(not st["ledger_started"], "A2: the store does not believe the ledger was started")
    x.run_one("I0")
    ok("I0" in starts, "A2 control: the proposed item's lease did call ledger_start (the counter sees)")
    prompt = [l for l in x.w.launches if l[0] == "B0"][-1][2]
    ok("PROOF-LINES JOB" in prompt and "A1" in prompt, "A2: the worker's brief says lines only and names the owed one")
    try:
        R.contract(x.s, "B0", st["gen"], "python3 lint.py", game="A1", r=x.r)
        ok(False, "A2: a proof-lines contract with --game is refused")
    except ValueError:
        ok(True, "A2: a proof-lines contract with --game is refused (its game phase would call implemented)")
    for _ in range(4):      # retire() must not read built as `a seat took it` on a queued job
        x.tick()
    T.FAILS[:] = []
    T.full_pass(x, "B0")
    ok(not T.FAILS, "A2: the job ran the full finish -> check -> PASS cycle (%s)" % T.FAILS)
    for _ in range(3):
        x.tick()
    st = x.st("B0")
    ok(st["status"] == "done", "A2: the checked PASS marks the store done (%s)" % st["status"])
    ok(not [c for c in x.w.closes if c[0] == "B0"], "A2: the checked PASS issued no `close`")
    ok(not impl and x.w.items["B0"] == "built", "A2: no `implemented`; the ledger still says built")
    ok("B0" not in starts, "A2: and no `start` across the whole life")
    x.done()


def t_a2_retire_when_ledger_moves():
    x, starts, impl = rig(1, proof_lines_per_tick=1, max_workers=0)
    x.tick()
    ok(P.is_job(x.st("B0")) and x.st("B0")["status"] == "queued", "A2: queued job waits while the ledger stays built")
    x.w.items["B0"] = "doing"           # a seat took it up again: no lines job left to do
    x.w.proof_lines_order = lambda r: []
    x.tick()
    ok(x.st("B0")["status"] == "retired", "A2: a queued job retires once the ledger leaves built")
    x.done()


def t_a3_cap():
    x, _, _ = rig(5, proof_lines_per_tick=2, max_workers=0, proof_lines_max_queued=9)
    x.tick()
    jobs = [i for i in x.s.items() if P.is_job(x.st(i))]
    ok(len(jobs) == 2, "A3: proof_lines_per_tick 2 enrols 2 of 5 in one tick (%d)" % len(jobs))
    x.tick()
    jobs = [i for i in x.s.items() if P.is_job(x.st(i))]
    ok(len(jobs) == 4, "A3: the next tick 2 more (%d)" % len(jobs))
    x.done()
    x, _, _ = rig(5, proof_lines_per_tick=0, max_workers=0)
    x.tick()
    ok(not x.s.items(), "A3: proof_lines_per_tick 0 enrols none")
    x.done()
    x, _, _ = rig(5, proof_lines_per_tick=9, max_workers=0, proof_lines_max_queued=3)
    x.tick()
    ok(len(x.s.items()) == 3, "A3: the lane's own cap proof_lines_max_queued bounds it (%d)" % len(x.s.items()))
    x.tick()
    ok(len(x.s.items()) == 3, "A3: and holds on the next tick while 3 jobs still wait (%d)" % len(x.s.items()))
    x.done()
    shipped = R.rules().get("proof_lines_per_tick")
    ok(isinstance(shipped, int) and 0 < shipped <= R.rules()["enrol_per_tick"],
       "A3: the shipped rules set a positive proof_lines_per_tick no larger than enrol_per_tick (%r)" % shipped)


def t_starved_by_build_line():
    """LIVE_PROOF_LINES_FILL_FOR_BUILT: measured 2026-11-06, 25 build items in turn against max_queued 8 gave the lines
    lane room -17, so no built item owing a line was ever enrolled. A full build line must not starve the lines lane."""
    x, _, _ = rig(2, proof_lines_per_tick=1, max_workers=0, max_queued=2, enrol_per_tick=0)
    for k in range(5):      # a build line over its own cap: five queued, in-turn build items
        st = R.new_state("Q%d" % k, x.now, "build")
        x.s.save(st)
    inline = sum(1 for s in x.s.states() if R.in_line(s))
    ok(inline >= 5, "starve control: the build line holds %d in-turn items against max_queued 2" % inline)
    P.enrol(x.s, x.w, x.r, x.now, R.new_state, R.iso, {s["item"] for s in x.s.states()}, P.queued_jobs(x.s.states()))
    jobs = [i for i in x.s.items() if P.is_job(x.st(i))]
    ok(len(jobs) == 1, "starve: a built item owing a line enrols as a lines job past a full build line (%d)" % len(jobs))
    old = P.enrol(x.s, x.w, x.r, x.now, R.new_state, R.iso, set(), 5 + 1)    # the shape before: the build line's count
    ok(old == [], "starve control: fed the build line's count (the old call) the lane enrols nothing")
    x.done()
    # the call site: the supervisor's own R.enrol must hand the lines lane its own count, never the build line's
    x, _, _ = rig(6, proof_lines_per_tick=1, max_workers=0, max_queued=2, enrol_per_tick=0, proof_lines_max_queued=3)
    for k in range(5):
        x.s.save(R.new_state("Q%d" % k, x.now, "build"))
    ok(sum(1 for s in x.s.states() if R.in_line(s)) >= 5, "starve control: R.enrol rig holds 5 in-turn build items")
    counts = []
    for t in range(5):
        R.enrol(x.s, x.w, x.r, x.now + t)
        counts.append(len([i for i in x.s.items() if P.is_job(x.st(i))]))
    ok(counts[0] == 1, "starve: R.enrol (the real call site) enrols a lines job past a full build line (%r)" % counts)
    ok(counts[:3] == [1, 2, 3], "starve: one lines job per tick through R.enrol (%r)" % counts)
    ok(counts[3:] == [3, 3], "starve: R.enrol holds the lines lane at proof_lines_max_queued 3 (%r)" % counts)
    x.done()
    shipped = R.rules()
    ok(isinstance(shipped.get("proof_lines_max_queued"), int) and shipped["proof_lines_max_queued"] > 0,
       "starve: the shipped rules give the lines lane its own positive queue cap (%r)" % shipped.get("proof_lines_max_queued"))


def main():
    for t in (t_a1_eligible, t_a2_no_start_no_close, t_a2_retire_when_ledger_moves, t_a3_cap, t_starved_by_build_line):
        print("--", t.__name__)
        t()
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
