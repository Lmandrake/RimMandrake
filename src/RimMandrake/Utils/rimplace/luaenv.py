"""rimplace.luaenv - the Lua runtime, its sandbox, and the API templates get.

WHY LUA (owner, 2026-08-22): "we will need something like lua for rapid
prototyping and debugging without constant game reloads."

The point is the EDIT-RUN LOOP. A template is a text file; changing it and
seeing the new house is one command and a few milliseconds. No build, no deploy,
no load. That is the entire justification, and it is why the renderer in
plan.py matters as much as this file.

🔴 THE SANDBOX IS NOT OPTIONAL. Templates are DATA. A template that can open a
socket or delete a file is a template that can do it on someone else's machine
when we ship one. `os`, `io`, `require`, `dofile`, `loadfile`, `load`, `package`
and — the one that actually mattered — **`python`** are all removed. This is
cheap to do now and impossible to retrofit once templates are being shared.

⚠️ Until 2026-09-02 this paragraph was FALSE. lupa injects a `python` table
whenever `register_builtins` is on, which it is by default, so a template could
reach `python.builtins.open(...)` no matter what else was nil'd. Verify the
sandbox by BEHAVIOUR — try to write a file and assert it fails — never by
listing names, because the list cannot contain the name you forgot.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

from .core import BuildPlan, Palette, Rect, SeededRng

# Removed from the template environment. `load`/`loadstring` go too: they are
# the standard way back out of a sandbox that only removed the obvious names.
#
# 🔴 `python` IS THE ONE THAT MATTERED, AND IT WAS MISSING UNTIL 2026-09-02.
# lupa injects a `python` table whenever `register_builtins` is on — and it is on by
# default; `register_eval=False` turns off `python.eval`, NOT the table. So a template
# could reach `python.builtins.__import__("os").system(...)` or `python.builtins.open`
# and every name below was irrelevant. Demonstrated in review: a template wrote a file
# to disk and returned a clean value. Templates are DATA, and this file's own docstring
# promises they cannot touch the machine — that promise was false for as long as it
# existed. ⚠️ The three SANDBOX selftests asserted exactly the three names they nil'd,
# which is why nobody noticed: a test that checks the list you wrote cannot find the
# entry you forgot. The selftest now probes `python` by BEHAVIOUR, not by name.
#
# 🔴 `pcall`/`xpcall` DEFEAT THE INSTRUCTION BUDGET, AND THIS WAS NEVER TESTED WITH
# ONE. RIMPLACE_LUA_EXECUTION_BUDGET_1's own verification only tried a bare
# `while true do end` — `debug.sethook`'s count hook fires by calling Lua's
# `error()`, and a Lua error raised from a hook is caught by an ordinary
# enclosing `pcall` exactly like any other runtime error. `while true do
# pcall(function() while true do end end) end` therefore catches the
# "exceeded N instructions" error every N instructions FOREVER — confirmed by
# hand: 21 outer iterations and 10.5 million inner loop turns in well under a
# second, no sign of stopping on its own. Removing `pcall`/`xpcall` from the
# template environment is the only place in Lua's own semantics that closes
# this: with no `pcall` reachable, the hook's `error()` is never caught by
# anything and always reaches `run_template`'s handler as a loud TemplateError.
# This also closes half of the OTHER standing risk this file worries about —
# a template that swallows a real error and does nothing instead of failing
# loud — since `pcall` was the only way a template could do that at all.
_FORBIDDEN = ("os", "io", "package", "require", "dofile", "loadfile",
              "load", "loadstring", "collectgarbage", "debug", "rawset",
              "rawget", "setmetatable", "getmetatable", "python",
              "pcall", "xpcall")

_SANDBOX_PRELUDE = """
for _, name in ipairs({%s}) do _G[name] = nil end
""" % ", ".join(f'"{n}"' for n in _FORBIDDEN)

# RIMPLACE_LUA_EXECUTION_BUDGET_1: `function min_rect(params) while true do end
# end` used to wedge the whole process forever, with `rimplace minrect all`
# running every template in the library and no output naming which one hung.
# 5,000,000 Lua instructions trips a runaway loop in well under a hundredth of
# a second; the largest real template build measured runs a few hundred
# thousand.
_INSTRUCTION_BUDGET = 5_000_000

_BUDGET_HOOK = """
debug.sethook(function()
  error("exceeded %d Lua instructions without finishing - likely an infinite loop")
end, "", %d)
""" % (_INSTRUCTION_BUDGET, _INSTRUCTION_BUDGET)


def _attribute_filter(obj, name, is_setting):
    """Refuse every dunder, and refuse writing ANY attribute, on the Python side.

    🔴 NILLING NAMES IN `_G` NEVER CLOSED THE SANDBOX, BECAUSE WE HAND LUA LIVE
    PYTHON OBJECTS. `ctx`, `role` and `rng.int` are a Ctx, a bound method and a bound
    method; lupa exposes their attributes to Lua, so with no filter a template walks

        ctx.__class__.__init__.__globals__.Path("/anywhere"):write_text(...)
        ctx.plan.__class__.__init__.__globals__["__builtins__"]["open"](...)
        role.__self__.__class__.__init__.__globals__ ...

    and reaches `open`, `__import__` and this module's own `Path`. Demonstrated by
    behaviour on 2026-09-02: all four routes created a file on disk with `os`, `io`,
    `python`, `require`, `load` and `debug` all nil. The 2026-09-02 `python` fix and
    its behavioural selftest both closed exactly the one route they knew about —
    which is the same mistake the name-list tests made, one level up.

    ⚠️ THE FILTER IS THE FENCE; `_FORBIDDEN` IS A CONVENIENCE. Underscore-prefixed
    names are refused wholesale rather than a denylist of `__class__`/`__globals__`,
    because a denylist is the thing that keeps failing here. Templates only ever call
    the public API (`ctx:place`, `ctx.rect`, `rng.int`), so nothing legitimate is lost.

    ⚠️ `is_setting` is refused outright. A template that could assign to `ctx.rect` or
    `ctx.plan` would rewrite the engine's own state mid-build, and no template has any
    reason to: everything a template may change goes through a method on Ctx.
    """
    if is_setting:
        raise AttributeError(
            "templates are DATA and may not set attributes on engine objects "
            "(tried to set %r on %s)" % (name, type(obj).__name__))
    if name.startswith("_"):
        raise AttributeError(
            "sandbox: %r is not reachable from a template. Underscore attributes are "
            "the route out of the sandbox and are refused on every object; use the "
            "documented ctx: API." % (name,))
    return name


_PRELUDE_PATH = Path(__file__).resolve().parent / "prelude.lua"


def _prelude_text() -> str:
    return _PRELUDE_PATH.read_text(encoding="utf-8")


def _prelude_sha() -> str:
    return hashlib.sha256(_prelude_text().encode("utf-8")).hexdigest()[:16]


def _sandboxed_runtime(rng=None):
    """The ONE place a LuaRuntime is constructed. Two existed and only one was
    reviewed; a second construction site is a second sandbox to keep in step.

    ⭐ `prelude.lua` (the shared authoring helpers: scatter, along_wall, dress,
    shell...) is executed here, AFTER the sandbox strips the forbidden names and
    BEFORE any template runs, so it lives under exactly the same fence a
    template does and can only ever call the documented ctx API. Its content
    hash rides on every plan as meta.prelude_sha256 next to the template's own,
    because a plan is a function of BOTH sources now. It needs `rng` to exist
    as a global (shuffle/jitter), which is why the rng table is bound first.
    """
    from lupa import LuaRuntime
    L = LuaRuntime(unpack_returned_tuples=True, register_eval=False,
                   attribute_filter=_attribute_filter)
    # The hook is installed HERE, before the prelude nils `debug` out of _G.
    # debug.sethook is a VM-level registration, not a name lookup in the
    # global table, so removing `debug` stops a template calling sethook
    # itself without touching the hook already installed. It must be a Lua
    # closure, not a Python callable passed in as an argument: debug.sethook
    # requires a real Lua function (LUA_TFUNCTION) and lupa exposes a Python
    # callable to Lua as userdata with a __call metamethod, which fails that
    # check with "function expected, got POBJECT" — confirmed by hand before
    # writing this.
    L.execute(_BUDGET_HOOK)
    L.execute(_SANDBOX_PRELUDE)
    if rng is not None:
        _bind_rng(L, rng)
    L.execute(_prelude_text())
    return L


def _bind_rng(L, rng):
    rngt = L.table()
    rngt["int"] = rng.int
    rngt["chance"] = rng.chance
    rngt["pick"] = lambda t: rng.pick(list(t.values()) if hasattr(t, "values") else t)
    L.globals()["rng"] = rngt


class TemplateTooSmall(RuntimeError):
    """The rect is below the minimum the template DECLARED, checked before build().

    🔑 TEMPLATE_CANVAS_UNDECLARED_1. A template's required canvas used to live
    nowhere a caller could read it: 4 of 21 templates drew nothing at the default
    16x12 because each needed more room, and the only place that said so was a
    `ctx:refuse()` fired mid-build, after floor and prop placement had already run.
    `min_rect(params) -> w, h` is the declaration; this is what a caller gets
    instead of a half-built plan.

    ⚠️ A declared minimum is a FLOOR, not a guarantee. `build()` may still refuse a
    rect that clears it, for reasons no single pair of numbers can express (a bed
    that will not fit a particular room, a palette with no cooler). Nothing here
    replaces `ctx:refuse` — it front-runs the one refusal that is purely about size.
    """
    def __init__(self, template, need, got):
        self.template, self.need, self.got = template, need, got
        super().__init__(
            "%s needs at least %dx%d and was given %dx%d. It declares this itself "
            "(`min_rect` in the template); nothing was built."
            % (template, need[0], need[1], got[0], got[1]))


class TemplateError(RuntimeError):
    pass


class Ctx:
    """The object a template's build(ctx) receives.

    Everything a template can do to the world goes through here, which means
    every mutation is observable, loggable and refusable in ONE place.
    """

    def __init__(self, plan: BuildPlan, rect: Rect, params: dict,
                 palette: Palette, rng: SeededRng, site=None):
        self.plan = plan
        self.rect = rect
        self.params = params
        self.palette = palette
        self.rng = rng
        self.site = site
        self._room_seq = 0
        self._sizes = None          # lazy: the ThingDef footprint index

    # ---- palette ----------------------------------------------------------
    def role(self, name):
        """Resolve an abstract role to a defName. Returns nil if unmapped."""
        return self.palette.get(str(name))

    def has_role(self, name):
        return self.palette.get(str(name)) is not None

    # ---- queries ----------------------------------------------------------
    def in_bounds(self, x, z):
        return self.rect.contains(int(x), int(z))

    def buildable(self, x, z):
        """Site check. With no site model loaded, everything in bounds is
        buildable - and the plan records that the check was VACUOUS rather
        than passing, so nobody mistakes 'not checked' for 'checked ok'."""
        x, z = int(x), int(z)
        if not self.rect.contains(x, z):
            return False
        if self.site is None:
            return True
        return self.site.buildable(x, z)

    def occupied(self, x, z):
        return self.plan.occupied(int(x), int(z))

    # ---- footprints -------------------------------------------------------
    def sizes(self):
        """The ThingDef size index, loaded once. {} means UNMEASURED."""
        if self._sizes is None:
            try:
                from .defsize import load as _load
                self._sizes = _load()
            except Exception:
                self._sizes = {}
        return self._sizes

    def footprint_of(self, defName, x, z, rot=0):
        """The cells a thing would occupy, or None if its size is unmeasured."""
        from .defsize import footprint as _fp
        return _fp(str(defName), int(x), int(z), int(rot or 0), self.sizes())

    def _footprint_owner(self, cells, defName, origin):
        """The already-placed thing whose own footprint covers any of `cells`.

        Rebuilt per call rather than cached: door() removes the wall it
        replaces, and a stale occupancy map would refuse the door. A plan holds
        a few hundred things, so this is cheap and cannot drift.
        """
        sizes = self.sizes()
        if not sizes:
            return None
        from .defsize import footprint as _fp
        for t in self.plan.things:
            if t.overlay:
                continue            # non-edifice: shares a cell by design
            # Only the IDENTICAL thing in the IDENTICAL cell is exempt - that is
            # the shared-wall-column case place() already returns True for. Two
            # shelves at different origins overlap exactly as much as a shelf
            # and a table do, and the live map lost two shelves that way.
            if t.defName == str(defName) and (t.x, t.z) == origin:
                continue
            own = _fp(t.defName, t.x, t.z, t.rot or 0, sizes)
            if own is None:
                continue
            hit = cells & own
            if hit:
                return t, sorted(hit)[0]
        return None

    def role_at(self, x, z):
        """The palette ROLE of the edifice standing at (x,z), or nil. Overlays
        are skipped. This is what a template needs to keep the cell in front
        of a DOOR clear, or to find the WALL a lamp hangs on."""
        for t in self.plan.thing_at(int(x), int(z)):
            if not t.overlay:
                return t.role
        return None

    # ---- emit -------------------------------------------------------------
    def place(self, defName, x, z, rot=0, stuff=None, role=None, overlay=False):
        x, z = int(x), int(z)
        if defName is None:
            self.plan.refuse("place", "nil defName (unmapped palette role?)", x, z)
            return False
        if not self.rect.contains(x, z):
            self.plan.refuse(str(defName), "outside the footprint", x, z)
            return False
        if not self.buildable(x, z):
            self.plan.refuse(str(defName), "terrain is not buildable", x, z)
            return False
        # Idempotent: two adjacent rooms legitimately share a wall column, and
        # re-placing the same def there is not a collision. A DIFFERENT def in
        # the same cell still is, and the linter will say so.
        for ex in self.plan.thing_at(x, z):
            if ex.defName == str(defName):
                return True

        # 🔴 FOOTPRINT, not the origin cell. TEMPLATE_FOOTPRINT_IGNORES_SIZE_1:
        # this used to check (x,z) alone, so a 1x2 Table1x2c placed at (176,171)
        # left (176,172) looking free, a DiningChair went there, and
        # jawa/build_batch wiped the chair while reporting BOTH as placed. Three
        # of 81 things vanished that way and lint reported nothing.
        cells = self.footprint_of(defName, x, z, rot)
        if overlay:
            # A non-edifice shares its cells with whatever edifice is there
            # (GenSpawn.SpawningWipes never wipes for one, in either direction).
            # It still has to lie inside the footprint, whole.
            if cells is not None and not all(self.rect.contains(cx, cz) for cx, cz in cells):
                self.plan.refuse(str(defName), "overlay footprint leaves the plan rect", x, z)
                return False
            self.plan.add_thing(str(defName), x, z, int(rot or 0),
                                str(stuff) if stuff else None,
                                str(role) if role else None, overlay=True)
            return True
        if cells is None:
            # Unmeasured size. Say so on the plan and place it as authored -
            # refusing here would silently drop content because an INDEX is
            # missing, which is a worse failure than the one being fixed.
            self.plan.refuse(str(defName),
                             "size UNMEASURED (not in the def size index); "
                             "its footprint was not checked", x, z)
        else:
            clash = self._footprint_owner(cells, defName, (x, z))
            if clash is not None:
                other, cell = clash
                osz = self.sizes().get(other.defName, [1, 1])
                self.plan.refuse(
                    str(defName),
                    f"footprint overlaps {other.defName} "
                    f"({osz[0]}x{osz[1]} at {other.x},{other.z}) at {cell}",
                    x, z, level="ERROR", code="footprint-collision")
                return False

        self.plan.add_thing(str(defName), x, z, int(rot or 0),
                            str(stuff) if stuff else None,
                            str(role) if role else None)
        return True

    def width_of(self, name):
        """Cells wide, resolving a ROLE or a defName. 1 when unmeasured.

        Templates step by this. A run of 2-wide shelves laid on a 1-cell stride
        eats itself, and that is not a thing a template can see without asking.
        """
        d = self.role(str(name)) or str(name)
        s = self.sizes().get(d)
        return int(s[0]) if s else 1

    def height_of(self, name):
        d = self.role(str(name)) or str(name)
        s = self.sizes().get(d)
        return int(s[1]) if s else 1

    def can_place(self, name, x, z, rot=0):
        """Would the WHOLE footprint fit here, inside the rect and clear of
        everything already placed? Ask before laying anything multi-cell.

        🔴 Must mirror every gate `place()` itself checks, or a caller that
        loops "first cell can_place approves" (`place_role_fit`) commits to a
        cell `place()` then refuses, and the loop stops dead instead of
        trying the next cell. `buildable()` was missing here — silent no-op
        only once a site model exists (today `site` is always None, so this
        was unreachable), but the gap was real.
        """
        d = self.role(str(name)) or str(name)
        if d is None:
            return False
        x, z = int(x), int(z)
        if not self.buildable(x, z):
            return False
        cells = self.footprint_of(d, x, z, rot)
        if cells is None:
            return self.rect.contains(x, z) and not self.occupied(x, z)
        if not all(self.rect.contains(cx, cz) for cx, cz in cells):
            return False
        return self._footprint_owner(cells, d, (x, z)) is None

    def place_role_fit(self, role, x, z, w, h, rot=0):
        """Place a role at the first cell of the given rect where its whole
        footprint fits. Returns true if it landed.

        🔑 This is the difference between a plan that loses furniture and one
        that says it could not fit it: a refusal is recorded either way, and the
        caller can read the return value.
        """
        d = self.role(str(role))
        if d is None:
            self.plan.refuse(f"role:{role}", "no palette entry", int(x), int(z))
            return False
        x, z, w, h = int(x), int(z), int(w), int(h)
        for zz in range(z, z + h):
            for xx in range(x, x + w):
                if self.can_place(d, xx, zz, rot):
                    return self.place(d, xx, zz, rot,
                                      self.role(str(role) + "_STUFF"), role)
        self.plan.refuse(str(d),
                         f"no cell in {w}x{h} at ({x},{z}) fits its "
                         f"{self.width_of(d)}x{self.height_of(d)} footprint",
                         x, z)
        return False

    def place_role(self, role, x, z, rot=0):
        d = self.role(role)
        if d is None:
            self.plan.refuse(f"role:{role}", "no palette entry", int(x), int(z))
            return False
        return self.place(d, x, z, rot, self.role(str(role) + "_STUFF"), role)

    # Rot4 as the engine has it: 0 north (+z), 1 east (+x), 2 south (-z), 3 west (-x).
    _DIR = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}

    def place_overlay(self, name, x, z, rot=0):
        """Place a NON-EDIFICE thing that shares its cell(s): a floor decal, an
        Aurebesh sign, a rug-like marker. `name` is a palette ROLE or a raw
        defName. Skips every collision check on purpose - see Thing.overlay
        for the engine reading that makes this safe. 🔴 Only use it for defs
        whose building.isEdifice is false; an edifice placed this way would be
        wiped live while the plan reports it placed."""
        role = str(name)
        d = self.role(role)
        if d is None:
            d, role_tag = role, None
        else:
            role_tag = role
        return self.place(d, x, z, rot, self.role(role + "_STUFF") if role_tag else None,
                          role_tag, overlay=True)

    def wall_attach(self, role, x, z, rot=0):
        """A wall-mounted thing (wall lamp, wall torch) the way 1.6 actually
        places one: ON THE FLOOR CELL IN FRONT of the wall, rotated to FACE the
        wall. Placeworker_AttachedToWall (RimWorld/Placeworker_AttachedToWall.cs)
        refuses a Fillage-Full cell at `loc` and requires the wall at
        `loc + CardinalDirections[rot]` - read, not guessed. So `rot` here is
        the side the wall is on: a lamp on a room's north wall is placed one
        cell inside that wall at rot 0. Refuses (WARN, attach-no-wall) when
        there is no WALL-role thing in that cell, rather than spawning a lamp
        the game would have refused to build."""
        d = self.role(role)
        if d is None:
            self.plan.refuse(f"role:{role}", "no palette entry", int(x), int(z))
            return False
        x, z, rot = int(x), int(z), int(rot or 0) % 4
        dx, dz = self._DIR[rot]
        if self.role_at(x + dx, z + dz) != "WALL":
            self.plan.refuse(str(d), f"no WALL at ({x + dx},{z + dz}) for rot {rot} to attach to",
                             x, z, level="WARN", code="attach-no-wall")
            return False
        if self.role_at(x, z) == "WALL" or self.role_at(x, z) == "DOOR":
            self.plan.refuse(str(d), "wall attachments sit in FRONT of a wall, not in it",
                             x, z, level="WARN", code="attach-in-wall")
            return False
        return self.place(d, x, z, rot, self.role(str(role) + "_STUFF"), role, overlay=True)

    def floor(self, x, z, defName=None):
        d = defName or self.role("FLOOR")
        if d is None:
            self.plan.refuse("floor", "no FLOOR in palette", int(x), int(z))
            return False
        if not self.rect.contains(int(x), int(z)):
            self.plan.refuse(str(d), "outside the footprint", int(x), int(z))
            return False
        self.plan.set_terrain(x, z, str(d))
        return True

    def floor_rect(self, x, z, w, h, defName=None):
        n = 0
        for xx, zz in Rect(int(x), int(z), int(w), int(h)).cells():
            if self.floor(xx, zz, defName):
                n += 1
        return n

    def paint(self, x, z, colorDef):
        """Vanilla building paint (Building.ChangePaint) on the thing at x,z.
        Per-cell and explicit by the owner's ruling, 2026-08-28 — no palette
        involvement. Painting an empty cell is a refusal, not a silent no-op."""
        x, z = int(x), int(z)
        if not colorDef:
            self.plan.refuse("paint", "nil colorDef", x, z)
            return False
        here = self.plan.thing_at(x, z)
        if not here:
            self.plan.refuse("paint", "nothing at this cell to paint", x, z)
            return False
        for t in here:
            t.paint = str(colorDef)
        return True

    def floor_color(self, x, z, colorDef):
        """Floor colour (the 1.6 terrain colour grid). Colouring a cell this
        plan lays no floor on is a refusal — the colour would land on whatever
        the map happens to hold."""
        x, z = int(x), int(z)
        if not colorDef:
            self.plan.refuse("floor_color", "nil colorDef", x, z)
            return False
        if (x, z) not in self.plan.terrain:
            self.plan.refuse("floor_color", "no floor laid at this cell in this plan", x, z)
            return False
        self.plan.set_floor_color(x, z, str(colorDef))
        return True

    def roof(self, x, z, defName=None):
        """RIMPLACE_ROOF_ESCAPES_FOOTPRINT_1: `floor()` has always refused a
        cell outside `self.rect`; this had no such check, so a template could
        roof cells past its own declared footprint — onto whatever the map
        placed next door — and nothing would say so."""
        x, z = int(x), int(z)
        if not self.rect.contains(x, z):
            self.plan.refuse("roof", "outside the footprint", x, z)
            return False
        self.plan.set_roof(x, z, str(defName or "RoofConstructed"))
        return True

    def roof_rect(self, x, z, w, h, defName=None):
        """Cells actually roofed, mirroring `floor_rect` — the unconditional
        `return True` here used to report success even when every cell in
        the rect was refused."""
        n = 0
        for xx, zz in Rect(int(x), int(z), int(w), int(h)).cells():
            if self.roof(xx, zz, defName):
                n += 1
        return n

    def wall_rect(self, x, z, w, h, defName=None, stuff=None):
        """Walls around the PERIMETER of the rect. Returns cells placed.

        ⚠️ Deliberately does NOT roof. jawa/build_batch says it outright:
        WALLS CREATE NO ROOF. Templates must roof explicitly, or call
        ctx:room() which derives it.
        """
        d = defName or self.role("WALL")
        st = stuff or self.role("WALL_STUFF")
        n = 0
        for xx, zz in Rect(int(x), int(z), int(w), int(h)).edge_cells():
            if self.place(d, xx, zz, 0, st, "WALL"):
                n += 1
        return n

    def door(self, x, z, defName=None, stuff=None, rot=0):
        d = defName or self.role("DOOR")
        st = stuff or self.role("DOOR_STUFF")
        # A door replaces the wall in that cell rather than stacking on it.
        self.plan.things = [t for t in self.plan.things
                            if not (t.x == int(x) and t.z == int(z))]
        return self.place(d, x, z, rot, st, "DOOR")

    def wall_mount(self, role, x, z, rot=0):
        """Place a wall-mounted thing (cooler, vent, wall lamp) INTO a wall cell.

        RimWorld models these as occupying the wall itself, exactly like a door.
        Placing one on top of a wall instead of replacing it is a cell collision,
        which is what the linter caught on the nursery's first run.
        """
        d = self.role(role)
        if d is None:
            self.plan.refuse(f"role:{role}", "no palette entry", int(x), int(z))
            return False
        self.plan.things = [t for t in self.plan.things
                            if not (t.x == int(x) and t.z == int(z))]
        return self.place(d, x, z, rot, self.role(str(role) + "_STUFF"), role)

    def room(self, role, x, z, w, h, roofed=True):
        """Declare a room. Floors it, roofs it, and records it in the plan so
        the linter can check it is sealed and the reviewer can read it."""
        self._room_seq += 1
        r = Rect(int(x), int(z), int(w), int(h))
        rm = self.plan.add_room(f"r{self._room_seq}", str(role), r)
        for xx, zz in r.inner().cells():
            self.floor(xx, zz)
            if roofed:
                self.roof(xx, zz)
        if roofed:
            for xx, zz in r.edge_cells():
                self.roof(xx, zz)
        return rm.id

    def note(self, text):
        self.plan.notes.append(str(text))

    def refuse(self, what, reason):
        self.plan.refuse(str(what), str(reason))


def _require_lupa():
    """Import lupa, or raise the TemplateError that says how to get it.

    `declared_min_rect` used to `from lupa import LuaRuntime` bare, so the one query
    a caller makes BEFORE building — "how big does this template need to be" — failed
    with a raw ImportError traceback while `run_template` gave the venv recipe.
    """
    try:
        import lupa  # noqa: F401
    except ImportError as e:                                   # pragma: no cover
        raise TemplateError(
            "lupa (Lua runtime) is not importable. Create it with:\n"
            "  python3 -m venv ~/.local/venvs/rimlua\n"
            "  ~/.local/venvs/rimlua/bin/pip install lupa\n"
            "then run this tool with ~/.local/venvs/rimlua/bin/python"
        ) from e


def _lua_rect(L, rect: Rect):
    t = L.table()
    t["x"], t["z"], t["w"], t["h"] = rect.x, rect.z, rect.w, rect.h
    t["x2"], t["z2"] = rect.x2, rect.z2
    return t


def run_template(path: str | Path, rect: Rect, params: dict,
                 palette: Palette, seed: int, site=None) -> BuildPlan:
    """Execute a Lua template and return the BuildPlan it produced."""
    _require_lupa()
    path = Path(path)
    if not path.exists():
        raise TemplateError(f"template not found: {path}")

    # Provenance is the template's CONTENT HASH, not its path. An absolute path
    # makes two identical houses compare unequal and leaks the machine's layout
    # into a shared artifact; a hash says exactly which source produced the plan
    # and survives the file being moved or renamed.
    src_text = path.read_text(encoding="utf-8")
    plan = BuildPlan({
        "template": path.stem,
        "template_sha256": hashlib.sha256(src_text.encode("utf-8")).hexdigest()[:16],
        "prelude_sha256": _prelude_sha(),
        "seed": int(seed),
        "generator": "lua-prototype/0.1",
        "footprint": rect.as_list(),
        **{k: v for k, v in params.items()},
    })
    rng = SeededRng(seed)
    ctx = Ctx(plan, rect, params, palette, rng, site)

    L = _sandboxed_runtime(rng)

    g = L.globals()
    g["ctx"] = ctx
    g["rect"] = _lua_rect(L, rect)

    p = L.table()
    for k, v in params.items():
        p[k] = v
    g["params"] = p

    # role(name) as a bare function is the most-used call in any template
    g["role"] = ctx.role
    g["note"] = ctx.note

    try:
        L.execute(src_text)
    except Exception as e:
        raise TemplateError(f"{path.name}: {e}") from e

    # 🔑 THE SIZE CHECK RUNS BEFORE build(), which is the whole point. See
    # `TemplateTooSmall`. A template with no `min_rect` is not forced to grow one —
    # several are genuinely size-agnostic (scatter-only, terrain-led), and demanding
    # a declaration from those would be a regression, not a fix.
    need = _declared_min(g, p, path.name)
    if need is not None:
        plan.meta["min_rect"] = list(need)
        if rect.w < need[0] or rect.h < need[1]:
            raise TemplateTooSmall(path.stem, need, (rect.w, rect.h))

    build = g["build"]
    if build is None:
        raise TemplateError(f"{path.name}: no global function build(ctx)")
    try:
        build(ctx)
    except Exception as e:
        raise TemplateError(f"{path.name}: build() raised: {e}") from e

    return plan


def _declared_min(g, params_table, name):
    """-> (w, h) the template declared, or None if it declares no floor.

    The convention is `function min_rect(params) return W, H end`, mirroring
    `build(ctx)`: a global the engine looks for, defined only by templates that
    have a real floor. It takes `params` because some floors depend on them —
    dwelling.lua needs `5 * rooms + 1` columns, so one pair of constants could
    never have been the answer. A table `{w = .., h = ..}` is accepted too.
    """
    fn = g["min_rect"]
    if fn is None:
        return None
    try:
        got = fn(params_table)
    except Exception as e:
        raise TemplateError(f"{name}: min_rect() raised: {e}") from e
    if got is None:
        return None
    # ⚠️ EVERY shape that is not two numbers or a table must land as a TemplateError.
    # `return '6x4'` used to take the table branch — `str` has `__getitem__` — and then
    # `got["w"]` raised a bare TypeError that escaped this function, escaped
    # `cli._build`'s handlers, and reached the user as a traceback.
    if isinstance(got, tuple):
        pair = got[:2]
    elif isinstance(got, (str, bytes, int, float)) or not hasattr(got, "__getitem__"):
        raise TemplateError(
            f"{name}: min_rect() must return two numbers (`return W, H`) or a "
            f"table {{w = .., h = ..}}; got {got!r}")
    else:
        try:
            pair = (got["w"] if got["w"] is not None else got[1],
                    got["h"] if got["h"] is not None else got[2])
        except Exception as e:
            raise TemplateError(
                f"{name}: min_rect() returned something table-like that carries "
                f"neither w/h nor [1]/[2] ({got!r})") from e
    # 🔑 CEIL, NEVER int(). A computed floor of 6.5 truncated to 6 declares a minimum
    # SMALLER than the real one, so a 6-wide rect passes this gate and build() then
    # refuses halfway — which is the exact failure TemplateTooSmall exists to front-run.
    # A floor must always round UP.
    try:
        w, h = math.ceil(float(pair[0])), math.ceil(float(pair[1]))
    except (TypeError, ValueError, IndexError) as e:
        raise TemplateError(
            f"{name}: min_rect() returned {pair!r}, which is not a width and a "
            f"height") from e
    if w < 1 or h < 1:
        raise TemplateError(
            f"{name}: min_rect() returned {w}x{h}. A floor below 1x1 is not a "
            f"floor — return nothing at all if the template has no minimum.")
    return (w, h)


def declared_min_rect(path: str | Path, params: dict) -> tuple[int, int] | None:
    """The template's declared minimum canvas, WITHOUT running build().

    ⭐ This is the query TEMPLATE_CANVAS_UNDECLARED_1 exists for: a `TileMutatorDef`
    author, a re-export script or a review-sheet build can ask "how big does this
    footprint need to be" and get a number, instead of reading the Lua by hand or
    discovering it empirically from a half-built plan.
    """
    _require_lupa()
    path = Path(path)
    if not path.exists():
        raise TemplateError(f"template not found: {path}")
    # A fixed seed: min_rect() is a pure question about a floor and must answer
    # the same every time, but the prelude's helpers expect `rng` to exist.
    L = _sandboxed_runtime(SeededRng(0))
    g = L.globals()
    p = L.table()
    for k, v in (params or {}).items():
        p[k] = v
    g["params"] = p
    try:
        L.execute(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise TemplateError(f"{path.name}: {e}") from e
    return _declared_min(g, p, path.name)
