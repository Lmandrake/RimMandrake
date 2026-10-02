"""validation.py -- modcheck suite for RimUtinni Ishko's Dark Landmarks
(mandrake.rut.ishkolandmarks).

Pure-XML content mod: no Source/, no C#, no ModSettings -- `suite.toggles = []`
and every component is `beyond_toggle=True`. The whole mod is
`Defs/LandmarkDefs_IshkoDark.xml` plus `About/About.xml`.

THE CONTENT (read off the XML):

    RUT_LightlessSink     category=mountain  commonality=0.08  Hollow Required=True
    RUT_ShadowedOverhang  category=mountain  commonality=0.08  Chasm  Required=True
    RUT_ColdLavaTube      category=mountain  commonality=0.06  Cavern Required=True

each `MayRequire="Ludeon.RimWorld.Odyssey"`, each `iconTexturePath`
`World/Landmarks/Ashkarr/{Hollow,Chasm,Cavern}`, supplied by
mandrake.rut.ashkarrlandmarkart.

Chains (walk: design/validation_walks/RimUtinni/IshkoDarkLandmarks.md):
  source      offline reads of our own XML and the art mod's PNGs (no bridge)
  defs        jawa/get_defs readback of the RESOLVED defs (deep=true: a
              List<MutatorChance> without deep comes back as bare type names,
              so the old substring check could never have passed live)
  placement   the BEHAVIOUR: jawa/world_landmarks_set add (forced) on a plain
              land tile -> the tile carries our landmark AND its Required anchor
              mutator. Engine fact (WorldLandmarks.AddLandmark, decompiled 1.6):
              a mutatorChance is added when `Rand.Chance(chance) && ((required &&
              forced) || mutator.IsValidTile(..))`; a Required entry has chance 1,
              so with forced=true the anchor is certain. Removed again afterwards
              (and the anchor mutator stripped if the tile did not have it).

RULED OUT (kept here and in the walk's anti-guessing notes):
  * "none of the three is placed on the planet" as a bar. The old chain read
    `row["defName"]` from jawa/world_landmarks_get, whose rows carry `def`, so
    it was vacuous -- it passed whatever the planet held. And on a quicktest
    world it is not even true by design: worldgen places LandmarkDefs by
    commonality, and ours have 0.06-0.08, so a generated world may carry one.
    Placement is the owner's hand on the ASH'KARR save, not a property a test
    world can witness.
"""
import os
import xml.etree.ElementTree as ET

from modcheck import Suite, ExpectationFailed

suite = Suite("IshkoDarkLandmarks")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

PACKAGE_ID = "mandrake.rut.ishkolandmarks"
LANDMARKS = [
    ("RUT_LightlessSink", "mountain", 0.08, "Hollow"),
    ("RUT_ShadowedOverhang", "mountain", 0.08, "Chasm"),
    ("RUT_ColdLavaTube", "mountain", 0.06, "Cavern"),
]
HERE = os.path.dirname(os.path.abspath(__file__))
DEFS_XML = os.path.join(HERE, "Defs", "LandmarkDefs_IshkoDark.xml")
ART_TEX = os.path.join(os.path.dirname(HERE), "AshkarrLandmarkArt", "Textures")
TILE_SCAN = "0-1999"          # world tiles examined for a placement candidate


class _Unmeasured(Exception):
    pass


def _unmeasured(t, why):
    """Stop this component as UNMEASURED (could not ask), never a pass or a fail."""
    t.upstream_failed = True
    t.upstream_reason = "UNMEASURED: " + why
    raise _Unmeasured(why)


class _independent(object):
    """`with _independent(t, name):` -- a component whose FAIL/UNMEASURED does not
    poison the next one (each landmark is its own read or its own tile)."""

    def __init__(self, t, name):
        self.t, self.name = t, name

    def __enter__(self):
        self.before = self.t.upstream_failed
        self.ctx = self.t.component(self.name, beyond_toggle=True)
        return self.ctx.__enter__()

    def __exit__(self, *exc):
        r = self.ctx.__exit__(*exc)
        if not self.before:
            self.t.upstream_failed = False
            self.t.upstream_reason = "upstream failed -- this chain's state is meaningless"
        return r


def _live(t):
    return t.session is not None


def _fail(msg):
    raise ExpectationFailed(msg)


# ------------------------------------------------------------------ source (offline)

def _parse_defs():
    root = ET.parse(DEFS_XML).getroot()
    out = {}
    for el in root.findall("LandmarkDef"):
        name = (el.findtext("defName") or "").strip()
        req = [m.tag for m in (el.find("mutatorChances") or [])
               if (m.get("Required") or "").lower() == "true"]
        out[name] = {"mayRequire": el.get("MayRequire"), "required": req,
                     "icon": (el.findtext("iconTexturePath") or "").strip()}
    return out


@suite.chain("source")
def source(t):
    """Our own files, read whole. Runs in the live run too: it is what the defs chain
    is checking the RESOLVED game against."""
    with _independent(t, "defs_gated_on_odyssey"):
        if not _live(t):
            return
        got = _parse_defs()
        t._record("defs in %s" % os.path.basename(DEFS_XML), sorted(got))
        if sorted(got) != sorted(n for n, _, _, _ in LANDMARKS):
            _fail("LandmarkDefs in the XML are %s, expected exactly %s"
                  % (sorted(got), [n for n, _, _, _ in LANDMARKS]))
        bad = [n for n, d in got.items() if d["mayRequire"] != "Ludeon.RimWorld.Odyssey"]
        if bad:
            _fail("not MayRequire=\"Ludeon.RimWorld.Odyssey\": %s" % bad)
    with _independent(t, "icons_supplied_by_art_mod"):
        if not _live(t):
            return
        if not os.path.isdir(ART_TEX):
            _unmeasured(t, "art mod source folder not found at %s" % ART_TEX)
        missing = []
        for n, d in _parse_defs().items():
            png = os.path.join(ART_TEX, *(d["icon"].split("/"))) + ".png"
            t._record("%s icon %s" % (n, d["icon"]), os.path.isfile(png))
            if not d["icon"] or not os.path.isfile(png):
                missing.append("%s -> %r" % (n, d["icon"]))
        if missing:
            _fail("iconTexturePath not supplied by AshkarrLandmarkArt: %s" % missing)


# ------------------------------------------------------------------ defs (live readback)

def _row(r, def_name):
    for d in (r or {}).get("defs") or []:
        if d.get("defName") == def_name:
            return d
    return None


def _chances(raw):
    """deep get_defs of List<MutatorChance> -> [(mutator, chance, required)]; [] if not structured."""
    out = []
    for e in raw if isinstance(raw, list) else []:
        if isinstance(e, dict):
            out.append((str(e.get("mutator")), e.get("chance"),
                        str(e.get("required")).lower() == "true"))
    return out


@suite.chain("defs")
def defs(t):
    """Each LandmarkDef resolves in the running game, from OUR package (a defName
    collision would resolve to whichever mod loaded last), with the exact category,
    commonality, single Required anchor and a non-empty icon path."""
    for def_name, category, commonality, anchor in LANDMARKS:
        with _independent(t, "%s_resolves" % def_name):
            r = t.bridge_call("jawa/get_defs", defs="LandmarkDef/%s" % def_name,
                              fields="category,commonality,mutatorChances,iconTexturePath",
                              deep=True)
            if not _live(t):
                continue
            if not (r or {}).get("success"):
                _unmeasured(t, "jawa/get_defs did not answer: %s" % (r or {}).get("message"))
            row = _row(r, def_name)
            if not row or not row.get("found"):
                _fail("%s does not resolve (notFound=%s)" % (def_name, (r or {}).get("notFound")))
            t._record("%s packageId" % def_name, row.get("packageId"))
            if str(row.get("packageId") or "").lower() != PACKAGE_ID:
                _fail("%s resolves from %r, not %s -- a defName collision"
                      % (def_name, row.get("packageId"), PACKAGE_ID))
            f = row.get("fields") or {}
            t._record("%s fields" % def_name, f)
            if str(f.get("category")) != category:
                _fail("%s.category = %r, expected %r" % (def_name, f.get("category"), category))
            try:
                comm = float(f.get("commonality"))
            except (TypeError, ValueError):
                _fail("%s.commonality unreadable: %r" % (def_name, f.get("commonality")))
            if abs(comm - commonality) > 1e-6:
                _fail("%s.commonality = %r, expected %r" % (def_name, comm, commonality))
            ch = _chances(f.get("mutatorChances"))
            if not ch:
                _unmeasured(t, "%s.mutatorChances came back unstructured: %r"
                            % (def_name, f.get("mutatorChances")))
            req = [m for m, _, rq in ch if rq]
            if req != [anchor]:
                _fail("%s Required mutators = %s, expected exactly [%s]" % (def_name, req, anchor))
            if not f.get("iconTexturePath"):
                _fail("%s.iconTexturePath is empty" % def_name)


# ------------------------------------------------------------------ placement (behaviour)

def _candidate_tiles(t, n):
    r = t.bridge_call("jawa/world_mutators_get", range=TILE_SCAN, limit=2000)
    if not (r or {}).get("success"):
        _unmeasured(t, "jawa/world_mutators_get did not answer: %s" % (r or {}).get("message"))
    rows = [x for x in (r.get("tiles") or [])
            if not x.get("waterCovered") and not x.get("landmark")]
    if len(rows) < n:
        _unmeasured(t, "only %d land tiles without a landmark in %s" % (len(rows), TILE_SCAN))
    return rows[:n]


def _tile(t, tile):
    r = t.bridge_call("jawa/world_mutators_get", tiles=str(tile))
    rows = (r or {}).get("tiles") or []
    if not (r or {}).get("success") or not rows:
        _unmeasured(t, "could not read tile %s back: %s" % (tile, (r or {}).get("message")))
    return rows[0]


@suite.chain("placement")
def placement(t):
    """Placing each landmark (the owner's act on the real save) does what the def says:
    the tile carries our LandmarkDef and its Required anchor mutator. Each landmark on
    its own fresh land tile; cleaned up after."""
    picks = None
    for i, (def_name, _cat, _comm, anchor) in enumerate(LANDMARKS):
        with _independent(t, "%s_places_with_anchor" % def_name):
            if not _live(t):
                continue
            if picks is None:
                picks = _candidate_tiles(t, len(LANDMARKS))
            tile = int(picks[i]["tile"])
            had_anchor = anchor in [m.get("def") for m in (picks[i].get("mutators") or [])]
            r = t.bridge_call("jawa/world_landmarks_set", action="add", tiles=str(tile),
                              forced=True, checkValid=True, **{"def": def_name})
            try:
                if not (r or {}).get("success") or int(r.get("added") or 0) != 1:
                    _fail("world_landmarks_set add %s on tile %d: success=%s added=%s errors=%s"
                          % (def_name, tile, (r or {}).get("success"), (r or {}).get("added"),
                             (r or {}).get("errors")))
                back = _tile(t, tile)
                muts = [m.get("def") for m in (back.get("mutators") or [])]
                t._record("tile %d after add" % tile, {"landmark": back.get("landmark"), "mutators": muts,
                                                      "validity": r.get("validity")})
                if back.get("landmark") != def_name:
                    _fail("tile %d landmark = %r after add, expected %s" % (tile, back.get("landmark"), def_name))
                if anchor not in muts:
                    _fail("tile %d carries %s but not its Required anchor %s (mutators %s)"
                          % (tile, def_name, anchor, muts))
            finally:
                t.session.call("jawa/world_landmarks_set", action="remove", tiles=str(tile))
                if not had_anchor:
                    t.session.call("jawa/world_mutators_set", action="remove", mutators=anchor,
                                   tiles=str(tile))
