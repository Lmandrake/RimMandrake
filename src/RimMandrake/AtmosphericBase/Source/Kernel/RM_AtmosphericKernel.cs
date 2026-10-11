// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- the pure decision: may the framework drive this thing?
// Spec design/RimMandrake/atmospheric_base_mod_definition.md §2.1: discovered by CAPABILITY (a building with a glow),
// never a def whitelist; and NEVER glowing animals, worn equipment, plants or holograms (L16: a hologram is a god's
// body). Exclusions are tested first, so a thing that is both a building and a hologram is a hologram.
// No game types here: the facts are read from a Thing in RM_EmitterDiscovery and the selftest feeds them directly.
using System;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_EmitterVerdict
    {
        Eligible = 0,
        ExcludedPawn,          // glowing animals, and every other pawn
        ExcludedPlant,
        ExcludedWornOrEquipment,
        ExcludedHologram,
        NoGlower,
        NotABuilding,
        NotPlayerOwned,
        NotSpawned,
    }

    public struct RM_EmitterFacts
    {
        public bool isPawn;
        public bool isPlant;
        public bool isApparelOrEquipment;
        public bool hologramMarked;     // carries RM_AtmosphericExcluded
        public string defName;
        public string thingClassName;
        public bool hasGlower;
        public bool isBuilding;
        public bool playerOwned;
        public bool spawned;
    }

    public static class RM_AtmosphericKernel
    {
        public static bool LooksLikeHologram(string defName, string thingClassName)
        {
            return Has(defName, "holo") || Has(thingClassName, "holo");
        }

        private static bool Has(string s, string needle)
        {
            return !string.IsNullOrEmpty(s) && s.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0;
        }

        public static RM_EmitterVerdict Classify(RM_EmitterFacts f)
        {
            if (f.isPawn) return RM_EmitterVerdict.ExcludedPawn;
            if (f.isPlant) return RM_EmitterVerdict.ExcludedPlant;
            if (f.isApparelOrEquipment) return RM_EmitterVerdict.ExcludedWornOrEquipment;
            if (f.hologramMarked || LooksLikeHologram(f.defName, f.thingClassName)) return RM_EmitterVerdict.ExcludedHologram;
            if (!f.hasGlower) return RM_EmitterVerdict.NoGlower;
            if (!f.isBuilding) return RM_EmitterVerdict.NotABuilding;
            if (!f.playerOwned) return RM_EmitterVerdict.NotPlayerOwned;
            if (!f.spawned) return RM_EmitterVerdict.NotSpawned;
            return RM_EmitterVerdict.Eligible;
        }

        public static bool IsHardExclusion(RM_EmitterVerdict v)
        {
            return v == RM_EmitterVerdict.ExcludedPawn || v == RM_EmitterVerdict.ExcludedPlant
                || v == RM_EmitterVerdict.ExcludedWornOrEquipment || v == RM_EmitterVerdict.ExcludedHologram;
        }
    }
}
