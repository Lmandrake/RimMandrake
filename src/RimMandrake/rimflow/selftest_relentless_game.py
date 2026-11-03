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
import time

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
        self.bridge_held = None
        self.started, self.mods = None, 13
        self.books = "/books"
        self.owed = {"A2": "L1"}
        self.title = "a mod thing"
        self.pre, self.pre_calls = [], []        # relentless_live.preflight's answer, and who asked

    def game_preflight(self, item, lines, sites=None):
        self.pre_calls.append((item, dict(lines)))
        return [dict(b) for b in (self.pre(lines) if callable(self.pre) else self.pre)]

    def refusal_print(self, item, criterion, why, proof):
        import relentless_live
        return relentless_live.fingerprint(criterion, why, proof, self.title)

    def game_ledger(self, item):
        return self.led.get(item) or {"state": "doing", "built_sha": None, "title": self.title, "owed": {}}

    def game_implement(self, item, sha, crit, live=None):
        self.impl.append((item, sha, crit))
        self.events.append("implement")
        self.led[item] = {"state": "built", "built_sha": sha, "title": self.title, "owed": dict(self.owed)}

    def proofs_at(self, item, sha, ext=".txt"):
        return self.proofs.get((item, ext), PROOF if ext == ".txt" else "")

    def game_rows(self): return self.rows
    def clone_gap(self, c): return None
    def game_reading(self):
        state = {True: "UP", False: "DOWN"}.get(self.running, self.running)
        return {"state": state, "started": self.started, "mods": self.mods, "evidence": "fake %s" % state}
    def bridge_idle(self, p): return self.idle
    def bridge_reading(self): return dict(self.bridge_held or {"holder": None, "purpose": "", "since": None})

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
    if not st.get("contract"):      # a returned item keeps its contract
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


def t_refused_proof_returns_offline():
    """OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: a line the live lane would refuse goes back at implement, no live row."""
    x = rig(1)
    x.w.proofs[("I0", ".txt")] = 'live-proof A2: python.exe "$(wslpath -w src/RimMandrake/Utils/x.py)" < /dev/null\n'
    to_game(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "game_contract" and "at run time" in st["last_fail"]["detail"]
       and "A2" in st["last_fail"]["detail"], "a $-built live-proof line goes back to a worker before any live run")
    ok(not x.w.rows, "and writes no live run row")
    x.done()


def t_unmeasured_twice_returns_offline():
    """OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: a proof that ran and measured nothing twice on one build goes back to a
    worker; it is not re-proved, nor a reload asked for (one build re-proved 4x, all UNMEASURED)."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    dud = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
           "why": "the proof exited 2: it did not measure: Type not found: X.Y"}
    x.w.rows = [dict(dud)]
    x.tick()
    ok(x.st("I0")["status"] == "game", "one not-measured exit is retried on the game (a busy bridge happens)")
    x.w.rows.append(dict(dud, at="2099-01-01T00:20:00Z"))
    x.w.rows.append(dict(dud, sha="other0000000", at="2099-01-01T00:21:00Z"))
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "game_unmeasured" and "A2" in st["last_fail"]["detail"]
       and "2 times" in st["last_fail"]["detail"] and "Type not found" in st["last_fail"]["detail"],
       "the second goes back to a worker with the proof's last line: %s" % st.get("last_fail"))
    ok(G.not_measuring([dict(dud, why="not deployed: RM_Y")] * 3, "I0", SHA, ["A2"], 2) == {},
       "a staging cause (not deployed) is the restage path, never a proof defect")
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


def staged_then_ended(x, i="I0"):
    """Drive one staging: no game, the stage launches, its worker ends without a ready."""
    st = x.st(i)
    ok(st["game"]["phase"] == "staging", "a staging runs: %s" % st["game"]["phase"])
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    return x.st(i)


def t_tick_reads_windows_tools():
    """The root cause: the systemd tick's PATH has no powershell.exe, so game_started read None while the game ran."""
    import subprocess
    import relentless_live as L
    seen = {}
    real = subprocess.run

    def fake(argv, **kw):
        seen["path"] = (kw.get("env") or {}).get("PATH", "")
        raise OSError("no game here")
    subprocess.run = fake
    old = os.environ.get("PATH")
    os.environ["PATH"] = "/usr/bin:/bin"
    try:
        L.Fx().game_started()
    finally:
        subprocess.run = real
        os.environ["PATH"] = old
    want = [d for d in L.WINDOWS_DIRS if os.path.isdir(d)]
    ok(want and all(d in seen.get("path", "").split(os.pathsep) for d in want),
       "game_started runs powershell with the Windows dirs on PATH, whatever the unit's PATH: %s" % seen)
    ok(R.windows_path is L.windows_path, "one windows_path rule for the tick, the round and game_started")
    import inspect
    ok("windows_path(os.environ" in inspect.getsource(R.tick), "the real tick puts the Windows tools on its own PATH")


def t_loading_is_waited_not_restaged():
    """A cold load in progress is waited out, bounded by the list's size; no stage is spent while it loads."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    staged_then_ended(x)
    x.w.running, x.w.started, x.w.mods = "LOADING", x.now, 13
    takes = x.w.events.count("take")
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and st["game"]["phase"] == "prove" and "loading" in st["put_down"]["on"]
       and x.w.events.count("take") == takes, "loading: put down on the load, no new staging: %s" % st.get("put_down"))
    ok(st["game"]["stages"] == 1 and st["game"]["loading"]["bound"] == G.load_bound(G.cfg(x.r), 13),
       "the bound is the 13-mod list's: %s" % st["game"].get("loading"))
    x.w.mods = 316
    x.now = x.w.started + G.load_bound(G.cfg(x.r), 13) + 60      # past the minimal bound, inside the full list's
    x.tick(0)
    ok(x.st("I0")["game"]["phase"] == "prove" and x.w.events.count("take") == takes,
       "the full list's longer load is still waited")
    x.now = x.w.started + G.load_bound(G.cfg(x.r), 316) + 1
    x.w.running = "LOADING"
    x.tick(0)
    st = x.st("I0")
    ok(st["game"]["stages"] == 2 and x.w.events.count("take") == takes + 1,
       "past its bound the load failed: staged again: %s" % st["game"])
    ok(G.load_bound(G.cfg(x.r), None) == G.cfg(x.r)["load_unknown_s"], "an unread list takes the full list's bound")
    x.done()


def t_failed_staging_is_harness_not_owner():
    """stage_tries stagings with no build running: put down as OUR failure and retried, never held on the owner."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    for _ in range(G.cfg(x.r)["stage_tries"]):
        staged_then_ended(x)
        x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and not st.get("hold"), "not held: %s %s" % (st["status"], st.get("hold")))
    ok(st["game"]["phase"] == "stage" and st["game"]["stages"] == 0 and st["game"]["harness"] == 1
       and st["game"]["retry_at"] > x.now and st["put_down"]["on"].startswith("harness #1"),
       "put down on a harness failure, count reset, retry later: %s" % st["game"])
    ok(any("harness failure, not an owner question" in n for n in x.w.notes), "the ledger note says whose failure")
    x.tick()
    ok(x.w.needs == [] and x.st("I0")["status"] == "game", "nothing routed to the owner: %s" % x.w.needs)
    takes = x.w.events.count("take")
    x.tick()
    ok(x.w.events.count("take") == takes, "no staging before the retry")
    x.now = st["game"]["retry_at"] + 1
    x.tick(0)
    ok(x.st("I0")["game"]["phase"] == "staging" and x.w.events.count("take") == takes + 1, "after it, staged again")
    x.done()


def t_unreadable_game_waits():
    """No reading at all (no Windows tools): a harness wait; never a restart, a stage count or the owner."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = None
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and "take" not in x.w.events and st["game"]["stages"] == 0
       and st["put_down"]["on"].startswith("harness: the game cannot be read"), "unread: %s" % st.get("put_down"))
    x.done()


def t_unhold_game_hold_returns_to_game():
    """The wrongly held: unhold puts a game hold back in its game phase on the same sha, not to a new worker."""
    x = rig(1)
    to_game(x, "I0")
    with x.s.lock():
        st = x.st("I0")
        st["status"] = "held"
        st["game"]["stages"] = 2
        st["hold"] = {"why": "game phase: 2 staging(s) and the build still is not running: no running game",
                      "kind": "game", "delivered": True, "at": x.now}
        x.s.save(st)
    R.unhold(x.s, "I0", "per ruling")
    st = x.st("I0")
    ok(st["status"] == "game" and st["game"]["phase"] == "prove" and st["game"]["stages"] == 0 and not st["hold"],
       "back to its game phase: %s %s" % (st["status"], st["game"]))
    with x.s.lock():
        st = x.st("I0")
        st["status"] = "held"
        st["hold"] = {"why": "game phase: flyer: a flyer's flight", "kind": "game", "delivered": True, "at": x.now}
        x.s.save(st)
    R.unhold(x.s, "I0", "his yes")
    ok(x.st("I0")["status"] == "queued", "a flyer hold keeps the old road")
    x.done()


def t_stage_refuses_a_clone_without_launcher():
    """QUICKTEST_POLICY_NRE_FULLLIST_1: systemd-run failed on a clone missing claude_bounded.sh. The stage checks the
    clone it is about to launch in, after prepare, and takes no bridge when it lacks the launcher."""
    import tempfile
    c = tempfile.mkdtemp(prefix="rlg-clone-")
    os.makedirs(os.path.join(c, ".git"))
    ok(R.Effects({"seat": "BENCH"}, S.Rig(1).s).clone_gap(c) == "src/RimMandrake/Utils/claude_bounded.sh",
       "the real check names the missing launcher")
    x = rig(1)
    to_game(x, "I0")
    x.w.clone_gap = lambda c: "src/RimMandrake/Utils/claude_bounded.sh"
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "stage" and "take" not in x.w.events and not [l for l in x.w.launches if "STAGING" in l[2]]
       and "lacks src/RimMandrake/Utils/claude_bounded.sh" in st["put_down"]["on"],
       "no bridge, no launch, put down on the clone: %s" % st.get("put_down"))
    x.w.clone_gap = lambda c: None
    x.tick()
    ok(x.st("I0")["game"]["phase"] == "staging", "a whole clone stages")
    x.done()


def iso_(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def two_in_prove(x):
    """I0 and I1 both in the game phase, prove, the game UP since x.w.started; I0 tried, I1 not."""
    for i in ("I0", "I1"):
        to_game(x, i)
    x.w.started = x.now - 50
    for i in ("I0", "I1"):
        with x.s.lock():
            st = x.s.load(i)
            st["status"] = "game"
            st["game"].update(phase="prove", entered_at=x.now - 500, staged_at=None, stages=0, proved_at=None)
            st.pop("put_down", None)
            x.s.save(st)
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["proved_at"] = x.now - 20
        x.s.save(st)
    x.w.rows = [{"at": iso_(x.now - 10), "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                 "why": "not in the running load: RM_X (mandrake.rm.x)"}]


def t_running_game_serves_others_before_a_reload():
    """owner 2026-11-02 ("To save game loads"): an item the running game cannot serve waits, bounded, while another game
    item is untried on it; then the one staging carries every waiting item, and they all try the new game."""
    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(st["game"]["phase"] == "prove" and st["game"].get("waits_reload") == x.now and "take" not in x.w.events[-1:]
       and any(a["do"] == "game_batch_wait" and "I1" in a["why"] for a in acts),
       "I0 waits for one reload while I1 is untried: %s %s" % (acts, st["game"]))
    proves = len(x.w.proves)
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)
    ok(len(x.w.proves) == proves + 1 and x.st("I1")["game"]["phase"] == "proving", "the running game serves I1")
    book = json.load(open(x.s.p(G.SESSIONS)))
    e = book[str(int(x.w.started))]
    ok(e["served"] == ["I1"] and e["loads_saved"] == 0, "the session records whom it served: %s" % e)
    G.session_note(x.s, x.w.started, "I9", served=True, now=x.now)
    ok(json.load(open(x.s.p(G.SESSIONS)))[str(int(x.w.started))]["loads_saved"] == 1, "a second item served saves a load")
    # I1 is tried now: I0 stops waiting and stages, carrying I1 if it waits too
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="prove", waits_reload=x.now)
        x.s.save(st)
    x.w.rows.append({"at": iso_(x.now - 5), "item": "I1", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                     "why": "not deployed: RM_Y"})
    x.now += 30
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging" and st["game"]["batch"] == ["I1"]
       and "ONE LOAD FOR ALL" in x.w.launches[-1][2] and "I1" in x.w.launches[-1][2],
       "the staging carries I1 in one load: %s %s" % (acts, st["game"]))
    x.w.up[st["run"]["unit"]] = False
    G.step(x.s, x.w, x.r, "I0", x.now + 60, acts, R)
    G.step(x.s, x.w, x.r, "I0", x.now + 120, acts, R)
    g1 = x.st("I1")["game"]
    ok(g1["phase"] == "prove" and g1["staged_at"] and not g1.get("waits_reload")
       and any(a.get("batch") == ["I1"] for a in acts if a["do"] == "game_staged"),
       "I1 rode the reload and tries the new game: %s" % g1)
    x.done()


def t_batch_wait_is_bounded():
    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["waits_reload"] = x.now - G.cfg(x.r)["batch_wait_s"] - 1
        x.s.save(st)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    ok(x.st("I0")["game"]["phase"] == "staging", "past batch_wait_s it stages even with I1 untried: %s" % acts)
    x.done()


def t_fail_on_a_running_game_is_worked_live():
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.started = x.now - 100
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "FAIL",
                 "log": "/l/A2.log"}]
    x.tick()
    st = x.st("I0")
    li = st.get("live_iter") or {}
    ok(li.get("started") == x.w.started and li.get("clauses") == ["A2"] and li.get("sha") == SHA,
       "a FAIL with the game up: the worker iterates on it: %s" % li)
    x.run_one("I0")
    st = x.st("I0")
    ok(st.get("live_iter") and "LIVE:" in x.w.launches[-1][2] and "reload-needed" in x.w.launches[-1][2],
       "the worker brief says work it live, prove the reload")
    ok(G.other_active([st, {"item": "I7", "status": "game", "game": {}}], "I7") == "I0",
       "a live-iterating worker is the game's one live user")
    try:
        R.reload_needed(x.s, "I0", st["gen"], "")
        ok(False, "reload-needed without its proof is refused")
    except ValueError:
        ok(True, "reload-needed without its proof is refused")
    R.reload_needed(x.s, "I0", st["gen"], "the fix is in the C# assembly; a DLL loads only cold", now=x.now)
    st = x.st("I0")
    ok(not st.get("live_iter") and "DLL" in st["reload_needed"]["why"]
       and G.other_active([st], "I7") is None, "its proof is recorded and the game is free")
    e = json.load(open(x.s.p(G.SESSIONS)))[str(int(x.w.started))]
    ok("I0" in e["reload_needed"], "the session records the reload it needs: %s" % e)
    x.done()


def live_iterating(x, i="I0"):
    """I0 FAILed on the running game and its worker now iterates on it (live_iter)."""
    to_game(x, i)
    x.tick()
    x.tick()
    x.w.started = x.now - 100
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": i, "criterion": "A2", "sha": SHA, "outcome": "FAIL",
                 "log": "/l/A2.log"}]
    x.tick()
    x.run_one(i)
    ok(x.st(i).get("live_iter") and x.st(i)["status"] == "running", "%s iterates live" % i)


def held(x, i="I0"):
    return G.other_active(x.s.states() + [{"item": "I7", "status": "game", "game": {}}], "I7") == i


def t_idle_live_hold_lapses():
    """RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER: a live-iterating worker that leaves the bridge free for live_idle_s no longer
    holds the game (2026-11-03: ATMOSBASE held it 47 min, bridge free, ten items waiting). Red on the old code: the
    hold lasted as long as the worker."""
    x = rig(1)
    live_iterating(x)
    x.r = dict(x.r, game=dict(x.r.get("game") or {}, live_idle_s=600))     # inside the worker's run_max_s
    idle = G.cfg(x.r)["live_idle_s"]
    gen = x.st("I0")["gen"]
    x.w.bridge_held = {"holder": "BENCH", "purpose": "relentless live iteration I0", "since": x.now}
    R.beat(x.s, "I0", gen, now=x.now + idle - 60)
    x.tick(idle - 60)
    R.beat(x.s, "I0", gen, now=x.now + idle - 60)
    x.tick(idle - 60)
    ok(held(x), "a worker that drives the bridge for its item keeps the game past live_idle_s")
    x.w.bridge_held = {"holder": "BENCH", "purpose": "someone else's look at I7", "since": x.now}
    R.beat(x.s, "I0", gen, now=x.now + 120)
    x.tick()
    ok(held(x), "within live_idle_s of its last bridge use it still holds")
    R.beat(x.s, "I0", gen, now=x.now + idle)
    x.tick(idle)
    st = x.st("I0")
    ok(not held(x) and st["status"] == "running" and not st.get("live_iter") and st.get("live_lapsed"),
       "bridge not held for it for live_idle_s: the hold lapses, the worker runs on offline: %s" % st.get("live_lapsed"))
    ok(any(j.get("do") == "game_hold_released" and j.get("item") == "I0" and "bridge" in j.get("why", "")
           for j in map(json.loads, open(x.s.p("journal.jsonl")))), "the release is journaled with its reason")
    ok("hold lapsed" in x.s.learned("I0"), "the item's record says the hold lapsed")
    R.reload_needed(x.s, "I0", gen, "the fix is a DLL; only a cold load reads it", now=x.now)
    ok("DLL" in x.st("I0")["reload_needed"]["why"], "reload-needed after a lapse still records its proof")
    x.done()


def t_live_hold_lapses_when_its_game_is_gone():
    x = rig(1)
    live_iterating(x)
    x.w.bridge_held = {"holder": "BENCH", "purpose": "relentless live iteration I0", "since": x.now}
    x.w.started = x.now + 5         # another load: not the game that showed the FAIL
    x.tick()
    ok(not held(x) and "no longer runs" in (x.st("I0").get("live_lapsed") or {}).get("why", ""),
       "a different game than the one that failed: the hold lapses")
    x.done()


def t_dead_prove_pid_frees_the_game():
    """stale_holds is pure: a proving holder whose pid is dead is named, a live one is not."""
    c = G.cfg({})
    st = [{"item": "P", "status": "game", "game": {"phase": "proving", "prove_pid": 41}}]
    ok(G.stale_holds(st, 1e6, c, lambda p: False, dict, dict)[0][:2] == ("P", "proving"), "dead prove pid: stale")
    ok(G.stale_holds(st, 1e6, c, lambda p: True, dict, dict) == [], "running prove pid: still holds")
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    with x.s.lock():
        s = x.s.load("I0")
        s["game"].update(phase="proving", prove_pid=777)
        x.s.save(s)
    acts = []
    G.lapse_holds(x.s, x.w, x.r, x.now, acts)
    ok(x.st("I0")["game"]["phase"] == "prove" and acts and acts[0]["kind"] == "proving",
       "lapse_holds frees a proving holder whose pid is dead before any step runs: %s" % acts)
    x.done()


def t_fail_with_no_game_is_offline():
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.running = False
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "FAIL",
                 "log": "/l/A2.log"}]
    x.tick()
    ok(not x.st("I0").get("live_iter"), "no game up: no live iteration")
    x.done()


def t_stage_tries_a_newer_running_game_first():
    """An item put to stage (its game read DOWN while another item's staging restarted it) tries the game that came up
    before it stages a load of its own; a row from that game sends it on to stage."""
    x = rig(1)
    to_game(x, "I0")
    with x.s.lock():
        st = x.s.load("I0")
        st["game"].update(phase="stage", staged_at=x.now - 400, entered_at=x.now - 500, proved_at=x.now - 450)
        x.s.save(st)
    x.w.started = x.now - 60
    x.w.rows = []
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    g = x.st("I0")["game"]
    ok(g["phase"] == "prove" and g["staged_at"] == x.w.started and "take" not in x.w.events
       and any(a["do"] == "game_try_running" for a in acts), "no row from the running game: try it first: %s" % acts)
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["phase"] = "stage"
        x.s.save(st)
    x.w.rows = [{"at": iso_(x.now - 10), "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                 "why": "not in the running load: RM_X (mandrake.rm.x)"}]
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    ok(x.st("I0")["game"]["phase"] == "staging", "a row from the running game: it stages: %s" % acts)
    x.done()


FINAL_GAME = {"clauses": ["A1", "F1"], "why": "A1 on the smallest list; F1 is the full-list final verification"}
FINAL_PROOF = ("live-proof A1: python.exe src/RimMandrake/Utils/northstar_driver/cli.py needs-mods --mod Graffiti\n"
               "live-proof F1: python.exe src/RimMandrake/Utils/northstar_driver/cli.py running-list\n")


def two_final(x):
    """I0 and I1 in prove; on the running (small) game each A1 PASSed and each F1 read FINAL_WAIT."""
    x.w.owed = {"A1": "L1", "F1": G.FINAL_LEVEL}
    for i in ("I0", "I1"):
        x.w.proofs[(i, ".txt")] = FINAL_PROOF
        to_game(x, i, game=FINAL_GAME)
    x.w.started = x.now - 50
    for i in ("I0", "I1"):
        with x.s.lock():
            st = x.s.load(i)
            st["status"] = "game"
            st["game"].update(phase="prove", entered_at=x.now - 500, staged_at=None, stages=0, proved_at=x.now - 40)
            x.s.save(st)
        x.w.led[i] = {"state": "built", "built_sha": SHA, "title": x.w.title, "owed": dict(x.w.owed)}
    x.w.rows = [r for i in ("I0", "I1") for r in (
        {"at": iso_(x.now - 30), "item": i, "criterion": "A1", "sha": SHA, "outcome": "PASS"},
        {"at": iso_(x.now - 30), "item": i, "criterion": "F1", "sha": SHA, "outcome": "UNMEASURED",
         "why": G.FINAL_WAIT + ": the running game holds 23 of 316"})]


def t_final_verification_waits_and_batches():
    """PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS (owner 2026-11-02: "small mod lists should always be the way to test
    until a final verification pass on the whole huge mod list"): an item whose small clauses PASS and whose GREEN-FULL
    clause waits for the full list holds nothing and stages nothing on its own; a newer game gets one try; the oldest
    stages ONE full-list load that carries every waiting final."""
    x = rig(2, share=1.0, max_workers=2)
    two_final(x)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    x.now += 1
    G.step(x.s, x.w, x.r, "I1", x.now, acts, R)
    ok([x.st(i)["game"]["phase"] for i in ("I0", "I1")] == ["final", "final"]
       and sum(a["do"] == "game_final_wait" for a in acts) == 2 and "take" not in x.w.events,
       "small clauses PASS, the final waits: phase final, no take, no stage: %s" % acts)
    proves = len(x.w.proves)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now + 60, acts, R)
    ok(x.st("I0")["game"]["phase"] == "final" and not acts and "take" not in x.w.events and len(x.w.proves) == proves,
       "below final_batch_min and inside final_wait_s: it keeps waiting, holding nothing, proving nothing")
    # a game started since (another item's load, or his): one try on it, no load
    x.w.started = x.now + 100
    acts = []
    G.step(x.s, x.w, x.r, "I1", x.now + 200, acts, R)
    ok(x.st("I1")["game"]["phase"] == "prove" and any(a["do"] == "game_final_try_running" for a in acts),
       "a newer game: the final tries it once: %s" % acts)
    for i in ("I0", "I1"):      # both tried the newer game and still wait for the full list
        with x.s.lock():
            st = x.s.load(i)
            st["game"].update(phase="final", final_game=x.w.started)
            x.s.save(st)
        x.w.rows.append({"at": iso_(x.w.started + 5), "item": i, "criterion": "F1", "sha": SHA, "outcome": "UNMEASURED",
                         "why": G.FINAL_WAIT})
    # the bound: the oldest final stages one full-list load carrying the batch
    t = x.now + G.DEFAULTS["final_wait_s"] + 10
    acts = []
    G.step(x.s, x.w, x.r, "I1", t, acts, R)
    ok(x.st("I1")["game"]["phase"] == "final" and not acts, "only the oldest final stages")
    G.step(x.s, x.w, x.r, "I0", t, acts, R)
    g0 = x.st("I0")["game"]
    ok(g0["phase"] == "staging" and g0.get("full") and g0["batch"] == ["I1"]
       and any(a["do"] == "game_final_stage" and a["batch"] == ["I0", "I1"] for a in acts),
       "the oldest stages one full load with the batch: %s %s" % (acts, g0))
    ok("FINAL VERIFICATION" in x.w.launches[-1][2] and "FULL.LATEST" in x.w.launches[-1][2],
       "the staging prompt asks for the whole full list")
    x.w.up[x.st("I0")["run"]["unit"]] = False
    G.step(x.s, x.w, x.r, "I0", t + 60, acts, R)
    G.step(x.s, x.w, x.r, "I0", t + 120, acts, R)
    ok(x.st("I1")["game"]["phase"] == "prove" and not x.st("I0")["game"].get("full"),
       "I1 rode the full load; the full flag ends with the staging: %s" % x.st("I1")["game"])
    # a small staging never carries a waiting final
    st = {"item": "I9", "status": G.GAME, "game": {"phase": "final"}}
    ok(G.batch([st], "I0", t) == [] and G.batch([st], "I0", t, full=True) == [st], "batch: finals ride only a full load")
    x.done()


def t_owed_final_joins_the_clauses():
    """A contract written before the tier rule names A1 only; the criteria file owes F1 GREEN-FULL with a proof line:
    F1 joins the game clauses at implement, so the item cannot wait on it forever."""
    x = rig(1)
    x.w.owed = {"A1": "L1", "F1": G.FINAL_LEVEL, "Z9": G.FINAL_LEVEL}
    x.w.proofs[("I0", ".txt")] = FINAL_PROOF
    to_game(x, "I0", game={"clauses": ["A1"], "why": "small"})
    x.tick()
    g = x.st("I0")["game"]
    ok(g["phase"] == "prove" and g["clauses"] == ["A1", "F1"], "F1 joins, Z9 (no proof line) does not: %s" % g)
    x.done()


CUT = {"cid": "A2", "why": "I0 A2 is cut at 160 chars on the ledger and no prose holds the rest", "fp": "fpA",
       "kind": "refused"}


def t_refusal_returns_once_then_holds():
    """LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD + LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT: a clause the live lane would refuse
    whatever the game does goes back at implement, before any prove round or staging; back again with nothing a worker
    could change (same fingerprint) it is held with the reason; a changed criterion text is a new fingerprint."""
    x = rig(1)
    x.w.pre = [CUT]
    to_game(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "game_contract" and "cut at 160" in st["last_fail"]["detail"],
       "a cut criterion goes back at implement: %s" % st.get("last_fail"))
    ok(not x.w.proves and "take" not in x.w.events and not x.w.rows, "and spends no prove round, bridge or row")
    ok("fpA" in (st.get("refused_fps") or {}), "its fingerprint is kept")
    to_game(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and "refused again unchanged" in st["hold"]["why"] and "cut at 160" in st["hold"]["why"],
       "back with the same fingerprint: held with the reason, no second worker round: %s" % st.get("hold"))
    ok(not x.w.proves, "still no prove round")
    x.done()
    y = rig(1)
    y.w.pre = [CUT]
    to_game(y, "I0")
    y.tick()
    y.w.pre = [dict(CUT, fp="fpB")]      # the worker changed the criterion: the refusal is a new one
    to_game(y, "I0")
    y.tick()
    ok(y.st("I0")["status"] != "held" and y.st("I0")["last_fail"]["class"] == "game_contract",
       "a changed text is a new refusal: back again, not held")
    y.w.pre = []
    to_game(y, "I0")
    y.tick()
    ok(y.st("I0")["game"]["phase"] == "prove", "fixed: on to the prove phase")
    y.done()


def t_retiered_criteria_are_rerecorded():
    """GRAFFITI_NORTHSTAR_GREEN_FULL_1: the ledger held an older criterion under the id; a recorded build re-records the
    criteria file once before judging, and a clean preflight after it goes on to prove."""
    x = rig(1)
    retier = dict(CUT, why="I0 A2 is cut at 160 chars on the ledger and the item's criteria now say something else "
                           "under that id (re-tiered): re-record them")
    x.w.led["I0"] = {"state": "built", "built_sha": SHA, "title": x.w.title, "owed": dict(x.w.owed)}
    x.w.pre = lambda lines: [retier] if len(x.w.impl) < 1 else []
    to_game(x, "I0")
    x.tick()
    acts = [a for a in x.w.impl]
    ok(len(acts) == 1 and x.st("I0")["game"]["phase"] == "prove",
       "a re-tiered criterion is re-recorded, then the item proves: impl %s phase %s" % (acts, x.st("I0")["game"]["phase"]))
    x.done()


def t_stale_build_caught_before_a_slot():
    """LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT: a game file of the build changed in a later commit: no staging load and no
    prove round can run that sha, so it goes back to be rebuilt before either is spent."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    ok(x.st("I0")["game"]["phase"] == "prove", "implemented, clean")
    x.w.pre = [{"cid": None, "why": "changed since the built commit, so the game cannot run sha1: a.xml (c0ffee)",
                "fp": "fpS", "kind": "stale"}]
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "game_stale_build" and "c0ffee" in st["last_fail"]["detail"],
       "a stale build goes back before the staging load: %s" % st.get("last_fail"))
    ok("take" not in x.w.events and not x.w.proves, "no bridge take, no staging, no prove round")
    x.done()
    y = rig(1)
    to_game(y, "I0")
    y.tick()
    y.w.pre = [{"cid": None, "why": "changed since the built commit, so ...", "fp": "fpS", "kind": "stale"}]
    y.tick()
    ok(not y.w.proves and y.st("I0")["last_fail"]["class"] == "game_stale_build", "and before a prove round")
    y.done()


def t_dead_rows_go_back():
    """A stale-build row or a defect row (the same cause on two games) decides its build: the item goes back once with
    the row's reason instead of being proved every 15 minutes and reloaded every third run."""
    for row, klass in (({"why": "changed since the built commit, so the game cannot run sha1: a (b)"}, "game_stale_build"),
                       ({"why": "proof or site defect: the same cause on the game of G1 and on this one (G2)",
                         "defect": True}, "game_proof_unmeasured")):
        x = rig(1)
        to_game(x, "I0")
        x.tick()
        x.tick()
        ok(x.w.proves == ["I0"], "proving")
        x.w.rows = [dict({"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA,
                          "outcome": "UNMEASURED", "proof": "python3 p.py"}, **row)]
        x.tick()
        st = x.st("I0")
        ok(st["last_fail"] and st["last_fail"]["class"] == klass, "%s row goes back: %s" % (klass, st.get("last_fail")))
        ok(x.w.proves == ["I0"], "no second prove round on it")
        x.done()


def main():
    for t in (t_parse_and_brief, t_pool, t_contract_widens, t_pass_enters_game_and_proves, t_fail_returns,
              t_not_owed_returns, t_refused_proof_returns_offline, t_unmeasured_twice_returns_offline, t_gate, t_stage_and_release, t_stage_snag_releases, t_one_live_user, t_round_only_item, t_flyer_put_down, t_waits_put_down,
              t_stage_remakes_clone, t_tick_reads_windows_tools, t_loading_is_waited_not_restaged,
              t_failed_staging_is_harness_not_owner, t_unreadable_game_waits, t_unhold_game_hold_returns_to_game,
              t_stage_refuses_a_clone_without_launcher, t_running_game_serves_others_before_a_reload,
              t_batch_wait_is_bounded, t_fail_on_a_running_game_is_worked_live, t_fail_with_no_game_is_offline,
              t_stage_tries_a_newer_running_game_first,
              t_final_verification_waits_and_batches, t_owed_final_joins_the_clauses,
              t_refusal_returns_once_then_holds, t_retiered_criteria_are_rerecorded, t_stale_build_caught_before_a_slot,
              t_dead_rows_go_back, t_idle_live_hold_lapses, t_live_hold_lapses_when_its_game_is_gone,
              t_dead_prove_pid_frees_the_game):
        print("--", t.__name__)
        t()
    print("selftest_relentless_game: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
