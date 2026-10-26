using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FIRE_BAN_1 — "So there's no oxygen down in the sea floor so
    // it's not explosive." (owner, 2026-09-27, typed verbatim). Total ban
    // on ignition at the bottom of the Chill, everywhere EXCEPT:
    //   (a) a cell marked oxygenated (RM_MapComponent_ChillOxygenation —
    //       written by a running Odyssey oxygen pump in a sealed room,
    //       RM_CompChillAirSupply, and the hook CHILL_WARLAB_ROUTES_1
    //       hangs its burn routes on), or
    //   (b) a Thing whose def carries RM_SelfOxidizingExtension — Fuselight
    //       (CHILL_FLORA_BUILD_1, not yet built) is the one example, but
    //       this checks a DefModExtension flag, never a defName, so
    //       anything built later that ships this extension opts itself
    //       out for free. (ThingDef has no generic string-tags field —
    //       weaponTags/apparel.tags are narrow, purpose-built lists — so a
    //       marker DefModExtension is this codebase's actual idiom for
    //       "any def can opt in to X"; verified against the decompiled
    //       ThingDef/Def source, not assumed.)
    //
    // Surface/shore maps (the Chill's own BiomeDef, RM_TheChill, is the
    // surface too) and every other biome are completely untouched — this
    // gate only fires true-or-false for a specific MAP, and only a Chill
    // FLOOR map counts. There are two kinds of Chill floor map
    // (SEABED_FLOOR_GENERATORS_1), and the gate covers both:
    //   (1) the sea-dive hatch's pocket map: RM_SeaDiveGenerator_TheChill's
    //       pocketMapProperties.biome is RM_TheChill (RM_SeaDiveGenerators.xml),
    //       so that map's own Map.Biome.defName is "RM_TheChill" — the same
    //       defName as the surface biome, which is why a bare biome check
    //       cannot tell surface from floor. `Map.IsPocketMap` (a real engine
    //       flag, MEASURED against decompiled 1.6 PocketMapUtility / Game.cs,
    //       SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1) is what does: a surface
    //       Chill tile is an ordinary world-tile map (IsPocketMap == false).
    //   (2) a seabed-layer map: a world-tile map on the seabed planet layer
    //       (not a pocket map) whose SURFACE tile above it is RM_TheChill.
    // The identity is RM_SeaFloorIdentity.IsFloorOf(map, "RM_TheChill")
    // (RM_SeabedSiteParent.cs): pocket map → its own biome; seabed-layer
    // tile → the biome of the surface tile above; anything else → not a
    // floor. Never "RM_TheChill biome AND IsPocketMap" alone — that misses
    // every seabed-layer map.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_ChillFireGate
    {
        public const string ChillBiomeDefName = "RM_TheChill";

        /// <summary>
        /// True only for a Chill floor map (the hatch's pocket map or a seabed-layer map) — never the
        /// surface/shore map, even though both carry biome RM_TheChill.
        /// </summary>
        public static bool IsChillSeabedMap(Map map)
        {
            // SEABED_FLOOR_GENERATORS_1: the hatch's pocket map (biome RM_TheChill) or a
            // seabed-layer map under the Chill (RM_SeaFloorIdentity reads the surface above).
            return RM_SeaFloorIdentity.IsFloorOf(map, ChillBiomeDefName);
        }

        /// <summary>
        /// CHILL_THERMAL_ENGINE_1's ambient-severity hook. The pocket map's
        /// outdoor temperature (RM_SeaDiveGenerator_TheChill's own
        /// pocketMapProperties.temperature, -110) already IS the map's real
        /// ambient severity — Verse.MapTemperature.OutdoorTemp returns it
        /// directly for any pocket map, MEASURED off the decompiled engine,
        /// and vanilla's own Room.TempTracker.EqualizeTemperature() already
        /// pulls every unheated/underheated room toward it. No parallel
        /// MapComponent was built to duplicate this — it is already public,
        /// already live, and duplicating it would just be a second number
        /// that can drift from the real one. On a seabed-layer Chill floor map
        /// (not a pocket map) there is no pocketMapProperties.temperature: the
        /// method returns that map's own ordinary OutdoorTemp reading the same
        /// way. CHILL_HEATED_SUIT_1 (or
        /// anything else that needs "how brutal is it right now") reads
        /// this, not a private field. NaN off the Chill seabed — check
        /// IsChillSeabedMap first, or just test for NaN.
        /// </summary>
        public static float ChillSeabedAmbientC(Map map)
        {
            return IsChillSeabedMap(map) ? map.mapTemperature.OutdoorTemp : float.NaN;
        }

        public static bool IsSelfOxidizing(Thing t)
        {
            return t?.def != null && t.def.HasModExtension<RM_SelfOxidizingExtension>();
        }

        /// <summary>RM_NonCombustionExtension: a fuelled building that burns nothing (a fission reactor).</summary>
        public static bool BurnsNothing(Thing t)
        {
            return t?.def != null && t.def.HasModExtension<RM_NonCombustionExtension>();
        }

        /// <summary>
        /// The one call every ignition patch in Patch_ChillFireBan.cs
        /// routes through. True = fire may happen here; false = the ban
        /// applies. Every non-Chill-seabed map always returns true — this
        /// mechanism is invisible everywhere else, by construction.
        /// The decision itself is RM_ChillFireBanKernel.IgnitionAllowed (fuzzed offline); this reads its inputs.
        /// </summary>
        public static bool IsIgnitionAllowed(Map map, IntVec3 cell, Thing relevantThing = null)
        {
            if (!IsChillSeabedMap(map))
            {
                return true; // cheap reject: every other map
            }
            bool banEnabled = RM_DivingSettings.masterEnabled && RM_DivingSettings.chillFireBanEnabled;
            if (!banEnabled)
            {
                return true; // mod fully inert / this mechanic switched off — degrade to vanilla fire
            }
            RM_MapComponent_ChillOxygenation oxygenation = map.GetComponent<RM_MapComponent_ChillOxygenation>();
            return RM_ChillFireBanKernel.IgnitionAllowed(true, banEnabled,
                IsSelfOxidizing(relevantThing), BurnsNothing(relevantThing), insideBurningFire > 0,
                oxygenation != null && oxygenation.IsCellOxygenated(cell));
        }

        /// <summary>
        /// Above 0 while a Fire's TickInterval runs (Patch_Fire_TickInterval), a Fire's Spark lands (Patch_Spark_Impact)
        /// or a burning pawn dies (Patch_Pawn_Kill_CorpseFire): every ignition asked then is that fire spreading, damaging,
        /// attaching or relighting on the corpse, and its instigator's oxidizer no longer counts
        /// (CHILLFIREBAN_FIX_FUSELIGHT_FIRE_SPREADS, CHILLFIREBAN_FIX_SPARK_CARRIES_OXIDIZER,
        /// CHILLFIREBAN_FIX_CORPSE_FIRE_KEEPS_OXIDIZER). Main thread only, like the tick itself.
        /// </summary>
        internal static int insideBurningFire;

        /// <summary>
        /// Above 0 while FireUtility.TryStartFireIn or TryAttachFire runs a body this gate admitted: the Fire spawned then
        /// was asked for. A Fire spawned on the seabed with it at 0 came through no gate (a mod's own MakeThing + GenSpawn)
        /// and Patch_Fire_SpawnSetup judges it (CHILLFIREBAN_FIX_MODDED_DIRECT_FIRE_SPAWN). Main thread only.
        /// </summary>
        internal static int admittingFire;
    }

    /// <summary>
    /// Marker DefModExtension: "this fuelled building burns nothing" — CHILLFIREBAN_FIX_MELTDOWN_FIRE_ESCAPES_BAN.
    /// Read ONLY by the flame-building classification (RM_ChillFireBanKernel.UsesFlame): the building keeps making
    /// power, heat and light on the seabed. It is NOT an oxidizer: fire it instigates (a meltdown's flame explosions)
    /// is banned like any other. VQE's four uranium Genetrons carry it (Patches/RM_ChillFireBan_FissionGenetrons.xml).
    /// Use RM_SelfOxidizingExtension only for a thing whose own fire really burns without air (Fuselight).
    /// </summary>
    public class RM_NonCombustionExtension : DefModExtension
    {
    }

    /// <summary>
    /// Marker DefModExtension: "this def carries its own oxidizer, ignore
    /// the Chill's no-oxygen ignition ban for it." Add
    /// &lt;modExtensions&gt;&lt;li Class="RimMandrake.DivingInteraction.RM_SelfOxidizingExtension" /&gt;&lt;/modExtensions&gt;
    /// to Fuselight's ThingDef (CHILL_FLORA_BUILD_1) — or to anything else
    /// built later — to opt it out of the ban. No fields: presence alone
    /// is the flag.
    /// </summary>
    public class RM_SelfOxidizingExtension : DefModExtension
    {
    }
}
