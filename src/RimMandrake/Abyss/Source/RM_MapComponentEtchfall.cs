using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Abyss
{
    // ABYSS_ETCHFALL_BUILD_1. The Dark's falling grain erodes UNROOFED natural rock and steel
    // structures, leaving tholin dust; where rock is eaten through, the cell becomes etch-hollow
    // (the etchcap's only ground). Roofed cells (including mountain roof) are immune.
    // No state is stored: all of it is read off the map each pass, so there is nothing to Scribe.
    public class RM_MapComponent_Etchfall : MapComponent
    {
        private const int PassInterval = 250;
        private const int CellsPerPass = 24;       // tries per pass at strength 1
        private const float DamagePerHit = 6f;     // at strength 1

        public RM_MapComponent_Etchfall(Map map) : base(map) { }

        /// <summary>The grain hook. Until ABYSS_DARK_BUILD_1 supplies the Dark as a real weather/overlay,
        /// the grain falls wherever the biome is the Abyss. DARK replaces this body, nothing else.</summary>
        public static bool IsGrainfall(Map map)
        {
            return map?.Biome != null && map.Biome.defName == "RM_Abyss";
        }

        public static bool Erodible(Thing edifice)
        {
            if (edifice == null || edifice.Destroyed || edifice.def.building == null) return false;
            if (edifice.def.building.isNaturalRock) return true;
            return edifice.Stuff == ThingDefOf.Steel;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % PassInterval != 0) return;
            float strength = RM_AbyssSettings.etchfallStrength;
            if (strength <= 0.001f || !IsGrainfall(map)) return;

            int tries = Mathf.CeilToInt(CellsPerPass * strength);
            for (int i = 0; i < tries; i++)
            {
                IntVec3 c = CellRect.WholeMap(map).RandomCell;
                if (c.Roofed(map)) continue;
                Thing e = c.GetEdifice(map);
                if (!Erodible(e)) continue;
                Erode(c, e, DamagePerHit * strength);
            }
        }

        private void Erode(IntVec3 c, Thing e, float amount)
        {
            bool rock = e.def.building.isNaturalRock;
            e.TakeDamage(new DamageInfo(DamageDefOf.Deterioration, amount));
            ThingDef dust = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Tholin");
            if (dust != null && Rand.Chance(0.5f))
            {
                Thing d = ThingMaker.MakeThing(dust);
                d.stackCount = Rand.RangeInclusive(1, 3);
                GenPlace.TryPlaceThing(d, c, map, ThingPlaceMode.Near);
            }
            if (rock && e.Destroyed && c.GetEdifice(map) == null)
            {
                TerrainDef hollow = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_EtchHollow");
                if (hollow != null) map.terrainGrid.SetTerrain(c, hollow);
            }
        }
    }
}
