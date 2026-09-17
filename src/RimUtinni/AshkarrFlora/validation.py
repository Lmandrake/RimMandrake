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
§6 rule 3) at `plant.visualSizeRange` 5.0~6.5, well above vanilla's biggest
common tree, matching the owner's "huge, ancient, never small" ruling.
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

🔴 A REAL, CURRENTLY-TRUE BLOCKING GAP, confirmed by this pass, not merely
copied from the walk doc: `RUT_SweetlineTree`'s `texPath` is
`Things/Plant/RUT_SweetlineTree`, and `src/RimUtinni/AshkarrFlora/Textures/`
DOES NOT EXIST AT ALL on disk (checked directly: `find
src/RimUtinni/AshkarrFlora/Textures -type f` returns nothing, and there is
no `Textures` directory under this mod at any depth) -- not merely empty, as
the walk doc's own wording ("the texture folder exists but is EMPTY")
states. Candidate art sits unmoved and unselected in
`_artsrc/sweetline_orphans_2026-09-06/` (11 PNGs + a CONTACT_SHEET.png +
README.md, no recorded pick). `art_folder_exists_and_has_art` below asserts
this directly and is EXPECTED TO FAIL on this pass and every pass until a
PNG is actually placed there -- this is the correct, honest signal (the mod
genuinely cannot render a tree today), not a bug in this suite to work
around. `RUT_SweetlineTree` will still spawn as an invisible/placeholder
Thing without art -- this suite does not claim otherwise.

WHY BOTH REMAINING COMPONENTS ARE DEF READ-BACK / LOG CHECKS ONLY: this mod
carries no C#, no work-giver, no comp, nothing behavioral to run -- the only
mechanism is "does the ThingDef resolve with these exact values" and "does
the immunity patch stay a true no-op with the donor mods absent". A human
visual pass on the actual rendered canopy (once art lands) is explicitly out
of this suite's scope per the walk doc's own final line -- a separate
MOD_HUMAN_EXPLORATION_PASS_1 item.

Still not proven / real gaps:
  1. `art_folder_exists_and_has_art` will keep failing until art is chosen
     from `_artsrc/sweetline_orphans_2026-09-06/` and placed at
     `Textures/Things/Plant/RUT_SweetlineTree/`. This suite cannot pick the
     art for the owner; it can only detect the gap.
  2. `betterTrees_patch_stays_noop_on_minimal` proves the patch is silent
     with the three donor mods ABSENT (the minimal list, per the walk doc's
     own environment). It does not prove the patch is STILL a no-op with
     the donor mods actually active and their templates loaded -- that
     needs a run with `ChaoticEnrico.BetterTrees` (+ the two texture packs)
     added to the smoke-test list, which the walk doc itself flags as a
     separate check ("equally on a list where the donor mods are active").
  3. `mustBeWildToSow=true` is inherited from `TreeBase` and never
     re-declared in `RUT_SweetlineTree`'s own XML -- the def read-back below
     checks the RESOLVED (post-inheritance) value via `jawa/get_def`, since
     that is the only way to see it; nothing here independently re-derives
     inheritance from `Plants_Bases.xml` by hand.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("AshkarrFlora")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

DEF_NAME = "RUT_SweetlineTree"
DEF_TYPE = "ThingDef"

# Verbatim from RUT_AshkarrFlora_Plants.xml (read in full before writing
# this), not guessed.
EXPECT_FIELDS = {
    "parentName": "TreeBase",
    "statBases.MaxHitPoints": "650",
    "statBases.Flammability": "0.1",
    "statBases.Mass": "900",
    "statBases.BeautyOutdoors": "10",
    "plant.visualSizeRange": "5.0~6.5",
    "plant.growDays": "240",
    "plant.harvestWork": "4200",
    "plant.harvestYield": "160",
    "plant.wildClusterRadius": "0",
    "plant.wildClusterWeight": "0.05",
    "plant.wildOrder": "4",
    "plant.mustBeWildToSow": "True",   # inherited from TreeBase, not re-declared here
}


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


@suite.chain("art_asset_present")
def art_asset_present(t):
    """Pure repo check, no bridge call -- `os.path` against this mod's own
    Textures folder. Runs even under the offline declaration probe (like
    StarWarsRaces' own First.txt check), because it needs neither a session
    nor a live game. See module docstring: this is EXPECTED TO FAIL today."""
    import os
    mod_dir = os.path.dirname(os.path.abspath(__file__))
    tex_dir = os.path.join(mod_dir, "Textures", "Things", "Plant", DEF_NAME)

    with t.component("art_folder_exists_and_has_art", beyond_toggle=True):
        if not os.path.isdir(tex_dir):
            raise ExpectationFailed(
                "%s does not exist at all -- RUT_SweetlineTree's texPath "
                "(Things/Plant/RUT_SweetlineTree) has no backing art on disk. "
                "Candidate art is unselected in "
                "_artsrc/sweetline_orphans_2026-09-06/ (11 PNGs + contact "
                "sheet, no pick recorded)." % tex_dir)
        pngs = [f for f in os.listdir(tex_dir) if f.lower().endswith(".png")]
        if not pngs:
            raise ExpectationFailed(
                "%s exists but has 0 .png files -- same gap as above, "
                "folder was created but never populated." % tex_dir)


@suite.chain("sweetline_thingdef_readback")
def sweetline_thingdef_readback(t):
    """Every authored field on RUT_SweetlineTree, exact values copied
    verbatim from RUT_AshkarrFlora_Plants.xml, checked post-inheritance via
    jawa/get_def (proves both the def's own values AND that TreeBase's
    inheritance chain resolves cleanly)."""
    t.clear_area(size=10)

    with t.component("sweetline_fields_match_shipped_xml", beyond_toggle=True):
        r = t.bridge_call("jawa/get_def", defType=DEF_TYPE, defName=DEF_NAME)
        if _live(t):
            row = r or {}
            resolved = row.get("resolved") or row.get("fields") or {}

            def _get(path):
                cur = resolved
                for part in path.split("."):
                    if not isinstance(cur, dict):
                        return None
                    cur = cur.get(part)
                return cur

            bad = []
            if not resolved:
                raise ExpectationFailed(
                    "jawa/get_def(%s, %s) returned no resolved fields: %r"
                    % (DEF_TYPE, DEF_NAME, r))
            for path, expect in EXPECT_FIELDS.items():
                got = _get(path)
                if str(got) != str(expect):
                    bad.append("%s: expected %r, got %r" % (path, expect, got))
            if bad:
                raise ExpectationFailed(
                    "RUT_SweetlineTree field mismatch: %s" % "; ".join(bad))
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
