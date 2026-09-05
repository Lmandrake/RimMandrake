"""rimplace.selftest - prove the engine works, including that its checks FAIL.

🔑 Every negative control here exists because a check that cannot fail is
worthless. This project has a register of instruments caught returning a
confident wrong number (`infrastructure/state/BUILDABLE.md`); the point of
these cases is that this tool never joins it.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .core import Palette, Rect
from .luaenv import (TemplateError, TemplateTooSmall, declared_min_rect,
                     run_template)
from .contract import check_calls, tool_parameters
from .plan import compile_calls, lint, render

_HERE = Path(__file__).resolve().parent
_TEMPLATES = _HERE.parents[3] / "design" / "Jawa" / "templates"


def _pal(faction="Jawa_IndigenousTribes", tech="Industrial", wealth="modest"):
    data = json.loads((_HERE / "palette.json").read_text(encoding="utf-8"))
    return Palette(data, faction, tech, wealth)


def _run(src: str, rect=Rect(0, 0, 16, 10), params=None, seed=1, pal=None):
    with tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False,
                                     encoding="utf-8") as f:
        f.write(src)
        p = f.name
    try:
        return run_template(p, rect, params or {}, pal or _pal(), seed)
    finally:
        Path(p).unlink(missing_ok=True)


CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


# --------------------------------------------------------------------------- #
#  Positive: the engine does what it says
# --------------------------------------------------------------------------- #
@case("a template can place a thing")
def t_place():
    p = _run("function build(ctx) ctx:place('Wall', 1, 1) end")
    assert len(p.things) == 1, p.things
    assert p.things[0].defName == "Wall"


@case("palette roles resolve to defNames")
def t_roles():
    p = _run("function build(ctx) ctx:place_role('WALL', 2, 2) end")
    assert p.things[0].defName == "Wall"
    assert p.things[0].stuff == "BlocksSandstone"


@case("wall_rect walls the perimeter and nothing else")
def t_wallrect():
    p = _run("function build(ctx) ctx:wall_rect(0, 0, 5, 5) end")
    assert len(p.things) == 16, len(p.things)      # 5x5 perimeter
    assert not p.thing_at(2, 2)


@case("a door replaces the wall rather than stacking on it")
def t_door():
    p = _run("function build(ctx) ctx:wall_rect(0,0,5,5) ctx:door(2,0) end")
    at = p.thing_at(2, 0)
    assert len(at) == 1 and at[0].role == "DOOR", at


@case("the same def twice in one cell is idempotent, not a collision")
def t_idem():
    p = _run("function build(ctx) ctx:place('Wall',1,1) ctx:place('Wall',1,1) end")
    assert len(p.things) == 1
    assert not [f for f in lint(p) if f.code == "cell-collision"]


@case("the same seed gives a byte-identical plan")
def t_determinism():
    src = ("function build(ctx) "
           "for i=1,20 do ctx:place('Wall', rng.int(0,10), rng.int(0,8)) end end")
    # Compare the GEOMETRY, not meta: meta legitimately carries the template's
    # name, and these two runs come from two different temp files.
    def geom(pl):
        d = pl.to_dict()
        d.pop("meta")
        return json.dumps(d, sort_keys=True)
    assert geom(_run(src, seed=7)) == geom(_run(src, seed=7)), \
        "same seed produced different geometry"


@case("a different seed gives a different plan")
def t_seed_varies():
    src = ("function build(ctx) "
           "for i=1,20 do ctx:place('Wall', rng.int(0,10), rng.int(0,8)) end end")
    def geom(pl):
        d = pl.to_dict()
        d.pop("meta")
        return json.dumps(d, sort_keys=True)
    assert geom(_run(src, seed=7)) != geom(_run(src, seed=8))


# --------------------------------------------------------------------------- #
#  Negative controls: the checks must actually FIRE
# --------------------------------------------------------------------------- #
@case("NEGATIVE: two different defs in one cell is an ERROR")
def t_collision_fires():
    """Two halves, because the guard MOVED and a test that only knew the old
    half would have read as a regression.

    ctx:place() now refuses the second thing outright (footprint-collision), so
    a plan built through the template API never reaches lint carrying one. The
    lint check still has to work for a plan built any other way - so this
    asserts the refusal AND builds the bad plan directly to prove the linter
    itself still fires."""
    p = _run("function build(ctx) ctx:place('Wall',1,1) ctx:place('Door',1,1) end")
    assert len(p.things) == 1, "the generator let a second def into an occupied cell"
    assert [r for r in p.refusals if r.code == "footprint-collision"], \
        "the generator did not refuse it"

    p.add_thing("Door", 1, 1, 0, None, "DOOR")      # bypass the generator
    assert [f for f in lint(p) if f.code == "cell-collision"], \
        "the linter's own cell-collision check no longer fires"


@case("NEGATIVE: an unsealed room is an ERROR")
def t_unsealed_fires():
    p = _run("function build(ctx) ctx:room('Bedroom',0,0,6,6) end")
    assert [f for f in lint(p) if f.code == "room-not-sealed"], "gap not caught"


@case("NEGATIVE: a room with no door is an ERROR")
def t_nodoor_fires():
    p = _run("function build(ctx) ctx:room('Bedroom',0,0,6,6) "
             "ctx:wall_rect(0,0,6,6) end")
    assert [f for f in lint(p) if f.code == "room-unreachable"], "no-door not caught"


@case("NEGATIVE: placing outside the footprint is refused AND flagged")
def t_outside_refused():
    p = _run("function build(ctx) ctx:place('Wall', 99, 99) end")
    assert not p.things, "placed outside the rect"
    assert p.refusals, "refusal not recorded"


@case("NEGATIVE: an unverified defName is an ERROR when a def set is given")
def t_unverified_fires():
    p = _run("function build(ctx) ctx:place('NotARealDef_XYZ',1,1) end")
    f = lint(p, verified_defs={"Wall"})
    assert [x for x in f if x.code == "def-unverified"], "bad def not caught"


@case("NEGATIVE: a template that builds nothing is an ERROR")
def t_empty_fires():
    p = _run("function build(ctx) end")
    assert [f for f in lint(p) if f.code == "empty-plan"], "empty plan not caught"


@case("NEGATIVE: a vent in a nursery shell is an ERROR")
def t_vent_fires():
    p = _run("function build(ctx) "
             "ctx:room('Nursery',0,0,6,6) ctx:wall_rect(0,0,6,6) "
             "ctx:door(3,0) "
             "ctx.plan:add_thing('Vent',0,3,0,nil,'VENT') end")
    assert [f for f in lint(p) if f.code == "vent-defeats-cooling"], \
        "vent in a cold room not caught"


# --------------------------------------------------------------------------- #
#  Sandbox
# --------------------------------------------------------------------------- #
@case("SANDBOX: io is unreachable")
def t_sandbox_io():
    try:
        _run("function build(ctx) local f = io.open('/tmp/x','w') end")
    except TemplateError:
        return
    raise AssertionError("io was reachable from a template")


@case("SANDBOX: os is unreachable")
def t_sandbox_os():
    try:
        _run("function build(ctx) os.execute('true') end")
    except TemplateError:
        return
    raise AssertionError("os was reachable from a template")


@case("SANDBOX: require is unreachable")
def t_sandbox_require():
    try:
        _run("function build(ctx) require('os') end")
    except TemplateError:
        return
    raise AssertionError("require was reachable from a template")


@case("SANDBOX: a template CANNOT WRITE A FILE (behaviour, not a name list)")
def t_sandbox_cannot_write_a_file():
    """🔴 The test the three above could never have been. They each assert that one
    name we remembered to nil is nil — so they all passed for months while lupa's
    `python` table sat there un-nil'd and a template could call
    `python.builtins.open(...)`. Demonstrated in review 2026-09-02: a template wrote a
    file to disk and returned cleanly.

    ⇒ This one asserts the PROPERTY the docstring actually promises — a template
    cannot touch the machine — by trying to touch it. It keeps working if lupa adds a
    new escape hatch under a name nobody here has heard of, which is the entire point.
    """
    import os as _os, tempfile
    probe = _os.path.join(tempfile.gettempdir(), "rimplace_sandbox_probe.txt")
    if _os.path.exists(probe):
        _os.remove(probe)
    try:
        _run("function build(ctx) python.builtins.open(%r, 'w') end" % probe)
    except TemplateError:
        pass                      # refused, as it must be
    assert not _os.path.exists(probe), (
        "SANDBOX BREACH: a template wrote %s. Something reachable from Lua can touch "
        "the filesystem — find it and nil it in _FORBIDDEN." % probe)


@case("SANDBOX: no route out through the LIVE PYTHON OBJECTS handed to the template")
def t_sandbox_no_attribute_walk():
    """🔴 THE ONE ABOVE WAS ALSO TOO NARROW, AND FOR THE SAME REASON. It probes the
    single route its author had just closed (`python.builtins`), so it passed on
    2026-09-02 while FOUR other routes wrote a file to disk. `ctx`, `role` and
    `rng.int` are live Python objects, and lupa exposes their attributes: nilling
    names in `_G` cannot touch `ctx.__class__.__init__.__globals__`.

    ⇒ Every escape below is a MEASURED one — each wrote a file before
    `luaenv._attribute_filter` existed. Any new object handed into the Lua globals
    must keep them all failing.
    """
    import os as _os, tempfile
    probe = _os.path.join(tempfile.gettempdir(), "rimplace_attrwalk_probe.txt")
    routes = {
        "ctx.__class__": 'local g=c.__class__.__init__.__globals__ '
                         'g["__builtins__"]["open"](%r,"w")',
        "ctx.plan.__class__": 'local g=c.plan.__class__.__init__.__globals__ '
                              'g["__builtins__"]["open"](%r,"w")',
        "role.__self__": 'local g=role.__self__.__class__.__init__.__globals__ '
                         'g["__builtins__"]["open"](%r,"w")',
        "rng.int.__self__ -> the module's own Path":
            'local g=rng.int.__self__.__class__.__init__.__globals__ '
            'g["Path"](%r):write_text("x")',
    }
    for name, body in routes.items():
        if _os.path.exists(probe):
            _os.remove(probe)
        # pcall so a refusal inside Lua does not mask the thing being measured:
        # the assertion is about the FILE, never about the error text.
        src = ("function build(c) pcall(function() " + (body % probe) + " end) end")
        try:
            _run(src)
        except TemplateError:
            pass
        assert not _os.path.exists(probe), (
            "SANDBOX BREACH via %s: a template wrote %s. A live Python object in the "
            "Lua globals is walkable again — check luaenv._attribute_filter is still "
            "passed to every LuaRuntime." % (name, probe))


@case("SANDBOX: a template cannot SET an attribute on an engine object")
def t_sandbox_no_attribute_write():
    """Templates are DATA. One that could assign `ctx.rect` would rewrite the engine's
    own bounds mid-build, and every later refusal would be measured against it."""
    try:
        p = _run("function build(c) c.rect = nil end")
    except TemplateError:
        return                    # refused, as it must be
    raise AssertionError("a template assigned to ctx.rect; the plan built was %r" % p)


@case("min_rect: a floor is rounded UP, never truncated")
def t_min_rect_ceils():
    """A computed 6.5 truncated to 6 declares a floor SMALLER than the real one, so an
    undersized rect clears the gate and build() refuses halfway — exactly what
    TemplateTooSmall exists to prevent."""
    import tempfile, os as _os
    p = _os.path.join(tempfile.gettempdir(), "rimplace_ceil_probe.lua")
    open(p, "w").write("function min_rect(params) return 6.5, 4.2 end\n"
                       "function build(ctx) end\n")
    assert declared_min_rect(p, {}) == (7, 5), declared_min_rect(p, {})


@case("min_rect: a bad return shape is a TemplateError, never a raw traceback")
def t_min_rect_bad_shape():
    """`return '6x4'` used to reach `got['w']` — str has __getitem__ — and raise a bare
    TypeError past every handler, out to the user as a traceback."""
    import tempfile, os as _os
    for body in ("return '6x4'", "return {}", "return true"):
        p = _os.path.join(tempfile.gettempdir(), "rimplace_shape_probe.lua")
        open(p, "w").write("function min_rect(params) %s end\n"
                           "function build(ctx) end\n" % body)
        try:
            declared_min_rect(p, {})
        except TemplateError:
            continue
        except Exception as e:
            raise AssertionError("%r escaped as %s, not TemplateError" % (body, type(e).__name__))


# --------------------------------------------------------------------------- #
#  Compiler
# --------------------------------------------------------------------------- #
@case("the compiler groups by stuff, because stuff is per-CALL")
def t_grouping():
    p = _run("function build(ctx) "
             "ctx:place('Wall',1,1,0,'Steel') ctx:place('Wall',2,1,0,'Steel') "
             "ctx:place('Wall',3,1,0,'WoodLog') end")
    calls = compile_calls(p)
    bb = [c for c in calls if c["tool"] == "jawa/build_batch"]
    assert len(bb) == 2, f"expected 2 stuff groups, got {len(bb)}"
    stuffs = sorted(c["params"]["stuff"] for c in bb)
    assert stuffs == ["Steel", "WoodLog"], stuffs


@case("the compiler always ends with map_commit")
def t_commit():
    p = _run("function build(ctx) ctx:place('Wall',1,1) end")
    assert compile_calls(p)[-1]["tool"] == "jawa/map_commit"


@case("the compiler emits terrain BEFORE things and roof LAST")
def t_order():
    p = _run("function build(ctx) ctx:room('Bedroom',0,0,5,5) "
             "ctx:wall_rect(0,0,5,5) end")
    tools = [c["tool"] for c in compile_calls(p)]
    assert tools.index("jawa/set_terrain_batch") < tools.index("jawa/build_batch")
    assert tools.index("jawa/build_batch") < tools.index("jawa/set_roof_batch")


@case("every compiled call uses parameters the companion actually declares")
def t_contract():
    """TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1. 23/23 selftests passed while the
    compiler emitted a `rect` parameter no tool has, because every test compared
    the compiler against itself. This one compares it against the C#."""
    tpl = _TEMPLATES / "dwelling.lua"
    params = tool_parameters()
    if params is None:
        raise AssertionError(
            "UNMEASURED: the companion source did not parse, so nothing was "
            "contract-checked. Fix the parser rather than skipping the case.")
    plans = [_run("function build(ctx) ctx:room('Bedroom',0,0,6,6) "
                  "ctx:wall_rect(0,0,6,6) ctx:place('Wall',1,1,0,'Steel') end")]
    if tpl.exists():
        plans.append(run_template(tpl, Rect(0, 0, 18, 10),
                                  {"faction": "Jawa_IndigenousTribes",
                                   "rooms": 3, "occupants": 4}, _pal(), 1))
    for pl in plans:
        bad = check_calls(compile_calls(pl, dry_run=False), params)
        assert not bad, "; ".join(bad)


@case("NEGATIVE: an invented parameter IS caught by the contract check")
def t_contract_fires():
    params = tool_parameters()
    assert params is not None, "contract unreadable"
    bad = check_calls([{"tool": "jawa/set_terrain_batch",
                        "params": {"rect": "1,1,2,2", "terrainDef": "Gravel"}}],
                      params)
    assert bad, "a `rect` parameter that no tool has was not caught"
    assert "rect" in bad[0]


@case("terrain and roof compile to the ops grammar the tools parse")
def t_ops_grammar():
    p = _run("function build(ctx) ctx:room('Bedroom',0,0,6,6) "
             "ctx:wall_rect(0,0,6,6) end")
    import re as _re
    for tool in ("jawa/set_terrain_batch", "jawa/set_roof_batch"):
        for c in [c for c in compile_calls(p, dry_run=False) if c["tool"] == tool]:
            assert "ops" in c["params"], f"{tool} emitted {sorted(c['params'])}"
            for op in c["params"]["ops"].split(";"):
                assert _re.match(r"^[A-Za-z_][A-Za-z0-9_]*:-?\d+,-?\d+,\d+,\d+$", op), \
                    f"{tool} op is not 'Def:x,z,w,h': {op!r}"


@case("NEGATIVE: a multi-cell footprint overlapping another thing is an ERROR")
def t_footprint_fires():
    from .defsize import load as _sizes
    if not _sizes():
        raise AssertionError("no def size index; run rimplace.defsize --refresh")
    # Table1x2c is 1x2: placed at (2,2) it also holds (2,3), so a chair there
    # is destroyed by build_batch while BOTH report placed.
    p = _run("function build(ctx) ctx:place('Table1x2c',2,2,0,'WoodLog') "
             "ctx:place('DiningChair',2,3,0,'WoodLog') end")
    f = [x for x in lint(p) if x.code == "footprint-collision"]
    assert f, "a chair inside a 1x2 table was not caught"


@case("an overlay (floor decal) shares a cell with an edifice and lint is silent")
def t_overlay_coexists():
    p = _run("function build(ctx) ctx:place('DiningChair',2,2,0,'WoodLog') "
             "ctx:place_overlay('OuterRim_Decal_HuttClan',2,2,0) end")
    assert len(p.things) == 2, p.things
    assert p.things[1].overlay is True
    assert not p.occupied(3, 3), "an overlay-only cell must not read as occupied"
    bad = [f for f in lint(p) if f.code in ("cell-collision", "footprint-collision")]
    assert not bad, [str(f) for f in bad]


@case("NEGATIVE: a wall lamp with no wall to hang on is refused, not placed")
def t_wall_attach_refuses():
    p = _run("function build(ctx) ctx:wall_attach('WALL_LIGHT', 3, 3, 0) end")
    assert not p.things, "a lamp was placed with no wall in front of it"
    assert [r for r in p.refusals if r.code == "attach-no-wall"], p.refusals


@case("a wall lamp in front of a wall lands as an overlay facing the wall")
def t_wall_attach_places():
    p = _run("function build(ctx) ctx:wall_rect(0,0,6,6) "
             "assert(ctx:wall_attach('WALL_LIGHT', 2, 4, 0)) end")
    lamps = [t for t in p.things if t.role == "WALL_LIGHT"]
    assert len(lamps) == 1 and lamps[0].overlay and lamps[0].rot == 0, lamps
    assert not [f for f in lint(p) if f.level == "ERROR"]


@case("the prelude's helpers exist and scatter() places what it says it placed")
def t_prelude():
    p = _run("function build(ctx) local r = R(0,0,12,8) "
             "local n = scatter(ctx, 'STOOL', r, 6) "
             "assert(n == 6, 'scatter placed ' .. n) "
             "assert(dress(ctx, r, {{role='CRATE', n={1,2}, where='corner'}}) >= 1) end")
    assert p.meta.get("prelude_sha256"), "prelude hash missing from the plan meta"
    assert sum(1 for t in p.things if t.role == "STOOL") == 6


@case("NEGATIVE: shell() with no floor named is a refusal, not bare ground")
def t_shell_needs_floor():
    p = _run("function build(ctx) shell(ctx, 'Room', R(0,0,6,6), {doors={'S'}}) end")
    assert [r for r in p.refusals if r.what == "floor"], p.refusals
    p2 = _run("function build(ctx) shell(ctx, 'Room', R(0,0,6,6), "
              "{floor='PavedTile', doors={'S'}}) end")
    assert not [r for r in p2.refusals if r.what == "floor"]
    assert p2.terrain[(2, 2)] == "PavedTile", p2.terrain.get((2, 2))
    assert not [f for f in lint(p2) if f.level == "ERROR"]


@case("a template can step by a def's real width, and 2-wide shelves do not overlap")
def t_shelf_stride():
    from .defsize import load as _sizes
    sizes = _sizes()
    if not sizes:
        raise AssertionError("no def size index; run rimplace.defsize --refresh")
    assert sizes.get("Shelf") == [2, 1], f"Shelf reads {sizes.get('Shelf')}"
    p = _run("function build(ctx) local w = ctx:width_of('Shelf') "
             "local x = 1 while x <= 6 do ctx:place('Shelf',x,1,0,'WoodLog') "
             "x = x + w end end")
    errs = [x for x in lint(p) if x.level == "ERROR"]
    assert not errs, [str(e) for e in errs]
    assert len(p.things) == 3, f"expected 3 shelves on a 2-cell stride, got {len(p.things)}"


# --------------------------------------------------------------------------- #
#  The shipped template
# --------------------------------------------------------------------------- #
@case("the shipped dwelling lints clean at 1, 2 and 3 rooms")
def t_dwelling():
    tpl = _TEMPLATES / "dwelling.lua"
    if not tpl.exists():
        return
    for n in (1, 2, 3):
        params = {"faction": "Jawa_IndigenousTribes", "rooms": n,
                  "occupants": 2, "wealth": "modest"}
        p = run_template(tpl, Rect(0, 0, 18, 10), params, _pal(), 1)
        errs = [f for f in lint(p) if f.level == "ERROR"]
        assert not errs, f"{n} rooms: {[str(e) for e in errs]}"


@case("the droid palette really produces a dwelling with no beds")
def t_droids_no_beds():
    tpl = _TEMPLATES / "dwelling.lua"
    if not tpl.exists():
        return
    pal = _pal("Jawa_FreeDroidEnclaves", "Spacer")
    params = {"faction": "Jawa_FreeDroidEnclaves", "rooms": 2, "occupants": 3}
    p = run_template(tpl, Rect(0, 0, 18, 10), params, pal, 1)
    beds = [t for t in p.things if (t.role or "") == "BED"]
    assert not beds, f"droids got {len(beds)} bed(s); canon says none"


@case("a footprint too small for the rooms asked is REFUSED, not silently shrunk")
def t_refuses_small():
    """⭐ The guarantee is unchanged; WHERE it is enforced moved earlier. This used to
    assert a `ctx:refuse` recorded mid-build. Since TEMPLATE_CANVAS_UNDECLARED_1 the
    template DECLARES its floor and the engine refuses before build() runs at all —
    strictly better, because the old path had already placed floor and props by the
    time it noticed. Both are refusals; neither silently shrinks."""
    tpl = _TEMPLATES / "dwelling.lua"
    if not tpl.exists():
        return
    params = {"faction": "Jawa_IndigenousTribes", "rooms": 3, "occupants": 2}
    try:
        p = run_template(tpl, Rect(0, 0, 8, 6), params, _pal(), 1)
    except TemplateTooSmall as e:
        assert e.need == (16, 1), e.need      # 5n + 1 at rooms=3
        return
    assert p.refusals, "a 8x6 rect silently accepted 3 rooms"
    assert len(p.rooms) != 3, "it built 3 rooms in a rect that cannot hold them"


@case("a declared min_rect is checked BEFORE build(), and nothing is placed")
def t_min_rect_precedes_build():
    """🔑 TEMPLATE_CANVAS_UNDECLARED_1's whole point: caught upstream of build, not as
    a renamed `ctx:refuse`. The proof is that no plan comes back at all — the old
    behaviour returned a plan with terrain and props already in it."""
    tpl = _TEMPLATES / "junkers_scrapyard.lua"
    if not tpl.exists():
        return
    # The template's OWN declaration is the reference, read the way a caller
    # would, so a redesign of the scrapyard does not silently fail this case.
    need = declared_min_rect(tpl, {})
    assert need and need[0] > 16, need
    try:
        run_template(tpl, Rect(0, 0, 16, 12), {}, _pal(), 1)
    except TemplateTooSmall as e:
        assert e.need == need, (e.need, need)
        assert "16x12" in str(e), str(e)
        return
    raise AssertionError("a 16x12 rect built a template that declares %dx%d" % need)


@case("a size-agnostic template declares nothing, and is not forced to")
def t_no_min_rect_is_legal():
    """⚠️ The regression this mechanism could have been: demanding a floor from every
    template. Four are genuinely size-agnostic (scatter-only or terrain-led)."""
    for name in ("bantha_graveyard", "mynock_roost", "glass_sea", "broken_ring"):
        tpl = _TEMPLATES / f"{name}.lua"
        if not tpl.exists():
            continue
        assert declared_min_rect(tpl, {}) is None, f"{name} grew a floor it never had"
        run_template(tpl, Rect(0, 0, 16, 12), {}, _pal(), 1)   # must not raise


@case("min_rect is answerable WITHOUT running build()")
def t_min_rect_is_queryable():
    """The gap named in the item: a TileMutatorDef author or a re-export script must
    be able to ask how big a canvas a template needs without running it."""
    tpl = _TEMPLATES / "dwelling.lua"
    if not tpl.exists():
        return
    # params-dependent, which is why the convention is a function, not a constant
    assert declared_min_rect(tpl, {"rooms": 1}) == (6, 1)
    assert declared_min_rect(tpl, {"rooms": 2}) == (11, 1)
    assert declared_min_rect(tpl, {"rooms": 3}) == (16, 1)


# --------------------------------------------------------------------------- #
#  RIMPLACE_ENGINE_DELTAS_1 (E1-E6)
# --------------------------------------------------------------------------- #
@case("E1: every plan built via run_template auto-carries a footprint CLEAR")
def t_e1_auto_clear():
    p = _run("function build(ctx) ctx:place('Wall',1,1) end", rect=Rect(0, 0, 6, 6))
    assert len(p.clears) == 2, p.clears
    assert p.clears[0].mode == "soft" and p.clears[1].mode == "all"
    assert not [f for f in lint(p) if f.code == "footprint-not-cleared"]


@case("NEGATIVE: footprint-not-cleared fires on a plan built without run_template")
def t_e1_footprint_not_cleared_fires():
    from .core import BuildPlan
    p = BuildPlan({"footprint": [0, 0, 6, 6]})
    p.add_thing("Wall", 1, 1, 0, None, "WALL")
    assert [f for f in lint(p) if f.code == "footprint-not-cleared"], \
        "a plan with no CLEAR at all was not caught"


@case("E1: ctx:clear records a directive, and rejects a bad mode")
def t_e1_clear_ctx():
    p = _run("function build(ctx) ctx:clear(2,2,3,3,'soft') "
             "ctx:clear(0,0,1,1,'bogus') end")
    soft = [c for c in p.clears if (c.x, c.z, c.w, c.h) == (2, 2, 3, 3)]
    assert soft and soft[0].mode == "soft", p.clears
    assert [r for r in p.refusals if r.code == "clear-bad-mode"], p.refusals


@case("E2: ctx:run resolves a role and records a directive")
def t_e2_run():
    p = _run("function build(ctx) assert(ctx:run(1,1,'e','WALL')) end")
    assert len(p.runs) == 1, p.runs
    assert p.runs[0].dir == "E" and p.runs[0].defName == "Wall", p.runs[0]
    assert "Wall" in p.defnames()


@case("NEGATIVE: ctx:run refuses an unknown direction")
def t_e2_run_bad_dir():
    p = _run("function build(ctx) ctx:run(1,1,'NE','WALL') end")
    assert not p.runs
    assert [r for r in p.refusals if r.code == "run-bad-dir"], p.refusals


@case("E3: ctx:pawn records a directive for a real kindDef/faction/state")
def t_e3_pawn():
    p = _run("function build(ctx) assert(ctx:pawn('Jawa',1,1,'wild','dead')) end")
    assert len(p.pawns) == 1, p.pawns
    pawn = p.pawns[0]
    assert (pawn.kindDef, pawn.faction, pawn.state) == ("Jawa", "wild", "dead"), pawn
    assert "Jawa" in p.defnames()


@case("NEGATIVE: ctx:pawn refuses faction=player outright")
def t_e3_pawn_refuses_player():
    p = _run("function build(ctx) ctx:pawn('Jawa',1,1,'player','alive') end")
    assert not p.pawns, "a PAWN directive was recorded for faction=player"
    assert [r for r in p.refusals if r.code == "pawn-player-faction"], p.refusals


@case("NEGATIVE: ctx:pawn refuses an unknown state")
def t_e3_pawn_bad_state():
    p = _run("function build(ctx) ctx:pawn('Jawa',1,1,'wild','undead') end")
    assert not p.pawns
    assert [r for r in p.refusals if r.code == "pawn-bad-state"], p.refusals


@case("E4: ctx:window replaces the wall cell, like ctx:door")
def t_e4_window():
    p = _run("function build(ctx) ctx:wall_rect(0,0,5,5) ctx:window(2,0) end")
    at = p.thing_at(2, 0)
    assert len(at) == 1 and at[0].role == "WINDOW", at


@case("E4: rng.jitter(r) returns an offset in [-r,r]")
def t_e4_rng_jitter():
    p = _run("function build(ctx) "
             "for i=1,50 do local j = rng.jitter(3) "
             "assert(j >= -3 and j <= 3, 'jitter out of range: '..j) end "
             "ctx:place('Wall',1,1) end")
    assert p.things


@case("E4: hug/clutter/aisle_ok exist and do what they say")
def t_e4_prelude_helpers():
    p = _run("function build(ctx) "
             "local r = shell(ctx, 'Room', R(0,0,8,8), {floor='FLOOR', doors={'S'}}) "
             "local n = hug(ctx, 'STOOL', r, {'N','E','W'}, {n=2}) "
             "local c = clutter(ctx, r, {{role='CRATE', weight=2}, {role='BARREL', weight=1}}, 3) "
             "local ok, cov, unreached = aisle_ok(ctx, r) "
             "note(string.format('hug=%d clutter=%d ok=%s cov=%.2f unreached=%d', "
             "n, c, tostring(ok), cov, unreached)) end")
    assert any("hug=" in n for n in p.notes), p.notes
    assert not [f for f in lint(p) if f.level == "ERROR"], \
        [str(f) for f in lint(p) if f.level == "ERROR"]


@case("E4: ctx:ruin removes wall cells and returns how many")
def t_e4_ruin():
    p = _run("function build(ctx) "
             "local r = shell(ctx, 'Room', R(0,0,10,10), {floor='FLOOR', doors={'S'}}) "
             "ctx:place_role('BED', 2, 2) "
             "local removed = ctx:ruin(0.3) "
             "note('ruin removed ' .. removed) end")
    walls_left = [t for t in p.things if (t.role or "") == "WALL"]
    assert len(walls_left) < 36, "ruin() removed no wall cells at all"
    assert any("ruin removed" in n for n in p.notes)


@case("NEGATIVE: ctx:ruin on a wall-less plan refuses rather than crashing")
def t_e4_ruin_no_walls():
    p = _run("function build(ctx) ctx:ruin(0.5) end")
    assert [r for r in p.refusals if r.what == "ruin"], p.refusals


@case("E6: interior-bare-ground fires for a room with an unfloored cell")
def t_e6_bare_ground_fires():
    p = _run("function build(ctx) ctx:room('Bedroom',0,0,5,5) "
             "ctx:wall_rect(0,0,5,5) ctx:door(2,0) end")
    # ctx:room() floors its own interior; delete one cell's terrain to prove
    # the rule actually looks, rather than trusting room() always did its job.
    any_cell = next(iter(p.terrain))
    del p.terrain[any_cell]
    assert [f for f in lint(p) if f.code == "interior-bare-ground"], \
        "a room missing one floor cell was not caught"


@case("NEGATIVE: regular-grid fires for >=2 equally-spaced lines, never for the walls")
def t_e6_regular_grid_fires():
    p = _run("function build(ctx) local r = shell(ctx, 'Room', R(0,0,10,4), "
             "{floor='FLOOR', doors={'S'}}) "
             "for _, x in ipairs({1,3,5,7}) do "
             "ctx:place('Stool', x, 1) ctx:place('Stool', x, 2) end end")
    f = [x for x in lint(p) if x.code == "regular-grid"]
    assert f, "two parallel equally-spaced lines of Stool were not caught"
    assert not [x for x in lint(p) if x.code == "regular-grid" and "Wall" in x.msg], \
        "the room's own rectangular WALL perimeter false-positived as a lattice"


@case("NEGATIVE: no-secondary fires for a primary with zero clutter, "
     "but an OVERLAY secondary (a wall lamp) satisfies it")
def t_e6_no_secondary_fires():
    p = _run("function build(ctx) local r = shell(ctx, 'Bedroom', R(0,0,6,6), "
             "{floor='FLOOR', doors={'S'}}) ctx:place_role('BED', 2, 2) end")
    assert [f for f in lint(p) if f.code == "no-secondary"], \
        "a bedroom with a bed and nothing else was not caught"
    p2 = _run("function build(ctx) local r = shell(ctx, 'Bedroom', R(0,0,6,6), "
              "{floor='FLOOR', doors={'S'}}) ctx:place_role('BED', 2, 2) "
              "assert(ctx:wall_attach('WALL_LIGHT', 3, 4, 0)) end")
    assert not [f for f in lint(p2) if f.code == "no-secondary"], \
        "an overlay wall lamp should count as the room's secondary"


@case("NEGATIVE: door-centred fires at the exact midpoint of a >=7 wall, "
     "and door_on's own random default no longer lands there")
def t_e6_door_centred_fires():
    from .core import BuildPlan
    p = BuildPlan({"footprint": [0, 0, 9, 9]})
    p.add_room("r1", "Room", Rect(0, 0, 9, 9))
    for x in range(9):
        p.add_thing("Wall", x, 0, 0, None, "WALL")
        p.add_thing("Wall", x, 8, 0, None, "WALL")
    for z in range(1, 8):
        p.add_thing("Wall", 0, z, 0, None, "WALL")
        p.add_thing("Wall", 8, z, 0, None, "WALL")
    p.things = [t for t in p.things if not (t.x == 4 and t.z == 0)]
    p.add_thing("Door", 4, 0, 0, None, "DOOR")
    assert [f for f in lint(p) if f.code == "door-centred"], \
        "a door at the exact midpoint of a 9-long wall was not caught"
    # door_on()'s own default must avoid landing there across many seeds
    for seed in range(1, 30):
        pl = _run("function build(ctx) local r = shell(ctx, 'Room', R(0,0,9,4), "
                  "{floor='FLOOR', doors={'S'}}) end", seed=seed)
        assert not [f for f in lint(pl) if f.code == "door-centred"], \
            f"door_on landed on the exact midpoint at seed {seed}"


@case("NEGATIVE: aisle-blocked fires when furniture walls off a primary")
def t_e6_aisle_blocked_fires():
    # Built directly on the IR (like the door-centred case above), not via a
    # real BED defName: a real Bedroll's own footprint sits 1x2, and picking
    # a corner cell for a symbolic test collides with the shell's own wall
    # before the aisle-fill logic is even reached - the interior geometry is
    # what this case is about, not a real thing's real size.
    from .core import BuildPlan
    p = BuildPlan({"footprint": [0, 0, 6, 6]})
    p.add_room("r1", "Room", Rect(0, 0, 6, 6))
    for x, z in Rect(0, 0, 6, 6).edge_cells():
        p.add_thing("Wall", x, z, 0, None, "WALL")
    p.things = [t for t in p.things if not (t.x == 2 and t.z == 0)]
    p.add_thing("Door", 2, 0, 0, None, "DOOR")
    # a bed tucked in the far corner (4,4), sealed off by two "walls" of its
    # own (a barricade line a template built badly) at its only two in-bounds
    # interior neighbours
    p.add_thing("Bed", 4, 4, 0, None, "BED")
    p.add_thing("Crate", 3, 4, 0, None, "CRATE")
    p.add_thing("Crate", 4, 3, 0, None, "CRATE")
    f = [x for x in lint(p) if x.code == "aisle-blocked" and x.level == "ERROR"]
    assert f, "a bed sealed off by its own neighbours was not caught"


def run_selftest() -> int:
    ok = fail = 0
    for name, fn in CASES:
        try:
            fn()
            ok += 1
            print(f"  PASS  {name}")
        except Exception as e:
            fail += 1
            print(f"  FAIL  {name}\n          {type(e).__name__}: {e}")
    print(f"\n  {ok}/{ok + fail} passed")
    return 1 if fail else 0
