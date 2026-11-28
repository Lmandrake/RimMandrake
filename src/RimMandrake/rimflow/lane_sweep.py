#!/usr/bin/env python3
"""lane_sweep.py - the offline sweep of the ticket lane and the work bundles: no state that nothing ends.

It runs the REAL list_dispatch.tick (gather, decide, execute), work_bundle (launch, overlay, the restart rule, note_end),
left_open_continue (at_finish, the continuation step run) and conductor_stops (the Conductor's stops view) over a
simulated day on a fake clock, one regime at a time. Stand-ins replace only what touches the world: the ledger store
(a list of events in memory, folded by the real model.replay), the run records, bundle store, lane state and Conductor
log (a scratch folder), helper launches (a record and a scheduled end), the worker inside each run (a script of ledger
acts per run), the machine load, the account gate, ssh hosts, games, mod folders and the outcome check (it fails while
the ticket is open). Page: design/specs/2026-11-27-lane-bundle-sweep/boundary.md. Item:
RIMMANDRAKE_BUILD_LANE_BUNDLE_SWEEP_FIVE_STUCK_STATES_SEEN.

On every tick it reads each open ticket's lane row and each bundle record and asks: what ends this state?
  - a run state (launched, in_bundle, bundled, bundle_live, live, claimed) needs a run that is running, or a
    continuation step that is due, for that ticket or bundle;
  - slots_full needs a running run; waiting needs a dated wait still ahead; waits_on and blocked need an open
    predecessor; system_wait needs its hour still ahead; bundle_hold needs its hold's end (hold_until) still ahead;
  - a hand state (conductor_stops.KINDS, machine_load) needs someone told: a row of the Conductor's stops view or a
    Conductor need line since it began, within REST_S + one tick;
  - a live bundle (work_bundle.LIVE_STATES) needs a running unit or a due continuation step of its own.
A state that fails its ender for two ticks is a finding (no_ender); a hand state nobody was told of is `untold`; a
Conductor act that does not end the state it answered is `act_did_not_end`; a Conductor line that claims a daily
limit it is over ("N of at most M today", N > M) is `false_count`; a home's ready tickets launched apart is `split`.

The Conductor stand-in acts on what it is told: a chain stop or a stop gets `list_dispatch.py clear` twice, then a
24 h wait; a machine-load hold gets the outside load ended; another hand state gets a 24 h wait.

Deterministic: no network, no live game, no model call; writes only under a temp folder it deletes.
  python3 lane_sweep.py [--regime NAME ...] [--plant NAME]     -> findings, cases, worst; exit 1 on a finding
"""
import argparse
import calendar
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

T0 = calendar.timegm((2026, 11, 27, 0, 0, 0))     # a fixed day: the sweep is the same on every run
TICK_S = 600        # src/RimMandrake/Utils/systemd/rm-list-dispatch.timer: OnUnitActiveSec=10min
TICKS = 144         # one day of ticks
# budget: danger=a simulated run that never ends would leave the sweep's fake day with no run end to read; ends no work: a simulated run ends at this simulated time
RUN_S = 2400        # a sim run's length (40 min); the death regime's first run ends at DEATH_S
DEATH_S = 600
STEP_S = 60         # finish kicks the continuation step; the step runs this much later
# budget: danger=a Conductor stand-in that never acts would leave a stopped ticket stopped for the whole fake day; ends no work: the stand-in's dated wait passes in sim time
HAND_WAIT_S = 86400     # the Conductor stand-in's dated wait, when it neither clears nor ends a load
CLEARS = 2          # list_dispatch.py clear, this many times per ticket, then a dated wait
CORES = 14          # Archmagi (list_dispatch.json _machine_load_per_core_doc: "28 on 14")
HIGH_LOAD = 30      # over the machine's line of 2 x 14 = 28 (list_dispatch.json machine_load_per_core)
SEAT = "BENCH"

RUN_STATES = ("launched", "in_bundle", "bundled", "bundle_live", "live", "claimed")
HAND = ("chain_stop", "stopped", "machine_load", "close_refused", "adopt_too_heavy", "no_bundle")
LINE_RX = re.compile(r"\((\d+) of at most (\d+) today\)")


def P(x):
    return "RIMMANDRAKE_SIM_" + x


# ---- the range: each regime is a world the lane can meet ------------------------------------------------------------
# tickets: [(id, {file fields})]; acts: {id: ([act of its 1st, 2nd .. run], act after)}; an act is close | none |
# left_open | refuse | wait | ("file", child id) (the run files a ticket caused by this one, then closes this one).
REGIMES_SPEC = {
    "idle": {"tickets": []},
    "block": {"tickets": [(P("BLK_A"), {}), (P("BLK_B"), {})], "blocks": {P("BLK_B"): P("BLK_A")},
              "acts": {P("BLK_A"): (["close"], "close"), P("BLK_B"): (["close"], "close")}},
    "chain": {"tickets": [(P("CHN_A"), {})],
              "acts": {P("CHN_A"): ([("file", P("CHN_B"))], "close"), P("CHN_B"): ([("file", P("CHN_C"))], "close"),
                       P("CHN_C"): (["close"], "close")}},
    "load_held": {"tickets": [(P("LDH_A"), {})], "load": "held", "acts": {P("LDH_A"): (["close"], "close")}},
    "load_burst": {"tickets": [(P("LDB_A"), {})], "load": "burst", "acts": {P("LDB_A"): (["close"], "close")}},
    "bundle_left_open": {"tickets": [(P("BLO_M%d" % k), {}) for k in range(1, 7)],
                         "homes": {P("BLO_M%d" % k): "pipeline:sim-bundle" for k in range(1, 7)},
                         "acts": dict([(P("BLO_M%d" % k), (["none"] * (k - 1) + ["close"], "close")) for k in range(1, 6)]
                                      + [(P("BLO_M6"), ([], "left_open"))])},
    "home": {"tickets": [(P("HOM_P"), {}), (P("HOM_C1"), {"caused_by": P("HOM_P")}),
                         (P("HOM_C2"), {"caused_by": P("HOM_P")})],
             "homes": {P("HOM_P"): "pipeline:sim-home"}, "group": [P("HOM_P"), P("HOM_C1"), P("HOM_C2")],
             "acts": {P("HOM_P"): (["close"], "close"), P("HOM_C1"): (["close"], "close"),
                      P("HOM_C2"): (["close"], "close")}},
    "death": {"tickets": [(P("DTH_A"), {})], "death": True, "acts": {P("DTH_A"): (["close"], "close")}},
    "refuse": {"tickets": [(P("REF_A"), {})], "acts": {P("REF_A"): (["refuse"], "refuse")}},
    "wait": {"tickets": [(P("WAI_A"), {})], "acts": {P("WAI_A"): (["wait"], "close")}},
}
REGIMES = list(REGIMES_SPEC)
LEFT_OUT = ("ssh hosts (SteveDesktop): a launch there is an ssh call, the world",
            "onboarding runs of old tickets with no check, judge and game routes, Shape: other units' rows",
            "mod work (mod_work rows): the maturation lane's, another sweep's",
            "a block with no predecessor (owner, judge, live, external): its ender is a person, out of the lane",
            "the account gate held: account_plan_sweep.py sweeps it")


# ---- plants: a reversal of each fix, so the sweep is seen to find what it was built to find -------------------------
def _old_block_facts(world, x, now):
    """block_facts as it read before its fix: a closed predecessor still blocks (evidence rank 2, 16 h)."""
    import list_dispatch as LD
    waits = [b for b in (x.blocked_on,) + tuple(x.blocked_also or ())
             if b and b in world.items and world.items[b].state not in LD.CLOSED]
    return waits, bool(x.blocked) and not waits


def _old_continued_line(unit, rec, p, new, lad, sid, fresh_why):
    """left_open_continue's continuation line as it read before its fix: a daily count for a bundle too."""
    import left_open_continue as LOC
    return "%s on %s ended with work left (%s); continued as %s on %s, %s, %s (%d of at most %d today)" % (
        unit, rec["item"], p.get("why"), new, p["target"],
        ("EFFORT LADDER: " + lad["why"]) if lad else "same model %s" % rec.get("model"),
        "its session resumed" if sid else "fresh: " + str(fresh_why), p["n"], LOC.MAX_PER_DAY)


PLANTS = ("block_on_done", "chain_no_row", "load_no_row", "loc_old_line", "system_per_ticket")


@contextlib.contextmanager
def planted(name):
    import conductor_stops as CS
    import left_open_continue as LOC
    import list_dispatch as LD
    import work_bundle as WB
    with contextlib.ExitStack() as es:
        if name == "block_on_done":
            es.enter_context(mock.patch.object(LD, "block_facts", _old_block_facts))
        elif name == "chain_no_row":
            es.enter_context(mock.patch.dict(CS.KINDS))
            CS.KINDS.pop("chain_stop", None)
        elif name == "load_no_row":
            if hasattr(CS, "NOTICED"):      # before its fix the shipped view had no notice: nothing to take away
                es.enter_context(mock.patch.dict(CS.NOTICED))
                CS.NOTICED.clear()
        elif name == "loc_old_line":
            if hasattr(LOC, "continued_line"):      # before its fix the shipped line was the old one
                es.enter_context(mock.patch.object(LOC, "continued_line", _old_continued_line))
        elif name == "system_per_ticket":
            orig = WB.system_of
            es.enter_context(mock.patch.object(WB, "system_of", lambda it, reading, items=None: orig(it, reading, None)))
        elif name:
            raise ValueError("no plant %r (plants: %s)" % (name, ", ".join(PLANTS)))
        yield


# ---- the simulated world ---------------------------------------------------------------------------------------------
def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


class Sim(object):
    def __init__(self, regime, root):
        self.regime, self.spec, self.d = regime, REGIMES_SPEC[regime], root
        self.now = T0 - 3600
        self.evs, self.tsn = [], 0
        self.pending = []           # [(t, seq, kind, unit)]
        self.seq = 0
        self.running = {}           # unit -> {"items": [...], "bundle": id or None}
        self.ran = {}               # ticket -> runs ended that held it
        self.needs = []             # [(t, text)]
        self.acted = {}             # (ticket, decision) -> t of the Conductor stand-in's act
        self.clears = {}
        self.outside = HIGH_LOAD if self.spec.get("load") in ("held", "burst") else 0.0
        self.findings, self.cases = [], 0
        self.holds = {}             # (kind, key) -> first t its ender was missing
        self.worst = (0, TICK_S, None)
        self.units = 0
        self.deaths = 1 if self.spec.get("death") else 0
        for sub in ("ld", "wb", "state", "items", "projects"):
            os.makedirs(os.path.join(root, sub), exist_ok=True)

    # the ledger store (the real model folds it)
    def add(self, ev):
        self.tsn += 1
        e = dict({"seat": SEAT, "ts": iso(self.now), "tsn": self.tsn}, **ev)
        self.evs.append(e)
        return e

    def world(self):
        import model as LM
        return LM.replay(list(self.evs))

    def seed(self):
        for iid, extra in self.spec["tickets"]:
            self.file(iid, extra)
        for iid, home in sorted((self.spec.get("homes") or {}).items()):
            self.add({"event": "home", "id": iid, "home": home, "group": "sim", "flag": "LOOKS CURRENT"})
        for iid, on in sorted((self.spec.get("blocks") or {}).items()):
            self.add({"event": "block", "id": iid, "on": on, "kind": "item", "reason": "after %s" % on})

    def file(self, iid, extra=None, unit=None):
        self.add(dict({"event": "file", "id": iid, "title": "sim ticket %s" % iid, "kind": "task", "for": SEAT,
                       "effect": "cmd:false"}, **dict(extra or {}, **({"role_unit": unit} if unit else {}))))
        self.add({"event": "claim", "id": iid, "why": "sim: started work"})

    # the worker inside a run: its ledger acts at the run's end
    def work(self, unit, items):
        w = self.world()
        for m in items:
            x = w.items.get(m)
            if x is None or x.state in ("done", "dropped", "superseded"):
                continue
            k = self.ran.get(m, 0)
            self.ran[m] = k + 1
            seq, after = (self.spec.get("acts") or {}).get(m, ([], "none"))
            act = seq[k] if k < len(seq) else after
            if isinstance(act, tuple) and act[0] == "file":
                if act[1] not in w.items:
                    self.file(act[1], {"caused_by": m}, unit=unit)
                act = "close"
            if act == "close":
                self.add({"event": "close", "id": m, "sha": "0000000", "noCode": "sim: the worker's fix"})
            elif act == "left_open":
                self.add({"event": "note", "id": m, "text": "LEFT OPEN: done: one part; next: the second part (sim)"})
            elif act == "refuse":
                self.add({"event": "note", "id": m, "text": "REFUSED BY BUNDLE: needs the full mod list (sim)"})
            elif act == "wait":
                self.add({"event": "wait", "id": m, "until": iso(self.now + 3 * 3600), "reason": "sim: a dated wait"})

    # stand-ins for the world's doors
    def launch_lane(self, item, model, cap, brief, seat, mod, host=None, env=None):
        import detached_helper as DH
        self.units += 1
        unit = "sim-%s-%d" % (self.regime, self.units)
        rec = {"unit": unit, "item": item, "seat": seat, "at": self.now, "status": "running", "env": dict(env or {}),
               "next_act_owner": "list_dispatch", "model": model, "state": os.path.join(self.d, "state"),
               "max_s": "none", "budget_usd": cap or 0.0}
        DH.write_record(rec)
        self.start(unit, item, (env or {}).get("RM_WORK_BUNDLE"))
        return 0, "DETACHED %s (sim)" % unit, unit

    def launch_continue(self, seat, target, text, model, max_s, budget, now=None, env=None, clone=None, extra=None,
                        skip_launch_checks=None, resume_session=None, projects=None):
        import detached_helper as DH
        self.units += 1
        unit = "sim-%s-%d" % (self.regime, self.units)
        rec = dict(extra or {}, unit=unit, item=target, seat=seat, at=self.now, status="running", env=dict(env or {}),
                   model=model, state=os.path.join(self.d, "state"), max_s=max_s, budget_usd=budget)
        DH.write_record(rec)
        self.start(unit, target, (env or {}).get("RM_WORK_BUNDLE"))
        return 0, "DETACHED %s (sim)" % unit

    def start(self, unit, item, bundle):
        import work_bundle as WB
        items = [item]
        if bundle:
            b = _must(WB.store_read(bundle), "bundle %s" % bundle)
            items = list(b.get("members") or [item])
        self.running[unit] = {"items": items, "bundle": bundle}
        dies = self.deaths > 0
        if dies:
            self.deaths -= 1
        self.later(self.now + (DEATH_S if dies else RUN_S), "end:killed: signal 9" if dies else "end", unit)

    def later(self, t, kind, unit):
        self.seq += 1
        self.pending.append((t, self.seq, kind, unit))
        self.pending.sort()

    def need(self, text, now):
        self.needs.append((now, str(text)))

    def read_members(self, clone, ids):
        """work_bundle.read_members, its own READ_MEMBERS script run in this process over the sim ledger."""
        import work_bundle as WB
        out, argv, path = io.StringIO(), sys.argv, list(sys.path)
        try:
            sys.argv = ["read_members"] + list(ids)
            with contextlib.redirect_stdout(out):
                exec(compile(WB.READ_MEMBERS, "READ_MEMBERS", "exec"), {"__name__": "__read_members__"})
        finally:
            sys.argv, sys.path[:] = argv, path
        return json.loads(out.getvalue())

    def read_item(self, item):
        w = self.world()
        x = w.items.get(item)
        if x is None:
            return None
        return {"state": x.state, "wait_until": x.wait_until, "home": (getattr(x, "home", None) or {}).get("home"),
                "notes": [e for e in self.evs if e.get("id") == item and e.get("event") == "note"]}

    # the run's end and the continuation step: the real left_open_continue
    def end(self, unit, result):
        import detached_helper as DH
        import left_open_continue as LOC
        run = self.running.pop(unit, None) or {"items": [], "bundle": None}
        if not result.startswith("killed"):
            self.work(unit, run["items"])
        rec = _must(DH.read_record(unit), "run record %s" % unit)
        rec.update(status="finished", result=result, ended_at=self.now)
        DH.write_record(rec)

        def continuer(fresh, p):
            self.later(self.now + STEP_S, "step", fresh["unit"])
            return "continue kicked %s-continue (sim)" % fresh["unit"]
        LOC.at_finish(rec, self.read_item(rec.get("item")), self.d, self.now, continuer=continuer,
                      states_reader=self.read_members)

    def step(self, unit):
        import left_open_continue as LOC
        LOC.run(unit, self.now, launch_fn=self.launch_continue, reader=self.read_item,
                projects=os.path.join(self.d, "projects"), plan_dir=os.path.join(self.d, "plan"))

    def due(self, t):
        while self.pending and self.pending[0][0] <= t:
            at, _s, kind, unit = self.pending.pop(0)
            self.now = at
            if kind == "step":
                self.step(unit)
            else:
                self.end(unit, kind[4:] if kind.startswith("end:") else "success (exit 0)")
        self.now = t

    def load(self):
        if self.spec.get("load") == "burst" and self.now >= T0 + 2400:
            self.outside = 0.0      # an outside burst that falls by itself after 40 min
        return float(self.outside)

    # the Conductor stand-in: it acts on what it is told
    def conduct(self, rd, told):
        import list_dispatch as LD
        for iid, d in sorted(told.items()):
            key = (iid, d)
            since = ((rd.get("items") or {}).get(iid) or {}).get("since") or self.now
            if self.acted.get(key, -1) >= since:
                continue
            self.acted[key] = self.now
            if d in ("chain_stop", "stopped") and self.clears.get(iid, 0) < CLEARS:
                self.clears[iid] = self.clears.get(iid, 0) + 1
                with contextlib.redirect_stdout(io.StringIO()):
                    LD.main(["clear", iid, "--why", "sim Conductor: one more run"])
            elif d == "machine_load":
                self.outside = 0.0      # the Conductor names what holds the load and ends it
            else:
                self.add({"event": "wait", "id": iid, "until": iso(self.now + HAND_WAIT_S),
                          "reason": "sim Conductor: %s, looked at" % d})


# ---- the checks ----------------------------------------------------------------------------------------------------
def told_of(rd, now, needs, iid, since):
    import conductor_stops as CS
    if any(iid in r.get("items") or [] for r in CS.rows(rd, now)):
        return "row"
    if any(t >= (since or 0) and iid in text for t, text in needs):
        return "need line"
    return None


def check(sim, rd):
    """One tick's look at every open sim ticket and every bundle. -> {ticket: hand decision} that someone was told of."""
    import conductor_stops as CS
    import work_bundle as WB
    now, w = sim.now, sim.world()
    rows = rd.get("items") or {}
    active = set(m for r in sim.running.values() for m in r["items"])
    stepping = set(u for (_t, _s, k, u) in sim.pending if k == "step")
    live_bundles = set(r["bundle"] for r in sim.running.values() if r["bundle"])
    import detached_helper as DH
    for u in stepping:
        b = _must(DH.read_record(u), "run record %s" % u).get("env", {}).get("RM_WORK_BUNDLE")
        if b:
            live_bundles.add(b)
            active.update(_must(WB.store_read(b), "bundle %s" % b).get("members", []))
    told, bad = {}, {}
    sim.cases += 1                  # the tick itself
    for iid, x in sorted(w.items.items()):
        if not iid.startswith(P("")) or x.state in ("done", "dropped", "superseded"):
            continue
        sim.cases += 1
        r = rows.get(iid)
        d = (r or {}).get("decision") or "(no row)"
        since = (r or {}).get("since")
        on = x.blocked_on
        on_open = bool(on) and on in w.items and w.items[on].state not in ("done", "dropped", "superseded")
        if d in RUN_STATES:
            ok = iid in active
        elif d == "slots_full":
            ok = bool(sim.running)
        elif d == "waiting":
            ok = bool(x.wait_until) and _epoch(x.wait_until) > now
        elif d in ("waits_on", "blocked"):
            ok = on_open
        elif d == "system_wait":
            ok = isinstance(since, (int, float)) and since + 3600 > now
        elif d == "bundle_hold":    # work_bundle.hold_systems: the hold ends at hold_until, or earlier at five ready
            hu = (r or {}).get("hold_until")
            ok = isinstance(hu, (int, float)) and hu > now
        elif d in HAND:
            how = told_of(rd, now, sim.needs, iid, since)
            if how:
                told[iid] = d
                ok = True
            else:
                hold(sim, "untold", iid, d, since if isinstance(since, (int, float)) else now,
                     CS.REST_S + TICK_S, "a hand state nobody is told of: no stops row, no need line since it began")
                ok = True       # its own clock; not a no_ender
        else:
            ok = False
        if not ok:
            bad[iid] = d
        key = (iid, d)
        if d in told.values() and key in sim.acted and sim.acted[key] >= (since or 0) and \
                now - sim.acted[key] >= 2 * TICK_S and told.get(iid) == d:
            sim.findings.append({"kind": "act_did_not_end", "regime": sim.regime, "item": iid, "decision": d,
                                 "t": now, "why": "the Conductor acted at %s and %s still holds" % (
                                     iso(sim.acted[key]), d)})
    for iid, d in bad.items():
        hold(sim, "no_ender", iid, d, None, TICK_S, "no later step of the code ends it: %s" % (
            (rows.get(iid) or {}).get("why") or "no lane row"))
    for k in list(sim.holds):
        if k[0] == "no_ender" and bad.get(k[1]) != k[2]:
            sim.holds.pop(k)
    for bid, b in sorted(WB.all_bundles().items()):
        sim.cases += 1
        if b.get("state") in WB.LIVE_STATES and bid not in live_bundles:
            hold(sim, "no_ender", bid, "bundle " + str(b.get("state")), None, TICK_S,
                 "a live bundle with no running unit and no continuation step due")
        else:
            sim.holds.pop(("no_ender", bid, "bundle " + str(b.get("state"))), None)
    split(sim, w)
    return told


def hold(sim, kind, key, d, since, limit, why):
    k = (kind, key, d)
    # a state with its own start (since) is aged from it, so a second spell of one decision is not aged from the first
    first = since if since is not None else sim.holds.setdefault(k, sim.now)
    age = sim.now - first
    if age / float(limit) > sim.worst[0] / float(sim.worst[1]):
        sim.worst = (age, limit, "%s %s %s in %s" % (kind, key, d, sim.regime))
    if age >= limit and not any(f["kind"] == kind and f["item"] == key and f.get("decision") == d
                                for f in sim.findings):
        sim.findings.append({"kind": kind, "regime": sim.regime, "item": key, "decision": d, "t": sim.now,
                             "held_s": age, "limit_s": limit, "why": why})


def split(sim, w):
    """A home's ready tickets launch as one bundle: a bundle that holds part of a declared group while another open,
    ready mate is in no live bundle is a split."""
    import work_bundle as WB
    group = sim.spec.get("group")
    if not group:
        return
    bundles = WB.all_bundles()
    for bid, b in sorted(bundles.items()):
        if b.get("at") != sim.now or not set(b.get("members") or []) & set(group):
            continue
        sim.cases += 1
        busy = set(m for o in bundles.values() if o.get("state") in WB.LIVE_STATES for m in o.get("members") or [])
        out = [m for m in group if m not in (b.get("members") or []) and m in w.items
               and w.items[m].state not in ("done", "dropped", "superseded") and not w.items[m].blocked
               and not w.items[m].wait_until and m not in busy]
        out += [m for m in group if m in busy and m not in (b.get("members") or [])]
        if out:
            sim.findings.append({"kind": "split", "regime": sim.regime, "item": bid, "decision": "launch", "t": sim.now,
                                 "why": "bundle %s of %s holds %s; its home's mates %s launch apart" % (
                                     bid, b.get("system"), ", ".join(b.get("members") or []), ", ".join(out))})


def counts(sim):
    """The Conductor log's daily counts: a line over its own limit is false."""
    p = os.path.join(sim.d, "conductor.log")
    if not os.path.isfile(p):
        return
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            sim.cases += 1
            m = LINE_RX.search(line)
            if m and int(m.group(1)) > int(m.group(2)):
                sim.findings.append({"kind": "false_count", "regime": sim.regime, "item": line.split()[0] if line.split()
                                     else "?", "decision": "line", "t": None,
                                     "why": "the Conductor log claims a daily limit it is over: " + line.strip()})


def _epoch(ts):
    import model as LM
    return LM.epoch(ts)


def _must(x, what):
    """-> x; a record or bundle that the sim itself wrote and cannot read is the sim's own fault: raise, never read it
    as empty (an empty one would hide a stuck state)."""
    if x is None:
        raise RuntimeError("lane_sweep: %s was written by the sim and reads as missing" % what)
    return x


# ---- the sweep -------------------------------------------------------------------------------------------------------
@contextlib.contextmanager
def world(sim):
    import detached_helper as DH
    import left_open_continue as LOC
    import list_dispatch as LD
    import list_effect as LE
    import model as LM
    import probe_result as PR
    import work_bundle as WB
    env = {"RM_UNDER_SELFTEST": "1", "RM_LIST_DISPATCH_DIR": os.path.join(sim.d, "ld"),
           "RM_WORK_BUNDLE_DIR": os.path.join(sim.d, "wb"), "RM_DISPATCHER_STATE": os.path.join(sim.d, "state"),
           "RM_CONDUCTOR_LOG": os.path.join(sim.d, "conductor.log"), "RM_CONTROL_DB": os.path.join(sim.d, "control.db")}

    def refuse(*a, **k):
        raise RuntimeError("lane_sweep: a stand-in is missing; the real code reached the world")
    with contextlib.ExitStack() as es:
        es.enter_context(mock.patch.dict(os.environ, env))
        for k in ("RIMFLOW_LEDGER", "RIMFLOW_ITEMS"):
            os.environ.pop(k, None)
        es.enter_context(mock.patch.object(time, "time", lambda: float(sim.now)))
        es.enter_context(mock.patch.object(os, "cpu_count", lambda: CORES))
        es.enter_context(mock.patch.object(LM, "read", lambda path=None: list(sim.evs)))
        es.enter_context(mock.patch.object(LM, "ITEMS", os.path.join(sim.d, "items")))
        for name, val in (("_mods", []), ("_off", (None, None)), ("_paused", None), ("_held", None), ("_pool", None),
                          ("_clone_exists", False), ("host_facts", {}), ("_games", [])):
            es.enter_context(mock.patch.object(LD, name, (lambda v: lambda *a, **k: v)(val)))
        es.enter_context(mock.patch.object(LD, "load_now", lambda: PR.value(sim.load())))
        es.enter_context(mock.patch.object(LD, "account_gate", lambda *a, **k: (True, "")))
        es.enter_context(mock.patch.object(DH, "live_status", lambda rec, *a, **k: rec.get("status")))
        es.enter_context(mock.patch.object(DH, "launch", refuse))
        es.enter_context(mock.patch.object(LE, "run", lambda *a, **k: ("fails", "sim: the outcome check fails")))
        es.enter_context(mock.patch.object(WB, "read_members", sim.read_members))
        es.enter_context(mock.patch.object(WB, "launch_remote", refuse))
        es.enter_context(mock.patch.dict(LOC.GATES, {k: (lambda *a, **kw: None) for k in LOC.GATES}))
        es.enter_context(mock.patch.object(LOC, "account_end_wait", lambda *a, **k: None))
        es.enter_context(mock.patch.object(LOC, "kick", refuse))
        yield


def run_regime(regime, plant=None, ticks=TICKS):
    import list_dispatch as LD
    import work_bundle as WB
    root = tempfile.mkdtemp(prefix="lane_sweep_%s_" % regime)
    try:
        sim = Sim(regime, root)
        with world(sim), planted(plant):
            cfg = dict(LD.load_cfg(), hosts={})
            fx = {"account": lambda: (True, ""), "launch": sim.launch_lane, "need": sim.need,
                  "close": lambda iid, text, why: (sim.add({"event": "close", "id": iid, "sha": "0000000",
                                                            "noCode": "sim: the lane's close"}) and 0),
                  "effect": lambda *a: (1, "sim: no effect writes"), "remote": lambda *a, **k: (1, "", "sim: no ssh"),
                  "home": lambda homes: (1, "sim: no home writes"), "name": lambda i, why: (1, "sim: no name writes")}
            sim.seed()
            for n in range(ticks):
                t = T0 + n * TICK_S
                sim.due(t)
                rd = LD.tick(cfg, True, fx, now=t)
                told = check(sim, rd)
                sim.conduct(rd, told)
            sim.due(T0 + ticks * TICK_S)
            counts(sim)
            bundles = sorted(WB.all_bundles().values(), key=lambda b: (b.get("at") or 0, b.get("id")))
        return sim, bundles
    finally:
        shutil.rmtree(root, ignore_errors=True)


_MEMO = {}


def sweep(regimes, plant=None, ticks=TICKS):
    """-> {"findings", "cases", "worst", "limit", "worst_at", "bundles": {regime: [bundle records]}}. Each (regime,
    plant) is run once per process: the sweep is deterministic."""
    out = {"findings": [], "cases": 0, "worst": 0, "limit": TICK_S, "worst_at": None, "bundles": {}}
    for r in regimes:
        key = (r, plant, ticks)
        if key not in _MEMO:
            _MEMO[key] = run_regime(r, plant, ticks)
        sim, bundles = _MEMO[key]
        out["findings"] += sim.findings
        out["cases"] += sim.cases
        out["bundles"][r] = bundles
        if sim.worst[0] / float(sim.worst[1]) > out["worst"] / float(out["limit"]):
            out["worst"], out["limit"], out["worst_at"] = sim.worst
    return out


def line(f):
    return "%s [%s] %s %s%s: %s" % (f["kind"], f["regime"], f["item"], f.get("decision") or "",
                                    (" held %ds, limit %ds" % (f["held_s"], f["limit_s"])) if "held_s" in f else "",
                                    f.get("why"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--regime", nargs="+", default=REGIMES, choices=REGIMES)
    ap.add_argument("--plant", choices=PLANTS)
    o = ap.parse_args(argv)
    os.environ["RM_UNDER_SELFTEST"] = "1"
    res = sweep(o.regime, o.plant)
    for f in res["findings"]:
        print(line(f))
    print("%d regime(s), %d case(s), %d finding(s); worst %ss of limit %ss (%s)" % (
        len(o.regime), res["cases"], len(res["findings"]), res["worst"], res["limit"], res["worst_at"]))
    return 1 if res["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
