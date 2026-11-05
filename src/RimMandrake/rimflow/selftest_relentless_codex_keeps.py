#!/usr/bin/env python3
"""RELENTLESS_CORE_FIX_CODEX_KEEPS_FINDING: the Codex r4 re-review's ten findings on relentless_game.py and
relentless.py, each row red without its fix (all ten were real; none rejected).

relentless_game.py
  #1  staged_idle: the idle clock runs from the first UP reading of THIS process, never from process start.
  #2  stale_holds: a bridge purpose names an item as a whole id (ART is not in "staging CART").
  #3  a final waiter whose batch timer runs out while the game LOADS meets the load bound, never a blind restage.
  #4  _env: a lane fix that rides the next staging does not swallow a second, unfixable cause: it routes, no builder.
  #5  a remedy is spent only by a staging that confirmed game-ready; one that died first keeps it for the next.
relentless.py
  #6  charge: a damaged day record raises before the item counts the run (no charge lost after the repair).
  #7  proof_gate: a contract-only proof repair on the unchanged sha is checked, as an empty commit carrying it is.
  #8  launch_failed / breaker_emergency: openings are counted inside the window, not over the whole incident.
  #9  hand_check_lint: a non-string title_rx entry is named, never a TypeError.
  #10 reserve_foreign / give_back: a hold that lands during settle_wait is never overwritten to queued.
"""
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402
import selftest_relentless_game as SG  # noqa: E402
import selftest_relentless_envcause as SE  # noqa: E402

FAILS = SG.FAILS
ok = SG.ok
RULES = R.rules()


def t_staged_idle_from_first_up():
    c = dict(G.cfg(RULES), stage_idle_s=600)
    S = 1_000_000.0
    fx = types.SimpleNamespace(game_reading=lambda: {"state": "UP", "started": S})
    g = {"staged_at": S - 10}
    now = S + 1500          # a 25-minute full-list load, read UP for the first time
    res = G.staged_idle(fx, g, c, now)
    ok(isinstance(res, tuple) and res[0] is None and (res[1] or {}).get("at") == now,
       "#1 a long load read UP for the first time is not idle; its clock starts at this reading: %s" % (res,))
    if not isinstance(res, tuple):
        return
    g["up_seen"] = res[1]
    ok(G.staged_idle(fx, g, c, now + 599)[0] is None, "#1 599 s after the first UP reading: still not idle")
    ok(G.staged_idle(fx, g, c, now + 600)[0], "#1 600 s after it: idle (the instrument can say yes)")
    fx2 = types.SimpleNamespace(game_reading=lambda: {"state": "UP", "started": S + 2000})
    why, seen = G.staged_idle(fx2, g, c, now + 2100)
    ok(why is None and seen["started"] == S + 2000 and seen["at"] == now + 2100,
       "#1 a new process restarts the clock: %s" % seen)


def t_purpose_names_whole_id():
    c = G.cfg(RULES)
    S = 2_000_000.0
    now = S + c["live_idle_s"] + 100

    def holds(purpose, item="ART"):
        states = [{"item": item, "status": "running", "live_iter": {"started": S, "at": S, "bridge_seen": S}}]
        return G.stale_holds(states, now, c, lambda p: True,
                             lambda: {"holder": "RELENTLESS", "purpose": purpose, "since": S},
                             lambda: {"state": "UP", "started": S})
    got = holds("relentless staging CART: deploy and restart for its live proofs")
    ok([k for _, k, _w in got] == ["live_iter"], "#2 CART's staging is not ART's bridge use: ART's idle hold lapses: %s" % got)
    ok([k for _, k, _w in holds("relentless staging ART_X (renew)")] == ["live_iter"], "#2 nor is ART_X's")
    ok([k for _, k, _w in holds("live iteration on ART: A2")] == ["seen"], "#2 a purpose naming ART itself is seen")


def t_final_waiter_meets_the_load_gate():
    x = SG.rig(2, share=1.0, max_workers=2)
    SG.two_final(x)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    x.now += 1
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)
    for i in ("I0", "I1"):
        with x.s.lock():
            st = x.s.load(i)
            st["game"].update(phase="final", final_game=x.w.started)
            x.s.save(st)
    t = x.now + G.DEFAULTS["final_wait_s"] + 10
    x.w.running, x.w.started, x.w.mods = "LOADING", t - 60, 316     # someone's cold load, one minute in
    takes = x.w.events.count("take")
    acts = []
    G.step(x.s, x.w, x.r, "I0", t, acts, R)
    g0 = x.st("I0")["game"]
    ok(g0["phase"] != "staging" and x.w.events.count("take") == takes and any(a["do"] == "game_loading" for a in acts),
       "#3 the batch timer ran out while the game loads: waited on the load bound, nothing restaged: %s %s"
       % (g0.get("phase"), [a["do"] for a in acts]))
    x.done()


def t_riding_fix_does_not_swallow_a_route():
    x = SE.in_prove()
    gen = x.st("I0")["gen"]
    acts = []
    rows = {"A2": SE.row(SE.WHYS["load2"], x.now),
            "A3": SE.row(SE.WHYS["proof_call"], x.now, criterion="A3", defect=True)}
    acted = G._env(x.s, x.w, x.r, "I0", rows, 0, x.now, acts)
    st = x.st("I0")
    ok(acted and st["status"] == "held" and st["gen"] == gen and not st.get("last_fail"),
       "#4 a reload fix that rides the staging, beside an unfixable cause: routed once, no builder: %s %s"
       % (acted, [a["do"] for a in acts]))
    ok((st["game"].get("remedy") or {}).get("mods") == ["7f.alienworlds", "mandrake.rm.generators"],
       "#4 and the riding fix is still recorded: %s" % st["game"].get("remedy"))
    x.done()


REMEDY = {"mods": ["mandrake.rsw.armoury"], "cmds": ["python.exe m.py run Armoury"], "why": "producer", "at": 1}


def staging_with_remedy():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.tick()
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["remedy"] = dict(REMEDY)
        x.s.save(st)
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging" and "python.exe m.py run Armoury" in (x.w.launches[-1][2] if x.w.launches else ""),
       "#5 the staging launched carrying the remedy")
    return x, st


def t_remedy_spent_only_on_ready():
    x, st = staging_with_remedy()
    x.w.up[st["run"]["unit"]] = False       # the staging dies without saying game-ready
    x.tick()
    g = x.st("I0")["game"]
    ok((g.get("remedy") or {}).get("cmds") == REMEDY["cmds"] and not g.get("remedy_carried"),
       "#5 a staging that died before game-ready leaves the remedy for the next one: %s" % g.get("remedy"))
    x.done()
    x, st = staging_with_remedy()
    G.ready(x.s, "I0", st["gen"], "ran python.exe m.py run Armoury", now=x.now)
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    g = x.st("I0")["game"]
    ok(not g.get("remedy") and not g.get("remedy_carried"), "#5 a staging that confirmed game-ready spends it: %s" % g)
    x.done()


def t_damaged_day_raises_before_counting():
    base = tempfile.mkdtemp(prefix="cxk_")
    try:
        store = R.Store(base)
        now = 1793866000.0
        y = store.p("spend-%s.json" % R.day_key(now - 86400))
        with open(y, "w") as f:
            f.write('{"spent": 3, "ru')
        st = {"spent": 0}
        try:
            R.charge(store, st, 500, now, {"run_reserve": 1000}, "u1", "transcript")
            raised = None
        except R.SpendUnreadable as e:
            raised = e
        ok(raised is not None and st["spent"] == 0, "#6 a damaged yesterday: the charge raises, the item counts nothing")
        os.unlink(y)
        got = R.charge(store, st, 500, now, {"run_reserve": 1000}, "u1", "transcript")
        with open(store.p("spend-%s.json" % R.day_key(now))) as f:
            d = json.load(f)
        ok(got == 500 and st["spent"] == 500 and d["runs"].get("u1") == 500 and d["spent"] == 500,
           "#6 after the repair the retried run is booked on the day and the item alike: %s %s" % (st, d))
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_contract_only_repair_on_same_sha():
    held = {"sha": "A", "contract": {"proof": "python verify.py", "live": None, "game": None, "by_gen": 1}}
    st = {"item": "I0", "proof_only": held,
          "contract": {"proof": "python verify.py --strict", "live": None, "game": None, "by_gen": 2, "why": "w"}}
    fx = types.SimpleNamespace(changed=lambda a, b, i: [], existed=lambda sha, p: True)
    ok(R.proof_gate(fx, RULES, st, {"sha": "A"}) == (None, None),
       "#7 a contract-only proof repair on the unchanged sha goes to the checker")
    st["contract"] = dict(held["contract"], by_gen=2, why="only the why moved")
    ok(R.proof_gate(fx, RULES, st, {"sha": "A"})[0] == "proof_unchanged", "#7 the same contract on the same sha is still refused")


def t_breaker_opens_counted_in_window():
    base = tempfile.mkdtemp(prefix="cxk_")
    try:
        store = R.Store(base)
        r = dict(RULES, launch_breaker=1, breaker_cool_s=10, breaker_cool_max_s=10, breaker_same_cause_window_s=60,
                 breaker_same_cause_opens=3, breaker_refusal_words=[])
        why = "claude: spawn ENOENT"
        told = []
        fx = types.SimpleNamespace(told=lambda row: told.append(row) and None, conductor_alarm=lambda t: None,
                                   staffing_alarm=lambda i, t: None)
        for t in (0.0, 40.0, 80.0):
            R.launch_failed(store, r, 1e6 + t, why)
        c = R.load_breaker(store)["opens"][R.cause_key(why)]
        ok(c["n"] == 2, "#8 openings at 0, 40, 80 s in a 60 s window are two: %s" % c)
        acts = []
        R.breaker_emergency(store, fx, r, 1e6 + 80, acts)
        ok(not told and not any(a["do"] == "breaker_emergency" for a in acts), "#8 and raise no emergency: %s" % acts)
        for t in (100.0, 120.0):
            R.launch_failed(store, r, 1e6 + t, why)
        R.breaker_emergency(store, fx, r, 1e6 + 120, acts)
        ok(told and any(a["do"] == "breaker_emergency" for a in acts),
           "#8 three inside the window (80, 100, 120 s) are the emergency: %s" % R.load_breaker(store)["opens"])
    finally:
        shutil.rmtree(base, ignore_errors=True)


def t_hand_check_lint_names_non_string():
    try:
        out = R.hand_check_lint({"hand_check": {"title_rx": [None, "(", "ok.*"]}}, {})
        raised = None
    except TypeError as e:
        out, raised = [], e
    ok(raised is None and len(out) == 2 and any("None" in o for o in out) and any("'('" in o for o in out),
       "#9 a null and a broken pattern are both named, no crash: %s %s" % (raised, out))


def t_hold_during_settle_wait_wins():
    base = tempfile.mkdtemp(prefix="cxk_")
    try:
        store = R.Store(base)
        now = 1793866000.0
        R.enrol_one(store, "F0", "foreign", now)
        with store.lock():
            st = store.load("F0")
            st["status"] = "queued"
            store.save(st)

        def hold_lands(_s):     # the owner's hold arrives while the supervisor waits out a racing claim
            with store.lock():
                cur = store.load("F0")
                cur["status"], cur["hold"] = "stopping", {"kind": "owner", "why": "his hold", "at": now}
                store.save(cur)
        fx = types.SimpleNamespace(settle_wait=hold_lands, seat_words=lambda: None,
                                   item_state=lambda i: {"owner": "FOUNDRY"}, ledger_take=lambda i: None)
        r = dict(RULES, staffing={"settle_s": 0, "foreign_seat": "FOUNDRY"})
        acts = []
        got = R.reserve_foreign(store, fx, r, "F0", now, acts)
        st = store.load("F0")
        ok(got is False and st["status"] == "stopping" and st.get("hold"),
           "#10 a hold that landed during settle_wait is kept, never given back to queued: %s %s" % (st["status"], acts))
        ok(R.give_back(store, "F0", "late", "queued", reserved=now) is False and store.load("F0")["status"] == "stopping",
           "#10 give_back with a stale reservation token moves nothing")
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    for t in (t_staged_idle_from_first_up, t_purpose_names_whole_id, t_final_waiter_meets_the_load_gate,
              t_riding_fix_does_not_swallow_a_route, t_remedy_spent_only_on_ready, t_damaged_day_raises_before_counting,
              t_contract_only_repair_on_same_sha, t_breaker_opens_counted_in_window, t_hand_check_lint_names_non_string,
              t_hold_during_settle_wait_wins):
        t()
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
