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
`--pre-recarry` turns relentless_game.recarry_returned off: a queued stale return whose carry now answers then waits for
a worker, as SUMP_TAR_FIRE_NETWORK_1 did (t_rebuilt_assembly_carries_the_build goes red).
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
        self.no_code = []
        self.running, self.idle, self.take_why, self.palive = True, None, None, set()
        self.proofs = {}
        self.bridge_held = None
        self.batch_plans = []
        self.started, self.mods = None, 13
        self.books = "/books"
        self.owed = {"A2": "L1"}
        self.title = "a mod thing"
        self.pre, self.pre_calls = [], []        # relentless_live.preflight's answer, and who asked
        self.carry, self.carry_calls = None, []     # relentless_live.carry's answer, and who asked
        self.gap, self.gap_calls, self.enabled, self.enable_why = {}, [], [], None     # relentless_live_round.mod_gap

    def game_preflight(self, item, lines, sites=None):
        self.pre_calls.append((item, dict(lines)))
        return [dict(b) for b in (self.pre(lines) if callable(self.pre) else self.pre)]

    def refusal_print(self, item, criterion, why, proof):
        import relentless_live
        return relentless_live.fingerprint(criterion, why, proof, self.title)

    def game_ledger(self, item):
        return self.led.get(item) or {"state": "doing", "built_sha": None, "title": self.title, "owed": {}}

    def game_carry(self, item, sha):
        self.carry_calls.append((item, sha))
        return self.carry(sha) if callable(self.carry) else self.carry

    def game_implement(self, item, sha, crit, live=None, why=None, no_code=None):
        self.impl.append((item, sha, crit))
        self.no_code.append(no_code)
        self.events.append("implement")
        self.led[item] = {"state": "built", "built_sha": sha, "title": self.title, "owed": dict(self.owed),
                          "criteria": {k: dict(c) for k, c in (getattr(self, "crit", None) or {}).items()}}

    def proofs_at(self, item, sha, ext=".txt"):
        return self.proofs.get((item, ext), PROOF if ext == ".txt" else "")

    def game_trees(self, builds):
        import relentless_live_round as R
        got = sorted({m for i, s in builds for m in R.live_deploy(self.proofs_at(i, s))})
        return (got, R.deploy_args(got, {})) if got else None

    def game_mod_gap(self, item, sha, running=True):
        self.gap_calls.append((item, sha, running))
        g = dict(self.gap.get(item) or {"mods": ["RM_X"]})
        if not running:
            g.pop("running", None)
        return g

    def game_batch_gap(self, builds):
        self.batch_plans.append(list(builds))
        gs = [self.game_mod_gap(i, s, running=False) for i, s in builds]
        return {"mods": sorted({m for g in gs for m in g.get("mods") or []}),
                "dll": sorted({d for g in gs for d in g.get("dll") or []})}

    # SteveDesktop through testq (relentless_game.steve_sync): every call recorded, the queue a dict
    def steve_deploy(self, item, sha):
        return list(getattr(self, "steve_mods", []))

    def testq_submit(self, item, sha, tier, clauses, deploy):
        self.events.append("testq_submit:%s:%s:%s" % (item, tier, ",".join(clauses)))
        if getattr(self, "submit_why", None):
            return None, self.submit_why
        self.testq = getattr(self, "testq", {})
        jid = "J20261106T000000Z-%06x" % (len(self.testq) + 1)
        self.testq[jid] = {"state": "pending", "rec": None, "gate": None,
                           "job": {"id": jid, "item": item, "profile": "tier:" + tier, "lane": "stevedesktop",
                                   "selector": {"proofs": list(clauses)}, "source_sha": sha, "deploy": list(deploy)}}
        return jid, None

    def testq_job(self, job):
        return dict(getattr(self, "testq", {}).get(job) or {"state": None, "rec": None, "gate": None})

    def steve_verify(self, item, criterion, level, sha, result, evidence, config):
        self.events.append("verify:%s:%s:%s" % (item, criterion, result))
        return None

    def game_row_append(self, row):
        self.rows.append(row)

    def modlist_enable(self, mods):
        self.enabled.append(list(mods))
        self.events.append("enable")
        return self.enable_why

    def game_rows(self): return self.rows
    def clone_gap(self, c): return None
    def game_reading(self):
        state = {True: "UP", False: "DOWN"}.get(self.running, self.running)
        return {"state": state, "started": self.started, "mods": self.mods, "evidence": "fake %s" % state}
    def bridge_idle(self, p): return self.idle
    def load_stall_evidence(self): return getattr(self, "stall", None)
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
    if st.get("warrant_owed"):    # a retry states its warrant (CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT)
        R.learn(x.s, i, st["gen"], "WARRANT: the mod now sets the comp | A3 still 0 means the binding, not the mod")
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


def t_nocode_rebuild_reaches_implemented():
    """step -> GameFx.game_implement: a ledger-only candidate carries --no-code only under a structured unchanged warrant
    of its own generation (RELENTLESS_NOCODE_REBUILD_IMPLEMENTED_REFUSED, review of 930b960a8e)."""
    for warrant, touched, want in (
            ({"unchanged": True, "changed": "UNCHANGED: required_checks.json moved"}, ["infrastructure/state/items/I0.md"],
             True),
            ({"changed": "nothing in the work changed except the cooldown fix"}, ["infrastructure/state/items/I0.md"],
             False),
            ({"unchanged": True, "changed": "UNCHANGED: env"}, ["src/RimMandrake/ModA/Defs/A.xml"], False)):
        x = rig(1)
        to_game(x, "I0")
        with x.s.lock():
            st = x.s.load("I0")
            st["warrant"] = dict(warrant, gen=(st.get("candidate") or {}).get("gen"))
            x.s.save(st)
        x.w.touched = lambda sha, t=touched: list(t)
        x.tick()
        ok(len(x.w.impl) == 1 and bool(x.w.no_code and x.w.no_code[0]) == want,
           "warrant %r, touched %s: --no-code %s (%r)" % (warrant.get("changed"), touched, want,
                                                          x.w.no_code[:1]))
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
    ok(st["gen"] == 1 and not st["failures"].get("game_fail") and (st.get("wait") or {}).get("kind") == "attribution",
       "an unattributed FAIL on the game earns no strike and no worker: %s" % st.get("wait"))
    S.blame_product(x, "I0")
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
    ok(st["last_fail"] and st["last_fail"]["class"] == "proof_owed" and "game_contract" in st["last_fail"]["detail"]
       and st.get("proof_only"), "a game clause owed at L0 is no game clause: the proof road (CONTRACT), not the code")
    x.done()


def t_refused_proof_returns_offline():
    """OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU: a line the live lane would refuse goes back at implement, no live row."""
    x = rig(1)
    x.w.proofs[("I0", ".txt")] = 'live-proof A2: python.exe "$(wslpath -w $HOME/x.py)" < /dev/null\n'
    to_game(x, "I0")
    x.tick()
    st = x.st("I0")
    ok(st["last_fail"] and st["last_fail"]["class"] == "proof_owed" and "at run time" in st["last_fail"]["detail"]
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
    gen = x.st("I0")["gen"]
    x.tick()
    st = x.st("I0")
    # UNMEASURED_LANE_REWIRE_STOP_REBUILDING_SITES: the proof's dud is routed once to one fixer, never a worker
    ok(st["status"] == "held" and st["hold"]["kind"] == "game" and not st.get("last_fail") and st["gen"] == gen
       and "A2" in st["hold"]["why"] and "2 times" in st["hold"]["why"] and "Type not found" in st["hold"]["why"],
       "the second is routed once to one fixer with the proof's last line, no worker: %s" % st.get("hold"))
    ok(G.not_measuring([dict(dud, why="not deployed: RM_Y")] * 3, "I0", SHA, ["A2"], 2) == {},
       "a staging cause (not deployed) is the restage path, never a proof defect")
    x.done()


def t_cap_returns_with_the_exit_reason_and_log():
    """PROOF_RERUNS_TAME_UNMEASURED_REPEATS: a defect row on its first run goes back to a worker carrying the reason and
    the log; back again with the same cause it is held; a fixed proof hitting a NEW cause on the same proof line is not
    "unchanged" (before, the defect's head filled the fingerprint's cause, so it was)."""
    import relentless_live
    def defect(reason):
        why = "the proof exited 2: it did not measure: " + reason
        return {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                "proof": "python.exe probe.py", "log": "/l/I0-A2.log", "defect": True, "cause": relentless_live.cause(why),
                "why": "%s: the proof's own call is broken, so a rerun or a reload cannot help: %s" % (relentless_live.DEFECT, why)}
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [defect("No public static CleanRead with 0 params")]
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and st["hold"]["kind"] == "game" and not st.get("last_fail")
       and "proof_call" in st["hold"]["why"] and "CleanRead" in st["hold"]["why"] and "/l/I0-A2.log" in st["hold"]["why"],
       "one defect row is routed at once to one fixer, with the reason and the log, no worker: %s" % st.get("hold"))
    first = sorted(st.get("env_routed") or {})
    ok(len(first) == 1, "the route is remembered: %s" % first)
    x.done()
    rows = [defect("No public static CleanRead with 0 params"), defect("Type not found: Foo")]
    fps = {relentless_live.fingerprint(v["criterion"], v["why"], v["proof"], "") for v in rows}
    ok(len(fps) == 2, "a new cause on the same proof line is a new return, not a hold")
    dud = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
           "log": "/l/d.log", "why": "the proof exited 2: it did not measure: x"}
    ok("/l/d.log" in G.not_measuring([dud, dud], "I0", SHA, ["A2"], 2)["A2"][1], "a plain dud's return names its log too")


def t_dud_on_this_game_returns_at_once():
    """LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: the round no longer reruns a dud on the game and build it ran on, so a
    single dud on THIS game, with nothing else left to measure here, goes back to a worker at once instead of waiting."""
    import relentless_live
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.started = x.now - 3000.0
    dud = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
           "log": "/l/here.log", "why": "the proof exited 2: it did not measure: Type not found: X.Y",
           "game": relentless_live.iso(1.0)}
    x.w.rows = [dict(dud)]
    x.tick()
    ok(x.st("I0")["status"] == "game", "a dud from another game is retried on this one")
    x.w.rows = [dict(dud, game=relentless_live.iso(x.w.started))]
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and not st.get("last_fail") and "this game and build" in st["hold"]["why"]
       and "Type not found" in st["hold"]["why"],
       "one dud on this game and build is routed at once, no worker: %s" % st.get("hold"))
    ok("/l/here.log" in st["hold"]["why"], "that route names the log too: %s" % st["hold"])
    ok(G.blocked_here({"A2": dict(dud, game=relentless_live.iso(x.w.started), why="bridge not taken: busy")}, ["A2"],
                      SHA, x.w.started, x.now) == {}, "a transient that is not a dud never sends it back")
    x.done()


def t_long_reason_survives_both_unmeasured_returns():
    """PROOF_RERUNS_TAME_UNMEASURED_REPEATS: the log now comes first in the line, so a cut sized for a bare reason would
    take the reason's end. Both game_unmeasured returns must hand the worker the whole of a long reason, and the log."""
    import relentless_live
    reason = "the proof exited 2: it did not measure: " + "x" * 300 + " THE_END_OF_THE_REASON"
    dud = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
           "log": "/l/long.log", "why": reason}

    def seen(st):
        d = (st.get("hold") or {})
        return st["status"] == "held" and "THE_END_OF_THE_REASON" in (d.get("why") or "") \
            and "/l/long.log" in (d.get("why") or "")
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.rows = [dict(dud), dict(dud, at="2099-01-01T00:20:00Z")]
    x.tick()
    ok(seen(x.st("I0")), "the ran-N-times route keeps the end of a long reason: %s" % x.st("I0").get("hold"))
    x.done()
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    x.w.started = x.now - 3000.0
    x.w.rows = [dict(dud, game=relentless_live.iso(x.w.started))]
    x.tick()
    ok(seen(x.st("I0")), "the this-game-and-build route keeps the end of a long reason: %s" % x.st("I0").get("hold"))
    x.done()


def t_stage_idle_releases():
    """LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: a staging worker whose game has been UP stage_idle_s since it started
    the load is done in all but name; the supervisor ends it and releases the bridge instead of holding to stage_max_s."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging", "staging")
    x.w.running = True
    x.w.started = st["game"]["staged_at"] - 50.0      # a game from before the staging: not this staging's load
    x.tick()
    ok("release" not in x.w.events, "a game older than the staging does not end it")
    x.w.started = st["game"]["staged_at"] + 10.0      # the load this staging started
    x.tick(dt=100)
    ok("release" not in x.w.events, "a fresh load not yet idle long: the worker keeps the bridge")
    x.tick(dt=600)
    x.tick()
    ok("release" in x.w.events and x.st("I0")["game"]["phase"] in ("prove", "proving"),
       "UP 600 s on its load: the staging ends and the bridge is released: %s" % x.w.events[-4:])
    x.done()


def t_stage_max_stops_before_quarantine():
    """LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT: a staging that reaches stage_max_s is STOPPED first; settle's quarantine
    clock runs from that stop, not from staged_at (ART_OVERRIDE_FAMILY_SCRIPT_1's unit was quarantined unstopped)."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging", "staging")
    unit = st["run"]["unit"]
    x.w.unkillable.add(unit)
    x.tick(dt=G.DEFAULTS["stage_max_s"] + 10)
    st = x.st("I0")
    ok(not st["quarantined"] and any(u == unit for u, _ in x.w.stops),
       "past stage_max_s: the unit is stopped, not quarantined unstopped: stops %s quarantined %s"
       % (x.w.stops, st["quarantined"]))
    x.tick(dt=x.r["stop_quarantine_s"] + 10)
    st = x.st("I0")
    ok(st["quarantined"] and st["game"]["phase"] in ("prove", "proving") and "release" in x.w.events,
       "still alive stop_quarantine_s after the stop: quarantined, the bridge released")
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
    ok(G.gate(st, "Gravship flying down to the floor and back up", PROOF, fl, None) is None, "a gravship is no flyer")
    ok("flyer" in (G.gate(st, "Mynock flying around the gravship", PROOF, fl, None) or ""), "a creature on a gravship is")
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
    ok(G.flyer_hold(st["hold"]["why"]) and R.hold_is_his(st["hold"]), "the words the writer really uses read as his: %s" % st["hold"]["why"])
    ok("I0" in x.w.needs and "take" not in x.w.events, "the ledger asks him; the bridge was never taken")
    ok(st["clone"] not in x.w.pool and st.get("bundle"), "its clone went back with its WIP bundled")
    for _ in range(3):
        x.tick()
    ok(x.st("I0")["status"] == "held" and not any(l[0] == "I0" for l in x.w.launches[1:] if "STAGING" in l[2]),
       "and nothing picks it until he lifts the hold")
    x.done()


L4_LOOK = ("live-proof L4: python3 -c \"import json,sys; ev=[json.loads(l) for l in "
           "open('infrastructure/state/ledger/events/OWNER.jsonl') if 'I0' in l]; sys.exit(0 if ev else 1)\"\n")


def t_owner_look_skipped_routes_owner():
    """RELENTLESS_FIX_GAME_LANE_OWNER_LOOK_FAILS: WATER_DEPTH_RESKIN_HE_LOOKS_FIRST bound L4 ("the owner has looked at the
    one review and kept it", filed at L2, its proof a read of OWNER.jsonl) as a game clause and bounced 4 times on a
    check only he can pass. His look is never a game clause: implement does not send it back, the round never runs it,
    and once every game clause PASSes the item is held on him (needs=owner), no game_fail and no worker."""
    for proof_reads_ledger in (True, False):
        x = rig(1)
        x.w.owed = {"A2": "L1", "L4": "L2"}
        x.w.crit = {"A2": {"id": "A2", "level": "L1", "text": "the comp loads"},
                    "L4": {"id": "L4", "level": "L2", "text": "the owner has looked at the one review (with X) and kept "
                           "it - an OWNER ledger event on this item after 2026-11-03."}}
        x.w.proofs[("I0", ".txt")] = PROOF + (L4_LOOK if proof_reads_ledger else
                                              "live-proof L4: python.exe src/RimMandrake/Utils/shot.py --out x.png\n")
        to_game(x, "I0", game={"clauses": ["A2", "L4"], "why": "A2 needs the loaded defs; L4 is his look"})
        x.tick()
        st = x.st("I0")
        ok(st["status"] == "game" and st["game"]["phase"] == "prove" and not st.get("last_fail"),
           "proof reads ledger %s: his look does not send the item back at implement: %s %s" % (
               proof_reads_ledger, st["status"], st.get("last_fail")))
        ok(st["game"]["clauses"] == ["A2"] and st["game"].get("owner_clauses") == ["L4"],
           "L4 leaves the game clauses and is kept as his: %s" % st["game"])
        ok(all("L4" not in lines for _i, lines in x.w.pre_calls), "the preflight never sees his line: %s" % x.w.pre_calls)
        x.tick()
        ok(x.w.proves == ["I0"], "the round runs for the game's own clause")
        x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "PASS"}]
        x.w.led["I0"]["owed"] = {"L4": "L2"}        # the A2 verify landed; his look is all that is owed
        x.tick()
        st = x.st("I0")
        ok(st["status"] == "held" and G.owner_look_hold(st["hold"]["why"]) and R.hold_is_his(st["hold"])
           and "L4" in st["hold"]["why"], "every game clause PASSed: held on his look: %s %s" % (st["status"], st.get("hold")))
        ok(not st["failures"].get("game_fail") and (st.get("last_fail") or {}).get("class") != "game_fail",
           "no game_fail, no strike")
        x.tick()
        ok("I0" in x.w.needs, "the ledger routes it to him (needs=owner)")
        launches = len(x.w.launches)
        for _ in range(3):
            x.tick()
        ok(x.st("I0")["status"] == "held" and len(x.w.launches) == launches, "and no worker is sent while he has not looked")
        x.done()
    # a state from before the fix still names his look among its game clauses: the prove phase takes it out
    x = rig(1)
    x.w.owed = {"A2": "L1", "L4": "L2"}
    x.w.crit = {"L4": {"id": "L4", "level": "L2", "text": "the owner has looked at the one review and kept it"}}
    x.w.proofs[("I0", ".txt")] = PROOF + L4_LOOK
    to_game(x, "I0")
    x.tick()
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["clauses"] = ["A2", "L4"]
        x.s.save(st)
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "PASS"},
                {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "L4", "sha": SHA, "outcome": "FAIL",
                 "log": "/l/L4.log"}]
    x.w.led["I0"]["owed"] = {"L4": "L2"}
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and G.owner_look_hold(st["hold"]["why"]) and st["game"]["clauses"] == ["A2"],
       "an old state's L4 FAIL row is no game_fail: his look is taken out and the item is his: %s %s" % (
           st["status"], st.get("hold")))
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


def t_dropped_staging_keeps_bridge():
    """SHOWINGS_HARDEN_FLYERS_OUT_SUBJECTS_TIGHT (Codex review): an item dropped mid-staging gave the bridge back before
    its staging worker died, and `retiring` counted as no live user, so another item could stage beside it."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(st["game"]["phase"] == "staging", "staging: %s" % st["game"]["phase"])
    unit = st["run"]["unit"]
    x.w.led["I0"] = {"state": "dropped", "built_sha": SHA, "title": "t", "owed": {}}
    x.tick()
    ok(x.st("I0")["status"] in ("retiring", "retired") and "release" not in x.w.events,
       "dropped mid-staging: no release while its worker may still drive the game: %s" % x.st("I0")["status"])
    ok(x.st("I0")["status"] != "retiring" or G.other_active(x.s.states(), "I9") == "I0",
       "and the retiring item still counts as the game's live user")
    x.w.up[unit] = False
    for _ in range(3):
        x.tick()
    ok(x.st("I0")["status"] == "retired" and x.w.events.count("release") == 1, "once it is down: released once, retired")
    x.done()


def t_rides_ok():
    """A batched item rides another's staging only past its own gate and preflight (Codex review)."""
    w = GW(1)
    o = {"item": "I1", "status": "game", "contract": {"game": {"clauses": ["A2"]}},
         "game": {"sha": SHA, "clauses": ["A2"], "offline_green": {"sha": SHA}}}
    w.led["I1"] = {"state": "built", "built_sha": SHA, "title": "a mod thing", "owed": {"A2": "L1"}}
    ok(G._rides_ok(w, {}, o), "a clean batched item rides")
    w.led["I1"] = dict(w.led["I1"], title="Mynock flies over the canyon")
    w.proofs[("I1", ".txt")] = "live-proof A2: python3 x.py --flight\n"
    ok(not G._rides_ok(w, {}, o), "a flyer's flight does not ride")
    w.led["I1"] = dict(w.led["I1"], title="a mod thing")
    w.proofs.pop(("I1", ".txt"))
    w.pre = [{"cid": "A2", "why": "files changed since the build", "fp": "x", "kind": "changed"}]
    ok(not G._rides_ok(w, {}, o), "one its own preflight refuses does not ride")


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
    ok(st["game"]["stages"] == 1 and x.w.events.count("take") == takes and "deadline exceeded" in st["put_down"]["on"]
       and "ALIVE" in st["put_down"]["on"],
       "past its deadline with NO stall evidence: waited, never restaged on the clock alone: %s" % st.get("put_down"))
    x.w.stall = "STALLED player_log: Player.log silent 600 s"
    x.tick(0)
    st = x.st("I0")
    ok(st["game"]["stages"] == 2 and x.w.events.count("take") == takes + 1,
       "past its deadline WITH stall evidence: staged again: %s" % st["game"])
    ok(G.load_bound(G.cfg(x.r), None) == G.load_bound(G.cfg(x.r), 316), "an unread list takes the full list's bound")
    import load_policy
    ok(G.load_bound(G.cfg(x.r), 316) == load_policy.profile_for(316)["process_to_bridge_deadline_s"],
       "the bound is load_policy.json's, not a number restated here")
    import belt_watchdog as bw
    ok(G.stall_evidence([bw.Sig("bridge", bw.STALLED, "not answering past warn", "")]) is None
       and G.stall_evidence([bw.Sig("game", bw.WEDGED, "Not Responding 300 s", "")]),
       "the watchdog's clock-only bridge signal is not stall evidence; Not Responding is")
    x.done()


def t_blind_stall_probe_ends_attempt():
    """LOAD_WAIT_FIX_BLIND_PROBE_WAITS_FOREVER: a load past its deadline whose stall probe cannot read is not 'no
    evidence' waited for ever: the attempt ends as a counted harness failure, the still-loading game is never restarted
    on the clock, and a probe that sees again decides as before."""
    import belt_watchdog as bw
    real = bw.gather

    def boom(**kw):
        raise OSError("probe broken")
    bw.gather = boom
    try:
        ev = G.GameFx.load_stall_evidence(None)
    finally:
        bw.gather = real
    ok(ev and ev.startswith(G.STALL_BLIND) and "probe broken" in ev,
       "the real probe reports a raising gather() as BLIND, never None: %r" % ev)
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.running = False
    x.tick()
    staged_then_ended(x)
    x.w.running, x.w.started, x.w.mods = "LOADING", x.now, 316
    takes = x.w.events.count("take")
    x.tick()
    x.w.stall = G.STALL_BLIND + "OSError: probe broken"
    x.now = x.w.started + G.load_bound(G.cfg(x.r), 316) + 1
    x.tick(0)
    st = x.st("I0")
    ok(st["game"].get("harness") == 1 and st["game"]["phase"] == "stage" and st["game"]["retry_at"] > x.now
       and st["put_down"]["on"].startswith("harness #1") and "blind" in st["put_down"]["on"]
       and x.w.events.count("take") == takes,
       "past its deadline, a blind probe ends the attempt as a counted harness failure, no restart: %s" % st)
    ok(any("harness failure" in n and "blind" in n for n in x.w.notes), "the ledger note reports the blind probe up")
    ok(any(j.get("kind") == "game_harness" for j in map(json.loads, open(x.s.p("journal.jsonl")))),
       "an alarm is journaled")
    x.now = st["game"]["retry_at"] + 1
    x.tick(0)
    st = x.st("I0")
    ok(x.w.events.count("take") == takes and st["game"]["phase"] == "prove",
       "at the retry the still-loading game is read again, not restaged: %s" % st["game"])
    x.tick(0)
    st = x.st("I0")
    ok(x.w.events.count("take") == takes and st["game"]["harness"] == 2 and st["game"].get("spare_load"),
       "still blind past the deadline: the attempt ends again, counted, the game still spared: %s" % st["game"])
    x.now = st["game"]["retry_at"] + 1
    x.w.stall = "STALLED player_log: Player.log silent 600 s"
    x.tick(0)       # the retry reads the spared load again (prove) ...
    x.tick(0)       # ... where the probe, seeing again, finds evidence
    st = x.st("I0")
    ok(x.w.events.count("take") == takes + 1 and "spare_load" not in st["game"],
       "a probe that sees again and finds stall evidence restages the load: %s" % st["game"])
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
        st["hold"] = {"why": "game phase: refused again: proof selftest_flyer: changed since the build", "kind": "game",
                      "delivered": True, "at": x.now}
        x.s.save(st)
    R.unhold(x.s, "I0", "per ruling")
    ok(x.st("I0")["status"] == "game", "the word flyer in a proof's name is a plain game hold, back to its game phase")
    with x.s.lock():
        st = x.st("I0")
        st["status"] = "held"
        st["hold"] = {"why": "game phase: flyer: a flyer's flight", "kind": "game", "delivered": True, "at": x.now}
        x.s.save(st)
    R.unhold(x.s, "I0", "his yes")
    ok(x.st("I0")["status"] == "queued", "a flyer hold keeps the old road")
    x.done()


def t_green_sha_is_not_judged_again():
    """PASS3_FLOOD_FIX_REJUDGE_GREEN_SHA (2026-11-05): a hold of a queued item and its unhold sent four candidates back to
    the Judge on the sha it had already passed; each paid a Judge to say PASS again and only then went to its game step.
    A candidate whose sha holds the Judge's PASS goes to its game step; a contract moved since is judged afresh."""
    x = rig(1)
    to_game(x, "I0")
    n = x.st("I0")["check_count"]
    with x.s.lock():        # the incident: an old WEAK the live rule reads PASS, queued after the game, held, unheld
        st = x.st("I0")
        st["status"] = "queued"
        st["proof_only"] = {"sha": "old", "at": x.now - 99, "weak": "GAP:OTHER the proof could be stronger"}
        x.s.save(st)
    R.hold(x.s, "I0", "conductor: stop the churn")
    R.unhold(x.s, "I0", "conductor: the lane fix is live")
    ok(x.st("I0")["status"] == "candidate", "the unhold lifts it to its candidate: %s" % x.st("I0")["status"])
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "game" and st["check_count"] == n, "no second Judge on the passed sha, back to the game step: "
       "%s, %d checks" % (st["status"], st["check_count"]))
    ok(st["game"]["offline_green"]["sha"] == SHA == st["game"]["sha"], "the Judge's green is kept on the same sha")
    ok(any(a.get("routed") == "green_stands" for a in x.s.attempts("I0")), "the routing is written to the attempts")
    x.done()
    for why, change in (("a contract moved since", lambda s: s["contract"].update(proof="python3 selftest_y.py")),
                        ("an older green with a contract row after it",
                         lambda s: (s["game"]["offline_green"].pop("contract"),
                                    x.s.attempt("I0", {"at": R.iso(x.now + 60), "contract": s["contract"]})))):
        x = rig(1)
        to_game(x, "I0")
        with x.s.lock():
            st = x.st("I0")
            change(st)
            st["status"] = "candidate"
            x.s.save(st)
        ok(G.green_stands(x.st("I0"), x.s.attempts("I0")) is None, "%s: the Judge reads it afresh" % why)
        x.tick()
        ok(x.st("I0")["status"] == "checking", "%s: a check is launched: %s" % (why, x.st("I0")["status"]))
        x.done()


def to_check(x, i):
    x.run_one(i)
    st = x.st(i)
    R.contract(x.s, i, st["gen"], "python3 selftest_x.py", game=GAME)
    R.finish(x.s, i, st["gen"], SHA, "evidence")
    x.w.up[st["run"]["unit"]] = False
    x.tick()
    x.tick()
    ok(x.st(i)["status"] == "checking", "%s: finish reaches the checker" % i)


def t_bounce_from_checking_is_quarantined():
    """CHECKING_BOUNCE_ENFORCE_QUARANTINE_HOLD, owner 2026-11-05: "Please watch carefully for dangerously expensive
    poorly passing items. Quarantine them if they bounce again from Checking." An item at pass >= 3, or over its
    advisory item_spend_limit, that the Judge does not PASS is held at once: no build, no re-check, one Conductor line,
    out only by a ruling's unhold. Below both bars a bounce routes as before."""
    cases = (("pass 3, WEAK", dict(returns=2), "WEAK", "pass 3"),
             ("pass 3, FAIL", dict(returns=2), "FAIL", "pass 3"),
             ("pass 3, UNMEASURED", dict(returns=2), "UNMEASURED", "pass 3"),
             ("over the spend limit, pass 1, WEAK", dict(spent=5 * 10 ** 6), "WEAK", "pass 1"),
             ("pass 1, under the limit, WEAK", {}, "WEAK", None))
    for name, preset, word, at in cases:
        x = rig(1)
        x.r = dict(x.r, item_spend_limit=3 * 10 ** 6)
        to_check(x, "I0")
        with x.s.lock():
            st = x.st("I0")
            st.update(preset)
            x.s.save(st)
        st = x.st("I0")
        R.verdict(x.s, "I0", st["check"]["nonce"], word, {"WEAK": "GAP:DIFF hunk 2 put back, proof green." + S.STRONG_WEAK,
                                                          "FAIL": "the comp is never added",
                                                          "UNMEASURED": "CANNOT REACH: ssh stevedesktop exit 255"}[word])
        x.w.up[st["check"]["run"]["unit"]] = False
        runs, checks = len(x.w.launches), x.st("I0")["check_count"]
        for _ in range(4):
            x.tick()
            x.now += 3600       # past any recheck wait
        st = x.st("I0")
        h = st.get("hold") or {}
        if at is None:
            ok(h.get("kind") != R.QUARANTINE and not any("quarantine" in a for a in x.w.attn),
               "%s: routed as before, no quarantine (%s)" % (name, st["status"]))
            x.done()
            continue
        ok(st["status"] == "held" and h.get("kind") == R.QUARANTINE, "%s: held as quarantine: %s %s"
           % (name, st["status"], h.get("kind")))
        ok(h.get("why", "").startswith("quarantine: bounced from checking at %s, %d tokens" % (at, st["spent"])),
           "%s: the reason leads with pass and tokens: %s" % (name, h.get("why", "")[:90]))
        ok(len(x.w.launches) == runs and st["check_count"] == checks,
           "%s: no build and no re-check starts: %d runs, %d checks" % (name, len(x.w.launches) - runs,
                                                                         st["check_count"] - checks))
        ok(sum("quarantine: bounced" in a for a in x.w.attn) == 1, "%s: one Conductor line: %d"
           % (name, sum("quarantine: bounced" in a for a in x.w.attn)))
        R.unhold(x.s, "I0", "PER RULING CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM: rebuild it once")
        st = x.st("I0")
        ok(st["status"] != "held" or (st.get("hold") or {}).get("kind") != R.QUARANTINE,
           "%s: a ruling's unhold lifts the quarantine: %s %s" % (name, st["status"], (st.get("hold") or {}).get("kind")))
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
                 "log": "/l/A2.log", "game_started": R.relentless_live.iso(x.w.started)}]
    x.tick()
    S.blame_product(x, "I0")
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
                 "log": "/l/A2.log", "game_started": R.relentless_live.iso(x.w.started)}]
    x.tick()
    S.blame_product(x, i)
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


def t_live_hold_clock_restarts_at_lease():
    """OPS_RELENTLESS_GAME_HOLD_UNSTICK_DRDP: _back keeps live_iter through stopping -> queued; the next worker leased
    30 min later inherited the FAIL's clock, so ops_watch read 31.6 min idle and lapse_holds would free the game before
    the new worker could touch it. Red on the old code: bridge_seen stayed at the FAIL."""
    x = rig(1)
    live_iterating(x)
    idle = G.cfg(x.r)["live_idle_s"]
    with x.s.lock():
        st = x.s.load("I0")
        st["status"], st["run"], st["returned_at"] = "queued", None, x.now
        st["live_iter"].pop("bridge_seen", None)
        st["live_iter"]["at"] = x.now - idle - 600       # the FAIL, long before this lease
        x.s.save(st)
    x.run_one("I0")
    li = x.st("I0").get("live_iter") or {}
    ok(li.get("bridge_seen") and x.now - li["bridge_seen"] <= 120, "the lease restarts the idle clock: %s" % li)
    x.tick()
    ok(held(x) and x.st("I0").get("live_iter"), "a freshly leased live worker is not lapsed on its first tick")
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


def t_fail_on_a_restarted_game_is_offline():
    """RELENTLESS_CORE_FIX_CODEX_FOUND_TEN_MORE #10: a FAIL read after the game restarted grants no live iteration on
    the new process, which may not run the failed build; a row with no game_started cannot show it ran here."""
    for label, game_of in (("another game", lambda x: R.relentless_live.iso(x.w.started - 5000)), ("no game", lambda x: None)):
        x = rig(1)
        to_game(x, "I0")
        x.tick()
        x.tick()
        x.w.started = x.now - 100
        row = {"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "FAIL",
               "log": "/l/A2.log"}
        if game_of(x):
            row["game_started"] = game_of(x)
        x.w.rows = [row]
        x.tick()
        S.blame_product(x, "I0")
        st = x.st("I0")
        ok(not st.get("live_iter") and st.get("last_fail"),
           "a FAIL on %s: back to a worker, no live iteration on the game now up: %s" % (label, st.get("live_iter")))
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


def t_met_clause_is_not_missing():
    """MODCHECK_DONOR_ENVIRONMENTS_1: A2 already passed live at this build (a verify event, so not outstanding); the
    implement phase read it as "missing" and sent the item back for ever. A met clause leaves the game clauses."""
    x = rig(1)
    x.w.owed = {"A1": "L1"}
    impl = x.w.game_implement

    def implement(item, sha, crit, live=None):
        impl(item, sha, crit, live)
        x.w.led[item]["passed"] = {"A2": "L1"}
    x.w.game_implement = implement
    to_game(x, "I0", game={"clauses": ["A1", "A2"], "why": "both load"})
    x.tick()
    st = x.st("I0")
    ok(not (st.get("last_fail") or {}).get("class") and st["status"] == "game", "a met clause sends nothing back: %s"
       % (st.get("last_fail") or {}).get("detail"))
    ok(st["game"]["phase"] == "prove" and st["game"]["clauses"] == ["A1"], "it leaves the clauses: %s" % st["game"])
    x.done()
    x = rig(1)
    x.w.owed = {"A1": "L1"}
    to_game(x, "I0", game={"clauses": ["A1", "A2"], "why": "both load"})
    x.tick()
    ok("missing ['A2']" in ((x.st("I0").get("last_fail") or {}).get("detail") or ""), "a clause neither owed nor met is missing")
    x.done()


def t_owed_final_joins_the_clauses():
    """A contract written before the tier rule names A1 only; the criteria file owes F1 GREEN-FULL with a proof line:
    F1 joins the game clauses at implement, so the item cannot wait on it forever. An owed GREEN-FULL with no line (Z9)
    sends the item back for one."""
    x = rig(1)
    x.w.owed = {"A1": "L1", "F1": G.FINAL_LEVEL, "Z9": G.FINAL_LEVEL}
    x.w.proofs[("I0", ".txt")] = FINAL_PROOF
    to_game(x, "I0", game={"clauses": ["A1"], "why": "small"})
    x.tick()
    st = x.st("I0")
    # changed on purpose (RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN #7): Z9 with no proof line used to stay out of the
    # clauses and the item waited at the all-PASS return forever; it now goes back for its line
    ok(st["last_fail"] and "game_contract" in st["last_fail"]["detail"] and "Z9" in st["last_fail"]["detail"]
       and "F1" not in st["last_fail"]["detail"], "Z9 (owed GREEN-FULL, no proof line) sends the item back: %s" % st.get("last_fail"))
    x.done()
    y = rig(1)
    y.w.owed = {"A1": "L1", "F1": G.FINAL_LEVEL}
    y.w.proofs[("I0", ".txt")] = FINAL_PROOF
    to_game(y, "I0", game={"clauses": ["A1"], "why": "small"})
    y.tick()
    g = y.st("I0")["game"]
    ok(g["phase"] == "prove" and g["clauses"] == ["A1", "F1"], "F1 joins the game clauses: %s" % g)
    y.done()
    z = rig(1)
    z.w.owed = {"A1": "L1", "B1": "L1"}
    z.w.proofs[("I0", ".txt")] = FINAL_PROOF
    to_game(z, "I0", game={"clauses": ["A1"], "why": "small"})
    z.tick()
    st = z.st("I0")
    ok(st["last_fail"] and "game_contract" in st["last_fail"]["detail"] and "B1" in st["last_fail"]["detail"],
       "an owed L1 the contract never named sends the item back too: %s" % st.get("last_fail"))
    z.done()


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
    ok(st["last_fail"] and st["last_fail"]["class"] == "proof_owed" and "cut at 160" in st["last_fail"]["detail"],
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
    ok(y.st("I0")["status"] != "held" and y.st("I0")["last_fail"]["class"] == "proof_owed",
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


def t_retiered_rerecorded_every_phase():
    """RELENTLESS_CRITERIA_SYNC_AFTER_RETIER: a worker cannot run `rimflow implemented` on an item relentless carries,
    so a re-tiered criterion found in the prove phase (its preflight, or a REFUSED live row) is re-recorded by the
    supervisor, never sent back as a worker's strike; a re-record that changed nothing is refused as before."""
    retier = dict(CUT, why="I0 A2 is cut at 160 chars on the ledger and the item's criteria now say something else "
                           "under that id (re-tiered): re-record them")
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    ok(x.st("I0")["game"]["phase"] == "prove" and len(x.w.impl) == 1, "implemented, on to prove")
    x.w.pre = lambda lines: [retier] if len(x.w.impl) < 2 else []      # the .criteria file changed after implement
    x.tick()
    ok(len(x.w.impl) == 2 and x.w.proves == ["I0"] and x.st("I0")["status"] == "game",
       "prove preflight: re-recorded, then the round runs (impl %d proves %s status %s)"
       % (len(x.w.impl), x.w.proves, x.st("I0")["status"]))
    # the run itself refused on the older text: re-recorded once, no worker strike, the next round decides
    x.w.rows = [dict(retier, at="2099-01-01T00:00:00Z", item="I0", criterion="A2", sha=SHA, outcome="REFUSED",
                     proof="python3 p.py")]
    x.tick()
    st = x.st("I0")
    ok(len(x.w.impl) == 3 and st["status"] == "game" and not st.get("last_fail"),
       "a REFUSED re-tiered row is re-recorded, not a strike (impl %d status %s)" % (len(x.w.impl), st["status"]))
    x.tick()
    ok(x.w.proves == ["I0", "I0"] and len(x.w.impl) == 3, "the same row once re-recorded: a new round, no re-record again")
    x.w.rows = [dict(x.w.rows[0], at="2099-01-02T00:00:00Z")]
    x.tick()
    st = x.st("I0")
    ok(st["status"] != "game" and st["last_fail"]["class"] == "proof_owed" and "game_refused" in st["last_fail"]["detail"]
       and not st["failures"].get("game_refused") and len(x.w.impl) == 3,
       "refused again after the re-record: back as before, not re-recorded for ever")
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


def t_rebuilt_assembly_carries_the_build():
    """OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT: a build stale only because another commit rebuilt a shared assembly (carry
    says so) moves to that commit inside the game phase: no worker, no strike, the Judge's green carried with its origin,
    the ledger re-recorded there. carry None, or CARRY_MAX carries already, is the stale road as before."""
    stale = [{"cid": None, "why": "changed since the built commit, so the game cannot run sha1: A.dll (c0ffee)",
              "fp": "fpS", "kind": "stale"}]
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    ok(x.st("I0")["game"]["phase"] == "prove", "implemented, clean")
    x.w.pre = lambda lines: stale if x.w.led["I0"]["built_sha"] == SHA else []
    x.w.carry = lambda sha: ("sha2full", "only rebuilt assemblies changed") if sha == SHA else None
    x.w.running = False
    x.tick()
    st = x.st("I0")
    ok(not st.get("last_fail") and st["status"] == G.GAME, "carried, not sent back: %s" % st.get("last_fail"))
    g = st["game"]
    ok(g["sha"] == "sha2full" and g["offline_green"]["sha"] == "sha2full" and g["offline_green"]["carried_from"] == SHA
       and g["carries"] == 1, "the game phase and its green moved, origin named: %s" % g)
    ok(x.w.impl[-1][1] == "sha2full" and x.w.led["I0"]["built_sha"] == "sha2full", "the ledger re-recorded on the carry")
    ok(x.w.carry_calls == [("I0", SHA)], "asked once, on the stale sha: %s" % x.w.carry_calls)
    ok(not G.gate(st, "t", PROOF, "(?!x)x", None), "the carried green passes the lease gate: %s" % G.gate(st, "t", PROOF, "(?!x)x", None))
    # SUMP_TAR_FIRE_NETWORK_1: the carried sha (another item's commit) goes stale on ITS OWN sources; carry is asked
    # again from the item's origin build, which still carries (to the newest rebuild)
    x.w.pre = lambda lines: stale if x.w.led["I0"]["built_sha"] != "sha3full" else []
    x.w.carry = lambda sha: ("sha3full", "only rebuilt assemblies changed") if sha == SHA else None
    x.tick()
    st = x.st("I0")
    ok(not st.get("last_fail") and st["game"]["sha"] == "sha3full" and st["game"]["offline_green"]["carried_from"] == SHA
       and st["game"]["carries"] == 2, "a second carry goes from the origin, not the carried sha: %s %s" % (st.get("last_fail"), st["game"]))
    ok(x.w.carry_calls[-1] == ("I0", SHA), "asked on the origin: %s" % x.w.carry_calls)
    x.done()
    y = rig(1)
    to_game(y, "I0")
    y.tick()
    y.w.pre, y.w.carry = stale, None
    y.w.running = False
    y.r = dict(y.r, max_workers=0)     # every place taken: the return waits queued, as SUMP_TAR_FIRE_NETWORK_1 did
    y.tick()
    ok(y.st("I0")["last_fail"] and y.st("I0")["last_fail"]["class"] == "game_stale_build",
       "a stale build carry refuses (the build's own source changed) goes back as before")
    # SUMP_TAR_FIRE_NETWORK_1, 18:16Z: the refusal was the supervisor's own (carry_scope), fixed while the item waited
    # queued for a worker; once carry answers, it re-enters the game step on the Judge's green, and no worker is sent
    yst = y.st("I0")
    if yst["status"] == "queued" and not yst.get("run"):
        y.w.carry = lambda sha: ("sha2full", "only rebuilt assemblies changed") if sha == SHA else None
        y.w.pre = lambda lines: stale if y.w.led["I0"]["built_sha"] == SHA else []
        y.tick()
        yst = y.st("I0")
        ok(yst["status"] == G.GAME and not yst.get("run") and ("I0", SHA) in y.w.carry_calls,
           "a queued stale return that carries now re-enters the game step, no worker: %s %s" % (yst["status"], yst.get("run")))
        y.tick()
        yst = y.st("I0")
        ok(yst["status"] == G.GAME and yst["game"]["sha"] == "sha2full" and yst["game"]["offline_green"]["carried_from"] == SHA,
           "and its preflight carries it to the rebuild: %s" % yst["game"])
    else:
        ok(False, "the stale return is queued with no worker yet: %s %s" % (yst["status"], yst.get("run")))
    y.done()
    z = rig(1)
    to_game(z, "I0")
    z.tick()
    G._save(z.s, "I0", lambda s: s["game"].update(carries=G.CARRY_MAX))
    z.w.pre, z.w.carry = stale, ("sha2full", "why")
    z.w.running = False
    z.tick()
    ok(z.st("I0")["last_fail"] and z.st("I0")["last_fail"]["class"] == "game_stale_build" and not z.w.carry_calls,
       "past CARRY_MAX carries the stale build goes back")
    z.done()


def t_stale_row_carries_the_build():
    """A stale row from a prove round (the assembly rebuilt between preflight and the run) carries the same way."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.tick()
    ok(x.w.proves == ["I0"], "proving")
    x.w.rows = [{"at": "2099-01-01T00:00:00Z", "item": "I0", "criterion": "A2", "sha": SHA, "outcome": "UNMEASURED",
                 "proof": "python3 p.py", "why": "changed since the built commit, so the game cannot run sha1: a (b)"}]
    x.w.carry = ("sha2full", "only rebuilt assemblies changed")
    x.tick()
    st = x.st("I0")
    ok(not st.get("last_fail") and st["game"]["sha"] == "sha2full", "a stale row carries: %s" % st.get("last_fail"))
    x.done()


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
        if klass == "game_stale_build":
            ok(st["last_fail"] and st["last_fail"]["class"] == klass, "%s row goes back: %s" % (klass, st.get("last_fail")))
        else:   # UNMEASURED_LANE_REWIRE_STOP_REBUILDING_SITES: the proof's or site's, routed once, never a worker
            ok(st["status"] == "held" and not st.get("last_fail") and "proof_or_site" in st["hold"]["why"],
               "a defect row is routed once to one fixer, no worker: %s" % st.get("hold"))
        ok(x.w.proves == ["I0"], "no second prove round on it")
        x.done()


GAPS = {"running": {"mods": ["Graffiti"], "running": "not in the running load: Graffiti (mandrake.rm.graffiti)"},
        "modsconfig": {"mods": ["UtinniPatches"], "off": {"UtinniPatches": "not enabled in ModsConfig"}},
        "dll": {"mods": ["FlowWorks"], "dll": ["FlowWorks/Assemblies/FlowWorks.dll"]}}


def t_modlist_gate_before_slot():
    """LIVE_MODLIST_ENFORCE_BEFORE_SLOT: 6 of 28 live runs measured nothing because the game lacked the build's mods
    (HORRORS x3 'UtinniPatches not enabled in ModsConfig', GRAFFITI x3 'not in the running load', DRAWBRIDGE a stale
    FlowWorks DLL). Each is caught before the prove round takes the game: the item stages a load instead, the supervisor
    enables its mods on the live list first, and the staging brief names the mods and the stale DLLs."""
    for kind, gap in sorted(GAPS.items()):
        x = rig(1)
        to_game(x, "I0")
        x.tick()
        ok(x.st("I0")["game"]["phase"] == "prove", "%s: implemented" % kind)
        x.w.started = x.now - 100
        x.w.gap["I0"] = gap
        x.tick()
        st = x.st("I0")
        ok(not x.w.proves, "%s: no prove round on a game that lacks the build's mods: %s" % (kind, x.w.proves))
        ok(st["game"]["phase"] == "stage" and (st["game"].get("mod_gap") or {}).get("game") == x.w.started
           and "modlist gate" in st["game"]["mod_gap"]["why"], "%s: it stages a load instead: %s" % (kind, st["game"]))
        x.tick()
        st = x.st("I0")
        ok(x.w.enabled and x.w.enabled[-1] == gap["mods"] and "enable" in x.w.events
           and x.w.events.index("enable") < x.w.events.index("take"),
           "%s: the supervisor enables %s on the live list before it takes the game: %s %s"
           % (kind, gap["mods"], x.w.enabled, x.w.events))
        stage = [l for l in x.w.launches if "STAGING" in l[2]]
        ok(st["game"]["phase"] == "staging" and stage and "--enable %s --apply" % gap["mods"][0] in stage[-1][2],
           "%s: the staging brief carries the enable command: %s" % (kind, st["game"]["phase"]))
        if kind == "dll":
            ok("SHUTDOWN WINDOW: with the game DOWN" in stage[-1][2] and "deploy FlowWorks" in stage[-1][2],
               "dll: the stale DLL is deployed in the shutdown window before the launch")
        x.done()


def t_modlist_gate_reads_once_per_game():
    """A running load cannot gain a mod: the gate reads the gap once per game, not on every tick while it waits."""
    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    x.w.rows = []
    x.w.gap["I0"] = GAPS["running"]
    with x.s.lock():
        st = x.s.load("I0")
        st["game"]["proved_at"] = None
        x.s.save(st)
    acts, proves = [], len(x.w.proves)
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    st = x.st("I0")
    ok(len(x.w.proves) == proves and st["game"].get("waits_reload") and any(a["do"] == "game_mod_gap" for a in acts),
       "the gap waits while I1 is untried on the running game: %s" % acts)
    n = len(x.w.gap_calls)
    G.step(x.s, x.w, x.r, "I0", x.now + 5, [], R)
    ok(len(x.w.gap_calls) == n and len(x.w.proves) == proves, "the second tick reuses the reading of this game")
    x.done()


def t_modlist_enable_refused_holds():
    """No restart path holds the mods (a name or dependency resolves nowhere): held with the reason and an alarm, never
    a load that cannot serve it."""
    x = rig(1)
    to_game(x, "I0")
    x.tick()
    x.w.started = x.now - 100
    x.w.gap["I0"] = GAPS["modsconfig"]
    x.w.enable_why = "REFUSING: cannot enable UtinniPatches needs foo.bar, which neither list holds"
    x.tick()
    x.tick()
    st = x.st("I0")
    ok(st["status"] == "held" and "foo.bar" in st["hold"]["why"] and "take" not in x.w.events,
       "held with the reason, no bridge take: %s" % st.get("hold"))
    ok(any("next load cannot hold its mods" in n for n in x.w.notes), "and the ledger says why")
    x.done()


def t_modlist_batch_enables_union():
    """Items waiting for a reload ride one load: the supervisor enables every one's mods before it."""
    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    x.w.gap = {"I0": GAPS["running"], "I1": GAPS["modsconfig"]}
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="stage")
        x.s.save(st)
    x.w.running = False
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    G.step(x.s, x.w, x.r, "I0", x.now + 1, acts, R)
    ok(x.w.enabled and x.w.enabled[-1] == ["Graffiti", "UtinniPatches"], "one enable for the whole batch: %s %s"
       % (x.w.enabled, acts))
    x.done()


def t_modlist_rider_refusal_stages_alone():
    """OPS_CHURN_DIAGNOSE_PLAYER_YGLE_IHKT: PLAYER_START_SITE_1 was held because riders named Utils, bridgetools and
    BiomesShell ("no About.xml with a packageId"). A refused batch enable retries the item's own mods; when they enable,
    the item stages alone and is never held on a rider's names."""
    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    x.w.gap = {"I0": GAPS["running"], "I1": {"mods": ["Utils"]}}
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="stage")
        x.s.save(st)
    x.w.running = False
    plain = x.w.modlist_enable

    def enable(mods):
        plain(mods)
        return "REFUSING: Utils (no About.xml with a packageId in the game folder or the repo)" if "Utils" in mods else None
    x.w.modlist_enable = enable
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    G.step(x.s, x.w, x.r, "I0", x.now + 1, acts, R)
    st = x.s.load("I0")
    ok(x.w.enabled[-2:] == [["Graffiti", "Utils"], ["Graffiti"]], "the batch, then the item alone: %s" % x.w.enabled)
    ok(st["status"] != "held" and "take" in x.w.events and any(a["do"] == "game_modlist_riders_dropped" for a in acts),
       "not held; it stages alone: %s %s %s" % (st["status"], x.w.events, acts))
    ok((st["game"].get("batch") or []) == [], "no rider rides it: %s" % st["game"].get("batch"))
    x.done()


def t_stage_plans_once_for_the_batch():
    """A staging of three plans once, over the union: 17 sequential plans outlived the tick's 20-minute kill."""
    import relentless_live_round as LR

    class F(object):
        plans = []
        def mods_of(self, sha):
            if sha == "bad":
                raise ValueError("no such sha")
            return {"a": ["FlowWorks"], "b": ["Graffiti"], "c": ["FlowWorks"]}[sha]
        def folded(self): return {}
        def deploy_plan(self, args, t):
            self.plans.append(args)
            return 0, ""
    g = LR.batch_gap(F(), [("a", ""), ("b", "live-mods: UtinniPatches\n"), ("c", "")])
    ok(F.plans == ["--mod FlowWorks --mod Graffiti --mod UtinniPatches --gate"] and g["mods"] == ["FlowWorks", "Graffiti", "UtinniPatches"],
       "one plan over the union: %s %s" % (F.plans, g))
    F.plans = []
    g = LR.batch_gap(F(), [("bad", ""), ("b", "")])
    ok(len(F.plans) == 1 and g["mods"] == ["Graffiti"] and "no such sha" in g["error"], "one unread build costs the others nothing: %s" % g)

    x = rig(2, share=1.0, max_workers=2)
    two_in_prove(x)
    x.w.gap = {"I0": GAPS["running"], "I1": GAPS["modsconfig"]}
    with x.s.lock():
        st = x.s.load("I1")
        st["game"].update(phase="stage")
        x.s.save(st)
    x.w.running = False
    G.step(x.s, x.w, x.r, "I0", x.now, [], R)
    G.step(x.s, x.w, x.r, "I0", x.now + 1, [], R)
    ok(len(x.w.batch_plans) == 1 and len(x.w.batch_plans[0]) == 2, "the stage asks once for both: %s" % x.w.batch_plans)
    x.done()


def t_bridge_refused_costs_no_plan():
    """The bridge check comes first: while it refuses no deploy is planned and ModsConfig is not touched."""
    x = rig(1)
    to_game(x, "I0")
    with x.s.lock():
        st = x.s.load("I0")
        st["game"].update(phase="stage")
        x.s.save(st)
    x.w.running = False
    x.w.idle = "NOT TAKEABLE  driver lock held by BENCH"
    n, en = len(x.w.batch_plans), len(x.w.enabled)
    acts = []
    G.step(x.s, x.w, x.r, "I0", x.now, acts, R)
    ok(len(x.w.batch_plans) == n and len(x.w.enabled) == en and "take" not in x.w.events[-1:],
       "no plan, no enable: %s %s" % (x.w.batch_plans, x.w.enabled))
    ok(any(a["do"] == "game_waits" and "driver lock" in a["why"] for a in acts), "and it says why it waits: %s" % acts)
    x.done()


def t_staging_reads_the_runs_live_mods():
    """WATER_DEPTH_RESKIN_HE_LOOKS_FIRST: the build's file said RimMandrake.FlowWorks, main said FlowWorks; the run reads
    main's, so the staging must too, and falls back to the build's only when the books have none."""
    class Round(object):
        def __init__(self, texts):
            self.texts = texts

        def proofs(self, item):
            return self.texts.get(item, "")

    class Fx(G.GameFx):
        def __init__(self, texts):
            self._round = Round(texts)

        def _round_fx(self):
            return self._round

        def proofs_at(self, item, sha, ext=".txt"):
            return "live-mods: RimMandrake.FlowWorks\n" if sha == "old" else ""
    fx = Fx({"W": "live-mods: FlowWorks\n"})
    ok(fx._mods_text("W", "old") == "live-mods: FlowWorks\n", "the books' current file wins over the build's")
    ok(fx._mods_text("X", "old") == "live-mods: RimMandrake.FlowWorks\n", "no current file: the build's is read")
    import relentless_live_round as LR
    got = sorted({m for i, s in [("W", "old")] for m in LR.live_deploy(fx._mods_text(i, s))})
    ok(got == [], "live-mods names no tree to deploy: %r" % got)


def t_mod_gap_pure():
    import relentless_live_round as LR
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
    import modlist_swap as M
    ok(G.mod_gap_why({"mods": ["A"], "off": {}, "dll": [], "running": None, "error": "plan failed"}) is None,
       "a clean gap (or an unread plan) blocks nothing")
    for gap in GAPS.values():
        ok((G.mod_gap_why(gap) or "").startswith("modlist gate:"), "each kind blocks: %s" % gap)
    ok(G.enable_set([GAPS["running"], GAPS["dll"], None]) == ["FlowWorks", "Graffiti"], "enable set is the union")
    ok(G.dll_mods([GAPS["dll"]]) == ["FlowWorks"], "stale DLL mods")
    ok(M.merged(["a", "b", "d"], ["c", "x", "B"], ["a", "b", "c", "d"]) == ["a", "b", "c", "d", "x"],
       "enable keeps the owner's order, appends the unknown, never repeats")

    class F(object):
        def mods_of(self, sha): return ["FlowWorks"]
        def folded(self): return {}
        def deploy_plan(self, args, t):
            self.args = args
            return 1, ("FlowWorks        mandrake.rm.flowworks      \n  ~ Assemblies/FlowWorks.dll\n"
                       "UtinniPatches    mandrake.rut.patches       not enabled in ModsConfig\n")
        def running_load_gap(self, mods): return "not in the running load: %s" % mods[0]
    f = F()
    g = LR.mod_gap(f, "s", "live-mods: UtinniPatches\n")
    ok(g["mods"] == ["FlowWorks", "UtinniPatches"] and "--mod UtinniPatches" in f.args, "plans the build and its live-mods: %s" % g)
    ok(g["off"] == {"UtinniPatches": "not enabled in ModsConfig"}, "reads not-enabled from the plan: %s" % g["off"])
    ok(g["running"] and LR.mod_gap(f, "s", "", running=False)["running"] is None, "the running read only when asked")


def main():
    args = sys.argv[1:]
    if "--pre-recarry" in args:     # replays SUMP_TAR_FIRE_NETWORK_1's 19:07Z reopen as it ran before recarry_returned
        G.recarry_returned = lambda store, fx, now, acts: None     # (OPS_CHURN_DIAGNOSE_SUMP_GSVT_SSCT's class guard)
    picked, ran = set(a for a in args if not a.startswith("--")), 0      # no names: every test
    for t in (t_parse_and_brief, t_pool, t_contract_widens, t_pass_enters_game_and_proves,
              t_nocode_rebuild_reaches_implemented, t_fail_returns,
              t_not_owed_returns, t_refused_proof_returns_offline, t_unmeasured_twice_returns_offline, t_cap_returns_with_the_exit_reason_and_log, t_long_reason_survives_both_unmeasured_returns, t_dud_on_this_game_returns_at_once, t_gate, t_stage_and_release, t_stage_idle_releases, t_stage_max_stops_before_quarantine, t_stage_snag_releases, t_one_live_user, t_dropped_staging_keeps_bridge, t_rides_ok, t_round_only_item, t_flyer_put_down, t_owner_look_skipped_routes_owner, t_waits_put_down,
              t_stage_remakes_clone, t_tick_reads_windows_tools, t_loading_is_waited_not_restaged, t_blind_stall_probe_ends_attempt,
              t_failed_staging_is_harness_not_owner, t_unreadable_game_waits, t_unhold_game_hold_returns_to_game,
              t_green_sha_is_not_judged_again, t_bounce_from_checking_is_quarantined,
              t_stage_refuses_a_clone_without_launcher, t_running_game_serves_others_before_a_reload,
              t_batch_wait_is_bounded, t_fail_on_a_running_game_is_worked_live, t_fail_with_no_game_is_offline, t_fail_on_a_restarted_game_is_offline,
              t_stage_tries_a_newer_running_game_first,
              t_final_verification_waits_and_batches, t_owed_final_joins_the_clauses, t_met_clause_is_not_missing,
              t_refusal_returns_once_then_holds, t_retiered_criteria_are_rerecorded, t_retiered_rerecorded_every_phase, t_stale_build_caught_before_a_slot,
              t_rebuilt_assembly_carries_the_build, t_stale_row_carries_the_build, t_dead_rows_go_back, t_idle_live_hold_lapses, t_live_hold_clock_restarts_at_lease,
              t_live_hold_lapses_when_its_game_is_gone,
              t_dead_prove_pid_frees_the_game, t_modlist_gate_before_slot, t_modlist_gate_reads_once_per_game,
              t_modlist_enable_refused_holds, t_modlist_batch_enables_union, t_modlist_rider_refusal_stages_alone, t_mod_gap_pure, t_staging_reads_the_runs_live_mods,
              t_stage_plans_once_for_the_batch, t_bridge_refused_costs_no_plan):
        if picked and t.__name__ not in picked:
            continue
        ran += 1
        print("--", t.__name__)
        t()
    if picked and ran != len(picked):     # a misspelt or unlisted name must not read as a clean run
        print("selftest_relentless_game: FAIL ran %d of the %d named" % (ran, len(picked)))
        return 1
    print("selftest_relentless_game: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
