// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1 -- capability discovery (spec §2.1). Reads the kernel's facts off a Thing.
// "A building with a glow": def.category Building plus a CompGlower, never a list of known lamps -- the live stack
// carries four separate lighting mods and all of them ship the stock CompGlower (Phase 0, Q3).
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_EmitterDiscovery
    {
        public static CompGlower GlowerOf(Thing t)
        {
            return (t as ThingWithComps)?.GetComp<CompGlower>();
        }

        public static RM_EmitterFacts FactsOf(Thing t)
        {
            ThingDef d = t.def;
            return new RM_EmitterFacts
            {
                isPawn = t is Pawn,
                isPlant = t is Plant || d?.plant != null,
                isApparelOrEquipment = t is Apparel || d != null && (d.IsApparel || d.equipmentType != EquipmentType.None),
                hologramMarked = d != null && d.HasModExtension<RM_AtmosphericExcluded>(),
                defName = d?.defName,
                thingClassName = d?.thingClass?.Name,
                hasGlower = GlowerOf(t) != null,
                isBuilding = d != null && d.category == ThingCategory.Building,
                playerOwned = t.Faction != null && t.Faction == Faction.OfPlayer,
                spawned = t.Spawned,
            };
        }

        public static RM_EmitterVerdict Classify(Thing t)
        {
            return t == null ? RM_EmitterVerdict.NoGlower : RM_AtmosphericKernel.Classify(FactsOf(t));
        }

        /// <summary>Every eligible emitter on the map, discovered by capability.</summary>
        public static IEnumerable<Building> EligibleOn(Map map)
        {
            List<Building> all = map.listerBuildings.allBuildingsColonist;
            for (int i = 0; i < all.Count; i++)
                if (Classify(all[i]) == RM_EmitterVerdict.Eligible)
                    yield return all[i];
        }
    }
}
