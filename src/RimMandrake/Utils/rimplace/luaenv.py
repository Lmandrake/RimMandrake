"""rimplace.luaenv - the Lua runtime, its sandbox, and the API templates get.

WHY LUA (owner, 2026-08-22): "we will need something like lua for rapid
prototyping and debugging without constant game reloads."

The point is the EDIT-RUN LOOP. A template is a text file; changing it and
seeing the new house is one command and a few milliseconds. No build, no deploy,
no load. That is the entire justification, and it is why the renderer in
plan.py matters as much as this file.

🔴 THE SANDBOX IS NOT OPTIONAL. Templates are DATA. A template that can open a
socket or delete a file is a template that can do it on someone else's machine
when we ship one. `os`, `io`, `require`, `dofile`, `loadfile`, `load` and
`package` are all removed. This is cheap to do now and impossible to retrofit
once templates are being shared.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .core import BuildPlan, Palette, Rect, SeededRng

# Removed from the template environment. `load`/`loadstring` go too: they are
# the standard way back out of a sandbox that only removed the obvious names.
_FORBIDDEN = ("os", "io", "package", "require", "dofile", "loadfile",
              "load", "loadstring", "collectgarbage", "debug", "rawset",
              "rawget", "setmetatable", "getmetatable")

_SANDBOX_PRELUDE = """
for _, name in ipairs({%s}) do _G[name] = nil end
""" % ", ".join(f'"{n}"' for n in _FORBIDDEN)


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

    # ---- emit -------------------------------------------------------------
    def place(self, defName, x, z, rot=0, stuff=None, role=None):
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
        everything already placed? Ask before laying anything multi-cell."""
        d = self.role(str(name)) or str(name)
        if d is None:
            return False
        x, z = int(x), int(z)
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
        self.plan.set_roof(x, z, str(defName or "RoofConstructed"))
        return True

    def roof_rect(self, x, z, w, h, defName=None):
        for xx, zz in Rect(int(x), int(z), int(w), int(h)).cells():
            self.roof(xx, zz, defName)
        return True

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


def _lua_rect(L, rect: Rect):
    t = L.table()
    t["x"], t["z"], t["w"], t["h"] = rect.x, rect.z, rect.w, rect.h
    t["x2"], t["z2"] = rect.x2, rect.z2
    return t


def run_template(path: str | Path, rect: Rect, params: dict,
                 palette: Palette, seed: int, site=None) -> BuildPlan:
    """Execute a Lua template and return the BuildPlan it produced."""
    try:
        from lupa import LuaRuntime
    except ImportError as e:                                   # pragma: no cover
        raise TemplateError(
            "lupa (Lua runtime) is not importable. Create it with:\n"
            "  python3 -m venv ~/.local/venvs/rimlua\n"
            "  ~/.local/venvs/rimlua/bin/pip install lupa\n"
            "then run this tool with ~/.local/venvs/rimlua/bin/python"
        ) from e

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
        "seed": int(seed),
        "generator": "lua-prototype/0.1",
        "footprint": rect.as_list(),
        **{k: v for k, v in params.items()},
    })
    rng = SeededRng(seed)
    ctx = Ctx(plan, rect, params, palette, rng, site)

    L = LuaRuntime(unpack_returned_tuples=True, register_eval=False)
    L.execute(_SANDBOX_PRELUDE)

    g = L.globals()
    g["ctx"] = ctx
    g["rect"] = _lua_rect(L, rect)

    p = L.table()
    for k, v in params.items():
        p[k] = v
    g["params"] = p

    rngt = L.table()
    rngt["int"] = rng.int
    rngt["chance"] = rng.chance
    rngt["pick"] = lambda t: rng.pick(list(t.values()) if hasattr(t, "values") else t)
    g["rng"] = rngt

    # role(name) as a bare function is the most-used call in any template
    g["role"] = ctx.role
    g["note"] = ctx.note

    try:
        L.execute(src_text)
    except Exception as e:
        raise TemplateError(f"{path.name}: {e}") from e

    build = g["build"]
    if build is None:
        raise TemplateError(f"{path.name}: no global function build(ctx)")
    try:
        build(ctx)
    except Exception as e:
        raise TemplateError(f"{path.name}: build() raised: {e}") from e

    return plan
