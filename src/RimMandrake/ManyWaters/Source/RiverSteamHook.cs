using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RiverSteamHook
{
    // Ambient visual only: rivers on the Pyrelands (ZBiome_Grasslands) throw
    // periodic steam puffs, per the owner's ask (RIVER_STEAM_ANIMATION_1).
    // Reuses vanilla's own "Steam" FleckDef (Defs/Ideology/Effects/Fleck_Visual.xml,
    // ParentName="FleckBase_Thrown") and the exact river-cell test
    // RimWorld.SeasonalFlood already uses (TerrainDef.IsRiver) -- no new art,
    // no heat push, no gameplay effect. MapComponent subclasses are
    // auto-instantiated per map by Map.FillComponents(), so no Harmony/XML
    // registration is needed.
    public class MapComponent_RiverSteam : MapComponent
    {
        private static readonly IntRange TicksBetweenPuffs = new IntRange(90, 260);

        private List<IntVec3> riverCells;
        private int nextPuffTick = -1;
        private FleckDef steamFleck;

        public MapComponent_RiverSteam(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            steamFleck = DefDatabase<FleckDef>.GetNamedSilentFail("Steam");
            riverCells = new List<IntVec3>();

            // Pyrelands only ("stormy savanna", ZBiome_Grasslands) -- not every
            // river on every biome. See ASHKARR_WORLD_DEFINITION.md's biome table.
            if (map.Biome == null || map.Biome.defName != "ZBiome_Grasslands")
            {
                return;
            }

            foreach (IntVec3 c in map.AllCells)
            {
                if (c.GetTerrain(map).IsRiver)
                {
                    riverCells.Add(c);
                }
            }

            ScheduleNext();
        }

        public override void MapComponentTick()
        {
            if (steamFleck == null || riverCells == null || riverCells.Count == 0)
            {
                return;
            }

            if (Find.TickManager.TicksGame < nextPuffTick)
            {
                return;
            }

            IntVec3 cell = riverCells[Rand.Range(0, riverCells.Count)];
            if (!cell.Fogged(map))
            {
                Vector3 loc = cell.ToVector3Shifted();
                FleckCreationData data = FleckMaker.GetDataStatic(loc, map, steamFleck, Rand.Range(1f, 1.8f));
                data.velocityAngle = Rand.Range(60, 120);
                data.velocitySpeed = Rand.Range(0.15f, 0.3f);
                map.flecks.CreateFleck(data);
            }

            ScheduleNext();
        }

        private void ScheduleNext()
        {
            nextPuffTick = Find.TickManager.TicksGame + TicksBetweenPuffs.RandomInRange;
        }
    }
}
