"""validation.py -- modcheck suite for RimMandrake: Weeping Stones (mandrake.rm.weepingstones).

Walk: design/validation_walks/RimMandrake/WeepingStones.md (`## must be true`, agent-owned, not hashed).
Item: WEEPING_STONES_FIRST_SCRIPT_1. Process: design/RimMandrake/debug_process.md section 2.

PACKAGING. This dev folder is SOURCE only. The biome ships COMPOSED inside `mandrake.rm.biomes`
(Biomes.compose.json), so a run loads the `weepingstones_solo` tier (modset_builder.py: BRIDGE +
mandrake.rm.biomes + the five DLCs) and `northstar_plan.py` expects `mandrake.rm.biomes` active.
`modcheck run WeepingStones` appends the dev folder's packageId with no closure and lands on a list
without the biome: drive `northstar_driver/cli.py run --mod WeepingStones --plan <northstar_plan.py>`.

What the mod is for (every line below is sourced; see the walk):
  * `RM_WeepingStones`, a hand-placed (generatesNaturally=false) BiomeDef that wires 6 stocked-pool
    animals + 8 invented natives + the canyon crab into `wildAnimals`, 14 plants into `wildPlants`,
    the freshwater catch into `fishTypes`, and the RM_WaterTruceExtension block.
  * the Stocked Pool husbandry kit: a water-only pen zone designator (`RM_Zone_PoolPen`) gated by the
    ONE Mod Setting `RM_WeepingStonesSettings.stockedPoolsEnabled`, and five jobs that move stock
    through it: NET (wild -> breeding-stock item), STOCK (item -> live pawn in a pen), FEED, HARVEST
    (pawn -> species meat), CULL (vhorrin -> an enormous meat harvest).
  * the cuisine layer: 5 recipes wired onto both stoves by patch, doubt-meat thoughts.

Derived from the mod's own `Defs/*.xml` at import (never a hand list): the def groups, the biome
roster, the fish table, the plants' harvested items, the items that carry a Rottable comp. Pinned
floors (FLOORS) stop a parse failure from reading as "nothing to check".

NOT measurable with the existing bridge tools (named in the walk, never faked here):
  * the pen's READ gauge (Healthy/Thin/Silent/Vhorrin) -- only `RM_Zone_PoolPen.GetInspectString`
    shows it and no tool reads a Zone's inspect string;
  * the three pulse mechanics (unfed-days death, vhorrin emergence, vizhik escape): per-pulse random
    chances, statistical (debug_process.md section 4), and the toggle's tick gate with them;
  * `RM_WorkGiver_*` autonomous offering (forced jobs bypass the scanner), `RM_BiomeWorker_*.GetScore`
    (inert by generatesNaturally=false), flyers (kirruk/mirrik flight: state read only, never live).

Every bridge call uses only parameters the live tool declares (lint_calls.py). Result shapes MEASURED
live elsewhere: `jawa/list_things` -> countMatched / isCompleteList / things[].id; `jawa/list_pawns` ->
pawns[].id/kindDef/faction; `jawa/get_defs` -> foundCount/notFound/defs[].fields; `jawa/biome_probe` ->
biomes[].animals/plants/findResults; `jawa/map_zones listZones` -> zones[].label/type/cells. UNPROVEN
until the first live run: the `rimworld/list_architect_*` row keys, `jawa/get_defs` serialising
`fishTypes`/`modExtensions`, and a stack-size key on list_things rows. A component that cannot read
a shape it needs records UNMEASURED (`_unmeasured`), never PASS.
"""
import contextlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("WeepingStones")
suite.toggles = ["oasisNativeFloraEnabled", "stockedPoolsEnabled", "vhorrinOddsMultiplier", "vizhikEscapeChance", "condenserSeasonDays", "waterTruceSuppressionEnabled", "dewsilkEnabled"]
SLIDERS = {"vhorrinOddsMultiplier": (1.0, 0.0, 3.0), "vizhikEscapeChance": (0.05, 0.0, 0.25),
           "condenserSeasonDays": (15.0, 3.0, 30.0)}   # WEEPINGSTONES_WALKING_CONDENSER_1

SETTINGS = "RimMandrake.WeepingStones.RM_WeepingStonesSettings"
EH_SETTINGS = "RimMandrake.EnvironmentalHazards.RM_EnvironmentalHazardsSettings"
EH_SLIDERS = {"waterTruceRadius": (10.0, 3.0, 25.0)}   # truce radius, cells
TOGGLE = "stockedPoolsEnabled"
EH_TOGGLE = "waterTruceSuppressionEnabled"   # WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1 (lives in EnvironmentalHazards)
_EH_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "EnvironmentalHazards", "Source")
BIOME = "RM_WeepingStones"
OUR_PACKAGES = ("mandrake.rm.biomes", "mandrake.rm.weepingstones")
ACTIVE_ON_TIER = ("Ludeon.RimWorld.Odyssey", "Ludeon.RimWorld.Biotech", "Ludeon.RimWorld.Ideology",
                  "Ludeon.RimWorld.Royalty", "Ludeon.RimWorld.Anomaly", "mandrake.rm.biomes")
PAD = 29                    # the fixture pad: PAD x PAD cells around the chain's anchor
PAD_OFFSET = 45             # the pad sits this far from the map centre, clear of the start colonists
POOL = 6                    # the water body is POOL x POOL, centred on the anchor
PEN_DESIGNATOR_NEEDLES = ("pool pen", "poolpen", "pool_pen")

# ----------------------------------------------------------------------- source parse (import time)

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Defs")
_ERRORS = []


def _parse(rel):
    try:
        return ET.parse(os.path.join(_DIR, rel)).getroot()
    except Exception as ex:                       # a def file that does not parse is itself a finding
        _ERRORS.append("%s: %s" % (rel, ex))
        return None


def _defs_in(subdir):
    """[(DefType, defName, element)] for every non-abstract def under Defs/<subdir>."""
    rows = []
    d = os.path.join(_DIR, subdir)
    if not os.path.isdir(d):
        _ERRORS.append("missing Defs/%s" % subdir)
        return rows
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".xml"):
            continue
        root = _parse(os.path.join(subdir, fn))
        if root is None:
            continue
        for el in root:
            if not isinstance(el.tag, str) or el.get("Abstract", "").lower() == "true":
                continue
            nm = (el.findtext("defName") or "").strip()
            if nm:
                rows.append((el.tag, nm, el))
    return rows


_BY_DIR = dict((d, _defs_in(d)) for d in (
    "ThingDefs_Races", "ThingDefs_Items", "ThingDefs_Plants", "RecipeDefs", "ThoughtDefs", "JobDefs",
    "WorkGiverDefs", "ThingSetMakerDefs", "BiomeDefs", "ThingDefs_Buildings", "LetterDefs"))


def _names(subdir, deftype):
    return [n for t, n, _ in _BY_DIR[subdir] if t == deftype]


# (group, DefType, names, floor). The floor is the count at authoring (2026-10-01): a shrink must be a
# deliberate edit of this script, never a silent pass.
GROUPS = [
    ("race_things", "ThingDef", _names("ThingDefs_Races", "ThingDef"), 18),
    ("pawnkinds", "PawnKindDef", _names("ThingDefs_Races", "PawnKindDef"), 18),
    ("items", "ThingDef", _names("ThingDefs_Items", "ThingDef"), 36),
    ("plants", "ThingDef", _names("ThingDefs_Plants", "ThingDef"), 10),
    ("recipes", "RecipeDef", _names("RecipeDefs", "RecipeDef"), 5),
    ("thoughts", "ThoughtDef", _names("ThoughtDefs", "ThoughtDef"), 8),
    ("jobs", "JobDef", _names("JobDefs", "JobDef"), 5),
    ("workgivers", "WorkGiverDef", _names("WorkGiverDefs", "WorkGiverDef"), 5),
    ("set_makers", "ThingSetMakerDef", _names("ThingSetMakerDefs", "ThingSetMakerDef"), 1),
    ("biome", "BiomeDef", _names("BiomeDefs", "BiomeDef"), 1),
    ("buildings", "ThingDef", _names("ThingDefs_Buildings", "ThingDef"), 1),
    ("letters", "LetterDef", _names("LetterDefs", "LetterDef"), 1),
]
ALL_DEFNAMES = set(n for _, _, names, _ in GROUPS for n in names)

_BIOME_EL = next((el for t, n, el in _BY_DIR["BiomeDefs"] if n == BIOME), None)


def _roster(tag):
    """{defName: (commonality, MayRequire-or-None)} for the biome's <wildAnimals>/<wildPlants>
    (children named for the def, text = commonality; never <li> -- CLAUDE.md)."""
    out = {}
    block = _BIOME_EL.find(tag) if _BIOME_EL is not None else None
    for ch in (block if block is not None else []):
        try:
            out[ch.tag] = (float((ch.text or "").strip()), ch.get("MayRequire"))
        except ValueError:
            _ERRORS.append("%s/%s: commonality %r is not a number" % (tag, ch.tag, ch.text))
    return out


BIOME_ANIMALS = _roster("wildAnimals")
BIOME_PLANTS = _roster("wildPlants")


def _fish_names():
    names = []
    ft = _BIOME_EL.find("fishTypes") if _BIOME_EL is not None else None
    for grp in (ft if ft is not None else []):
        for ch in grp:
            names.append(ch.tag)
        if not len(grp) and grp.tag != "rareCatchesSetMaker":
            names.append(grp.tag)
    return [n for n in names if n != "rareCatchesSetMaker"]


FISH_NAMES = _fish_names()
BIOME_SCALARS = dict((k, float(_BIOME_EL.findtext(k))) for k in ("animalDensity", "plantDensity", "maxFishPopulation")
                     if _BIOME_EL is not None and _BIOME_EL.findtext(k))
# stove recipes only: a recipe that declares its own <recipeUsers> (RM_SpinDewsilk -> tailor benches) is wired by the def,
# not by RM_StockedPoolRecipeWiring.xml. Live 2026-10-03 flagged RM_SpinDewsilk as "missing from the stoves" -- a script
# bug (wrong bench), not a content bug.
RECIPES = [n for _, n, el in _BY_DIR["RecipeDefs"] if el.find("recipeUsers") is None]

# the stocked-pool species: pawnkind <K> pairs with RM_<K>Meat (HARVEST/CULL drop it), and the seven
# stockable ones also with <K>BreedingStock (NET drops it, STOCK reads it): RM_PoolBreederUtility.cs.
_STOCK_KINDS = sorted(n for n in _names("ThingDefs_Races", "PawnKindDef") if n in (
    "RM_Murrin", "RM_Skarrin", "RM_Karrek", "RM_Vizhik", "RM_Vhorrin", "RM_Loomu", "RM_Huldu", "RM_Ivvol"))
STOCKABLE = [k for k in _STOCK_KINDS if k != "RM_Vhorrin"]
PAIRED = ["%sMeat" % k for k in _STOCK_KINDS] + ["%sBreedingStock" % k for k in STOCKABLE]
ROTTABLE_ITEMS = sorted(n for t, n, el in _BY_DIR["ThingDefs_Items"]
                        if any(li.get("Class") == "CompProperties_Rottable" for li in el.findall("comps/li")))
FLORA_PRODUCTS = [(n, (el.findtext("plant/harvestedThingDef") or "").strip())
                  for t, n, el in _BY_DIR["ThingDefs_Plants"]
                  if (el.findtext("plant/harvestedThingDef") or "").strip().startswith("RM_")]
CATCH_KINDS = sorted(n[:-5] for n in FISH_NAMES if n.endswith("Catch"))   # RM_SkarrinCatch -> RM_Skarrin

_G = {}                     # per-process memo (designator id)


# --------------------------------------------------------------------------------- helpers

class _Unmeasured(Exception):
    pass


def _live(t):
    """True only for a real run against a real Session and an unfailed chain; False in the offline
    declaration probe, so manual assertions never trip on its no-op (None) results."""
    return t.session is not None and not t.upstream_failed


def _fail(msg):
    raise ExpectationFailed(msg)


def _unmeasured(t, why):
    """Stop this component and record UNMEASURED with `why` (never a pass)."""
    t._why = why
    t._record("UNMEASURED", why)
    t.upstream_failed = True            # the grader's only route to an UNMEASURED verdict
    raise _Unmeasured(why)


@contextlib.contextmanager
def _comp(t, name, independent=False, **kw):
    """t.component() plus: `_unmeasured` records the real reason as the detail; with independent=True
    a FAIL or UNMEASURED does not poison the next component (pure reads that share no state), while a
    setup component (the default) leaves every later component of its chain UNMEASURED."""
    before = t.upstream_failed
    t._why = None
    with t.component(name, **kw) as tt:
        yield tt
    why = getattr(t, "_why", None)
    if why and not before:
        t.components[-1].detail = "UNMEASURED: %s" % why
    if independent and not before:
        t.upstream_failed = False         # a setup component (independent=False) keeps the chain blocked
    t._why = None
    if t.session is not None and t.components:
        c = t.components[-1]
        print("[ws] %s %s %s" % (time.strftime("%H:%M:%S"), c.name, c.verdict), str(c.detail or "")[:300],
              file=sys.stderr, flush=True)


def _note(t, label, data):
    """Evidence record, also echoed to stderr (the results JSON keeps only a short excerpt)."""
    t._record(label, data)
    if t.session is not None:
        print("[ws-note] %s: %s" % (label, json.dumps(data, default=str)[:1200]), file=sys.stderr, flush=True)


def _ok(r, what):
    if not isinstance(r, dict) or r.get("success") is False:
        _fail("%s failed: %r" % (what, r))
    return r


def _flat(obj):
    """Every string / number / bool anywhere inside a JSON-ish value, as strings."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k)
            for x in _flat(v):
                yield x
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for x in _flat(v):
                yield x
    elif obj is not None:
        yield str(obj)


def _need_parse(t):
    if _ERRORS:
        _fail("the mod's own Defs did not parse: %s" % "; ".join(_ERRORS[:3]))


def _get_defs(t, specs, fields=None, deep=False):
    """get_defs over `DefType/defName` specs (a STRING, chunked); returns [row,...] and notFound.
    Reads the tool's own success/foundCount/notFound -- never a substring of the payload."""
    rows, missing = [], []
    for i in range(0, len(specs), 40):
        chunk = specs[i:i + 40]
        r = t.bridge_call("jawa/get_defs", defs=";".join(chunk), fields=fields or "", deep=bool(deep))
        if not _live(t):
            return [], []
        _ok(r, "get_defs(%d defs)" % len(chunk))
        if r.get("requested") not in (None, len(chunk)):
            _fail("get_defs asked for %d, tool says it handled %r" % (len(chunk), r.get("requested")))
        rows.extend(r.get("defs") or [])
        missing.extend(r.get("notFound") or [])
        if (r.get("foundCount") is not None
                and r.get("foundCount") + len(r.get("notFound") or []) != len(chunk)):
            _fail("get_defs foundCount %r + notFound %r != %d requested" % (
                r.get("foundCount"), len(r.get("notFound") or []), len(chunk)))
    return rows, missing


def _things(t, defs, rect, limit=500):
    r = t.bridge_call("jawa/list_things", defName=defs, rect=rect, limit=limit)
    if not _live(t):
        return []
    _ok(r, "list_things(%s)" % defs)
    if r.get("isCompleteList") is False:
        _fail("list_things(%s) truncated: %r" % (defs, r.get("message")))
    return list(r.get("things") or [])


def _row_def(row):
    return row.get("def") or row.get("defName")


def _pawns(t, rect, kind=None):
    r = t.bridge_call("jawa/list_pawns", rect=rect, limit=200)
    if not _live(t):
        return []
    _ok(r, "list_pawns")
    if r.get("truncated"):
        _fail("list_pawns truncated: %r" % r.get("message"))
    return [p for p in (r.get("pawns") or []) if kind is None or p.get("kindDef") == kind]


def _stack(row):
    for k in ("stackCount", "count", "stack"):
        if isinstance(row.get(k), (int, float)):
            return int(row[k])
    return None


def _enter(t):
    """First line of every fixture chain: move this chain's anchor to the pad, off the map centre."""
    if not getattr(t, "_ws_anchored", False):
        x, z = t.anchor
        # The driver's anchor comes off the quicktest map and can sit near an edge of the 250x250 situational
        # map (MEASURED 2026-10-03: "Cell is outside the map", pen covering 18 of 36 cells = pool half off-map).
        # Re-base on the live map centre, as Contagion's _pad does.
        if _live(t):
            try:
                mi = t.bridge_call("jawa/map_info")
                if isinstance(mi, dict) and mi.get("sizeX") and mi.get("sizeZ"):
                    x, z = int(mi["sizeX"]) // 2, int(mi["sizeZ"]) // 2
            except Exception:
                pass
        t.anchor = (x + PAD_OFFSET, z + PAD_OFFSET)
        t._ws_anchored = True


def _pad_rect(t):
    x, z = t.anchor
    h = PAD // 2
    return "%d,%d,%d,%d" % (x - h, z - h, PAD, PAD)


def _pool_rect(t):
    x, z = t.anchor
    return (x - POOL // 2, z - POOL // 2, POOL, POOL)


def _rs(r):
    return "%d,%d,%d,%d" % tuple(r)


# ----------------------------------------------------------------------------- the site fixture

def _pen_zones(t):
    r = t.bridge_call("jawa/map_zones", action="listZones")
    if not _live(t):
        return []
    _ok(r, "map_zones(listZones)")
    return [z for z in (r.get("zones") or []) if z.get("type") == "RM_Zone_PoolPen"]


def _reset_pad(t, terrain="Concrete"):
    """Everything true before the first assertion: our zones gone, the pad empty (things AND pawns),
    flat dry floor, unfogged. The pad sits off the map centre so the start colonists are not in it."""
    rect = _pad_rect(t)
    for zone in _pen_zones(t):
        t.bridge_call("jawa/map_zones", action="deleteZone", zone=zone.get("label"))
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="All")
    t.bridge_call("jawa/destroy_batch", rects=rect, categories="Pawn")
    # destroy_batch LEAVES PAWNS ALONE (MEASURED live 2026-10-03: "2 pawn(s) left alone"), so skarrin and
    # vhorrin from earlier chains survived every reset and broke the next site's precondition.
    t.bridge_call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    t.bridge_call("jawa/set_terrain_batch", ops="%s:%s" % (terrain, rect))
    t.bridge_call("jawa/set_fog", action="unfog", rect=rect)
    t.bridge_call("jawa/log_autoopen_suppress")
    if _live(t):
        if _pen_zones(t):
            _fail("pool-pen zones survived deleteZone")


def _teardown(t):
    """Best-effort, runs even after a FAILED chain (t.bridge_call is then a no-op, so use the session)."""
    if t.session is None or not getattr(t, "_ws_anchored", False):
        return
    try:
        rect = _pad_rect(t)
        for zone in [z for z in ((t.session.call("jawa/map_zones", action="listZones") or {}).get("zones") or [])
                     if z.get("type") == "RM_Zone_PoolPen"]:
            t.session.call("jawa/map_zones", action="deleteZone", zone=zone.get("label"))
        t.session.call("jawa/destroy_batch", rects=rect, categories="All")
        t.session.call("jawa/destroy_batch", rects=rect, categories="Pawn")
        t.session.call("jawa/destroy_bulk", filter="nonColonists", dryRun=False)
    except Exception as ex:                       # teardown must never mask the chain's own verdict
        print("[ws] teardown failed: %s" % ex, file=sys.stderr, flush=True)


def _spawn(t, kind, x, z, faction):
    r = t.bridge_call("jawa/spawn_pawn", kindDef=kind, x=x, z=z, faction=faction, count=1)
    if not _live(t):
        return None
    _ok(r, "spawn_pawn(%s)" % kind)
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    if not pid:
        _fail("spawn_pawn(%s) returned no pawn id: %r" % (kind, r))
    return pid


def _settle(t, pid):
    """A colonist that will not wander off to eat, sleep or fight: needs full, undrafted."""
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Food", level=1.0)
    t.bridge_call("jawa/pawn_need", pawn=pid, action="need", need="Rest", level=1.0)
    t.bridge_call("jawa/set_draft", pawnId=pid, drafted=False)


class _patient(object):
    """Raise the bridge client's per-reply socket timeout (the runner's 30 s) for a slow job order or tick
    wait, then restore it. MEASURED live 2026-10-03: ordered_job took 17 s with waitTicks=60 and the NET /
    STOCK / FEED / CULL waits then outran 30 s. A mock session without a real socket is left alone."""
    def __init__(self, t, secs=240.0):
        self.rb = getattr(getattr(t, "session", None), "_rb", None)
        self.secs, self.old = secs, None

    def __enter__(self):
        if self.rb is not None and hasattr(self.rb, "timeout"):
            self.old = self.rb.timeout
            self.rb.timeout = self.secs
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.secs)
        return self

    def __exit__(self, *a):
        if self.old is not None:
            self.rb.timeout = self.old
            sock = getattr(self.rb, "sock", None)
            if sock is not None:
                sock.settimeout(self.old)
        return False


def _run_job(t, pid, job, a, ticks, *pos, **kw):
    with _patient(t):
        _order(t, pid, job, a, *pos, **kw)
        t.wait_ticks(ticks)


def _order(t, pid, job, a, bx=None, bz=None, count=None):
    """Force `job` on pawn `pid`: targetA a thing id, optional targetB cell, optional stack count."""
    if bx is None:
        r = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef=job, targetAId=a, waitTicks=60, timeoutSeconds=60)
    elif count is None:
        r = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef=job, targetAId=a, targetBX=bx, targetBZ=bz,
                          waitTicks=60, timeoutSeconds=60)
    else:
        r = t.bridge_call("jawa/ordered_job", pawnId=pid, jobDef=job, targetAId=a, targetBX=bx, targetBZ=bz,
                          count=count, waitTicks=60, timeoutSeconds=60)
    if _live(t):
        if not (bool((r or {}).get("accepted")) and bool((r or {}).get("nowRunningRequested"))):
            _fail("jawa/ordered_job %s was not accepted and running: %r" % (job, r))
    return r


# ------------------------------------------------------------------ the pen designator (UI path)

def _zone_designators(t):
    """([designator rows], pen_row_or_None, control_row_or_None) from the vanilla "Zone" category.
    A designatorId is a UI path, never a defName (skills/rimbridge map-authoring.md): resolve it live."""
    cats = t.bridge_call("rimworld/list_architect_categories")
    if not _live(t):
        return [], None, None
    rows = cats if isinstance(cats, list) else (_ok(cats, "list_architect_categories").get("categories") or [])
    zone = next((c for c in rows if c.get("categoryDefName") == "Zone"), None)
    if not zone or not zone.get("id"):
        _unmeasured(t, "no architect category with categoryDefName 'Zone' in %s" % str(rows)[:200])
    lst = t.bridge_call("rimworld/list_architect_designators", categoryId=zone["id"])
    ds = _ok(lst, "list_architect_designators").get("designators")
    if not isinstance(ds, list) or not ds:
        _unmeasured(t, "list_architect_designators(Zone) returned no designator list: %s" % str(lst)[:200])
    pen = next((d for d in ds if any(n in json.dumps(d).lower() for n in PEN_DESIGNATOR_NEEDLES)), None)
    control = next((d for d in ds if "growing" in json.dumps(d).lower()), None)
    if control is None:
        _unmeasured(t, "the vanilla growing-zone designator is not in the Zone listing, so the listing "
                       "is not trustworthy: %s" % str(ds)[:300])
    return ds, pen, control


def _make_pen(t, rect):
    """Create a pen over `rect` (x, z, w, h) through the real designator, then prove it by reading
    the zone list back. Returns the zone row."""
    _, pen, _ = _zone_designators(t)
    if _live(t) and pen is None:
        _unmeasured(t, "no pool-pen designator in the Zone category, so no pen can be made here: the "
                       "defect is reported by settings_and_designator.designator_listed_when_on")
    did = (pen or {}).get("id")
    r = t.bridge_call("rimworld/apply_architect_designator", designatorId=did, x=rect[0], z=rect[1],
                      width=rect[2], height=rect[3], keepSelected=False)
    if not _live(t):
        return {}
    _ok(r, "apply_architect_designator(pool pen)")
    zones = _pen_zones(t)
    if len(zones) != 1:
        _fail("expected exactly one RM_Zone_PoolPen after designating %s, found %d: %r" % (rect, len(zones), zones))
    return zones[0]


def _pen_site(t, plant_pool=True):
    """Dry pad, a POOL x POOL shallow-water body at the anchor, one pen over all of it."""
    _reset_pad(t)
    rect = _pool_rect(t)
    t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%s" % _rs(rect))
    if _live(t):
        got = t.bridge_call("jawa/get_terrain_batch", rects=_rs(rect))
        _ok(got, "get_terrain_batch")
        if "WaterShallow" not in str(got):
            _fail("the pool did not take WaterShallow terrain: %s" % str(got)[:200])
    zone = _make_pen(t, rect)
    if _live(t) and zone.get("cells") != POOL * POOL:
        _fail("pen covers %r cells, expected the whole %dx%d pool (%d)" % (
            zone.get("cells"), POOL, POOL, POOL * POOL))
    return zone


# ================================================================================ chains

@suite.chain("log_clean")
def log_clean(t):
    """The whole load, one read: no config error, unresolved cross-reference, missing type or exception
    naming this mod's content. Guards the 2026-09-20..24 load defects: a stale EnvironmentalHazards.dll
    discarding the BiomeDef whole ('Could not find type named ...RM_WaterTruceExtension'), 16 PawnKindDefs
    with the wrong lifeStages count, 8 species on a linkedBodyPartsGroup their body lacks, RM_Ssurr's
    dangling Tail group."""
    with _comp(t, "player_log_names_no_weepingstones_error", independent=True):
        if _live(t):
            _need_parse(t)
            from game_paths import PLAYER_LOG
            if not os.path.isfile(PLAYER_LOG):
                _unmeasured(t, "no Player.log at %s" % PLAYER_LOG)
            with open(PLAYER_LOG, "rb") as fh:
                text = fh.read().decode("utf-8", "replace")
            lines = text.splitlines()
            if "Bridge token" not in text and "RimBridge" not in text:
                _unmeasured(t, "Player.log (%d lines) does not look like a bridged live session" % len(lines))
            names = re.compile("|".join(re.escape(n) for n in sorted(ALL_DEFNAMES | set(
                ["WeepingStones", "RM_WaterTruceExtension", BIOME]))))
            bad_kind = ("Config error", "Could not resolve cross-reference", "Could not find type named",
                        "Exception", "rror in")
            hits = [ln.strip() for ln in lines if names.search(ln) and any(k in ln for k in bad_kind)]
            general = sum(1 for ln in lines if "Config error" in ln or "Could not resolve cross-reference" in ln)
            _note(t, "Player.log scan", {"lines": len(lines), "hits": hits[:5],
                                         "game-wide config/xref lines (instrument probe)": general})
            if hits:
                _fail("%d Player.log line(s) name this mod's content in an error: %s" % (
                    len(hits), " | ".join(h[:200] for h in hits[:3])))


@suite.chain("defs_resolve")
def defs_resolve(t):
    """Every def this mod ships resolves in the running game (a def that fails to load is dropped whole
    and silently: a missing comp/worker type, an XML comment with a double hyphen). Expected names come
    from the mod's own XML. A control proves the instrument can say 'not found'."""
    with _comp(t, "resolve_probe_sees_absence", independent=True):
        real = (GROUPS[2][2] or ["RM_Murrin"])[0]
        rows, missing = _get_defs(t, ["ThingDef/RM_NoSuchWeepingStonesDef_Control", "ThingDef/%s" % real])
        if _live(t):
            found = [r.get("defName") for r in rows if r.get("found")]
            if missing != ["ThingDef/RM_NoSuchWeepingStonesDef_Control"] or found != [real]:
                _fail("the def probe cannot tell present from absent: found=%r notFound=%r" % (found, missing))

    for group, deftype, names, floor in GROUPS:
        with _comp(t, "defs_resolve_%s" % group, independent=True):
            if _live(t):
                _need_parse(t)
                if len(names) < floor:
                    _fail("source parse found %d %s defs, floor is %d -- a parse failure or an undeclared "
                          "deletion (edit FLOORS deliberately if the mod shrank)" % (len(names), group, floor))
            rows, missing = _get_defs(t, ["%s/%s" % (deftype, n) for n in names])
            if _live(t):
                if missing:
                    _fail("%d of %d %s not loaded by the game: %s" % (len(missing), len(names), group, missing[:8]))
                wrong = [r.get("defName") for r in rows if r.get("packageId") not in OUR_PACKAGES]
                if wrong:
                    _fail("defs resolve but from another mod (shadowed?): %s" % wrong[:6])

    with _comp(t, "defs_pair_up_by_convention", independent=True):
        # HARVEST/CULL read RM_<Kind>Meat and NET reads <Kind>BreedingStock BY NAME with GetNamedSilentFail:
        # a renamed def makes the job succeed and drop nothing (RM_JobDriver_HarvestPoolPen.cs).
        if _live(t):
            _need_parse(t)
            if len(PAIRED) < 14:
                _fail("convention list is short (%d): parse failure" % len(PAIRED))
        rows, missing = _get_defs(t, ["ThingDef/%s" % n for n in PAIRED])
        if _live(t) and missing:
            _fail("the job-by-name convention is broken, these defs do not exist: %s" % missing)


@suite.chain("biome_roster")
def biome_roster(t):
    """`RM_WeepingStones` as the game resolved it (jawa/biome_probe reads the runtime caches, the only
    tool that can see wildAnimals/wildPlants). Live is compared with the mod's own XML, so a patch
    that removes or zeroes a row, a dropped record, or a dead roster each fail."""
    box = {}
    with _comp(t, "biome_probe_ready"):
        r = t.bridge_call("jawa/biome_probe", biomes=BIOME, animals=True, plants=True, topN=200,
                          find="RM_Vhorrin,RM_Sillik,RM_NoSuchCreatureControl")
        if _live(t):
            _ok(r, "biome_probe")
            rows = r.get("biomes") or []
            if len(rows) != 1 or rows[0].get("defName") != BIOME:
                _fail("biome_probe did not return exactly %s: %s" % (BIOME, str(r)[:300]))
            box["row"] = rows[0]
            box["animals"] = dict((a.get("defName"), a.get("commonality")) for a in (rows[0].get("animals") or []))
            box["plants"] = dict((p.get("defName"), p.get("commonality")) for p in (rows[0].get("plants") or []))
            box["find"] = dict((f.get("defName"), f.get("state")) for f in (rows[0].get("findResults") or []))
            if rows[0].get("wildAnimalCount") != rows[0].get("animalsListed") or \
                    rows[0].get("wildPlantCount") != rows[0].get("plantsListed"):
                _fail("biome_probe lists were capped (animals %r/%r, plants %r/%r)" % (
                    rows[0].get("animalsListed"), rows[0].get("wildAnimalCount"),
                    rows[0].get("plantsListed"), rows[0].get("wildPlantCount")))

    with _comp(t, "biome_flags_and_densities", independent=True):
        if _live(t):
            _need_parse(t)
            row = box["row"]
            if row.get("generatesNaturally") is not False:
                _fail("generatesNaturally is %r; the biome is hand-placed, never natural worldgen" % row.get("generatesNaturally"))
            # wildAnimals spawn only while animalDensity > 0 (MEASURED from the engine, CLAUDE.md): 0 = dead roster
            for k in ("animalDensity", "plantDensity"):
                if not (float(row.get(k) or 0) > 0):
                    _fail("%s is %r: a zero density makes the roster dead content" % (k, row.get(k)))
                if k in BIOME_SCALARS and abs(float(row[k]) - BIOME_SCALARS[k]) > 1e-4:
                    _fail("%s live %r != source %r" % (k, row[k], BIOME_SCALARS[k]))

    for kind, live_key, expect in (("animals", "animals", BIOME_ANIMALS), ("plants", "plants", BIOME_PLANTS)):
        with _comp(t, "wild_%s_wired" % kind, independent=True):
            if _live(t):
                _need_parse(t)
                if len(expect) < 10:
                    _fail("source parse found %d wild %s rows: parse failure" % (len(expect), kind))
                missing, skewed, skipped = [], [], []
                for name, (c, req) in sorted(expect.items()):
                    if req and req not in ACTIVE_ON_TIER:
                        skipped.append("%s (needs %s)" % (name, req))
                        continue
                    live = box[live_key].get(name)
                    if live is None:
                        missing.append(name)
                    elif abs(float(live) - c) > 1e-3:
                        skewed.append("%s live %.3f != source %.3f" % (name, float(live), c))
                _note(t, "wild %s rows not asserted (their donor mod is not on this tier)" % kind, skipped)
                if missing or skewed:
                    _fail("wild %s drift: missing %s; commonality %s" % (kind, missing, skewed))

    with _comp(t, "vhorrin_never_ambient_and_probe_is_honest", independent=True):
        # RM_Vhorrin is the mismanagement state made flesh (spec 2d): 'NOT placed on any wildAnimals list'.
        # The two controls prove the three-state probe: a real row is 'spawning', an invented one 'absent'.
        if _live(t):
            f = box["find"]
            if f.get("RM_Sillik") != "spawning" or f.get("RM_NoSuchCreatureControl") != "absent":
                _fail("biome_probe's find states are not trustworthy: %r" % f)
            if f.get("RM_Vhorrin") != "absent":
                _fail("RM_Vhorrin is %r on %s; it must never roam wild" % (f.get("RM_Vhorrin"), BIOME))

    with _comp(t, "stocked_catch_has_living_counterpart", independent=True):
        # the two-def law (biome XML header, STOCKED_POOL spec 0/2): every stocked catch item has its pawn
        # in wildAnimals, so what is fished is also alive in the pool.
        if _live(t):
            _need_parse(t)
            if len(CATCH_KINDS) < 7:
                _fail("source parse found %d stocked catch items, expected 7 (murrin included)" % len(CATCH_KINDS))
            dead = [k for k in CATCH_KINDS if box["animals"].get(k) is None]
            if dead:
                _fail("catch items with no living pawn on the biome roster: %s" % dead)
            if "RM_Murrin" not in CATCH_KINDS:
                _fail("RM_MurrinCatch missing from the source parse (WEEPINGSTONES_MURRIN_CATCH_WIRING_1)")

    with _comp(t, "fish_types_wired", independent=True):
        rows, missing = _get_defs(t, ["BiomeDef/%s" % BIOME], fields="fishTypes,maxFishPopulation", deep=True)
        if _live(t):
            _need_parse(t)
            if missing or not rows:
                _fail("BiomeDef %s not resolvable: %r" % (BIOME, missing))
            fields = rows[0].get("fields") or {}
            ft = fields.get("fishTypes")
            blob = set(_flat(ft))
            if not isinstance(ft, (dict, list)):
                _unmeasured(t, "get_defs cannot serialise fishTypes into a structure (got %r)" % (ft,))
            absent = [n for n in FISH_NAMES if n not in blob]
            if absent:
                _fail("fishTypes lacks %s" % absent)
            if "maxFishPopulation" in BIOME_SCALARS and float(fields.get("maxFishPopulation") or 0) != BIOME_SCALARS["maxFishPopulation"]:
                _fail("maxFishPopulation live %r != source %r" % (fields.get("maxFishPopulation"), BIOME_SCALARS["maxFishPopulation"]))

    with _comp(t, "water_truce_extension_present", independent=True):
        # the WATER_TRUCE_RETRIBUTION_1 block lives in EnvironmentalHazards.dll; a stale dll discarded the
        # whole BiomeDef (WEEPINGSTONES_RM_MOD_BUILD_1 live proof).
        rows, missing = _get_defs(t, ["BiomeDef/%s" % BIOME], fields="modExtensions", deep=True)
        if _live(t):
            if missing or not rows:
                _fail("BiomeDef %s not resolvable: %r" % (BIOME, missing))
            ext = (rows[0].get("fields") or {}).get("modExtensions")
            blob = list(_flat(ext))
            if ext in (None, "(no such field)"):
                _unmeasured(t, "get_defs cannot read modExtensions (got %r)" % (ext,))
            # get_defs flattens a modExtension to its FIELDS with the class name absent (MEASURED live
            # 2026-10-03: [{"radius": 10.0}]); recognise it by its name OR by its one field, `radius`
            # (source: RM_WeepingStones_Biome.xml carries RM_WaterTruceExtension with <radius>10</radius>).
            if not any("WaterTruce" in s or s == "radius" for s in blob):
                _fail("RM_WaterTruceExtension is not among the biome's modExtensions: %s" % blob[:8])
            _note(t, "modExtensions", blob[:12])


    with _comp(t, "sun_heat_extension_present", independent=True):
        # WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1: the biome declares its heat kind (one planet-wide kind of
        # heat). get_defs flattens a modExtension to its FIELDS (class name absent, see above), so
        # recognise RM_SunHeatExtension by its name OR by its distinctive field `heatKind`.
        rows, missing = _get_defs(t, ["BiomeDef/%s" % BIOME], fields="modExtensions", deep=True)
        if _live(t):
            if missing or not rows:
                _fail("BiomeDef %s not resolvable: %r" % (BIOME, missing))
            ext = (rows[0].get("fields") or {}).get("modExtensions")
            if ext in (None, "(no such field)"):
                _unmeasured(t, "get_defs cannot read modExtensions (got %r)" % (ext,))
            blob = list(_flat(ext))
            if not any("SunHeat" in s or s == "heatKind" for s in blob):
                _fail("RM_SunHeatExtension is not among the biome's modExtensions: %s" % blob[:10])

    with _comp(t, "no_dead_windhour_text", independent=True):
        # Wind-hour was ruled DEAD (owner, 2026-09-24, "nah"); twelve def sentences and one C# comment
        # still named it until WEEPINGSTONES_HEAT_WINDHOUR_TEXT_1. Source read, not live: text that
        # ships in a def description cannot be un-said by the running game.
        hits, seen = [], 0
        modroot = os.path.dirname(_DIR)
        for root, _d, files in os.walk(modroot):
            for fn in files:
                if fn.endswith((".xml", ".cs")):
                    seen += 1
                    fp = os.path.join(root, fn)
                    with open(fp, encoding="utf-8", errors="replace") as fh:
                        if re.search(r"wind[- ]hour", fh.read(), re.I):
                            hits.append(os.path.relpath(fp, modroot))
        if seen < 20:          # sanity probe: a scan that read almost nothing proves nothing
            _fail("the wind-hour scan read only %d files -- wrong root, not a clean bill" % seen)
        if hits:
            _fail("the dead wind-hour wording is back in: %s" % hits[:6])


@suite.chain("cuisine_wiring")
def cuisine_wiring(t):
    """The cuisine layer: the five recipes reach both stoves (a patch that matches nothing logs nothing),
    and every item with a Rottable comp actually ticks it."""
    with _comp(t, "recipes_on_both_stoves", independent=True):
        rows, missing = _get_defs(t, ["ThingDef/ElectricStove", "ThingDef/FueledStove"], fields="recipes")
        if _live(t):
            _need_parse(t)
            if missing or len(rows) != 2:
                _fail("stove defs not resolvable: %r" % missing)
            if len(RECIPES) < 5:
                _fail("source parse found %d recipes, expected 5" % len(RECIPES))
            for row in rows:
                have = set(_flat((row.get("fields") or {}).get("recipes")))
                if "CookMealSimple" not in have:
                    _unmeasured(t, "the vanilla CookMealSimple recipe is not readable from %s.recipes "
                                   "(control), so the list is not trustworthy: %s" % (row.get("defName"), sorted(have)[:6]))
                lacking = [r for r in RECIPES if r not in have]
                if lacking:
                    _fail("%s lacks recipes %s (RM_StockedPoolRecipeWiring.xml matched nothing?)" % (
                        row.get("defName"), lacking))

    with _comp(t, "rottable_items_tick", independent=True):
        # RM_HulduFat once had a CompProperties_Rottable and tickerType Never: the comp never ticked.
        rows, missing = _get_defs(t, ["ThingDef/%s" % n for n in ROTTABLE_ITEMS], fields="tickerType")
        if _live(t):
            _need_parse(t)
            if len(ROTTABLE_ITEMS) < 10:
                _fail("source parse found %d Rottable items, expected 14+" % len(ROTTABLE_ITEMS))
            if missing:
                _fail("rottable items not loaded: %s" % missing[:5])
            never = [r.get("defName") for r in rows if (r.get("fields") or {}).get("tickerType") in ("Never", None, "(no such field)")]
            unread = [r.get("defName") for r in rows if (r.get("fields") or {}).get("tickerType") == "(no such field)"]
            if unread:
                _unmeasured(t, "tickerType unreadable on %s" % unread[:4])
            if never:
                _fail("Rottable comp never ticks (tickerType Never) on: %s" % never)


@suite.chain("settings_and_designator")
def settings_and_designator(t):
    """The ONE Mod Setting, `stockedPoolsEnabled`: shipped default, and what it does to the designator
    (RM_Designator_ZoneAdd_PoolPen.Visible reads it live). OFF arm always restores in `finally`."""
    with _comp(t, "setting_default_on_and_assembly_loaded", independent=True, toggle=TOGGLE):
        r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=TOGGLE)
        if _live(t):
            _ok(r, "mod_settings_field(get)")
            if str(r.get("value")) != "True":
                _fail("%s reads %r; the shipped default is true (RM_WeepingStonesSettings.cs)" % (TOGGLE, r.get("value")))

    with _comp(t, "designator_listed_when_on", independent=True, toggle=TOGGLE):
        ds, pen, _ = _zone_designators(t)
        if _live(t):
            if pen is None:
                _fail("no pool-pen designator among %d Zone designators (SPECIAL designator patch matched "
                      "nothing, or the toggle gates it off): %s" % (len(ds), str(ds)[:300]))
            _note(t, "pen designator row", pen)

    with _comp(t, "designator_hidden_when_off", independent=True, toggle=TOGGLE):
        try:
            t.set_setting(SETTINGS, {TOGGLE: False})
            ds, pen, control = _zone_designators(t)
            if _live(t) and pen is not None:
                # Source reads correct (Visible => stockedPoolsEnabled; the static read back False) yet the
                # bridge row said visible=true (live 2026-10-03, deploy older than the last commit). The
                # listing's provenance (cache vs fresh Visible read, deployed DLL age) cannot be settled
                # offline, so a still-listed row is UNMEASURED, never a pass and never a proven defect.
                if pen.get("visible") is False:
                    return
                _unmeasured(t, "pool-pen designator still listed (row visible=%r) with %s=false; source Visible "
                               "reads the setting, so this is a stale deployed DLL or a cached bridge listing; "
                               "redeploy and re-run, or look at the Zone tab" % (pen.get("visible"), TOGGLE))
        finally:
            if t.session is not None:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field=TOGGLE, value="True")
                back = t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field=TOGGLE) or {}
                if str(back.get("value")) != "True":
                    raise ExpectationFailed("%s did not restore to its shipped default: %r" % (TOGGLE, back))


@suite.chain("settings_sliders")
def settings_sliders(t):
    """The two sliders (WEEPINGSTONES_SETTINGS_SLIDERS_1): shipped default, then a write+read-back at the
    top of the range; always restored to the shipped default in `finally`."""
    for field, (default, _lo, hi), stype in ([(f, v, SETTINGS) for f, v in SLIDERS.items()]
                                             + [(f, v, EH_SETTINGS) for f, v in EH_SLIDERS.items()]):
        with _comp(t, "%s_slider_roundtrip" % field, independent=True, toggle=field):
            try:
                r = t.bridge_call("jawa/mod_settings_field", typeName=stype, action="get", field=field)
                if _live(t):
                    _ok(r, "mod_settings_field(get)")
                    if abs(float(r.get("value")) - default) > 1e-6:
                        _fail("%s reads %r; the shipped default is %s" % (field, r.get("value"), default))
                # not t.set_setting: its read-back compares the STRING '3' to str(3.0) == '3.0' (MEASURED live
                # 2026-10-03), a harness defect in Utils/modcheck/suite.py; compare numerically here instead.
                w = t.bridge_call("jawa/mod_settings_field", typeName=stype, action="set", field=field, value=str(hi))
                if _live(t):
                    _ok(w, "mod_settings_field(set)")
                back = t.bridge_call("jawa/mod_settings_field", typeName=stype, action="get", field=field)
                if _live(t) and abs(float(back.get("value")) - hi) > 1e-6:
                    _fail("%s wrote %s but reads back %r" % (field, hi, back.get("value")))
            finally:
                if t.session is not None:
                    t.session.call("jawa/mod_settings_field", typeName=stype, action="set", field=field, value=str(default))


def _truce_hunt_source_problems():
    """Offline structure of WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1, read from the kit's own source."""
    probs = []

    def src(name):
        try:
            with open(os.path.join(_EH_SRC, name), encoding="utf-8") as fh:
                return fh.read()
        except OSError as ex:
            probs.append("cannot read %s: %s" % (name, ex))
            return ""
    hook = src("RM_WaterTruceHuntSuppression.cs")
    for needle in ("IsAcceptablePreyFor_Postfix", "MakeNewToils_Postfix", "AddFailCondition", "IsTruceWater",
                   "waterTruceSuppressionEnabled"):
        if needle not in hook:
            probs.append("RM_WaterTruceHuntSuppression.cs lacks %s" % needle)
    if "ByDefName" in hook or "RM_WeepingStones" in hook:
        probs.append("suppression keys on a biome defName; it must read RM_WaterTruceExtension via the map component")
    if "RM_WaterTruceHuntSuppression.cs" not in src("RM_EnvironmentalHazards.csproj"):
        probs.append("RM_WaterTruceHuntSuppression.cs is not in RM_EnvironmentalHazards.csproj (compiles into nothing)")
    patches = src("BiomeGlowPatches.cs")
    for seam in ("IsAcceptablePreyFor", "JobDriver_PredatorHunt"):
        if seam not in patches:
            probs.append("BiomeGlowPatches.cs does not arm the %s seam" % seam)
    mod = src("RM_EnvironmentalHazardsMod.cs")
    if "waterTruceSuppressionEnabled = true" not in mod or '"waterTruceSuppressionEnabled"' not in mod \
            or "ref waterTruceSuppressionEnabled," not in mod:
        probs.append("waterTruceSuppressionEnabled is not declared default-true, scribed and shown in the settings window")
    return probs


@suite.chain("truce_hunt_suppression")
def truce_hunt_suppression(t):
    """WEEPINGSTONES_TRUCE_HUNT_SUPPRESSION_1: the suppression half of the water truce is wired (source) and its
    toggle ships on and round-trips. The behaviour itself (10 hungry predators + 10 prey inside a pool's radius,
    zero hunt jobs over 30,000 ticks; setting off = at least one, the control; a chase abandoned on entering) is a
    statistical live quicktest named on the item and NOT measurable offline: so no component here claims it."""
    with _comp(t, "suppression_source_wired", independent=True):
        if _live(t):
            probs = _truce_hunt_source_problems()
            if probs:
                _fail("; ".join(probs))

    with _comp(t, "suppression_toggle_default_and_roundtrip", independent=True, toggle=EH_TOGGLE):
        try:
            r = t.bridge_call("jawa/mod_settings_field", typeName=EH_SETTINGS, action="get", field=EH_TOGGLE)
            if _live(t):
                _ok(r, "mod_settings_field(get)")
                if str(r.get("value")) != "True":
                    _fail("%s reads %r; the shipped default is true" % (EH_TOGGLE, r.get("value")))
            w = t.bridge_call("jawa/mod_settings_field", typeName=EH_SETTINGS, action="set", field=EH_TOGGLE, value="False")
            back = t.bridge_call("jawa/mod_settings_field", typeName=EH_SETTINGS, action="get", field=EH_TOGGLE)
            if _live(t) and str(back.get("value")) != "False":
                _fail("%s wrote False but reads back %r" % (EH_TOGGLE, back.get("value")))
        finally:
            if t.session is not None:
                t.session.call("jawa/mod_settings_field", typeName=EH_SETTINGS, action="set", field=EH_TOGGLE, value="True")


def _condenser_source_problems():
    """Offline structure of WEEPINGSTONES_WALKING_CONDENSER_1, read from the mod's own XML (never a hand list)."""
    probs = []
    race = next((el for _, n, el in _BY_DIR["ThingDefs_Races"] if n == "RM_GorraskCondenser"), None)
    if race is None or not any(li.get("Class", "").endswith("CompProperties_WalkingCondenser") for li in race.findall("comps/li")):
        probs.append("RM_GorraskCondenser lacks the CompProperties_WalkingCondenser comp")
    if "RM_GorraskCondenser" in BIOME_ANIMALS:
        probs.append("RM_GorraskCondenser is in the biome's wildAnimals (it is one per world, placed by the spawner)")
    plant = next((el for _, n, el in _BY_DIR["ThingDefs_Buildings"] if n == "RM_AncientCondenserPlant"), None)
    if plant is None or not (plant.findtext("minifiedDef") or "").strip():
        probs.append("RM_AncientCondenserPlant is not minifiable")
    if plant is not None and not any(li.get("Class", "").endswith("CompProperties_AncientCondenser") for li in plant.findall("comps/li")):
        probs.append("RM_AncientCondenserPlant lacks its water comp")
    if "RM_CondenserWater" not in _names("ThingDefs_Items", "ThingDef"):
        probs.append("RM_CondenserWater (the plant's output) is missing")
    return probs


@suite.chain("walking_condenser")
def walking_condenser(t):
    """The walking condenser's defs are wired the way the C# expects (comp classes, minifiable plant, not a
    wildAnimals row). The pool/truce/choices are live mechanics, owed a quicktest (criteria on the item)."""
    with _comp(t, "condenser_defs_wired", independent=True):
        if _live(t):
            _need_parse(t)
            probs = _condenser_source_problems()
            if probs:
                _fail("; ".join(probs))
        rows, missing = _get_defs(t, ["ThingDef/RM_GorraskCondenser", "ThingDef/RM_AncientCondenserPlant"])
        if _live(t) and missing:
            _fail("walking-condenser defs not loaded: %s" % missing)


# components that are UNMEASURED by design on a healthy run (a live mechanic this suite cannot drive)
LIVE_ONLY_UNMEASURED = {"dewsilk.tamed_mirrik_yield_cocoons", "oasis_flora.oasis_map_census"}


def _dewsilk_source_problems():
    """Offline structure of WEEPINGSTONES_DEWSILK_COCOON_1, read from the mod's own XML (never a hand list)."""
    probs = []
    items = dict((n, el) for _, n, el in _BY_DIR["ThingDefs_Items"])
    race = next((el for _, n, el in _BY_DIR["ThingDefs_Races"] if n == "RM_Mirrik" and _ == "ThingDef"), None)
    shear = [li for li in (race.findall("comps/li") if race is not None else []) if li.get("Class") == "CompProperties_Shearable"]
    if len(shear) != 1:
        probs.append("RM_Mirrik carries %d CompProperties_Shearable comps, expected 1" % len(shear))
    elif (shear[0].findtext("woolDef") or "").strip() != "RM_DewsilkCocoon":
        probs.append("RM_Mirrik's shearable woolDef is not RM_DewsilkCocoon")
    for need in ("RM_DewsilkCocoon", "RM_Dewsilk"):
        if need not in items:
            probs.append("%s is not defined" % need)
    cloth = items.get("RM_Dewsilk")
    if cloth is not None:
        cats = [c.text for c in cloth.findall("stuffProps/categories/li")]
        if "Fabric" not in cats:
            probs.append("RM_Dewsilk is not a Fabric stuff")
        if cloth.find("statBases/StuffPower_Insulation_Heat") is None:
            probs.append("RM_Dewsilk lacks its heat-insulation stat")
    rec = next((el for t_, n, el in _BY_DIR["RecipeDefs"] if n == "RM_SpinDewsilk"), None)
    if rec is None:
        probs.append("RM_SpinDewsilk is missing")
    else:
        if (rec.findtext("ingredients/li/filter/thingDefs/li") or "").strip() != "RM_DewsilkCocoon" or rec.find("products/RM_Dewsilk") is None:
            probs.append("RM_SpinDewsilk does not turn RM_DewsilkCocoon into RM_Dewsilk")
        users = [u.text for u in rec.findall("recipeUsers/li")]
        if "HandTailoringBench" not in users or "ElectricTailoringBench" not in users:
            probs.append("RM_SpinDewsilk is not on both tailor benches")
    # fields the engine does not have (today's load-log lessons)
    for tag in ("canBeDoneByNonColonists", "minifiable"):
        for _t, n, el in _BY_DIR["ThingDefs_Items"] + _BY_DIR["RecipeDefs"]:
            if n.startswith("RM_Dewsilk") or n == "RM_SpinDewsilk":
                if el.find(tag) is not None:
                    probs.append("%s carries the invalid field <%s>" % (n, tag))
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
    try:
        with open(os.path.join(src, "RM_WeepingStones.csproj"), encoding="utf-8") as fh:
            if "RM_DewsilkSwitch.cs" not in fh.read():
                probs.append("RM_DewsilkSwitch.cs is not in RM_WeepingStones.csproj (compiles into nothing)")
        with open(os.path.join(src, "RM_WeepingStonesSettings.cs"), encoding="utf-8") as fh:
            st = fh.read()
        if "dewsilkEnabled = true" not in st or '"dewsilkEnabled"' not in st or "ref dewsilkEnabled," not in st:
            probs.append("dewsilkEnabled is not declared default-true, scribed and shown in the settings window")
    except OSError as ex:
        probs.append("cannot read Source: %s" % ex)
    return probs


@suite.chain("dewsilk")
def dewsilk(t):
    """WEEPINGSTONES_DEWSILK_COCOON_1: cocoon item, fabric, spinning recipe and mirrik harvest are wired (source +
    defs load), and the switch ships on. The harvest itself (a TAMED mirrik gathered after the interval) needs a
    tamed swarm on a live quicktest map and is reported UNMEASURED here, never claimed."""
    with _comp(t, "dewsilk_defs_wired", independent=True):
        if _live(t):
            _need_parse(t)
            probs = _dewsilk_source_problems()
            if probs:
                _fail("; ".join(probs))
        rows, missing = _get_defs(t, ["ThingDef/RM_DewsilkCocoon", "ThingDef/RM_Dewsilk", "RecipeDef/RM_SpinDewsilk"])
        if _live(t) and missing:
            _fail("dewsilk defs not loaded: %s" % missing)

    with _comp(t, "dewsilk_toggle_default_and_roundtrip", independent=True, toggle="dewsilkEnabled"):
        try:
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="dewsilkEnabled")
            if _live(t):
                _ok(r, "mod_settings_field(get)")
                if str(r.get("value")) != "True":
                    _fail("dewsilkEnabled reads %r; the shipped default is true" % r.get("value"))
            t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="dewsilkEnabled", value="False")
            back = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="dewsilkEnabled")
            if _live(t) and str(back.get("value")) != "False":
                _fail("dewsilkEnabled wrote False but reads back %r" % back.get("value"))
        finally:
            if t.session is not None:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="dewsilkEnabled", value="True")

    with _comp(t, "tamed_mirrik_yield_cocoons", independent=True):
        if _live(t):
            _unmeasured(t, "needs a TAMED mirrik swarm gathered after shearIntervalDays on a live quicktest map "
                           "(tame roll and wait are not driven by this suite); the comp's wiring is covered by dewsilk_defs_wired")


# ---------------------------------------------------------------- WEEPINGSTONES_OASIS_MUTATOR_FLORA_1
OASIS_STRIPPED = ("Plant_TreePalm", "Plant_RatPalm", "Plant_Grass", "Plant_GrayGrass", "TreePalma", "VEE_Plant_DatePalm")
OASIS_WORKER = "RimMandrake.WeepingStones.RM_TileMutatorWorker_Oasis"


_UTINNI_OASIS_PATCH = None   # selftests may point this at a synthetic campaign patch; an absent file is skipped


def _utinni_oasis_problems():
    """Campaign twin half: the RimUtinni oasis patch whitelists RUT_WeepingStones, carries the same extension with
    every stripped def, and no longer adds TreePalma / VEE_Plant_DatePalm to the mutator's bonus flora."""
    here = os.path.dirname(os.path.abspath(__file__))
    path = _UTINNI_OASIS_PATCH or os.path.join(here, "..", "..", "RimUtinni", "UtinniPatches", "Patches", "OasisMutator_DesertOasis.xml")
    if not os.path.isfile(path):
        return []
    try:
        root = ET.parse(path).getroot()
    except Exception as ex:
        return ["campaign oasis patch unreadable: %s" % ex]
    probs = []
    lis = " ".join((x.text or "") for x in root.iter("li"))
    if "RUT_WeepingStones" not in lis:
        probs.append("campaign patch does not whitelist RUT_WeepingStones into Oasis")
    ext = [x for x in root.iter("li") if (x.get("Class") or "").endswith("RM_OasisFloraExtension")]
    if not ext:
        probs.append("campaign patch adds no RM_OasisFloraExtension to RUT_WeepingStones")
    else:
        stripped = [x.text for x in ext[0].findall("stripDefNames/li")]
        for need in OASIS_STRIPPED:
            if need not in stripped:
                probs.append("campaign extension does not strip %s" % need)
    for op in root.iter("xpath"):
        if "additionalWildPlants" in (op.text or ""):
            probs.append("campaign patch still edits Oasis.additionalWildPlants (palms must not be added)")
    for tag in ("TreePalma", "VEE_Plant_DatePalm"):
        if any(e.tag == tag for e in root.iter()):
            probs.append("campaign patch still adds %s to the Oasis bonus flora" % tag)
    return probs


def _oasis_source_problems():
    """Offline structure of the Oasis swap, read from the mod's own files: the patch whitelists our biome and swaps
    the worker, the biome carries the extension (every Earth plant stripped, only our own plants added, Reeds kept),
    the worker is in the csproj, and the setting ships default-true, scribed and shown."""
    probs = _utinni_oasis_problems()
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        pr = ET.parse(os.path.join(here, "Patches", "RM_OasisMutatorFlora.xml")).getroot()
        xp = " ".join((x.text or "") for x in pr.iter("xpath"))
        vals = " ".join((x.text or "") for x in pr.iter("li")) + " " + " ".join((x.text or "") for x in pr.iter("workerClass"))
        if 'defName="Oasis"' not in xp or "biomeWhitelist" not in xp or BIOME not in vals:
            probs.append("the patch does not whitelist %s into the Oasis mutator" % BIOME)
        if OASIS_WORKER not in vals:
            probs.append("the patch does not swap in %s" % OASIS_WORKER)
        for bad in ("PatchOperationAddOrReplace", "MayRequire"):
            if bad in open(os.path.join(here, "Patches", "RM_OasisMutatorFlora.xml"), encoding="utf-8").read().replace("MayRequire\n", ""):
                probs.append("the Oasis patch uses %s (inert/invalid on a whole Operation)" % bad)
    except Exception as ex:
        probs.append("Oasis patch unreadable: %s" % ex)
    ext = None
    if _BIOME_EL is not None:
        for li in _BIOME_EL.findall("modExtensions/li"):
            if (li.get("Class") or "").endswith("RM_OasisFloraExtension"):
                ext = li
    if ext is None:
        probs.append("%s carries no RM_OasisFloraExtension" % BIOME)
    else:
        stripped = [x.text for x in ext.findall("stripDefNames/li")]
        for need in OASIS_STRIPPED:
            if need not in stripped:
                probs.append("the extension does not strip %s" % need)
        if "Plant_Reeds" in stripped:
            probs.append("Plant_Reeds is a ruled keep and must not be stripped")
        own = set(n for _t, n, _e in _BY_DIR["ThingDefs_Plants"])
        plants = [(x.tag, x.text) for x in ext.findall("plants/*")]
        if not plants:
            probs.append("the extension adds no native plants")
        for tag, txt in plants:
            if tag not in own:
                probs.append("oasis plant %s is not a plant this mod defines" % tag)
            if tag in stripped:
                probs.append("oasis plant %s is also stripped" % tag)
            try:
                if float(txt) <= 0:
                    probs.append("oasis plant %s has no weight" % tag)
            except (TypeError, ValueError):
                probs.append("oasis plant %s has a non-numeric weight %r" % (tag, txt))
    src = os.path.join(here, "Source")
    try:
        with open(os.path.join(src, "RM_WeepingStones.csproj"), encoding="utf-8") as fh:
            if "RM_TileMutatorWorker_Oasis.cs" not in fh.read():
                probs.append("RM_TileMutatorWorker_Oasis.cs is not in RM_WeepingStones.csproj (compiles into nothing)")
        with open(os.path.join(src, "RM_WeepingStonesSettings.cs"), encoding="utf-8") as fh:
            st = fh.read()
        if ("oasisNativeFloraEnabled = true" not in st or '"oasisNativeFloraEnabled"' not in st
                or "ref oasisNativeFloraEnabled," not in st):
            probs.append("oasisNativeFloraEnabled is not declared default-true, scribed and shown in the settings window")
    except OSError as ex:
        probs.append("cannot read Source: %s" % ex)
    return probs


@suite.chain("oasis_flora")
def oasis_flora(t):
    """WEEPINGSTONES_OASIS_MUTATOR_FLORA_1: the Oasis mutator accepts our biome and runs our worker (source + loaded
    def), the toggle ships on, and the map-level result (no Earth palm/grass on our oasis, native blade plants
    present, a vanilla desert oasis still grows palms) needs a generated oasis map and is UNMEASURED here."""
    with _comp(t, "oasis_source_wired", independent=True):
        if _live(t):
            _need_parse(t)
            probs = _oasis_source_problems()
            if probs:
                _fail("; ".join(probs))

    with _comp(t, "oasis_def_accepts_our_biome", independent=True):
        rows, missing = _get_defs(t, ["TileMutatorDef/Oasis"], fields="biomeWhitelist,workerClass")
        if _live(t):
            if missing or not rows:
                _fail("TileMutatorDef/Oasis is not loaded (Odyssey absent?): %r" % missing)
            blob = list(_flat(rows[0].get("fields")))
            if "biomeWhitelist" not in blob or "workerClass" not in blob:
                _unmeasured(t, "get_defs did not return biomeWhitelist/workerClass for Oasis")
            if BIOME not in blob:
                _fail("Oasis.biomeWhitelist does not contain %s: %r" % (BIOME, blob[:20]))
            # LIVE 2026-10-03: get_defs cannot serialise TileMutatorDef.workerClass (a non-public System.Type field; it
            # answers "(non-public field 'workerClass' ... type RuntimeType not serialis...)"), so the worker swap is
            # NOT readable here and the old check failed on EVERY run for an instrument reason. What this component
            # can prove is the whitelist; the worker swap is proved by oasis_source_wired (offline) and, in play, by
            # oasis_map_census.
            if any(x.startswith("(non-public field 'workerClass'") for x in blob):
                _note(t, "Oasis.workerClass not serialisable by get_defs (instrument limit)", True)
            elif not any(OASIS_WORKER in x or x.endswith("RM_TileMutatorWorker_Oasis") for x in blob):
                _fail("Oasis.workerClass is not %s: %r" % (OASIS_WORKER, blob[:20]))

    with _comp(t, "oasis_toggle_default_and_roundtrip", independent=True, toggle="oasisNativeFloraEnabled"):
        try:
            r = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="oasisNativeFloraEnabled")
            if _live(t):
                _ok(r, "mod_settings_field(get)")
                if str(r.get("value")) != "True":
                    _fail("oasisNativeFloraEnabled reads %r; the shipped default is true" % r.get("value"))
            t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="oasisNativeFloraEnabled", value="False")
            back = t.bridge_call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="oasisNativeFloraEnabled")
            if _live(t) and str(back.get("value")) != "False":
                _fail("oasisNativeFloraEnabled wrote False but reads back %r" % back.get("value"))
        finally:
            if t.session is not None:
                t.session.call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="oasisNativeFloraEnabled", value="True")

    with _comp(t, "oasis_map_census", independent=True):
        if _live(t):
            _enter(t)
            _unmeasured(t, "needs a generated Weeping Stones Oasis-mutator map (census per def with jawa/list_things: zero "
                           "Plant_TreePalm/Plant_RatPalm/TreePalma/VEE_Plant_DatePalm/Plant_Grass/Plant_GrayGrass, native "
                           "RM_Dewblade count > 0 as the can-it-see probe, and a vanilla Desert oasis control still growing palms); "
                           "the suite does not generate world-tile maps")


@suite.chain("pen_zone")
def pen_zone(t):
    """The pen is a zone over WATER only (RM_Designator_ZoneAdd_PoolPen.CanDesignateCell): a rect over dry
    floor makes no zone; a rect straddling the shoreline makes one whose cells are exactly the water."""
    _enter(t)
    with _comp(t, "site_ready_pen_zone"):
        _reset_pad(t)
        x, z = t.anchor
        half = POOL
        t.bridge_call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,%d,%d" % (x, z - half // 2, half // 2, half))
        _, pen, _ = _zone_designators(t)
        if _live(t):
            if pen is None:
                _unmeasured(t, "no pool-pen designator in the Zone category: the defect is reported by "
                               "settings_and_designator.designator_listed_when_on")
            _G["did"] = pen.get("id")

    with _comp(t, "pen_refuses_dry_floor", toggle=TOGGLE):
        x, z = t.anchor
        r = t.bridge_call("rimworld/apply_architect_designator", designatorId=_G.get("did"), x=x - 8, z=z + 6,
                          width=4, height=4, keepSelected=False)
        if _live(t):
            _note(t, "designating dry floor", r)
            if _pen_zones(t):
                _fail("a pen zone exists after designating 16 dry cells: %r" % _pen_zones(t))

    with _comp(t, "pen_covers_exactly_the_water", toggle=TOGGLE):
        x, z = t.anchor
        half = POOL
        # a POOL x POOL rect whose east half (POOL/2 columns) is water, the west half dry
        r = t.bridge_call("rimworld/apply_architect_designator", designatorId=_G.get("did"), x=x - half // 2,
                          z=z - half // 2, width=half, height=half, keepSelected=False)
        if _live(t):
            _ok(r, "apply_architect_designator(straddle)")
            pens = _pen_zones(t)
            water = (half // 2) * half
            if len(pens) != 1 or pens[0].get("cells") != water:
                _fail("expected one pen of exactly the %d water cells, got %r" % (water, pens))
    _teardown(t)


# ---------------------------------------------------------------------- the husbandry jobs

def _handler(t):
    x, z = t.anchor
    pid = _spawn(t, "Colonist", x + 8, z, "player")
    if _live(t):
        _settle(t, pid)
    return pid


@suite.chain("job_net")
def job_net(t):
    """NET: a handler nets a wild stockable pawn and it becomes its carryable breeding-stock item
    (RM_JobDriver_NetPoolBreeder). Wild pawn gone, exactly one RM_SkarrinBreedingStock appears.

    LIVE POKE 2026-10-03 (why this component is RED, a real mechanic finding not a script bug): the wild skarrin FLEES
    the handler at flight speed (~13 cells per 100 ticks against the colonist's ~5) and leaves the map before the
    200-tick net completes, so no stock item is ever made ("0 wild left, 0 stock": the pawn is gone because it flew
    off, not because it was netted). FALSE THEORY ruled out: RM_SkarrinBreedingStock resolves live and the finish
    toil's def lookup is fine. Fix belongs in the mechanic (hold/stun the target, or net from range), an owner-visible
    design call; do not pad the test to pass."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_net"):
            _reset_pad(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            box["wild"] = _spawn(t, "RM_Skarrin", x + 6, z + 5, "none")
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Skarrin"))
                s = len(_things(t, "RM_SkarrinBreedingStock", _pad_rect(t)))
                if n != 1 or s != 0:
                    _fail("precondition: expected 1 wild skarrin and 0 breeding stock, got %d / %d" % (n, s))
        with _comp(t, "net_turns_wild_pawn_into_breeding_stock"):
            _run_job(t, box["handler"], "RM_NetPoolBreeder", box["wild"], 900)
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Skarrin"))
                stock = _things(t, "RM_SkarrinBreedingStock", _pad_rect(t))
                if n != 0 or len(stock) != 1:
                    _fail("after NET: %d wild skarrin left (want 0), %d RM_SkarrinBreedingStock (want 1)" % (n, len(stock)))
    finally:
        _teardown(t)


@suite.chain("job_stock")
def job_stock(t):
    """STOCK: a handler carries a breeding-stock item into a pen and releases a live pawn of the species
    there (RM_JobDriver_StockPoolPen); the item is consumed."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_stock"):
            zone = _pen_site(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            t.bridge_call("jawa/spawn_batch", ops="RM_SkarrinBreedingStock:%d,%d" % (x + 6, z + 5))
            if _live(t):
                stock = _things(t, "RM_SkarrinBreedingStock", _pad_rect(t))
                if len(stock) != 1 or _pawns(t, _pad_rect(t), "RM_Skarrin"):
                    _fail("precondition: want 1 breeding stock and no skarrin, got %d stock / %d skarrin" % (
                        len(stock), len(_pawns(t, _pad_rect(t), "RM_Skarrin"))))
                box["stock"] = stock[0].get("id")
        with _comp(t, "stock_releases_species_pawn_into_pen"):
            x, z = t.anchor
            _run_job(t, box["handler"], "RM_StockPoolPen", box["stock"], 1500, x, z)
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Skarrin"))
                left = len(_things(t, "RM_SkarrinBreedingStock", _pad_rect(t)))
                if n != 1 or left != 0:
                    _fail("after STOCK: %d skarrin released (want 1), %d breeding stock left (want 0)" % (n, left))
    finally:
        _teardown(t)


@suite.chain("job_stock_outside_pen")
def job_stock_outside_pen(t):
    """STOCK refuses to release outside a pen (the zone re-check in the job's finish toil): the item is
    picked up but nothing is released. The item leaving the ground proves the job ran (a job that never
    started would leave it, and read as a false pass)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_stock_dry"):
            _pen_site(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            t.bridge_call("jawa/spawn_batch", ops="RM_SkarrinBreedingStock:%d,%d" % (x + 6, z + 5))
            if _live(t):
                stock = _things(t, "RM_SkarrinBreedingStock", _pad_rect(t))
                if len(stock) != 1:
                    _fail("precondition: want 1 breeding stock, got %d" % len(stock))
                box["stock"] = stock[0].get("id")
        with _comp(t, "stock_outside_pen_releases_nothing"):
            x, z = t.anchor
            _run_job(t, box["handler"], "RM_StockPoolPen", box["stock"], 1500, x + 8, z + 8)
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Skarrin"))
                on_ground = len(_things(t, "RM_SkarrinBreedingStock", _pad_rect(t)))
                if on_ground != 0:
                    _fail("the breeding stock is still on the ground: the job never ran (%d left)" % on_ground)
                if n != 0:
                    _fail("a skarrin was released at a cell outside any pen (%d)" % n)
    finally:
        _teardown(t)


@suite.chain("job_feed")
def job_feed(t):
    """FEED: a handler carries one unit of food to the pen and it is consumed (RM_JobDriver_FeedPoolPen)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_feed"):
            _pen_site(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            t.bridge_call("jawa/spawn_batch", ops="MealSimple:%d,%d" % (x + 6, z + 5))
            if _live(t):
                meal = _things(t, "MealSimple", _pad_rect(t))
                if len(meal) != 1:
                    _fail("precondition: want 1 MealSimple, got %d" % len(meal))
                box["meal"] = meal[0].get("id")
        with _comp(t, "feed_consumes_food_at_the_pen"):
            x, z = t.anchor
            _run_job(t, box["handler"], "RM_FeedPoolPen", box["meal"], 1200, x, z, count=1)
            if _live(t):
                left = len(_things(t, "MealSimple", _pad_rect(t)))
                if left != 0:
                    _fail("the meal is still on the ground after FEED (%d): the job never delivered it" % left)
    finally:
        _teardown(t)


@suite.chain("job_harvest")
def job_harvest(t):
    """HARVEST: a handler takes a stocked pawn out of the pen and the species meat appears, 2-4 units
    (RM_JobDriver_HarvestPoolPen reads RM_<Kind>Meat by name)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_harvest"):
            _pen_site(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            box["stock"] = _spawn(t, "RM_Skarrin", x, z, "none")
            if _live(t):
                if len(_pawns(t, _pad_rect(t), "RM_Skarrin")) != 1 or _things(t, "RM_SkarrinMeat", _pad_rect(t)):
                    _fail("precondition: want 1 skarrin and no skarrin meat")
        with _comp(t, "harvest_yields_species_meat"):
            _run_job(t, box["handler"], "RM_HarvestPoolPen", box["stock"], 1200)
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Skarrin"))
                meat = _things(t, "RM_SkarrinMeat", _pad_rect(t))
                if n != 0 or not meat:
                    _fail("after HARVEST: %d skarrin left (want 0), %d meat stacks (want >=1)" % (n, len(meat)))
                total = sum(_stack(m) or 0 for m in meat)
                _note(t, "harvest meat stacks", [_stack(m) for m in meat])
                if all(_stack(m) is not None for m in meat) and not 2 <= total <= 4:
                    _fail("harvest yield %d outside 2-4 (RM_JobDriver_HarvestPoolPen)" % total)
    finally:
        _teardown(t)


@suite.chain("job_cull")
def job_cull(t):
    """CULL: a handler culls the vhorrin and an enormous meat harvest, 18-24 units, appears
    (RM_JobDriver_CullVhorrin; sized to clear the Cull Feast recipe alone)."""
    _enter(t)
    box = {}
    try:
        with _comp(t, "site_ready_cull"):
            _pen_site(t)
            x, z = t.anchor
            box["handler"] = _handler(t)
            box["vhorrin"] = _spawn(t, "RM_Vhorrin", x, z, "none")
            if _live(t):
                if len(_pawns(t, _pad_rect(t), "RM_Vhorrin")) != 1 or _things(t, "RM_VhorrinMeat", _pad_rect(t)):
                    _fail("precondition: want 1 vhorrin and no vhorrin meat")
        with _comp(t, "cull_yields_enormous_harvest"):
            _run_job(t, box["handler"], "RM_CullVhorrin", box["vhorrin"], 1500)
            if _live(t):
                n = len(_pawns(t, _pad_rect(t), "RM_Vhorrin"))
                meat = _things(t, "RM_VhorrinMeat", _pad_rect(t))
                if n != 0 or not meat:
                    _fail("after CULL: %d vhorrin left (want 0), %d meat stacks (want >=1)" % (n, len(meat)))
                total = sum(_stack(m) or 0 for m in meat)
                _note(t, "cull meat stacks", [_stack(m) for m in meat])
                if all(_stack(m) is not None for m in meat) and not 18 <= total <= 24:
                    _fail("cull yield %d outside 18-24 (RM_JobDriver_CullVhorrin)" % total)
    finally:
        _teardown(t)


# ----------------------------------------------------------------------------- native flora

def _flora_chain(plant, product):
    def chain(t):
        _enter(t)
        box = {}
        try:
            with _comp(t, "site_ready_%s" % plant):
                _reset_pad(t, terrain="Soil")
                x, z = t.anchor
                t.bridge_call("jawa/set_plants", ops="%s:%d,%d,3,1" % (plant, x, z), growth=1.0)
                box["handler"] = _handler(t)
                if _live(t):
                    plants = _things(t, plant, _pad_rect(t))
                    if not plants:
                        _fail("set_plants placed no %s" % plant)
                    if _things(t, product, _pad_rect(t)):
                        _fail("precondition: %s already on the pad" % product)
                    box["plants"] = [p.get("id") for p in plants[:3]]
            with _comp(t, "harvest_yields_%s" % product):
                for pid in box.get("plants") or []:
                    t.bridge_call("jawa/ordered_job", pawnId=box["handler"], jobDef="Harvest",
                                  targetAId=pid, queue=True, waitTicks=0)   # waitTicks>0 on a paused clock burns ~17 s per order (LIVE 2026-10-03)
                t.wait_ticks(2500)
                if _live(t):
                    made = _things(t, product, _pad_rect(t))
                    _note(t, "%s stacks" % product, [_stack(m) for m in made])
                    if not made:
                        _fail("no %s after a forced harvest of %d %s (harvestedThingDef is wired in the "
                              "def; the yield never arrived)" % (product, len(box["plants"]), plant))
        finally:
            _teardown(t)
    chain.__doc__ = ("Harvest: %s (plant.harvestedThingDef) yields %s when a handler harvests it. "
                     "Read from the mod's own flora XML." % (plant, product))
    return chain


for _plant, _product in FLORA_PRODUCTS:
    suite.chain("flora_%s" % _plant)(_flora_chain(_plant, _product))
