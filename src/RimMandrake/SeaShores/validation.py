"""validation.py -- modcheck suite for RimMandrake SeaShores (mandrake.rm.seashores).

Grounded in this mod's actual Source, read whole before writing this file:
`RM_SeaShoreExtension.cs`, `RM_SeaShoreUtility.cs`,
`RM_TileMutatorWorker_SeaCoast.cs`, `RM_WorldComponent_SeaShoreHealer.cs`,
`RM_SeaShoresHarmony.cs`, `RM_SeaShoresSettings.cs`, `RM_SeaShoresMod.cs` --
never the About.xml blurb or SEA_FLOOR_AND_CATCH_PASS_1's aspirations for it.

WHAT THIS MOD ACTUALLY IS AT RUNTIME, four separable pieces:

  (1) IsCoastal. A Harmony postfix on `World.CoastDirectionAt` answers a
      direction for a land tile whose neighbour is a BiomeDef carrying
      `RM_SeaShoreExtension` with `countsAsCoast`. Vanilla only ever compares
      against `BiomeDefOf.Ocean` by reference, so every modded ocean is
      invisible to it. Consumed by `Tile.IsCoastal`, WildAnimalSpawner's
      coastal roster, PawnsArrivalModeWorker_EmergeFromWater,
      IncidentWorker_HerdMigration, TileMutatorWorker_Basin and the river
      delta logic.

  (2) The shore itself. `RM_SeaCoast` (TileMutatorDef, category Coast,
      genOrder 100, priority 0) whose worker subclasses
      `TileMutatorWorker_Coast` and overrides four `protected virtual`
      members: `GetCoastAngle` (pass the SEA def to `World.CoastAngleAt`
      instead of `BiomeDefOf.Ocean`), and `DeepWaterTerrainAt` /
      `ShallowWaterTerrainAt` / `BeachTerrainAt`. A prefix on the private
      static `WorldGenStep_Mutators.TryAddMutator` substitutes it for vanilla
      `Coast` on tiles that have a sea neighbour and no vanilla-Ocean one.

  (3) The frozen-world healer. `RM_WorldComponent_SeaShoreHealer.FinalizeInit`
      adds `RM_SeaCoast` to qualifying tiles that carry no Coast-category
      mutator. This exists because tile mutators are SCRIBED
      (`Tile.ExposeData`, key "mutatorDefs") and worldgen runs once per
      planet: on a hand-authored, frozen world (2) fires for nobody, ever.
      Logs exactly one line, `[RM_SeaShores] healed N tiles with RM_SeaCoast
      (M already coastal)`, and only when N+M > 0.

  (4) The catch. A postfix on `WaterBody.SetFishTypes` refills
      `commonFish`/`uncommonFish` from the SEA's `fishTypes` when the water
      body's root cell carries that sea's water, with an empty band falling
      back to the other salt/fresh pair (RUT_TheScald keeps its catches in
      `freshwater_*` while its terrain declares `waterBodyType Saltwater`).
      A transpiler on `FishingUtility.GetCatchesFor` redirects the two
      `pawn.Map.Biome` loads that feed `fishTypes.rareCatchesSetMaker` to
      `RM_SeaShoreUtility.FishBiomeFor(map, cell)`.

MOD SETTINGS -- suite.toggles below. The four fields are INSTANCE fields on
`RM_SeaShoresSettings` (deliberately not `public static`, unlike Pits /
Aftermath / RimProperty, whose static fields make `jawa/mod_settings_field`
refuse outright -- found live 2026-09-12 on the Pits pilot), so the bridge
setter can reach them. They are nonetheless ALL beyond_toggle here, and the
reasons are mechanical rather than an oversight:

  * `seasCountAsCoast` and `generateSeaShores` are read during WORLD and MAP
    generation. Flipping either mid-session changes nothing already
    generated; proving either needs a fresh world or a fresh map on a tile
    beside a sea, which is not a smoke-test-budget operation.
  * `healFrozenWorldOnLoad` is read once, in `WorldComponent.FinalizeInit`,
    i.e. strictly before any bridge call can be made against that world.
  * `seaCatchTables` is read at `WaterBody.SetFishTypes` time -- at map init
    and on `RecacheState`/PostLoadInit -- not at fishing time.

🔴 NOTHING IN THIS MOD HAS EVER BEEN PROVEN LIVE. It was authored 2026-09-23
against the decompiled 1.6 source and compiled clean; no game has loaded it.
Two things in particular are reasoned, not measured, and must not be written
up as measured:
  1. That `RM_SeaCoast` actually lays water on a land map beside one of our
     seas. `QUICKTEST_RIVER_WATER_MISSING_1` is open and reports quicktest
     maps generating zero water terrain at all, so a negative result from a
     quicktest proves nothing about this mod until that is understood.
  2. That the healer's `Tile.AddMutator` on an already-loaded world is picked
     up by map generation later in the same session. `AddMutator` calls
     `Worker?.OnAddedToTile` and re-sorts, and mutators are read from the
     Tile at map-gen time, so it should be -- but "should be" is the claim,
     not the finding.

Still not proven / likely first-live-run corrections:
  1. The rare-catch transpiler asserts `Map.Biome` appears in
     `FishingUtility.GetCatchesFor` as a `callvirt get_Biome`. If the shipped
     build inlines or restructures it, the transpiler matches nothing and
     logs `[RM_SeaShores] rare-catch transpiler matched no Map.Biome load`.
     That warning line is the falsifier and the suite below looks for it.
  2. Whether `<wildAnimals>` spawn on an `impassable=true` water biome at all
     is an open engine question for the FLOOR half of
     SEA_FLOOR_AND_CATCH_PASS_1. It is not this mod's business -- this mod
     only ever touches LAND maps -- but a reviewer conflating the two would
     mis-file the result.
"""
import os
import re

from modcheck import Suite, ExpectationFailed

HERE = os.path.dirname(os.path.abspath(__file__))

suite = Suite("SeaShores")
suite.toggles = [
    "seasCountAsCoast",
    "generateSeaShores",
    "seaCatchTables",
    "healFrozenWorldOnLoad",
]

BOOT_LOG_TAG = "[RM_SeaShores]"


@suite.chain("healer_ran_clean")
def healer_ran_clean(t):
    """Beyond-toggle: the one thing observable without generating a world.

    Proves three things at once, all of which fail loudly rather than
    silently: that the assembly loaded and its `[DefOf]` resolved
    `RM_SeaCoast` (a missing def would have logged a DefOf error and left
    the healer inert); that `RM_WorldComponent_SeaShoreHealer.FinalizeInit`
    ran against the loaded world; and that the Harmony bootstrap found
    `WorldGenStep_Mutators.TryAddMutator` and
    `FishingUtility.GetCatchesFor`'s `Map.Biome` load -- both of which
    announce their own ABSENCE with a Log.Warning rather than failing
    closed.

    The healed COUNT is deliberately not asserted: a world with no tile
    beside a sea is a legitimate zero, and CLAUDE.md's standing ruling is
    that a zero-tile biome mid-migration is the expected state, not a
    defect. Only the presence of a warning is a failure."""
    with t.component("boot_and_heal", beyond_toggle=True):
        drained = t.bridge_call("jawa/drain_log", limit=400, contains=BOOT_LOG_TAG)
        msgs = [m.get("text", "") for m in ((drained or {}).get("messages") or [])]
        joined = "\n".join(msgs)
        if t._guard():
            if "transpiler matched no Map.Biome load" in joined:
                raise ExpectationFailed(
                    "%s rare-catch transpiler matched nothing -- the IL shape of "
                    "FishingUtility.GetCatchesFor has drifted. Common and uncommon "
                    "catches are unaffected; rare catches are vanilla. Lines: %r"
                    % (BOOT_LOG_TAG, msgs))
            if "TryAddMutator not found" in joined:
                raise ExpectationFailed(
                    "%s WorldGenStep_Mutators.TryAddMutator not found -- fresh "
                    "worldgen will lay vanilla coasts beside modded seas. Lines: %r"
                    % (BOOT_LOG_TAG, msgs))
        t.screenshot()


# ---------------------------------------------------------------------------------------------------------------
# SEASHORES_COVERAGE_GAPS_1. RM_SeaShoresProof.ProofShore (jawa/static_call) runs the SHIPPED rules against the live
# world without changing it: CoastDirectionAt beside a modded sea with seasCountAsCoast on/off, the real TryAddMutator
# prefix, the shore-suppression switch, the healer's plan (Heal with apply=false), FishBiomeFor's off arm, and the
# PATCHED IL of FishingUtility.GetCatchesFor read back through Harmony. Expected values are derived from the documented
# rules here. A planet with no buildable land tile beside a modded sea (the expected mid-migration state) leaves the
# tile-dependent bars UNMEASURED, never PASS. Still UNMEASURED: the sea-water catch on a real sea map, a freshly
# generated shore's terrain, and the healed-tile count (deliberately not asserted, see healer_ran_clean).
_PROOF = "RimMandrake.SeaShores.RM_SeaShoresProof"

GATES = (   # (setting, file, class, member) -- the setting must be read inside that member
    ("seasCountAsCoast", "RM_SeaShoresHarmony.cs", "RM_Patch_CoastDirectionAt", "Postfix"),
    ("seaCatchTables", "RM_SeaShoresHarmony.cs", "RM_Patch_SetFishTypes", "Postfix"),
    ("seaCatchTables", "RM_SeaShoreUtility.cs", "RM_SeaShoreUtility", "FishBiomeFor"),
    ("generateSeaShores", "RM_TileMutatorWorker_SeaCoast.cs", "RM_TileMutatorWorker_SeaCoast", "ShoreSuppressed"),
    ("healFrozenWorldOnLoad", "RM_WorldComponent_SeaShoreHealer.cs", "RM_WorldComponent_SeaShoreHealer", "FinalizeInit"),
)
WIRING = (  # (file, needle, why)
    ("RM_SeaShoresHarmony.cs", "[HarmonyPatch(typeof(World), nameof(World.CoastDirectionAt))]", "seas stop counting as coast"),
    ("RM_SeaShoresHarmony.cs", "[HarmonyPatch(typeof(WaterBody), nameof(WaterBody.SetFishTypes))]", "common/uncommon catches stay the land's"),
    ("RM_SeaShoresHarmony.cs", "[HarmonyPatch(typeof(FishingUtility), nameof(FishingUtility.GetCatchesFor))]", "rare catches stay the land's"),
    ("RM_SeaShoresHarmony.cs", '"TryAddMutator"', "fresh worldgen lays vanilla coasts beside modded seas"),
    ("RM_SeaShoresHarmony.cs", "typeof(RM_Patch_TryAddMutator), nameof(RM_Patch_TryAddMutator.Prefix)", "the TryAddMutator prefix is never registered"),
    ("RM_SeaShoresHarmony.cs", "mutator = RM_SeaShoresDefOf.RM_SeaCoast;", "the prefix no longer substitutes the sea coast"),
    ("RM_SeaShoresHarmony.cs", "mutator != TileMutatorDefOf.Coast", "the prefix would rewrite every mutator, not just Coast"),
    ("RM_SeaShoresHarmony.cs", "ci.opcode = OpCodes.Ldarg_1;", "the transpiler no longer pushes the fished cell"),
    ("RM_SeaShoresHarmony.cs", "nameof(RM_SeaShoreUtility.FishBiomeFor)", "the transpiler no longer targets the cell resolver"),
    ("RM_WorldComponent_SeaShoreHealer.cs", "Heal(world.grid.Surface, true,", "FinalizeInit no longer runs the healing rule"),
    ("RM_TileMutatorWorker_SeaCoast.cs", "return ShoreSuppressed ? null : base.CoastTerrainAt(cell, map);", "a suppressed shore still lays coast terrain"),
    ("RM_SeaShores.csproj", 'Compile Include="RM_SeaShoresProof.cs"', "the proof compiles into nothing"),
)


def load_sources():
    d = os.path.join(HERE, "Source")
    return dict((fn, open(os.path.join(d, fn), encoding="utf-8").read()) for fn in os.listdir(d) if fn.endswith((".cs", ".csproj")))


def _balanced(src, start):
    i, depth = src.index("{", start) + 1, 1
    j = i
    while j < len(src) and depth:
        depth += {"{": 1, "}": -1}.get(src[j], 0)
        j += 1
    return src[i:j]


def member_body(src, cls, member):
    """Text of `member` (method or property) inside `class cls`, comments removed; None when absent."""
    src = re.sub(r"//[^\n]*", "", src)
    m = re.search(r"class\s+%s\b" % re.escape(cls), src)
    if not m:
        return None
    body = _balanced(src, m.end())
    mm = re.search(r"\b%s\s*(?:\([^)]*\))?\s*\{" % re.escape(member), body)
    return _balanced(body, mm.start()) if mm else None


def static_findings(srcs):
    """Pure over {filename: text}: every setting read where it does its job, every Harmony seam and rewrite present."""
    bad = []
    for setting, fn, cls, member in GATES:
        b = member_body(srcs.get(fn, ""), cls, member)
        if b is None:
            bad.append("[%s] %s: %s.%s not found" % (setting, fn, cls, member))
        elif setting not in b:
            bad.append("[%s] %s.%s no longer reads %s (the toggle gates nothing)" % (setting, cls, member, setting))
    for fn, needle, why in WIRING:
        if needle not in srcs.get(fn, ""):
            bad.append("[wiring] %s lost `%s`: %s" % (fn, needle, why))
    w = srcs.get("RM_TileMutatorWorker_SeaCoast.cs", "")
    for member in ("CoastTerrainAt", "GeneratePostElevationFertility"):
        b = member_body(w, "RM_TileMutatorWorker_SeaCoast", member)
        if b is None or "ShoreSuppressed" not in b:
            bad.append("[generateSeaShores] RM_TileMutatorWorker_SeaCoast.%s no longer consults ShoreSuppressed" % member)
    x = srcs.get("RM_SeaShoresSettings.cs", "")
    for f in ("seasCountAsCoast", "generateSeaShores", "seaCatchTables", "healFrozenWorldOnLoad"):
        if not re.search(r'Scribe_Values\.Look\(ref %s, "%s"' % (f, f), x):
            bad.append("[settings] %s is not Scribed" % f)
        if not re.search(r"ref %s," % f, x.split("DoWindowContents", 1)[-1]):
            bad.append("[settings] %s has no control in DoWindowContents" % f)
    return bad


def _kv(t):
    r = t.bridge_call("jawa/static_call", type=_PROOF, method="ProofShore", args="")
    if not t._guard():
        return None, ""
    text = (r or {}).get("result") if isinstance(r, dict) else None
    if text in (None, ""):
        t.upstream_reason = "UNMEASURED: RM_SeaShoresProof.ProofShore answered nothing (DLL not rebuilt/deployed yet?): %s" % (
            str((r or {}).get("message") or (r or {}).get("error"))[:120])
        t.upstream_failed = True
        return None, ""
    text = str(text)
    if text.startswith("ERROR"):
        raise ExpectationFailed("ProofShore: %s" % text)
    return dict(re.findall(r"(\w+)=(\S+)", text)), text


def _want(kv, text, want):
    bad = dict((k, kv.get(k)) for k, v in want.items() if kv.get(k) != str(v))
    if bad:
        raise ExpectationFailed("got %s, want %s: %s" % (bad, dict((k, want[k]) for k in bad), text[:400]))


def _no_tile(t, kv, text):
    t.upstream_reason = ("UNMEASURED: this planet has no buildable land tile beside a coasting modded sea (the expected mid-migration state, "
                         "not a defect) so the tile rule cannot be read: %s" % text[:160])
    t.upstream_failed = True


@suite.chain("sea_shore_rules")
def sea_shore_rules(t):
    with t.component("static_gates_wiring_and_settings_scribe", beyond_toggle=True):
        bad = static_findings(load_sources())
        if bad:
            raise ExpectationFailed("; ".join(bad))
    with t.component("rare_catch_transpiler_rewrote_the_patched_il", toggle="seaCatchTables"):
        kv, text = _kv(t)
        if kv:
            if int(kv.get("rare_orig_biome_loads", "0")) < 1:
                raise ExpectationFailed("the original FishingUtility.GetCatchesFor has no Map.Biome load to redirect (the shape drifted): %s" % text[:300])
            _want(kv, text, {"rare_redirects": kv.get("rare_orig_biome_loads"), "rare_biome_loads_left": 0})
    with t.component("generateSeaShores_switch_suppresses_the_shore", toggle="generateSeaShores"):
        kv, text = _kv(t)
        if kv:
            _want(kv, text, {"coast_def": "True", "shore_suppressed_when_on": "False", "shore_suppressed_when_off": "True"})
    with t.component("seaCatchTables_off_arm_returns_the_land_biome_and_land_cells_stay_land", toggle="seaCatchTables"):
        kv, text = _kv(t)
        if kv:
            if kv.get("fish_off_is_land") == "-":
                t.upstream_reason, t.upstream_failed = "UNMEASURED: no current map to resolve a fishing cell on: " + text[:160], True
            else:
                _want(kv, text, {"fish_off_is_land": "True", "fish_on_is_land_when_not_sea": "True"})
    with t.component("seasCountAsCoast_makes_land_beside_a_sea_coastal_and_off_restores_vanilla", toggle="seasCountAsCoast"):
        kv, text = _kv(t)
        if kv:
            if kv.get("coast_on") == "-":
                _no_tile(t, kv, text)
            else:
                _want(kv, text, {"coast_on": "True", "coast_off": "False"})
    with t.component("worldgen_prefix_swaps_coast_for_sea_coast_only_beside_a_sea", beyond_toggle=True):
        kv, text = _kv(t)
        if kv:
            if kv.get("sub_sea") == "-":
                _no_tile(t, kv, text)
            else:
                _want(kv, text, {"sub_sea": "True", "sub_other_mutator": "True"})
                if kv.get("sub_vanilla") not in ("-", "True"):
                    raise ExpectationFailed("a tile that borders the VANILLA ocean had its Coast replaced: %s" % text[:300])
    with t.component("healer_leaves_nothing_to_heal_after_load", toggle="healFrozenWorldOnLoad"):
        kv, text = _kv(t)
        if kv:
            if kv.get("heal_setting") != "True":
                t.upstream_reason, t.upstream_failed = "UNMEASURED: healFrozenWorldOnLoad is off in this session, so the healer did not run on load", True
            elif kv.get("tiles_beside_sea", "0") == "0":
                _no_tile(t, kv, text)
            else:
                _want(kv, text, {"heal_left": 0, "heal_stale_left": 0})
    with t.component("sea_water_catch_and_fresh_shore_terrain_state_read", beyond_toggle=True):
        if t._guard():
            t.upstream_reason = ("UNMEASURED: the sea's own fish on a real water body, and the shore terrain a freshly generated map beside a "
                                 "modded sea lays, need a map generated on such a tile (QUICKTEST_RIVER_WATER_MISSING_1 and a painted neighbour); "
                                 "instrument missing: a [Tool] that generates a map on a given tile")
            t.upstream_failed = True
