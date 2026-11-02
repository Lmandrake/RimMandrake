#!/usr/bin/env python3
"""selftest_relentless_game.py -- Relentless's second mode (relentless_game.py, RELENTLESS_LIVE_BUILD_ONE_AGENT_TWO_MODES).

No game, no bridge, no ledger: selftest_relentless's FakeWorld plus the game effects, all recorded. What must hold, each
red under its mutant:
  a live-game item joins the pool only with the mode on; the worker brief carries the resource rule and the checker's
  the game clauses; a blind offline PASS on an item with game clauses is no close, it enters the game phase on that sha;
  `implemented` runs on that sha and a clause not owed at a live level goes back to a worker; the lease rule (green
  offline on the same sha or a stated no-offline reason, a proof line per clause, no flyer, one live user, bridge idle);
  the blind rerun is the round for this item; a FAIL row returns the item with the finding; a ledger done finishes it;
  staging takes the bridge, launches the pilot agent and releases the bridge the moment it ends, snag or not; the
  global live round waits while a game phase holds the game.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R            # noqa: E402
import relentless_game as G       # noqa: E402
import selftest_relentless as S   # noqa: E402

FAILS = S.FAILS
ok = S.ok
SHA = "sha1"
PROOF = "live-proof A2: python3 src/RimMandrake/Utils/live_def_check.py --has ThingDef/RM_X=CompProperties_Y\n"


class GW(S.FakeWorld):
    def __init__(self, n=2):
        S.FakeWorld.__init__(self, n)
        self.led, self.impl, self.rows, self.events, self.proves = {}, [], [], [], []
        self.running, self.idle, self.take_why, self.palive = True, None, None, set()
        self.proofs = {}
        self.books = "/books"
        self.owed = {"A2": "L1"}
        self.title = "a mod thing"

    def game_ledger(self, item):
        return self.led.get(item) or {"state": "doing", "built_sha": None, "title": self.title, "owed": {}}

    def game_implement(self, item, sha, crit, live=None):
        self.impl.append((item, sha, crit))
        self.events.append("implement")
        self.led[item] = {"state": "built", "built_sha": sha, "title": self.title, "owed": dict(self.owed)}

    def proofs_at(self, item, sha, ext=".txt"):
        return self.proofs.get((item, ext), PROOF if ext == ".txt" else "")

    def game_rows(self): return self.rows
    def game_running(self): return self.running
    def bridge_idle(self, p): return self.idle

    def bridge_take(self, p):
        self.events.append("take")
        return self.take_why

    def bridge_release(self):
        self.events.append("release")

    def prove_launch(self, item):
        self.proves.append(item)
        self.events.append("prove")
        return 4000 + len(self.proves)

    def prove_alive(self, pid): return pid in self.palive
    def live_round_alive(self, pid): return False

    def live_round_launch(self):
        self.events.append("global_round")
        return 99


def rig(n=2, **kw):
    x = S.Rig(n, **kw)
    x.w = GW(n)
    x.r = dict(x.r, live=dict(x.r.get("live") or {}, auto=False))
    return x


GAME = {"clauses": ["A2"], "why": "the comp only exists once the defs load"}


def to_game(x, i, game=GAME, word="PASS"):
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], "python3 selftest_x.py", game=game)
    R.finish(x.s, i, st["gen"], SHA, "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    st = x.st(i)
    ok(st["status"] == "checking", "%s: finish reaches the checker" % i)
    R.verdict(x.s, i, st["check"]["nonce"], word, "ran it")
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()


def t_parse_and_brief():
    ok(G.parse_game(None, None, None) is None, "no game words, no game block")
    for bad in (("A2", None, None), ("", "why", None), ("a2;rm", "why", None)):
        try:
            G.parse_game(*bad)
            ok(False, "a half or malformed game block is refused: %r" % (bad,))
        except ValueError:
            ok(True, "a half or malformed game block is refused: %r" % (bad,))
    g = G.parse_game("B3, A2", "why", "no offline harness")
    ok(g == {"clauses": ["A2", "B3"], "why": "why", "no_offline": "no offline harness"}, "clauses sorted, reasons kept")
    st = R.new_state("I0", 0, "t")
    on = dict(S.RULES, game=dict(G.DEFAULTS, enabled=True))
    off = dict(S.RULES, game=dict(G.DEFAULTS, enabled=False))
    ok("RESOURCES" in R.worker_prompt(st, "x", "", on) and "offline first" in R.worker_prompt(st, "x", "", on).lower()
       or "Prove everything you can offline first" in R.worker_prompt(st, "x", "", on),
       "the worker brief teaches the resource rule when the mode is on")
    ok("RESOURCES" not in R.worker_prompt(st, "x", "", off), "and not when it is off")
    for w in ("never a flyer's flight", "never fullscreen or focus the game", "minimal mod list", "one live user",
              "--game a2,b3"):
        ok(w in " ".join(G.BRIEF).lower(), "the brief says: %s" % w)
    st["candidate"] = {"sha": SHA, "evidence": "e"}
    st["contract"] = {"proof": "p", "game": GAME}
    ok("GAME CLAUSES A2" in R.checker_prompt(st, "x", "n"), "the checker reads the game clauses' proof lines")


def t_pool():
    class It:
        owner, state, blocked, kind, lease, id, title = "BENCH", "ready", False, "feature", None, "X", "t"
    it = It()
    it.needs = "bridge"
    on = dict(S.RULES, pool_seats=["BENCH"], game=dict(G.DEFAULTS, enabled=True))
    off = dict(on, game=dict(G.DEFAULTS, enabled=False))
    ok(R.eligible(it, on), "a needs=bridge item joins the pool with the game mode on")
    ok(not R.eligible(it, off), "and stays out with it off")
    it.needs = "owner"
    ok(not R.eligible(it, on), "needs=owner never joins")


def t_contract_widens():
    x = rig(1)
    x.run_one("I0")
    st = x.st("I0")
    R.contract(x.s, "I0", st["gen"], "p", live="once: t")
    R.contract(x.s, "I0", st["gen"], "p", why="A2 needs the loaded defs", game=GAME)
    k = x.st("I0")["contract"]
    ok(k.get("game") == GAME and k.get("live") == "once: t", "game clauses widen a set contract and keep its live line")
    try:
        R.contract(x.s, "I0", st["gen"], "other proof", why="w", game=GAME)
        ok(False, "a game block cannot smuggle in a new proof")
    except ValueError:
        ok(True, "a game block cannot smuggle in a new proof")
    x.done()


def t_pass_enters_game_and_proves():
    x = rig(1)
    to_game(x, "I0")
    st = x.st("I0")
    ok(st["status"] == "game" and not x.w.closes, "an offline PASS with game clauses is no close: status game")
    ok(st["game"]["offline_green"]["sha"] == SHA == st["game"]["sha"], "the offline PASS is recorded on the same sha")
    x.tick()
    ok(x.w.impl and x.w.impl[0][1] == SHA, "implemented on the passed sha")
    ok(x.st("I0")["game"]["phase"] == "prove", "then the prove phase")
    x.w.idle = "NOT TAKEABLE  OWNER holds it"
    x.tick()
    ok(not x.w.proves and "take" not in x.w.events, "his hold: no round, no take")
    x.w.idle = None
    x.tick()
    ok(x.w.proves == ["I0"] and x.st("I0")["game"]["phase"] == "proving", "bridge idle: the blind round for this item")
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "PASS"}]
    x.tick()
    ok(x.st("I0")["status"] == "game", "a PASS row waits for the ledger's own done")
    x.w.led["I0"]["state"] = "done"
    x.tick()
    ok(x.st("I0")["status"] == "done" and not x.w.closes, "the ledger's done finishes it, no second close")
    x.done()


def t_fail_returns():
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "FAIL",
                 "log": "/l/A2.log"}]
    x.tick()
    st = x.st("I0")
    ok(st["status"] in ("stopping", "queued", "running") and st["last_fail"]["class"] == "game_fail"
       and "/l/A2.log" in st["last_fail"]["detail"], "a FAIL on the game sends it back to a worker with the log")
    ok(any("game_fail" in n for n in x.w.notes), "and says so on the ledger")
    x.done()


def t_not_owed_returns():
    x = rig(1)
    x.w.owed = {"A2": "L0"}
    to_game(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "game_contract", "a game clause owed at L0 is no game clause")
    x.done()


def t_gate():
    st = {"game": {"sha": "s2", "offline_green": {"sha": "s1"}}, "contract": {"game": {"clauses": ["A2"]}}}
    fl = r"\b(flight|flying)\b"
    ok("offline" in (G.gate(st, "t", PROOF, fl, None) or ""), "no lease without a green offline proof on the same sha")
    st["contract"]["game"]["no_offline"] = "nothing offline reads it"
    ok(G.gate(st, "t", PROOF, fl, None) is None, "unless the item states why none is possible")
    st["game"]["offline_green"]["sha"] = "s2"
    ok("A2" in (G.gate(st, "t", "", fl, None) or ""), "a clause with no proof line gets no lease")
    ok("flyer" in (G.gate(st, "the flying lizard", PROOF, fl, None) or ""), "a flyer gets no lease")
    ok("one live user" in (G.gate(st, "t", PROOF, fl, "I9") or ""), "another item in a game phase: no lease")


def t_stage_and_release():
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging" and x.w.events.count("take") == 1, "no game: the supervisor takes the bridge")
    ok(x.w.launches[-1][3] == x.r["pilot_agent"] and "STAGING" in x.w.launches[-1][2], "and launches one staging worker")
    R.beat(x.s, "I0", st["gen"])
    G.ready(x.s, "I0", st["gen"], "deployed, minimal list")
    x.w.running = True
    x.tick()        # ready with the unit still up: it is stopped, the bridge stays held until it is down
    ok("release" not in x.w.events, "no release while the staging worker may still drive the game")
    x.tick()
    ok(x.w.events[-1] == "release" and x.st("I0")["game"]["phase"] == "prove", "ready and down: the bridge is released at once")
    x.tick()
    ok(x.w.proves == ["I0"], "then the blind round")
    x.done()


def t_stage_snag_releases():
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    R.snag(x.s, "I0", st["gen"], "game_stage", "steam would not start", x.r)
    ok(x.st("I0")["status"] == "game", "a staging snag waits for the supervisor")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    st = x.st("I0")
    ok("release" in x.w.events and st["last_fail"]["class"] == "game_stage", "the bridge is released, then it goes back")
    x.done()


def t_flyer_put_down():
    """A flyer waits on the owner himself: held, asked on the ledger, its clone back at once (owner 2026-11-02)."""
    x = rig(1)
    x.w.title = "the flying lizard"
    to_game(x, "I0")
    st = x.st("I0")
    x.w.pool[st["clone"]] = {"idle": 5, "real": ["a.cs"]}
    x.tick()
    x.w.running = False
    x.tick(), x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and "flyer" in st["hold"]["why"] and st["put_down"]["on"].startswith("game phase: flyer"),
       "a flyer is put down on the owner, not left waiting: %s %s" % (st["status"], st.get("hold")))
    ok("I0" in x.w.needs and "take" not in x.w.events, "the ledger asks him; the bridge was never taken")
    ok(st["clone"] not in x.w.pool and st.get("bundle"), "its clone went back with its WIP bundled")
    for _ in range(3):
        x.tick()
    ok(x.st("I0")["status"] == "held" and not any(l[0] == "I0" for l in x.w.launches[1:] if "STAGING" in l[2]),
       "and nothing picks it until he lifts the hold")
    x.done()


def t_waits_put_down():
    """Waiting on the bridge holds no clone: parked, and the record says on what."""
    x = rig(1)
    to_game(x, "I0")
    x.w.pool[x.st("I0")["clone"]] = {"idle": 5}
    x.w.idle = "bridge: held by FOUNDRY"
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and st["put_down"]["on"] == "bridge: held by FOUNDRY", "the wait is recorded: %s" % st.get("put_down"))
    ok(st["clone"] not in x.w.pool, "its clone goes back while it waits; the stage makes it again")
    x.done()


def t_stage_remakes_clone():
    """BLUEDESERT_FLORA_PLANT_REFUSAL_1: the stage launched in a clone released while it waited. It is made again."""
    x = rig(1)
    to_game(x, "I0")
    made = []
    x.w.prepare = lambda st: made.append(st["clone"]) or None
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    stage = [l for l in x.w.launches if "STAGING" in l[2]]
    ok(st["game"]["phase"] == "staging" and made == [st["clone"]], "the stage prepares the item's clone first: %s" % made)
    ok(stage and stage[-1][4] == st["clone"] and stage[-1][4] != x.w.books, "and launches in it, never in the books")
    x.done()
    x = rig(1)
    to_game(x, "I0")
    x.w.prepare = lambda st: "clone failed: scratch_clone: no room"
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "stage" and "take" not in x.w.events and "clone: clone failed" in st["put_down"]["on"],
       "a clone that cannot be made is a wait, the bridge untouched: %s" % st.get("put_down"))
    x.done()


def t_one_live_user():
    x = rig(2, share=1.0, max_workers=2)
    to_game(x, "I0")
    to_game(x, "I1")
    x.w.running = False
    for _ in range(3):
        x.tick()
    phases = sorted((x.st(i)["game"] or {}).get("phase") for i in ("I0", "I1") if x.st(i)["status"] == "game")
    ok(phases.count("staging") == 1 and x.w.events.count("take") == 1, "two game items, one bridge user: %s" % phases)
    x.r = dict(x.r, live=dict(x.r["live"], auto=True, round_every_s=0))
    x.tick()
    ok("global_round" not in x.w.events, "the global live round waits while a game phase has the game")
    x.done()


def t_round_only_item():
    import tempfile
    import relentless_live_round as RR
    root = tempfile.mkdtemp(prefix="rlg-")
    os.makedirs(os.path.join(root, "live"))
    with open(os.path.join(root, "live", "runs.jsonl"), "w") as f:
        for i in ("I0", "I1"):
            f.write(json.dumps({"at": "2026-11-02T10:00:00Z", "item": i, "criterion": "A2", "sha": SHA,
                                "outcome": "UNMEASURED", "why": "no running game to test"}) + "\n")

    class Fx:
        def items(self):
            return [{"id": i, "state": "built", "built_sha": SHA, "title": "t", "outstanding": ["A2"],
                     "criteria": [{"id": "A2", "level": "L1", "text": "x"}]} for i in ("I0", "I1")]
        def proofs(self, i): return PROOF
        def foundry_seat(self, i): return False
    now = 1793613600.0 + 600      # ten minutes after the UNMEASURED rows
    todo, counts = RR.plan(Fx(), root, {}, now)
    ok(not todo and counts.get("unmeasured lately") == 2, "the global round waits out a recent UNMEASURED")
    todo, _ = RR.plan(Fx(), root, {}, now, only="I1")
    ok([t[0] for t in todo] == ["I1"], "the game phase's round runs its one item at once, after staging")


def main():
    for t in (t_parse_and_brief, t_pool, t_contract_widens, t_pass_enters_game_and_proves, t_fail_returns,
              t_not_owed_returns, t_gate, t_stage_and_release, t_stage_snag_releases, t_one_live_user, t_round_only_item, t_flyer_put_down, t_waits_put_down,
              t_stage_remakes_clone):
        print("--", t.__name__)
        t()
    print("selftest_relentless_game: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
