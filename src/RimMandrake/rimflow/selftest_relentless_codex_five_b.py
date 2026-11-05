#!/usr/bin/env python3
"""RELENTLESS_REVIEW_FIX_ROUND_FIVE_DIGS: the Codex r5 findings on relentless_game.py and relentless.py, each row red
without its fix.

relentless_game.py
  #1  green_stands: a contract row in the same whole second as a fractional offline_green.at (no fingerprint) follows it.
  #2  not_measuring: "the proof exited -11: it did not measure" (killed by a signal) is a dud and counts to the limit.
  #3  stage phase: an unread game ({"state": None}) is a harness wait, never a launch or a deploy.
  #4  _env: an environment row older than `since` (read before this staging) neither routes nor holds; at `since` it acts.
relentless.py
  #19 help_step: a help whose clone an unreaped quarantine holds is never resumed (help_account_lost); a fresh try.
  #20 game_pass(began=): a wake spends the tick's remaining game budget, never a fresh one; tick passes its loop's began.
  #21 tick: a wake written during the final flush is not taken by that tick (its writes would go unflushed).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import relentless_game as G  # noqa: E402
import selftest_relentless_game as SG  # noqa: E402
import selftest_relentless_envcause as SE  # noqa: E402

FAILS = SG.FAILS
ok = SG.ok
SHA = SG.SHA


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def t_green_same_second_contract_row():
    st = {"candidate": {"sha": SHA}, "contract": {"game": {"clauses": ["A2"]}},
          "game": {"offline_green": {"sha": SHA, "at": 1_000_000.6}}}
    ok(G.green_stands(st, []), "#1 sanity: no contract row, the green stands")
    ok(G.green_stands(st, [{"at": iso(1_000_000), "contract": {"proof": "x"}}]) is None,
       "#1 a contract row in green's own whole second: the Judge reads it afresh")
    ok(G.green_stands(st, [{"at": iso(999_999), "contract": {"proof": "x"}}]),
       "#1 a contract row a second before the green: it still stands")


def t_signal_exit_is_a_dud():
    dud = {"at": iso(1_000_000), "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
           "why": "the proof exited -11: it did not measure: x", "log": "/l/d.log"}
    got = G.not_measuring([dud, dud], "I0", SHA, ["A2"], 2)
    ok(got.get("A2", (0,))[0] == 2, "#2 two -11 duds count to limit 2: %s" % got)


def t_stage_unread_waits():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    with x.s.lock():
        st = x.s.load("I0")
        st["game"].update(phase="stage", staged_at=None, entered_at=x.now - 500, retry_at=None)
        x.s.save(st)
    x.w.running = None
    takes, launches, enables = x.w.events.count("take"), len(x.w.launches), len(x.w.enabled)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    g = x.st("I0")["game"]
    ok(g["phase"] == "stage" and x.w.events.count("take") == takes and len(x.w.launches) == launches
       and len(x.w.enabled) == enables, "#3 an unread game in stage waits, no take/launch/deploy: %s %s"
       % (g["phase"], [a.get("do") for a in acts]))
    x.done()


def t_env_row_before_since_ignored():
    x = SE.in_prove()
    rows = {"A3": SE.row(SE.WHYS["proof_call"], x.now - 100, criterion="A3", defect=True)}
    acts = []
    acted = G._env(x.s, x.w, x.r, "I0", rows, x.now - 50, x.now, acts)
    ok(not acted and x.st("I0")["status"] != "held", "#4 a row read before this staging: no route, no hold: %s %s"
       % (acted, [a.get("do") for a in acts]))
    acted = G._env(x.s, x.w, x.r, "I0", rows, x.now - 100, x.now, acts)
    ok(acted and x.st("I0")["status"] == "held", "#4 the same row at since: it routes: %s" % acted)
    x.done()


def t_quarantined_help_not_resumed():
    import selftest_relentless as T
    import selftest_relentless_attrib as TA
    import selftest_relentless_resume as RS
    real = R.tree_present
    R.tree_present = lambda p: True
    try:
        x = TA.rig([TA.STEVE], circling=T.HELP)
        h0 = dict(RS.consult_running(x, TA.STEVE))
        with x.s.lock():
            st = x.s.load(TA.STEVE)
            st["quarantined"].append({"run": {"unit": "q-unit"}, "at": x.now, "clone": h0["clone"]})
            x.s.save(st)
        x.w.account_sign = RS.LOST
        x.w.up[h0["run"]["unit"]] = False
        called = []
        real_lost = R.help_account_lost
        R.help_account_lost = lambda *a, **k: (called.append(1), real_lost(*a, **k))[1]
        try:
            R.help_step(x.s, x.w, x.r, TA.STEVE, x.now + x.r["circling"]["help_max_s"] + 1, [])
        finally:
            R.help_account_lost = real_lost
        h = x.st(TA.STEVE)["help"]
        ok(not called and not h.get("nonce") and not h.get("clone") and not (h.get("run") or {}).get("resume"),
           "#19 a quarantined clone's help is a fresh try, never resumed: called=%s %s" % (called, h))
        x.done()
    finally:
        R.tree_present = real


def t_wake_spends_the_tick_budget():
    x = SG.rig(1)
    SG.to_game(x, "I0")
    x.r = dict(x.r, tick_game_budget_s=60)
    x.w.wall = lambda: 10_000.0
    stepped = []
    real = R.step
    R.step = lambda store, fx, r, item, now, acts: stepped.append(item)
    try:
        R.game_pass(x.s, x.w, x.r, x.now, [], began=10_000.0 - 60)
        ok(stepped == [], "#20 a wake with the tick's budget spent steps nothing: %s" % stepped)
        R.game_pass(x.s, x.w, x.r, x.now, [], began=10_000.0 - 10)
        ok(stepped == ["I0"], "#20 sanity: budget left, it steps: %s" % stepped)
    finally:
        R.step = real
    x.done()
    # the tick's wake gets the step loop's began
    x = SG.rig(1)
    SG.to_game(x, "I0")
    seen, real_gp, real_step = [], R.game_pass, R.step

    def gp(store, fx, r, now, acts, began=None):
        seen.append(began)

    def st_(store, fx, r, item, now, acts):
        if not seen and not os.path.exists(store.p(R.GAME_WAKE)):
            open(store.p(R.GAME_WAKE), "w").close()
        return real_step(store, fx, r, item, now, acts)
    R.game_pass, R.step = gp, st_
    try:
        x.tick()
    finally:
        R.game_pass, R.step = real_gp, real_step
    ok(seen and seen[0] is not None, "#20 the tick's wake passes its step loop's began: %s" % seen)
    x.done()


def t_flush_wake_not_taken():
    x = SG.rig(1)
    SG.to_game(x, "I0")

    def flush():
        open(x.s.p(R.GAME_WAKE), "w").close()
        return None
    x.w.flush = flush
    x.tick()
    ok(os.path.exists(x.s.p(R.GAME_WAKE)), "#21 a wake written during the final flush is left for game_next / next tick")
    x.done()


def main():
    for name, fn in sorted(globals().items()):
        if name.startswith("t_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001  a crash is a failed row
                FAILS.append(name)
                print("FAIL %s raised %s: %s" % (name, type(e).__name__, e))
    if FAILS:
        print("selftest_relentless_codex_five_b: FAIL %d" % len(FAILS))
        return 1
    print("selftest_relentless_codex_five_b: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
