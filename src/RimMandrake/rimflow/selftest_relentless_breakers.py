#!/usr/bin/env python3
"""Selftest: loop breakers redirect work instead of demanding novelty (CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT;
design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md rank 3).

    python3 src/RimMandrake/rimflow/selftest_relentless_breakers.py

Pins, on the supervisor's transitions (FakeWorld from selftest_relentless), not only the helpers:
  * RETRY WARRANT: a worker sent after a failed attempt is briefed to state one and `finish` is refused until it has;
    a first attempt and a wait on time owe none; the warrant is kept whole on the attempt record;
  * SAME SIGNATURE: one failure signature on three builds (two product changes) holds the item, kind `signature`; two
    builds do not; ids and numbers do not split a signature, different words do; an unhold restarts the count;
  * ONE INCIDENT: one capability signature on three items opens ONE incident, told once; its probe is relaunched and
    the others are not; an unaffected item still runs; the probe's candidate releases it and the others come back;
    `incident-release` needs evidence;
  * HISTORY: a classification and a warrant reach the next builder and the fresh pair of eyes whole (no cut at 140);
    the blind checker's prompt carries none of it; and a CLASSIFY line `learn` takes is recorded whole (no cut at 300).
The known-unmet-predecessor wait is relentless_block's, pinned by selftest_relentless_block.py.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R                       # noqa: E402
import relentless_breakers as B              # noqa: E402
import selftest_relentless as SR             # noqa: E402

FAILS = []
LOOSE = dict(same_failure_limit=50, unchanged_returns_limit=500, snag_again_wait_h=0)   # only the breakers decide


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def rig(n=1, **rules):
    x = SR.Rig(n=n, share=1.0, max_workers=max(1, n), **dict(LOOSE, **rules))
    x.tick()
    return x


def stop(x, i):
    st = x.st(i)
    x.w.up[st["run"]["unit"]] = False
    x.tick()


def contract(x, i):
    st = x.st(i)
    if not st.get("contract"):
        R.contract(x.s, i, st["gen"], "python3 selftest_x.py")


def build_and_fail(x, i, sha, klass, detail):
    """One build: a worker runs, finishes `sha`, and the result comes back `klass` (as a checker's end would)."""
    x.run_one(i)
    contract(x, i)
    st = x.st(i)
    if st.get("warrant_owed"):
        R.learn(x.s, i, st["gen"], "WARRANT: %s changed the comp | the same reading again means the binding" % sha)
    R.finish(x.s, i, st["gen"], sha, "evidence")
    with x.s.lock():
        cur = x.s.load(i)
        # a validation ending reaches the builder only attributed PRODUCT (relentless_attrib): as a Marker's defect is
        R.fail(x.s, cur, klass, detail, x.r, x.now, attributed={"targets": ["PRODUCT"], "evidence": detail, "at": x.now})
    stop(x, i)


def last_prompt(x, i):
    return [lz[2] for lz in x.w.launches if lz[0] == i][-1]


# ---------------------------------------------------------------- the retry warrant

def t_warrant():
    x = rig()
    x.run_one("I0")
    contract(x, "I0")
    ok(not x.st("I0").get("warrant_owed") and "RETRY WARRANT" not in last_prompt(x, "I0"),
       "a first attempt owes no warrant and is not told to write one")
    R.snag(x.s, "I0", x.st("I0")["gen"], "wait_for_sample", "the sample is filling", x.r, now=x.now, wait_hours=0.01)
    stop(x, "I0")
    x.run_one("I0")
    ok(not x.st("I0").get("warrant_owed"), "a wait on time is no failed approach: no warrant owed")
    R.snag(x.s, "I0", x.st("I0")["gen"], "tool_broke", "the def loader threw on RM_Thing", x.r, now=x.now)
    stop(x, "I0")
    x.run_one("I0")
    st = x.st("I0")
    ok(st.get("warrant_owed", {}).get("after") == "tool_broke", "a retry after a failure owes its warrant")
    ok("RETRY WARRANT" in last_prompt(x, "I0"), "and its brief says so")
    try:
        R.finish(x.s, "I0", st["gen"], "a" * 40, "evidence")
        ok(False, "finish without a warrant is refused")
    except ValueError as e:
        ok("owes its warrant" in str(e), "finish without a warrant is refused: %s" % str(e)[:80])
    R.learn(x.s, "I0", st["gen"], "WARRANT nothing")
    ok(x.st("I0").get("warrant_owed"), "a line that is not a warrant pays nothing")
    long = "the loader now skips abstract defs " + "x" * 400
    R.learn(x.s, "I0", st["gen"], "WARRANT: %s | RM_Thing still throwing means the def, not the loader" % long)
    ok(not x.st("I0").get("warrant_owed"), "a warrant pays the debt")
    rec = [a for a in x.s.attempts("I0") if a.get("warrant")]
    ok(rec and rec[-1]["warrant"]["changed"] == long and rec[-1]["warrant"]["after"] == "tool_broke",
       "the warrant is on the attempt record whole")
    R.finish(x.s, "I0", st["gen"], "a" * 40, "evidence")
    ok(x.st("I0")["status"] == "candidate", "with its warrant, the retry finishes")
    x.done()


# ---------------------------------------------------------------- same signature, new code

def t_signature():
    ok(B.signature("blind_fail", "A2 reads 0 at tick 1234 on 0123456789ab")
       == B.signature("blind_fail", "A2 reads 3 at tick 98 on fedcba987654"), "ids and numbers do not split a signature")
    ok(B.signature("blind_fail", "A2 reads 0") != B.signature("blind_fail", "A3 never spawned"),
       "different words are different signatures")
    ok(B.signature("game_fail", "A2 FAIL on the running game (/l/a.log)")
       == B.signature("game_fail", "A2 FAIL on the running game (/l/zz.log)"), "a live FAIL is keyed by its clauses")
    x = rig()
    build_and_fail(x, "I0", "1" * 40, "blind_fail", "A2 reads 0 at tick 1200")
    build_and_fail(x, "I0", "2" * 40, "blind_fail", "A2 reads 0 at tick 1300")
    ok(x.st("I0")["status"] != "held", "the same signature on two builds: not yet held")
    build_and_fail(x, "I0", "3" * 40, "blind_fail", "A2 reads 0 at tick 1400")
    st = x.st("I0")
    ok(st["status"] == "held" and (st.get("hold") or {}).get("kind") == "signature",
       "on three builds (two product changes): held, kind signature: %s" % st["status"])
    ok("compare the product, the proof and the binding" in st["hold"]["why"], "the hold says what to compare")
    n = len(x.w.launches)
    for _ in range(4):
        x.tick(600)
    ok(all(lz[0] != "I0" for lz in x.w.launches[n:]), "held: automatic rebuilding is suspended")
    R.unhold(x.s, "I0", "the clause is bound to the wrong comp; rebind and rebuild")
    build_and_fail(x, "I0", "4" * 40, "blind_fail", "A2 reads 0 at tick 1500")
    ok(x.st("I0")["status"] != "held", "an unhold restarts the count")
    x.done()
    # the same failures, all on one build: no product change, no signature hold
    x = rig()
    for _ in range(3):
        x.run_one("I0")
        R.snag(x.s, "I0", x.st("I0")["gen"], "tool_broke", "the def loader threw", x.r, now=x.now)
        stop(x, "I0")
    ok(x.st("I0").get("hold") is None or x.st("I0")["hold"].get("kind") != "signature",
       "three endings with no build between: no signature hold (no product change happened)")
    x.done()


# ---------------------------------------------------------------- one incident per capability

def t_incident():
    x = rig(n=4)
    why = "ssh to steve-c refused: Permission denied (publickey) after 30 s"
    for i in ("I0", "I1", "I2"):
        x.run_one(i)
        R.snag(x.s, i, x.st(i)["gen"], "bridge_unreachable", why, x.r, now=x.now)
        stop(x, i)
    d = B.load(x.s)
    opened = [k for k, v in d.items() if v.get("open")]
    ok(len(opened) == 1, "three items, one capability signature: one incident: %s" % opened)
    key = opened[0] if opened else None
    inc = d.get(key) or {}
    ok(inc.get("probe") == "I0" and sorted(inc.get("items") or {}) == ["I0", "I1", "I2"], "the first item is its probe")
    x.tick()
    told = [j for j in x.w.jams if j.startswith("INCIDENT")]
    ok(len(told) == 1 and key in told[0], "the Conductor is told once")
    for u in list(x.w.up):      # every worker that was already running ends (an incident leases nothing new; it kills nothing)
        x.w.up[u] = False
    x.tick()
    ok(any(v.get("open") for v in B.load(x.s).values()), "a probe's lost process says nothing: the incident stays open")
    n = len(x.w.launches)
    for _ in range(6):
        for u in list(x.w.up):
            x.w.up[u] = False
        x.tick(600)
    later = [lz[0] for lz in x.w.launches[n:]]
    ok("I1" not in later and "I2" not in later, "the affected items wait behind the probe: %s" % later)
    ok("I0" in later, "the probe is relaunched")
    ok("I3" in later or x.st("I3")["status"] in ("running", "candidate", "checking"), "an unaffected item still runs")
    x.tick()
    ok(len([j for j in x.w.jams if j.startswith("INCIDENT")]) == 1, "told once, not every tick")
    # the probe passes: its candidate is the evidence; the others come back
    x.run_one("I0")
    contract(x, "I0")
    st = x.st("I0")
    if st.get("warrant_owed"):
        R.learn(x.s, "I0", st["gen"], "WARRANT: the key was re-added on steve-c | refused again means the route, not the key")
    R.finish(x.s, "I0", st["gen"], "5" * 40, "evidence")
    ok(key not in B.load(x.s), "the probe's candidate releases the incident")
    ok(B.waits(x.s, "I1") is None, "and the affected items are back in line")
    x.done()
    # a probe that leaves the line hands the probe on; with none left, the incident ends
    x = rig(n=3)
    for i in ("I0", "I1", "I2"):
        x.run_one(i)
        R.snag(x.s, i, x.st(i)["gen"], "bridge_unreachable", why, x.r, now=x.now)
        stop(x, i)
    key = [k for k, v in B.load(x.s).items() if v.get("open")][0]
    with x.s.lock():
        cur = x.s.load("I0")
        cur["status"] = "held"
        cur["hold"] = {"why": "test", "kind": "strikes", "delivered": False, "at": x.now}
        x.s.save(cur)
    x.tick()
    ok(B.load(x.s)[key]["probe"] == "I1", "the probe was held: the next affected item probes")
    with x.s.lock():
        for i in ("I1", "I2"):
            cur = x.s.load(i)
            cur["status"] = "held"
            cur["hold"] = {"why": "test", "kind": "strikes", "delivered": False, "at": x.now}
            x.s.save(cur)
    x.tick()
    ok(key not in B.load(x.s), "no affected item left in line: the incident ends, nothing waits on it forever")
    x.done()
    # a hand release needs evidence
    x = rig(n=3)
    for i in ("I0", "I1", "I2"):
        x.run_one(i)
        R.snag(x.s, i, x.st(i)["gen"], "game_unmeasured_like_harness", "the stall probe is blind", x.r, now=x.now)
        stop(x, i)
    key = [k for k, v in B.load(x.s).items() if v.get("open")]
    try:
        B.release_by_hand(x.s, key[0], "", x.now)
        ok(False, "incident-release without evidence is refused")
    except ValueError:
        ok(True, "incident-release without evidence is refused")
    B.release_by_hand(x.s, key[0], "probe fixed in 1a2b3c4: stall probe reads the log again", x.now)
    ok(not B.load(x.s), "with evidence, released")
    x.done()
    # an ordinary product failure on three items is no incident
    x = rig(n=3)
    for i in ("I0", "I1", "I2"):
        x.run_one(i)
        R.snag(x.s, i, x.st(i)["gen"], "def_missing", "RM_Thing has no label", x.r, now=x.now)
        stop(x, i)
    ok(not any(v.get("open") for v in B.load(x.s).values()), "a product failure shared by three items opens nothing")
    x.done()


# ---------------------------------------------------------------- the history each role sees

def t_history():
    long = "the bridge returned map 0 while the probe read map 1: " + "y" * 600 + " END-OF-EVIDENCE"
    att = [{"gen": 1, "end": "game_fail", "detail": "A2 FAIL on the running game (/l/a.log)", "approach_next": "build"},
           {"gen": 2, "classified": "HARNESS", "evidence": long},
           {"gen": 2, "warrant": {"changed": "probe reads map 1", "decides": "A2 red again means the mod " + "z" * 300 + " END-W"}}]
    hist = R.ending_history(att)
    ok(any("END-OF-EVIDENCE" in h for h in hist), "the next builder reads the classification whole")
    ok(any("END-W" in h for h in hist), "and the retry warrant whole")
    x = rig()
    x.run_one("I0")
    st = x.st("I0")
    st["help"] = {"why": "circling", "tries": 0}
    r = dict(x.r, circling=dict(x.r.get("circling") or {}, help_options_max=3))
    p = R.help_prompt(st, "item text", att[:1], "nonce", r, att)
    ok("END-OF-EVIDENCE" in p and "attributions on record" in p, "the fresh pair of eyes reads the attributions whole")
    pv = R.help_prompt_vendor(st, "item text", att[:1], r, att)
    ok("END-OF-EVIDENCE" in pv, "so does the second vendor")
    R.contract(x.s, "I0", st["gen"], "python3 selftest_x.py")
    R.finish(x.s, "I0", st["gen"], "6" * 40, "evidence")
    for a in att[1:]:
        x.s.attempt("I0", a)
    cp = R.checker_prompt(x.st("I0"), "item text", "nonce")
    ok("END-OF-EVIDENCE" not in cp and "END-W" not in cp, "the blind checker sees none of it")
    x.done()


def t_learn_classify():
    """The classification reaches the record through `learn` itself, not a hand-written attempt: a CLASSIFY line far
    over 300 characters is kept whole on `diagnosed`, on the attempt record, in ending_history and in both help prompts."""
    x = rig()
    x.run_one("I0")
    contract(x, "I0")
    with x.s.lock():
        cur = x.s.load("I0")
        R.fail(x.s, cur, "game_fail", "A2 FAIL on the running game (/l/a.log)", x.r, x.now)
    stop(x, "I0")
    x.run_one("I0")
    st = x.st("I0")
    ok(bool(st.get("diagnose_owed")), "a game_fail leaves the next worker owing a classification")
    tail = "x" * 900 + " CLASSIFY-TAIL-PAST-300"
    R.learn(x.s, "I0", st["gen"], "CLASSIFY: HARNESS the bridge returned map 0 while the probe read map 1: " + tail)
    st = x.st("I0")
    ok(not st.get("diagnose_owed") and (st.get("diagnosed") or {}).get("class") == "HARNESS",
       "learn takes the CLASSIFY line and pays the debt")
    ok("CLASSIFY-TAIL-PAST-300" in ((st.get("diagnosed") or {}).get("evidence") or ""), "diagnosed keeps the evidence whole")
    att = x.s.attempts("I0")
    ok(any("CLASSIFY-TAIL-PAST-300" in (a.get("evidence") or "") for a in att), "the attempt record keeps it whole")
    ok(any("CLASSIFY-TAIL-PAST-300" in h for h in R.ending_history(att)), "the next builder reads it whole via learn")
    st["help"] = {"why": "circling", "tries": 0}
    r = dict(x.r, circling=dict(x.r.get("circling") or {}, help_options_max=3))
    ok("CLASSIFY-TAIL-PAST-300" in R.help_prompt(st, "item text", att, "nonce", r, att),
       "the fresh pair of eyes reads it whole via learn")
    ok("CLASSIFY-TAIL-PAST-300" in R.help_prompt_vendor(st, "item text", att, r, att), "so does the second vendor")
    x.done()


def main():
    for t in (t_warrant, t_signature, t_incident, t_history, t_learn_classify):
        print("--", t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            import traceback
            traceback.print_exc()
            ok(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_relentless_breakers: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
