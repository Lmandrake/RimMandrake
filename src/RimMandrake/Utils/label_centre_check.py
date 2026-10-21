"""Compare a region label's live `drawCenter` with a plan's, in a frame-independent way.

Stdlib only: imported by `world/_parity_apply_2026-10-20.py` under Windows python.exe.

## Why not a per-axis 0.01 tolerance (LABELS_SHRINK_APPLY_LIVE_SEVENTY_PERCENT, 2026-10-20)

The engine does NOT recompute `drawCenter` at load: `WorldFeature.ExposeData` scribes it
verbatim (`Scribe_Values.Look(ref drawCenter, "drawCenter")`) and nothing writes it after.
`world_features_set centerOnTile` stores `PlanetLayer.GetTileCenter(tile)` -- the MEAN OF THE
TILE'S VERTICES, so radius ~99.989, not 100. The U1 planner (`parity_fix_plans.label_plan`)
wrote `after.drawCenter` from `worldgeom` (the exported lat/long, unit vector x 100, rounded
to 4 dp). Those are two spellings of the same tile centre. Measured on the PARITY,
PARITY_QUIET and PARITY_QUIET_R2 saves (identical on all three): 57 of 71 labels differ from
the plan by more than 0.01 on some axis (max 0.178 units, Slough), but the ANGLE between them
is median 0.0045 deg, p90 0.0175 deg, max 0.109 deg (Slough; Knuckles next at 0.040), and on
71 of 71 the tile nearest the live centre is the planned `centerOnTile`.
The angular part is LongLatOf's own bias: it takes lat = asin(y / 100) on a centre whose
radius is ~99.989, so the exported latitude is short by asin(y/100) - asin(y/|c|), which
grows toward the poles -- recomputed from the saved centres it is exactly 0.1094 deg for
Slough and 0.0395 deg for Knuckles (lat ~86 deg and ~81 deg), the two the U1 readback named.

## The tolerance

Compare DIRECTIONS (radius ignored) with CENTRE_TOL_DEG = 0.4 deg. On this planet the
smallest arc between two neighbouring tile centres is 0.934 deg, so any point within 0.467
deg of tile A's centre is nearer A than any other tile: 0.4 is still a same-tile test, and
is 3.7x the worst measured spelling difference. A label on a neighbouring tile (>= 0.934 deg)
or another region (degrees to tens of degrees) fails.
"""
import math
import xml.etree.ElementTree as ET

CENTRE_TOL_DEG = 0.4
SIZE_TOL = 0.01


def _xyz(v):
    if isinstance(v, dict):
        return (float(v["x"]), float(v["y"]), float(v["z"]))
    return tuple(float(c) for c in v)


def centre_arc_deg(a, b):
    """Angle in degrees between two engine Vector3s, radius ignored."""
    a, b = _xyz(a), _xyz(b)
    na = math.sqrt(sum(c * c for c in a)); nb = math.sqrt(sum(c * c for c in b))
    if na < 1e-9 or nb < 1e-9:
        return 180.0
    d = sum(x * y for x, y in zip(a, b)) / (na * nb)
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def check_labels(plan_features, live_by_name, phase, tol_deg=CENTRE_TOL_DEG):
    """Rows where live != plan[phase]. live_by_name: name -> {drawCenter, maxDrawSizeInTiles}.
    Each row: (name, reason, detail)."""
    bad = []
    for f in plan_features:
        want = f[phase]; l = live_by_name.get(f["name"])
        if l is None:
            bad.append((f["name"], "missing live", None)); continue
        arc = centre_arc_deg(l["drawCenter"], want["drawCenter"])
        if arc > tol_deg:
            bad.append((f["name"], "centre", round(arc, 4)))
        ls = l.get("maxDrawSizeInTiles")
        if want.get("size") is not None and (ls is None or abs(float(ls) - float(want["size"])) > SIZE_TOL):
            bad.append((f["name"], "size", (l["maxDrawSizeInTiles"], want["size"])))
    return bad


def read_save_features(path):
    """name -> {uniqueID, drawCenter (x,y,z), maxDrawSizeInTiles} from a .rws, read-only."""
    root = ET.parse(path).getroot()
    out = {}
    for li in root.find(".//world/features").iter("li"):
        dc = li.find("drawCenter")
        if dc is None:
            continue
        sz = li.find("maxDrawSizeInTiles")
        out[li.find("name").text] = {
            "uniqueID": int(li.find("uniqueID").text),
            "drawCenter": tuple(float(x) for x in dc.text.strip("()").split(",")),
            "maxDrawSizeInTiles": float(sz.text) if sz is not None else None}
    return out
