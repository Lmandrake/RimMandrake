"""rimplace.plan - lint a BuildPlan, draw it, and compile it to bridge calls.

Three jobs, all offline:
  lint()     find what is wrong BEFORE a game load pays for it
  render()   draw the house as text - the whole reason the edit loop is fast
  compile()  BuildPlan -> the exact jawa/* calls that would build it
"""
from __future__ import annotations

import json
from collections import defaultdict

from . import netinfo

from .core import BuildPlan, Rect, Room

# --------------------------------------------------------------------------- #
#  Rendering
# --------------------------------------------------------------------------- #
_GLYPH = {
    "WALL": "#", "DOOR": "+", "BED": "b", "LIGHT": "*", "TABLE": "T",
    "CHAIR": "h", "STORAGE": "S", "STOVE": "K", "COOLER": "C", "HEATER": "H",
    "DECOR": "o", "BATTERY": "B", "GENERATOR": "G", "TURRET": "X",
    "SANDBAG": ",", "VENT": "v", "NEST": "n",
    # the clutter/prop vocabulary (DISTRICT_TEMPLATE_LIBRARY_1, 2026-09-05)
    "STOOL": "s", "CRATE": "c", "BARREL": "c", "SHELF_SMALL": "S",
    "END_TABLE": "t", "DRESSER": "D", "PLANT_POT": "p", "WALL_LIGHT": "'",
    "JUNK_PILE": "%", "SCRAP": "%", "WRECK": "W", "WRECK_BIG": "W",
    "FORGE": "K", "BRAZIER": "K", "THRONE": "R", "GAME": "g", "HOLO": "g",
    "INSTRUMENT": "g", "TERMINAL": "i", "SCREEN": "i", "CHARGER": "E",
    "GONK": "E", "FUEL_TANK": "F", "FUEL_TANK_SMALL": "F", "REFINERY": "F",
    "REACTOR": "F", "FABRICATOR": "F", "WATER_TANK": "U", "FOUNTAIN": "U",
    "WELL": "U", "TROUGH": "U", "TUB": "U", "HOSPITAL_BED": "b",
    "VITALS": "m", "HYDRO": "y", "SUNLAMP": "*", "TRAP": "x",
    "BARRICADE": ",", "FENCE": "|", "BANNER": "!", "DECAL": "~", "SIGN": "~",
    "PILLAR": "#", "DESK": "T", "MEDICINE": "m",
    "LIGHT_TALL": "*", "TABLE_SMALL": "T", "INSTRUMENT_BIG": "g", "HOLO_BAND": "g",
    "BED_FINE": "b", "CRATE_WIDE": "c", "SPICE": "%", "DRUG_LAB": "K",
    "CHARGER_BIG": "E", "REACTOR_BIG": "F", "GAS_TANK": "F", "TERMINAL_TALL": "i",
    "HOLO_TABLE": "i", "WORKBENCH": "K", "COMPONENT": "%", "STEEL": "%",
    "BASIN": "U", "SINK": "U", "DECOR_BIG": "o", "DECAL_ALT": "~",
    # INHABITED_AUGMENTATION_BUILD_1 (homestead + mining site vocabulary)
    "WINDOW": "=", "CHEST": "c", "FOOTLOCKER": "c", "CANDLE": "*",
    "NIGHT_LIGHT": "*", "TROPHY": "o", "JUNK": "%", "GRAVE": "_",
    "HAY": "%", "PEN_MARKER": "n", "COOLER_PASSIVE": "C", "GATE": "+",
    "ROCK": "@", "SEAM": "$", "RAIL_CAR": "W", "MACHINE": "F",
    "SUPPORT": "|", "TOOL": "/", "CONDUIT": "-", "FILTH": "`",
}


def render(plan: BuildPlan, show_roof=False) -> str:
    """Draw the plan as text. THIS is the debug loop the owner asked for:
    edit the .lua, re-run, look at the house. Milliseconds, no game."""
    fp = plan.meta.get("footprint")
    if not fp:
        return "(no footprint)"
    rect = Rect(*fp)
    grid = {}

    for (x, z) in plan.terrain:
        grid[(x, z)] = "."
    if show_roof:
        for (x, z) in plan.roof:
            if grid.get((x, z)) == ".":
                grid[(x, z)] = "-"
    # overlays (wall lamps, decals) draw only where nothing solid stands, so
    # the edifice under a decal is what the reviewer sees
    for t in sorted(plan.things, key=lambda t: t.overlay):
        g = _GLYPH.get((t.role or "").upper())
        if g is None and (t.role or "").upper().startswith("SIGN_"):
            g = "~"
        if g is None:
            d = t.defName.lower()
            g = ("#" if "wall" in d else "+" if "door" in d else
                 "b" if "bed" in d else "?")
        if t.overlay and grid.get((t.x, t.z), " ") not in (" ", ".", "-"):
            continue
        grid[(t.x, t.z)] = g

    pad = 1
    lines = []
    header = f"  {plan.meta.get('template','?')}  " \
             f"seed={plan.meta.get('seed')}  " \
             f"faction={plan.meta.get('faction','-')}  " \
             f"rooms={plan.meta.get('rooms','-')}  " \
             f"occ={plan.meta.get('occupants','-')}  " \
             f"wealth={plan.meta.get('wealth','-')}"
    lines.append(header)
    lines.append(f"  footprint {rect.w}x{rect.h} at ({rect.x},{rect.z})")
    lines.append("")
    # north at the top: z descends down the page
    for z in range(rect.z2 + pad, rect.z - pad - 1, -1):
        row = []
        for x in range(rect.x - pad, rect.x2 + pad + 1):
            row.append(grid.get((x, z), " "))
        lines.append(f"  {''.join(row)}")
    lines.append("")
    for r in plan.rooms:
        lines.append(f"  room {r.id:<4} {r.role:<12} "
                     f"{r.rect.w}x{r.rect.h} at ({r.rect.x},{r.rect.z})")
    if plan.notes:
        lines.append("")
        for n in plan.notes:
            lines.append(f"  note: {n}")
    legend = " ".join(f"{v}={k.lower()}" for k, v in _GLYPH.items()
                      if v in {g for g in grid.values()})
    if legend:
        lines.append("")
        lines.append(f"  {legend}  .=floor" + ("  -=roof" if show_roof else ""))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
#  Linting
# --------------------------------------------------------------------------- #
class Finding:
    def __init__(self, level, code, msg, x=None, z=None):
        self.level, self.code, self.msg, self.x, self.z = level, code, msg, x, z

    def __str__(self):
        loc = f" at ({self.x},{self.z})" if self.x is not None else ""
        return f"{self.level:<5} {self.code:<22} {self.msg}{loc}"


# RIMPLACE_ENGINE_DELTAS_1 E6. Role classes for the `no-secondary` rule - "a
# class from a palette role list, not a name list" (the item's own wording):
# these are ROLES, resolved from whatever defName the active faction/tech/
# wealth block maps them to, never a hardcoded defName.
_PRIMARY_ROLES = {"BED", "TABLE", "STOVE", "WORKBENCH", "STORAGE", "THRONE",
                  "GENERATOR", "TURRET", "FORGE", "DRUG_LAB", "HYDRO",
                  "REACTOR", "FABRICATOR", "REFINERY", "CHARGER", "DESK",
                  "GONK"}
# palette.json's own README names this exact tier ("CLUTTER tier: STOOL
# CRATE BARREL SHELF_SMALL END_TABLE DRESSER PLANT_POT WALL_LIGHT GAME"),
# plus the other roles the room recipes (spec §4) call secondary/personal.
_SECONDARY_ROLES = {"STOOL", "CRATE", "BARREL", "SHELF_SMALL", "END_TABLE",
                    "DRESSER", "PLANT_POT", "WALL_LIGHT", "GAME", "DECOR",
                    "SIGN", "BANNER", "INSTRUMENT", "TROUGH", "ANIMAL_BED",
                    "CHAIR", "DECOR_BIG", "TUB", "BASIN", "SINK", "SCRAP",
                    "JUNK_PILE", "WRECK", "DECAL", "BANNER"}


def lint(plan: BuildPlan, verified_defs: set[str] | None = None) -> list[Finding]:
    """Everything decidable without a game. Each check exists because the
    corresponding live failure is expensive or silent."""
    out: list[Finding] = []
    fp = plan.meta.get("footprint")
    rect = Rect(*fp) if fp else None

    # 1. two things in one cell - build_batch would silently wipe one.
    #    Overlays (Thing.overlay: non-edifice wall lamps, floor decals) are
    #    exempt by the engine's own rule (GenSpawn.SpawningWipes never wipes
    #    for or against a non-edifice), and 1b below skips them the same way.
    bycell = defaultdict(list)
    for t in plan.things:
        if t.overlay:
            continue
        bycell[(t.x, t.z)].append(t)
    for (x, z), ts in sorted(bycell.items()):
        if len(ts) > 1:
            names = ", ".join(t.defName for t in ts)
            out.append(Finding("ERROR", "cell-collision",
                               f"{len(ts)} things share a cell: {names}", x, z))

    # 1b. FOOTPRINT collisions, for a plan that did not come from luaenv.
    #     ctx:place() refuses these at generation time; this catches a plan
    #     built or edited by anything else, and it is the check that was missing
    #     when 3 of 81 things were destroyed on the map with lint reporting 0
    #     findings (TEMPLATE_FOOTPRINT_IGNORES_SIZE_1).
    try:
        from .defsize import footprint as _fp, load as _sizes
        sizes = _sizes()
    except Exception:
        sizes = {}
    if sizes:
        owner: dict = {}
        unmeasured = set()
        for t in plan.things:
            if t.overlay:
                continue
            cells = _fp(t.defName, t.x, t.z, t.rot or 0, sizes)
            if cells is None:
                unmeasured.add(t.defName)
                continue
            for c in sorted(cells):
                prev = owner.get(c)
                if prev is not None and (prev.defName, prev.x, prev.z) != (t.defName, t.x, t.z):
                    out.append(Finding(
                        "ERROR", "footprint-collision",
                        f"{t.defName} ({sizes.get(t.defName)}) at ({t.x},{t.z}) "
                        f"overlaps {prev.defName} at ({prev.x},{prev.z})",
                        c[0], c[1]))
                owner[c] = t
        for d in sorted(unmeasured):
            out.append(Finding("WARN", "size-unmeasured",
                               f"'{d}' is not in the def size index, so its "
                               f"footprint was NOT checked - this is UNMEASURED, "
                               f"not 1x1"))
    else:
        out.append(Finding("WARN", "size-index-missing",
                           "no def size index, so NO footprint was checked. "
                           "Build it: python3 -m rimplace.defsize --refresh"))

    # 2. out of footprint
    if rect:
        for t in plan.things:
            if not rect.contains(t.x, t.z):
                out.append(Finding("ERROR", "outside-footprint",
                                   f"{t.defName} is outside the rect", t.x, t.z))

    # 3. sealed rooms - the temperature mechanic needs a closed shell.
    #    An unsealed nursery is the failure that ruins a Jawa clutch.
    # A wall-mounted edifice fills the wall cell and still seals the room:
    # a cooler or heater is as much a shell as the wall it replaced.
    # ⚠️ A VENT is deliberately NOT in this set. It seals against WIND but its
    # whole purpose is to equalise temperature between two rooms - a vent in a
    # nursery wall defeats the cooling the nursery exists for. Check 5b catches
    # that specifically, because it is exactly the kind of thing that looks
    # correct on a plan and ruins a clutch in play.
    # A WINDOW is a wall-slot cell (E4: `ctx:window` replaces the wall the
    # way `ctx:door` does; RUT_WindowAdobe is parented on Wall and keeps
    # holdsRoof/isWall) - spec §3.1.3 says outright it "counts as WALL for
    # room-not-sealed". It was missing here, so the first template to cut a
    # window (homestead.lua, INHABITED_AUGMENTATION_BUILD_1) failed the seal
    # check on every window it cut; the E4 selftest only checked the replace.
    SEALING = {"WALL", "DOOR", "COOLER", "HEATER", "WINDOW"}
    walls = {(t.x, t.z) for t in plan.things if (t.role or "").upper() == "WALL"}
    doors = {(t.x, t.z) for t in plan.things if (t.role or "").upper() == "DOOR"}
    shell = {(t.x, t.z) for t in plan.things if (t.role or "").upper() in SEALING}
    for r in plan.rooms:
        gaps = [c for c in r.rect.edge_cells() if c not in shell]
        if gaps:
            out.append(Finding("ERROR", "room-not-sealed",
                               f"room {r.id} ({r.role}) has {len(gaps)} open "
                               f"perimeter cell(s); first at {gaps[0]}"))

    # 4. every room needs a way in
    for r in plan.rooms:
        if not any(c in doors for c in r.rect.edge_cells()):
            out.append(Finding("ERROR", "room-unreachable",
                               f"room {r.id} ({r.role}) has no door"))

    # 5. roofed cells with no enclosing wall would collapse or read as outdoors
    for r in plan.rooms:
        unroofed = [c for c in r.rect.inner().cells() if c not in plan.roof]
        if unroofed:
            out.append(Finding("WARN", "room-unroofed",
                               f"room {r.id} has {len(unroofed)} unroofed "
                               f"interior cell(s) - it will not hold temperature"))

    # 5b. a vent in a temperature-critical room's shell defeats it
    vents = {(t.x, t.z) for t in plan.things if (t.role or "").upper() == "VENT"}
    for r in plan.rooms:
        if r.role.lower() not in ("nursery", "coldroom", "freezer"):
            continue
        bad = [c for c in r.rect.edge_cells() if c in vents]
        if bad:
            out.append(Finding("ERROR", "vent-defeats-cooling",
                               f"room {r.id} ({r.role}) has a vent in its shell; "
                               f"it will equalise with the room next door",
                               bad[0][0], bad[0][1]))

    # 6. roof support. Vanilla drops unsupported roof; 6 cells from a support
    #    is the conventional safe span.
    supports = walls | {(t.x, t.z) for t in plan.things
                        if (t.role or "").upper() in ("PILLAR", "WALL", "WINDOW")}
    for (x, z) in plan.roof:
        if any((x + dx, z + dz) in supports
               for dx in range(-6, 7) for dz in range(-6, 7)
               if abs(dx) + abs(dz) <= 6):
            continue
        out.append(Finding("WARN", "roof-unsupported",
                           "roof cell >6 from any wall; vanilla may collapse it", x, z))

    # 7. unverified defNames - the expensive mistake
    if verified_defs is not None:
        for d in sorted(plan.defnames()):
            if d not in verified_defs:
                out.append(Finding("ERROR", "def-unverified",
                                   f"'{d}' was not found in the def dump"))

    # 8. the generator's own refusals are findings, not footnotes, and they
    #    carry their OWN level - a footprint collision is an ERROR because the
    #    thing really would have been destroyed (TEMPLATE_FOOTPRINT_IGNORES_SIZE_1).
    for r in plan.refusals:
        out.append(Finding(getattr(r, "level", "WARN"),
                           getattr(r, "code", "generator-refusal"),
                           f"{r.what}: {r.reason}", r.x, r.z))

    # 9. a plan that builds nothing is a bug, not an empty house
    if not plan.things:
        out.append(Finding("ERROR", "empty-plan", "the template placed nothing"))

    # --- RIMPLACE_ENGINE_DELTAS_1 E6 --------------------------------------
    # 10. E1's own lint: the plan's FIRST clear must cover the whole
    # footprint. `run_template` auto-injects this for every plan it builds
    # (`luaenv.run_template`), so this only ever fires for a plan assembled
    # some other way - same shape as rule 1b's footprint-collision check.
    if rect:
        first = plan.clears[0] if plan.clears else None
        covers = (first is not None and first.x <= rect.x and first.z <= rect.z
                 and first.x + first.w >= rect.x2 + 1
                 and first.z + first.h >= rect.z2 + 1)
        if not covers:
            out.append(Finding("ERROR", "footprint-not-cleared",
                               "the plan's first directive is not a CLEAR "
                               "covering its footprint (R1)"))

    # 11. every ROOM interior cell must carry a named TERRAIN entry - the
    # owner's own R2 complaint (bare ground read as unfinished).
    for r in plan.rooms:
        bare = [c for c in r.rect.inner().cells() if c not in plan.terrain]
        if bare:
            out.append(Finding("ERROR", "interior-bare-ground",
                               f"room {r.id} ({r.role}) has {len(bare)} "
                               f"interior cell(s) with no floor", *bare[0]))

    # 12. regular-grid: >=3 identical defs equally spaced on a line, AND
    # >=2 such parallel lines, in the same room - the lattice signature R3
    # names by name ("mechanical arrays are horrible").
    # Structural roles are EXPECTED to form straight, equally-spaced runs (a
    # rectangular room's own perimeter is four such lines) - this rule is
    # about furniture ("anything a person owns"), not the shell around it.
    _STRUCTURAL_ROLES = {"WALL", "DOOR", "WINDOW", "PILLAR", "FENCE", "SANDBAG"}
    for r in plan.rooms:
        in_room = [t for t in plan.things
                  if not t.overlay and r.rect.contains(t.x, t.z)
                  and (t.role or "").upper() not in _STRUCTURAL_ROLES]
        by_def: dict[str, list] = defaultdict(list)
        for t in in_room:
            by_def[t.defName].append(t)
        for defName, ts in by_def.items():
            n_lines = 0
            # horizontal runs: group by z, sort by x
            rows: dict[int, list] = defaultdict(list)
            for t in ts:
                rows[t.z].append(t.x)
            for xs in rows.values():
                if _has_equal_spaced_run(sorted(xs)):
                    n_lines += 1
            cols: dict[int, list] = defaultdict(list)
            for t in ts:
                cols[t.x].append(t.z)
            for zs in cols.values():
                if _has_equal_spaced_run(sorted(zs)):
                    n_lines += 1
            if n_lines >= 2:
                out.append(Finding("WARN", "regular-grid",
                                   f"room {r.id} ({r.role}) has {n_lines} "
                                   f"equally-spaced line(s) of '{defName}' "
                                   "- R3 bans lattices for anything a person "
                                   "owns"))

    # 13. no-secondary: a room with a primary and zero secondary-class things.
    # A secondary counts whether it is an overlay or not - a wall lamp or a
    # floor decal is exactly the "lived-in" dressing R4 wants, and excluding
    # overlays here (as the OTHER rules correctly do, to skip a decal for
    # collision purposes) produced false ERRORs on rooms whose only clutter
    # was a wall-mounted light. Primaries stay non-overlay-only: a primary is
    # a real edifice, never a decal.
    for r in plan.rooms:
        primaries = {(t.role or "").upper() for t in plan.things
                    if not t.overlay and r.rect.contains(t.x, t.z)}
        secondaries = {(t.role or "").upper() for t in plan.things
                      if r.rect.contains(t.x, t.z)}
        if primaries & _PRIMARY_ROLES and not (secondaries & _SECONDARY_ROLES):
            out.append(Finding("ERROR", "no-secondary",
                               f"room {r.id} ({r.role}) has a primary "
                               f"({sorted(primaries & _PRIMARY_ROLES)}) and zero "
                               "secondary/clutter things - R4"))

    # 14. door-centred: an exterior door at the EXACT midpoint of a wall
    # >=7 long (spec §3.1.2 - doors read as hand-placed only when offset).
    for r in plan.rooms:
        rr = r.rect
        edge = set(rr.edge_cells())
        for (dx, dz) in doors:
            if (dx, dz) not in edge:
                continue
            if dz in (rr.z, rr.z2) and rr.w >= 7:
                mid = rr.x + rr.w // 2
                if dx == mid and rr.w % 2 == 1:
                    out.append(Finding("WARN", "door-centred",
                                       f"room {r.id} door at ({dx},{dz}) sits "
                                       f"at the exact midpoint of a {rr.w}-long "
                                       "wall", dx, dz))
            elif dx in (rr.x, rr.x2) and rr.h >= 7:
                mid = rr.z + rr.h // 2
                if dz == mid and rr.h % 2 == 1:
                    out.append(Finding("WARN", "door-centred",
                                       f"room {r.id} door at ({dx},{dz}) sits "
                                       f"at the exact midpoint of a {rr.h}-long "
                                       "wall", dx, dz))

    # 15. aisle-blocked: spec §3.5's flood-fill, reimplemented here (not a
    # call into the Lua prelude's aisle_ok - lint runs on a BuildPlan with no
    # Lua runtime attached). ERROR if a primary is completely unreached by a
    # fill from the room's own doors; WARN if reachable coverage is thin.
    for r in plan.rooms:
        ok, coverage, unreached = _aisle_fill(plan, r, sizes)
        if ok is None:
            continue          # no door on this room - room-unreachable already says so
        if unreached:
            out.append(Finding("ERROR", "aisle-blocked",
                               f"room {r.id} ({r.role}) has {unreached} "
                               "primary thing(s) the door(s) cannot flood-"
                               "fill reach"))
        elif coverage < 0.45:
            out.append(Finding("WARN", "aisle-blocked",
                               f"room {r.id} ({r.role}) flood-fill reaches "
                               f"only {coverage:.0%} of its interior (<45%)"))
    return out


def _has_equal_spaced_run(coords: list[int], min_len: int = 3) -> bool:
    """True if `coords` (sorted, distinct positions along one axis) contains
    >=min_len values at a constant positive step - the lattice signature."""
    n = len(coords)
    for i in range(n - min_len + 1):
        step = coords[i + 1] - coords[i]
        if step <= 0:
            continue
        run = 2
        j = i + 1
        while j + 1 < n and coords[j + 1] - coords[j] == step:
            run += 1
            j += 1
        if run >= min_len:
            return True
    return False


# Roles a flood-fill treats as impassable - mirrors prelude.lua's
# IMPASSABLE_ROLES (rule 15 has no Lua runtime to call `ctx:aisle_ok` on, so
# this is a second, Python-side reading of the SAME spec rule; keep both in
# step if the vocabulary changes).
_IMPASSABLE_ROLES = {
    "WALL", "BED", "TABLE", "STORAGE", "SHELF_SMALL", "CRATE", "BARREL",
    "DRESSER", "WORKBENCH", "STOVE", "GENERATOR", "BATTERY", "TURRET",
    "PILLAR", "THRONE", "FORGE", "REFINERY", "REACTOR", "FABRICATOR",
    "CHARGER", "HYDRO", "FENCE", "BARRICADE", "SANDBAG", "DRUG_LAB",
    "DESK", "ANIMAL_BED", "WATER_TANK", "FOUNTAIN",
    # INHABITED_AUGMENTATION_BUILD_1 - keep in step with prelude.lua
    "CHEST", "FOOTLOCKER", "LOCKER", "TOOL_CABINET", "MACHINE", "RAIL_CAR",
    "WRECK", "WRECK_BIG", "ROCK", "SEAM", "SUPPORT", "GONK",
}
# A structural/boundary role BLOCKS the flood fill but is not itself a
# "primary" that needs a passable neighbour - a wall is not something a
# person walks up to. Without this exclusion, a second room's shared wall
# falling inside THIS room's outer rect (a carved-out office corner, say)
# reads as an unreached primary forever, since a wall cell's neighbours are
# routinely other wall cells. Measured on deepwater_cistern_hall.lua: the
# "unreached primary" was the Office's own partition wall, not a fixture.
_STRUCTURAL_IMPASSABLE = {"WALL", "DOOR", "WINDOW", "PILLAR", "FENCE",
                          "BARRICADE", "SANDBAG"}


def _aisle_fill(plan: BuildPlan, room: Room, sizes: dict | None = None):
    """-> (ok, coverage, unreached_primary_count), or (None, 0, 0) if the
    room has no door to flood-fill from.

    FOOTPRINTS, not origins (`sizes` is the defsize index lint already
    loaded): this used to mark only each thing's origin cell, so a 3x1
    ElectricStove read as passable across two of its cells and a room the
    door could not cross passed - found on the first homestead compound
    (INHABITED_AUGMENTATION_BUILD_1). Mirrors prelude.lua's aisle_ok, which
    now reads `ctx:role_covering`. Unreached is counted per THING (by
    origin), so a 3-long stove reached at one end is reached."""
    inner = room.rect.inner()
    role_at: dict[tuple[int, int], str] = {}
    owner_at: dict[tuple[int, int], tuple[int, int]] = {}
    for t in plan.things:
        if t.overlay:
            continue
        cells = None
        if sizes:
            from .defsize import footprint as _fp
            cells = _fp(t.defName, t.x, t.z, t.rot or 0, sizes)
        if cells is None:
            cells = {(t.x, t.z)}
        for c in cells:
            if inner.contains(*c):
                role_at.setdefault(c, (t.role or "").upper())
                owner_at.setdefault(c, (t.x, t.z))

    def passable(x, z):
        return role_at.get((x, z), "") not in _IMPASSABLE_ROLES

    # A DOOR sits ON the wall (rect edge), never inside `inner` - the flood
    # fill has to start from the door's INTERIOR neighbour cell, not the door
    # cell itself, or it seeds from a cell `inner.contains()` always rejects
    # and floods nothing at all. Mirrors prelude.lua's aisle_ok exactly.
    door_cells = {(t.x, t.z) for t in plan.things if (t.role or "").upper() == "DOOR"}
    if not door_cells:
        return None, 0, 0
    seeds = []
    for x in range(inner.x, inner.x2 + 1):
        if (x, inner.z2 + 1) in door_cells:
            seeds.append((x, inner.z2))
        if (x, inner.z - 1) in door_cells:
            seeds.append((x, inner.z))
    for z in range(inner.z, inner.z2 + 1):
        if (inner.x2 + 1, z) in door_cells:
            seeds.append((inner.x2, z))
        if (inner.x - 1, z) in door_cells:
            seeds.append((inner.x, z))
    if not seeds:
        return None, 0, 0     # this room's door(s) open onto another room, not `inner`
    seen = {s for s in seeds if passable(*s)}
    queue = list(seen)
    head = 0
    while head < len(queue):
        x, z = queue[head]
        head += 1
        for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nc = (x + dx, z + dz)
            if inner.contains(*nc) and nc not in seen and passable(*nc):
                seen.add(nc)
                queue.append(nc)
    cells = list(inner.cells())
    total = len(cells) or 1
    reached = sum(1 for c in cells if c in seen)
    thing_ok: dict[tuple[int, int], bool] = {}
    for c in cells:
        role = role_at.get(c, "")
        if role in _IMPASSABLE_ROLES and role not in _STRUCTURAL_IMPASSABLE:
            x, z = c
            key = owner_at[c]
            hit = any((x + dx, z + dz) in seen
                      for dx, dz in ((0, 1), (0, -1), (1, 0), (-1, 0)))
            thing_ok[key] = thing_ok.get(key, False) or hit
    unreached = sum(1 for ok in thing_ok.values() if not ok)
    return (reached / total >= 0.45 and unreached == 0), reached / total, unreached


# --------------------------------------------------------------------------- #
#  Compiling to bridge calls
# --------------------------------------------------------------------------- #
# 🔴 THESE ARE THE COMPANION'S OWN LIMITS, not chosen here. Read from
# JawaBenchTerrainTools.cs: `private const int MaxOps = 4096;` and
# `MaxCells = 70000`. A call over either is REFUSED whole, so the compiler must
# split before the bridge does — a settlement's terrain is the case that hits it.
MAX_OPS = 4096
MAX_CELLS = 70000


def _rect_cells(cells: dict) -> int:
    """How many map cells the compiled rects will touch. Only used to keep a
    single call under the companion's MaxCells."""
    return len(cells)


def _chunk_ops(ops: list[str], total_cells: int) -> list[list[str]]:
    """Split an op list so no single call exceeds the companion's MaxOps, and,
    when the rects are large, its MaxCells too.

    ⚠️ The cell bound is approximated by the cell COUNT of the source grid, not
    re-derived from each op — a plan is a house or a settlement, both far under
    70,000, and an approximation that can only split EARLIER is safe in the one
    direction that matters. If that ever stops being true the honest fix is to
    sum w*h per op, not to raise the constant.
    """
    if not ops:
        return []
    per_call = MAX_OPS
    if total_cells > MAX_CELLS:
        # keep each call's share of the cells under the bound
        per_call = max(1, int(len(ops) * MAX_CELLS / float(total_cells)))
    return [ops[i:i + per_call] for i in range(0, len(ops), per_call)]


def _rects_from_cells(cells: dict) -> list[tuple[str, list]]:
    """Greedy 2D rectangle decomposition, per defName.

    A horizontal-run-only version emitted 21 set_terrain_batch calls for one
    three-room house. That is fine for a house and ruinous for a settlement,
    where the call count is what decides whether a village takes seconds or
    minutes. Merging vertically as well cuts it to a handful.
    """
    out = []
    for defName in sorted(set(cells.values())):
        remaining = {c for c, d in cells.items() if d == defName}
        while remaining:
            x0, z0 = min(remaining, key=lambda c: (c[1], c[0]))
            # widen east
            w = 1
            while (x0 + w, z0) in remaining:
                w += 1
            # then grow north while the whole row of that width is present
            h = 1
            while all((x0 + dx, z0 + h) in remaining for dx in range(w)):
                h += 1
            for dz in range(h):
                for dx in range(w):
                    remaining.discard((x0 + dx, z0 + dz))
            out.append((defName, [x0, z0, w, h]))
    return out


def compile_calls(plan: BuildPlan, faction: str | None = None,
                  dry_run: bool = True) -> list[dict]:
    """BuildPlan -> the exact ordered jawa/* calls.

    🔑 The grouping here is forced by the bridge, not chosen: `stuff` is a
    per-CALL parameter of jawa/build_batch, so one call paints one material.

    🔴 EVERY tool here takes `ops`, and terrain/roof used to be emitted with a
    `rect` parameter that NO tool has (TEMPLATE_RECT_PARAM_NOT_ACCEPTED_1).
    4 of one dwelling's 13 compiled calls were unrunnable, taking all 112 terrain
    and 180 roof cells with them; the bridge refused loudly, which is the only
    reason it was not silent. The grammar is 'Def:x,z,w,h' joined by ';', read
    from JawaBenchTerrainTools.cs, and it carries the def PER OP — so one call
    can now paint several materials, which the old shape could not.
    """
    calls: list[dict] = []

    # E1 CLEAR, first of all - before foundation, exactly like the mapgen-time
    # path. `jawa/destroy_batch` (JawaBench.BridgeTools/JawaBenchTerrainTools.cs)
    # is the live equivalent of GenStep_RimplacePlan.ExecuteClear's Plant/Filth/
    # Item/Building sweep; it has no rock-type-aware terrain replacement, so
    # mode="all"'s "replace mined rock with its rough terrain" is UNAVAILABLE
    # live - noted on the plan rather than silently dropped, and true today
    # only because no such tool exists yet, not a permanent limitation.
    if plan.clears:
        by_mode: dict[str, list] = defaultdict(list)
        for c in plan.clears:
            by_mode[c.mode].append(f"{c.x},{c.z},{c.w},{c.h}")
        for mode, rects in sorted(by_mode.items()):
            cats = "Plant,Item,Filth,Building" if mode == "all" else "Plant,Item,Filth"
            calls.append({"tool": "jawa/destroy_batch",
                          "params": {"rects": ";".join(rects), "categories": cats}})
        if any(c.mode == "all" for c in plan.clears):
            plan.notes.append(
                "⚠️ live path: CLEAR mode=all destroyed Building-category things "
                "in its rects via jawa/destroy_batch, but did NOT replace mined "
                "rock with its rough-rock terrain (no such live tool exists) - "
                "that replacement only happens on the mapgen-time GenStep path.")

    # E2 RUN has no live equivalent: extending a line to the MAP EDGE needs
    # the real map's size, which no jawa/* tool in this pass exposes. Only the
    # mapgen-time GenStep (which has the real Map) can execute it.
    if plan.runs:
        plan.notes.append(
            f"⚠️ live path: {len(plan.runs)} RUN directive(s) were NOT compiled "
            "to any bridge call - no live tool walks a line to the map edge. "
            "RUN only executes on the mapgen-time GenStep path.")

    # E3 PAWN: only state=alive compiles live, via jawa/spawn_pawn - a corpse
    # (dead/dessicated/skeleton) needs CompRottable surgery no jawa/* tool
    # exposes yet, so those stay mapgen-only (GenStep_RimplacePlan.ExecutePawn).
    if plan.pawns:
        dead = [p for p in plan.pawns if p.state != "alive"]
        for p in plan.pawns:
            if p.state != "alive":
                continue
            calls.append({"tool": "jawa/spawn_pawn",
                          "params": {"kindDef": p.kindDef, "x": p.x, "z": p.z,
                                     "faction": "none" if p.faction == "wild" else p.faction,
                                     "count": 1}})
        if dead:
            plan.notes.append(
                f"⚠️ live path: {len(dead)} PAWN directive(s) with a corpse "
                "state were NOT compiled to any bridge call - no live tool "
                "makes a Corpse. Those only execute on the mapgen-time GenStep path.")

    # foundation first (gravship Substructure - the 1.6 third grid), then floors:
    # a floor laid on missing substructure is refused by the engine, so the
    # foundation must exist before the terrain pass runs.
    for chunk in _chunk_ops([f"{d}:{x},{z},{w},{h}"
                             for d, (x, z, w, h) in _rects_from_cells(plan.foundation)],
                            _rect_cells(plan.foundation)):
        calls.append({"tool": "jawa/set_terrain_batch",
                      "params": {"ops": ";".join(chunk), "layer": "foundation"}})

    # terrain next: floors under things, and set_terrain does not care about
    # what is standing there, while build_batch's wipeExisting does.
    for chunk in _chunk_ops([f"{d}:{x},{z},{w},{h}"
                             for d, (x, z, w, h) in _rects_from_cells(plan.terrain)],
                            _rect_cells(plan.terrain)):
        calls.append({"tool": "jawa/set_terrain_batch",
                      "params": {"ops": ";".join(chunk)}})

    # things, grouped by (def, stuff) because stuff is per-call
    groups: dict[tuple, list] = defaultdict(list)
    for t in plan.things:
        groups[(t.defName, t.stuff)].append(t)
    # 🔴 TRANSMITTERS BEFORE CONNECTORS, or the power layer is dead on arrival.
    # A connector (Cooler, most machines) binds to the nearest transmitter
    # within ConnectMaxDist=6 AT SPAWN; a transmitter appearing afterwards does
    # not retroactively claim it. Alphabetical grouping put Battery and Cooler
    # ahead of PowerConduit, so every cooler bound to nothing and read
    # `Grid excess: 0 W` even after the bus was live and the game had ticked.
    # Measured 2026-08-26; re-placing the same coolers afterwards fixed them.
    tx = netinfo.transmitters({d for d, _ in groups})
    if tx is None:
        # UNMEASURED: the def dump is unreadable, so we do NOT invent an order.
        # Previous behaviour, plus a note on the plan so nobody reads the
        # resulting layout as power-verified.
        tx = set()
        plan.notes.append("⚠️ def dump unreadable: build order NOT sorted "
                          "transmitters-first, so any power or pipe network in "
                          "this plan may spawn unbound. Re-place connectors "
                          "after the bus, or re-run with the dump present.")

    def _rank(kv):
        defName = kv[0][0]
        return (0 if defName in tx else 1, str(kv[0]))

    for (defName, stuff), ts in sorted(groups.items(), key=_rank):
        ops = [f"{defName}:{t.x},{t.z}" + (f",{t.rot}" if t.rot else "")
               for t in ts]
        for i in range(0, len(ops), MAX_OPS):
            p = {"ops": ";".join(ops[i:i + MAX_OPS])}
            if stuff:
                p["stuff"] = stuff
            if faction:
                p["faction"] = faction
            calls.append({"tool": "jawa/build_batch", "params": p})

    # roofs last: walls create no roof, and roofing before the walls exist
    # gives an unsupported span
    for chunk in _chunk_ops([f"{d}:{x},{z},{w},{h}"
                             for d, (x, z, w, h) in _rects_from_cells(plan.roof)],
                            _rect_cells(plan.roof)):
        calls.append({"tool": "jawa/set_roof_batch",
                      "params": {"ops": ";".join(chunk)}})

    # paint AFTER the things exist (owner, 2026-08-28). Building paint is the
    # vanilla PaintColorDef via jawa/paint_building — grouped by colour, cells
    # form, chunked. Floor colour goes through jawa/set_terrain_layer, which is
    # rect-only, so cells are folded into horizontal runs per colour.
    by_color: dict[str, list] = defaultdict(list)
    for t in plan.things:
        if t.paint:
            by_color[t.paint].append((t.x, t.z))
    for color, cells in sorted(by_color.items()):
        cells = sorted(set(cells))
        for i in range(0, len(cells), 300):
            calls.append({"tool": "jawa/paint_building",
                          "params": {"cells": ";".join(f"{x},{z}" for x, z in cells[i:i + 300]),
                                     "colorDef": color}})
    fc_by_color: dict[str, dict] = defaultdict(dict)
    for (x, z), color in plan.floor_color.items():
        fc_by_color[color][(x, z)] = color
    for color, cellmap in sorted(fc_by_color.items()):
        for _, (x, z, w, h) in _rects_from_cells(cellmap):
            calls.append({"tool": "jawa/set_terrain_layer",
                          "params": {"layer": "color", "rect": f"{x},{z},{w},{h}",
                                     "def": color}})

    calls.append({"tool": "jawa/map_commit",
                  "params": {"regions": True, "pathing": True,
                             "power": True, "redraw": True}})
    if dry_run:
        for c in calls:
            c["params"]["_dryRun"] = True
    return calls


def compile_flat(plan: BuildPlan) -> str:
    """BuildPlan -> the flat runtime format `GenStep_RimplacePlan` reads at
    mapgen time (src/RimMandrake/StructureInjections/Source/RimplacePlan.cs).
    Deliberately NOT JSON: RimWorldWin64_Data/Managed ships no JSON library,
    so the mapgen-time parser is plain StreamReader + string.Split, no
    dependency at all. `to_json()` stays the IR for human review and
    diffing; this is a second, disposable compile target off the same
    object, same relationship as `compile_calls()`.

    One directive per line, tab-separated, "#" comment lines ignored:
        FOOTPRINT   x  z  w  h
        CLEAR       x  z  w  h  mode(all|soft)
        FOUNDATION  x  z  defName
        TERRAIN     x  z  defName
        THING       defName  x  z  rot  stuff-or-dash
        RUN         x  z  dir(N|E|S|W)  defName  stuff-or-dash
        ROOF        x  z  defName
        PAINT       x  z  colorDefName
        FLOORCOLOR  x  z  colorDefName
        PAWN        kindDef  x  z  faction  state(alive|dead|dessicated|skeleton)
    Sections are emitted in the order the live path proved necessary
    (CLEAR before anything - RIMPLACE_ENGINE_DELTAS_1 E1 - then foundation,
    terrain, things, RUN, roof, paint, floor color, and PAWN last so a spawned
    pawn/corpse cannot be wiped by anything built after it) so a reader that
    just applies lines top-to-bottom gets that ordering for free.

    🔑 v2 (RIMPLACE_ENGINE_DELTAS_1): a reader built for v1 has no CLEAR/RUN/
    PAWN cases and would silently skip every one as an unrecognised directive
    - exactly the R1 regression this whole item exists to close. The header
    bump is the visible marker; `GenStep_RimplacePlan`/`RimplacePlan.Parse`
    additionally `Log.Warning` once per unknown directive verb it skips, so
    an old DLL replaying a new plan fails LOUD, not silently.
    """
    lines = ["# rimplace flat plan v2"]
    fp = plan.meta.get("footprint")
    # 🔑 A THIRD PARTY HOLDING ONLY THIS .txt can now read what it was baked at and
    # what it needs. The rect is already a real directive (FOOTPRINT, parsed by
    # RimplacePlan.cs and used by centerOnMap), so it was never actually missing —
    # what was missing is the FLOOR, and these comment lines carry it to whoever is
    # deciding whether this plan can be re-wired onto a different TileMutatorDef
    # footprint. Comment lines are ignored by the mapgen parser by design.
    lines.append("# template  %s (sha %s)"
                 % (plan.meta.get("template", "?"),
                    plan.meta.get("template_sha256", "?")))
    mr = plan.meta.get("min_rect")
    lines.append("# min_rect  %s   baked at %s"
                 % ("%dx%d" % (mr[0], mr[1]) if mr else "none declared",
                    "%dx%d" % (fp[2], fp[3]) if fp else "?"))
    if fp:
        lines.append(f"FOOTPRINT\t{fp[0]}\t{fp[1]}\t{fp[2]}\t{fp[3]}")
    for c in plan.clears:
        lines.append(f"CLEAR\t{c.x}\t{c.z}\t{c.w}\t{c.h}\t{c.mode}")
    for (x, z), d in sorted(plan.foundation.items()):
        lines.append(f"FOUNDATION\t{x}\t{z}\t{d}")
    for (x, z), d in sorted(plan.terrain.items()):
        lines.append(f"TERRAIN\t{x}\t{z}\t{d}")
    for t in plan.things:
        lines.append(f"THING\t{t.defName}\t{t.x}\t{t.z}\t{t.rot}\t{t.stuff or '-'}")
    for r in plan.runs:
        lines.append(f"RUN\t{r.x}\t{r.z}\t{r.dir}\t{r.defName}\t{r.stuff or '-'}")
    for (x, z), d in sorted(plan.roof.items()):
        lines.append(f"ROOF\t{x}\t{z}\t{d}")
    for t in plan.things:
        if t.paint:
            lines.append(f"PAINT\t{t.x}\t{t.z}\t{t.paint}")
    for (x, z), d in sorted(plan.floor_color.items()):
        lines.append(f"FLOORCOLOR\t{x}\t{z}\t{d}")
    for p in plan.pawns:
        lines.append(f"PAWN\t{p.kindDef}\t{p.x}\t{p.z}\t{p.faction}\t{p.state}")
    return "\n".join(lines) + "\n"


def calls_summary(calls: list[dict]) -> str:
    n = defaultdict(int)
    for c in calls:
        n[c["tool"]] += 1
    total_ops = sum(len(c["params"].get("ops", "").split(";"))
                    for c in calls if "ops" in c["params"])
    lines = [f"  {len(calls)} bridge call(s), {total_ops} build op(s)"]
    for t, k in sorted(n.items()):
        lines.append(f"    {k:>3} x {t}")
    return "\n".join(lines)
