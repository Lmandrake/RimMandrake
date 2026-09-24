"""validation.py -- modcheck suite for RimUtinni: Ash'karr Landmark Art
(mandrake.rut.ashkarrlandmarkart).

Patch-only content mod: no Source/, no Assemblies/, no ModSettings class --
`src/RimUtinni/AshkarrLandmarkArt/` holds only About/About.xml, one patch
file (`Patches/LandmarkIcons.xml`, read in full before writing this),
`Textures/World/Landmarks/Ashkarr/*.png`, and three standalone icon-
generator scripts (`make_ashfall_spire_icon.py`,
`make_complex_structures_icon.py`, `make_slough_breach_icon.py` -- dev
tooling, not shipped mod content, not exercised here).
`suite.toggles = []`, every component `beyond_toggle=True`.

⚠️ ENVIRONMENT: this suite needs the **FULL** mod list, not minimal, per
the walk doc's own environment line. This mod repaints 48 `LandmarkDef`s
sourced from FOUR different providers (vanilla Odyssey DLC + Vanilla
Expanded Exploration + Alpha Biomes + Star Wars Animal Collection) -- none
of the three non-Odyssey providers are on the minimal list, so a
minimal-list run only proves the patch's own conditional guards are a safe
no-op, never that a single icon actually applies to a real def.

THE MECHANISM (About.xml's own description): vanilla Landmarks Expanded
ships desert landmarks as a single opaque 128x128 fill; Ludeon's own
Cliffs/Valley/Ruins are a translucent wash over a hard black rim. This mod
points 48 `LandmarkDef.iconTexturePath` fields at repainted 1024x1024 icons
in that house style -- every silhouette is lifted unchanged, so worldgen and
tile behaviour are untouched; only the picture moves. Every `<Operation>` is
double-`PatchOperationConditional`-wrapped (outer: does the def exist at
all; inner: does it already have an `iconTexturePath` node, since some defs
like `AncientGarrison` only INHERIT the field from an abstract parent and
take the Add branch instead of Replace) -- any of the four provider mods
being inactive produces zero errors, only a silent no-op for that def's
entries (CLAUDE.md: "a patch that matches nothing logs nothing").

🔴 THE WALK DOC IS WRONG ON THE PNG COUNT -- checked directly against disk,
not copied from the doc: it claims "48 <xpath> defName entries, 49 PNGs on
disk -- the 1 extra, RUT_ComplexStructures.png, [is] consumed ... by a
separate LandmarkDef ... not by this mod's own patch". The REAL count,
measured this pass (`find Textures/World/Landmarks/Ashkarr -iname '*.png' |
wc -l`), is **52 PNGs**, not 49 -- FOUR extras beyond the 48 patched
defNames, not one: `RUT_AshfallSpire.png`, `RUT_ComplexStructures.png`,
`RUT_GapingDoom.png` and `RUT_Slough_GelatinousBreach.png`. All four ARE
each consumed by their own separate `LandmarkDef` under
`src/RimUtinni/UtinniPatches/Defs/LandmarkDefs/` (confirmed by grep: each of
the four names appears in exactly one file there, `RUT_AshfallSpire.xml`,
`RUT_ComplexStructures.xml`, `RUT_GapingDoom.xml`,
`RUT_Slough_GelatinousBreach.xml`) -- so the walk doc's CLAIM ("cross-mod
texture dependency, out of this walk's scope") is directionally right for
all four, it just undercounted by 3. `patch_targets_have_matching_png`
below asserts the corrected 48 + 4 = 52 split, not the walk doc's 48 + 1 = 49.

Facts confirmed by direct repo check this pass, matching the walk doc:
  - The 4 oceanic landmarks (Bay, Peninsula, CoastalIsland, Archipelago)
    never appear in LandmarkIcons.xml -- 0 matches, confirmed by grep.
    About.xml's own description explains why: they ship as pure white
    silhouettes so the engine can tint them the ocean's own colour.
  - Exactly 48 unique `defName="..."` values in the patch file (grepped and
    counted, not eyeballed), spanning unprefixed (25 vanilla-Odyssey-style
    names), `AB_*` (3), `VEE_*` (18), and `sw_*` (2) by prefix convention --
    25 + 3 + 18 + 2 = 48.

Still not proven / real gaps:
  1. `jawa/world_landmarks_get` (the walk doc's own step 8, confirming the
     targeted LandmarkDef set is actually reachable on a live generated
     world with `odysseyActive=true`) is included below as a live-only
     check, but this suite cannot force the runner onto the FULL list --
     if run on minimal, `_live` still executes the call but the assertion
     is written to tolerate `count==0`/`odysseyActive=false` there (see the
     component's own docstring) rather than fail on an environment gap this
     script does not control.
  2. No pixel-level check of any repainted icon's actual appearance
     (translucent wash + black rim vs. Ludeon's own style) is possible
     offline or via any bridge tool found -- the walk doc's own final line
     defers this to a human pass (MOD_HUMAN_EXPLORATION_PASS_1), and this
     suite agrees: `iconTexturePath` resolving to the right file proves
     WIRING, never the art itself.
  3. Which specific mod owns the `AB_*` vs `VEE_*` prefix (Alpha Biomes vs.
     Vanilla Expanded Exploration) is not independently confirmed here
     either -- same gap the walk doc names, carried forward rather than
     invented an answer for.
"""
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("AshkarrLandmarkArt")
suite.toggles = []   # patch-only, no Source/, no ModSettings

_MOD_DIR = os.path.dirname(os.path.abspath(__file__))
_PATCH_PATH = os.path.join(_MOD_DIR, "Patches", "LandmarkIcons.xml")
_TEX_DIR = os.path.join(_MOD_DIR, "Textures", "World", "Landmarks", "Ashkarr")

OCEANIC = ["Bay", "Peninsula", "CoastalIsland", "Archipelago"]

# Cross-mod texture dependencies: PNGs in this mod's own Textures/ that are
# consumed by a DIFFERENT mod's LandmarkDef (src/RimUtinni/UtinniPatches/
# Defs/LandmarkDefs/), not by this mod's own patch -- confirmed by grep
# before writing this, not guessed. The walk doc names only 1 of these 4.
KNOWN_CROSS_MOD_EXTRAS = {
    "RUT_AshfallSpire", "RUT_ComplexStructures", "RUT_GapingDoom",
    "RUT_Slough_GelatinousBreach",
}

# One representative def per provider prefix, values copied verbatim from
# LandmarkIcons.xml.
SAMPLE_DEFS = {
    "Cliffs": "World/Landmarks/Ashkarr/Cliffs",                 # Replace branch, vanilla Odyssey
    "AncientGarrison": "World/Landmarks/Ashkarr/AncientGarrison",  # Add branch (inherited field)
    "sw_Sarlacc": "World/Landmarks/Ashkarr/sw_Sarlacc",           # StarWarsAnimalCollection
    "VEE_AlluvialFan": "World/Landmarks/Ashkarr/VEE_AlluvialFan", # VEE_-prefixed provider
}


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


def _patch_defnames():
    import re
    with open(_PATCH_PATH, "r", encoding="utf-8") as f:
        xml = f.read()
    return sorted(set(re.findall(r'defName="([^"]+)"', xml)))


@suite.chain("repo_checks")
def repo_checks(t):
    """Pure repo checks, no bridge call -- run even under the offline
    declaration probe, same pattern as StarWarsRaces' First.txt check."""
    t.clear_area(size=8)   # keeps the runner's evidence/screenshot machinery uniform

    with t.component("oceanic_landmarks_never_patched", beyond_toggle=True):
        with open(_PATCH_PATH, "r", encoding="utf-8") as f:
            xml = f.read()
        hits = [name for name in OCEANIC if ('defName="%s"' % name) in xml]
        if hits:
            raise ExpectationFailed(
                "LandmarkIcons.xml patches oceanic landmark(s) %r -- these "
                "must stay untouched so the engine's ocean-colour tint "
                "still applies" % hits)

    with t.component("exactly_48_patch_targets", beyond_toggle=True):
        names = _patch_defnames()
        if len(names) != 48:
            raise ExpectationFailed(
                "expected exactly 48 unique defName targets in "
                "LandmarkIcons.xml, counted %d: %r" % (len(names), names))

    with t.component("patch_targets_have_matching_png", beyond_toggle=True):
        names = set(_patch_defnames())
        if not os.path.isdir(_TEX_DIR):
            raise ExpectationFailed("%s does not exist" % _TEX_DIR)
        pngs = {os.path.splitext(f)[0] for f in os.listdir(_TEX_DIR)
               if f.lower().endswith(".png")}
        missing = names - pngs
        if missing:
            raise ExpectationFailed(
                "%d patched defName(s) have no matching .png in %s: %r"
                % (len(missing), _TEX_DIR, sorted(missing)))
        extra = pngs - names
        unexplained = extra - KNOWN_CROSS_MOD_EXTRAS
        if unexplained:
            raise ExpectationFailed(
                "found .png(s) in %s that are neither a patch target nor a "
                "known cross-mod dependency (RUT_AshfallSpire/"
                "RUT_ComplexStructures/RUT_GapingDoom/"
                "RUT_Slough_GelatinousBreach): %r -- new, unaccounted-for "
                "art?" % (_TEX_DIR, sorted(unexplained)))
        if extra != KNOWN_CROSS_MOD_EXTRAS:
            # The corrected finding (module docstring): the walk doc claims
            # only 1 extra; this fails loudly if the count ever drifts again
            # rather than silently re-trusting either number.
            raise ExpectationFailed(
                "expected exactly the 4 known cross-mod extras %r, found "
                "%r" % (sorted(KNOWN_CROSS_MOD_EXTRAS), sorted(extra)))


@suite.chain("sample_defs_readback")
def sample_defs_readback(t):
    """One representative LandmarkDef per provider/branch shape: Cliffs
    (Replace branch, vanilla Odyssey), AncientGarrison (Add branch -- field
    inherited from an abstract parent, no local node to Replace), sw_Sarlacc
    (StarWarsAnimalCollection-sourced), VEE_AlluvialFan (VEE_-prefixed
    provider). REQUIRES THE FULL MOD LIST -- see module docstring's
    environment note; on minimal, sw_Sarlacc and VEE_AlluvialFan's provider
    mods are absent and `jawa/get_defs` will report not-found, which this
    component treats as an environment gap (UNMEASURED-style skip) rather
    than a hard failure -- see `_check_one`'s own guard.

    🔴 FOUND AND FIXED (wave 12): this component used to call `jawa/get_def`
    (singular) with `defType="LandmarkDef"` and read
    `row.get("resolved") or row.get("fields")`. Cross-checked against
    `JawaBenchTerrainTools.cs`'s `GetDef`: neither `resolved` nor `fields`
    is ever a key on that tool's response -- its per-def `extra` block is
    hand-modelled for exactly THREE types (ThingDef/PawnKindDef/BiomeDef,
    per the tool's own comment), so for a LandmarkDef `extra` comes back
    null and `iconTexturePath` was never reachable through it at all. The
    old guard (`not row.get("resolved") and not row.get("fields")`) was
    therefore unconditionally true on EVERY call, success or failure, so
    this component always took the "not found" branch and never once
    compared `iconTexturePath` against anything -- a silent, permanent
    no-op, the mirror image of AshkarrFlora's wave-11 bug (that one always
    raised; this one never even checked). Switched to `jawa/get_defs`
    (plural), the tool built exactly for this -- "name the fields you want
    off ANY def type and they are read reflectively" -- whose real
    per-entry shape (`found`, `fields` -- confirmed against `GetDefs` in
    the same file) actually carries `iconTexturePath`."""
    t.clear_area(size=8)

    def _check_one(name, expect_path):
        with t.component("landmark_%s_repainted" % name, beyond_toggle=True):
            r = t.bridge_call("jawa/get_defs", defs="LandmarkDef/%s" % name,
                              fields="iconTexturePath")
            if _live(t):
                rows = (r or {}).get("defs") or []
                row = rows[0] if rows else {}
                if not row.get("found"):
                    # Provider mod likely absent on this run's list (e.g.
                    # minimal) -- an environment gap, not a patch defect.
                    # Recorded, not silently swallowed.
                    t._record("landmark_%s not found -- provider mod likely "
                             "absent from this run's mod list" % name, None)
                    return
                fields = row.get("fields") or {}
                got = fields.get("iconTexturePath")
                if got != expect_path:
                    raise ExpectationFailed(
                        "%s.iconTexturePath: expected %r, got %r"
                        % (name, expect_path, got))
            t.screenshot()

    for name, path in SAMPLE_DEFS.items():
        _check_one(name, path)


@suite.chain("world_landmarks_reachable")
def world_landmarks_reachable(t):
    """Walk doc step 8: on a live generated world, the targeted LandmarkDef
    set should be reachable at all (odysseyActive=true, count>0). Tolerates
    a minimal-list run (module docstring gap #1) by not hard-failing on
    odysseyActive=false -- that is an environment fact about THIS run, not
    a defect in this mod's patch."""
    t.clear_area(size=8)

    with t.component("world_landmarks_get_succeeds", beyond_toggle=True):
        r = t.bridge_call("jawa/world_landmarks_get")
        if _live(t):
            row = r or {}
            if not row.get("success"):
                raise ExpectationFailed(
                    "jawa/world_landmarks_get did not report success: %r" % row)
            if not row.get("odysseyActive"):
                t._record(
                    "odysseyActive=false -- this run's mod list lacks "
                    "Odyssey; landmark set is not fully reachable here "
                    "(environment gap, not a patch defect)", None)
        t.screenshot()
