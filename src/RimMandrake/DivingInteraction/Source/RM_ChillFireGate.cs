using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_FIRE_BAN_1 — "So there's no oxygen down in the sea floor so
    // it's not explosive." (owner, 2026-09-27, typed verbatim). Total ban
    // on ignition at the bottom of the Chill, everywhere EXCEPT:
    //   (a) a cell some future mechanism has marked oxygenated
    //       (RM_MapComponent_ChillOxygenation — this is the hook
    //       CHILL_WARLAB_ROUTES_1 hangs its burn routes on), or
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
    // gate only fires true-or-false for a specific MAP, and the surface
    // Chill map never carries RM_SeaDiveGenerator_TheChill's identity.
    // The pocket map IS the identity: RM_SeaDiveGenerator_TheChill's own
    // pocketMapProperties.biome is RM_TheChill (RM_SeaDiveGenerators.xml),
    // so the seabed pocket map's own Map.Biome.defName is ALSO
    // "RM_TheChill" — same defName as the surface biome. That means a
    // bare biome-defName check cannot tell surface from seabed by itself.
    //
    // What DOES distinguish them, read off the engine (PocketMapUtility /
    // Game.cs, MEASURED against decompiled 1.6 source, same evidence base
    // as RM_SeaDiveGenerators.xml's own destroyOnParentMapAbandoned
    // comment, SEADIVEHATCH_CACHES_FIRST_SEA_FLOOR_1): every pocket map's
    // MapParent is a Building_MapPortal-owned PocketMapParent whose
    // ParentedMap (the map that owns the portal back to the surface) is
    // non-null, and `Map.IsPocketMap` is a real, distinct engine flag no
    // ordinary overworld map carries. A surface Chill tile is a normal
    // world-tile map (IsPocketMap == false); the seabed is always a
    // pocket map (IsPocketMap == true). ⇒ the real identity check is
    // "RM_TheChill biome AND IsPocketMap", not the biome alone.
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
        /// that can drift from the real one. CHILL_HEATED_SUIT_1 (or
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

        /// <summary>
        /// The one call every ignition patch in Patch_ChillFireBan.cs
        /// routes through. True = fire may happen here; false = the ban
        /// applies. Every non-Chill-seabed map always returns true — this
        /// mechanism is invisible everywhere else, by construction.
        /// </summary>
        public static bool IsIgnitionAllowed(Map map, IntVec3 cell, Thing relevantThing = null)
        {
            if (!IsChillSeabedMap(map))
            {
                return true;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillFireBanEnabled)
            {
                return true; // mod fully inert / this mechanic switched off — degrade to vanilla fire
            }
            if (IsSelfOxidizing(relevantThing))
            {
                return true; // carries its own oxidizer — Fuselight's future exemption
            }
            RM_MapComponent_ChillOxygenation oxygenation = map.GetComponent<RM_MapComponent_ChillOxygenation>();
            return oxygenation != null && oxygenation.IsCellOxygenated(cell);
        }
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
