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
from .luaenv import TemplateError, run_template
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
    tpl = _TEMPLATES / "dwelling.lua"
    if not tpl.exists():
        return
    params = {"faction": "Jawa_IndigenousTribes", "rooms": 3, "occupants": 2}
    p = run_template(tpl, Rect(0, 0, 8, 6), params, _pal(), 1)
    assert p.refusals, "a 8x6 rect silently accepted 3 rooms"
    assert len(p.rooms) != 3, "it built 3 rooms in a rect that cannot hold them"


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
