#!/usr/bin/env python3
"""Per-pawn holds of a station on a COLONY stage (RIMMANDRAKE_BUILD_COLONY_STATION_HOLDS_BYSTANDERS_BY_AREA).

A colony map holds a real colony, so its bystanders cannot be removed (a stage map holds the cast only). This module holds
each bystander pawn and animal out of a station by an allowed area that excludes the station plus its margin, and sets the
things of the station forbidden. At the close it gives each pawn back the area it had. A pawn that the area cannot bind
(drafted, in a mental state, no player settings, or the game refused) is NAMED, never counted as held.

Pure: no game. `call(tool, **args) -> dict` is the bridge door (scene `_call`). Tools used, all existing except the last:
jawa/list_pawns, jawa/new_allowed_area, jawa/paint_area, jawa/set_player_settings, and jawa/set_forbidden (this item).
Promises and tests: src/RimMandrake/bridgetools/selftest_stage_colony_holds.py."""

LIST_PAWNS, NEW_AREA, PAINT, SETTINGS, FORBID = ("jawa/list_pawns", "jawa/new_allowed_area", "jawa/paint_area",
                                                 "jawa/set_player_settings", "jawa/set_forbidden")
AREA_LABEL = "RM_StationHold"
CANNOT_BIND = (("drafted", "drafted"), ("mentalState", "in a mental state"), ("inMentalState", "in a mental state"))


class HoldFault(Exception):
    """The hold could not be made, or could not be read back. `name` says which; nothing is claimed held."""

    def __init__(self, name, why):
        super().__init__("%s: %s" % (name, why))
        self.name, self.why = name, why


def free_rects(map_size, rect, margin):
    """The rectangles (x, z, w, h) that cover every map cell outside `rect` grown by `margin`, clamped to the map."""
    mx, mz = map_size
    x0, z0 = max(0, rect[0] - margin), max(0, rect[1] - margin)
    x1, z1 = min(mx, rect[0] + rect[2] + margin), min(mz, rect[1] + rect[3] + margin)
    out = [(0, 0, mx, z0),                        # south band, full width
           (0, z1, mx, mz - z1),                  # north band, full width
           (0, z0, x0, z1 - z0),                  # west of the grown station
           (x1, z0, mx - x1, z1 - z0)]            # east of the grown station
    return [r for r in out if r[2] > 0 and r[3] > 0]


def ops(rects):
    return ";".join("%d,%d,%d,%d" % tuple(r) for r in rects)


def _why_not_bindable(p):
    if p.get("playerSettings") is False or p.get("hasPlayerSettings") is False:
        return "has no player settings"
    for key, text in CANNOT_BIND:
        if p.get(key):
            return text
    return None


def hold(call, map_size, rect, margin, cast=()):
    """Hold every pawn on the map that is not cast out of rect+margin, and set the station's things forbidden.
    -> a hold: {"area", "held": [{id, was}], "unbound": [{id, why}], "forbidden": n}. Raises HoldFault with nothing half-made
    that the caller cannot undo with release(hold)."""
    r = call(LIST_PAWNS)
    if r.get("success") is False or not isinstance(r.get("pawns"), list):
        raise HoldFault("COULD_NOT_LOOK", "the pawns of the colony map could not be read: %s" % str(r)[:200])
    rects = free_rects(map_size, rect, margin)
    if not rects:
        raise HoldFault("NO_FREE_CELLS", "station %s with margin %d leaves no cell of the %dx%d map to stand in" % (tuple(rect), margin, *map_size))
    made = call(NEW_AREA, label=AREA_LABEL)
    if made.get("success") is not True:
        raise HoldFault("NO_AREA", "the allowed area %s could not be made: %s" % (AREA_LABEL, made.get("message") or made))
    p = call(PAINT, area=AREA_LABEL, ops=ops(rects), value=True, clearAreaFirst=True)
    if p.get("success") is not True or p.get("failedVerify") or p.get("outOfBounds"):
        raise HoldFault("AREA_NOT_PAINTED", "the area %s did not read back as painted: %s" % (AREA_LABEL, str(p)[:200]))
    h = {"area": AREA_LABEL, "held": [], "unbound": [], "forbidden": 0, "rects": rects}
    for pawn in r["pawns"]:
        pid = pawn.get("id")
        if pid in cast:
            continue
        why = _why_not_bindable(pawn)
        if why:
            h["unbound"].append({"id": pid, "why": why})
            continue
        was = call(SETTINGS, pawnId=pid)
        if was.get("success") is not True:
            h["unbound"].append({"id": pid, "why": "its area could not be read: %s" % (was.get("message") or was)})
            continue
        got = call(SETTINGS, pawnId=pid, area=AREA_LABEL)
        if got.get("success") is not True or got.get("area") != AREA_LABEL:
            h["unbound"].append({"id": pid, "why": "the game did not take the area (read back %r)" % (got.get("area"),)})
            continue
        h["held"].append({"id": pid, "was": was.get("area")})
    f = call(FORBID, rect="%d,%d,%d,%d" % tuple(rect), forbidden=True)
    if f.get("success") is not True or f.get("failedVerify"):
        h["unbound"].append({"id": "things of station %s" % (tuple(rect),), "why": "not all set forbidden: %s" % (f.get("message") or f)})
    else:
        h["forbidden"] = f.get("changed", 0)
    return h


def release(call, h, rect):
    """Give each held pawn back its own area, the station's things back their own state. -> lines; a pawn not restored is named."""
    lines = []
    for p in h["held"]:
        r = call(SETTINGS, pawnId=p["id"], area=p["was"] or "none")
        if r.get("success") is not True or r.get("area") != p["was"]:
            lines.append("NOT RESTORED: pawn %s should be on area %r and reads %r" % (p["id"], p["was"], r.get("area")))
    f = call(FORBID, rect="%d,%d,%d,%d" % tuple(rect), forbidden=False)
    if f.get("success") is not True:
        lines.append("NOT RESTORED: the things of station %s are still forbidden: %s" % (tuple(rect), f.get("message") or f))
    c = call(PAINT, area=h["area"], ops=ops(h["rects"]), value=False)
    if c.get("success") is not True:
        lines.append("NOT RESTORED: the area %s was not cleared: %s" % (h["area"], c.get("message") or c))
    return lines


def receipt_line(sid, h):
    """The `shared map` line of the receipt: what is held, and each pawn that is not."""
    s = "shared map: station %s held %d pawn(s) out by area %s and set %d thing(s) forbidden" % (sid, len(h["held"]), h["area"], h["forbidden"])
    if h["unbound"]:
        s += "; NOT HELD: " + ", ".join("%s (%s)" % (u["id"], u["why"]) for u in h["unbound"])
    return s
