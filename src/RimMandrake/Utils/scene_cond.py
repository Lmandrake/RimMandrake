"""scene.cond - the helpers that build a scene's conditions and tracks. `from scene import cond as c`.

A condition is data: the game evaluates it at the end of each tick and it decides only when to stop (scene_contracts/run.md).
The builders of conds_dsl.py (cell, fw, pawn, thing, game, map_, ring, all_, any_, not_, edge, stays, changed) are the same
objects here. Compare a probe with a number to get a condition; join conditions with & | ~.

    c.track(of, path)      a value to record on every tick. `of`: an alias, a group, or a thing id ("Human12")
    c.value(of, path)      the same value, in a condition: c.value("Human12", "positionInt.x") > 40
    c.gone_ok(of, path, cond)   cond, or the thing is gone: a gone thing is then readable, and the part is true
    c.ticks(n)             n ticks after the start (the same as until=n)
    c.played(n)            in a contract: n ticks of the judged run have played (the run's start tick is written in at the run)
    c.state(of, path)      the state of a value as text: ok, null, gone, unbound, error. It can always be read:
                           c.state("people[0]", "positionInt") == "gone" says that colonist died or left the map"""
import re

import conds
from conds import (Expr, cell, fw, pawn, thing, game, map_, ring, all_, any_, not_, edge, stays, changed, to_tree)  # noqa: F401
from scene_core import Refused

_STEP = r"(?:comp<[A-Za-z_][\w.]*>|[A-Za-z_]\w*)(?:\[(?:\d+(?:,\d+)?|cell)\])*"
PATH = re.compile(r"^%s(?:\.%s)*$" % (_STEP, _STEP))
OF = re.compile(r"^(?:thing:[\w.]+|def:[\w.]+/[\w.\- ]+|static:[\w.+`]+|map|game|world|\$|[A-Za-z_]\w*(?:\[\d+\])?)$")
VALUE_PROBES = ("value", "value.state")
TICK = "game.tick"


class Track(object):
    """A value to record on every tick."""

    def __init__(self, of, path):
        self.of, self.path = of, path
        self.name = "%s.%s" % (of, path)

    def __repr__(self):
        return "track(%s)" % self.name


def track(of, path):
    return Track(of, path)


class ProbeTrack(Track):
    """A named engine probe to record on every tick ({name, probe} in jawa/run_until's record)."""

    def __init__(self, name, probe):
        self.of, self.path, self.name, self.probe = None, None, name, probe

    def __repr__(self):
        return "probe_track(%s)" % self.name


def flight(pawn):
    """-> the tracks of one bird's flight and flip-book frame (pawn.flight.*, pawn.anim.*), named as flight_frames reads
    them. `pawn` is the pawn's thing id (`thing:` is dropped). The judge of the series is flight_frames.py."""
    import flight_frames
    pid = pawn[6:] if pawn.startswith("thing:") else pawn
    return [ProbeTrack(flight_frames.track_name(pid, f), {"p": flight_frames.PROBE_OF[f], "pawn": pid})
            for f in flight_frames.FIELDS]


class Ticks(object):
    def __init__(self, n):
        self.n = n


def ticks(n):
    return Ticks(n)


def value(of, path):
    return Expr({"p": "value", "of": of, "path": path}, "any")


def state(of, path):
    return Expr({"p": "value.state", "of": of, "path": path}, "any")


def played(n):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise Refused("BAD_ARGS", "played(n): n is a number of ticks, 1 or more, not %r" % (n,))
    return game.tick >= {"played": n}


def gone_ok(of, path, cond):
    return any_(Expr({"p": "value.state", "of": of, "path": path}, "any") == "gone", cond)


def bad_path(of, path):
    """Why this track is not in the path grammar, or None."""
    if not isinstance(of, str) or not OF.match(of):
        return "target %r is not an alias, a group member, thing:<id>, def:<Type>/<name>, static:<Type>, map, game or world" % (of,)
    if not isinstance(path, str) or not PATH.match(path):
        return "path %r is not field steps joined by points (a step is a field, a property, comp<Class> or [n])%s" % (
            path, "; a method is never called" if isinstance(path, str) and "(" in path else "")
    return None


def walk(node):
    """-> [(probe, optional)] of a condition tree, in order. `optional`: a node above it counts an unreadable value as false."""
    out = []

    def go(n, opt):
        if isinstance(n, dict):
            opt = opt or bool(n.get("optional"))
            if "p" in n:
                out.append((n, opt))
                return
            for k in sorted(n):
                go(n[k], opt)
        elif isinstance(n, list):
            for x in n:
                go(x, opt)
    go(node, False)
    return out


def probe_name(p):
    if p.get("p") in VALUE_PROBES or p.get("p") == "thing.field":
        return "%s.%s%s" % (p.get("of") or p.get("thing"), p.get("path"), "#state" if p.get("p") == "value.state" else "")
    rest = ",".join("%s=%s" % (k, p[k]) for k in sorted(p) if k not in ("p", "id"))
    return p["p"] + ("(%s)" % rest if rest else "")


def excused(node):
    """-> the names of the values that a gone_ok() covers: an any of `value.state == gone` and something."""
    out = set()

    def go(n):
        if isinstance(n, dict):
            kids = n.get("any")
            if isinstance(kids, list):
                for k in kids:
                    cmp = k.get("cmp") if isinstance(k, dict) else None
                    if cmp and isinstance(cmp[0], dict) and cmp[0].get("p") == "value.state" and cmp[1:] == ["==", "gone"]:
                        out.add("%s.%s" % (cmp[0].get("of"), cmp[0].get("path")))
            for v in n.values():
                go(v)
        elif isinstance(n, list):
            for v in n:
                go(v)
    go(node)
    return out


def compile_until(until):
    """-> (tree, None) or (None, ticks). Refuses UNRECORDED_VALUE / BAD_ARGS; no game is asked."""
    if isinstance(until, Ticks):
        until = until.n
    if isinstance(until, bool) or until is None:
        raise Refused("BAD_ARGS", "until is a condition of scene.cond or a number of ticks, not %r" % (until,))
    if isinstance(until, int):
        if until < 1:
            raise Refused("BAD_ARGS", "until=%d: a number of ticks is 1 or more" % until)
        return None, until
    try:
        tree = to_tree(until)
    except (TypeError, ValueError, AttributeError) as e:
        raise Refused("BAD_ARGS", "until is a condition of scene.cond or a number of ticks: %s" % e)
    if not isinstance(tree, dict):
        raise Refused("BAD_ARGS", "until is a condition of scene.cond or a number of ticks, not %r" % (until,))
    probes = walk(tree)
    if not probes:
        raise Refused("UNRECORDED_VALUE", "the condition reads no value (`help cond`)")
    for p, opt in probes:
        if p["p"] not in VALUE_PROBES and p["p"] not in conds.PROBES:
            raise Refused("UNRECORDED_VALUE", "no track or tap records %r; the recordable probes: %s (`help cond`), or file a "
                          "hands ticket" % (p["p"], ", ".join(sorted(conds.PROBES) + list(VALUE_PROBES))))
        if opt:
            raise Refused("UNRECORDED_VALUE", "%s stands under optional=True, which counts an unreadable value as false; use "
                          "c.gone_ok(...)" % probe_name(p))
        if "path" in p:
            why = bad_path(p.get("of") or p.get("thing"), p["path"])
            if why:
                raise Refused("UNRECORDED_VALUE", "%s (`help cond`)" % why)
    return tree, None


def _taps(op, names, where=None):
    """A recorded tap probe for scene.judge, with an optional equality filter for count."""
    p = {"p": op, "taps": list(names)}
    if where:
        p["where"] = where
    return Expr(p, "num" if op == "count" else "bool")


def count(tap, **where):
    """Number of matching records of an armed tap."""
    return _taps("count", (tap,), where)


def seq(*taps):
    """The named taps occurred in this entry order."""
    return _taps("seq", taps)


def before(first, second):
    """The first occurrence of one tap entered before the first occurrence of another."""
    return _taps("before", (first, second))


def after(first, second):
    """The first occurrence of one tap entered after the first occurrence of another."""
    return _taps("after", (first, second))
