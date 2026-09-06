#!/usr/bin/env python3
"""mapgen_v0.py -- MACRO_GENERATOR_V0_1: the CHOOSER + terrain grid.

Implements design/RimMandrake/map_generator_chooser_spec.md. The chooser
(`plan()`) reads a biome sheet's field 6 (hard bans) and field 8 (inhabited
objects / nouns) plus a seed and writes ONE PLAN (schema in the spec's
section A). `validate()` is the spec's section-D failure-mode tests as
code. `grid()` paints a defName-per-cell terrain grid from the plan using
`scatter.py` primitives, matching the spec's per-landform recipe (a
plateau is a raised blob with a rim band, a canyon is a walk widened with
blobs, a crater is radial_field + rim_band, a dry lake is a low blob of a
distinct terrain). `gates()` is an offline connectivity / buildable-area
check (rule 8) computed on the grid alone, no game.

Deliberately NOT done here (see the spec's section E and the item's "not
chasing"): structures, residents, dressing, micro texture, the LLM plan
author, world-tile targeting. The plan's `anchor.holds` and `history` name
nouns; nothing is built.
"""
import argparse
import glob
import json
import math
import os
import random
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import scatter  # noqa: E402

_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
CORPUS_STATS_PATH = os.path.join(
    _REPO_ROOT, "research", "RimMandrake", "reference", "corpus_map_stats.md")
BIOMES_DIR = os.path.join(
    _REPO_ROOT, "design", "Jawa", "worldbuilding", "biomes")
DUMP_DIR = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
            "RimWorld by Ludeon Studios/DefDump")

# --------------------------------------------------------------- vocabulary
GL_IDS = ["DesertPlateau", "Badlands", "Canyon", "Crater", "Rift", "Gorge",
          "Sinkhole", "Caldera", "Cirque", "LoneMountain", "SecludedValley"]
VANILLA_IDS = ["DryLake", "Oasis", "Valley", "Coast", "Cove", "Lake",
               "Peninsula", "CoastalIsland"]
ALL_IDS = GL_IDS + VANILLA_IDS
LINEAR_IDS = {"Canyon", "Gorge", "Rift", "Badlands"}
COASTAL_IDS = {"Coast", "Cove", "Peninsula", "CoastalIsland"}
WIND_GRAIN_DEG = 60  # UNKNOWN: the sheets name a wind grain but no numeric
                      # heading is recorded anywhere read for this item; a
                      # fixed constant satisfies rule 11's "one 30-degree
                      # band" test without inventing a canon value.

HYDRO_KINDS = {"none", "dry_riverbed", "salt_pan", "brine_seep", "spring",
               "river", "delta", "coast_inlet"}

FOOTPRINT_RANGE = {
    "DesertPlateau": (0.30, 0.55), "Badlands": (0.30, 0.55),
    "Canyon": (0.15, 0.30), "Gorge": (0.15, 0.30), "Rift": (0.15, 0.30),
    "Crater": (0.12, 0.35), "Caldera": (0.12, 0.35), "Sinkhole": (0.12, 0.35),
    "Cirque": (0.12, 0.35),
    "LoneMountain": (0.10, 0.25),
    "SecludedValley": (0.35, 0.60), "Valley": (0.35, 0.60),
    "DryLake": (0.15, 0.40), "Oasis": (0.15, 0.40), "Lake": (0.15, 0.40),
    "Coast": (0.30, 0.60), "Cove": (0.30, 0.60), "Peninsula": (0.30, 0.60),
    "CoastalIsland": (0.30, 0.60),
}

ANCHOR_TABLE = {
    "DesertPlateau": ["rim", "cliff_foot"],
    "Badlands": ["table", "mouth"],
    "Canyon": ["head", "narrows"],
    "Gorge": ["rim_over_narrows", "floor_wide_end"],
    "Rift": ["floor_centre", "shoulder"],
    "Crater": ["ring_centre", "rim_breach"],
    "Caldera": ["ring_centre", "rim_breach"],
    "Sinkhole": ["lip", "pit_floor"],
    "Cirque": ["headwall", "threshold"],
    "LoneMountain": ["lee_foot", "flank_shelf"],
    "SecludedValley": ["valley_end", "neck"],
    "Valley": ["valley_end", "neck"],
    "DryLake": ["centre", "inlet_shore"],
    "Oasis": ["water_edge"],
    "Lake": ["centre", "inlet_shore"],  # UNKNOWN: rule-3 table only lists
                                         # DryLake explicitly; "Lake" is
                                         # given the same two positions as
                                         # its wet twin -- closest reading.
    "Coast": ["tip_or_island", "inlet_head"],
    "Cove": ["tip_or_island", "inlet_head"],
    "Peninsula": ["tip_or_island", "inlet_head"],
    "CoastalIsland": ["tip_or_island", "inlet_head"],
}

# rule 2: field-8 noun lexicon -> weight
NOUN_TABLE = [
    (r"canyon|gorge|gulch|ravine", ["Canyon", "Gorge"]),
    (r"cave|cavern|throat|sinkhole|pit", ["Sinkhole", "Rift"]),
    (r"ridge|crag|isolated rock|rock island|mountain", ["LoneMountain", "DesertPlateau"]),
    (r"plateau|mesa|table|shelf|cliff", ["DesertPlateau", "Cirque"]),
    (r"crater|blast|vitrified|impact|wreck fell|debris fall", ["Crater", "Caldera"]),
    (r"salt|pan|basin|dead river|lakebed|pool", ["DryLake"]),
    (r"seep|spring|oasis|dew", ["Oasis"]),
    (r"valley|secluded|hidden", ["SecludedValley", "Valley"]),
    (r"dune|scour|badland|gully|yardang", ["Badlands"]),
    (r"coast|shore|bay|headland|sea", ["Coast", "Cove", "Peninsula", "CoastalIsland"]),
]

# rule 2: field-6 ban lexicon -> removed landforms ([] = no landform removed)
BAN_TABLE = [
    (r"no standing (surface )?water|no potable|no water\b|no liquid water",
     ["Oasis", "Lake", "Coast", "Cove", "Peninsula", "CoastalIsland"]),
    (r"no geothermal|no volcanism|no vents", ["Caldera"]),
    (r"no abundant shade|no cover|no relief", ["Cirque", "SecludedValley", "Gorge"]),
    (r"no open sand", ["Badlands"]),
    (r"no roads", []),
]

SHEET_TO_BIOME = {
    "desert.md": "Desert",
    "arid_shrubland.md": "AridShrubland",
    "deep_desert.md": "ExtremeDesert",
    "wasteland.md": "Wasteland",
}

COMMON_NOUN = {
    "DesertPlateau": "plateau", "Badlands": "badlands", "Canyon": "canyon",
    "Gorge": "gorge", "Rift": "rift", "Crater": "crater", "Caldera": "caldera",
    "Sinkhole": "sinkhole", "Cirque": "cirque", "LoneMountain": "lone rock",
    "SecludedValley": "hidden valley", "Valley": "valley",
    "DryLake": "dry lakebed", "Oasis": "oasis", "Lake": "still lake",
    "Coast": "coastline", "Cove": "cove", "Peninsula": "headland",
    "CoastalIsland": "island",
}

LANDFORM_DELETION_TEXT = {
    "DesertPlateau": "any relief outside the plateau footprint",
    "Badlands": "any flat ground untouched by a gully",
    "Canyon": "any relief outside the canyon walls",
    "Gorge": "a second channel or branch",
    "Rift": "relief outside the rift shoulders",
    "Crater": "a second impact ring",
    "Caldera": "a second vent or ring",
    "Sinkhole": "a second throat",
    "Cirque": "an opening on more than one side",
    "LoneMountain": "a second rock mass",
    "SecludedValley": "a second entrance",
    "Valley": "a second watercourse",
    "DryLake": "a second basin or outflow",
    "Oasis": "a second water source",
    "Lake": "a second standing body",
    "Coast": "inland water",
    "Cove": "a second bay",
    "Peninsula": "a second headland",
    "CoastalIsland": "a second island",
}

HISTORY_NOUNS = ["wreck", "farmstead", "salt works", "tree-road", "holding",
                  "bone-field", "trench", "canal", "waystation", "hedge-fort",
                  "moisture farm", "herder camp", "rock shelter", "cavern",
                  "road", "silverbole stand", "rib-vault", "caravanserai"]

LANDFORM_CATEGORY = {
    "DesertPlateau": "raised_blob", "LoneMountain": "raised_blob", "Cirque": "raised_blob",
    "Badlands": "carved_line", "Canyon": "carved_line", "Gorge": "carved_line",
    "Rift": "carved_line", "SecludedValley": "carved_line", "Valley": "carved_line",
    "Crater": "radial", "Caldera": "radial", "Sinkhole": "radial",
    "DryLake": "basin", "Oasis": "basin", "Lake": "basin",
    "Coast": "coastal", "Cove": "coastal", "Peninsula": "coastal", "CoastalIsland": "coastal",
}


# --------------------------------------------------------------- sheet parse
def _section(md_text, n):
    """Return the whole markdown body of "## N. ..." up to the next "## N+"."""
    m = re.search(r"(?ms)^##\s+%d\.\s.*?(?=^##\s+\d+\.|\Z)" % n, md_text)
    return m.group(0) if m else ""


def _parse_numbered_list(section_text):
    body = re.sub(r"^##.*\n", "", section_text, count=1)
    parts = re.split(r"\n(?=\d+\.\s)", body.strip())
    items = []
    for p in parts:
        m = re.match(r"(\d+)\.\s+(.*)", p, re.S)
        if m:
            idx = int(m.group(1))
            txt = re.sub(r"\s+", " ", m.group(2)).strip()
            items.append((idx, txt))
    return items


def _split_bullets(section_text):
    body = re.sub(r"^##.*\n", "", section_text, count=1)
    parts = re.split(r"\n(?=-\s)", body.strip())
    bullets = []
    for p in parts:
        p = p.strip()
        if p.startswith("-"):
            txt = re.sub(r"\s+", " ", p[1:]).strip()
            if txt:
                bullets.append(txt)
    return bullets


def _short(text, limit=90):
    text = re.sub(r"[*_`]", "", text)
    text = re.sub(r"^🔴\s*|^🔑\s*|^⭐\s*|^⛔\s*", "", text)
    return text[:limit].strip()


# --------------------------------------------------------- calibration data
def _load_calibration(stats_path):
    text = open(stats_path, encoding="utf-8").read()
    m = re.search(r"(?ms)^## By size bucket.*?(?=^## )", text)
    section = m.group(0) if m else text
    metric_key_map = {
        "region count": "region_count",
        "largest-region fraction of map": "largest_region_fraction",
        "perimeter/area, mean over regions": "perimeter_area_mean",
        "openness (top-3 hash fraction)": "openness_top3",
        "openness std across 25x25 windows": "openness_std_25",
        "distinct terrain hashes": "distinct_terrains",
    }
    buckets = {"250": {}, "275": {}, "300": {}, "325+": {}, "400+": {}}
    blocks = re.split(r"\n(?=- \*\*)", section)
    for block in blocks:
        mh = re.match(r"- \*\*(.+?)\*\*", block)
        if not mh:
            continue
        key = metric_key_map.get(mh.group(1).strip())
        if not key:
            continue
        for bm in re.finditer(
                r"(250|275|300|325\+|400\+):\s*min=([\d.]+)\s*p50=[\d.]+\s*max=([\d.]+)",
                block):
            b, lo, hi = bm.groups()
            buckets[b][key] = [float(lo), float(hi)]
    return buckets


CALIBRATION = _load_calibration(CORPUS_STATS_PATH)


def _bucket_for_size(size):
    if size <= 262:
        return "250"
    if size <= 287:
        return "275"
    if size <= 312:
        return "300"
    if size <= 362:
        return "325+"
    return "400+"


# ------------------------------------------------------------- def dump
def _load_terrain_defnames():
    captures = sorted(glob.glob(os.path.join(DUMP_DIR, "captures", "*")))
    for cand in reversed(captures):
        p = os.path.join(cand, "defs", "TerrainDef.json")
        if os.path.isfile(p):
            d = json.load(open(p, encoding="utf-8"))
            return {x["defName"] for x in d["defs"]}
    direct = os.path.join(DUMP_DIR, "defs", "TerrainDef.json")
    if os.path.isfile(direct):
        d = json.load(open(direct, encoding="utf-8"))
        return {x["defName"] for x in d["defs"]}
    return set()


# --------------------------------------------------------------- the chooser
def _eligible_landforms(field6_text, field8_text, tile):
    weights = {i: 0 for i in ALL_IDS}
    for bullet in _split_bullets(field8_text):
        matched = False
        for rx, ids in NOUN_TABLE:
            if re.search(rx, bullet, re.I):
                matched = True
                for lf in ids:
                    weights[lf] += 1
        if not matched:
            print("UNMATCHED field-8 bullet: %s" % bullet[:80], file=sys.stderr)

    items = _parse_numbered_list(field6_text)
    removed = set()
    matched_bans = []
    for idx, text in items:
        for rx, ids in BAN_TABLE:
            if re.search(rx, text, re.I):
                removed.update(ids)
                matched_bans.append((idx, text))

    if not tile.get("has_coast"):
        removed.update(COASTAL_IDS)
    if not (tile.get("has_river") or tile.get("has_coast")):
        removed.update(["Valley", "Oasis"])

    survivors = [i for i in ALL_IDS if i not in removed and weights[i] > 0]
    return survivors, weights, matched_bans, items


def _wind_grain(field9_text):
    if re.search(r"yardang|wind grain|superrotating wind", field9_text, re.I):
        return WIND_GRAIN_DEG
    return None


def _anchor_cell_frac(position, rng):
    lo, hi = 0.12, 0.88
    p = position
    if any(k in p for k in ("centre", "table", "headwall", "floor_centre", "ring_centre")):
        x, y = rng.uniform(0.42, 0.58), rng.uniform(0.42, 0.58)
    elif any(k in p for k in ("rim", "lip", "shoulder", "breach", "cliff")):
        ang = rng.uniform(0, 2 * math.pi)
        x, y = 0.5 + 0.3 * math.cos(ang), 0.5 + 0.3 * math.sin(ang)
    elif any(k in p for k in ("head", "neck", "mouth", "inlet", "valley_end", "water_edge")):
        edge = rng.choice(["N", "S", "E", "W"])
        d = rng.uniform(0.15, 0.25)
        x, y = {"N": (rng.uniform(0.3, 0.7), d), "S": (rng.uniform(0.3, 0.7), 1 - d),
                 "W": (d, rng.uniform(0.3, 0.7)), "E": (1 - d, rng.uniform(0.3, 0.7))}[edge]
    else:
        x, y = rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)
    return round(min(max(x, lo), hi), 3), round(min(max(y, lo), hi), 3)


def _anchor_holds(field8_text, rng):
    bullets = _split_bullets(field8_text) or ["this ground"]
    nouns = []
    for n in HISTORY_NOUNS:
        if n in field8_text.lower():
            nouns.append(n)
    if nouns:
        return "the abandoned %s" % rng.choice(nouns)
    return "a bare marker on " + _short(rng.choice(bullets), 40).lower()


def _choose_hydrology(landform, field6_text, tile, rng):
    water_restricted = bool(re.search(
        r"no standing (surface )?water|no potable|no water\b|no liquid water",
        field6_text, re.I))
    if landform == "DryLake":
        kind = "delta" if tile.get("has_river") else "salt_pan"
    elif landform == "Lake":
        kind = "river" if tile.get("has_river") else "spring"
    elif landform == "Oasis":
        kind = "spring"
    elif landform in COASTAL_IDS:
        kind = "coast_inlet"
    elif landform in ("Valley", "SecludedValley"):
        kind = "river" if tile.get("has_river") else "none"
    else:
        options = ["none", "dry_riverbed"]
        options += (["salt_pan", "brine_seep"] if water_restricted else ["spring"])
        kind = rng.choice(options)
    if kind in ("river", "delta", "coast_inlet") and not (
            tile.get("has_river") or tile.get("has_coast")):
        kind = "none"
    if kind == "none":
        cause = "none, because the %s sits far from any standing or flowing water" % landform
    else:
        cause = "the %s is what the %s's own relief produces" % (
            kind.replace("_", " "), landform)
    return kind, cause


def _build_premise(landform, position, rng):
    noun = COMMON_NOUN[landform]
    templates = [
        "A %s dominates the map; the only way through is at the %s.",
        "One %s cuts the ground, and everything answers to the %s.",
        "A %s shapes the whole map, anchored on the %s.",
    ]
    t = rng.choice(templates)
    return t % (noun, position.replace("_", " "))


def _build_history(field8_text, no_roads, rng):
    low = field8_text.lower()
    present = [n for n in HISTORY_NOUNS if n in low and not (no_roads and n == "road")]
    noun = rng.choice(present) if present else "holding"
    reasons = ["its people moved on", "the water moved away",
               "the wind buried what was left", "the route shifted"]
    return "A %s stood here until %s." % (noun, rng.choice(reasons))


def _build_deletions(landform, field6_text, matched_bans, rng):
    items = _parse_numbered_list(field6_text)
    seen = set()
    sheet_dels = []
    for idx, text in matched_bans:
        if idx not in seen:
            seen.add(idx)
            sheet_dels.append({"forbid": _short(text), "source": "sheet:6.%d" % idx})
    if len(sheet_dels) < 2:
        keywords = ("lush", "fire", "burn", "water", "rot", "decay", "green", "relief", "shade")
        for idx, text in items:
            if idx in seen:
                continue
            if any(k in text.lower() for k in keywords):
                sheet_dels.append({"forbid": _short(text), "source": "sheet:6.%d" % idx})
                seen.add(idx)
            if len(sheet_dels) >= 2:
                break
    if not sheet_dels and items:
        idx, text = items[0]
        sheet_dels.append({"forbid": _short(text), "source": "sheet:6.%d" % idx})

    dels = sheet_dels[:2]
    dels.append({"forbid": LANDFORM_DELETION_TEXT.get(landform, "a second instance of the landform"),
                 "source": "landform"})
    dels.append({"forbid": "a second %s or feature the premise does not mention" % COMMON_NOUN[landform],
                 "source": "premise"})
    while len(dels) < 3:
        dels.append({"forbid": "any dressing outside what the anchor names", "source": "premise"})
    return dels


def plan(biome_sheet_path, seed, tile=None, map_size=250):
    """The CHOOSER. Returns one PLAN dict per the spec's section-A schema."""
    tile = dict(tile or {})
    text = open(biome_sheet_path, encoding="utf-8").read()
    field6 = _section(text, 6)
    field8 = _section(text, 8)
    field9 = _section(text, 9)
    sheet_name = os.path.basename(biome_sheet_path)
    biome = SHEET_TO_BIOME.get(sheet_name, os.path.splitext(sheet_name)[0])

    survivors, weights, matched_bans, _items = _eligible_landforms(field6, field8, tile)
    no_roads = bool(re.search(r"no roads", field6, re.I) or re.search(r"no roads", field8, re.I))

    rng = random.Random(seed)
    if not survivors:
        print("WARN sheet_narrow: 0 landforms survive; forcing DesertPlateau fallback",
              file=sys.stderr)
        survivors = ["DesertPlateau"]
        weights["DesertPlateau"] = 1
    elif len(survivors) < 4:
        print("WARN sheet_narrow: %d landforms" % len(survivors), file=sys.stderr)

    total = sum(weights[i] for i in survivors)
    r = rng.uniform(0, total)
    upto, chosen = 0.0, survivors[-1]
    for i in survivors:
        upto += weights[i]
        if r <= upto:
            chosen = i
            break
    source = "gl" if chosen in GL_IDS else "vanilla"

    lo, hi = FOOTPRINT_RANGE[chosen]
    footprint = round(rng.uniform(lo, hi), 3)
    grain = _wind_grain(field9)
    if chosen in LINEAR_IDS and grain is not None:
        orientation = int(grain + rng.uniform(-15, 15)) % 360
    else:
        orientation = rng.randrange(0, 360)
    relief = (rng.choice(["mid", "high"]) if chosen in ("Crater", "Sinkhole", "Caldera")
              else rng.choice(["low", "mid", "high"]))

    position = rng.choice(ANCHOR_TABLE[chosen])
    cell_frac = _anchor_cell_frac(position, rng)
    holds = _anchor_holds(field8, rng)

    hydro_kind, hydro_cause = _choose_hydrology(chosen, field6, tile, rng)
    history = _build_history(field8, no_roads, rng)
    premise = _build_premise(chosen, position, rng)
    deletions = _build_deletions(chosen, field6, matched_bans, rng)

    bucket = _bucket_for_size(map_size)
    calib = {"bucket": bucket}
    calib.update(CALIBRATION.get(bucket, {}))

    return {
        "schema_version": 1,
        "seed": seed,
        "biome": biome,
        "sheet": sheet_name,
        "map_size": map_size,
        "premise": premise,
        "landform": {"id": chosen, "source": source},
        "landform_params": {"footprint_fraction": footprint,
                              "orientation_deg": orientation,
                              "relief_class": relief},
        "hydrology": {"kind": hydro_kind, "cause": hydro_cause},
        "anchor": {"position": position, "cell_frac": list(cell_frac), "holds": holds},
        "history": history,
        "deletions": deletions,
        "calibration": calib,
    }


# ------------------------------------------------------------------ validate
def validate(plan_dict):
    """The spec's section-D failure-mode tests, as code. Returns a list of
    error strings; empty means the plan may be rendered."""
    errs = []
    p = plan_dict
    if p.get("schema_version") != 1:
        return ["unknown schema_version %r" % p.get("schema_version")]

    lf = p.get("landform", {}) if isinstance(p.get("landform"), dict) else {}
    lf_id = lf.get("id")
    if not isinstance(lf_id, str):
        errs.append("rule1/5: landform.id must be a single string, got %r" % (lf_id,))
        lf_id = None
    elif lf_id not in ALL_IDS:
        errs.append("rule1: landform.id '%s' not in closed vocabulary" % lf_id)
        lf_id = None
    else:
        expect = "gl" if lf_id in GL_IDS else "vanilla"
        if lf.get("source") != expect:
            errs.append("rule1: landform.source mismatch for %s" % lf_id)

    params = p.get("landform_params", {}) if isinstance(p.get("landform_params"), dict) else {}
    if lf_id and lf_id in FOOTPRINT_RANGE:
        lo, hi = FOOTPRINT_RANGE[lf_id]
        ff = params.get("footprint_fraction")
        if not isinstance(ff, (int, float)) or not (lo - 1e-9 <= ff <= hi + 1e-9):
            errs.append("rule10: footprint_fraction %r out of range %s for %s" % (ff, (lo, hi), lf_id))
    od = params.get("orientation_deg")
    if not isinstance(od, int) or not (0 <= od <= 359):
        errs.append("rule: orientation_deg must be an int in 0-359")
    if params.get("relief_class") not in ("low", "mid", "high"):
        errs.append("rule: relief_class invalid")

    hydro = p.get("hydrology", {}) if isinstance(p.get("hydrology"), dict) else {}
    kind = hydro.get("kind")
    if not isinstance(kind, str) or kind not in HYDRO_KINDS:
        errs.append("rule5: hydrology.kind must be one scalar from the enum, got %r" % (kind,))
        kind = None
    cause = hydro.get("cause")
    if not isinstance(cause, str) or not cause.strip():
        errs.append("rule4: hydrology.cause missing/empty")
    elif kind == "none":
        if not cause.startswith("none, because"):
            errs.append("rule4: kind=none cause must start with 'none, because'")
    elif kind:
        hist = p.get("history", "") if isinstance(p.get("history"), str) else ""
        hist_words = set(re.findall(r"[a-zA-Z]{4,}", hist.lower()))
        ok = (lf_id and lf_id.lower() in cause.lower()) or any(
            w in cause.lower() for w in hist_words)
        if not ok:
            errs.append("rule4: cause names neither the landform nor a history word")

    anchor = p.get("anchor", {}) if isinstance(p.get("anchor"), dict) else {}
    pos = anchor.get("position")
    if not isinstance(pos, str):
        errs.append("rule3/5: anchor.position must be a single string, got %r" % (pos,))
    elif lf_id and lf_id in ANCHOR_TABLE and pos not in ANCHOR_TABLE[lf_id]:
        errs.append("rule3: anchor.position '%s' not valid for %s" % (pos, lf_id))
    cf = anchor.get("cell_frac")
    if not (isinstance(cf, (list, tuple)) and len(cf) == 2
            and all(isinstance(v, (int, float)) for v in cf)):
        errs.append("rule: anchor.cell_frac malformed, got %r" % (cf,))
    elif not (0.12 - 1e-9 <= cf[0] <= 0.88 + 1e-9 and 0.12 - 1e-9 <= cf[1] <= 0.88 + 1e-9):
        errs.append("rule3: anchor.cell_frac within 0.12 of an edge: %r" % (cf,))
    if not isinstance(anchor.get("holds"), str) or not anchor.get("holds", "").strip():
        errs.append("rule: anchor.holds missing")

    if not isinstance(p.get("history"), str) or not p.get("history", "").strip():
        errs.append("rule9: history missing")

    dels = p.get("deletions")
    if not isinstance(dels, list) or len(dels) < 3:
        errs.append("rule6: deletions must be a list with >=3 entries, got %r" % (dels,))
    else:
        has_premise = False
        for d in dels:
            if not isinstance(d, dict) or "forbid" not in d or "source" not in d:
                errs.append("rule6: deletion entry missing forbid/source: %r" % (d,))
                continue
            src = d["source"]
            if src == "premise":
                has_premise = True
            elif src == "landform":
                pass
            elif not re.match(r"^sheet:6\.\d+$", src or ""):
                errs.append("rule6: deletion source '%s' not tagged sheet:6.n/landform/premise" % src)
        if not has_premise:
            errs.append("rule6: no premise-sourced deletion entry")

    premise = p.get("premise", "")
    if isinstance(premise, str) and lf_id:
        hitgroups = set()
        for rx, ids in NOUN_TABLE:
            if re.search(rx, premise, re.I):
                hitgroups.add(tuple(sorted(ids)))
        if len(hitgroups) > 1:
            errs.append("rule5: premise contains more than one landform noun group: %r" % premise)

    calib = p.get("calibration", {}) if isinstance(p.get("calibration"), dict) else {}
    for k in ("bucket", "region_count", "largest_region_fraction", "perimeter_area_mean",
              "openness_top3", "openness_std_25", "distinct_terrains"):
        if k not in calib:
            errs.append("calibration missing key %s" % k)

    return errs


# ---------------------------------------------------------------------- grid
def _make_plain(size, seed):
    grid_rows = [["Sand"] * size for _ in range(size)]
    for z in range(size):
        row = grid_rows[z]
        for x in range(size):
            n = scatter.fbm(x, z, seed=seed, octaves=3, scale=16.0)
            if n > 0.60:
                row[x] = "Gravel"
            elif n < 0.32:
                row[x] = "SoftSand"
    return grid_rows


def _paint(grid_rows, cells, terrain, size):
    for item in cells:
        x, z = item[0], item[1]
        if 0 <= x < size and 0 <= z < size:
            grid_rows[int(z)][int(x)] = terrain


def _line_endpoints(cx, cy, length, rot, size):
    dx, dy = math.cos(rot), math.sin(rot)
    half = length / 2.0
    x0, y0 = cx - dx * half, cy - dy * half
    x1, y1 = cx + dx * half, cy + dy * half
    m = size * 0.06
    clamp = lambda v: min(max(v, m), size - m)
    return clamp(x0), clamp(y0), clamp(x1), clamp(y1)


def _edge_from_orientation(deg):
    d = deg % 360
    if 45 <= d < 135:
        return "S"
    if 135 <= d < 225:
        return "W"
    if 225 <= d < 315:
        return "N"
    return "E"


def _dist_from_edge(x, z, edge, size):
    if edge == "N":
        return z
    if edge == "S":
        return size - 1 - z
    if edge == "W":
        return x
    return size - 1 - x


def _push_point(cx, cy, edge, radius, size):
    if edge == "N":
        return cx, max(radius, cy - radius)
    if edge == "S":
        return cx, min(size - radius, cy + radius)
    if edge == "W":
        return max(radius, cx - radius), cy
    return min(size - radius, cx + radius), cy


def _edge_point_toward(cx, cy, edge, size):
    if edge == "N":
        return cx, 2
    if edge == "S":
        return cx, size - 2
    if edge == "W":
        return 2, cy
    return size - 2, cy


def _carve(plan_dict, size):
    seed = plan_dict["seed"]
    grid_rows = _make_plain(size, seed)
    lf = plan_dict["landform"]["id"]
    params = plan_dict["landform_params"]
    footprint = params["footprint_fraction"]
    orient = math.radians(params["orientation_deg"])
    relief = params["relief_class"]
    hydro = plan_dict["hydrology"]["kind"]
    cat = LANDFORM_CATEGORY.get(lf, "raised_blob")
    cx, cy = size / 2.0, size / 2.0
    area = footprint * size * size

    if cat == "raised_blob":
        radius = math.sqrt(area / math.pi)
        core = scatter.blob(cx, cy, radius, seed=seed, roughness=0.5)
        rim = scatter.rim_band(cx, cy, radius, width=0.18,
                                squash=0.8 if lf == "LoneMountain" else 0.55,
                                rotation=orient)
        core_fill = "Sandstone_Smooth" if relief == "low" else "Sandstone_Rough"
        _paint(grid_rows, core, core_fill, size)
        _paint(grid_rows, rim, "Sandstone_RoughHewn", size)

    elif cat == "carved_line":
        length = max(size * 0.7, math.sqrt(area) * 3.2)
        x0, y0, x1, y1 = _line_endpoints(cx, cy, length, orient, size)
        width = max(3, int(math.sqrt(area) / 6))
        wallcells = scatter.walk(x0, y0, x1, y1, wander=0.45, seed=seed, width=width + 3)
        _paint(grid_rows, [(x, z, 1.0) for x, z in wallcells], "Sandstone_Rough", size)
        floorcells = scatter.walk(x0, y0, x1, y1, wander=0.45, seed=seed, width=width)
        floor_fill = "Gravel" if hydro == "dry_riverbed" else "SoftSand"
        _paint(grid_rows, [(x, z, 1.0) for x, z in floorcells], floor_fill, size)
        if lf == "Badlands":
            for i in range(2):
                sign = 1 if i else -1
                bx0, by0, bx1, by1 = _line_endpoints(
                    cx + sign * size * 0.15, cy + sign * size * 0.15,
                    length * 0.5, orient + math.radians(40 * sign), size)
                cells = scatter.walk(bx0, by0, bx1, by1, wander=0.5, seed=seed + 10 + i,
                                      width=max(2, width - 1))
                _paint(grid_rows, [(x, z, 1.0) for x, z in cells], floor_fill, size)

    elif cat == "radial":
        radius = math.sqrt(area / math.pi)
        core = list(scatter.radial_field(cx, cy, radius, falloff=1.4))
        rim = scatter.rim_band(cx, cy, radius, width=0.16)
        floor_fill = "Mud" if lf == "Sinkhole" else (
            "SoftSand" if hydro in ("salt_pan", "brine_seep") else "Gravel")
        _paint(grid_rows, [(x, z, d) for x, z, d in core if d > 0.04], floor_fill, size)
        _paint(grid_rows, rim, "Sandstone_RoughHewn", size)
        if hydro in ("spring", "brine_seep") and lf in ("Crater", "Caldera"):
            centre_cells = [(x, z, d) for x, z, d in core if d > 0.75]
            _paint(grid_rows, centre_cells, "WaterShallow", size)

    elif cat == "basin":
        radius = math.sqrt(area / math.pi)
        cells = scatter.blob(cx, cy, radius, seed=seed, roughness=0.35)
        basin_fill = {"salt_pan": "SoftSand", "delta": "Mud", "brine_seep": "Marsh",
                      "spring": "WaterShallow", "river": "WaterShallow",
                      "none": "Mud"}.get(hydro, "Mud")
        _paint(grid_rows, cells, basin_fill, size)
        if hydro in ("delta", "river", "spring"):
            edge = _edge_from_orientation(params["orientation_deg"])
            ex, ey = _edge_point_toward(cx, cy, edge, size)
            path = scatter.walk(ex, ey, cx, cy, wander=0.4, seed=seed + 3, width=2)
            _paint(grid_rows, [(x, z, 1.0) for x, z in path], "WaterShallow", size)

    elif cat == "coastal":
        edge = _edge_from_orientation(params["orientation_deg"])
        depth = size * footprint
        for z in range(size):
            for x in range(size):
                d = _dist_from_edge(x, z, edge, size)
                wob = (scatter.fbm(x, z, seed=seed, octaves=2, scale=14.0) - 0.5) * size * 0.12
                if d + wob < depth:
                    grid_rows[z][x] = "WaterOceanDeep" if d + wob < depth * 0.45 else "WaterOceanShallow"
        if lf == "Peninsula":
            radius = math.sqrt(area / math.pi) * 0.6
            px, py = _push_point(cx, cy, edge, radius, size)
            cells = scatter.blob(px, py, radius, seed=seed, roughness=0.4)
            _paint(grid_rows, cells, "Sand", size)

    return grid_rows


def grid(plan_dict, size=250):
    """Terrain grid: list of rows (z), each a list of defNames (x)."""
    sz = plan_dict.get("map_size", size)
    return _carve(plan_dict, sz)


# --------------------------------------------------------------------- gates
IMPASSABLE = {"WaterOceanDeep", "WaterDeep", "WaterMovingChestDeep"}


def gates(grid_rows):
    """Offline connectivity (flood-fill from map centre) and largest
    buildable area (largest connected non-water region), rule 8.

    UNKNOWN/simplification: this v0 terrain grid carries no actual
    ThingDef walls (structures are out of scope, spec section E), so
    "impassable" here means only deep water. The rule-3 test ("an anchor
    cell unreachable from two map edges") is not checked per-anchor;
    the aggregate connectivity_fraction is used as the proxy instead.
    """
    h = len(grid_rows)
    w = len(grid_rows[0]) if h else 0
    total = w * h

    def passable(t):
        return t not in IMPASSABLE

    def buildable(t):
        return "water" not in t.lower()

    cx, cy = w // 2, h // 2
    start = None
    for r in range(max(w, h)):
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, z = cx + dx, cy + dz
                if 0 <= x < w and 0 <= z < h and passable(grid_rows[z][x]):
                    start = (x, z)
                    break
            if start:
                break
        if start:
            break

    total_passable = sum(1 for row in grid_rows for t in row if passable(t))
    reached = 0
    if start:
        seen = [[False] * w for _ in range(h)]
        stack = [start]
        seen[start[1]][start[0]] = True
        while stack:
            x, z = stack.pop()
            reached += 1
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, nz = x + dx, z + dz
                if 0 <= nx < w and 0 <= nz < h and not seen[nz][nx] and passable(grid_rows[nz][nx]):
                    seen[nz][nx] = True
                    stack.append((nx, nz))
    connectivity_fraction = reached / total_passable if total_passable else 0.0

    seen2 = [[False] * w for _ in range(h)]
    best = 0
    for z0 in range(h):
        for x0 in range(w):
            if seen2[z0][x0] or not buildable(grid_rows[z0][x0]):
                continue
            stack = [(x0, z0)]
            seen2[z0][x0] = True
            count = 0
            while stack:
                x, z = stack.pop()
                count += 1
                for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, nz = x + dx, z + dz
                    if 0 <= nx < w and 0 <= nz < h and not seen2[nz][nx] and buildable(grid_rows[nz][nx]):
                        seen2[nz][nx] = True
                        stack.append((nx, nz))
            best = max(best, count)
    largest_buildable_fraction = best / total if total else 0.0
    passed = connectivity_fraction >= 0.90 and largest_buildable_fraction >= 0.05
    return {
        "connectivity_fraction": round(connectivity_fraction, 4),
        "largest_buildable_fraction": round(largest_buildable_fraction, 4),
        "passed": passed,
    }


# ------------------------------------------------------------------------ IO
def _write_grid_txt(grid_rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in grid_rows:
            f.write(",".join(row) + "\n")


def cmd_single(args):
    p = plan(args.sheet, args.seed)
    errs = validate(p)
    if errs:
        print("VALIDATE FAIL:\n" + "\n".join(errs), file=sys.stderr)
        return 1
    g = grid(p)
    gt = gates(g)
    if not gt["passed"]:
        print("GATES FAIL: %r" % gt, file=sys.stderr)
        return 1
    _write_grid_txt(g, args.out)
    plan_path = args.plan or (os.path.splitext(args.out)[0] + ".plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(p, f, indent=2)
    print("wrote %s and %s (gates=%r)" % (args.out, plan_path, gt))
    return 0


def cmd_batch(args):
    os.makedirs(args.outdir, exist_ok=True)
    lo, hi = [int(x) for x in args.seeds.split("-")]
    ok = True
    for s in range(lo, hi + 1):
        p = plan(args.sheet, s)
        errs = validate(p)
        if errs:
            print("seed %d VALIDATE FAIL: %s" % (s, errs), file=sys.stderr)
            ok = False
            continue
        g = grid(p)
        gt = gates(g)
        base = os.path.join(args.outdir, "seed%02d" % s)
        _write_grid_txt(g, base + ".grid.txt")
        with open(base + ".plan.json", "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2)
        with open(base + ".gates.json", "w", encoding="utf-8") as f:
            json.dump(gt, f, indent=2)
        print("seed %d: landform=%s premise=%r gates=%r" % (s, p["landform"]["id"], p["premise"], gt))
        if not gt["passed"]:
            ok = False
    return 0 if ok else 1


def cmd_selftest(_args):
    sheet = os.path.join(BIOMES_DIR, "deep_desert.md")
    dump_names = _load_terrain_defnames()
    landforms = set()
    ok_validate = True
    ok_gates = True
    ok_defnames = True
    for s in range(1, 9):
        p = plan(sheet, s)
        errs = validate(p)
        if errs:
            ok_validate = False
            print("seed %d validate errors: %s" % (s, errs), file=sys.stderr)
            continue
        landforms.add(p["landform"]["id"])
        g = grid(p)
        gt = gates(g)
        if not gt["passed"]:
            ok_gates = False
            print("seed %d gates fail: %r" % (s, gt), file=sys.stderr)
        names = {name for row in g for name in row}
        missing = names - dump_names if dump_names else set()
        if missing:
            ok_defnames = False
            print("seed %d unknown defNames: %s" % (s, missing), file=sys.stderr)
    ok_variety = len(landforms) >= 4
    print("landforms seen: %s" % sorted(landforms))
    checks = {"variety(>=4 distinct)": ok_variety, "validate(all pass)": ok_validate,
              "gates(all pass)": ok_gates, "defnames(all known)": ok_defnames}
    for name, v in checks.items():
        print("  %-24s %s" % (name, "PASS" if v else "FAIL"))
    passed = sum(1 for v in checks.values() if v)
    print("SELFTEST PASS %d/%d" % (passed, len(checks)))
    return 0 if passed == len(checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sheet")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out")
    ap.add_argument("--plan")
    ap.add_argument("--batch", action="store_true")
    ap.add_argument("--seeds")
    ap.add_argument("--outdir")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return cmd_selftest(args)
    if args.batch:
        if not (args.sheet and args.seeds and args.outdir):
            ap.error("--batch requires --sheet --seeds --outdir")
        return cmd_batch(args)
    if args.sheet and args.seed is not None and args.out:
        return cmd_single(args)
    ap.error("need --sheet --seed --out, or --batch --sheet --seeds --outdir, or --selftest")


if __name__ == "__main__":
    raise SystemExit(main())
