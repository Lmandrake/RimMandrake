#!/usr/bin/env python3
"""conds.py - the Python twin of the bridge condition evaluator (CONDCORE_BUILD_THREE_VALUED_TREES).

Spec: design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §1 (this file implements §1.2-§1.5 and §1.8 for
the pure core; the Verse probes are T2, the safe_advance wiring T3, the builders T4).

This module and src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCondCore.cs are ONE semantics written
twice. src/RimMandrake/Utils/selftest_conds_vectors.py runs both on src/RimMandrake/Utils/conds_vectors.json and
requires byte-identical output, so a change here without the same change there fails. Keep the two in step line
for line: same traversal order, same refusal order, same detail strings, same number formatting.

Semantics (the decisions §1 left open, made here and mirrored in C#):
  * Values are three-valued: True, False, None (UNKNOWN). A probe read is (v, status, detail); status is one of
    ok | gone | oob | unbound | error; anything but ok makes the reading UNKNOWN, never 0 or false.
  * all/any/not are strong Kleene; every child is evaluated on every due evaluation (no short-circuit). An UNKNOWN
    result carries the status and detail of the first UNKNOWN child in order.
  * "optional": true on a node turns that node's UNKNOWN into a definite False (status "ignored", detail = the
    original status), which is what "ignore per node" means.
  * changed(p): True when an ok value differs from the previous ok value; no baseline yet = False; an UNKNOWN resets
    the baseline. edge(c, rise|fall): True on the evaluation where c flips; no baseline (arm) = False; an UNKNOWN
    resets. stays(c, ticks): True when c has been True on every evaluation since a streak that began >= ticks ago.
  * A run evaluates at arm (k = 0) and then on every due tick k % every == 0; the deadline tick k == max_ticks is
    always evaluated. True at arm = state hit, executed 0, trueAtArm. A hit on the deadline tick is a hit.
  * Arbitration on one tick: a safety stop (frame "stop") wins the state (stopped) and the hit is still reported,
    triggers list ["cond", <stop>]. An epoch change ends the run with state "epoch" before evaluating that tick
    (stays and the deadline are refused across an epoch change). A non-consecutive tick ends it with state "error".
  * ring.count is a count since arm: the raw cursor read at arm is the baseline; an arm read that is not ok makes
    every later read UNKNOWN with the arm status.
  * Rect [x, z, w, h] covers x..x+w-1 and z..z+h-1 (inclusive cells); cells are read z-major, x-minor.
  * Caps: 64 nodes (tree nodes plus probe objects, across until and every watch tree), 1,024 rect cells across the
    whole spec, 16 watchers, 4,096 sample rows (rows past the cap are counted in sampleDropped).
  * Canonical JSON: keys sorted by code point, no spaces, integral numbers below 1e15 as integers, other numbers by
    the shortest of 15/16/17 significant digits that round-trips, positional when -6 < exponent < 15.

Run: python3 src/RimMandrake/Utils/conds.py <vectors.json>   (prints the vector output text, as the C# harness does)
"""
import json
import math
import sys

STATUSES = ("ok", "gone", "oob", "unbound", "error")
MAX_NODES = 64
MAX_CELLS = 1024
MAX_WATCHERS = 16
MAX_SAMPLE_ROWS = 4096
HARD_MAX_TICKS = 1200000       # JawaBenchVitalsCore.HardAdvanceCap
MAX_EVERY = 60000

# The refusal names the core can emit; the selftest requires a vector for each, and the C# core to emit the same set.
REFUSALS = ("json", "type", "unknown_key", "missing_key", "bad_value", "unknown_node", "unknown_probe",
            "probe_not_in_v1", "missing_arg", "bad_arg", "map_unknown", "cell_oob", "rect_empty", "reduce_bad",
            "cmp_op", "cmp_type", "empty_children", "alarm_not_root", "field_method", "duplicate_id",
            "duplicate_watch", "cap_nodes", "cap_cells", "cap_watchers", "bind")

SPATIAL = ("cell.terrain", "cell.is_water", "fw.depth", "fw.fill", "fw.source", "cell.glow", "cell.roofed",
           "cell.temp", "cell.fire")
# name -> (value type, required args, optional args); spatial probes also take cell|rect, reduce, where.
PROBES = {
    "cell.terrain": ("str", (), ()), "cell.is_water": ("bool", (), ()),
    "fw.depth": ("num", (), ()), "fw.fill": ("num", (), ()), "fw.source": ("bool", (), ()),
    "cell.glow": ("num", (), ()), "cell.roofed": ("bool", (), ()), "cell.temp": ("num", (), ()),
    "cell.fire": ("bool", (), ()),
    "map.sky_glow": ("num", (), ()), "map.count": ("num", ("def",), ("rect",)),
    "game.tick": ("num", (), ()), "game.hour": ("num", (), ()),
    "pawn.pos": ("num", ("pawn", "f"), ()), "pawn.map": ("num", ("pawn",), ()),
    "pawn.job": ("job", ("pawn", "f"), ()), "pawn.state": ("bool", ("pawn", "f"), ()),
    "thing.exists": ("bool", ("thing",), ()), "thing.spawned": ("bool", ("thing",), ()),
    "thing.pos": ("num", ("thing", "f"), ()), "thing.field": ("any", ("thing", "path"), ()),
    "ring.count": ("num", ("source",), ("filter",)),
}
F_VALUES = {"pawn.pos": ("x", "z"), "pawn.job": ("def", "id"), "pawn.state": ("downed", "dead", "mental", "drafted"),
            "thing.pos": ("x", "z")}
RING_SOURCES = ("damage_log", "incident_journal", "drain_log", "letters")
REDUCERS = ("any", "all", "count_where", "max", "min")
OPS = ("==", "!=", "<", "<=", ">", ">=", "in", "hour_in")
NODE_KINDS = ("all", "any", "not", "cmp", "changed", "edge", "stays", "alarm")
NODE_KEYS = {"all": (), "any": (), "not": (), "cmp": ("tol",), "changed": (), "edge": ("dir",), "stays": ("ticks",),
             "alarm": ()}
# Arg check order is fixed (and mirrored in C#).
ARG_ORDER = ("cell", "rect", "reduce", "where", "mapId", "def", "pawn", "thing", "f", "path", "source", "filter")
RUN_KEYS = ("every", "mapId", "max_ticks", "on_unknown", "runKey", "sample", "snapshot_on_hit", "until", "watch")
EVAL_KEYS = ("mapId", "tree")


class Refused(Exception):
    def __init__(self, name, at, detail):
        Exception.__init__(self, name)
        self.name, self.at, self.detail = name, at, detail


# ---------------------------------------------------------------------------------------------- JSON (canonical)
def _dup_hook(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError("duplicate key")
        d[k] = v
    return d


def parse_json(text):
    """Strict parse: duplicate keys and NaN/Infinity refused (the C# parser refuses the same)."""
    def bad_const(_):
        raise ValueError("constant")

    def num(s):
        # every number is a double, as in C#; an out-of-range one (1e400) is refused, never infinity
        x = float(s)
        if not math.isfinite(x):
            raise ValueError("number out of range")
        return int(s) if ("." not in s and "e" not in s and "E" not in s and abs(x) < 1e15) else x
    return json.loads(text, object_pairs_hook=_dup_hook, parse_constant=bad_const, parse_float=num, parse_int=num)


def fmt_num(x):
    if isinstance(x, int):
        x = float(x)
    if not math.isfinite(x):
        return "null"
    if x == int(x) and abs(x) < 1e15:
        return str(int(x))
    s = None
    for p in (15, 16, 17):
        s = "%.*e" % (p - 1, x)
        if float(s) == x:
            break
    mant, exp = s.split("e")
    exp = int(exp)
    neg = mant.startswith("-")
    digits = mant.lstrip("-").replace(".", "").rstrip("0") or "0"
    sign = "-" if neg else ""
    if -6 < exp < 15:
        if exp >= 0:
            if len(digits) <= exp + 1:
                body = digits + "0" * (exp + 1 - len(digits))
            else:
                body = digits[:exp + 1] + "." + digits[exp + 1:]
        else:
            body = "0." + "0" * (-exp - 1) + digits
        return sign + body
    return sign + digits[0] + ("." + digits[1:] if len(digits) > 1 else "") + "e" + str(exp)


def fmt_str(s):
    out = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif o < 0x20:
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def canon(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return fmt_num(v)
    if isinstance(v, str):
        return fmt_str(v)
    if isinstance(v, list):
        return "[" + ",".join(canon(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ",".join(fmt_str(k) + ":" + canon(v[k]) for k in sorted(v)) + "}"
    raise TypeError("not JSON: %r" % (v,))


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def is_int(x):
    return is_num(x) and math.isfinite(x) and float(x) == int(x) and abs(x) < 2147483648


def jtype(x):
    if x is None:
        return "null"
    if isinstance(x, bool):
        return "bool"
    if is_num(x):
        return "num"
    if isinstance(x, str):
        return "str"
    if isinstance(x, list):
        return "list"
    return "object"


def key_val(v):
    """Compact value text inside a probe key."""
    if isinstance(v, list):
        return ",".join(key_val(x) for x in v)
    if isinstance(v, str):
        return v
    return canon(v)


# ---------------------------------------------------------------------------------------------- compiled tree
class Probe(object):
    def __init__(self):
        self.name = self.ptype = self.reduce = self.where_op = self.where_lit = None
        self.args = {}        # canonical args excluding p/cell/rect/reduce/where/mapId
        self.cell = self.rect = None
        self.map_id = 0
        self.key = ""         # series key (point probes) or base key (rect)
        self.canonical = {}

    def cell_key(self, x, z):
        parts = [self.name] + ["%s=%s" % (k, key_val(self.args[k])) for k in sorted(self.args)]
        parts.append("cell=%d,%d" % (x, z))
        return " ".join(parts)

    def vtype(self):
        """Type of the value this probe yields after reduction."""
        if self.rect is not None and self.name in SPATIAL:
            return "bool" if self.reduce in ("any", "all") else "num"
        if self.ptype == "job":
            return "str" if self.args.get("f") == "def" else "num"
        return self.ptype


class Node(object):
    def __init__(self, kind, nid):
        self.kind, self.id = kind, nid
        self.optional = False
        self.children = []
        self.probe = None
        self.op = self.lit = None
        self.tol = None
        self.dir = "rise"
        self.ticks = 0
        self.canonical = None
        self.reset()

    def reset(self):
        self.has_prev = False
        self.prev = None
        self.start = None


class Compiler(object):
    def __init__(self, source, mode):
        self.source, self.mode = source, mode
        self.nodes = 0        # tree nodes plus probe objects (the cap)
        self.idn = 0          # tree nodes only (default ids n0, n1, ... in preorder)
        self.cells = 0
        self.ids = set()
        self.map_id = 0

    # -- helpers
    def obj(self, x, at):
        if not isinstance(x, dict):
            raise Refused("type", at, "want object, got " + jtype(x))
        return x

    def keys(self, d, allowed, at):
        for k in sorted(d):
            if k not in allowed:
                raise Refused("unknown_key", at, k)

    def int_in(self, d, k, lo, hi, at, default=None):
        if k not in d:
            if default is None:
                raise Refused("missing_key", at, k)
            return default
        v = d[k]
        if not is_num(v):
            raise Refused("type", at + "." + k, "want num, got " + jtype(v))
        if not is_int(v) or v < lo or v > hi:
            raise Refused("bad_value", at + "." + k, "want integer in [%d,%d]" % (lo, hi))
        return int(v)

    # -- top level
    def compile_spec(self, spec):
        spec = self.obj(spec, "$")
        allowed = RUN_KEYS if self.mode == "run" else EVAL_KEYS
        self.keys(spec, allowed, "$")
        root = "until" if self.mode == "run" else "tree"
        if root not in spec:
            raise Refused("missing_key", "$", root)
        c = Compiled(self.mode)
        self.map_id = self.int_in(spec, "mapId", 0, 1000000, "$", default=-1)
        if self.map_id < 0:
            self.map_id = self.source.current_map()
        canonical = {"mapId": self.map_id}
        if self.mode == "run":
            c.max_ticks = self.int_in(spec, "max_ticks", 0, HARD_MAX_TICKS, "$")
            c.every = self.int_in(spec, "every", 1, MAX_EVERY, "$", default=1)
            c.on_unknown = "stop"
            if "on_unknown" in spec:
                v = spec["on_unknown"]
                if not isinstance(v, str):
                    raise Refused("type", "$.on_unknown", "want str, got " + jtype(v))
                if v not in ("stop", "continue"):
                    raise Refused("bad_value", "$.on_unknown", "want stop|continue")
                c.on_unknown = v
            c.run_key = None
            if "runKey" in spec:
                v = spec["runKey"]
                if not isinstance(v, str):
                    raise Refused("type", "$.runKey", "want str, got " + jtype(v))
                if v == "" or len(v) > 64:
                    raise Refused("bad_value", "$.runKey", "want 1-64 chars")
                c.run_key = v
            canonical.update({"max_ticks": c.max_ticks, "every": c.every, "on_unknown": c.on_unknown,
                              "runKey": c.run_key})
        c.tree = self.node(spec[root], "$." + root, "", True, False)
        canonical[root] = c.tree.canonical
        if self.mode == "run":
            if "watch" in spec:
                wl = spec["watch"]
                if not isinstance(wl, list):
                    raise Refused("type", "$.watch", "want list, got " + jtype(wl))
                if len(wl) > MAX_WATCHERS:
                    raise Refused("cap_watchers", "$.watch", "%d > %d" % (len(wl), MAX_WATCHERS))
                names = set()
                cw = []
                for i, w in enumerate(wl):
                    at = "$.watch[%d]" % i
                    w = self.obj(w, at)
                    self.keys(w, ("name", "tree"), at)
                    for k in ("name", "tree"):
                        if k not in w:
                            raise Refused("missing_key", at, k)
                    nm = w["name"]
                    if not isinstance(nm, str):
                        raise Refused("type", at + ".name", "want str, got " + jtype(nm))
                    if nm == "" or len(nm) > 64:
                        raise Refused("bad_value", at + ".name", "want 1-64 chars")
                    if nm in names:
                        raise Refused("duplicate_watch", at + ".name", nm)
                    names.add(nm)
                    tree = self.node(w["tree"], at + ".tree", nm + "/", False, True)
                    c.watch.append(Watcher(nm, tree))
                    cw.append({"name": nm, "tree": tree.canonical})
                canonical["watch"] = cw
            if "sample" in spec:
                at = "$.sample"
                s = self.obj(spec["sample"], at)
                self.keys(s, ("degrade", "every", "on_change_only", "probes"), at)
                c.sample_every = self.int_in(s, "every", 1, MAX_EVERY, at)
                c.sample_change_only = self.flag(s, "on_change_only", at)
                degrade = self.flag(s, "degrade", at)
                if "probes" not in s:
                    raise Refused("missing_key", at, "probes")
                c.sample = self.probe_map(s["probes"], at + ".probes")
                canonical["sample"] = {"every": c.sample_every, "on_change_only": c.sample_change_only,
                                       "degrade": degrade,
                                       "probes": dict((k, p.canonical) for k, p in c.sample)}
            if "snapshot_on_hit" in spec:
                c.snapshot = self.probe_map(spec["snapshot_on_hit"], "$.snapshot_on_hit")
                canonical["snapshot_on_hit"] = dict((k, p.canonical) for k, p in c.snapshot)
        if self.nodes > MAX_NODES:
            raise Refused("cap_nodes", "$", "%d > %d" % (self.nodes, MAX_NODES))
        if self.cells > MAX_CELLS:
            raise Refused("cap_cells", "$", "%d > %d" % (self.cells, MAX_CELLS))
        c.canonical = canonical
        return c

    def flag(self, d, k, at):
        if k not in d:
            return False
        if not isinstance(d[k], bool):
            raise Refused("type", at + "." + k, "want bool, got " + jtype(d[k]))
        return d[k]

    def probe_map(self, m, at):
        m = self.obj(m, at)
        if not m:
            raise Refused("bad_value", at, "want at least one probe")
        out = []
        for k in sorted(m):
            if k == "" or len(k) > 64:
                raise Refused("bad_value", at, "probe names are 1-64 chars")
            out.append((k, self.probe(m[k], at + "." + k, False)))
        return out

    # -- nodes
    def node(self, x, at, prefix, is_until_root, is_watch_root):
        d = self.obj(x, at)
        kinds = [k for k in NODE_KINDS if k in d]
        if not kinds:
            raise Refused("unknown_node", at, "no node kind among: " + ",".join(sorted(d)))
        if len(kinds) > 1:
            raise Refused("unknown_node", at, "two node kinds: " + ",".join(kinds))
        kind = kinds[0]
        self.keys(d, (kind, "id", "optional") + NODE_KEYS[kind], at)
        self.nodes += 1
        nid = prefix + "n%d" % self.idn
        self.idn += 1
        if "id" in d:
            v = d["id"]
            if not isinstance(v, str):
                raise Refused("type", at + ".id", "want str, got " + jtype(v))
            if v == "" or len(v) > 64:
                raise Refused("bad_value", at + ".id", "want 1-64 chars")
            nid = v
        if nid in self.ids:
            raise Refused("duplicate_id", at, nid)
        self.ids.add(nid)
        n = Node(kind, nid)
        n.optional = self.flag(d, "optional", at)
        body = d[kind]
        cd = {"id": nid}
        if n.optional:
            cd["optional"] = True
        sub = at + "." + kind
        if kind in ("all", "any"):
            if not isinstance(body, list):
                raise Refused("type", sub, "want list, got " + jtype(body))
            if not body:
                raise Refused("empty_children", sub, kind)
            for i, ch in enumerate(body):
                n.children.append(self.node(ch, "%s[%d]" % (sub, i), prefix, False, False))
            cd[kind] = [ch.canonical for ch in n.children]
        elif kind in ("not", "edge", "stays", "alarm"):
            if kind == "alarm" and not is_watch_root:
                raise Refused("alarm_not_root", at, "alarm is a watch root only")
            n.children.append(self.node(body, sub, prefix, False, False))
            cd[kind] = n.children[0].canonical
            if kind == "edge":
                if "dir" in d:
                    if not isinstance(d["dir"], str):
                        raise Refused("type", at + ".dir", "want str, got " + jtype(d["dir"]))
                    if d["dir"] not in ("rise", "fall"):
                        raise Refused("bad_value", at + ".dir", "want rise|fall")
                    n.dir = d["dir"]
                cd["dir"] = n.dir
            if kind == "stays":
                n.ticks = self.int_in(d, "ticks", 0, HARD_MAX_TICKS, at)
                cd["ticks"] = n.ticks
        elif kind == "changed":
            n.probe = self.probe(body, sub, True)
            cd[kind] = n.probe.canonical
        elif kind == "cmp":
            if not isinstance(body, list):
                raise Refused("type", sub, "want list, got " + jtype(body))
            if len(body) != 3:
                raise Refused("bad_value", sub, "cmp is [probe, op, value]")
            n.probe = self.probe(body[0], sub + "[0]", True)
            op = body[1]
            if not isinstance(op, str):
                raise Refused("type", sub + "[1]", "want str, got " + jtype(op))
            if op not in OPS:
                raise Refused("cmp_op", sub + "[1]", op)
            n.op = op
            n.lit = self.literal(n.probe, op, body[2], sub + "[2]")
            cd[kind] = [n.probe.canonical, op, n.lit]
            if "tol" in d:
                t = d["tol"]
                if not is_num(t):
                    raise Refused("type", at + ".tol", "want num, got " + jtype(t))
                if t < 0:
                    raise Refused("bad_value", at + ".tol", "want >= 0")
                if op not in ("==", "!="):
                    raise Refused("cmp_op", at + ".tol", "tol applies to == and != only")
                if n.probe.vtype() not in ("num", "any"):
                    raise Refused("cmp_type", at + ".tol", "tol needs a number probe")
                n.tol = t
                cd["tol"] = t
        n.canonical = cd
        return n

    def literal(self, probe, op, lit, at):
        vt = probe.vtype()
        if op in ("in", "hour_in"):
            if not (isinstance(lit, list) and len(lit) == 2 and is_num(lit[0]) and is_num(lit[1])):
                raise Refused("cmp_type", at, op + " wants [num, num]")
            if vt not in ("num", "any"):
                raise Refused("cmp_type", at, op + " needs a number probe, got " + vt)
            if op == "in" and lit[0] > lit[1]:
                raise Refused("bad_value", at, "in [a,b] wants a <= b")
            return lit
        if op in ("<", "<=", ">", ">="):
            if not is_num(lit):
                raise Refused("cmp_type", at, op + " wants num, got " + jtype(lit))
            if vt not in ("num", "any"):
                raise Refused("cmp_type", at, op + " needs a number probe, got " + vt)
            return lit
        lt = jtype(lit)
        if lt not in ("num", "bool", "str"):
            raise Refused("cmp_type", at, "want num|bool|str, got " + lt)
        if vt != "any" and lt != vt:
            raise Refused("cmp_type", at, "probe is %s, value is %s" % (vt, lt))
        return lit

    # -- probes
    def probe(self, x, at, counts):
        d = self.obj(x, at)
        if "p" not in d:
            raise Refused("missing_key", at, "p")
        name = d["p"]
        if not isinstance(name, str):
            raise Refused("type", at + ".p", "want str, got " + jtype(name))
        if name not in PROBES:
            if name.startswith("pawn.flight.") or name.startswith("pawn.anim.") or name == "static.call":
                raise Refused("probe_not_in_v1", at + ".p", name)
            raise Refused("unknown_probe", at + ".p", name)
        ptype, req, opt = PROBES[name]
        allowed = ("p", "mapId") + req + opt
        if name in SPATIAL:
            allowed = allowed + ("cell", "rect", "reduce", "where")
        self.keys(d, allowed, at)
        for k in req:
            if k not in d:
                raise Refused("missing_arg", at, k)
        if counts:
            self.nodes += 1
        p = Probe()
        p.name, p.ptype = name, ptype
        p.map_id = self.map_id
        for k in ARG_ORDER:
            if k not in d:
                continue
            v = d[k]
            ak = at + "." + k
            if k in ("cell", "rect"):
                n = 2 if k == "cell" else 4
                if not (isinstance(v, list) and len(v) == n and all(is_int(c) for c in v)):
                    raise Refused("bad_arg", ak, "want %d integers" % n)
                if k == "cell":
                    p.cell = [int(c) for c in v]
                else:
                    p.rect = [int(c) for c in v]
            elif k == "reduce":
                if not isinstance(v, str):
                    raise Refused("type", ak, "want str, got " + jtype(v))
                if v not in REDUCERS:
                    raise Refused("reduce_bad", ak, v)
                p.reduce = v
            elif k == "where":
                if not (isinstance(v, list) and len(v) == 2 and isinstance(v[0], str)):
                    raise Refused("bad_arg", ak, "want [op, value]")
                if v[0] not in ("==", "!=", "<", "<=", ">", ">="):
                    raise Refused("cmp_op", ak, v[0])
                p.where_op, p.where_lit = v[0], v[1]
            elif k == "mapId":
                if not is_int(v) or v < 0:
                    raise Refused("bad_arg", ak, "want integer >= 0")
                p.map_id = int(v)
            elif k == "f":
                if not isinstance(v, str) or v not in F_VALUES[name]:
                    raise Refused("bad_arg", ak, "want one of " + "|".join(F_VALUES[name]))
                p.args[k] = v
            elif k == "path":
                if not isinstance(v, str) or v == "":
                    raise Refused("bad_arg", ak, "want a field path")
                if "(" in v or ")" in v:
                    raise Refused("field_method", ak, "fields and properties only: " + v)
                p.args[k] = v
            elif k == "source":
                if not isinstance(v, str) or v not in RING_SOURCES:
                    raise Refused("bad_arg", ak, "want one of " + "|".join(RING_SOURCES))
                p.args[k] = v
            else:   # def, pawn, thing, filter
                if not isinstance(v, str) or v == "":
                    raise Refused("bad_arg", ak, "want a non-empty string")
                p.args[k] = v
        size = self.source.map_size(p.map_id)
        if name in SPATIAL:
            if (p.cell is None) == (p.rect is None):
                raise Refused("bad_arg", at, "want exactly one of cell, rect")
            if p.cell is not None and (p.reduce is not None or p.where_op is not None):
                raise Refused("reduce_bad", at, "reduce and where need a rect")
            if p.rect is not None:
                self.check_rect_reduce(p, at)
        if p.cell is not None or p.rect is not None or name in ("map.sky_glow", "map.count"):
            if size is None:
                raise Refused("map_unknown", at, "mapId %d" % p.map_id)
        if p.cell is not None:
            x, z = p.cell
            if not (0 <= x < size[0] and 0 <= z < size[1]):
                raise Refused("cell_oob", at + ".cell", "%d,%d outside %dx%d" % (x, z, size[0], size[1]))
        if p.rect is not None:
            x, z, w, h = p.rect
            if w <= 0 or h <= 0:
                raise Refused("rect_empty", at + ".rect", "%dx%d" % (w, h))
            if not (0 <= x and 0 <= z and x + w <= size[0] and z + h <= size[1]):
                raise Refused("cell_oob", at + ".rect", "%d,%d,%d,%d outside %dx%d" % (x, z, w, h, size[0], size[1]))
            if name in SPATIAL:
                self.cells += w * h
        cd = {"p": name}
        cd.update(p.args)
        if p.cell is not None:
            cd["cell"] = p.cell
        if p.rect is not None:
            cd["rect"] = p.rect
        if p.reduce is not None:
            cd["reduce"] = p.reduce
        if p.where_op is not None:
            cd["where"] = [p.where_op, p.where_lit]
        if name in SPATIAL or name in ("map.sky_glow", "map.count"):
            cd["mapId"] = p.map_id
        p.canonical = cd
        parts = [name] + ["%s=%s" % (k, key_val(p.args[k])) for k in sorted(p.args)]
        if p.cell is not None:
            parts.append("cell=%d,%d" % tuple(p.cell))
        if p.rect is not None:
            parts.append("rect=%s" % key_val(p.rect))
        p.key = " ".join(parts)
        why = self.source.refuse(p.key)
        if why:
            raise Refused("bind", at, why)
        return p

    def check_rect_reduce(self, p, at):
        if p.reduce is None:
            raise Refused("reduce_bad", at, "a rect needs reduce")
        if p.reduce in ("max", "min"):
            if p.ptype != "num":
                raise Refused("reduce_bad", at, p.reduce + " needs a number probe")
            if p.where_op is not None:
                raise Refused("reduce_bad", at, p.reduce + " takes no where")
            return
        if p.where_op is None:
            if p.ptype != "bool":
                raise Refused("reduce_bad", at, p.reduce + " over a non-bool probe needs where")
            p.where_op, p.where_lit = "==", True
            return
        lt = jtype(p.where_lit)
        if p.where_op in ("<", "<=", ">", ">="):
            if p.ptype != "num" or lt != "num":
                raise Refused("cmp_type", at + ".where", "ordered where needs num")
        elif lt != p.ptype:
            raise Refused("cmp_type", at + ".where", "probe is %s, value is %s" % (p.ptype, lt))


class Watcher(object):
    def __init__(self, name, tree):
        self.name, self.tree = name, tree
        self.events = 0
        self.unknowns = 0
        self.disarmed = None


class Compiled(object):
    def __init__(self, mode):
        self.mode = mode
        self.tree = None
        self.watch = []
        self.sample = None
        self.sample_every = 0
        self.sample_change_only = False
        self.snapshot = None
        self.max_ticks = 0
        self.every = 1
        self.on_unknown = "stop"
        self.run_key = None
        self.canonical = None


# ---------------------------------------------------------------------------------------------- evaluation
def rec(v, status, detail):
    r = {"v": v, "status": status}
    if status != "ok":
        r["detail"] = detail
    return r


class Evaluator(object):
    """Evaluates compiled trees against an IProbeSource-shaped object: current_map(), map_size(mapId),
    refuse(key) -> None|reason, read(key) -> (v, status, detail)."""

    def __init__(self, source):
        self.source = source
        self.reads = 0
        self.node_evals = 0
        self.ring_base = {}
        self.first_error = None

    def raw(self, key, ptype):
        self.reads += 1
        got = self.source.read(key)
        v, status, detail = got[0], got[1], (got[2] if len(got) > 2 else "")
        if status not in STATUSES:
            return None, "error", "bad status " + str(status)
        if status != "ok":
            return None, status, detail
        t = jtype(v)
        if ptype == "any":
            if t not in ("num", "bool", "str"):
                return None, "error", "type: got " + t
        elif t != ptype:
            return None, "error", "type: want %s, got %s" % (ptype, t)
        return v, "ok", ""

    def arm_rings(self, probes):
        for p in probes:
            if p.name == "ring.count" and p.key not in self.ring_base:
                self.ring_base[p.key] = self.raw(p.key, "num")

    def read_probe(self, p):
        if p.rect is not None and p.name in SPATIAL:
            x0, z0, w, h = p.rect
            vals = []
            bad = None
            for z in range(z0, z0 + h):
                for x in range(x0, x0 + w):
                    v, st, de = self.raw(p.cell_key(x, z), p.ptype)
                    if st != "ok" and bad is None:
                        bad = (st, de)
                    vals.append(v)
            if bad is not None:
                return None, bad[0], bad[1]
            if p.reduce == "max":
                return max(vals), "ok", ""
            if p.reduce == "min":
                return min(vals), "ok", ""
            hits = [cmp_value(v, p.where_op, p.where_lit, None) for v in vals]
            if p.reduce == "any":
                return any(hits), "ok", ""
            if p.reduce == "all":
                return all(hits), "ok", ""
            return sum(1 for b in hits if b), "ok", ""
        vt = p.vtype()
        v, st, de = self.raw(p.key, vt)
        if p.name == "ring.count" and st == "ok":
            b = self.ring_base.get(p.key)
            if b is None:
                return None, "error", "ring not armed"
            if b[1] != "ok":
                return None, b[1], "at arm: " + b[2]
            return v - b[0], "ok", ""
        return v, st, de

    def eval_node(self, n, tick, out):
        """-> (v, status, detail); appends this node's record to out in preorder."""
        self.node_evals += 1
        r = {"id": n.id}
        out.append(r)
        pv = None
        if n.kind in ("all", "any"):
            res = [self.eval_node(c, tick, out) for c in n.children]
            v, st, de = kleene(n.kind, res)
        elif n.kind == "not":
            cv, st, de = self.eval_node(n.children[0], tick, out)
            v = None if cv is None else (not cv)
        elif n.kind == "alarm":
            v, st, de = self.eval_node(n.children[0], tick, out)
        elif n.kind == "cmp":
            pv, st, de = self.read_probe(n.probe)
            if st == "ok":
                v, st, de = cmp_checked(pv, n.op, n.lit, n.tol)
            else:
                v = None
            self.note_error(st, de)
        elif n.kind == "changed":
            pv, st, de = self.read_probe(n.probe)
            self.note_error(st, de)
            if st != "ok":
                v = None
                n.has_prev = False
            else:
                v = n.has_prev and not same_value(pv, n.prev)
                n.has_prev, n.prev = True, pv
        elif n.kind == "edge":
            cv, st, de = self.eval_node(n.children[0], tick, out)
            if cv is None:
                v = None
                n.has_prev = False
            else:
                if not n.has_prev:
                    v = False
                elif n.dir == "rise":
                    v = (n.prev is False) and cv is True
                else:
                    v = (n.prev is True) and cv is False
                n.has_prev, n.prev = True, cv
        elif n.kind == "stays":
            cv, st, de = self.eval_node(n.children[0], tick, out)
            if cv is True:
                if n.start is None:
                    n.start = tick
                v = (tick - n.start) >= n.ticks
            else:
                n.start = None
                v = cv
        else:
            raise AssertionError(n.kind)
        if v is not None:
            st, de = "ok", ""
        elif n.optional:
            v, st, de = False, "ignored", st + ": " + de
        r["v"] = v
        r["status"] = st
        if st != "ok":
            r["detail"] = de
        if n.kind in ("cmp", "changed"):
            r["pv"] = pv
        return v, st, de

    def note_error(self, st, de):
        if st == "error" and self.first_error is None:
            self.first_error = de

    def evaluate(self, tree, tick):
        out = []
        self.first_error = None
        v, st, de = self.eval_node(tree, tick, out)
        if st == "ignored":
            st = "ok"
        return v, st, de, out


def kleene(kind, res):
    want = kind == "any"     # the value that decides: any->True, all->False
    for v, st, de in res:
        if v is want:
            return want, "ok", ""
    for v, st, de in res:
        if v is None:
            return None, st, de
    return (not want), "ok", ""


def same_value(a, b):
    return jtype(a) == jtype(b) and a == b


def cmp_value(v, op, lit, tol):
    if op in ("==", "!="):
        if is_num(v) and is_num(lit):
            eq = abs(v - lit) <= (tol or 0)
        else:
            eq = jtype(v) == jtype(lit) and v == lit
        return eq if op == "==" else not eq
    if op == "<":
        return v < lit
    if op == "<=":
        return v <= lit
    if op == ">":
        return v > lit
    if op == ">=":
        return v >= lit
    if op == "in":
        return lit[0] <= v <= lit[1]
    a, b = lit
    return (a <= v < b) if a <= b else (v >= a or v < b)


def cmp_checked(v, op, lit, tol):
    """cmp on a value whose type is checked at run time (thing.field is 'any')."""
    if op not in ("==", "!=") and not is_num(v):
        return None, "error", "type: %s needs num, got %s" % (op, jtype(v))
    if op in ("==", "!=") and jtype(v) != jtype(lit):
        return None, "error", "type: value is %s, literal is %s" % (jtype(v), jtype(lit))
    return cmp_value(v, op, lit, tol), "ok", ""


def all_probes(c):
    out = []

    def walk(n):
        if n.probe is not None:
            out.append(n.probe)
        for ch in n.children:
            walk(ch)
    walk(c.tree)
    for w in c.watch:
        walk(w.tree)
    for _, p in (c.sample or []):
        out.append(p)
    for _, p in (c.snapshot or []):
        out.append(p)
    return out


def first_unknown(records):
    for r in records:
        if "pv" in r and r["status"] not in ("ok", "ignored"):
            return r
    return records[0] if records else None


class Run(object):
    """One armed run over a stream of end-of-tick frames (the pure half of jawa/safe_advance + until)."""

    def __init__(self, compiled, source, clock=None):
        self.c, self.src = compiled, source
        self.ev = Evaluator(source)
        self.clock = clock
        self.state = "running"
        self.hit_tick = None
        self.values = []
        self.at_arm = []
        self.true_at_arm = False
        self.tick_from = self.tick_to = None
        self.epoch = None
        self.triggers = []
        self.evals = 0
        self.gaps = []
        self.gap_open = None
        self.unknown = None
        self.events = []
        self.seq = 0
        self.rows = []
        self.dropped = 0
        self.last_row = None
        self.snapshot = None
        self.ms_total = 0.0
        self.ms_max = 0.0

    def timed(self, fn):
        t0 = self.clock() if self.clock else 0.0
        out = fn()
        if self.clock:
            ms = self.clock() - t0
            self.ms_total += ms
            self.ms_max = max(self.ms_max, ms)
        return out

    def eval_until(self, tick):
        v, st, de, recs = self.timed(lambda: self.ev.evaluate(self.c.tree, tick))
        self.evals += 1
        self.values = recs
        if v is None:
            if self.gap_open is None:
                self.gap_open = [tick, tick]
                self.gaps.append(self.gap_open)
            else:
                self.gap_open[1] = tick
        else:
            self.gap_open = None
        return v, st, de

    def eval_watch(self, tick):
        for w in self.c.watch:
            if w.disarmed is not None:
                continue
            v, st, de, recs = self.timed(lambda: self.ev.evaluate(w.tree, tick))
            if self.ev.first_error is not None:
                w.disarmed = {"tick": tick, "why": "error: " + self.ev.first_error}
                continue
            if v is None:
                w.unknowns += 1
                continue
            if v:
                self.seq += 1
                w.events += 1
                ev = {"name": w.name, "seq": self.seq, "tick": tick, "values": recs}
                if w.tree.kind == "alarm":
                    ev["alarm"] = True
                    w.disarmed = {"tick": tick, "why": "alarm"}
                self.events.append(ev)

    def take_sample(self, k, tick):
        if self.c.sample is None or k % self.c.sample_every != 0:
            return
        vals = {}
        for name, p in self.c.sample:
            v, st, de = self.ev.read_probe(p)
            vals[name] = rec(v, st, de)
        if self.c.sample_change_only and self.last_row is not None and canon(vals) == canon(self.last_row):
            return
        self.last_row = vals
        if len(self.rows) >= MAX_SAMPLE_ROWS:
            self.dropped += 1
            return
        self.rows.append({"tick": tick, "values": vals})

    def take_snapshot(self):
        if self.c.snapshot is None:
            return
        self.snapshot = {}
        for name, p in self.c.snapshot:
            v, st, de = self.ev.read_probe(p)
            self.snapshot[name] = rec(v, st, de)

    def arm(self, frame):
        self.tick_from = self.tick_to = frame["tick"]
        self.epoch = frame.get("epoch", 0)
        for n in walk_nodes(self.c):
            n.reset()
        self.ev.arm_rings(all_probes(self.c))
        v, st, de = self.eval_until(frame["tick"])
        self.at_arm = self.values
        self.eval_watch(frame["tick"])
        self.take_sample(0, frame["tick"])
        if v is True:
            self.state, self.hit_tick, self.true_at_arm = "hit", frame["tick"], True
            self.triggers = ["cond"]
            self.take_snapshot()
        elif v is None and self.c.on_unknown == "stop":
            self.state, self.triggers = "unknown", ["unknown"]
            self.unknown = self.describe_unknown(st, de)
        elif self.c.max_ticks == 0:
            self.state, self.triggers = "done", ["deadline"]

    def describe_unknown(self, st, de):
        r = first_unknown(self.values)
        return {"id": r["id"] if r else None, "status": st, "detail": de}

    def step(self, frame):
        if self.state != "running":
            return
        tick = frame["tick"]
        if tick != self.tick_to + 1:
            self.state, self.triggers = "error", ["tick_gap"]
            return
        self.tick_to = tick
        if frame.get("epoch", 0) != self.epoch:
            self.state, self.triggers = "epoch", ["epoch"]
            return
        k = tick - self.tick_from
        hit = unk = False
        if k % self.c.every == 0 or k == self.c.max_ticks:
            v, st, de = self.eval_until(tick)
            self.eval_watch(tick)
            hit = v is True
            unk = v is None and self.c.on_unknown == "stop"
        self.take_sample(k, tick)
        stop = frame.get("stop")
        trig = []
        if hit:
            trig.append("cond")
            self.hit_tick = tick
            self.take_snapshot()
        if unk:
            trig.append("unknown")
            self.unknown = self.describe_unknown(st, de)
        if stop:
            trig.append(stop)
            self.state = "stopped"
        elif hit:
            self.state = "hit"
        elif unk:
            self.state = "unknown"
        elif k >= self.c.max_ticks:
            self.state = "done"
            trig.append("deadline")
        self.triggers = trig

    def end_of_series(self):
        if self.state == "running":
            self.state, self.triggers = "stopped", ["series_end"]

    def result(self):
        c = self.c
        return {
            "runKey": c.run_key, "state": self.state, "hitTick": self.hit_tick, "values": self.values,
            "atArm": self.at_arm, "trueAtArm": self.true_at_arm, "executed": self.tick_to - self.tick_from,
            "tickFrom": self.tick_from, "tickTo": self.tick_to, "epoch": self.epoch, "triggers": self.triggers,
            "unknown": self.unknown,
            "coverage": {"every": c.every, "evals": self.evals, "resolutionTicks": c.every, "gaps": self.gaps,
                         "complete": not self.gaps},
            "cost": {"evals": self.evals, "nodeEvals": self.ev.node_evals, "reads": self.ev.reads,
                     "evalMsTotal": round(self.ms_total, 3), "evalMsMax": round(self.ms_max, 3)},
            "watch": self.events,
            "watchers": [{"name": w.name, "events": w.events, "unknowns": w.unknowns, "disarmed": w.disarmed}
                         for w in c.watch],
            "sample": self.rows, "sampleDropped": self.dropped, "snapshot": self.snapshot, "mutations": [],
            "canonical": c.canonical,
        }


def walk_nodes(c):
    out = []

    def walk(n):
        out.append(n)
        for ch in n.children:
            walk(ch)
    walk(c.tree)
    for w in c.watch:
        walk(w.tree)
    return out


def refusal(e):
    return {"refused": e.name, "at": e.at, "detail": e.detail}


def cond_eval(spec, source):
    """jawa/cond_eval: compile {tree, mapId?} and evaluate once, no tick."""
    try:
        c = Compiler(source, "eval").compile_spec(spec)
    except Refused as e:
        return refusal(e)
    ev = Evaluator(source)
    ev.arm_rings(all_probes(c))
    v, st, de, recs = ev.evaluate(c.tree, 0)
    return {"canonical": c.canonical, "v": v, "status": st, "values": recs,
            "cost": {"nodeEvals": ev.node_evals, "reads": ev.reads}}


def evaluate(spec, series, mode="run"):
    """The offline twin of a run: spec (wire JSON) over a SeriesSource-shaped series. -> result dict."""
    if mode == "eval":
        return cond_eval(spec, series)
    try:
        c = Compiler(series, "run").compile_spec(spec)
    except Refused as e:
        return refusal(e)
    r = Run(c, series)
    frames = series.frames
    series.goto(0)
    r.arm(frames[0])
    for i in range(1, len(frames)):
        if r.state != "running":
            break
        series.goto(i)
        r.step(frames[i])
    r.end_of_series()
    return r.result()


# ---------------------------------------------------------------------------------------------- vectors
class SeriesSource(object):
    """An IProbeSource over a vector's frames. Reads carry forward from earlier frames; a key never given reads
    status error. `refuse` maps a probe key to a bind refusal reason."""

    def __init__(self, vec):
        m = vec.get("map", [250, 250])
        self.size = None if m is None else (int(m[0]), int(m[1]))
        self.cur_map = int(vec.get("mapId", 0))
        self.refusals = vec.get("refuse", {})
        self.frames = vec.get("frames") or [{"tick": 0}]
        self.state = {}
        self.at = -1

    def current_map(self):
        return self.cur_map

    def map_size(self, map_id):
        return self.size if map_id == self.cur_map else None

    def refuse(self, key):
        return self.refusals.get(key)

    def goto(self, i):
        while self.at < i:
            self.at += 1
            for k, v in sorted(self.frames[self.at].get("reads", {}).items()):
                self.state[k] = v

    def read(self, key):
        v = self.state.get(key)
        if v is None:
            return None, "error", "no series value for " + key
        return v[0], v[1], (v[2] if len(v) > 2 else "")


def run_vector(vec):
    if "spec_text" in vec:
        try:
            spec = parse_json(vec["spec_text"])
        except ValueError:
            return {"refused": "json", "at": "$", "detail": "parse error"}
    else:
        spec = vec["spec"]
    src = SeriesSource(vec)
    if vec.get("mode", "run") == "eval":
        src.goto(0)
    return evaluate(spec, src, vec.get("mode", "run"))


def run_vectors_text(text):
    """The vector output both twins print: one '<name>\\t<canonical result>' line per vector."""
    doc = parse_json(text)
    lines = []
    for vec in doc["vectors"]:
        lines.append(vec["name"] + "\t" + canon(run_vector(vec)) + "\n")
    return "".join(lines)


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        sys.stdout.write(run_vectors_text(fh.read()))
