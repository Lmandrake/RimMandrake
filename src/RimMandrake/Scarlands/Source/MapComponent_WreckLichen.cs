using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Scarlands
{
    // WARSCAR_FREE_TIER_BODY_1: places RM_WreckLichen on open cells beside ruins
    // and wreck, never on open ground. Runs only on RM_Warscar maps. One pass
    // shortly after the map exists, then a slow top-up so scraped lichen returns.
    public class MapComponent_WreckLichen : MapComponent
    {
        private const int FirstPassTick = 60;
        private const int TopUpInterval = 15000;
        private const int MaxLichen = 400;
        private const float SeedChance = 0.3f;
        private const float TopUpChance = 0.02f;

        private bool seeded;

        public MapComponent_WreckLichen(Map map) : base(map) { }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seeded, "seeded", false);
        }

        // Ruins and wreck: any building whose defName starts "Ancient" (Odyssey's wall,
        // broken turrets, crane parts, trucks, junk) - never player or other-mod buildings.
        private static bool IsWreckAnchor(Thing t)
        {
            return t.def.category == ThingCategory.Building && t.def.defName.StartsWith("Ancient");
        }

        public override void MapComponentTick()
        {
            if (!RM_WarscarSettings.enableWreckLichenSeeder) return;
            if (map.Biome == null || map.Biome.defName != "RM_Warscar") return;
            int t = Find.TickManager.TicksGame;
            if (!seeded && t >= FirstPassTick)
            {
                seeded = true;
                Seed(SeedChance);
            }
            else if (seeded && t % TopUpInterval == 0)
            {
                Seed(TopUpChance);
            }
        }

        private void Seed(float chance)
        {
            ThingDef lichen = DefDatabase<ThingDef>.GetNamedSilentFail("RM_WreckLichen");
            if (lichen == null) return;
            int existing = map.listerThings.ThingsOfDef(lichen).Count;
            if (existing >= MaxLichen) return;

            List<Thing> all = new List<Thing>(map.listerThings.AllThings); // copy: spawning mutates the live list
            for (int i = 0; i < all.Count && existing < MaxLichen; i++)
            {
                Thing anchor = all[i];
                if (!anchor.Spawned || !IsWreckAnchor(anchor)) continue;
                foreach (IntVec3 c in anchor.OccupiedRect().ExpandedBy(1).Cells)
                {
                    if (existing >= MaxLichen) break;
                    if (!Rand.Chance(chance)) continue;
                    if (!c.InBounds(map) || !c.Walkable(map) || c.GetEdifice(map) != null) continue;
                    if (c.GetPlant(map) != null || c.GetTerrain(map).IsWater) continue;
                    Plant p = (Plant)ThingMaker.MakeThing(lichen);
                    p.Growth = Rand.Range(0.2f, 1f);
                    GenSpawn.Spawn(p, c, map);
                    existing++;
                }
            }
        }
    }
}
