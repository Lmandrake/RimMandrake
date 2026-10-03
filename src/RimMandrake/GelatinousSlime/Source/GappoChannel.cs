using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // GELATINOUSSLIME_GAPPO_FAMILY_1: the greater gappo's scoop leaves a clean channel behind it.
    // Every rare tick, while the creature is up and on the map, the cell under it that is soft
    // slime ground (tagged RM_SlimeTerrain, not the liquid) is set to RM_Slime_Hardened and any
    // slime smear on it is wiped. Tag-driven like the rest of the mod: no defName list of ground.
    // Gated by SlimeSettings.gappoChannels. Numbers are // INVENTED.
    public class RM_CompProperties_GappoChannel : CompProperties
    {
        public RM_CompProperties_GappoChannel()
        {
            compClass = typeof(RM_CompGappoChannel);
        }
    }

    public class RM_CompGappoChannel : ThingComp
    {
        private static TerrainDef hardened;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!SlimeSettings.gappoChannels) return;
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead || pawn.Downed) return;

            Map map = pawn.Map;
            IntVec3 c = pawn.Position;
            if (hardened == null) hardened = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_Slime_Hardened");
            if (hardened == null) return;

            TerrainDef here = c.GetTerrain(map);
            if (here != null && here != hardened && here.HasTag(SlimeDefs.SlimeTerrainTag)
                && here.defName != "RM_Slime_Liquid")
            {
                map.terrainGrid.SetTerrain(c, hardened);
            }

            List<Thing> things = c.GetThingList(map);
            for (int i = things.Count - 1; i >= 0; i--)
            {
                if (things[i] is Filth && things[i].def.defName == "RM_Filth_SlimeSmear")
                    things[i].Destroy();
            }
        }
    }
}
