#!/usr/bin/env python3
"""testless_census.py: every open ticket with no test, each in one state: the route that gives it a test, or what stops it.

Item RIMMANDRAKE_PROVE_TESTLESS_TICKETS_ROUTE_HE_WAS_TOLD_NONE; page one_page.md beside this file. A measuring script, not pipeline machinery.
Read-only: it changes no ticket, launches nothing. "No test" is list_shape.needs_shape_run, the lane's own reading.

The routes that give a ticket a test with no hand (code, not titles):
  Shape stage   list_shape.due: a non-mod ticket named for Shape, or filed at or after shape_from (it waits shape_grace_h)
  no-home step  list_dispatch.no_home_names: an old ticket with no home that no rule places is named for Shape, from
                no_home_shape_from (rule homes: list_home.rule_home, written by the same tick)
  age line      list_dispatch.block_age / work_bundle.ready_split(stale): a block with no end, idle, is taken past
  onboarding    list_dispatch.onboard_step: one run per `pipeline:`, `machine:` or `game:` home of an `on` class
  mod bundle    maturation_dispatch.pilot_holders -> road_back_holder -> work_bundle.mod_members: the holder run of a ledger
                pilot mod with open road-back items takes that mod's old tickets (onboard_classes mod: on)

    python3 -I design/specs/2026-11-26-testless-tickets/testless_census.py [--json] [--examples N]
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RF = os.path.join(REPO, "src", "RimMandrake", "rimflow")
for _p in (RF, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

CLOSED = ("done", "dropped", "superseded")
NOT_WORK = ("alarm", "notice", "standing", "owed")        # kinds that are not real work here (the brief of the item)
STATES = ("ON A ROUTE", "PARKED", "CLASS OFF", "MOD HELD", "MOD NOT ADMITTED", "NO HOME", "NO ROUTE", "NOT WORK",
          "COULD NOT LOOK")


def verdict(st, why, route=None, hole=False, then=None):
    return {"state": st, "why": why, "route": route, "hole": hole, "then": then}


def park_of(x, waits, blocked, now, epoch, end=None):
    """-> (kind, end condition or None) of a park that holds `x` now, or None when none holds. waits: the open items its
    block waits on (list_dispatch.block_facts); blocked: a block with no open predecessor still holds. end(x) -> the
    lane's own end of that block (lane_block_end), or None; without it, the kinds below decide alone."""
    if x.wait_until:
        t = epoch(x.wait_until)
        if t is None or t > now:
            return "dated wait", ("until %s" % x.wait_until) if t is not None else None
    if waits:
        return "block on an open item", "the blocker %s closes" % ", ".join(waits)
    if blocked:
        kind = x.blocked_kind or "other"
        if end is not None:
            return "block: %s" % kind, end(x)
        if kind == "time":
            return "block: time", ("its date %s" % x.blocked_lift_at) if x.blocked_lift_at else None
        if kind == "owner":
            return "block: owner", "the owner's act (`rimflow unblock`)"
        if kind == "live":
            return "block: live game", "a game window opens (the age line, list_dispatch.block_age)"
        if kind == "external":
            return "block: external", "an outside event, lifted by `rimflow unblock`" if x.blocked_reason else None
        return "block: other", None
    return None


def classify(x, env):
    """x: a model.Item. env: the facts of now (see gather). -> verdict dict. Pure over (x, env)."""
    kind = (x.kind or "").lower()
    if kind in NOT_WORK:
        return verdict("NOT WORK", "kind %s is a promise or notice kept by hand, not work" % kind)
    base = _route(x, env)
    p = env["park"](x) or env["refusal"](x)
    if p:
        k, end = p
        v = verdict("PARKED", "%s; ends when %s" % (k, end) if end else "%s, with no end condition" % k, hole=end is None)
        v["then"] = base
        v["park_kind"] = k
        return v
    return base


def _route(x, env):
    """The state of `x` if no park held it."""
    s = env["system"](x)
    if s is None:
        return verdict("COULD NOT LOOK", "which home it belongs to could not be read")
    mod = s[4:] if s.startswith("mod:") else None
    if mod:
        if mod not in env["admitted"]:
            return verdict("MOD NOT ADMITTED", "%s has no stage record, so no bundle of it exists" % mod)
        h = env["held"](mod)
        if h:
            return verdict("MOD HELD", "%s: %s" % (mod, h))
        if not env["on"](mod):
            return verdict("MOD HELD", "%s is not ON in the Maturation Pipeline" % mod)
        rb = env["road_back"](mod) if mod in env["pilots"] else []
        if rb is None:
            return verdict("COULD NOT LOOK", "the road-back hold of %s could not be read" % mod)
        if rb:
            return verdict("ON A ROUTE", "the holder run of %s (its road back is open)" % mod, route="mod bundle")
        if mod in env["rests"]:      # the Conductor's owed view lists a resting mod's tickets (conductor_stops)
            return verdict("NO ROUTE", "%s rests after its pass: no run takes its tickets, and the Conductor's owed view "
                           "lists them (conductor_stops mod_rest; `sort` sends each to the lane or the next version)" % mod)
        why = ("%s is ON but not a ledger pilot" % mod) if mod not in env["pilots"] else (
            "%s is ON and a pilot, but has no open road-back item" % mod)
        return verdict("NO ROUTE", "%s: pilot_holders launches a holder run (the only caller of work_bundle.mod_members) "
                       "for a pilot mod with an open road back only" % why, hole=True)
    under = _non_mod(x, s, env)
    off = env["off"](x)
    if off:
        v = verdict("MOD HELD" if off.startswith("HELD BY OWNER") else "PARKED",
                    off if off.startswith("HELD BY OWNER") else "stopped by a switch: %s" % off)
        v["then"] = under      # a lifted switch leaves the ticket where `under` says: a hole stays a hole
        return v
    return under


def _non_mod(x, s, env):
    """The route of a ticket that is not one mod's work, ignoring switches."""
    due = env["shape_due"](x)
    if due:
        return verdict("ON A ROUTE", "the Shape stage: %s" % due, route="Shape stage")
    if s.startswith(("item:", "cause:")):
        r = env.get("no_home_route", lambda x: None)(x)
        if r:
            return verdict("ON A ROUTE", "no home of its own (%s): %s" % (s, r), route="no-home step")
        return verdict("NO HOME", "no home of its own (%s), and it was filed before Shape went live and never named" % s,
                       hole=True)
    kind = s.partition(":")[0]
    cls = env["classes"].get(kind)
    if cls == "off":
        return verdict("CLASS OFF", "onboard_classes %s: off" % kind)
    if cls != "on":
        return verdict("NO ROUTE", "onboard_classes has no setting for %s" % kind, hole=True)
    return verdict("ON A ROUTE", "the onboarding run of %s" % s, route="onboarding")


FAR_DAYS = 400      # "ever": a time past every date of the lane's settings, for asking its code whether a route exists


def lane_block_end(x, system, cfg, now):
    """The lane's own answer for a block of `x` that holds with no open predecessor: its end (list_dispatch.block_end),
    else whether the age line ever takes it past the block, asked of the lane's code with its last own event long ago
    and every date passed: block_age for a lane ticket (its class taken as on: a class off is the next state, not this
    park), ready_split with endless_stale for a mod's ticket. -> the end text, or None (a hole)."""
    import list_dispatch as LD
    import work_bundle as WB
    e = LD.block_end(x)
    if e:
        return e
    far = max(now, LD._epoch_of(cfg.get("no_home_shape_from")) or 0) + FAR_DAYS * 86400

    class Op(object):
        last, opened = {x.id: 0.0}, {}
    s = system(x)
    days = float(cfg.get("block_idle_days", 3))
    if str(s or "").startswith("mod:"):
        ready, _out = WB.ready_split([x.id], {x.id: x}, far, refused=lambda i: None, held=lambda i: None,
                                     leased=lambda it: False, stale=lambda it: LD.endless_stale(it, 0.0, far, cfg))
        return (LD.ENDLESS_END % days) if ready else None
    kind = str(s or "").partition(":")[0]
    c2 = dict(cfg, onboard_classes=dict(cfg.get("onboard_classes") or {}, **({kind: "on"} if kind else {})))
    due, _why = LD.block_age(x, Op(), far, c2, system=s)
    return (LD.ENDLESS_END % days) if due else None


def lane_no_home_route(x, cfg, now):
    """The lane's own answer for an old ticket with no home: does its no-home step ever name it (list_dispatch.
    no_home_names, with every date passed)? -> the route's words, or None."""
    import list_dispatch as LD
    far = max(now, LD._epoch_of(cfg.get("no_home_shape_from")) or 0) + FAR_DAYS * 86400
    got, _why = LD.no_home_names({x.id: 0.0}, cfg, {}, far)
    if x.id not in got:
        return None
    return ("the lane's no-home step names it for Shape from %s, %s a day, oldest first (list_dispatch.no_home_names)"
            % (cfg.get("no_home_shape_from"), cfg.get("no_home_shape_per_day", 5)))


def gather(now=None):
    """-> (open testless tickets {id: Item}, env). Raises when the ledger could not be read."""
    import list_dispatch as LD
    import list_effect as LE
    import list_shape as LS
    import mod_owner_hold as MOH
    import model as LM
    import mod_work as MW
    import work_bundle as WB
    now = time.time() if now is None else now
    w = LE._world()
    cfg = LD.load_cfg()
    open_ = {i: x for i, x in w.items.items() if x.state not in CLOSED}
    no = {i: x for i, x in open_.items() if LS.needs_shape_run(LS.facts(x))}
    modset = MW.mods()
    mods = LD._mods()
    croot = os.path.join(REPO, "design", "concepts")
    admitted = set(f for f in os.listdir(croot) if not f.startswith("_") and os.path.isdir(os.path.join(croot, f))
                   and (os.path.exists(os.path.join(croot, f, "version", "VERSION.json"))
                        or os.path.exists(os.path.join(croot, f, "stage.json"))))
    import control as C
    import modledger
    pilots = set(modledger.config().get("pilot_mods") or [])
    import conductor_stops as CS
    ref = WB.refusals(LM.read())
    sys_cache, rb_cache = {}, {}

    def system(x):
        if x.id not in sys_cache:
            mw = MW.reading(x, modset, LM.ITEMS)
            sys_cache[x.id] = WB.system_of(x, lambda it, m=mw: m, w.items)
        return sys_cache[x.id]

    def road_back(mod):
        if mod not in rb_cache:
            try:
                rb_cache[mod] = WB.road_back_ids(mod)
            except Exception:  # noqa: BLE001 - could not look is not "no road back"
                rb_cache[mod] = None
        return rb_cache[mod]

    def park(x):
        waits, blocked = LD.block_facts(w, x, now)
        return park_of(x, waits, blocked, now, LM.epoch, end=lambda y: lane_block_end(y, system, cfg, now))

    def shape_due(x):
        sf = LS.facts(x)
        d, why = LS.due(sf, cfg, now)
        if d:
            return why
        if x.kind and not LS.needs_shape_run(sf):
            return None
        frm = cfg.get("shape_from")
        if frm and sf.get("filed") is not None and sf["filed"] >= LS._epoch(frm):
            return "%s (it enters after its filer's grace)" % why     # filed after shape_from: only the grace is left
        return None

    def off(x):
        o, cnl = LD._off(x.id, LD.mod_of(x.id, x.title, mods))
        return o or cnl

    def on(mod):
        try:
            return not C.blocked({"family": "maturation", "mod": mod})
        except Exception:  # noqa: BLE001 - could not look: not ON
            return False

    env = {"system": system, "park": park, "shape_due": shape_due, "off": off, "on": on, "admitted": admitted,
           "pilots": pilots, "road_back": road_back, "rests": set(CS.rests()), "classes": cfg.get("onboard_classes") or {},
           "no_home_route": lambda x: lane_no_home_route(x, cfg, now),
           "held": lambda mod: LD._held(mod) if MOH.held(mod) else None,
           "refusal": lambda x: ("refused by a bundle", "a new ledger event on it (the refusal reads since its last other event)")
           if ref.get(x.id) else None}
    return no, env


def census(no, env):
    return {i: classify(x, env) for i, x in sorted(no.items())}


def report(rows, no, n_examples=5):
    by = collections.defaultdict(list)
    for i, v in rows.items():
        by[v["state"]].append(i)
    lines = ["open tickets with no test (list_shape.needs_shape_run): %d" % len(rows)]
    for st in STATES:
        ids = by.get(st, [])
        if not ids:
            continue
        lines.append("%-18s %4d" % (st, len(ids)))
        for i in ids[:n_examples]:
            lines.append("    %s  %s" % (i, rows[i]["why"][:150]))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--examples", type=int, default=5)
    o = ap.parse_args(argv)
    try:
        no, env = gather()
    except Exception as e:  # noqa: BLE001 - could not look is never an empty census
        print("UNMEASURED: the ledger or the lane's settings could not be read (%s: %s)" % (type(e).__name__, e))
        return 2
    rows = census(no, env)
    if o.json:
        print(json.dumps(rows, indent=1, default=str))
    else:
        print(report(rows, no, o.examples))
    return 0


if __name__ == "__main__":
    sys.exit(main())
