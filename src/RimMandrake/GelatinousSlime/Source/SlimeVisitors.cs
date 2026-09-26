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
        // Shared with GenStep_SlimeVisitorSeed below — one cap, one place.
        internal const int MaxVisitorsOnMap = 14;

        // [INVENTED] Arrivals turn up already part-read: they walked here.
        // internal, not private: GenStep_SlimeVisitorSeed reuses the same
        // number for the map-generation seed pass (owner ruling 2026-09-24).
        internal static readonly FloatRange ArrivalSeverity = new FloatRange(0.25f, 0.7f);

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
            return CountVisitors(map);
        }

        internal static int CountVisitors(Map map)
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
            return BuildNeighbourRoster(map);
        }

        // internal static: shared with GenStep_SlimeVisitorSeed's one-time
        // map-generation seed pass below — same neighbour-tile read, same
        // never-hostile filter, so a freshly generated Slime map opens
        // already showing the "everything that ever touched it" cast instead
        // of gelatids-only for the first days (owner ruling 2026-09-24).
        internal static List<PawnKindDef> BuildNeighbourRoster(Map map)
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

    // ════════════════════════════════════════════════════════════════════
    // THE VISITOR SEED PASS (§10, owner ruling 2026-09-24: "Yes, I think
    // that's a good idea" to BENCH's offer).
    //
    // A freshly generated Slime map opened with only RM_Gelatid on it for
    // the first days — technically correct per spike C (arrivals are meant
    // to accumulate over time) but a flat start for a biome whose whole
    // fiction is "everything that ever touched it is in circulation". This
    // seeds 3-5 of those same never-hostile, part-read arrivals ONCE, at
    // generation.
    //
    // A GenStep, not a FinalizeInit flag: GenStep.Generate only runs during
    // MapGenerator.GenerateMap for a brand-new map, never on load of an
    // existing one — so "once per map, never on load" is true by
    // construction, no Scribed bookkeeping needed. Registered onto the
    // shared MapCommonBase generator (Patches/RM_SlimeVisitorSeed_MapGenPatch.xml),
    // the same self-gating shape RM_GenStep_LiquidShores/
    // RUT_FungalSoilScatter already use: safe to add globally because
    // Generate() below no-ops on every non-Slime map.
    // ════════════════════════════════════════════════════════════════════
    public class GenStep_SlimeVisitorSeed : GenStep
    {
        // [INVENTED] distinct from every vanilla/other RimMandrake step so
        // MapGenerator.GetSeedPart's de-duplication does not fold this in
        // with an unrelated neighbour.
        public override int SeedPart => 0x51A20;

        public override void Generate(Map map, GenStepParams parms)
        {
            try
            {
                if (SlimeDefs.GelatinousSlime == null || map.Biome != SlimeDefs.GelatinousSlime)
                {
                    return;
                }

                List<PawnKindDef> neighbourKinds =
                    MapComponent_SlimeVisitors.BuildNeighbourRoster(map);
                if (neighbourKinds.Count == 0)
                {
                    return;
                }

                int cap = MapComponent_SlimeVisitors.MaxVisitorsOnMap
                    - MapComponent_SlimeVisitors.CountVisitors(map);
                if (cap <= 0)
                {
                    return;
                }

                int want = Rand.RangeInclusive(3, 5);
                int n = Math.Min(want, cap);
                for (int i = 0; i < n; i++)
                {
                    IntVec3 cell = CellFinderLoose.RandomCellWith(
                        c => c.Standable(map) && !c.Fogged(map), map, 200);
                    if (!cell.IsValid)
                    {
                        continue;
                    }

                    PawnKindDef kind = neighbourKinds.RandomElement();
                    Pawn pawn = PawnGenerator.GeneratePawn(kind, null);
                    GenSpawn.Spawn(pawn, cell, map, Rot4.Random);

                    // Arrive already part-read, same as the ambient spawner
                    // (§3 law 2: never hostile — pre-staged, not converted
                    // on arrival).
                    if (SlimeDefs.Slimification != null && !SlimeUtility.IsResistant(pawn))
                    {
                        Hediff h = pawn.health.AddHediff(SlimeDefs.Slimification);
                        if (h != null)
                        {
                            h.Severity = MapComponent_SlimeVisitors.ArrivalSeverity.RandomInRange;
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce(
                    "[RimMandrake.GelatinousSlime] visitor seed pass: " + e.Message, 0x51A21);
            }
        }
    }
}
