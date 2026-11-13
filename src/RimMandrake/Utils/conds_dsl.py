#!/usr/bin/env python3
"""conds_dsl.py - the Python side of bridge conditions (CONDSDSL_WIRE_PYTHON_BUILDERS, build_spec §1.9 / §2 T4).

Spec: design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md. conds.py is the pure evaluator (T1, twinned
with JawaBenchCondCore.cs); this file is Python only and has no C# twin. conds.py re-exports its public names, so
callers write `from conds import cell, fw, pawn, game, ring, all_, any_, not_, edge, stays, changed`.

    r = B.until(fw(106, 103).fill >= 1, max_ticks=6000)        # -> CondResult
    with B.watch("dry", edge(cell(110, 90).is_water == False), owner=RUN) as w:
        B.ticks(2500)
        for ev in w.events(): ...                                # ev.tick, ev.values, ev.seq
    B.cond_eval(tree)                                            # one evaluation, no tick

Builders. Operator overloading builds the wire JSON of §1.2: a probe is an `Expr`; comparing it gives a `Cond`
(`cmp`); `&`, `|`, `~` give all/any/not; a bool probe used where a condition is wanted means `== True`. Python's
`and`/`or`/`not` cannot be overloaded: use `&`, `|`, `~` (or all_/any_/not_), and parenthesise comparisons
(`(a >= 1) & (b == False)`).

The wire (what the companion is sent; T3/T5 implement it, tool_schemas.json lists it):
    jawa/safe_advance  ticks=<max_ticks>, until, every, on_unknown, mapId, watch, sample, snapshot_on_hit, runKey,
                       stopOn, timeoutMs (<= 480000).  The companion compiles {until, max_ticks: ticks, ...}.
                       A start with a runKey it already holds returns that run (re-attach), never a second one.
    jawa/cond_eval     tree, mapId
    jawa/cond_watch    action=arm   owner, ttlMin, watch=[{name, tree}]
                       action=read  owner, since_seq   -> {events:[{seq, name, tick, values}], nextSeq, gap}
                       action=clear owner, names       (the owner's own watchers only)
                       action=list  owner

Runner semantics (§1.9): B.until re-attaches by runKey while the run is still `running` after a call's timeoutMs,
so no single command passes the 540 s limit; it prints one progress line per return. A `stopped` run goes through
clockgate: a resumable stop (clockgate.resumable_stop) resumes as is; otherwise the bridge's recover hook
(validation_core.site_recover) may clear the disturbance, which is appended to result.mutations[]; a stop neither
can absorb raises clockgate.GovernorStop. A resume starts a new segment with the ticks left and runKey
`<base>~r<N>`: level conditions carry on, edge/changed/stays restart their baseline, and coverage.gaps[] names the
hole. A hit is never a GovernorStop. verdict(): hit -> PASS, done -> the caller's choice, anything else UNMEASURED.
"""
import json
import os
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMAS = os.path.join(HERE, "northstar_driver", "tool_schemas.json")

SAFE_ADVANCE = "jawa/safe_advance"
COND_EVAL = "jawa/cond_eval"
COND_WATCH = "jawa/cond_watch"
TIMEOUT_MS_MAX = 480000          # one call's in-game wait; the bridge command limit is 540 s
REATTACH_MAX = 200               # re-attaches of one segment (200 x 480 s is > 26 h of wall time)
RESUME_MAX = 25                  # resumed segments of one until (clockgate.BENIGN_RESUME_MAX)
STATEFUL = ("edge", "changed", "stays", "alarm")
TERMINAL = ("hit", "done", "stopped", "unknown", "budget", "epoch", "error", "cancelled")
# safe_advance params a condition run adds (the core's RUN_KEYS minus max_ticks, which is `ticks` on the wire)
SAFE_ADVANCE_COND_PARAMS = ("until", "every", "on_unknown", "mapId", "watch", "sample", "snapshot_on_hit", "runKey")
WIRE_PARAMS = {
    SAFE_ADVANCE: ("ticks", "stopOn", "timeoutMs") + SAFE_ADVANCE_COND_PARAMS,
    COND_EVAL: ("tree", "mapId"),
    COND_WATCH: ("action", "owner", "ttlMin", "watch", "since_seq", "names"),
}


def _core():
    import conds  # noqa: E402 - lazy: conds re-exports this module at its end
    return conds


class CondRefused(Exception):
    """The companion (or the offline precheck) refused the spec by name (§1.2). A programming error, never a verdict."""

    def __init__(self, r, where="companion"):
        self.refusal = r
        Exception.__init__(self, "%s refused %s at %s: %s" % (where, r.get("refused"), r.get("at"), r.get("detail")))


# ---------------------------------------------------------------------------------------------- builders
class Cond(object):
    """A condition node: `.tree` is its wire JSON."""
    __hash__ = None

    def __init__(self, tree):
        self.tree = tree

    def __and__(self, other):
        return all_(self, other)

    def __rand__(self, other):
        return all_(other, self)

    def __or__(self, other):
        return any_(self, other)

    def __ror__(self, other):
        return any_(other, self)

    def __invert__(self):
        return not_(self)

    def __bool__(self):
        raise TypeError("a Cond has no truth value in Python: use & | ~ (or all_/any_/not_), not and/or/not")
    __nonzero__ = __bool__

    def named(self, nid):
        """Give the root node an id, echoed back in the results."""
        t = dict(self.tree)
        t["id"] = nid
        return Cond(t)

    def optional(self):
        """An UNKNOWN in this node reads as a definite False (status `ignored`)."""
        t = dict(self.tree)
        t["optional"] = True
        return Cond(t)

    def __repr__(self):
        return "Cond(%s)" % json.dumps(self.tree, sort_keys=True)


class Expr(object):
    """A probe read. Comparisons build `cmp` nodes; a bool probe is also a condition (`== True`)."""
    __hash__ = None

    def __init__(self, probe, vtype):
        self.probe, self.vtype = probe, vtype

    def _cmp(self, op, v, tol=None):
        if isinstance(v, Expr):
            raise TypeError("cmp compares a probe with a literal, not with another probe (§1.4)")
        t = {"cmp": [dict(self.probe), op, v]}
        if tol is not None:
            t["tol"] = tol
        return Cond(t)

    def __eq__(self, v):
        return self._cmp("==", v)

    def __ne__(self, v):
        return self._cmp("!=", v)

    def __lt__(self, v):
        return self._cmp("<", v)

    def __le__(self, v):
        return self._cmp("<=", v)

    def __gt__(self, v):
        return self._cmp(">", v)

    def __ge__(self, v):
        return self._cmp(">=", v)

    def eq(self, v, tol=None):
        return self._cmp("==", v, tol)

    def ne(self, v, tol=None):
        return self._cmp("!=", v, tol)

    def in_(self, lo, hi):
        return self._cmp("in", [lo, hi])

    def hour_in(self, lo, hi):
        """Circular hour window (crosses midnight when lo > hi)."""
        return self._cmp("hour_in", [lo, hi])

    def __bool__(self):
        raise TypeError("an Expr has no truth value in Python: compare it, or use it inside &, |, ~, edge, stays")
    __nonzero__ = __bool__

    def __invert__(self):
        return not_(self)

    def __and__(self, other):
        return all_(self, other)

    def __or__(self, other):
        return any_(self, other)

    # rect reducers (spatial probes over a rect only; the core refuses the rest by name)
    def _reduce(self, red, where=None, vtype="num"):
        p = dict(self.probe)
        p["reduce"] = red
        if where is not None:
            p["where"] = list(where)
        return Expr(p, vtype)

    def max(self):
        return self._reduce("max", vtype=self.vtype)

    def min(self):
        return self._reduce("min", vtype=self.vtype)

    def any(self, op=None, v=None):
        return self._reduce("any", None if op is None else (op, v), "bool")

    def all(self, op=None, v=None):
        return self._reduce("all", None if op is None else (op, v), "bool")

    def count_where(self, op=None, v=None):
        return self._reduce("count_where", None if op is None else (op, v), "num")

    def __repr__(self):
        return "Expr(%s)" % json.dumps(self.probe, sort_keys=True)


def to_tree(x):
    """Cond | bool Expr | wire dict -> wire dict."""
    if isinstance(x, Cond):
        return x.tree
    if isinstance(x, Expr):
        return {"cmp": [dict(x.probe), "==", True]}
    if isinstance(x, dict):
        return x
    raise TypeError("not a condition: %r" % (x,))


def _probe(name, vtype, **args):
    p = {"p": name}
    for k, v in args.items():
        if v is not None:
            p[k] = v
    return Expr(p, vtype)


class _Spatial(object):
    """cell(x, z) / rect(x, z, w, h) on a map: the cell.* and fw.* probes as attributes."""
    _PROBES = {}

    def __init__(self, loc, map_id=None):
        self.loc, self.map_id = loc, map_id

    def __getattr__(self, attr):
        if attr.startswith("_") or attr not in self._PROBES:
            raise AttributeError("%s has no probe %r (have: %s)" % (type(self).__name__, attr,
                                                                    ", ".join(sorted(self._PROBES))))
        name, vtype = self._PROBES[attr]
        args = dict(self.loc)
        if self.map_id is not None:
            args["mapId"] = self.map_id
        return _probe(name, vtype, **args)


class _CellProbes(_Spatial):
    _PROBES = {"terrain": ("cell.terrain", "str"), "is_water": ("cell.is_water", "bool"),
               "glow": ("cell.glow", "num"), "roofed": ("cell.roofed", "bool"), "temp": ("cell.temp", "num"),
               "fire": ("cell.fire", "bool")}


class _FwProbes(_Spatial):
    _PROBES = {"depth": ("fw.depth", "num"), "fill": ("fw.fill", "num"), "source": ("fw.source", "bool")}


def _loc(x, z, w=None, h=None):
    if w is None and h is None:
        return {"cell": [int(x), int(z)]}
    return {"rect": [int(x), int(z), int(w), int(h)]}


def cell(x, z, w=None, h=None, map_id=None):
    """cell(x, z).is_water; cell(x, z, w, h).glow.max() is a rect (inclusive, x..x+w-1)."""
    return _CellProbes(_loc(x, z, w, h), map_id)


def fw(x, z, w=None, h=None, map_id=None):
    """FlowWorks excavation: fw(x, z).fill / .depth / .source (status `unbound` without FlowWorks)."""
    return _FwProbes(_loc(x, z, w, h), map_id)


class _Game(object):
    @property
    def tick(self):
        return _probe("game.tick", "num")

    @property
    def hour(self):
        return _probe("game.hour", "num")


game = _Game()


class _Map(object):
    def __init__(self, map_id=None):
        self.map_id = map_id

    def __call__(self, map_id):
        return _Map(map_id)

    @property
    def sky_glow(self):
        return _probe("map.sky_glow", "num", mapId=self.map_id)

    def count(self, def_, x=None, z=None, w=None, h=None):
        rect = None if x is None else [int(x), int(z), int(w), int(h)]
        return _probe("map.count", "num", mapId=self.map_id, rect=rect, **{"def": def_})


map_ = _Map()


class _Pawn(object):
    def __init__(self, pid):
        self.pid = str(pid)

    def _p(self, name, vtype, f=None):
        return _probe(name, vtype, pawn=self.pid, f=f)

    x = property(lambda s: s._p("pawn.pos", "num", "x"))
    z = property(lambda s: s._p("pawn.pos", "num", "z"))
    map = property(lambda s: s._p("pawn.map", "num"))
    job_def = property(lambda s: s._p("pawn.job", "job", "def"))
    job_id = property(lambda s: s._p("pawn.job", "job", "id"))
    downed = property(lambda s: s._p("pawn.state", "bool", "downed"))
    dead = property(lambda s: s._p("pawn.state", "bool", "dead"))
    mental = property(lambda s: s._p("pawn.state", "bool", "mental"))
    drafted = property(lambda s: s._p("pawn.state", "bool", "drafted"))


def pawn(pid):
    return _Pawn(pid)


class _Thing(object):
    def __init__(self, tid):
        self.tid = str(tid)

    exists = property(lambda s: _probe("thing.exists", "bool", thing=s.tid))
    spawned = property(lambda s: _probe("thing.spawned", "bool", thing=s.tid))
    x = property(lambda s: _probe("thing.pos", "num", thing=s.tid, f="x"))
    z = property(lambda s: _probe("thing.pos", "num", thing=s.tid, f="z"))

    def field(self, path):
        """A field or property path, compiled to a getter once; a method call is refused."""
        return _probe("thing.field", "any", thing=self.tid, path=path)


def thing(tid):
    return _Thing(tid)


class _Ring(object):
    def __init__(self, source, filter_=None):
        self.source, self.filter_ = source, filter_

    @property
    def count(self):
        """Rows since arm (a cursor diff)."""
        return _probe("ring.count", "num", source=self.source, filter=self.filter_)


def ring(source, filter=None):  # noqa: A002 - the wire name
    return _Ring(source, filter)


def _kids(cs):
    if len(cs) == 1 and isinstance(cs[0], (list, tuple)):
        cs = tuple(cs[0])
    return [to_tree(c) for c in cs]


def _flat(kind, cs):
    out = []
    for t in _kids(cs):
        if set(t) == {kind}:          # (a & b) & c -> all[a, b, c]; an id'd or optional node stays its own node
            out.extend(t[kind])
        else:
            out.append(t)
    return Cond({kind: out})


def all_(*cs):
    return _flat("all", cs)


def any_(*cs):
    return _flat("any", cs)


def not_(c):
    return Cond({"not": to_tree(c)})


def edge(c, dir="rise"):  # noqa: A002 - the wire name
    return Cond({"edge": to_tree(c), "dir": dir})


def stays(c, ticks):
    return Cond({"stays": to_tree(c), "ticks": int(ticks)})


def changed(e):
    if not isinstance(e, Expr):
        raise TypeError("changed() takes a probe, e.g. changed(fw(1, 2).fill)")
    return Cond({"changed": dict(e.probe)})


def alarm(c):
    """A watcher root only: the first True is a violation event."""
    return Cond({"alarm": to_tree(c)})


def run_spec(until, max_ticks, every=None, on_unknown=None, map_id=None, watch=None, sample=None,
             snapshot_on_hit=None, run_key=None):
    """The §1.2 run spec (what conds.evaluate and the companion compile). watch: {name: cond} or [(name, cond)];
    sample: {"every": n, "probes": {name: Expr}, "on_change_only": b}; snapshot_on_hit: {name: Expr}."""
    s = {"until": to_tree(until), "max_ticks": int(max_ticks)}
    if every is not None:
        s["every"] = int(every)
    if on_unknown is not None:
        s["on_unknown"] = on_unknown
    if map_id is not None:
        s["mapId"] = int(map_id)
    if run_key is not None:
        s["runKey"] = run_key
    if watch:
        items = watch.items() if isinstance(watch, dict) else watch
        s["watch"] = [{"name": n, "tree": to_tree(c)} for n, c in items]
    if sample:
        sm = dict(sample)
        sm["probes"] = _probe_map(sm.get("probes") or {})
        s["sample"] = sm
    if snapshot_on_hit:
        s["snapshot_on_hit"] = _probe_map(snapshot_on_hit)
    return s


def _probe_map(m):
    return dict((k, dict(v.probe) if isinstance(v, Expr) else v) for k, v in m.items())


def stateful_ids(canonical):
    """ids of the edge/changed/stays/alarm nodes in a COMPILED spec's canonical form (every node carries the id
    the core gave it: one counter across until and every watch tree, a watcher's prefixed "<name>/"). Never
    renumbered here: the canonical form is the one source of node ids."""
    out = []

    def walk(t):
        if not isinstance(t, dict):
            return
        kind = next((k for k in ("all", "any", "not", "cmp", "changed", "edge", "stays", "alarm") if k in t), None)
        if kind in STATEFUL:
            out.append(t.get("id"))
        if kind in ("all", "any"):
            for ch in t[kind]:
                walk(ch)
        elif kind in ("not", "edge", "stays", "alarm"):
            walk(t[kind])
    if not isinstance(canonical, dict):
        return out
    walk(canonical.get("until") or canonical.get("tree"))
    for w in canonical.get("watch") or []:
        walk(w.get("tree"))
    return out


class _ShapeSource(object):
    """A probe source for the offline precheck: every map is current and huge, nothing is refused at bind. It sees
    the spec's shape only (keys, types, node kinds, caps); defs, cells and maps are the companion's to refuse."""

    def current_map(self):
        return 0

    def map_size(self, map_id):
        return (1000000, 1000000)

    def refuse(self, key):
        return None


def precheck(spec, mode="run"):
    """Compile `spec` with the T1 core over _ShapeSource; raise CondRefused on a shape refusal. -> canonical."""
    C = _core()
    try:
        c = C.Compiler(_ShapeSource(), mode).compile_spec(json.loads(json.dumps(spec)))
    except C.Refused as e:
        raise CondRefused(C.refusal(e), "offline precheck")
    return c.canonical


def shape_canonical(spec, mode="run"):
    """precheck's canonical, or None when the shape is refused (the companion will say why)."""
    try:
        return precheck(spec, mode)
    except CondRefused:
        return None


# ---------------------------------------------------------------------------------------------- tool schema names
_SCHEMA = {}


def schema_tools(path=SCHEMAS):
    if path not in _SCHEMA:
        with open(path) as f:
            _SCHEMA[path] = json.load(f)["tools"]
    return _SCHEMA[path]


def check_wire_names(path=SCHEMAS):
    """Every tool and param this module sends is declared in tool_schemas.json. -> list of misses (empty = clean)."""
    tools = schema_tools(path)
    miss = []
    for tool, params in sorted(WIRE_PARAMS.items()):
        spec = tools.get(tool)
        if spec is None:
            miss.append("%s: not in tool_schemas.json" % tool)
            continue
        for p in params:
            if p not in spec.get("parameters", ()):
                miss.append("%s: param %s not in tool_schemas.json" % (tool, p))
    return miss


def _guard_names(tool, kw):
    bad = [k for k in kw if k not in WIRE_PARAMS[tool]]
    if bad:
        raise ValueError("%s: params %s are not on the wire (WIRE_PARAMS)" % (tool, ",".join(sorted(bad))))


# ---------------------------------------------------------------------------------------------- results
class CondResult(object):
    """One until's result (§1.5), stitched over its segments. `raw` is the last segment's reply; `segments` all of
    them; `mutations` every mutation made while it was armed; `coverage.gaps` every hole (resume baselines)."""

    def __init__(self, d, segments=None, mutations=None, resumes=None):
        self.raw = d
        self.segments = segments if segments is not None else [d]
        self.mutations = list(mutations or [])
        self.resumes = list(resumes or [])
        self.state = d.get("state")
        self.hit_tick = d.get("hitTick")
        self.values = d.get("values")
        self.unknown = d.get("unknown")
        self.triggers = d.get("triggers") or []
        self.snapshot = d.get("snapshot")
        first = self.segments[0]
        self.run_key = first.get("runKey")
        self.at_arm = first.get("atArm")
        self.true_at_arm = bool(first.get("trueAtArm")) and len(self.segments) == 1
        self.tick_from = first.get("tickFrom")
        self.tick_to = d.get("tickTo")
        self.executed = sum(int(s.get("executed") or 0) for s in self.segments)
        gaps, evals, complete = [], 0, True
        ms_total, ms_max = 0.0, 0.0
        watch, sample = [], []
        for i, s in enumerate(self.segments):
            cov = s.get("coverage") or {}
            gaps.extend(cov.get("gaps") or [])
            evals += int(cov.get("evals") or 0)
            complete = complete and cov.get("complete", True) is not False
            cost = s.get("cost") or {}
            ms_total += float(cost.get("evalMsTotal") or 0)
            ms_max = max(ms_max, float(cost.get("evalMsMax") or 0))
            for ev in s.get("watch") or []:
                watch.append(dict(ev, segment=i))
            sample.extend(s.get("sample") or [])
        for r in self.resumes:
            if r.get("gap"):
                gaps.append(r["gap"])
        self.coverage = {"every": (first.get("coverage") or {}).get("every"), "evals": evals, "gaps": gaps,
                         "complete": complete and not gaps}
        self.cost = {"evalMsTotal": round(ms_total, 3), "evalMsMax": round(ms_max, 3)}
        self.watch = watch
        self.sample = sample

    @property
    def hit(self):
        return self.state == "hit" or (self.state == "stopped" and self.hit_tick is not None)

    def verdict(self, on_done="FAIL", expect_hit=True):
        """-> (PASS|FAIL|UNMEASURED, reason). hit = the condition held (PASS, or FAIL when expect_hit is False);
        done = max_ticks with no hit (`on_done`, the caller's choice; PASS when expect_hit is False); every other
        state is UNMEASURED, with the probe's reason for `unknown`."""
        if self.hit:
            return ("PASS" if expect_hit else "FAIL"), "hit at tick %s" % self.hit_tick
        if self.state == "done":
            if not expect_hit:
                return "PASS", "no hit in %s tick(s)" % self.executed
            if on_done not in ("FAIL", "UNMEASURED"):
                raise ValueError("on_done is FAIL or UNMEASURED")
            return on_done, "no hit in %s tick(s)" % self.executed
        if self.state == "unknown":
            u = self.unknown or {}
            return "UNMEASURED", "unknown: %s %s %s" % (u.get("probe") or u.get("id") or "",
                                                        u.get("status") or "", u.get("detail") or "")
        return "UNMEASURED", "state %s: %s" % (self.state, self.triggers or self.raw.get("abortWhy") or "")

    def as_dict(self):
        return {"runKey": self.run_key, "state": self.state, "hitTick": self.hit_tick, "values": self.values,
                "atArm": self.at_arm, "trueAtArm": self.true_at_arm, "executed": self.executed,
                "tickFrom": self.tick_from, "tickTo": self.tick_to, "triggers": self.triggers,
                "unknown": self.unknown, "coverage": self.coverage, "cost": self.cost, "watch": self.watch,
                "sample": self.sample, "snapshot": self.snapshot, "mutations": self.mutations,
                "resumes": self.resumes, "segments": len(self.segments)}

    def __repr__(self):
        return "CondResult(state=%s, hit_tick=%s, executed=%s, gaps=%d, mutations=%d)" % (
            self.state, self.hit_tick, self.executed, len(self.coverage["gaps"]), len(self.mutations))


def _unwrap(r):
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:                                    # noqa: BLE001
            pass
    if isinstance(r, dict) and isinstance(r.get("result"), dict) and "state" not in r and "refused" not in r:
        r = r["result"]
    return r if isinstance(r, dict) else {"raw": r}


def _clockgate():
    d = os.path.join(HERE, "modcheck")
    if d not in sys.path:
        sys.path.insert(0, d)
    import clockgate  # noqa: E402
    return clockgate


def new_run_key(prefix="py"):
    return "%s-%s" % (prefix, uuid.uuid4().hex[:12])


_USED_KEYS = set()


def _stop_tick(r):
    sb = r.get("stopBy") or {}
    return sb.get("tick") if sb.get("tick") is not None else r.get("tickTo")


def run_until(call, cond, max_ticks, recover=None, stop_on="default", timeout_ms=TIMEOUT_MS_MAX, progress=None,
              run_key=None, precheck_offline=True, on_mutation=None, **opts):
    """The B.until engine over any `call(tool, **kw) -> dict`.

    recover(r) -> None (a real stop) or a mutation dict (the disturbance was cleared and read back); it is tried
    after clockgate.resumable_stop. on_mutation(m) is told of each mutation (watch handles re-arm on it).
    opts: every, on_unknown, map_id, watch, sample, snapshot_on_hit (run_spec's). -> CondResult."""
    cg = _clockgate()
    timeout_ms = int(min(int(timeout_ms), TIMEOUT_MS_MAX))
    say = progress if progress is not None else (lambda s: print(s, flush=True))
    base = run_key or new_run_key()
    if base in _USED_KEYS:
        # the companion would hand back the retained result of the earlier run with that key, and no tick would move
        raise ValueError("runKey %r was already used in this process: a runKey names ONE run" % base)
    spec = run_spec(cond, max_ticks, run_key=base, **opts)
    canon = precheck(spec) if precheck_offline else shape_canonical(spec)
    _USED_KEYS.add(base)
    segments, mutations, resumes = [], [], []
    pending_gap = None
    left, key, attempt = int(max_ticks), base, 0
    while True:
        kw = dict((k, v) for k, v in spec.items() if k != "max_ticks")
        kw.update(ticks=left, runKey=key, stopOn=stop_on, timeoutMs=timeout_ms)
        _guard_names(SAFE_ADVANCE, kw)
        r, attaches, first_from = None, 0, None
        while True:
            r = _unwrap(call(SAFE_ADVANCE, **kw))
            if "refused" in r and r.get("refused"):
                if isinstance(r.get("refused"), str) and r.get("at") is not None:
                    raise CondRefused(r)
                raise cg.GovernorStop(r)                     # a safe_advance refusal (budget, profile): a real stop
            st = r.get("state")
            if attaches and None not in (first_from, r.get("tickFrom")) and r.get("tickFrom") != first_from:
                # a re-attach that found no run under its key started a new one: the earlier ticks are lost
                try:
                    call(SAFE_ADVANCE, action="cancel")
                except Exception:                            # noqa: BLE001
                    pass
                r = dict(r, state="error", abortWhy="run %s lost on re-attach: tickFrom %s became %s"
                         % (key, first_from, r.get("tickFrom")))
                break
            if first_from is None:
                first_from = r.get("tickFrom")
            say("until %s: %s, %s tick(s) so far%s" % (key, st, r.get("executed"),
                                                       (", re-attaching" if st == "running" else "")))
            if st != "running":
                break
            attaches += 1
            if attaches > REATTACH_MAX:
                try:
                    call(SAFE_ADVANCE, action="cancel")
                except Exception:                            # noqa: BLE001
                    pass
                r = dict(r, state="cancelled", abortWhy="still running after %d re-attaches" % REATTACH_MAX)
                break
        segments.append(r)
        if pending_gap is not None:
            pending_gap["toTick"] = r.get("tickFrom", pending_gap["toTick"])
            pending_gap = None
        st = r.get("state")
        if st != "stopped":
            if st not in TERMINAL:
                r = dict(r, state="error", abortWhy="unknown state %r" % (st,))
                segments[-1] = r
            return CondResult(r, segments, mutations, resumes)
        # stopped: the vitals latch ended the segment. Resume only what clockgate or the recover hook can absorb.
        # clockgate reads triggers as dicts; the condition run's own entries ("cond", "unknown") are strings
        why = cg.resumable_stop(dict(r, triggers=[t for t in r.get("triggers") or [] if isinstance(t, dict)]))
        mut = None
        if not why and recover is not None and attempt < RESUME_MAX:
            mut = recover(r)
            if mut is not None:
                why = "site_recover"
        if not why or attempt >= RESUME_MAX:
            g = cg.GovernorStop(r)
            # a real stop wins the tick (§1.5); a hit on the same tick is still evidence, readable on the exception
            g.cond_result = CondResult(r, segments, mutations, resumes)
            raise g
        ex = int(r.get("executed") or 0)
        at = _stop_tick(r)
        if mut is not None:
            mut = dict(mut, atTick=at, runKey=key)
            mutations.append(mut)
            if on_mutation is not None:
                on_mutation(mut)
        else:
            cg.BENIGN_STOPS.append({"detail": (r.get("stopBy") or {}).get("detail"), "executedBeforeStop": ex,
                                    "why": why, "subjectId": (r.get("stopBy") or {}).get("subjectId"),
                                    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        left -= ex
        gap = None
        stateful = stateful_ids(r.get("canonical") or canon)
        if stateful:
            # toTick becomes the next segment's tickFrom (its arm): the span where no edge/stays baseline existed
            gap = pending_gap = {"fromTick": at, "toTick": at, "why": "resumed after %s: baselines restarted" % why,
                                 "nodes": stateful}
        if r.get("hitTick") is not None or left <= 0:
            # the hit (or the deadline) landed on the stop's own tick and the stop is absorbed: the run is over
            fin = dict(r, state="hit" if r.get("hitTick") is not None else "done")
            segments[-1] = fin
            resumes.append({"why": why, "atTick": at, "resumed": False})
            return CondResult(fin, segments, mutations, resumes)
        attempt += 1
        key = "%s~r%d" % (base, attempt)
        resumes.append({"why": why, "atTick": at, "resumed": True, "runKey": key, "ticksLeft": left, "gap": gap})
        say("until %s: stopped at tick %s (%s), resuming as %s with %d tick(s) left" % (base, at, why, key, left))


def cond_eval(call, cond, map_id=None):
    """One evaluation now, no tick (jawa/cond_eval). -> the companion's reply (canonical, v, status, values, cost)
    or its refusal dict; a dry run, so a refusal is returned, not raised."""
    kw = {"tree": to_tree(cond)}
    if map_id is not None:
        kw["mapId"] = int(map_id)
    _guard_names(COND_EVAL, kw)
    return _unwrap(call(COND_EVAL, **kw))


class WatchEvent(object):
    def __init__(self, d):
        self.raw = d
        self.seq, self.name, self.tick, self.values = d.get("seq"), d.get("name"), d.get("tick"), d.get("values")

    def __repr__(self):
        return "WatchEvent(%s %s @%s)" % (self.seq, self.name, self.tick)


class WatchHandle(object):
    """Persistent watchers (jawa/cond_watch) under one owner, as a context manager: arm on enter, clear on exit.
    events() reads past the cursor; a ring overflow is recorded in `gaps`. A mutation made while armed (B.ticks'
    site_recover) is appended to `mutations`, and a watcher with edge/changed/stays/alarm nodes is drained, cleared
    and re-armed, so its baseline restarts and the hole is in `gaps`."""

    def __init__(self, call, owner, watch, ttl_min=30, precheck_offline=True, registry=None):
        self.call, self.owner, self.ttl_min = call, owner, int(ttl_min)
        items = watch.items() if isinstance(watch, dict) else watch
        self.watch = [{"name": n, "tree": to_tree(c)} for n, c in items]
        probe = {"until": {"cmp": [{"p": "game.tick"}, ">=", 0]}, "max_ticks": 0, "watch": self.watch}
        self.canon = precheck(probe) if precheck_offline else shape_canonical(probe)
        self.cursor, self.gaps, self.mutations, self.buffer = 0, [], [], []
        self.armed, self.registry, self.lost, self.arm_reply = False, registry, None, {}

    def _call(self, **kw):
        _guard_names(COND_WATCH, kw)
        return _unwrap(self.call(COND_WATCH, **kw))

    def arm(self):
        r = self._call(action="arm", owner=self.owner, ttlMin=self.ttl_min, watch=self.watch)
        if r.get("refused"):
            raise CondRefused(r)
        if r.get("success") is False:
            raise RuntimeError("cond_watch arm failed: %s" % json.dumps(r, default=str))
        self.armed = True
        self.arm_reply = r
        if r.get("nextSeq") is not None:
            self.cursor = int(r["nextSeq"])
        if self.registry is not None and self not in self.registry:
            self.registry.append(self)
        return r

    @property
    def complete(self):
        """True when no event can have been missed: no gap, and the watchers were never lost."""
        return not self.gaps and self.lost is None

    def _read(self):
        if not self.armed:
            return []
        r = self._call(action="read", owner=self.owner, since_seq=self.cursor)
        if r.get("refused") or r.get("success") is False or r.get("disarmed"):
            # a load, game change, ttl expiry or probe exception cleared the watchers (§1.7): say so, never return []
            # as if nothing happened
            self.lost = r.get("disarmedWhy") or r.get("error") or r.get("refused") or r.get("disarmed") or "lost"
            self.armed = False
            self.gaps.append({"fromSeq": self.cursor, "toSeq": None, "why": "watchers lost: %s" % (self.lost,)})
            return [WatchEvent(e) for e in r.get("events") or []]
        g = r.get("gap")
        if g:
            if isinstance(g, (list, tuple)):
                g = {"fromSeq": g[0], "toSeq": g[1] if len(g) > 1 else None}
            elif not isinstance(g, dict):
                g = {"detail": g}
            self.gaps.append(dict(g, why="ring overflow"))
        evs = [WatchEvent(e) for e in r.get("events") or []]
        if r.get("nextSeq") is not None:
            self.cursor = int(r["nextSeq"])
        elif evs:
            self.cursor = max(int(e.seq) for e in evs) + 1
        return evs

    def events(self):
        """Events since the last read (buffered ones from a re-arm first)."""
        out, self.buffer = self.buffer + self._read(), []
        return out

    def clear(self):
        if self.armed:
            self._call(action="clear", owner=self.owner, names=[w["name"] for w in self.watch])
            self.armed = False
        if self.registry is not None and self in self.registry:
            self.registry.remove(self)

    def on_mutation(self, mut):
        self.mutations.append(mut)
        stateful = stateful_ids(self.arm_reply.get("canonical") or self.canon)
        if not stateful or not self.armed:
            return
        self.buffer.extend(self._read())
        if not self.armed:                                   # the drain found the watchers lost: never re-arm silently
            return
        self._call(action="clear", owner=self.owner, names=[w["name"] for w in self.watch])
        self.armed = False
        self.arm()
        at = mut.get("atTick")
        self.gaps.append({"fromTick": at, "toTick": at, "why": "re-armed after %s: baselines restarted"
                          % mut.get("kind", "a mutation"), "nodes": stateful})

    def __enter__(self):
        self.arm()
        return self

    def __exit__(self, *exc):
        self.clear()
        return False
