#!/usr/bin/env python3
"""RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS: 53 binding repairs proposed, 3 ruled by hand, 44 items blocked on a judge no
program started. Rows, through the real tick on selftest_relentless's rig; only the claude call and the ledger are fake:
  T  a seeded pending proposal reaches a ruling via the tick: fresh judge (rm-judge, opus, new session, cwd outside the
     item's clone), ruled through bind_judge, the contract moves on approve, the item returns to the line.
  B  REJECT and AMBIGUOUS return to the worker with the reason; neither moves the contract; an ambiguous one may be
     proposed again, a rejected binding may not. The CLI's own ambiguous still holds pending.
  S  a worker session cannot rule; an approve the machine refuses becomes a reject with the machine's reason.
  L  limits: at most IN_FLIGHT at once, oldest first; a judge with no RULING is retried at most TRIES times; a running item
     is left to its worker; a pause starts nobody; an owner's block is never lifted.
  A  one alarm when a proposal has waited over 2 h, said once, re-armed when the wait ends.
  K  the real Effects has the launch (a test Fx without it starts nothing, so a rename would go dark), and kick is a
     detached unit from this file with a filesystem-safe name.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R                  # noqa: E402
import relentless_bindjudge as J        # noqa: E402
import selftest_relentless as T         # noqa: E402

FAILS = []
GOOD = {"before": "calls the old script", "after": "calls the renamed one", "behaviour": "same",
        "defect": "selftest_x.py was renamed: the old proof exits 2"}
H = 3600


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def claude(says, seen=None):
    """A fake claude: `says` is the RULING's fields, or text with no ruling."""
    def run(argv, cwd=None, stdout=None, stderr=None, timeout=None, stdin=None):
        if seen is not None:
            seen.append({"argv": argv, "cwd": cwd})
        text = says if isinstance(says, str) else "I read it.\nRULING " + json.dumps(says)
        stdout.write(json.dumps({"type": "result", "result": text, "session_id": "s"}) + "\n")
        return type("P", (), {"returncode": 0})()
    return run


def rig(n=1, says=None, seen=None):
    x = T.Rig(n=n, share=1.0)
    x.r = dict(x.r, wall={})
    x.w.held = {}
    x.w.kicks = []
    plain = x.w.item_state

    def item_state(item, fresh=False):
        got = plain(item, fresh)
        if got is not None and item in x.w.held:
            got = dict(got, block_holds=True, block="reason (kind %s)" % x.w.held[item])
        return got

    def ledger_block(item, kind, ons, reason):
        x.w.held[item] = kind

    def ledger_unblock(item, reason):
        x.w.held.pop(item, None)
        x.w.__dict__.setdefault("unblocks", []).append(item)

    def kick(store, item, pid, tries):
        x.w.kicks.append(item)
        if x.w.__dict__.get("synchronous", True):
            J.work(store, item, pid, runner=claude(x.w.says, seen), env={})

    x.w.says = says
    x.w.item_state, x.w.ledger_block, x.w.ledger_unblock, x.w.bindjudge_kick = item_state, ledger_block, ledger_unblock, kick
    return x


def seed(x, i="I0", proof="python3 a/selftest_x_renamed.py"):
    """The worker's own road: a contract, a rebind, the snag that parks it on the judge."""
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], "python3 a/selftest_x.py", obligation="the gourd selects", r=x.r)
    R.rebind(x.s, i, st["gen"], {"proof": proof}, dict(GOOD), now=x.now, r=x.r)
    R.snag(x.s, i, st["gen"], "binding_repair", "the proof names a renamed file", x.r, blocker="judge")
    x.w.up[x.st(i)["run"]["unit"]] = False


def settle(x, i="I0", ticks=6):
    for _ in range(ticks):
        x.tick()
        if x.st(i)["status"] not in ("stopping", "blocked", "running"):
            return
    return


def park(x, i="I0"):
    """To blocked with the ledger block written, the judge not yet started."""
    was = x.w.bindjudge_kick
    x.w.bindjudge_kick = lambda *a: "held by the test"
    for _ in range(4):
        x.tick()
    ok(x.st(i)["status"] == "blocked" and x.w.held.get(i) == "judge", "seed: %s is blocked on kind judge" % i)
    x.w.bindjudge_kick = was
    J._write(J._book(x.s, i), {})


def t_tick_reaches_ruling():
    seen = []
    x = rig(says={"verdict": "approve", "why": "the renamed file holds the same assertions"}, seen=seen)
    seed(x)
    park(x)
    x.tick()
    st = x.st("I0")
    ok(st["contract"]["proof"] == "python3 a/selftest_x_renamed.py" and st["contract"]["binding_version"] == 2
       and not st.get("binding_proposal"), "T: the tick's judge approved and the binding moved")
    a = seen[0]["argv"]
    ok(a[a.index("--agent") + 1] == "rm-judge" and a[a.index("--model") + 1] == "opus" and "--session-id" in a,
       "T: a fresh rm-judge session on opus")
    ok("the gourd selects" in a[2] and "selftest_x_renamed" in a[2] and "RULING" in a[2], "T: the prompt carries the packet")
    clone = st.get("clone") or "/nonexistent"
    ok(not os.path.realpath(seen[0]["cwd"]).startswith(os.path.realpath(clone)), "T: the judge stands outside the item's clone")
    ok(os.path.exists(os.path.join(seen[0]["cwd"], ".claude", "agents", "rm-judge.md")),
       "T: the judge's cwd holds its agent (real claude from an empty dir: --agent 'rm-judge' not found, and a fake never sees it)")
    rec = [e for e in x.s.attempts("I0") if e.get("end") == "rebind_approve"]
    ok(rec and rec[-1]["judge"].startswith("rm-judge-"), "T: the attempt record names the judge")
    x.tick()
    ok(x.w.__dict__.get("unblocks") == ["I0"] or "I0" not in x.w.held, "T: the judge's block is lifted")
    settle(x)
    ok(x.st("I0")["status"] in ("queued", "running") and not x.st("I0").get("binding_ruled"), "T: the item is back in line: %s" % x.st("I0")["status"])
    x.done()


def t_back_to_worker():
    for verdict, end in (("reject", "rebind_reject"), ("ambiguous", "rebind_ambiguous_returned")):
        reason = "THE-REASON-%s the old proof still runs" % verdict
        x = rig(says={"verdict": verdict, "why": reason})
        seed(x)
        park(x)
        x.tick()
        st = x.st("I0")
        ok(not st.get("binding_proposal") and st["contract"]["proof"] == "python3 a/selftest_x.py",
           "B: %s leaves the contract alone and clears the wait" % verdict)
        ok([e for e in x.s.attempts("I0") if e.get("end") == end], "B: %s is recorded as %s" % (verdict, end))
        settle(x)
        st = x.st("I0")
        ok(st["status"] in ("queued", "running"), "B: %s returns the item to a worker: %s" % (verdict, st["status"]))
        ok(reason in x.s.learned("I0"), "B: %s's reason reaches the worker's notes" % verdict)
        ok(bool(st.get("bindings_rejected")) == (verdict == "reject"), "B: only a reject bars the binding")
        x.done()
    x = rig()
    seed(x)
    R.bind_judge(x.s, "I0", "conductor", "ambiguous", "cannot tell", env={}, r=x.r, cwd="/")
    ok(x.st("I0").get("binding_proposal") and not x.st("I0").get("binding_ruled"), "B: the CLI's ambiguous still holds pending")
    x.done()


def t_seats():
    x = rig()
    seed(x)
    park(x)
    p = J.pid_of(x.st("I0")["binding_proposal"])
    code = J.work(x.s, "I0", p, runner=claude({"verdict": "approve", "why": "mine"}), env={"RELENTLESS_GEN": "1"})
    ok(code == 1 and x.st("I0").get("binding_proposal"), "S: a worker's session cannot rule through the launch")
    with x.s.lock():
        st = x.s.load("I0")
        st["binding_proposal"]["from_binding_hash"] = "moved"
        x.s.save(st)
    code = J.work(x.s, "I0", J.pid_of(x.st("I0")["binding_proposal"]),
                  runner=claude({"verdict": "approve", "why": "fine"}), env={})
    st = x.st("I0")
    rec = [e for e in x.s.attempts("I0") if e.get("end") == "rebind_reject"]
    ok(code == 0 and not st.get("binding_proposal") and rec and "the machine refused" in rec[-1]["why"]
       and st["contract"]["proof"] == "python3 a/selftest_x.py", "S: an approve the machine refuses is a reject with its reason")
    x.done()


def t_limits():
    x = rig(n=J.IN_FLIGHT + 2, says="I could not decide and wrote no line")
    x.w.synchronous = False
    ids = ["I%d" % i for i in range(J.IN_FLIGHT + 2)]
    for n, i in enumerate(ids):
        seed(x, i)
        x.now += 1
        x.tick()
    for i in ids:
        for _ in range(4):
            if x.st(i)["status"] == "blocked":
                break
            x.tick()
    for i in ids:
        J._write(J._book(x.s, i), {})
    x.w.kicks = []
    x.tick()
    first = list(x.w.kicks)
    ok(len(first) == J.IN_FLIGHT, "L: %d judges at once, not %d" % (J.IN_FLIGHT, len(first)))
    oldest = sorted(ids, key=lambda i: (x.st(i)["binding_proposal"]["at"], i))[:J.IN_FLIGHT]
    ok(first == oldest, "L: oldest first")
    x.tick()
    ok(len(x.w.kicks) == J.IN_FLIGHT, "L: a judge in flight is not doubled and none past the cap")
    x.done()

    x = rig(says="no ruling line here")
    seed(x)
    park(x)
    x.w.kicks = []
    for _ in range(J.TRIES + 3):
        x.tick()
    ok(len(x.w.kicks) == J.TRIES and x.st("I0").get("binding_proposal"), "L: no RULING is tried %d times, then left to the alarm: %d" % (J.TRIES, len(x.w.kicks)))
    x.done()

    x = rig(says={"verdict": "approve", "why": "x"})
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "python3 a/selftest_x.py", obligation="the gourd selects", r=x.r)
    R.rebind(x.s, "I0", st["gen"], {"proof": "python3 a/selftest_x_renamed.py"}, dict(GOOD), now=x.now, r=x.r)
    x.tick()
    ok(not x.w.kicks and x.st("I0").get("binding_proposal"), "L: a running worker's proposal waits for its snag")
    x.done()

    x = rig(says={"verdict": "approve", "why": "x"})
    seed(x)
    park(x)
    x.w.kicks = []
    x.w.paused = lambda: True
    x.tick()
    ok(not x.w.kicks, "L: a pause starts no judge")
    x.done()

    x = rig(says={"verdict": "reject", "why": "no"})
    seed(x)
    park(x)
    x.w.held["I0"] = "owner"
    x.tick()
    x.tick()
    ok(x.w.held.get("I0") == "owner" and x.st("I0")["status"] == "blocked", "L: a ruled repair never lifts his block")
    x.done()


def t_alarm():
    x = rig()
    x.w.synchronous = False
    seed(x)
    park(x)
    late = "binding repair"
    ok(not [j for j in x.w.jams if late in j], "A: quiet under 2 h")
    x.now += 2 * H + 1
    x.tick()
    x.tick()
    said = [j for j in x.w.jams if late in j]
    ok(len(said) == 1 and "I0" in said[0], "A: past 2 h the Conductor hears it, once: %d" % len(said))
    R.bind_judge(x.s, "I0", "conductor", "reject", "no", env={}, r=x.r, cwd="/")
    x.tick()
    ok(not os.path.exists(os.path.join(J._dir(x.s), "alarm.json")), "A: an ended wait re-arms the alarm")
    x.done()


def t_kick():
    x = rig()
    calls = []

    def runner(argv, **kw):
        calls.append(argv)
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
    why = J.kick(x.s, "I0", "abc", 1, runner=runner)
    a = calls[0]
    ok(why is None and a[0] == "systemd-run" and "--wait" not in a and a[-4:] == [os.path.abspath(J.__file__), "work", "I0", "abc"],
       "K: a detached unit runs this file's work verb")
    ok(J.unit_name("I0", "abc", 1) != J.unit_name("I0", "abc", 2), "K: a retry is a new unit name")
    ok(callable(getattr(R.Effects, "bindjudge_kick", None)), "K: the real Effects can launch")
    x.done()


def main():
    for t in (t_tick_reaches_ruling, t_back_to_worker, t_seats, t_limits, t_alarm, t_kick):
        t()
    print("selftest_relentless_bindjudge: %s" % ("FAIL %d" % len(FAILS) if FAILS else "ok"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
