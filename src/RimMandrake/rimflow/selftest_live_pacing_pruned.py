#!/usr/bin/env python3
"""selftest_live_pacing_pruned.py -- PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE: the live round has no pacing.

The owner, 2026-11-06: "of course we should drop all this pacing control crap... the LLM's pace things slowly all by
themselves, we don't need to add to that." So: no round_max 6 (a round runs every eligible proof), no round_every_s
1800 (the tick starts a round whenever none runs and no other live user has the game), no unmeasured_retry_s 6 h (an
UNMEASURED row routes by cause: the bridge's or the round's own wall runs in the next round, a cause the proof wrote on
this game and build waits for another game or a new build). Kept: no rerun of a PASS/FAIL/REFUSED on the same sha.
No game, no bridge, no ledger.

    python3 src/RimMandrake/rimflow/selftest_live_pacing_pruned.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless_live_round as R      # noqa: E402

FAILS = []
NOW = 1_800_000_000
GAME = R.L.iso(NOW - 3 * 3600)          # the running game started three hours ago
OLD_GAME = R.L.iso(NOW - 30 * 3600)
PROSE = "live-proof A1: python3 live_log_check.py --absent RUT_A\n"
GONE = ("round_max", "round_every_s", "unmeasured_retry_s")


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


def item(i="EG_X", sha="abc123"):
    return {"id": i, "state": "built", "built_sha": sha, "title": "t",
            "criteria": [{"id": "A1", "level": "L1", "text": "x"}], "outstanding": ["A1"]}


def row(outcome, why="", game=GAME, age=60, sha="abc123"):
    r = {"item": "EG_X", "criterion": "A1", "sha": sha, "outcome": outcome, "why": why, "at": R.L.iso(NOW - age)}
    if game:
        r["game"] = game
    return r


def t_defaults_and_rules():
    check("DEFAULTS holds no pacing key", not any(k in R.DEFAULTS for k in GONE), R.DEFAULTS)
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        live = json.load(f)["live"]
    check("relentless_rules.json live holds no pacing key", not any(k in live for k in GONE), sorted(live))
    with open(os.path.join(HERE, "relentless_wake.json"), encoding="utf-8") as f:
        keys = json.load(f).get("clock_keys", {})
    check("relentless_wake.json lists no removed clock", not any("live." + k in keys for k in GONE))


def t_routes():
    """Each UNMEASURED cause's route, on the running game (cron round), never a timer: the same row a minute or a day
    old says the same thing."""
    for age in (60, 7 * 3600, 30 * 86400):
        def due(r, game=GAME, cron=1):
            return R.due(r, "abc123", NOW, cron, game, per_game=bool(cron))
        cases = (
            ("bridge busy (round STOP)", row("UNMEASURED", "bridge not taken: held by OWNER", age=age), None),
            ("no running game (round STOP)", row("UNMEASURED", "no running game to test", age=age), None),
            ("bridge dud", row("UNMEASURED", "rimbridge: IndeterminateError on call", age=age), None),
            ("proof exit 2 on this game", row("UNMEASURED", "the proof printed UNMEASURED: x", age=age), R.DUD_HERE),
            ("proof exit 2 on an older game", row("UNMEASURED", "UNMEASURED: x", game=OLD_GAME, age=age), None),
            ("not deployed on this game", row("UNMEASURED", R.L.UNDEPLOYED[0] + " RM_X", age=age),
             "not deployed on this game"),
            ("a pre-game-field row written on this game", row("UNMEASURED", "UNMEASURED: x", game=None, age=60),
             R.DUD_HERE),
        )
        for name, r, want in cases:
            got = due(r)
            check("route at age %ds: %s -> %s" % (age, name, want or "runs now"), got == want, got)
        nag = dict(row("NOT_ADMITTED", "the running load's mod list could not be read", age=age),
                   admit="load_unread")
        check("route at age %ds: transient NOT_ADMITTED runs now" % age, due(nag) is None, due(nag))
        plain = row("UNMEASURED", "UNMEASURED: x", age=age)
        check("route at age %ds: a game phase's own round runs it after staging" % age, due(plain, cron=0) is None)
        check("route at age %ds: a new build runs it" % age, R.due(plain, "def456", NOW, 1, GAME) is None)
    old = row("UNMEASURED", "UNMEASURED: x", game=None, age=10 * 3600)      # before this game started
    check("route: a pre-game-field row older than the game runs", R.due(old, "abc123", NOW, 1, GAME) is None)


def t_terminal_kept():
    for o in R.TERMINAL:
        for age in (60, 30 * 86400):
            got = R.due(row(o, age=age), "abc123", NOW, 1, GAME)
            check("kept: %s on the same sha never reruns (age %ds)" % (o, age), got == "judged on this build", got)
            check("kept: %s on another sha runs" % o, R.due(row(o, age=age), "def456", NOW, 1, GAME) is None)


class Fx:
    def __init__(self, n):
        self.n = n

    def game_started(self):
        return NOW - 3 * 3600

    def items(self):
        return [item("EG_%02d" % k) for k in range(self.n)]

    def proofs(self, _i):
        return PROSE

    def mods_of(self, _sha):
        return ["UtinniPatches"]

    def folded(self):
        return {}


def t_round_runs_all():
    calls = []

    def run(fx, root, item_id, cid, proof, args, r, now=None, **kw):
        calls.append(item_id)
        return {"item": item_id, "criterion": cid, "outcome": "PASS", "why": "proof exit 0", "sha": "abc123"}
    with tempfile.TemporaryDirectory() as root:
        s = R.run_round(Fx(11), root, {"live": {"round_max": 6}}, now=NOW, run=run)
        check("round: every eligible proof runs in one sitting (11 > the old 6), a stale round_max ignored",
              len(calls) == 11 and s["eligible"] == 11 and s["why"] == "done", (len(calls), s.get("why")))
        calls.clear()
        R.run_round(Fx(11), root, {}, max_items=2, now=NOW, run=run)
        check("round: --max is still a caller's own bound", len(calls) == 2, calls)


class TickStore:
    def __init__(self, d):
        self.d = d

    def p(self, name):
        return os.path.join(self.d, name)

    def _write(self, path, text):
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def states(self):
        return []


class TickFx:
    def __init__(self):
        self.launched, self._alive = 0, False

    def live_round_alive(self, _pid):
        return self._alive

    def live_round_launch(self):
        self.launched += 1
        return 4242


def t_tick_no_clock():
    import relentless as RL
    with tempfile.TemporaryDirectory() as d:
        st, fx, acts = TickStore(d), TickFx(), []
        r = {"live": {"auto": True, "round_every_s": 1800}}     # a stale key: nothing reads it
        for k, t in enumerate((1000.0, 1001.0, 1002.0)):
            RL.live_tick(st, fx, r, t, acts)
            check("tick %d: a round starts whenever none runs (no 1800 s clock)" % k, fx.launched == k + 1, fx.launched)
        fx._alive = True
        RL.live_tick(st, fx, r, 1003.0, acts)
        check("tick: a running round is never doubled", fx.launched == 3)


def t_no_wake_after_empty_round():
    """A round that ran nothing held no game: main() must not wake the supervisor, or an empty round and its game pass
    would chase each other now that no clock separates them."""
    src = open(os.path.join(HERE, "relentless_live_round.py"), encoding="utf-8").read()
    check("main: wake_supervisor only after a round that ran something",
          'if summary.get("runs"):' in src and "wake_supervisor(root)" in src.split('if summary.get("runs"):')[1][:200])


def main():
    for t in (t_defaults_and_rules, t_routes, t_terminal_kept, t_round_runs_all, t_tick_no_clock,
              t_no_wake_after_empty_round):
        t()
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
