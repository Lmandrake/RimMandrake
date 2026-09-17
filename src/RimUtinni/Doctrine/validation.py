"""validation.py -- modcheck suite for RimUtinni Jawa Doctrine Patches
(mandrake.rut.doctrine).

Grounded in the mod's actual Source and XML, read whole before writing
this: `DoctrinePatches.cs` (the one Harmony postfix,
DROIDWORKS_ISFLESH_RELATIONS_CRASH_1 -- allocates `pawn.relations` for any
Humanlike pawn whose `RaceProps.IsFlesh` is false, closing the gap
`DroidsAreMachines.xml`'s own `isOrganic:false` opens), `DroidsAreMachines.
xml` (read whole -- ONE `PatchOperationFindMod` block, Asimov only; see
STALE-WALK finding below), `NoDroidManufacture.xml` (read whole -- clears
`OuterRim_DroidFactory`'s `designationCategory`, replaces its
`description`, touches no recipe because the building has none), and
`MegafaunaYield.xml` (10412 lines, `Source/gen_megafauna_yield.py`-
generated, "Do not hand-edit" -- read via `grep`/measurement, never a bare
skim, per this project's own "a number about a large artifact comes from
`measure`, never a scan" rule, and cross-checked against the walk doc's own
claimed counts below). `Source/DoctrineCore/SelfTest/` holds only orphaned
build output (gitignored `.exe`/`obj/`), no `.cs`/`.csproj` anywhere in the
tree -- confirmed by `find`, matching the walk doc's own step 7 finding;
this mod has no C# self-test to defer to.

🔴 THE WALK DOC (`design/validation_walks/RimUtinni/Doctrine.md`) IS STALE
IN TWO INDEPENDENTLY-MEASURED WAYS, found while grounding this suite --
recorded here rather than silently worked around, per this project's own
"a doc can describe defects that were fixed before the doc was written"
register:

  1. Step 6 ("`ABF_FleshType_Synstruct_Base` `isOrganic` = false") and the
     walk's own `deps`/`loadAfter` lines both still name "ABF: Synstructs
     Core" (`killathon.artificialbeings.syncore`) as a live gate on
     `DroidsAreMachines.xml`. It is not: that file's OWN header comment
     says plainly "DROID_RETIRE_ABF_SYNCORE_1 (2026-09-10): ABF/SynCore
     retired from ModsConfig.xml ... this file's ABF_FleshType_
     Synstruct_Base Operation was removed - only the Asimov_Automaton
     Operation below remains." Read directly: the file contains exactly
     ONE `<Operation Class="PatchOperationFindMod">` block (`grep -c`,
     measured, not assumed) and zero occurrences of the string
     `ABF_FleshType_Synstruct` anywhere in it. This suite tests the
     Asimov_Automaton path only and does NOT test for an ABF FleshTypeDef
     that this mod no longer touches.
  2. `MegafaunaYield.xml`'s own header comment (§"must be true" in the
     walk) claims "424 unique defNames across 35 `PatchOperationFindMod`
     groups"; About.xml's description claims "42 PatchOperationFindMod
     blocks". MEASURED directly against the current file (2026-09-17):
     `grep -c 'PatchOperationFindMod'` = **34** groups, and
     `grep -oP 'defName="\\K[^"]+' | sort -u | wc -l` = **413** unique
     defNames. Neither prose count matches the generator's current
     output -- likely stale from before a mod's group was trimmed
     (About.xml itself documents several such removals: Megafauna/Beasts
     of the Rim/Jurassic Rimworld retired 2026-09-05, five more removed
     2026-09-06). `megafauna_yield_group_count` below asserts the MEASURED
     34/413, not either stale prose figure.

MOD SETTINGS: none. No `Settings.cs`/`ModSettings` subclass anywhere in
this mod's tree (checked) -- `suite.toggles = []`, every component
`beyond_toggle=True`.

WHAT IS AND ISN'T PROVEN, and the mod's own dependency structure:
  - `megafauna_yield_group_count` and `bear_grizzly_yield_readback` are
    minimal-safe: the `Core` group (Bear_Grizzly is base-game) needs no
    third-party mod, per the walk's own step 3.
  - `droid_factory_hidden` and `asimov_flesh_type_isorganic_false` need
    "Outer Rim - Droid Depot" / Asimov active respectively (full list) --
    written as normal assertions rather than skipped, per this suite
    family's own precedent (Antiquities' Armoury dependency,
    StructureInjections' moisture-farm KotOR dependency): a minimal-only
    run will fail these two named, which is the CORRECT signal for that
    environment, not a script bug.
  - `droid_relations_fix_no_nre` (walk step 8) needs a live Outer Rim
    droid pawn. The walk doc explicitly warns "Do not guess a PawnKindDef
    defName here" (the offline dump has no Outer Rim content indexed).
    This suite uses `OuterRim_BattleDroid` -- NOT a guess, but the exact
    string `DoctrinePatches.cs`'s own top-of-file comment names as the
    def "Confirmed 10/10 in a batch test" for this very crash
    (DROIDWORKS_ISFLESH_RELATIONS_CRASH_1's own reproduction record).
    Still genuinely uncertain: whether that string is a ThingDef,
    PawnKindDef, or both (RimWorld convention usually differs the two),
    and whether `jawa/spawn_pawn`'s `kindDef` takes it directly -- the
    walk's own "resolve live on the day of the run" caveat stands if this
    guess is wrong.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Doctrine")
suite.toggles = []   # no Settings.cs anywhere in this mod's tree

MEGAFAUNA_GROUPS_MEASURED = 34     # grep -c 'PatchOperationFindMod', 2026-09-17
MEGAFAUNA_DEFNAMES_MEASURED = 413  # grep -oP defName="..." | sort -u | wc -l


def _get_defs(t, defs, fields):
    return t.bridge_call("jawa/get_defs", defs=defs, fields=fields)


def _row_for(r, def_key):
    for d in (r or {}).get("defs", (r or {}).get("results", [])) or []:
        if d.get("defName") == def_key.split("/", 1)[-1]:
            return d
    return None


@suite.chain("no_load_or_patch_errors")
def no_load_or_patch_errors(t):
    """Walk steps 1-2: no Config error naming this mod's packageId or any
    of its three Patch files, and neither of `DoctrinePatches.cs`'s own
    two hand-written failure strings appears (a failed Harmony install or
    a reflection miss on `CreateInitialComponents`, each logged
    explicitly rather than silently)."""
    with t.component("no_config_or_xml_error", beyond_toggle=True):
        for tag in ("Config error in mandrake.rut.doctrine",
                    "DroidsAreMachines.xml", "MegafaunaYield.xml",
                    "NoDroidManufacture.xml"):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=tag)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            bad = [m for m in msgs if "error" in m.lower() or "Config error" in m]
            t._record("drain_log(%r) error lines -> %r" % (tag, bad), not bad)
            if bad:
                raise ExpectationFailed(
                    "found an error-looking log line mentioning %r: %r" % (tag, bad))

    with t.component("no_harmony_or_reflection_failure", beyond_toggle=True):
        for line in (
            "[RimMandrake.Utinni.Doctrine] Failed to apply patches:",
            "[RimMandrake.Utinni.Doctrine] PawnComponentsUtility."
            "CreateInitialComponents not found by reflection",
        ):
            r = t.bridge_call("jawa/drain_log", limit=400, contains=line)
            msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
            ok = not msgs
            t._record("no log line matching %r -> %s" % (line, ok), ok)
            if not ok:
                raise ExpectationFailed(
                    "found the hand-written failure line %r: %r" % (line, msgs))


@suite.chain("megafauna_yield_group_count")
def megafauna_yield_group_count(t):
    """Structural, not a live-game check: confirms this suite's own MEASURED
    counts (module docstring's stale-walk finding #2) are what the CURRENT
    generated file on disk carries, so a future regeneration that changes
    the group/defName count is caught here rather than silently drifting
    further from either stale prose figure. Reads the file directly (the
    same measurement method used to write this suite), never the game."""
    import os
    import re
    with t.component("measured_counts_match_current_file", beyond_toggle=True):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "Patches", "MegafaunaYield.xml")
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            raise ExpectationFailed("could not read %s: %s" % (path, e))
        groups = text.count("PatchOperationFindMod")
        defnames = len(set(re.findall(r'defName="([^"]+)"', text)))
        ok = groups == MEGAFAUNA_GROUPS_MEASURED and defnames == MEGAFAUNA_DEFNAMES_MEASURED
        t._record("groups=%d (expected %d), unique defNames=%d (expected %d)"
                  % (groups, MEGAFAUNA_GROUPS_MEASURED, defnames,
                     MEGAFAUNA_DEFNAMES_MEASURED), ok)
        if not ok:
            raise ExpectationFailed(
                "MegafaunaYield.xml now measures groups=%d defNames=%d, "
                "expected %d/%d (this suite's own 2026-09-17 measurement) -- "
                "the file was regenerated; re-measure and update this suite "
                "AND note whether the walk doc's stale 35/424 or 42 figures "
                "need correcting too" % (groups, defnames,
                                          MEGAFAUNA_GROUPS_MEASURED,
                                          MEGAFAUNA_DEFNAMES_MEASURED))


@suite.chain("bear_grizzly_yield_readback")
def bear_grizzly_yield_readback(t):
    """Minimal-safe (walk step 3): Bear_Grizzly is base-game Core content,
    needs no third-party mod. MeatAmount/BoneAmount rewritten to
    unit*bodySize (301/108) so the engine's own StatPart_BodySize multiply
    lands the final value at unit*bodySize^2 (301*2.15=647.15,
    108*2.15=232.2, per the file's own inline comment)."""
    t.clear_area(size=10)
    with t.component("bear_grizzly_meat_and_bone_amount", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/Bear_Grizzly", "statBases")
        row = _row_for(r, "ThingDef/Bear_Grizzly")
        fields = (row or {}).get("fields") or {}
        stat_text = str(fields.get("statBases", ""))
        ok_meat = "301" in stat_text
        ok_bone = "108" in stat_text
        t._record("Bear_Grizzly.statBases -> %r" % stat_text, ok_meat and ok_bone)
        if not (ok_meat and ok_bone):
            raise ExpectationFailed(
                "Bear_Grizzly.statBases = %r, expected to contain MeatAmount "
                "301 and BoneAmount 108" % stat_text)


@suite.chain("droid_factory_hidden")
def droid_factory_hidden(t):
    """Needs 'Outer Rim - Droid Depot' active (full list) -- a minimal-only
    run fails this named, which is correct for that environment, not a
    bug. `OuterRim_DroidFactory` has zero attached RecipeDefs (its own
    file's header comment); clearing designationCategory is the only lever
    NoDroidManufacture.xml has, and this is the only thing it does."""
    with t.component("droid_factory_designation_and_description", beyond_toggle=True):
        r = _get_defs(t, "ThingDef/OuterRim_DroidFactory", "designationCategory,description")
        row = _row_for(r, "ThingDef/OuterRim_DroidFactory")
        if row is None:
            raise ExpectationFailed(
                "ThingDef OuterRim_DroidFactory did not resolve -- 'Outer Rim "
                "- Droid Depot' is not active in this environment")
        fields = row.get("fields") or {}
        got_cat = fields.get("designationCategory", "")
        ok_cat = not got_cat or got_cat in ("(no such field)", "None", "null")
        t._record("designationCategory -> %r (expect cleared)" % got_cat, ok_cat)
        if not ok_cat:
            raise ExpectationFailed(
                "OuterRim_DroidFactory.designationCategory = %r, expected "
                "cleared (empty)" % got_cat)
        got_desc = fields.get("description", "")
        ok_desc = "do not build these" in str(got_desc).lower()
        t._record("description -> %r" % got_desc, ok_desc)
        if not ok_desc:
            raise ExpectationFailed(
                "OuterRim_DroidFactory.description = %r, expected to contain "
                "'do not build these'" % got_desc)


@suite.chain("asimov_flesh_type_isorganic_false")
def asimov_flesh_type_isorganic_false(t):
    """Needs Asimov active (full list). Tests ONLY the Asimov_Automaton
    path -- see module docstring's stale-walk finding #1 for why the ABF
    Synstruct path the walk doc still names is not tested here (that
    Operation was removed from the mod 2026-09-10)."""
    with t.component("asimov_automaton_isorganic_false", beyond_toggle=True):
        r = _get_defs(t, "FleshTypeDef/Asimov_Automaton", "isOrganic")
        row = _row_for(r, "FleshTypeDef/Asimov_Automaton")
        if row is None:
            raise ExpectationFailed(
                "FleshTypeDef Asimov_Automaton did not resolve -- Asimov is "
                "not active in this environment")
        got = (row.get("fields") or {}).get("isOrganic", "")
        ok = str(got).lower() == "false"
        t._record("Asimov_Automaton.isOrganic -> %r" % got, ok)
        if not ok:
            raise ExpectationFailed(
                "FleshTypeDef Asimov_Automaton.isOrganic = %r, expected false"
                % got)


@suite.chain("droid_relations_fix_no_nre")
def droid_relations_fix_no_nre(t):
    """Walk step 8. Needs an Outer Rim droid pawn. `OuterRim_BattleDroid`
    is read verbatim off `DoctrinePatches.cs`'s own top-of-file comment
    ("Confirmed 10/10 in a batch test on the already-shipped
    OuterRim_BattleDroid") -- not a guess, but still genuinely uncertain
    whether it is the right string for `jawa/spawn_pawn`'s `kindDef=`
    (ThingDef vs PawnKindDef naming convention can differ). Pre-patch this
    would NRE the instant anything reads `pawn.relations`
    (DROIDWORKS_ISFLESH_RELATIONS_CRASH_1's own reproduction) -- a clean,
    non-erroring `jawa/pawn_relations` response IS the proof."""
    t.clear_area(size=15)
    with t.component("battle_droid_relations_tracker_non_null", beyond_toggle=True):
        r = t.bridge_call("jawa/spawn_pawn", kindDef="OuterRim_BattleDroid",
                          x=t.anchor[0], z=t.anchor[1], faction="player", count=1)
        rows = (r or {}).get("pawns") or []
        if not rows:
            raise ExpectationFailed(
                "jawa/spawn_pawn(kindDef='OuterRim_BattleDroid') produced no "
                "pawn -- either the defName is wrong (see this chain's own "
                "docstring) or Outer Rim - Droid Depot is not active: %r" % r)
        pid = rows[0].get("id")
        t.session.track("pawn", pid, x=t.anchor[0], z=t.anchor[1])

        try:
            rel = t.bridge_call("jawa/pawn_relations", pawn=pid, action="list")
            ok = rel is not None and "error" not in (rel or {})
        except Exception as e:
            ok, rel = False, str(e)
        t._record("pawn_relations(list) on OuterRim_BattleDroid -> %r" % rel, ok)
        if not ok:
            raise ExpectationFailed(
                "jawa/pawn_relations(list) failed/errored for a spawned "
                "OuterRim_BattleDroid -- this is exactly the NRE "
                "DROIDWORKS_ISFLESH_RELATIONS_CRASH_1 describes if the fix "
                "did not apply: %r" % rel)
        t.screenshot()
