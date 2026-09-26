using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. The porter's "treasure trickle" (§2):
    // "it literally strips loot of its victims and scatters it near the
    // pools to attract you". A small hardcoded weighted table rather than
    // a full ThingSetMaker — this is a rare cosmetic deposit event, not a
    // reward economy needing full loot-table machinery. Weighted toward
    // plain currency (what a stripped victim carries) with the biome's own
    // resources (RM_SeepOil/RM_PottersClay/RM_OssagrelSap, already shipped
    // by FEVERWOOD_FLORA_ROSTER_1) as flavourful rarer finds. Vanilla
    // Silver/Gold are always loaded (Core); the three RM_ resources are
    // this mod's own, so no MayRequire is needed for any entry.
    public static class RM_TentacleLoot
    {
        private static readonly List<(string defName, float weight, int min, int max)> Table =
            new List<(string, float, int, int)>
            {
                ("Silver", 50f, 15, 60),
                ("Gold", 8f, 2, 10),
                ("RM_SeepOil", 15f, 1, 4),
                ("RM_PottersClay", 15f, 1, 4),
                ("RM_OssagrelSap", 12f, 1, 4),
            };

        public static ThingDef RollLoot(out int count)
        {
            float total = 0f;
            for (int i = 0; i < Table.Count; i++)
            {
                total += Table[i].weight;
            }
            float roll = Rand.Range(0f, total);
            for (int i = 0; i < Table.Count; i++)
            {
                roll -= Table[i].weight;
                if (roll <= 0f)
                {
                    count = Rand.RangeInclusive(Table[i].min, Table[i].max);
                    return DefDatabase<ThingDef>.GetNamedSilentFail(Table[i].defName);
                }
            }
            count = 0;
            return null;
        }
    }
}
