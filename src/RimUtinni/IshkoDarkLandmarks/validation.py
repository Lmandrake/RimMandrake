"""validation.py -- modcheck suite for RimUtinni Ishko's Dark Landmarks
(mandrake.rut.ishkolandmarks).

Pure-XML content mod: no Source/ folder, no C# at all, no ModSettings class --
`suite.toggles = []` and every component below is `beyond_toggle=True`. The
entire mod is one file, `Defs/LandmarkDefs_IshkoDark.xml` (read whole for
this pass), plus `About.xml` (read whole -- confirms the Odyssey
`modDependencies`/`loadAfter` and the `mandrake.rut.ashkarrlandmarkart`
`loadAfter` for the icon textures).

THE CONTENT (read directly off the XML, not the mod's own description):
three `LandmarkDef`s, each `MayRequire="Ludeon.RimWorld.Odyssey"` (Landmarks
are an Odyssey-only DefType) and each anchored on exactly one real, legal
`TileMutatorDef` marked `Required="True"` inside its own `mutatorChances`
block -- the same pattern every vanilla LandmarkDef in Core/Odyssey's own
`Landmarks.xml` uses, per the file's own header comment:

    RUT_LightlessSink     category=mountain  commonality=0.08  Hollow Required=True
    RUT_ShadowedOverhang  category=mountain  commonality=0.08  Chasm  Required=True
    RUT_ColdLavaTube      category=mountain  commonality=0.06  Cavern Required=True

Each `iconTexturePath` (`World/Landmarks/Ashkarr/Hollow` / `.../Chasm` /
`.../Cavern`) points at `src/RimUtinni/AshkarrLandmarkArt/Textures/World/
Landmarks/Ashkarr/{Hollow,Chasm,Cavern}.png` -- confirmed present on disk
(all three files exist, checked directly, not assumed from the `loadAfter`
declaration alone).

WHAT THIS MOD DELIBERATELY DOES NOT DO, per both the file's own header
comment and About.xml's own description: it does not place any of the three
landmarks on the actual Ash'karr planet -- "the owner's hand, per the item's
own title" (ISHKO_DARK_LANDMARKS_1). This suite's last chain proves that
absence rather than treating it as an oversight: none of the three defNames
should appear among `jawa/world_landmarks_get`'s currently-placed landmarks.

Still not proven / structurally offline-only:
  1. This suite proves the DEFS resolve with the expected fields once
     Odyssey + AshkarrLandmarkArt are active -- it does not prove the icon
     PNG actually renders correctly in the in-game landmark legend/tooltip
     (walk doc step 7, "(human pass) once the owner places one of the
     three"). No bridge tool renders a landmark icon for inspection; this is
     a genuine visual gap, left for the owner's own placement pass.
  2. `jawa/get_defs` on a `mutatorChances` dict-shaped field: the walk doc's
     own step 5 describes filtering the resolved field for the anchor
     mutator's `Required=True` entry as a substring check on the returned
     value's repr, the same pattern PawnFlavor/validation.py uses for a
     list-shaped field with no dedicated "does this dict contain this key
     with this value" bridge verb -- not independently confirmed against a
     live `jawa/get_defs` return shape for a `mutatorChances` field
     specifically (no other suite in this family reads one).
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("IshkoDarkLandmarks")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

LANDMARKS = [
    ("RUT_LightlessSink", "mountain", "0.08", "Hollow"),
    ("RUT_ShadowedOverhang", "mountain", "0.08", "Chasm"),
    ("RUT_ColdLavaTube", "mountain", "0.06", "Cavern"),
]


def _get_defs(t, defs, fields):
    return t.bridge_call("jawa/get_defs", defs=defs, fields=fields)


def _row_for(r, def_key):
    for d in (r or {}).get("defs", (r or {}).get("results", [])) or []:
        if d.get("defName") == def_key.split("/", 1)[-1]:
            return d
    return None


@suite.chain("landmark_defs_readback")
def landmark_defs_readback(t):
    """Each of the three Ishko LandmarkDefs resolves with its exact
    category/commonality/anchor-mutator, read straight off
    `LandmarkDefs_IshkoDark.xml` above -- catches a whole-file load break
    (a bad `MayRequire`, a malformed `mutatorChances` block) as much as it
    confirms the specific numbers."""
    t.clear_area(size=10)
    for def_name, category, commonality, anchor_mutator in LANDMARKS:
        with t.component("landmark_%s_resolves" % def_name, beyond_toggle=True):
            r = _get_defs(t, "LandmarkDef/%s" % def_name,
                         "category,commonality,mutatorChances,iconTexturePath")
            row = _row_for(r, "LandmarkDef/%s" % def_name)
            fields = (row or {}).get("fields") or {}

            got_cat = fields.get("category", "(no such field)")
            ok_cat = got_cat == category
            t._record("%s.category -> %r" % (def_name, got_cat), ok_cat)
            if not ok_cat:
                raise ExpectationFailed(
                    "%s.category = %r, expected %r" % (def_name, got_cat, category))

            got_comm = fields.get("commonality", "(no such field)")
            ok_comm = str(got_comm) == commonality
            t._record("%s.commonality -> %r" % (def_name, got_comm), ok_comm)
            if not ok_comm:
                raise ExpectationFailed(
                    "%s.commonality = %r, expected %r" % (def_name, got_comm, commonality))

            got_mut = fields.get("mutatorChances", "(no such field)")
            ok_mut = anchor_mutator in str(got_mut) and "Required" in str(got_mut)
            t._record("%s.mutatorChances -> %r" % (def_name, got_mut), ok_mut)
            if not ok_mut:
                raise ExpectationFailed(
                    "%s.mutatorChances = %r, expected to contain a Required "
                    "%s anchor" % (def_name, got_mut, anchor_mutator))

            got_icon = fields.get("iconTexturePath", "")
            ok_icon = bool(got_icon)
            t._record("%s.iconTexturePath -> %r" % (def_name, got_icon), ok_icon)
            if not ok_icon:
                raise ExpectationFailed(
                    "%s.iconTexturePath is empty -- icon did not resolve" % def_name)


@suite.chain("not_placed_on_planet")
def not_placed_on_planet(t):
    """Confirms the mod's own deliberate omission (About.xml: "Placement on
    the actual Ash'karr world is deliberately NOT done here") -- none of the
    three defNames should appear among the planet's currently-placed
    landmarks. A hit here would mean something ELSE placed one of these
    (or the owner already did, post-review), not a defect in this mod."""
    with t.component("no_ishko_landmark_placed_yet", beyond_toggle=True):
        r = t.bridge_call("jawa/world_landmarks_get")
        rows = (r or {}).get("landmarks") or []
        placed = [row.get("defName") for row in rows]
        hits = [name for name, _, _, _ in LANDMARKS if name in placed]
        t._record("world_landmarks_get placed defNames -> %r" % placed, not hits)
        if hits:
            raise ExpectationFailed(
                "expected none of %s placed on the planet yet, found %s "
                "already placed" % ([n for n, _, _, _ in LANDMARKS], hits))
