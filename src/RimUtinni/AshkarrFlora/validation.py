"""validation.py -- modcheck suite for RimUtinni: Ash'karr Flora
(mandrake.rut.ashkarrflora).

Pure-XML content mod: no Source/, no Assemblies/, no ModSettings class --
`src/RimUtinni/AshkarrFlora/` holds only About/About.xml, one ThingDef file
(`Defs/ThingDefs_Plants/RUT_AshkarrFlora_Plants.xml`) and one defensive patch
(`Patches/BetterTrees_SweetlineTree_Immunity.xml`), read in full before
writing this. `suite.toggles = []`, every component `beyond_toggle=True`.

THE MECHANISM (TREE_GRAPHICS_OWNERSHIP_1, per the mod's own About.xml and
`design/Jawa/worldbuilding/biomes/arid_shrubland.md` §4): ships
`RUT_SweetlineTree` (`ParentName="TreeBase"`, NOT `DeciduousTreeBase` -- this
is a fixed-sun tidally-locked world with no season cycle, arid_shrubland.md
§6 rule 3) at `plant.visualSizeRange` 7.7~10.0 (raised from an earlier
5.0~6.5 cap per the owner's "ten cells wide" ruling, ASHKARR_FLORA_SWEETLINE_ART_UNWIRED_1),
well above vanilla's biggest common tree, matching the owner's "huge,
ancient, never small" ruling.

SWEETLINE_WOOL_HARVEST_1 (2026-09-21): the harvest changed from TreeBase's
inherited destructive wood harvest to a non-destructive giant-wool harvest
(`harvestedThingDef` RUT_SweetlineWool, `harvestAfterGrowth` 0.05 instead of
TreeBase's implicit 0 -- see RUT_AshkarrFlora_Plants.xml's own header for the
full mechanism). EXPECT_FIELDS below reflects the new values.
`Flammability` is dropped to 0.1 (from `TreeBase`'s 0.8) per
arid_shrubland.md §6 rule 9's hard "no flammable living flora" ban -- not a
balance judgment. Three subscribed "better trees" mods
(`ChaoticEnrico.BetterTrees` + two texture packs) rescale/retexture trees by
an exact-defName lookup into their own `TreeScaleTemplateDef`/
`TreeTextureTemplateDef` dictionaries (About.xml's own research into the
live Workshop copies) -- `RUT_SweetlineTree` is a brand-new defName absent
from all three, so it is structurally immune already; the shipped patch is
pure insurance against a FUTURE donor-mod update reclaiming this defName,
and is EXPECTED to match nothing and log nothing today (CLAUDE.md: "a patch
that matches nothing logs nothing").

CORRECTED 2026-09-24 (wave 11 of DIRTY_CODE_REVIEW_STANDING_LOOP_1): the art
gap this section used to describe is CLOSED. `RUT_SweetlineTree`'s `texPath`
is `Things/Plant/RUT_SweetlineTree`, and
`src/RimUtinni/AshkarrFlora/Textures/Things/Plant/RUT_SweetlineTree/` now
holds 14 PNGs (`RUT_SweetlineTreeA.png`..`N.png`, landed at `0d9116326`,
2026-09-18 -- one day after this file was first written at `f145b6587`,
which is why the original text below was true when written and stale ever
since). `art_folder_exists_and_has_art` below now PASSES on every run; it is
kept as a standing regression guard (the art folder going empty again would
be exactly the gap this section used to describe) rather than removed.

WHY BOTH REMAINING COMPONENTS ARE DEF READ-BACK / LOG CHECKS ONLY: this mod
carries no C#, no work-giver, no comp, nothing behavioral to run -- the only
mechanism is "does the ThingDef resolve with these exact values" and "does
the immunity patch stay a true no-op with the donor mods absent". A human
visual pass on the actual rendered canopy (once art lands) is explicitly out
of this suite's scope per the walk doc's own final line -- a separate
MOD_HUMAN_EXPLORATION_PASS_1 item.

Still not proven / real gaps:
  1. `art_folder_exists_and_has_art` now passes (14 PNGs landed 2026-09-18,
     see above) -- a human visual pass on the actual rendered canopy is
     still separate scope, `MOD_HUMAN_EXPLORATION_PASS_1` (see below).
  2. `betterTrees_patch_stays_noop_on_minimal` proves the patch is silent
     with the three donor mods ABSENT (the minimal list, per the walk doc's
     own environment). It does not prove the patch is STILL a no-op with
     the donor mods actually active and their templates loaded -- that
     needs a run with `ChaoticEnrico.BetterTrees` (+ the two texture packs)
     added to the smoke-test list, which the walk doc itself flags as a
     separate check ("equally on a list where the donor mods are active").
  3. `mustBeWildToSow=true` is inherited from `TreeBase` and never
     re-declared in `RUT_SweetlineTree`'s own XML -- the def read-back below
     checks the RESOLVED (post-inheritance) value via `jawa/get_defs`
     (`fields="plant"`, `deep=True`), since that is the only way to see it;
     nothing here independently re-derives inheritance from
     `Plants_Bases.xml` by hand.

FIXED 2026-09-24 (wave 11): `sweetline_thingdef_readback` previously called
`jawa/get_def` and read `row.get("resolved") or row.get("fields")` -- neither
key exists on that tool's actual response (verified against
`JawaBenchTerrainTools.cs`'s `GetDef`: the real top-level keys are `success`,
`statBases`, `comps`, `extra`, `extraModelled`; `extra` for a ThingDef holds
category/tickerType/thingClass/etc, never `plant.*` or `parentName`). So
`resolved` was always `{}` and the chain raised `ExpectationFailed` on every
live run regardless of whether the def was correct -- a guaranteed false
failure, never caught because this suite had never been run against a live
bridge since it was written. Split into two components using tools that
actually expose the data: `jawa/get_def`'s own `statBases` (already a flat
`{statDefName: value}` dict, built purpose-fit in the tool's C#) for the four
`statBases.*` checks, and `jawa/get_defs(fields="plant", deep=True)` --
`GetDef`'s own `extraNote` names this as the documented escape hatch -- for
the eleven `plant.*` checks (`DeepSerializeValue` reflects `PlantProperties`'
own public fields, which are the same names the XML tags bind to). `parentName`
is dropped outright: it is consumed by the XML loader at parse time and is
not a field retained on the resolved runtime ThingDef at all, so no bridge
tool can read it back post-load; asserting it was never checkable. `plant.
visualSizeRange` (a `FloatRange` struct) is checked for presence only, not
exact min/max -- this repo's own rule is never to assert an un-measured
engine-internal field shape (`FloatRange`'s serialized field names were not
confirmed against a live call), so the other ten scalar/bool/Def-reference
plant fields get exact-value checks and this one does not.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("AshkarrFlora")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

DEF_NAME = "RUT_SweetlineTree"
DEF_TYPE = "ThingDef"

# Verbatim from RUT_AshkarrFlora_Plants.xml (read in full before writing
# this), not guessed. Split by which tool actually exposes it -- see the
# module docstring's "FIXED 2026-09-24" note.
EXPECT_STATBASES = {
    "MaxHitPoints": "650",
    "Flammability": "0.1",
    "Mass": "900",
    "BeautyOutdoors": "10",
}
EXPECT_PLANT = {
    "growDays": "240",
    "harvestWork": "4200",
    "harvestedThingDef": "RUT_SweetlineWool",   # SWEETLINE_WOOL_HARVEST_1: was WoodLog (inherited)
    "harvestYield": "20",                        # SWEETLINE_WOOL_HARVEST_1: was 160 (wood)
    "harvestTag": "Standard",                     # SWEETLINE_WOOL_HARVEST_1: was inherited "Wood"
    "harvestAfterGrowth": "0.05",                 # SWEETLINE_WOOL_HARVEST_1: makes HarvestDestroys false
    "forceIsTree": "True",                        # SWEETLINE_WOOL_HARVEST_1: harvestTag != "Wood" now
    "wildClusterRadius": "0",
    "wildClusterWeight": "0.05",
    "wildOrder": "4",
    "mustBeWildToSow": "True",   # inherited from TreeBase, not re-declared here
}
# Checked for presence only, not exact min/max -- FloatRange's serialized
# field names were never confirmed against a live call (module docstring).
PLANT_PRESENCE_ONLY = ("visualSizeRange",)


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


@suite.chain("art_asset_present")
def art_asset_present(t):
    """Pure repo check, no bridge call -- `os.path` against this mod's own
    Textures folder. Runs even under the offline declaration probe (like
    StarWarsRaces' own First.txt check), because it needs neither a session
    nor a live game. See module docstring: art landed 2026-09-18, so this
    now passes and stands as a regression guard against the folder going
    empty again."""
    import os
    mod_dir = os.path.dirname(os.path.abspath(__file__))
    tex_dir = os.path.join(mod_dir, "Textures", "Things", "Plant", DEF_NAME)

    with t.component("art_folder_exists_and_has_art", beyond_toggle=True):
        if not os.path.isdir(tex_dir):
            raise ExpectationFailed(
                "%s does not exist at all -- RUT_SweetlineTree's texPath "
                "(Things/Plant/RUT_SweetlineTree) has no backing art on disk. "
                "14 accepted PNGs normally live here (landed 0d9116326, "
                "2026-09-18) -- their absence means a REGRESSION, not the "
                "original pre-2026-09-18 gap." % tex_dir)
        pngs = [f for f in os.listdir(tex_dir) if f.lower().endswith(".png")]
        if not pngs:
            raise ExpectationFailed(
                "%s exists but has 0 .png files -- same gap as above, "
                "folder was created but never populated." % tex_dir)


@suite.chain("sweetline_thingdef_readback")
def sweetline_thingdef_readback(t):
    """Every authored field on RUT_SweetlineTree, exact values copied
    verbatim from RUT_AshkarrFlora_Plants.xml, checked post-inheritance --
    proves both the def's own values AND that TreeBase's inheritance chain
    resolves cleanly. Two components, two tools (module docstring's "FIXED
    2026-09-24" note explains why one tool cannot do both)."""
    t.clear_area(size=10)

    with t.component("statbases_match_shipped_xml", beyond_toggle=True):
        r = t.bridge_call("jawa/get_def", defType=DEF_TYPE, defName=DEF_NAME)
        if _live(t):
            stats = (r or {}).get("statBases") or {}
            if not stats:
                raise ExpectationFailed(
                    "jawa/get_def(%s, %s) returned no statBases: %r"
                    % (DEF_TYPE, DEF_NAME, r))
            bad = [
                "%s: expected %r, got %r" % (stat, expect, stats.get(stat, "(no such field)"))
                for stat, expect in EXPECT_STATBASES.items()
                if str(stats.get(stat, "(no such field)")) != str(expect)
            ]
            if bad:
                raise ExpectationFailed(
                    "RUT_SweetlineTree statBases mismatch: %s" % "; ".join(bad))

    with t.component("plant_fields_match_shipped_xml", beyond_toggle=True):
        r = t.bridge_call("jawa/get_defs", defs="%s/%s" % (DEF_TYPE, DEF_NAME),
                          fields="plant", deep=True)
        if _live(t):
            rows = (r or {}).get("defs") or []
            row = rows[0] if rows else {}
            plant = (row.get("fields") or {}).get("plant")
            if not isinstance(plant, dict):
                raise ExpectationFailed(
                    "jawa/get_defs(%s/%s, fields=plant, deep=True) did not return a "
                    "plant object: %r" % (DEF_TYPE, DEF_NAME, r))
            bad = [
                "%s: expected %r, got %r" % (field, expect, plant.get(field, "(no such field)"))
                for field, expect in EXPECT_PLANT.items()
                if str(plant.get(field, "(no such field)")) != str(expect)
            ]
            for field in PLANT_PRESENCE_ONLY:
                got = plant.get(field, "(no such field)")
                if got in (None, "(no such field)"):
                    bad.append("%s: expected present, got %r" % (field, got))
            if bad:
                raise ExpectationFailed(
                    "RUT_SweetlineTree plant field mismatch: %s" % "; ".join(bad))
        t.screenshot()


@suite.chain("betterTrees_patch_stays_noop_on_minimal")
def betterTrees_patch_stays_noop_on_minimal(t):
    """On the minimal list (the three BetterTrees-family donor mods absent),
    both PatchOperationConditional operations in
    BetterTrees_SweetlineTree_Immunity.xml should find their MayRequire mod
    missing and no-op silently -- proving the shipped def loads clean with
    no trace of a BetterTrees reference in the log, per the walk doc's own
    check #6. Does NOT prove the patch stays a no-op with the donor mods
    actually active (module docstring gap #2)."""
    t.clear_area(size=10)

    with t.component("no_bettertrees_reference_in_log_on_minimal",
                     beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=500,
                          contains="RUT_SweetlineTree")
        if _live(t):
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            hits = [m for m in msgs
                   if "TreeScaleTemplateDef" in m or "TreeTextureTemplateDef" in m
                   or "Config error" in m]
            if hits:
                raise ExpectationFailed(
                    "found BetterTrees/config-error log lines mentioning "
                    "RUT_SweetlineTree on the minimal (donor-mod-absent) "
                    "list, expected none: %r" % hits)
        t.screenshot()
