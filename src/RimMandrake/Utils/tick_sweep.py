#!/usr/bin/env python3
"""The sweep of the Maturation Pipeline tick over a simulated day (page design/specs/2026-11-27-tick-sweep/boundary.md).

It runs the real tick (maturation_dispatch.tick, apply=True, autonomy on: decide, maturation_autonomy.resolve and
execute, the deploy unit's books, the reading) every STEP_S seconds on a fake clock, over a grid of regimes. Around
it run the real readers of the tick's leftovers: the visit feed's waiting() (testq/visit_feed.py) on the tick's own
`ingame_testq` block, and the Conductor's owed list (conductor_stops.load) on the lane's reading. Stand-ins replace
only what touches the world: the mods' facts (build_facts reads git, the ledger and the game folders), the helper and
deploy launches, the games, Steve's test lane, the account meter, git, the ledger (model.read) and a scratch control
db. Every subprocess and socket the real code opens is refused and counted (`world touched`).

On every step it reads each mod, each open mod ticket and each visit check, and asks: is it moving (a run or deploy
started or ended, a live run the world ends, a check measured, a stage changed), on a wait the world itself holds (the
account gate shut, both games taken), told (a Needs Conductor line, a held or planned row, a pause a bar put there:
SPENT_PAUSES / SET_PAUSES, a Conductor's owed row), or done (past its start stage)? A thing that is none of these for
longer than its limit is STUCK: a state that nothing ends. At the day's end a mod that kept moving but never left its
start stage and is not told is STUCK too (a loop nothing ends), and a row whose why carries a Python exception the
tick caught is an error case. Deterministic; no network, no game, no model call; it writes only under its own temp
folder. Every report prints the worst value of each measure, its limit and the cases read.

    tick_sweep.py grid [--quick] [--base B] [--plant P]   every regime; --quick is the part ./publish runs
    tick_sweep.py one <base>.<window>.<offset> [--plant P] one regime, with each mod's rows and the world's events
"""
import argparse
import datetime
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIMFLOW = HERE.parent / "rimflow"
ROOT = Path(tempfile.mkdtemp(prefix="tick_sweep_"))
# the scratch world, set before the tick's code is imported (several modules read their folders at import)
_ENV = {"RM_MATURATION_DISPATCH_DIR": "state", "RM_WORK_BUNDLE_DIR": "state/work_bundle",
        "RM_CONTROL_DB": "control.db", "RM_DISPATCHER_STATE": "dispatcher",
        "RM_REFUSAL_DIR": "refusals", "RM_OPS_WATCH_DIR": "ops_watch", "RM_JUDGE_CALIBRATION": "no_calibration.json",
        "RM_OWNER_HOLD_FILE": "owner_hold.json", "MATURATION_BRIEF_DIR": "briefs", "RM_LIST_DISPATCH_DIR": "list_dispatch",
        "RIMFLOW_LEDGER": "ledger.jsonl"}
os.environ.update({k: str(ROOT / v) for k, v in _ENV.items()}, RM_UNDER_SELFTEST="1")
for _k in ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE", "RM_LIST_DISPATCH_DIR"):
    os.makedirs(os.environ[_k], exist_ok=True)
for _p in (str(HERE / "testq"), str(HERE), str(RIMFLOW)):
    sys.path.insert(0, _p)

# Audit the operations before Python hands them to the OS, including socket creation and DNS lookup.
TOUCHED = []
WORLD_EVENTS = {
    "subprocess.Popen", "os.system", "os.exec", "os.fork", "os.forkpty", "os.posix_spawn", "os.startfile",
    "os.startfile/2", "_posixsubprocess.fork_exec",
    "socket.__new__", "socket.bind", "socket.connect", "socket.sendto", "socket.sendmsg",
    "socket.getaddrinfo", "socket.gethostbyname", "socket.gethostbyaddr", "socket.getnameinfo",
}


def _refuse_world_call(event, args):
    if event in WORLD_EVENTS:
        detail = "%s %r" % (event, args[0]) if event == "subprocess.Popen" else event
        TOUCHED.append(detail)
        raise OSError("tick_sweep: refused " + detail)


sys.addaudithook(_refuse_world_call)


import control as C  # noqa: E402
import model  # noqa: E402
import maturation as M  # noqa: E402
import maturation_dispatch as MD  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402
import conductor_stops as CS  # noqa: E402
import failure_class as FC  # noqa: E402
import testq as T  # noqa: E402
import visit_feed as VF  # noqa: E402
import modledger as ML  # noqa: E402
import role_launch as RL  # noqa: E402

if TOUCHED:
    raise RuntimeError("tick_sweep: imports attempted world calls: " + ", ".join(TOUCHED))

DAY = 24 * 3600
STEP_S = 600            # a step every 10 min: the tick runs every 60 s live; 10 min keeps a day at 144 ticks (measured
#                         ~0.15 s a tick here), and every limit below is a multiple of it
T0 = 1795651200.0       # 2026-11-26T00:00:00Z, a fixed day: the same regime gives the same result every time
# The limits (each from a bar or a measured fact; the page's LIMITS):
# budget: danger=a stuck mod read as moving; ends no work: a limit on the sweep's fake clock, the case reads STUCK
STILL_LIMIT_S = 3600    # a mod that neither moves nor is told for an hour: the Conductor's own sort of a resting mod's
#                         tickets after 1 h (conductor_stops.REST_S) and the owner's "over an hour on one check" (2026-11-24)
TICKET_LIMIT_S = CS.REST_S + STEP_S     # a resting mod's open ticket is on the owed list once the rest passes REST_S;
#                                         one step late is the sweep's own grain
# budget: danger=a stand-in run ends too soon to show a live one; ends no work: the fake world ends the run
RUN_S = 40 * 60         # a stage or steward run: the world ends it in 40 min (under the hour, so a live run is moving)
DEPLOY_S = 10 * 60      # a deploy unit: 10 min (the one measured ran 998 s, MD.DEPLOY_MAX_S's source)
LANE_JOB_S = 5 * 60     # one testq job on Steve's lane: the 1-4 min refusal cycle of 2026-11-23 (visit_feed.py), rounded up
STALE = M.STALE_WALK + "the deployed walk folder is not the source at the visit's commit"


def iso(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f)


class Mod:
    """One mod of the world: what build_facts would read, kept by the world."""

    def __init__(self, name, stage, **kw):
        self.name, self.stage, self.start = name, stage, stage
        self.version = kw.get("version", "0.1.0")
        self.visit = kw.get("visit", 3)
        self.why = list(kw.get("why") or [])        # the exit's reasons (in_game)
        self.checks = dict(kw.get("checks") or {})  # {check: [chains]} the visit owes through testq
        self.measured = set()                        # chains measured PASS in this visit
        self.opened = kw.get("opened")
        self.passed_at = kw.get("passed_at")
        self.tickets = list(kw.get("tickets") or [])     # open mod_work ticket ids
        self.ticket_since = kw.get("ticket_since")
        self.road_back = list(kw.get("road_back") or [])  # open road-back item ids the offline build can work
        self.moved_back = kw.get("moved_back", T0 - 600)  # when the road back sent it to the offline build


class Run:
    def __init__(self, unit, mod, kind, start, end, item=None):
        self.unit, self.mod, self.kind, self.start, self.end, self.item = unit, mod, kind, start, end, item


class World:
    """The games, the runs, Steve's lane and the account, on the fake clock. Only the sweep and the stand-ins write it."""

    def __init__(self, regime, root):
        self.reg, self.root, self.t = regime, root, T0
        self.mods = {}
        self.runs = {}
        self.n = 0
        self.lane_queue, self.lane_now, self.lane_done = [], None, []
        self.moved = {}             # mod -> last time it moved
        self.events = []            # what happened, for a stuck case's story
        self.chain_tries = {}       # (mod, chain) -> [outcome]

    # -- the world's own holds (a cause that ends by itself; the stall clock does not run in them)
    def account_open(self, t):
        return not any(a <= t < b for a, b in self.reg.get("account_shut", []))

    def lane_refuses(self, t):
        return any(a <= t < b for a, b in self.reg.get("lane_refuses", []))

    def game_down(self, game, t):
        return any(a <= t < b for a, b in self.reg.get("game_down", {}).get(game, []))

    def bridge_busy(self, t):
        return any(a <= t < b for a, b in self.reg.get("bridge_busy", []))

    def world_holds(self, mod, t):
        """A cause the world ends by itself: the account gate shut, or both games taken by another lane (an in-game
        mod only: the offline stages take no game)."""
        m = self.mods.get(mod)
        return not self.account_open(t) or (self.bridge_busy(t) and m is not None and m.stage == "in_game")

    def move(self, mod, what):
        self.moved[mod] = self.t
        self.events.append((self.t, mod, what))

    # -- the facts build_facts would read
    def live_units(self, mod):
        return [r.unit for r in self.runs.values() if r.mod == mod and r.kind != "deploy" and (r.end is None or r.end > self.t)]

    def last_end(self, mod):
        """When the mod's latest run ended, or None when none has: the real facts' `last_end` (no run is not 0)."""
        ends = [r.end for r in self.runs.values() if r.mod == mod and r.end and r.end <= self.t]
        return max(ends) if ends else None

    def facts(self):
        out = {}
        for name, m in self.mods.items():
            f = {"mod": name, "stage": m.stage, "version": m.version, "visit": m.visit, "live_units": self.live_units(name),
                 "last_end": self.last_end(name), "run_tokens": {}, "stage_runs": {}, "blocked": [], "killed": [], "hand_steps": None}
            if m.stage == "in_game":
                owed = [k for k, ch in m.checks.items() if not set(ch) <= m.measured]
                why = list(m.why) + ["check %s owes a run" % k for k in owed]
                f.update(owed="exit met" if not why else "run" if owed else "exit not met",
                         exit={"state": "met" if not why else "not_met", "why": why, "build_match": None},
                         to_run=owed, testq=owed, opened=m.opened)
            if m.stage == "offline_build":
                # a road back: the exit is refused by road_back_items alone while its open items stand
                # (design/specs/2026-11-25-tick-launches-road-back-hold/boundary.md, a-road-back-hold)
                f.update(owed="blocked" if m.road_back else "ready to advance", build_refusals=[], refused_bars=[],
                         other_refusals=["road_back_items"] if m.road_back else [], bars_total=4, walk_bars=[],
                         observed={"road_back_items": "road back in_game -> offline_build"}, since=iso(m.moved_back),
                         road_back_hold={"open": [{"id": i, "title": i, "needs": "deploy"} for i in m.road_back],
                                         "stage6": [], "unread": [], "at": iso(m.moved_back),
                                         "move_at": m.moved_back, "waits": {}})
            out[name] = f
        return out

    # -- the stand-ins' side of a launch
    def launch(self, mod, kind, item=None):
        self.n += 1
        unit = "rm-sweep-%s-%d" % (kind, self.n)
        end = self.t + self.reg.get("run_s", RUN_S)
        m = self.mods.get(mod)
        if kind == "steward" and m and m.why == [STALE]:
            # a steward may not stop a game: the stale walk build is deployed only with ArchBig down. It waits for
            # good, or (gives_up_s) gives up after that long, as the one on Explosive Knockback did after 2 h
            end = self.t + self.reg["gives_up_s"] if self.reg.get("gives_up_s") else None
            if self.reg.get("game_down", {}).get("a"):
                end = min(b for a, b in self.reg["game_down"]["a"] if b > self.t) if any(
                    b > self.t for a, b in self.reg["game_down"]["a"]) else None
        self.runs[unit] = Run(unit, mod, kind, self.t, end, item)
        self.move(mod, "%s %s launched (%s)" % (kind, unit, item))
        return unit

    def deploy(self, mod, game, kind):
        self.n += 1
        unit = "rm-game-deploy-%d" % self.n
        took = 60 if self.bridge_busy(self.t) else DEPLOY_S     # a wait ends at once (game_repair's hold_refusal)
        self.runs[unit] = Run(unit, mod, "deploy", self.t, self.t + took, kind)
        self.move(mod, "deploy %s on %s started (%s)" % (unit, game, kind))
        return unit

    def record(self, unit):
        """The run record detached_helper keeps (status launching/running/finished), for the world's own units."""
        r = self.runs.get(unit)
        if r is None:
            return None
        live = r.end is None or r.end > self.t
        return dict({"unit": unit, "item": r.item, "at": r.start, "status": "running" if live else "finished"},
                    **({} if live else {"ended": r.end, "result": "success"}))

    def run_ends(self, mod):
        """True when a live unit of the mod is one the world ends (a run's length, not the limit, says when): a live run
        is moving however long it is. A run with no end (the steward that may not stop the game) is not."""
        return any(r.mod == mod and r.end is not None and r.end > self.t for r in self.runs.values())

    def unit_active(self, unit):
        r = self.runs.get(unit)
        return False if r is None else (r.end is None or r.end > self.t)

    # -- one step of the clock: runs end, deploys write their result, the lane works
    def advance(self, t):
        self.t = t
        lift = self.reg.get("hold_until")
        if self.reg.get("hold") and lift is not None and t >= lift and not getattr(self, "lifted", False):
            self.lifted = True
            _write(os.environ["RM_OWNER_HOLD_FILE"], {"holds": []})     # he lifts it: the file names no mod
            for mod in self.reg["hold"]:
                self.move(mod, "the owner lifted his hold")
        for r in list(self.runs.values()):
            if r.end is not None and r.end <= t and not getattr(r, "seen_end", False):
                r.seen_end = True
                m = self.mods.get(r.mod)
                if r.kind == "deploy" and self.bridge_busy(r.start):
                    # game_repair: another run holds the game's driver lock, so the unit ends at once on a wait
                    _write(os.path.join(MD.game_deploy_dir(), "%s.json" % r.mod), {
                        "mod": r.mod, "unit": r.unit, "game": "a", "kind": r.item, "at": r.start, "end": r.end,
                        "state": "wait", "text": "%s ArchBig is held by another run, so the deploy of %s cannot start "
                        "(sweep)" % (M.WAIT_MARK, r.mod), "sha": "c0ffee", "generation": None, "paths": []})
                    self.move(r.mod, "deploy %s ended on a wait: the game is another run's" % r.unit)
                elif r.kind == "deploy":
                    _write(os.path.join(MD.game_deploy_dir(), "%s.json" % r.mod), {
                        "mod": r.mod, "unit": r.unit, "game": "a", "kind": r.item, "at": r.start, "end": r.end,
                        "state": "ok", "text": "deployed the walk build", "sha": "c0ffee", "generation": 1, "paths": []})
                    if m and STALE in m.why:
                        m.why.remove(STALE)
                    self.move(r.mod, "deploy %s ended ok" % r.unit)
                elif r.kind == "steward" and m and "EXIT_MET" in str(r.item) and m.stage == "in_game":
                    self.move(r.mod, "steward %s confirmed the exit: in_game -> pre_human" % r.unit)
                    m.stage = "pre_human"       # the confirm run's advance; the walk brief is another lane's
                elif r.kind == "steward" and m and m.stage == "offline_build" and m.road_back:
                    self.move(r.mod, "holder %s closed the road-back items %s" % (r.unit, ", ".join(m.road_back)))
                    m.road_back = []
                elif r.kind == "steward" and m and "ADVANCE" in str(r.item) and m.stage == "offline_build":
                    self.move(r.mod, "steward %s advanced the mod: offline_build -> blind_challenge" % r.unit)
                    m.stage = "blind_challenge"
                elif r.kind == "steward" and m and STALE in m.why and not any(
                        a <= r.end <= b for a, b in self.reg.get("game_down", {}).get("a", [])):
                    self.move(r.mod, "steward %s gave up: ArchBig was never down, the walk build is still stale" % r.unit)
                elif r.kind == "steward" and m and STALE in m.why:
                    m.why.remove(STALE)
                    self.move(r.mod, "steward %s deployed the walk build with ArchBig down" % r.unit)
                else:
                    self.move(r.mod, "%s %s ended" % (r.kind, r.unit))
        self._lane(t)

    def _lane(self, t):
        if self.lane_now and self.lane_now["end"] <= t:
            j = self.lane_now
            self.lane_now = None
            m = self.mods.get(j["mod"])
            if j["refused"]:
                res = {"outcome": "REFUSED", "cause": "LOAD", "finished": iso(j["end"])}
            else:
                res = {"outcome": "DONE", "finished": iso(j["end"]),
                       "rows": [{"chain": c, "verdict": "PASS"} for c in j["chains"]]}
                if m:
                    m.measured.update(j["chains"])
            for c in j["chains"]:
                self.chain_tries.setdefault((j["mod"], c), []).append(res["outcome"])
            self.lane_done.append({"job": {"mod": j["mod"], "selector": {"chains": list(j["chains"])},
                                           "requested_by": "visit_feed"}, "result": res, "finished": iso(j["end"])})
            self.move(j["mod"], "lane job %s %s" % (",".join(j["chains"]), res["outcome"]))
        if not self.lane_now and self.lane_queue:
            j = self.lane_queue.pop(0)
            j.update(start=t, end=t + LANE_JOB_S, refused=self.lane_refuses(t))
            self.lane_now = j

    def after_tick(self):
        """The stage the real tick wrote (an advance writes version/stage_record.json) is the world's stage."""
        for m in self.mods.values():
            r = M.read_json(self.root, m.name, M.RECORD)[0]
            if isinstance(r, dict) and r.get("stage") and r["stage"] != m.stage:
                self.move(m.name, "stage %s -> %s" % (m.stage, r["stage"]))
                m.stage = r["stage"]
                if m.stage == "passed":
                    m.passed_at = self.t

    def in_lane(self, mod):
        return {c for j in self.lane_queue + ([self.lane_now] if self.lane_now else []) if j["mod"] == mod
                for c in j["chains"]}


def stand_ins(w):
    """-> the fx of the real tick: every hook that reaches the world answers from the World."""
    def launch(mod, cap, item, **kw):
        return 0, "STARTED %s" % item, w.launch(mod, "stage", item)

    def launch_brief(item, brief, model_, cap, seat, env=None):
        # the item names its mod as a whole word (RIMMANDRAKE_ADVANCE_EKB_...): Ek must not take Ekb's steward
        words = set(re.split(r"[^a-z0-9]+", str(item).lower()))
        mod = next((m for m in w.mods if m.lower() in words), None) or next(
            (m for m in sorted(w.mods, key=len, reverse=True) if re.search(r"\b%s\b" % re.escape(m), str(brief))), None)
        return 0, "STARTED steward on %s" % item, w.launch(mod, "steward", item)

    def game_deploy(mod, game, kind, purpose, seat="BENCH"):
        return 0, "STARTED", w.deploy(mod, game, kind)

    filed = w.filed = []
    return {
        "facts": w.facts,
        "account": lambda: (True, "sweep account open") if w.account_open(w.t) else (False, "ACCOUNT GATE: shut (sweep)"),
        "releases": lambda: ([], 0), "code": lambda: "sweep-code", "known": lambda: set(filed),
        "file": lambda item, *a, **k: (filed.append(item) or True, "filed %s" % item),
        "publish": lambda item: (True, "published %s (sweep: git stood in)" % item), "land_ledger": lambda paths: "landed %d path(s) (sweep: git stood in)" % len(paths),
        "clone": lambda: (0, 0), "clone_head": lambda: "c0ffee", "sync_clone": lambda *a, **k: None,
        "drain": lambda now: None, "pipe_off_end": lambda now: ([], None), "pins": lambda: {},
        "reap": lambda u: "reaped", "convergence": lambda root, rd: None,
        "launch": launch, "launch_brief": launch_brief, "game_deploy": game_deploy, "unit_active": w.unit_active,
        "record": w.record,
        "deploy_stale": lambda root, res, generation=None: None,
        "repair_launch": lambda *a, **k: (0, "repaired in place (sweep)", None),
        "bridge": lambda purpose, game=None: (False, "both games are taken by another lane (sweep)") if w.bridge_busy(
            w.t) else (True, "free"),
        "hands": {"lane_units": lambda: set(), "caused_by": lambda ids: set(), "events": lambda: [],
                  "known": lambda: set(filed)},
        "rescue": {}, "shortfall": {},
        # maturation_autonomy's world: the ledger's items and the Designer's books
        "designer_state": lambda m: {}, "version_locked": lambda m: True, "open_items": lambda ids, **kw: [],
        "version_evidence": lambda m: [], "designer_unit": lambda m: None, "designer_chain": lambda m: None,
        "live_endings": lambda ids: {}, "version_bugs": lambda *a, **k: [], "ticket_runs": lambda i: [],
        "walk_letter": lambda r, m: "a",
        # the walk's owed checks read git (rerun_relation): the world owes none past the visit's own exit
        "walk_owed": lambda root, mod: {"owed": {}, "why": []}, "walk_game": lambda: None,
        "pilot": lambda root, mod: True, "item_live": lambda item: None,
    }


# ---------------------------------------------------------------- the readers around the tick

def feed_step(w, rd):
    """The visit feed's real waiting() on the tick's own ingame_testq block; what it keeps is sent to Steve's lane (the
    send is stood in: one job per check). -> spent {mod: {chain: n}}."""
    blk = rd.get("ingame_testq")
    if not isinstance(blk, dict):
        return {}
    out, spent, backoff, faults = VF.waiting(w.t, blk, recs=list(w.lane_done))
    for mod, e in out.items():
        busy = w.in_lane(mod)
        for k, chains in e["checks"].items():
            left = [c for c in chains if c not in busy]
            if left:
                w.lane_queue.append({"mod": mod, "check": k, "chains": left})
    w._lane(w.t)
    return {m: v for m, v in spent.items() if m != "unread"}


def lane_reading(w):
    """The Workshop lane's reading (list_dispatch is another unit's): each open mod ticket, decision mod_work."""
    items = {}
    for m in w.mods.values():
        for iid in m.tickets:
            items[iid] = {"decision": "mod_work", "mod": m.name, "since": m.ticket_since or T0, "why": "waits on its mod"}
    _write(os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "reading.json"), {"at": w.t, "items": items})


# A paused row (maturation_autonomy._klass: every decision that neither launches, waits, rests nor is planned) is an
# alarm the Conductor sorts by hand. It is told, a state something ends, only when its pause is one the bars put there:
# a spent automatic try (one run per state, three cycles, one holder run per set: the pipeline did all it may) or a
# switch or cap the owner or the Conductor set (PAUSE_WHY's own words, maturation_autonomy.py). Any other pause (a
# non-build refusal, an input that cannot be read, a failed launch) in a world whose every input reads is the tick
# stopping on work it could do: the road-back hold read `blocked` with both games free (2026-11-25, 0.1 h seen).
SPENT_PAUSES = ("stopped", "steward_spent", "fixer_spent", "holder_spent", "auto_spent", "cycle_limit",
                "fix_chain_ended", "hand_run_seen")
SET_PAUSES = ("held", "no_cap", "blind_off", "ingame_off", "steward_off", "disabled", "designer_chain_cap", "ceiling",
              "owner_hold", "pipeline_paused", "control_off")


# The tick formats a caught exception as "ClassName: message", sometimes inside a longer reason.
ERROR_RE = re.compile(r"\b(?:[A-Z]\w*(?:Error|Exception)|Exception(?:Group)?|Stop(?:Async)?Iteration|"
                      r"TimeoutExpired|Unreadable):")


def told(row):
    """True when the row is a state something ends: a Conductor need line, a hold, a planned stop, or a pause the bars
    put there (SPENT_PAUSES, SET_PAUSES)."""
    return bool(row.get("need")) or row.get("klass") in ("held", "planned") or row.get("decision") in (
        SPENT_PAUSES + SET_PAUSES)


TICK_STAGES = ("offline_build", "blind_challenge", "in_game")


def done(w, mod):
    """A mod past the stage its regime starts it at is done for this sweep: the next stage is another regime's start
    (pre_human and his walk are other lanes')."""
    m = w.mods[mod]
    order = [x[0] for x in M.STAGES]
    if m.stage not in TICK_STAGES:
        return True
    return order.index(m.stage) > order.index(m.start)


# ---------------------------------------------------------------- one regime

def run_regime(reg, hours=24, trace=False):
    """-> {"stuck": [case], "worst": {...}, "cases": n, "touched": [...], "ticks": n, "s": seconds}."""
    import shutil
    sd = Path(os.environ["RM_MATURATION_DISPATCH_DIR"])
    shutil.rmtree(sd, ignore_errors=True)
    for p in (os.environ["RM_CONTROL_DB"],):
        if os.path.exists(p):
            os.remove(p)
    C.init(os.environ["RM_CONTROL_DB"])
    _write(os.environ["RM_OWNER_HOLD_FILE"], {"holds": [{"mod": mod, "said": "hold %s (sweep)" % mod, "date": "2026-11-27"}
                                                     for mod in reg.get("hold") or []]})
    root = str(ROOT / ("repo_%s" % reg["name"]))
    shutil.rmtree(root, ignore_errors=True)
    w = World(reg, root)
    for spec in reg["mods"]:
        m = Mod(**spec)
        w.mods[m.name] = m
        w.moved[m.name] = T0
        mdir = os.path.join(root, "design", "concepts", m.name, "version")
        os.makedirs(mdir, exist_ok=True)
        # the mod ledger (scratch copy under the regime's root) opens the version, as the Designer's lock does
        ML.append(root, m.name, "DISPATCH", "version.open", "version", body={"version": m.version}, version=m.version)
        if m.stage == "in_game":
            m.opened = m.opened or iso(T0 - 600)
            _write(os.path.join(mdir, "test_table.json"),
                   {"tests": {k: {"testq": {"chains": ch}} for k, ch in m.checks.items()}})
        if m.stage == "passed":
            _write(os.path.join(mdir, "stage_record.json"), {"stage": "passed", "version": m.version,
                                                              "since": iso(m.passed_at if m.passed_at else T0)})
    cfg = dict(MD.load_cfg(), advancing=[m.name for m in w.mods.values()])
    fx = stand_ins(w)
    for k, v in (reg.get("fx") or {}).items():
        fx[k] = v
    ledger = []
    model_read = model.read
    model.read = lambda path=None: list(ledger)
    unit_state = RL.unit_state      # systemd: the world's units are active until they end; any other is not found
    RL.unit_state = lambda unit, runner=None: ("active" if w.unit_active(unit) else "inactive") if unit in w.runs \
        else "not-found"
    stuck, worst, cases, ticks = {}, {"mod": (0, None), "ticket": (0, None), "chain": (0, None)}, 0, 0
    t_start = time.time()
    t_zero = T0 + reg.get("offset", 0)
    rows_of = {}
    try:
        for step in range(int(hours * 3600 // STEP_S)):
            t = t_zero + step * STEP_S
            w.advance(t)
            lane_reading(w)
            rd = MD.tick(root, cfg, True, fx=fx, now=t, page=False)
            ticks += 1
            spent = feed_step(w, rd)
            stops, cause = CS.load(now=t, root=os.path.join(root, "design", "concepts"))
            listed = {i for r in (stops or []) for i in r["items"]}
            w.after_tick()
            rows = rd.get("mods") or {}
            for mod in w.mods:
                cases += 1
                row = rows.get(mod) or {}
                rows_of.setdefault(mod, []).append((t, row.get("decision"), (row.get("why") or ""), row.get("klass"),
                                                    (row.get("need") or "")))
                swallowed = ERROR_RE.search(str(row.get("why") or ""))
                if swallowed:      # a stand-in that breaks the real contract, or a real fault: either way not a pass
                    stuck.setdefault(("error", mod), {"kind": "error", "what": mod, "since": t, "at": t,
                                                      "decision": row.get("decision"), "why": row.get("why")})
                if w.world_holds(mod, t) or w.run_ends(mod):
                    w.moved[mod] = max(w.moved[mod], t)     # the world ends this state: a window, or a run with an end
                if done(w, mod) or told(row):
                    w.moved[mod] = t
                    continue
                still = t - w.moved[mod]
                if still > worst["mod"][0]:
                    worst["mod"] = (still, mod)
                if still > STILL_LIMIT_S:
                    stuck.setdefault(("mod", mod), {"kind": "mod", "what": mod, "since": w.moved[mod], "at": t,
                                                    "decision": row.get("decision"), "why": row.get("why")})
            for m in w.mods.values():
                if m.stage != "passed" or not m.passed_at:
                    continue
                for iid in m.tickets:
                    cases += 1
                    age = t - max(m.passed_at, m.ticket_since or T0)
                    if iid in listed:
                        continue
                    if age > worst["ticket"][0]:
                        worst["ticket"] = (age, iid)
                    if age > TICKET_LIMIT_S:
                        stuck.setdefault(("ticket", iid), {"kind": "ticket", "what": "%s (%s rests)" % (iid, m.name),
                                                           "since": m.passed_at, "at": t, "why": cause or
                                                           "not on the Conductor's owed list"})
            for mod, chains in spent.items():
                for c in chains:
                    cases += 1
                    tries = w.chain_tries.get((mod, c), [])
                    if tries and all(x == "REFUSED" for x in tries):     # never measured: the lane refused each run
                        stuck.setdefault(("chain", mod, c), {"kind": "chain", "what": "%s %s" % (mod, c), "since": t,
                                                             "at": t, "why": "spent by %d lane refusal(s), never run; "
                                                             "nothing sends it again in this visit" % len(tries)})
                        worst["chain"] = (max(worst["chain"][0], len(tries)), "%s %s" % (mod, c))
        # the day's end: a mod that moves (runs that end, relaunched) but never leaves its start stage, and is not told,
        # is a loop nothing ends; every regime's windows close by +6 h, so a day is time enough for each start stage
        for mod in w.mods:
            cases += 1
            row = (rd.get("mods") or {}).get(mod) or {}
            if not (done(w, mod) or told(row)):
                stuck.setdefault(("mod", mod), {"kind": "day", "what": mod, "since": t_zero, "at": t,
                                                "decision": row.get("decision"), "why": "never left %s in %d h: %s" % (
                                                    w.mods[mod].stage, hours, row.get("why"))})
    finally:
        model.read, RL.unit_state = model_read, unit_state
    return {"name": reg["name"], "stuck": list(stuck.values()), "worst": worst, "cases": cases, "ticks": ticks,
            "touched": list(TOUCHED), "s": round(time.time() - t_start, 1), "events": w.events, "rows": rows_of}


# ---------------------------------------------------------------- the regimes (progress.md: the range, written first)
H = 3600
# the mods the tick launches on, one per state its stage can stand in (Mod's fields; names are the world's own)
BASES = {
    # in_game, the exit refused only by the stale walk build: the tick's deploy unit owns it (9f802d6866)
    "stale": [{"name": "Ek", "stage": "in_game", "why": [STALE]}],
    # in_game, the exit owing testq checks that Steve's lane measures (the visit feed sends them)
    "visit": [{"name": "Fw", "stage": "in_game", "checks": {"c1": ["x1"], "c2": ["x2", "x3"]}}],
    # in_game, every check met: the steward confirms the exit
    "met": [{"name": "Mt", "stage": "in_game"}],
    # offline_build on its road back: the hold's open items are the holder's work (2026-11-25 road-back boundary)
    "road": [{"name": "Ekb", "stage": "offline_build", "road_back": ["RIMMANDRAKE_RB1", "RIMMANDRAKE_RB2"]}],
    # passed half an hour ago and resting, two mod_work tickets still open (Gimme Some Slack, 2026-11-24)
    "rest": [{"name": "Gss", "stage": "passed", "passed_at": T0 - 1800, "tickets": ["RIMMANDRAKE_A", "RIMMANDRAKE_B"]}],
}
BASES["mixed"] = [dict(x) for k in ("stale", "visit", "road", "rest") for x in BASES[k]]
# what the world does to them: each window is a cause the world ends by itself (or the owner does)
WINDOWS = {
    "calm": {},
    "lane_refuses_1h": {"lane_refuses": [(T0, T0 + H)]},
    "lane_refuses_6h": {"lane_refuses": [(T0, T0 + 6 * H)]},
    "account_shut_2h": {"account_shut": [(T0 + H, T0 + 3 * H)]},
    "games_taken_3h": {"bridge_busy": [(T0, T0 + 3 * H)]},
    "archbig_down_2h": {"game_down": {"a": [(T0 + 2 * H, T0 + 4 * H)]}},
    "owner_hold_4h": {"hold_mod": True, "hold_until": T0 + 4 * H},
    "steward_gives_up": {"gives_up_s": 2 * H},     # the measured steward that gave up after two hours (9f802d6866)
    "long_runs": {"run_s": 3 * H},      # a builder's run of 3 h: longer than the still limit, and still moving
}
OFFSETS = (0, STEP_S // 2)       # the clock's phase against the runs' ends: on a step, and half a step after one


QUICK_HOURS = 12     # every window ends by +6 h and every limit is under 2 h: 12 h reads each one end and a limit past it


def regime(base, window, offset=0, hours=24):
    reg = dict(WINDOWS[window], name="%s.%s.%d" % (base, window, offset), offset=offset, hours=hours,
               mods=[dict(x, why=list(x.get("why") or [])) for x in BASES[base]])
    if reg.pop("hold_mod", False):
        reg["hold"] = [reg["mods"][0]["name"]]
    return reg


def grid(quick=False):
    """-> every regime. quick: every base under calm and every window on the mixed world, offset 0 (what ./publish
    runs); the full grid is every base x window x offset."""
    if quick:
        return [regime(b, "calm", hours=QUICK_HOURS) for b in BASES] + [
            regime("mixed", w, hours=QUICK_HOURS) for w in WINDOWS if w != "calm"]
    return [regime(b, w, o) for b in BASES for w in WINDOWS for o in OFFSETS]


# ---------------------------------------------------------------- the measured faults, planted (each a reversal)
class Plant:
    """A monkeypatch that puts a measured fault back into the shipped code for a `with` block."""

    def __init__(self, name, why, put):
        self.name, self.why, self._put, self._undo = name, why, put, []

    def __enter__(self):
        self._undo = self._put()
        return self

    def __exit__(self, *a):
        for obj, attr, old in reversed(self._undo):
            setattr(obj, attr, old)


def _swap(*triples):
    undo = [(o, a, getattr(o, a)) for o, a, _ in triples]
    for o, a, v in triples:
        setattr(o, a, v)
    return undo


def _plant_rest():
    rows = CS.rows
    return _swap((CS, "rows", lambda *a, **k: [r for r in rows(*a, **k) if r.get("kind") != "mod_rest"]))


def _plant_refused():
    of = FC.of_testq

    def counted(rec, c=None):
        if (rec.get("result") or {}).get("outcome") == "REFUSED":
            return FC.read(FC.BAD_REQUEST, "a refused load read as the check's own failure")
        return of(rec, c)
    return _swap((VF, "LANE_REFUSALS", set()), (T, "ARCH_BOUNCE", set()), (FC, "of_testq", counted))


def _plant_steward_deploy():
    return _swap((AUT, "_stale_walk", lambda f: None))


def _plant_road_back():
    return _swap((MD, "road_back_decide", lambda mod, f, row, put: put("blocked", "refused by road_back_items, not "
                                                                         "build work")))


def _plant_relaunch_loop():
    # the day-end check's own probe: no once-per-key gate, and the stale walk build back with a steward that gives up
    return _plant_steward_deploy() + _swap((AUT, "_retriable", lambda x, cfg, mod: True))


PLANTS = {
    # 07441d68f4: a passed mod rests and its open tickets were on no owed list (Gimme Some Slack, 45 h)
    "rest": Plant("rest", "conductor_stops lists no mod_rest row", _plant_rest),
    # 5d09ae880d: a lane refusal (LOAD) was counted as the check's visit failure and spent it
    "refused": Plant("refused", "visit_feed counts a REFUSED load as a failed run", _plant_refused),
    # 9f802d6866: the stale walk build went to a steward, which may not stop ArchBig to deploy it
    "steward_deploy": Plant("steward_deploy", "the stale walk build is a steward's, not the deploy unit's",
                            _plant_steward_deploy),
    # 2026-11-25 road-back hold: the offline build read `blocked` on road_back_items with both games free
    "road_back": Plant("road_back", "road_back_items reads blocked, not the holder's work", _plant_road_back),
    # the day-end check's probe (no measured fault): a steward relaunched for good on a state it cannot move; with the
    # regime's give-up window each run ends, so only the day's end sees the mod never left in_game
    "relaunch_loop": Plant("relaunch_loop", "the once-per-key steward gate removed, the stale walk build a steward's",
                           _plant_relaunch_loop),
}


# ---------------------------------------------------------------- the report

def sweep(regs, plant=None, rows=False):
    """-> {"results": [...], "stuck": n, "touched": n, "worst": {kind: (value, what, regime)}, "cases": n, "s": s}."""
    out = {"results": [], "stuck": 0, "touched": 0, "cases": 0, "ticks": 0,
           "worst": {"mod": (0, None, None), "ticket": (0, None, None), "chain": (0, None, None)}}
    t0 = time.time()
    for reg in regs:
        del TOUCHED[:]
        if plant:
            with PLANTS[plant]:
                r = run_regime(reg, hours=reg.get("hours", 24))
        else:
            r = run_regime(reg, hours=reg.get("hours", 24))
        if not rows:
            r.pop("rows", None)       # a day of rows per mod: only `one` prints them
        out["results"].append(r)
        out["stuck"] += len(r["stuck"])
        out["touched"] += len(r["touched"])
        out["cases"] += r["cases"]
        out["ticks"] += r["ticks"]
        for k, (v, what) in r["worst"].items():
            if v > out["worst"][k][0]:
                out["worst"][k] = (v, what, r["name"])
    out["s"] = round(time.time() - t0, 1)
    return out


LIMITS = {"mod": STILL_LIMIT_S, "ticket": TICKET_LIMIT_S, "chain": 0}


def report(out):
    lines = ["tick sweep: %d regime(s), %d tick(s), %d case(s) read, %.1f s" % (
        len(out["results"]), out["ticks"], out["cases"], out["s"])]
    for k, (v, what, reg) in out["worst"].items():
        unit = "refused tries of a spent check" if k == "chain" else "s"
        lines.append("  worst %-6s %8.0f %s (limit %s %s; %s in %s)" % (k, v, unit, LIMITS[k] if k != "chain" else
                                                                       "0 spent unrun", "" if k == "chain" else "s",
                                                                       what, reg))
    lines.append("  world touched: %d process/socket call(s)" % out["touched"])
    for r in out["results"]:
        for c in r["stuck"]:
            lines.append("  STUCK %s %s: %s (still since %+d min, read at %+d min; %s)" % (
                r["name"], c["kind"], c["what"], (c["since"] - T0) // 60, (c["at"] - T0) // 60,
                (c.get("decision") or "") + " " + str(c.get("why") or "")))
        for x in r["touched"][:3]:
            lines.append("  TOUCHED %s: %s" % (r["name"], x))
    lines.append("RESULT: %s" % ("CLEAN" if not out["stuck"] and not out["touched"] else "STUCK %d, TOUCHED %d" % (
        out["stuck"], out["touched"])))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("grid")
    g.add_argument("--quick", action="store_true")
    g.add_argument("--plant", choices=sorted(PLANTS))
    g.add_argument("--base", choices=sorted(BASES), help="the full grid of one base world only")
    o = sub.add_parser("one")
    o.add_argument("regime", help="<base>.<window>.<offset>, e.g. road.calm.0")
    o.add_argument("--plant", choices=sorted(PLANTS))
    a = ap.parse_args(argv)
    if a.cmd == "grid":
        out = sweep([r for r in grid(a.quick) if not a.base or r["name"].startswith(a.base + ".")], a.plant)
        print(report(out))
        return 0 if not out["stuck"] and not out["touched"] else 1
    base, window, offset = a.regime.split(".")
    out = sweep([regime(base, window, int(offset))], a.plant, rows=True)
    print(report(out))
    for mod, rows in (out["results"][0].get("rows") or {}).items():
        last = None
        for t, d, why, kl, need in rows:
            if (d, why[:60]) != last:
                print("  +%4d min %-8s %-14s %-8s %s%s" % ((t - T0) // 60, mod, d, kl, why,
                                                        " NEED: " + need if need else ""))
                last = (d, why[:60])
    for e in out["results"][0]["events"]:
        print("  event +%4d min %s %s" % ((e[0] - T0) // 60, e[1], e[2]))
    return 0 if not out["stuck"] and not out["touched"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        import shutil
        shutil.rmtree(ROOT, ignore_errors=True)
