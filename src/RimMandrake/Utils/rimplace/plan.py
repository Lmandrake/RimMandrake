"""rimplace.plan - lint a BuildPlan, draw it, and compile it to bridge calls.

Three jobs, all offline:
  lint()     find what is wrong BEFORE a game load pays for it
  render()   draw the house as text - the whole reason the edit loop is fast
  compile()  BuildPlan -> the exact jawa/* calls that would build it
"""
from __future__ import annotations

import json
from collections import defaultdict

from .core import BuildPlan, Rect

# --------------------------------------------------------------------------- #
#  Rendering
# --------------------------------------------------------------------------- #
_GLYPH = {
    "WALL": "#", "DOOR": "+", "BED": "b", "LIGHT": "*", "TABLE": "T",
    "CHAIR": "h", "STORAGE": "S", "STOVE": "K", "COOLER": "C", "HEATER": "H",
    "DECOR": "o", "BATTERY": "B", "GENERATOR": "G", "TURRET": "X",
    "SANDBAG": ",", "VENT": "v", "NEST": "n",
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
    for t in plan.things:
        g = _GLYPH.get((t.role or "").upper())
        if g is None:
            d = t.defName.lower()
            g = ("#" if "wall" in d else "+" if "door" in d else
                 "b" if "bed" in d else "?")
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


def lint(plan: BuildPlan, verified_defs: set[str] | None = None) -> list[Finding]:
    """Everything decidable without a game. Each check exists because the
    corresponding live failure is expensive or silent."""
    out: list[Finding] = []
    fp = plan.meta.get("footprint")
    rect = Rect(*fp) if fp else None

    # 1. two things in one cell - build_batch would silently wipe one
    bycell = defaultdict(list)
    for t in plan.things:
        bycell[(t.x, t.z)].append(t)
    for (x, z), ts in sorted(bycell.items()):
        if len(ts) > 1:
            names = ", ".join(t.defName for t in ts)
            out.append(Finding("ERROR", "cell-collision",
                               f"{len(ts)} things share a cell: {names}", x, z))

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
    SEALING = {"WALL", "DOOR", "COOLER", "HEATER"}
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
                        if (t.role or "").upper() in ("PILLAR", "WALL")}
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

    # 8. the generator's own refusals are findings, not footnotes
    for r in plan.refusals:
        out.append(Finding("WARN", "generator-refusal",
                           f"{r.what}: {r.reason}", r.x, r.z))

    # 9. a plan that builds nothing is a bug, not an empty house
    if not plan.things:
        out.append(Finding("ERROR", "empty-plan", "the template placed nothing"))
    return out


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

    # terrain first: floors under things, and set_terrain does not care about
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
    for (defName, stuff), ts in sorted(groups.items(), key=lambda kv: str(kv[0])):
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

    calls.append({"tool": "jawa/map_commit",
                  "params": {"regions": True, "pathing": True,
                             "power": True, "redraw": True}})
    if dry_run:
        for c in calls:
            c["params"]["_dryRun"] = True
    return calls


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
