using System;
using System.Collections.Generic;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.GelatinousSlime
{
    // ════════════════════════════════════════════════════════════════════
    // THE DYNAMIC VISITORS (spec §2 + spike C).
    //
    // The biome's wildAnimals table holds exactly one entry, RM_Gelatid, and
    // that is deliberate. Spec §1: the body's fiction is "every genome that
    // ever touched it is in circulation", and the campaign's specific
    // trace-tail creatures stay campaign-side. So the cast here is generated:
    //
    //   "ambient density: spawn pulls from NEIGHBOURING world tiles' biomes'
    //    wildAnimals (universal — works on any planet, any mod set), arriving
    //    PRE-STAGED."  — spec, spike C
    //
    // A hand-written animal list would be a lie about a biome whose whole
    // point is that it is made of whatever wandered in. This reads the actual
    // neighbours of the actual tile on the actual planet with the actual mod
    // set, so the visitors are always locally true.
    //
    // 🔴 ARRIVALS ARE NEVER HOSTILE (§3 law 2). They come in already part
    // converted — placid, slow, and filed. Nothing here sets manhunter, makes
    // a faction, or creates a Lord.
    // ════════════════════════════════════════════════════════════════════
    public class MapComponent_SlimeVisitors : MapComponent
    {
        // [INVENTED] Roughly one arrival every day and a half on a slime map.
        private const int CheckIntervalTicks = 2000;
        private const float ArrivalChancePerCheck = 0.03f;

        // Cap so a long game does not fill the map with wandering fauna.
        private const int MaxVisitorsOnMap = 14;

        // [INVENTED] Arrivals turn up already part-read: they walked here.
        private static readonly FloatRange ArrivalSeverity = new FloatRange(0.25f, 0.7f);

        private bool isSlimeMap;
        private List<PawnKindDef> neighbourKinds;

        public MapComponent_SlimeVisitors(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isSlimeMap = SlimeDefs.GelatinousSlime != null && map.Biome == SlimeDefs.GelatinousSlime;
            neighbourKinds = null;
        }

        public override void MapComponentTick()
        {
            if (!isSlimeMap)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckIntervalTicks != 0)
            {
                return;
            }
            if (!Rand.Chance(ArrivalChancePerCheck))
            {
                return;
            }

            try
            {
                if (neighbourKinds == null)
                {
                    neighbourKinds = BuildNeighbourRoster();
                }
                if (neighbourKinds.Count == 0)
                {
                    return;
                }
                if (CountVisitors() >= MaxVisitorsOnMap)
                {
                    return;
                }

                IntVec3 entry;
                if (!RCellFinder.TryFindRandomPawnEntryCell(out entry, map, CellFinder.EdgeRoadChance_Ignore))
                {
                    return;
                }

                PawnKindDef kind = neighbourKinds.RandomElement();
                Pawn pawn = PawnGenerator.GeneratePawn(kind, null);
                GenSpawn.Spawn(pawn, entry, map, Rot4.Random);

                // Pre-staged, per spike C — and only if the creature can be
                // read at all. A resistant arrival simply arrives.
                if (SlimeDefs.Slimification != null && !SlimeUtility.IsResistant(pawn))
                {
                    Hediff h = pawn.health.AddHediff(SlimeDefs.Slimification);
                    if (h != null)
                    {
                        h.Severity = ArrivalSeverity.RandomInRange;
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.GelatinousSlime] visitor arrival: " + e.Message, 0x51A14);
            }
        }

        private int CountVisitors()
        {
            int n = 0;
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                if (pawns[i].IsAnimal && pawns[i].Faction == null)
                {
                    n++;
                }
            }
            return n;
        }

        // Every wild animal of every biome on every tile adjacent to this one,
        // deduplicated. No defName is named anywhere in this method — that is
        // the point of the spike.
        private List<PawnKindDef> BuildNeighbourRoster()
        {
            List<PawnKindDef> result = new List<PawnKindDef>();
            HashSet<PawnKindDef> seen = new HashSet<PawnKindDef>();

            PlanetTile tile = map.Tile;
            if (!tile.Valid)
            {
                return result;
            }

            List<PlanetTile> neighbours = new List<PlanetTile>();
            Find.WorldGrid.GetTileNeighbors(tile, neighbours);

            for (int i = 0; i < neighbours.Count; i++)
            {
                Tile t = Find.WorldGrid[neighbours[i]];
                if (t == null)
                {
                    continue;
                }
                BiomeDef biome = t.PrimaryBiome;
                if (biome == null || biome == SlimeDefs.GelatinousSlime)
                {
                    continue;
                }
                foreach (PawnKindDef kind in biome.AllWildAnimals)
                {
                    if (kind == null || kind.race == null)
                    {
                        continue;
                    }
                    // Predators wander in like anything else, but a slimified
                    // predator does not hunt (§3 law 2 is enforced by the
                    // hediff comp, not by excluding them here). What IS
                    // excluded is anything that would arrive already hostile
                    // before the hediff can settle on it.
                    if (kind.RaceProps != null && kind.RaceProps.manhunterOnDamageChance >= 1f)
                    {
                        continue;
                    }
                    if (seen.Add(kind))
                    {
                        result.Add(kind);
                    }
                }
            }
            return result;
        }
    }
}
