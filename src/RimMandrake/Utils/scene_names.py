"""scene_names.py - five names of the scene library, built by RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP when the
first of its three scenes needed each: scene.contract, s.stage, s.act, s.read (and s.read_many), s.shot.

Pages: scene_contracts/<name>.md. What every name shares: scene_core.py and design/specs/2026-11-23-scene-library/boundary.md.
The hands behind them and their wire: design/specs/2026-11-23-bridge-v2-hands/boundary.md (jawa/read_paths, jawa/act_batch) and
design/specs/2026-11-23-bridge-v2/boundary.md §THE STAGE READ-BACK (jawa/spawn_pawn, jawa/build_batch, jawa/set_terrain_batch,
jawa/destroy_batch). A fake game proves what this Python does, never what the game does."""
import hashlib
import json
import os
import re
import uuid

import conds
import scene_cond as cond
from scene_core import NOT_APPLICABLE, CallFailed, Fault, Receipt, Refused, ReplyLost, Value

READ_PATHS, ACT_BATCH, CAPTURE = "jawa/read_paths", "jawa/act_batch", "jawa/artboard_capture"
SPAWN, BUILD, TERRAIN, CLEAN = "jawa/spawn_pawn", "jawa/build_batch", "jawa/set_terrain_batch", "jawa/destroy_batch"
SESSION = "jawa/session"
LIST_PAWNS, VANISH = "jawa/list_pawns", "jawa/pawn_force_incapacitate"
KINDS = ("A", "B", "C")
OWED_TAPS = "RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY"
OWED_TUNE = "RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST"
OWED_ORDER = "RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER"
OWED_RELOAD = "RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES"
STAGE_MAKE = "python3 src/RimMandrake/Utils/stage_map.py make <game> --kind settlement"
DUMP = os.path.join("observed", "inventory", "DefDump_OFFICIAL")
ALIAS = re.compile(r"^[A-Za-z_]\w*$")
MEMBER = re.compile(r"^([A-Za-z_]\w*)(?:\[(\d+)\])?$")
NAMED = ("thing:", "def:", "static:")
WHOLE = ("map", "game", "world")
TAP_PROBES = ("count", "seq", "before", "after")
ROWS_LISTED = 50                        # JawaBenchStageReadBack.ListedWrong: the most rows that one readBack block lists


# ================================================================================================ scene.contract
class Contract(object):
    """What the scene claims, as data (scene_contracts/contract.md). `plan(request, start)` is the judge's contract.json."""

    def __init__(self, claim, kind, trees, end, limit, budget, could_not_look):
        self.claim, self.kind, self.end, self.limit, self.budget = claim, kind, end, limit, budget
        self.exposure, self.success, self.forbidden = trees.get("exposure"), trees["success"], trees.get("forbidden")
        self.needs_record = sorted({(p["of"], p["path"]) for t in trees.values() for p, _o in cond.walk(t) if p.get("p") in cond.VALUE_PROBES})
        self.needs_record = [cond.track(of, path) for of, path in self.needs_record]
        self._trees = trees
        body = dict(trees, claim=claim, kind=kind, end=_end_text(end), limit=limit, budget=list(budget) if isinstance(budget, tuple) else budget)
        self.hash = hashlib.sha256(conds.canon(body).encode("utf-8")).hexdigest()
        self.receipt = Receipt("scene.contract", "contract_" + uuid.uuid4().hex[:10])
        self.receipt.game = self.receipt.build = NOT_APPLICABLE
        self.receipt.could_not_look = list(could_not_look)

    def plan(self, request=None, start=None):
        """-> the judge's contract (rimflow/scene_judge.py PLAN_KEYS). `c.played(n)` becomes `game.tick >= start + n`."""
        out = {"claim": self.claim, "kind": "A" if self.kind == "A" else "B", "version": "contract-%s" % self.hash[:12],
               "allowed_miss": isinstance(self.budget, tuple)}
        for role, tree in self._trees.items():
            out[role] = _played(tree, start)
        if request:
            out["request"] = request
        return out

    def __repr__(self):
        return "contract %s (kind %s): %s" % (self.hash[:12], self.kind, self.claim)


def _end_text(end):
    return end.n if isinstance(end, cond.Ticks) else end if isinstance(end, int) else cond.to_tree(end)


def _played(node, start):
    if isinstance(node, dict):
        if set(node) == {"played"}:
            if start is None:
                raise Fault("COULD_NOT_LOOK", detail="c.played(%s) needs the start tick of the judged run, and it is not known" % node["played"])
            return start + node["played"]
        return {k: _played(v, start) for k, v in node.items()}
    if isinstance(node, list):
        return [_played(x, start) for x in node]
    return node


def _join(name, x, how):
    items = x if isinstance(x, (list, tuple)) else [] if x is None else [x]
    trees = []
    for it in items:
        try:
            t = cond.to_tree(it)
        except (TypeError, ValueError, AttributeError) as e:
            raise Refused("BAD_ARGS", "%s holds %r, which is not a condition of scene.cond: %s" % (name, it, e))
        if not isinstance(t, dict):
            raise Refused("BAD_ARGS", "%s holds %r, which is not a condition of scene.cond (`help cond`)" % (name, it))
        trees.append(t)
    if not trees:
        return None
    return trees[0] if len(trees) == 1 else {how: trees}


def nodes(tree):
    """-> the size of a condition tree as the game and the judge count it: tree nodes plus probe objects (conds.MAX_NODES)."""
    if isinstance(tree, dict):
        return 1 if "p" in tree else 1 + sum(nodes(v) for v in tree.values() if isinstance(v, (dict, list)))
    if isinstance(tree, list):
        return sum(nodes(v) for v in tree if isinstance(v, (dict, list)))
    return 0


def _def_names():
    """-> the set of defNames of the frozen official dump, or None when it is not readable here."""
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    folder = os.path.join(root, DUMP)
    if not os.path.isdir(folder):
        return None
    names = set()
    for f in os.listdir(folder):
        if f.endswith(".json"):
            try:
                with open(os.path.join(folder, f), encoding="utf-8") as fh:
                    names |= set(re.findall(r'"defName"\s*:\s*"([^"]+)"', fh.read()))
            except OSError:
                return None
    return names or None


def contract(claim, kind, exposure, success, forbidden, end, limit, budget=None):
    """State what the scene claims, before the game is touched (scene_contracts/contract.md). No bridge call is made."""
    if not isinstance(claim, str) or len(claim.split()) < 3:
        raise Refused("BAD_ARGS", "claim is one sentence about what the player sees or can do, not %r" % (claim,))
    if kind not in KINDS:
        raise Refused("BAD_ARGS", "kind is 'A' (deterministic), 'B' (stochastic) or 'C' (a hunt), not %r" % (kind,))
    trees = {"success": _join("success", success, "all"), "exposure": _join("exposure", exposure, "all"),
             "forbidden": _join("forbidden", forbidden, "any")}
    trees = {k: v for k, v in trees.items() if v is not None}
    if "success" not in trees:
        raise Refused("BAD_ARGS", "success is empty: give the conditions that must hold (`help cond`)")
    if "exposure" not in trees:
        raise Refused("NO_EXPOSURE", "a success with no exposure can pass on a run where nothing happened: add the condition "
                      "that shows the opportunity happened (for example a raider stood in the moat)")
    if kind == "B" and budget is None:
        raise Refused("KIND_B_NO_BUDGET", "a kind B scene writes its budget before the first run: budget=<runs>, or (X, Y) "
                      "for X successes in Y valid opportunities")
    if kind == "A" and budget is not None:
        raise Refused("KIND_A_ALLOWED_MISS", "kind A is decided by one valid run and allows no miss: make it kind B, or remove budget=")
    if budget is not None and not ((isinstance(budget, int) and not isinstance(budget, bool) and budget >= 1) or
                                   (isinstance(budget, tuple) and len(budget) == 2 and all(isinstance(n, int) and n >= 1 for n in budget)
                                    and budget[0] <= budget[1])):
        raise Refused("BAD_ARGS", "budget is a number of runs, or (X, Y) with X <= Y, not %r" % (budget,))
    if end is None or isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise Refused("NO_END", "give both: end= (a condition, or a number of ticks) and limit= (the most ticks the scene may play)")
    try:
        _tree, n = cond.compile_until(end)
    except Refused as e:
        raise Refused(e.name if e.name != "BAD_ARGS" else "NO_END", "end: %s" % e.repair)
    if n is not None and n > limit:
        raise Refused("NO_END", "end is %d ticks and limit is %d: the scene would stop at its limit before its end" % (n, limit))
    for role, tree in trees.items():
        if nodes(tree) > conds.MAX_NODES:
            raise Refused("CONDITION_TOO_LARGE", "%s has %d nodes and the judge reads at most %d in one condition: name fewer "
                          "members, or put one part in exposure or forbidden" % (role, nodes(tree), conds.MAX_NODES))
    looked, defs = [], _def_names()
    for role, tree in trees.items():
        for p, opt in cond.walk(tree):
            kind_ = p.get("p")
            if kind_ in TAP_PROBES:
                raise Refused("UNRECORDED_VALUE", "%s reads the tap %s, and no cast tap is armed today (%s): name a value path "
                              "(`help cond`)" % (role, p.get("taps"), OWED_TAPS))
            if kind_ not in cond.VALUE_PROBES and kind_ not in conds.PROBES:
                raise Refused("UNRECORDED_VALUE", "%s: no track or tap records %r (`help cond`), or file a hands ticket" % (role, kind_))
            if opt:
                raise Refused("UNRECORDED_VALUE", "%s: %s stands under optional=True, which counts an unreadable value as false; use "
                              "c.gone_ok(...)" % (role, cond.probe_name(p)))
            if "path" in p:
                why = cond.bad_path(p.get("of") or p.get("thing"), p["path"])
                if why:
                    raise Refused("UNRECORDED_VALUE", "%s: %s (`help cond`)" % (role, why))
            of = p.get("of") or ""
            if of.startswith("def:"):
                name = of.split("/", 1)[-1]
                if defs is None:
                    looked.append("the def %s was not checked: the frozen dump %s is not readable here" % (name, DUMP))
                elif name not in defs:
                    import difflib
                    raise Refused("UNKNOWN_DEF", "%s is not in the frozen dump; near names: %s" % (
                        name, ", ".join(difflib.get_close_matches(name, defs, 5)) or "none"))
    looked.append("whether a success condition is already true before the first act: the judge decides that on the first sample")
    return Contract(claim, kind, trees, end, limit, budget, looked)


# ================================================================================================ aliases
def _check_alias_target(s, of):
    """A target that names an alias must name a bound one (pure: no bridge call). -> (alias, member) or (None, None)."""
    if not isinstance(of, str) or not of:
        raise Refused("BAD_ARGS", "a target is an alias, a group member like raiders[0], thing:<id>, def:<Type>/<name>, static:<Type> or map")
    if of.startswith(NAMED) or of in WHOLE:
        return None, None
    m = MEMBER.match(of)
    if not m:
        raise Refused("BAD_PATH", "target %r is not an alias, a member raiders[0], thing:<id>, def:, static: or map (`help read`)" % of)
    if m.group(1) not in s._aliases:
        raise Refused("UNKNOWN_ALIAS", "%s is not bound in this session (bound: %s): stage it, or read a def or a static" % (
            m.group(1), ", ".join(sorted(s._aliases)) or "none"))
    return m.group(1), None if m.group(2) is None else int(m.group(2))


def _thing_of(s, of):
    """-> thing:<id> for an alias or a member; the target itself for the others; None when the alias holds nothing there."""
    alias, i = _check_alias_target(s, of)
    if alias is None:
        return of
    got = s._aliases[alias]
    if isinstance(got, list):
        if i is None:
            raise Refused("BAD_ARGS", "%s is a group of %d: name one member, %s[0]" % (alias, len(got), alias))
        return ("thing:" + got[i]) if i < len(got) and got[i] else None
    if i is not None:
        raise Refused("BAD_ARGS", "%s is one thing, not a group: drop [%d]" % (alias, i))
    return ("thing:" + got) if got else None


def _paused(s, what):
    st = s._status()
    if st.get("paused") is not True:
        raise Refused("GAME_RUNNING", "the game is not paused: %s needs a paused game (s.run ends paused; read s.state)" % what)
    return st


# ================================================================================================ s.read
def _read_args(s, target, path):
    _check_alias_target(s, target)
    if not isinstance(path, str) or not path:
        raise Refused("BAD_PATH", "path is field steps joined by points, not %r (`help read`)" % (path,))
    if "(" in path:
        raise Refused("PATH_CALLS_METHOD", "%s calls a method; a read calls none. Ask for the reader in code review; meanwhile use "
                      "s.raw (the run is then EXPLORED)" % path)
    why = cond.bad_path("thing:x", path)
    if why:
        raise Refused("BAD_PATH", "%s (`help read`)" % why)


def _values(s, rec, pairs, rect=None, path=None):
    """One call of jawa/read_paths. -> [Value]. An alias that holds nothing reads unbound, with no bridge call for it."""
    if s.closed:
        raise Refused("SESSION_CLOSED", "this session has ended; open a session")
    asked, out = [], []
    for target, p in pairs:
        of = _thing_of(s, target)
        asked.append((target, of, p))
    args = {}
    if rect is not None:
        args = {"rect": "%d,%d,%d,%d" % tuple(rect), "path": path}
    wire = [{"of": of, "path": p} for _t, of, p in asked if of is not None]
    if wire:
        args["reads"] = json.dumps(wire, sort_keys=True)
    reply = {"values": [], "tick": s._tick, "paused": True}
    if args:
        try:
            reply = s._call(READ_PATHS, **args)
        except (CallFailed, ReplyLost) as e:
            raise Fault("COULD_NOT_LOOK", detail="%s: %s" % (READ_PATHS, e))
        if reply.get("success") is False:
            name = reply.get("refused") or "COULD_NOT_LOOK"
            if name in ("BAD_PATH", "PATH_CALLS_METHOD", "BAD_ARGS"):
                raise Refused(name, "%s (`help read`)" % (reply.get("message") or reply))
            raise Fault("COULD_NOT_LOOK", detail="%s: %s" % (READ_PATHS, reply.get("message") or reply))
    got = list(reply.get("values") or [])
    tick = reply.get("tick")
    if rect is None:
        for target, of, p in asked:
            name = "%s.%s" % (target, p)
            if of is None:
                out.append(Value(name, "unbound", None, tick, "the alias holds nothing at this place"))
                continue
            v = got.pop(0) if got else None
            if not isinstance(v, dict) or v.get("of") != of or v.get("path") != p:
                raise Fault("COULD_NOT_LOOK", detail="%s answered %r for %s.%s" % (READ_PATHS, v, of, p))
            out.append(Value(name, v.get("state"), v.get("v"), tick, v.get("detail")))
    else:
        for v in got:
            out.append(Value("%s.%s" % (v.get("of"), v.get("path")), v.get("state"), v.get("v"), tick, v.get("detail")))
            out[-1].of = v.get("of")
    for v in out:
        if v.state != "ok":
            rec.could_not_look.append("%s is %s (%s)" % (v.name, v.state, v.detail or "no detail"))
    if reply.get("paused") is False:
        rec.could_not_look.append("the game was running: the values belong to tick %s, and the game has moved on" % tick)
    return out


def read(s, target, path):
    """Read one value now, a hidden one included (scene_contracts/read.md). It changes nothing."""
    if s.closed:
        raise Refused("SESSION_CLOSED", "this session has ended; open a session")
    _read_args(s, target, path)
    rec = s._begin("s.read")
    v, = _values(s, rec, [(target, path)])
    v.receipt = s._finish(rec)
    return v


def read_many(s, reads=None, rect=None, path=None):
    """Many values on one tick, in one call: a list of (target, path), or one path for every thing in a rectangle."""
    if s.closed:
        raise Refused("SESSION_CLOSED", "this session has ended; open a session")
    if (reads is None) == (rect is None):
        raise Refused("BAD_ARGS", "give reads=[(target, path), ...], or rect=(x, z, w, h) with path=")
    if rect is not None:
        if not (isinstance(rect, (list, tuple)) and len(rect) == 4 and all(isinstance(n, int) for n in rect)):
            raise Refused("BAD_ARGS", "rect is (x, z, w, h) in map cells, not %r" % (rect,))
        _read_args(s, "map", path)
    else:
        for t, p in reads:
            _read_args(s, t, p)
    rec = s._begin("s.read_many")
    out = _values(s, rec, [] if reads is None else list(reads), rect, path)
    s._finish(rec)
    out = Values(out)
    out.receipt = rec
    return out


class Values(list):
    receipt = None


# ================================================================================================ s.stage
class Made(object):
    """One object that the game made (or did not make) for an alias."""

    def __init__(self, alias, id, kind, cell, state="ok", detail=None):
        self.alias, self.id, self.kind, self.cell, self.state, self.detail = alias, id, kind, cell, state, detail

    def __repr__(self):
        return "%s=%s %s at %s" % (self.alias, self.id, self.kind, self.cell) if self.state == "ok" else "%s is %s (%s)" % (
            self.alias, self.state, self.detail)


class Cast(dict):
    """alias -> Made, or a list of Made for a group."""
    receipt = None

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


def _cells(at):
    if isinstance(at, tuple) and len(at) == 2 and all(isinstance(n, int) for n in at):
        return [at], False
    if isinstance(at, list) and at and all(isinstance(c, tuple) and len(c) == 2 for c in at):
        return list(at), True
    raise Refused("BAD_ARGS", "at is a cell (x, z) or a list of cells for a group, not %r" % (at,))


def _plan_stage(s, cast, things, terrain, station):
    """-> the staging plan, checked whole before any bridge call."""
    if station is not None and not (isinstance(station, tuple) and len(station) == 4 and all(isinstance(n, int) for n in station)):
        raise Refused("BAD_ARGS", "station is (x, z, w, h) in map cells, or a request to the stage's allocator, "
                      "dict(size=(w, h), margin=, edge=, incident=, home=, weather=); with no station, positions are map cells")
    ox, oz = (station[0], station[1]) if station else (0, 0)
    plan, seen = [], set()

    def place(c):
        x, z = c[0] + ox, c[1] + oz
        if station and not (0 <= c[0] < station[2] and 0 <= c[1] < station[3]):
            raise Refused("OUTSIDE_STATION", "%s is outside the station of %dx%d: move it inside, or ask for a larger station" % (
                c, station[2], station[3]))
        return x, z

    for group, specs, need in (("cast", cast, "kind"), ("things", things, "thing"), ("terrain", terrain, "terrain")):
        if specs is None:
            continue
        if not isinstance(specs, dict):
            raise Refused("BAD_ARGS", "%s is a dict of alias -> dict(...)" % group)
        for alias, d in specs.items():
            if not isinstance(alias, str) or not ALIAS.match(alias):
                raise Refused("BAD_ARGS", "alias %r is not letters, digits and _" % (alias,))
            if alias in s._aliases or alias in seen:
                raise Refused("ALIAS_TAKEN", "%s is already bound in this session: choose another alias" % alias)
            seen.add(alias)
            if not isinstance(d, dict):
                raise Refused("BAD_ARGS", "%s.%s is dict(...) (`help stage`)" % (group, alias))
            if group == "cast" and "take" in d:
                ids = d["take"]
                many = isinstance(ids, list)
                ids = ids if many else [ids]
                if not ids or not all(isinstance(i, str) and i for i in ids) or set(d) - {"take"}:
                    raise Refused("BAD_ARGS", "cast.%s take= is a thing id or a list of ids that the map already holds, alone" % alias)
                plan.append(("take", alias, many, ids, d))
                continue
            if not isinstance(d.get(need), str) or not d[need]:
                raise Refused("BAD_ARGS", "%s.%s needs %s= (a defName)" % (group, alias, need))
            if group == "terrain":
                r = d.get("rect")
                if not (isinstance(r, tuple) and len(r) == 4 and all(isinstance(n, int) for n in r)):
                    raise Refused("BAD_ARGS", "terrain.%s rect is (x, z, w, h)" % alias)
                corners = [place((r[0], r[1])), place((r[0] + r[2] - 1, r[1] + r[3] - 1))]
                plan.append(("terrain", alias, False, [(corners[0][0], corners[0][1], r[2], r[3])], d))
                continue
            cells, many = _cells(d.get("at"))
            odd = set(d) - ({"kind", "at", "faction", "can"} if group == "cast" else {"thing", "at", "stuff", "rot"})
            if odd:
                raise Refused("BAD_ARGS", "%s.%s takes no %s (`help stage`)" % (group, alias, ", ".join(sorted(odd))))
            plan.append(("pawn" if group == "cast" else "thing", alias, many, [place(c) for c in cells], d))
    if not plan:
        raise Refused("BAD_ARGS", "nothing to stage: give cast=, things= or terrain=")
    return plan


def _block(s, tool, reply, rec, done):
    """-> the readBack block of a staging reply; a missing block is COULD_NOT_LOOK."""
    b = reply.get("readBack") if isinstance(reply, dict) else None
    if not isinstance(b, dict) or "made" not in b:
        raise Fault("COULD_NOT_LOOK", done=done, detail="%s gave no readBack block (the companion is older than "
                    "RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO): what it made is not known" % tool)
    if b.get("sameFrame") is not True:
        rec.could_not_look.append("%s: a frame ran between the write and the read-back (frames %s, %s)" % (tool, b.get("frameOpen"), b.get("frameReply")))
    return b


def stage(s, cast=None, things=None, terrain=None, station=None):
    """Put the cast, things and terrain on the map, and say what the game really made (scene_contracts/stage.md)."""
    if s.closed:
        raise Refused("SESSION_CLOSED", "this session has ended; open a session")
    request = station if isinstance(station, dict) else None
    if request is not None:
        size = request.get("size")
        if not (isinstance(size, tuple) and len(size) == 2 and all(isinstance(n, int) for n in size)):
            raise Refused("BAD_ARGS", "a station request names its size=(w, h)")
        _plan_stage(s, cast, things, terrain, (0, 0) + size)     # the whole plan is checked before a station is taken
        stage = _stage_of(s)
    plan = _plan_stage(s, cast, things, terrain, station) if request is None else None
    rec = s._begin("s.stage")
    _paused(s, "staging")
    did, bad, out = [], [], Cast()
    if request is not None:
        station = _take_station(s, stage, request, rec, did)
        plan = _plan_stage(s, cast, things, terrain, station)
    elif station:
        r = s._call(CLEAN, rects="%d,%d,%d,%d" % station, categories="All")
        b = _block(s, CLEAN, r, rec, did)
        did.append("cleaned the station %s" % (station,))
        if b.get("leftBlocking"):
            raise Fault("NO_CLEAN_STATION", done=did, detail="the clean left %s" % b.get("left"))
    for what, alias, many, cells, d in sorted(plan, key=lambda p: ("terrain", "thing", "pawn", "take").index(p[0])):
        made = []
        if what == "terrain":
            x, z, w, h = cells[0]
            r = s._call(TERRAIN, ops="%s:%d,%d,%d,%d" % (d["terrain"], x, z, w, h))
            b = _block(s, TERRAIN, r, rec, did)
            wrong = [row for row in b.get("wrong") or []]
            did.append("terrain %s: %s over %dx%d at %d,%d" % (alias, d["terrain"], w, h, x, z))
            if wrong or b.get("ok") is False:
                bad.append("%s: %d cells kept another terrain (%s)" % (alias, b.get("rowsWrong") or len(wrong), wrong[:2]))
            out[alias] = Made(alias, None, d["terrain"], (x, z))
            continue
        if what == "take":
            r = s._call(READ_PATHS, reads=json.dumps([{"of": "thing:" + i, "path": "def.defName"} for i in cells] +
                                                     [{"of": "thing:" + i, "path": "positionInt"} for i in cells], sort_keys=True))
            if r.get("success") is False:
                raise Fault("COULD_NOT_LOOK", done=did, detail="%s: %s" % (READ_PATHS, r.get("message") or r))
            vs = r.get("values") or []
            n = len(cells)
            for i, tid in enumerate(cells):
                dv, pv = (vs[i] if i < len(vs) else {}), (vs[n + i] if n + i < len(vs) else {})
                if dv.get("state") != "ok" or pv.get("state") != "ok":
                    made.append(Made(alias, None, None, None, dv.get("state") or "error", "%s: %s" % (tid, dv.get("detail") or pv.get("detail"))))
                    bad.append("%s: %s is %s" % (alias, tid, dv.get("state") or "unread"))
                else:
                    made.append(Made(alias, tid, dv.get("v"), _cell(pv.get("v"))))
            did.append("bound %s to %d thing(s) the map held" % (alias, len(made)))
        elif what == "thing":
            rows, wrong = {}, {}
            for at in range(0, len(cells), ROWS_LISTED):    # a readBack block lists at most 50 rows (StageReadBack.ListedWrong)
                part = cells[at:at + ROWS_LISTED]
                ops = ";".join("%s:%d,%d%s" % (d["thing"], x, z, ",%d" % d["rot"] if d.get("rot") is not None else "") for x, z in part)
                args = {"ops": ops, "faction": "player", "wipeExisting": False}
                if d.get("stuff"):
                    args["stuff"] = d["stuff"]
                r = s._call(BUILD, **args)
                b = _block(s, BUILD, r, rec, did)
                rows.update({(row.get("x"), row.get("z")): row for row in b.get("made") or []})
                wrong.update({(row.get("x"), row.get("z")): row for row in b.get("wrong") or []})
            for x, z in cells:
                row = rows.get((x, z))
                got = (row or {}).get("got") or {}
                if not row or not row.get("id"):
                    made.append(Made(alias, None, None, (x, z), "error", "not made"))
                    bad.append("%s at %d,%d: not made" % (alias, x, z))
                    continue
                made.append(Made(alias, row["id"], got.get("def"), _cell(got.get("cell"))))
                if (x, z) in wrong:
                    bad.append("%s at %d,%d: made as %s" % (alias, x, z, wrong[(x, z)].get("wrong")))
            did.append("built %s: %d %s" % (alias, len([m for m in made if m.id]), d["thing"]))
        else:
            for x, z in cells:
                r = s._call(SPAWN, kindDef=d["kind"], x=x, z=z, faction=d.get("faction", "player"), count=1)
                b = _block(s, SPAWN, r, rec, did)
                row = next(iter(b.get("made") or []), None)
                got = (row or {}).get("got") or {}
                if not row or not row.get("id") or got.get("spawned") != "True":
                    made.append(Made(alias, None, None, (x, z), "error", "not made: %s" % got))
                    bad.append("%s at %d,%d: not made" % (alias, x, z))
                    continue
                made.append(Made(alias, row["id"], got.get("kind"), _cell(got.get("cell"))))
                if got.get("kind") != d["kind"]:
                    bad.append("%s was made as %s %s, not %s" % (alias, row["id"], got.get("kind"), d["kind"]))
                for w in (b.get("wrong") or []):
                    for k in w.get("wrong") or []:
                        if k.get("key") != "kind":
                            bad.append("%s %s: %s is %s, not %s" % (alias, row["id"], k.get("key"), k.get("got"), k.get("want")))
            did.append("spawned %s: %d %s" % (alias, len([m for m in made if m.id]), d["kind"]))
            if d.get("can"):
                rec.could_not_look.append("can=%s of %s was not checked: the cast asserts are %s" % (d["can"], alias, OWED_ORDER))
        out[alias] = made if many else made[0]
        s._aliases[alias] = [m.id for m in made] if many else made[0].id
    _bind(s, rec, [a for _w, a, _m, _c, _d in plan if _w != "terrain"])
    if request is not None:
        did += stage_breaches(s)
    if bad:
        raise Fault("STAGING_FAULT", done=did + ["made: %s" % out], detail="; ".join(bad))
    out.receipt = s._finish(rec, did=did)
    return out


# ------------------------------------------------------------------ the stations of a stage map (scene_stations.py)
def _stage_of(s):
    """-> the allocator of the stage map that this game holds now. A map that is not a made stage is refused NO_STAGE."""
    import scene_stations as ST
    text = s.W.stage_state(s.key)
    if not text:
        raise Refused("NO_STAGE", "the map on %s is not a made stage, so no allocator gives stations on it: load a stage save "
                      "(needs={'map': 'RM_Stage_<list>'}; make one with `%s`), or give station as a rect (x, z, w, h)" % (s.game, STAGE_MAKE))
    try:
        stage = ST.Stage.from_json(text)
    except (ST.Refused, ValueError, KeyError) as e:
        raise Fault("COULD_NOT_LOOK", detail="the stage file of %s could not be read: %s" % (s.game, e))
    size = s._map_size()
    if tuple(size) != stage.size:
        raise Refused("STAGE_STALE", "the stage file of %s is for a %dx%d map and the map is %dx%d: load the stage save again" % (
            s.game, stage.size[0], stage.size[1], size[0], size[1]))
    return stage


def _clean_station(s, rect, rec, did):
    """Vanish every pawn on the station (jawa/destroy_batch keeps pawns), then destroy every thing. -> the clean's readBack block."""
    rs = "%d,%d,%d,%d" % tuple(rect)
    r = s._call(LIST_PAWNS, rect=rs)
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        raise Fault("COULD_NOT_LOOK", done=did, detail="the pawns on station %s could not be read: %s" % (rs, str(r)[:200]))
    for p in r["pawns"]:
        v = s._call(VANISH, pawn=p.get("id"), action="vanish")
        if v.get("success") is False:
            raise Fault("NO_CLEAN_STATION", done=did, detail="pawn %s on station %s did not vanish: %s" % (p.get("id"), rs, v.get("message") or v))
    if r["pawns"]:
        did.append("vanished %d pawn(s) on station %s" % (len(r["pawns"]), rs))
    return _block(s, CLEAN, s._call(CLEAN, rects=rs, categories="All"), rec, did)


def stage_breaches(s):
    """-> one line for each pawn on the stage map that is not cast in this session (a stage holds cast and nothing else)."""
    cast = set()
    for v in s._aliases.values():
        cast.update(v if isinstance(v, list) else [v])
    r = s._call(LIST_PAWNS)
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        raise Fault("COULD_NOT_LOOK", detail="the pawns of the stage could not be read: %s" % str(r)[:200])
    return ["BREACH: %s %s (%s) at %s is on the stage and is not cast" % (p.get("id"), p.get("kind") or p.get("def"), p.get("faction"),
                                                                         p.get("position") or p.get("cell") or p.get("pos")
                                                                         or ("%s,%s" % (p.get("x"), p.get("z")) if "x" in p else "an unread cell"))
            for p in r["pawns"] if p.get("id") not in cast and str(p.get("id")).replace("Thing_", "") not in cast]


def _take_station(s, stage, request, rec, did):
    """Give a station, clean it, and retire it and give another when the clean leaves a thing that blocks. -> its rect."""
    import scene_stations as ST
    while True:
        try:
            got = stage.give(**dict(request, scene=s.id))
        except ST.Refused as e:
            s.W.stage_save(s.key, stage.to_json())
            raise Refused(e.name, e.why)
        s.W.stage_save(s.key, stage.to_json())
        b = _clean_station(s, got["rect"], rec, did)
        if b.get("leftBlocking"):
            stage.retire(got["id"], "the clean left %s" % (b.get("left"),))
            s.W.stage_save(s.key, stage.to_json())
            did.append("retired station %s %s: the clean left %s" % (got["id"], got["rect"], b.get("left")))
            continue
        s._stations.append(got["id"])
        did.append("took station %s %s on the %s stage %s, cleaned" % (got["id"], got["rect"], got["kind"], got["stage"]))
        if got["shared_map"]:
            rec.could_not_look.append("shared map: station %s is on a colony map; its bystanders are held per pawn, not removed" % got["id"])
        return got["rect"]


def put_back_stations(s):
    """At close: clean each station this session took, release it, or retire it when the clean left a thing. -> one line."""
    import scene_stations as ST
    if not s._stations:
        return "no station was taken"
    text = s.W.stage_state(s.key)
    if not text:
        raise Fault("COULD_NOT_LOOK", detail="the stage file of %s is gone: stations %s were not cleaned" % (s.game, s._stations))
    stage = ST.Stage.from_json(text)
    lines = []
    for sid in list(s._stations):
        st = next(x for x in stage.stations if x["id"] == sid)
        try:
            b = _clean_station(s, st["rect"], Receipt("close", {}), [])
        except Fault as e:
            stage.retire(sid, "the clean at close: %s" % (e.detail or e.name))
            lines.append("retired %s: its clean failed: %s" % (sid, e.detail or e.name))
            s._stations.remove(sid)
            continue
        if b.get("leftBlocking"):
            stage.retire(sid, "the clean at close left %s" % (b.get("left"),))
            lines.append("retired %s: the clean left %s" % (sid, b.get("left")))
        else:
            stage.release(sid)
            lines.append("cleaned and released %s" % sid)
        s._stations.remove(sid)
    s.W.stage_save(s.key, stage.to_json())
    try:
        lines += stage_breaches(s)
    except Fault as e:
        lines.append("the breach census could not look: %s" % e.detail)
    return "; ".join(lines)


def _cell(v):
    if isinstance(v, str) and "," in v:
        parts = v.split(",")                    # "x,z", or "x,y,z" for an IntVec3 read whole
        a, b = (parts[0], parts[2]) if len(parts) == 3 else parts[:2]
        return int(float(a)), int(float(b))
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        return int(v[0]), int(v[1])
    return None


def _bind(s, rec, aliases):
    """Bind the aliases in the game's session, so that a track names them; with no session hand they stay in Python."""
    if not aliases:
        return
    if not s._insession:
        rec.could_not_look.append("the aliases %s are bound in Python only (the game has no %s): a track names the thing id" % (
            ", ".join(aliases), SESSION))
        return
    r = s._call(SESSION, action="bind", driver=s.id, bindings=json.dumps({a: s._aliases[a] for a in aliases}, sort_keys=True))
    if r.get("success") is not True:
        raise Fault(r.get("refused") or "NOT_BOUND", done=["staged %s" % ", ".join(aliases)], detail=str(r.get("message") or r))
    if s.hand is not None:
        s.hand.aliases.update(aliases)


# ================================================================================================ s.act
class Effect(object):
    """What one act did (scene_contracts/act.md). Accepted is not completed."""

    def __init__(self, verb, name, accepted, observed, tick, frame, replayed, request):
        self.verb, self.name, self.accepted, self.observed = verb, name, accepted, observed
        self.tick, self.frame, self.replayed, self.request, self.receipt = tick, frame, replayed, request, None

    def __repr__(self):
        return "%s %s: %s on tick %s%s" % (self.verb, self.name or "", "accepted" if self.accepted else "NOT accepted", self.tick,
                                           " (replayed)" if self.replayed else "")


VERBS = {
    "damage": "damage(target, amount, kind='Blunt', name=None): hurt a thing; observed: its hitPointsInt before and after (jawa/damage)",
    "job": "job(pawn, job, target=None, cell=None, name=None): force a job on a pawn through the player-order path (jawa/ordered_job)",
    "place": "place(thing, at, stuff=None, rot=None, bind=None, name=None): make one thing after staging (jawa/build_batch)",
    "order": "not built: the order through the game's own giver is %s" % OWED_ORDER,
    "explode": "not built: no converted scene needed it; jawa/explosion_at through s.raw meanwhile",
    "incident": "not built: no converted scene needed it", "weather": "not built: no converted scene needed it",
    "remove": "not built: no converted scene needed it", "reload": "not built: %s" % OWED_RELOAD,
    "tune": "not built: the live write and its TUNED stamp are %s" % OWED_TUNE,
}


class Act(object):
    """s.act.<verb>(...): one act on the paused game. `with s.act.batch() as b:` sends several in one hop."""

    def __init__(self, s, batch=None):
        self._s, self._batch = s, batch

    def __getattr__(self, verb):
        if verb in VERBS and VERBS[verb].startswith("not built"):
            from scene_core import NotBuilt
            raise NotBuilt("NOT_BUILT", "s.act.%s is %s. Until then `s.raw` reaches each tool, and the run is EXPLORED" % (verb, VERBS[verb]))
        raise AttributeError("s.act has no verb %r; `help verbs`: %s" % (verb, ", ".join(sorted(VERBS))))

    def batch(self):
        return _Batch(self._s)

    def damage(self, target, amount, kind="Blunt", name=None):
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount <= 0:
            raise Refused("BAD_ARGS", "amount is a positive number, not %r" % (amount,))
        thing = self._thing(target)
        return self._do("damage", name, "jawa/damage", {"thingId": thing[6:], "damageDef": kind, "amount": float(amount)},
                        target, before=(target, "hitPointsInt"))

    def job(self, pawn, job, target=None, cell=None, name=None):
        if not isinstance(job, str) or not job:
            raise Refused("BAD_ARGS", "job is a JobDef defName, not %r" % (job,))
        args = {"pawnId": self._thing(pawn)[6:], "jobDef": job}
        if target is not None:
            args["targetAId"] = self._thing(target)[6:]
        if cell is not None:
            if not (isinstance(cell, tuple) and len(cell) == 2):
                raise Refused("BAD_ARGS", "cell is (x, z), not %r" % (cell,))
            args["targetBX"], args["targetBZ"] = cell
        return self._do("job", name, "jawa/ordered_job", args, pawn)

    def place(self, thing, at, stuff=None, rot=None, bind=None, name=None):
        if not isinstance(thing, str) or not (isinstance(at, tuple) and len(at) == 2):
            raise Refused("BAD_ARGS", "place(thing='<defName>', at=(x, z))")
        if bind is not None and (not ALIAS.match(bind) or bind in self._s._aliases):
            raise Refused("ALIAS_TAKEN" if bind in self._s._aliases else "BAD_ARGS", "bind=%r: a new alias of letters, digits and _" % (bind,))
        args = {"ops": "%s:%d,%d%s" % (thing, at[0], at[1], ",%d" % rot if rot is not None else ""), "faction": "player", "wipeExisting": False}
        if stuff:
            args["stuff"] = stuff
        return self._do("place", name, BUILD, args, None, bind=bind)

    # ---- the one way an act is sent
    def _thing(self, of):
        t = _thing_of(self._s, of)
        if t is None or not t.startswith("thing:"):
            raise Refused("UNKNOWN_ALIAS", "%s names no thing of this session: stage it or place it first" % of)
        return t

    def _do(self, verb, name, tool, args, subject, before=None, bind=None):
        s = self._s
        if s.closed:
            raise Refused("SESSION_CLOSED", "this session has ended; open a session")
        s._require_own_driver("an act")
        act = {"verb": verb, "name": name, "tool": tool, "args": args, "subject": subject, "before": before, "bind": bind,
               "id": "act_" + uuid.uuid4().hex[:12]}
        if self._batch is not None:
            self._batch.acts.append(act)
            return act
        return _send(s, [act])[0]


class _Batch(object):
    """Several acts in one call of jawa/act_batch, with no frame between them."""

    def __init__(self, s):
        self.s, self.acts, self.effects = s, [], None
        self.act = Act(s, self)

    def __getattr__(self, verb):
        return getattr(self.act, verb)

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is None and self.acts:
            self.effects = _send(self.s, self.acts)
        return False


def _send(s, acts):
    rec = s._begin("s.act")
    _paused(s, "an act")
    befores = [a for a in acts if a["before"]]
    pre = _values(s, rec, [a["before"] for a in befores]) if befores else []
    if ACT_BATCH in s._tools and s._insession:
        wire = [{"id": a["id"], "tool": a["tool"], "args": a["args"]} for a in acts]
        try:
            r = s._call(ACT_BATCH, driver=s.id, acts=json.dumps(wire, sort_keys=True))
        except ReplyLost as e:
            r = s._call(ACT_BATCH, driver=s.id, acts=json.dumps(wire, sort_keys=True))     # the same ids: the game does it once
            rec.could_not_look.append("the first reply was lost (%s); the repeat of the same ids returned the first effect" % e)
        except CallFailed as e:
            raise Fault("ACT_NOT_DONE", detail="%s: %s" % (ACT_BATCH, e))
        if r.get("success") is False:
            name = r.get("refused") or "ACT_NOT_DONE"
            if name in ("GAME_RUNNING", "REQUEST_CONFLICT", "BAD_ARGS", "UNKNOWN_TOOL", "NOT_ONE_HOP"):
                raise Refused(name, "%s (`help act`)" % (r.get("message") or r))
            raise Fault(name, detail=str(r.get("message") or r))
        rows = r.get("acts") or []
    else:
        rec.could_not_look.append("the game has no %s in a session: each act was sent alone, with no request id" % ACT_BATCH)
        rows = []
        for a in acts:
            try:
                rep = s._call(a["tool"], **a["args"])
                rows.append({"id": a["id"], "state": "done" if rep.get("success") is not False else "refused", "reply": rep,
                             "tick": s._tick, "frame": None, "replayed": False})
            except (CallFailed, ReplyLost) as e:
                rows.append({"id": a["id"], "state": "failed", "error": str(e), "tick": s._tick, "frame": None})
    by = {row.get("id"): row for row in rows}
    effects, did = [], []
    for a in acts:
        row = by.get(a["id"], {"state": "not_tried"})
        reply = row.get("reply") if isinstance(row.get("reply"), dict) else {}
        accepted = row.get("state") == "done" and reply.get("success") is not False and reply.get("accepted") is not False
        observed = {"state": row.get("state"), "reply": reply}
        if a["bind"] and accepted:
            m = next(iter(((reply.get("readBack") or {}).get("made") or [])), {})
            s._aliases[a["bind"]] = m.get("id")
            observed["bound"] = m.get("id")
            _bind(s, rec, [a["bind"]])
        effects.append(Effect(a["verb"], a["name"], accepted, observed, row.get("tick"), row.get("frame"), bool(row.get("replayed")), a["id"]))
        did.append("%s %s%s: %s" % (a["verb"], a["subject"] or a["args"].get("ops", ""), " (%s)" % a["name"] if a["name"] else "", row.get("state")))
        if row.get("state") not in ("done",):
            rec.could_not_look.append("act %s was %s: %s" % (a["id"], row.get("state"), row.get("error") or reply.get("message") or ""))
    post = _values(s, rec, [a["before"] for a in befores]) if befores else []
    for a, b4, af in zip(befores, pre, post):
        e = effects[acts.index(a)]
        e.observed.update(before=b4, after=af)
    s._status()
    r = s._finish(rec, did=did)
    for e in effects:
        e.receipt = r
    return effects


# ================================================================================================ s.shot
def shot(s, rect, name, zoom=64):
    """Take one picture of a rectangle of the map that is known to be fresh (scene_contracts/shot.md)."""
    if s.closed:
        raise Refused("SESSION_CLOSED", "this session has ended; open a session")
    if not isinstance(name, str) or not ALIAS.match(name.replace("-", "_")):
        raise Refused("BAD_ARGS", "name is letters, digits, _ and -, unique in the run, not %r" % (name,))
    if name in s._shots:
        raise Refused("NAME_TAKEN", "%s was used in this run: choose another name" % name)
    if not isinstance(zoom, int) or not 8 <= zoom <= 256:
        raise Refused("BAD_ARGS", "zoom is pixels per cell, 8 to 256, not %r" % (zoom,))
    if isinstance(rect, tuple) and len(rect) == 2 and isinstance(rect[0], str):
        alias, margin = rect
        _check_alias_target(s, alias)
    elif not (isinstance(rect, tuple) and len(rect) == 4 and all(isinstance(n, int) for n in rect)):
        raise Refused("BAD_ARGS", "rect is (x, z, w, h), or (alias, margin), not %r" % (rect,))
    rec = s._begin("s.shot")
    _paused(s, "a picture")
    if isinstance(rect[0], str):
        ids = s._aliases[rect[0]]
        cells = [v.v for v in _values(s, rec, [("%s[%d]" % (rect[0], i) if isinstance(ids, list) else rect[0], "positionInt")
                                                for i in range(len(ids) if isinstance(ids, list) else 1)]) if v.state == "ok"]
        cells = [_cell(c) for c in cells]
        if not cells:
            raise Fault("COULD_NOT_LOOK", detail="no member of %s could be placed on the map" % rect[0])
        xs, zs = [c[0] for c in cells], [c[1] for c in cells]
        m = rect[1]
        rect = (min(xs) - m, min(zs) - m, max(xs) - min(xs) + 1 + 2 * m, max(zs) - min(zs) + 1 + 2 * m)
    try:
        size = s._map_size()
    except Fault as e:
        size = None
        rec.could_not_look.append("the rectangle was not checked against the map: %s" % e.detail)
    if size and (rect[0] >= size[0] or rect[1] >= size[1] or rect[0] + rect[2] <= 0 or rect[1] + rect[3] <= 0):
        raise Refused("RECT_OFF_MAP", "%s lies wholly outside the map of %dx%d: give cells of this map" % (rect, size[0], size[1]))
    if size:
        x0, z0 = max(0, rect[0]), max(0, rect[1])
        x1, z1 = min(size[0], rect[0] + rect[2]), min(size[1], rect[1] + rect[3])
        if (x0, z0, x1 - x0, z1 - z0) != tuple(rect):
            rec.could_not_look.append("the rectangle %s is partly off the map: cut to %s" % (rect, (x0, z0, x1 - x0, z1 - z0)))
        rect = (x0, z0, x1 - x0, z1 - z0)
    path = s.W.picture_path(s.run_dir, name)
    before = s.W.file_stamp(path)
    tick = s._tick
    try:
        r = s._call(CAPTURE, x=rect[0], z=rect[1], w=rect[2], h=rect[3], ppc=zoom, path=path, frames=4)
    except (CallFailed, ReplyLost) as e:
        raise Fault("SHOT_NOT_FRESH", detail="%s: %s" % (CAPTURE, e))
    after = s.W.file_stamp(path)
    fresh = r.get("success") is True and after is not None and after != before and (r.get("fileSizeBytes") or 0) > 0
    if not fresh:
        raise Fault("SHOT_NOT_FRESH", done=["asked %s for %s" % (CAPTURE, path)], detail="the capture wrote no new file (before %s, after %s): %s" % (
            before, after, r.get("message") or r.get("error") or "no message"))
    if r.get("foggedCells"):
        rec.could_not_look.append("%s cells of the rectangle are fogged" % r["foggedCells"])
    if r.get("cameraRestored") is False:
        rec.could_not_look.append("the capture says the camera was not put back")
    s._shots.add(name)
    st = s._status()
    out = Shot(path, st.get("tick", tick), (r.get("frame") or [None, None]), True)
    s.W.save(path + ".json", json.dumps({"name": name, "rect": list(rect), "tick": out.tick, "stamps": sorted(s.stamps), "session": s.id},
                                        sort_keys=True))
    out.receipt = s._finish(rec, did=["wrote %s" % path])
    return out


class Shot(object):
    def __init__(self, path, tick, size, fresh):
        self.path, self.tick, self.size, self.fresh, self.receipt = path, tick, size, fresh, None

    def __repr__(self):
        return "shot %s on tick %s" % (self.path, self.tick)
