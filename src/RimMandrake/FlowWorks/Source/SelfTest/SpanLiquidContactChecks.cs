// The generated members run the production span and coating logic. Map cells, excavation fill, pawn health,
// and game ticks are engine doubles. The tests drive a walked entry and a band sweep explicitly.
using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.SelfTest.SpanLiquidContact
{
    internal static class SpanLiquidContactChecks
    {
        private static void Assert(bool ok, string message)
        {
            if (!ok) throw new Exception(message);
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Underpass_rising_water_keeps_pawn_below_deck", () =>
            {
                var map = new Map();
                IntVec3 canal = new IntVec3(1, 0);
                map.excavation.SetHollow(default, 4);
                map.excavation.SetHollow(canal, 4);
                var deck = new Building_SuspensionDeck { Map = map, Position = canal };
                canal.GetThingList(map).Add(deck);
                var walker = new Pawn { Map = map, Position = canal };
                var rider = new Pawn { Map = map, Position = canal };
                canal.GetThingList(map).AddRange(new Thing[] { walker, rider });
                RM_SuspensionUnderpass.Entered(walker, default, canal);
                RM_SuspensionUnderpass.Entered(rider, new IntVec3(2, 0), canal);

                void Check(string phase)
                {
                    var standing = new List<Pawn>();
                    bool below = RM_SuspensionUnderpass.InFloorBand(walker);
                    float load = RM_SpanUtility.LoadOn(map, new List<IntVec3> { canal }, null, true, standing);
                    Assert(below && load == rider.Mass && standing.Count == 1 && standing[0] == rider,
                        phase + ": walker below=" + below + ", deck load=" + load + " kg (expected only the 70 kg rider)");
                }

                Check("Dry canal");
                map.excavation.Fill(canal, RimMandrakeFlowWorks_DefOf.RM_Fluid_Water, 3);
                Assert(map.excavation.ClimbDepthAt(canal) == 1, "1.5 m of water raises the climb surface to one notch");
                Check("At 1.5 m of water");
                map.bridges.Sweep();
                Check("After band sweep");
                map.excavation.Fill(canal, null, 0);
                Check("After draining");
            });

            Case("Coating_dry_solid_cover_over_oil_keeps_pawn_clean", () =>
            {
                var (map, pawn) = CoveredPit();
                map.excavation.Fill(pawn.Position, Oil, 1);
                Tick(map);
                pawn.Position = default;
                Tick(map);
                Assert(CoatOf(pawn) == null, "Leaving a dry solid cover applied " + CoatOf(pawn));
            });

            Case("Coating_dry_solid_cover_over_water_preserves_coat", () =>
            {
                var (map, pawn) = CoveredPit();
                IntVec3 cover = pawn.Position;
                IntVec3 oil = new IntVec3(2, 0);
                IntVec3 water = new IntVec3(3, 0);
                map.excavation.SetHollow(oil, 4);
                map.excavation.SetHollow(water, 4);
                map.excavation.Fill(oil, Oil, 1);
                map.excavation.Fill(water, RimMandrakeFlowWorks_DefOf.RM_Fluid_Water, 1);
                map.excavation.Fill(cover, RimMandrakeFlowWorks_DefOf.RM_Fluid_Water, 1);

                pawn.Position = oil;
                Tick(map);
                pawn.Position = default;
                Tick(map);
                Assert(CoatOf(pawn) == "coated in oil", "Leaving uncovered oil should apply its named coat");
                pawn.Position = cover;
                Tick(map);
                Assert(CoatOf(pawn) == "coated in oil", "Standing on a dry solid cover washed off oil");
                pawn.Position = water;
                Tick(map);
                Assert(CoatOf(pawn) == null, "Wading in uncovered water should wash off oil");
            });

            Case("Coating_stepping_onto_dry_cover_applies_previous_exposure", () =>
            {
                var (map, pawn) = CoveredPit();
                IntVec3 cover = pawn.Position;
                map.excavation.Fill(cover, Oil, 1);
                pawn.Position = new IntVec3(2, 0);
                map.excavation.SetHollow(pawn.Position, 4);
                map.excavation.Fill(pawn.Position, Oil, 1);
                Tick(map);
                pawn.Position = cover;
                Tick(map);
                Assert(CoatOf(pawn) == "coated in oil", "Stepping from oil onto a dry cover should apply the pending coat");
            });

            Case("Coating_dry_ground_skips_deck_lookup", () =>
            {
                Current.Game = new Game();
                var map = new Map();
                for (int x = 0; x < 12; x++)
                {
                    map.mapPawns.AllPawnsSpawned.Add(new Pawn { Map = map, Position = new IntVec3(x, 0) });
                }
                Tick(map);
                Assert(map.ThingGridReads == 0, $"Dry ground caused {map.ThingGridReads} deck lookups for 12 pawns");
            });
        }

        private static readonly FluidDef Oil = new FluidDef { label = "oil", coats = true };

        private static (Map, Pawn) CoveredPit()
        {
            Current.Game = new Game();
            var map = new Map();
            IntVec3 cell = new IntVec3(1, 0);
            map.excavation.SetHollow(cell, 4);
            cell.GetThingList(map).Add(new Building_SpanDeck { Map = map, Position = cell });
            var pawn = new Pawn { Map = map, Position = cell };
            map.mapPawns.AllPawnsSpawned.Add(pawn);
            return (map, pawn);
        }

        private static string CoatOf(Pawn p) => p.health.hediffSet.GetFirstHediffOfDef(RM_LiquidCoating.CoatDef)?.LabelBase;

        private static void Tick(Map map)
        {
            Find.TickManager.TicksGame += RM_LiquidCoating.IntervalTicks;
            RM_LiquidCoating.Tick(map, map.excavation);
        }
    }

    internal record struct IntVec3(int x, int z)
    {
        public IntVec3(int x, int y, int z) : this(x, z) { }
        public static IntVec3 Invalid => new IntVec3(-1, -1);
        public bool IsValid => x >= 0 && z >= 0;
        public bool InBounds(Map map) => IsValid;
        public List<Thing> GetThingList(Map map) => map.ThingsAt(this);
    }

    internal sealed class Map
    {
        private readonly Dictionary<IntVec3, List<Thing>> things = new();
        public readonly RM_MapComponent_SuspensionBridges bridges;
        public readonly RM_MapComponent_Excavation excavation = new();
        public readonly MapPawns mapPawns = new();
        public readonly TerrainGrid terrainGrid = new();
        public int ThingGridReads { get; private set; }

        public Map() => bridges = new RM_MapComponent_SuspensionBridges(this);
        public T GetComponent<T>() where T : class => bridges as T ?? excavation as T;

        public List<Thing> ThingsAt(IntVec3 cell)
        {
            ThingGridReads++;
            if (!things.TryGetValue(cell, out var list)) things[cell] = list = new List<Thing>();
            return list;
        }
    }

    internal sealed class MapPawns
    {
        public readonly List<Pawn> AllPawnsSpawned = new();
    }

    internal class Thing
    {
        public Map Map;
        public IntVec3 Position;
        public bool Spawned => Map != null;
    }

    internal sealed class Pawn : Thing
    {
        public bool Dead => false;
        public bool Flying => false;
        public Thing Corpse => null;
        public Faction Faction => null;
        public float Mass => 70f;
        public float GetStatValue(object stat) => Mass;
        public int thingIDNumber => 1;
        public string ThingID => "Pawn1";
        public Vector3 DrawPos => default;
        public readonly PawnHealth health = new();
    }

    internal sealed class Faction { }
    internal static class StatDefOf
    {
        public static readonly object Mass = new();
    }

    internal class Building_SpanDeck : Thing
    {
        public virtual bool FloorBandPassesUnder => false;
        public bool Decked => Spawned;
        public bool Grated => false;
        public int DeckNotches => 0;
    }

    internal partial class Building_SuspensionDeck { }

    internal partial class RM_MapComponent_SuspensionBridges
    {
        private readonly Map map;
        private readonly HashSet<Pawn> floorBand = new();
        public static int BandTotal { get; private set; }

        public RM_MapComponent_SuspensionBridges(Map map) => this.map = map;
        public static RM_MapComponent_SuspensionBridges Of(Map map) => map?.bridges;
        public bool InBandSet(Pawn p) => floorBand.Contains(p);
        public void SetBand(Pawn p, bool under)
        {
            if (under && floorBand.Add(p)) BandTotal++;
            if (!under && floorBand.Remove(p)) BandTotal--;
        }
        public void Sweep() => SweepUnder();
    }

    internal static partial class RM_SuspensionUnderpass
    {
        public static void SlideOut(Thing thing) { }
    }

    internal static partial class RM_SpanUtility
    {
        public static bool DeckedAt(Map map, IntVec3 cell) => DeckAt(map, cell) != null;
        public static int WalkingDepth(Map map, IntVec3 cell, int hollow) => DeckAt(map, cell)?.DeckNotches ?? hollow;
        private static float CarriedKg(Pawn p) => 0f;
    }

    internal sealed class RM_MapComponent_Excavation
    {
        private readonly Dictionary<IntVec3, int> hollows = new();
        private readonly Dictionary<IntVec3, (FluidDef fluid, int notches)> fill = new();
        public void SetHollow(IntVec3 c, int notches) => hollows[c] = notches;
        public void Fill(IntVec3 c, FluidDef fluid, int notches) => fill[c] = (fluid, notches);
        public int HollowDepthAt(IntVec3 c) => hollows.GetValueOrDefault(c);
        public int ClimbDepthAt(IntVec3 c)
        {
            int hollow = HollowDepthAt(c);
            int code = RM_SwimMath.DugSwimCode(true, hollow, fill.GetValueOrDefault(c).notches * RM_LevelSolve.U);
            return RM_SwimMath.ClimbDepthWithSwim(hollow, code < 0 ? -1 : code / 2);
        }
        public bool IsExcavated(IntVec3 c) => HollowDepthAt(c) > 0;
        public bool WetAt(IntVec3 c) => fill.GetValueOrDefault(c).notches > 0;
        public FluidDef FluidAt(IntVec3 c) => fill.GetValueOrDefault(c).fluid;
        public FluidDef ActiveFluid => RimMandrakeFlowWorks_DefOf.RM_Fluid_Water;
        public RM_MapComponent_Excavation SuperdeepTrap => this;
        public void NoteHandledArrival(Pawn p, IntVec3 to) { }
    }

    internal static class RM_SuperdeepTrap
    {
        public static RM_MapComponent_Excavation EngineOf(Map map) => map?.excavation;
    }

    internal static class RM_SuspensionSettings
    {
        public static bool suspensionWalkUnder => true;
    }

    internal static class RM_TrenchStride
    {
        public static bool SteppedOver(Pawn p, Map map, RM_MapComponent_Excavation ex, IntVec3 c) => false;
    }

    internal static class RM_PocketGrid
    {
        public static int ClimbLimitOf(Pawn p) => 2;
        public static int NaturalClimbLimitOf(Pawn p) => ClimbLimitOf(p);
    }

    internal static class RM_PitCoverBeneath
    {
        public static bool IsBeneath(Pawn p) => false;
    }

    internal sealed class TerrainDef
    {
        public bool IsWater => false;
    }

    internal sealed class TerrainGrid
    {
        private readonly TerrainDef ground = new();
        public TerrainDef TerrainAt(IntVec3 c) => ground;
    }

    internal sealed class FluidDef
    {
        public string label;
        public string defName => label;
        public bool coats, washesCoat;
        public TerrainDef floodTerrain => null;
        public TerrainDef fillTerrainVeryShallow => null;
        public TerrainDef fillTerrainHalf => null;
        public TerrainDef fillTerrainBrim => null;
        public TerrainDef fillTerrainSuperdeep => null;
    }

    internal static class RM_FluidIdentity
    {
        public static FluidDef FluidOfTerrain(TerrainDef terrain) => null;
    }

    internal static class RM_SlimeSlip
    {
        public static FluidDef NaturalSlime(Map map, IntVec3 c) => null;
    }

    internal static class RimMandrakeFlowWorks_DefOf
    {
        public static readonly FluidDef RM_Fluid_Water = new FluidDef { label = "water", washesCoat = true };
    }

    internal static class RimMandrakeFlowWorksSettings
    {
        public static bool liquidCoatEnabled => true;
        public static float liquidCoatFadeDays => 1f;
    }

    internal sealed class Game { }
    internal static class Current
    {
        public static Game Game { get; set; }
    }

    internal static class Find
    {
        public static readonly TickCounter TickManager = new();
        public static Map CurrentMap => null;
    }

    internal sealed class TickCounter
    {
        public int TicksGame;
    }

    internal sealed class HediffDef { }
    internal class HediffWithComps
    {
        public int ageTicks;
        public virtual string LabelBase => "";
        public virtual bool ShouldRemove => false;
        public virtual void ExposeData() { }
    }

    internal static class HediffMaker
    {
        public static HediffWithComps MakeHediff(HediffDef def, Pawn p) => new Hediff_LiquidCoat();
    }

    internal sealed class PawnHealth
    {
        private HediffWithComps coat;
        public PawnHealth hediffSet => this;
        public HediffWithComps GetFirstHediffOfDef(HediffDef def) => coat;
        public void AddHediff(HediffWithComps hediff) => coat = hediff;
        public void RemoveHediff(HediffWithComps hediff) => coat = null;
    }

    internal static class DefDatabase<T> where T : new()
    {
        public static T GetNamedSilentFail(string name) => new T();
        public static IReadOnlyList<T> AllDefsListForReading => Array.Empty<T>();
    }

    internal record struct Color(float r, float g, float b);
    internal record struct Vector3(float x, float y, float z)
    {
        public static Vector3 operator +(Vector3 a, Vector3 b) => new Vector3(a.x + b.x, a.y + b.y, a.z + b.z);
    }

    internal static class MoteMaker
    {
        public static void ThrowText(Vector3 drawPos, Map map, string text, Color color, float seconds) { }
    }

    internal static class Mathf
    {
        public static int RoundToInt(float value) => (int)Math.Round(value);
    }

    internal static class GenDate
    {
        public const int TicksPerDay = 60000;
    }

    internal static class Scribe_Values
    {
        public static void Look(ref string value, string label) { }
    }
}
