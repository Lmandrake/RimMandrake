using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.EnvironmentalHazards;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TheForge
{
    // FORGE_WHITE_PLUME_FRONTS_1. Quench steam rolls off newly crusted cells as moving fronts.
    //   obscure : vanilla GasType.BlindSmoke (ShotReport and AttackTargetFinder already read it: no Harmony there)
    //   soak    : vanilla Filth_Water puddles (allowsFire=false, evaporate in 0.2~0.4 days)
    //   heat    : +offset on Thing.AmbientTemperature for flesh pawns inside a front, so vanilla HediffGiver_Heat does
    //             the heatstroke (one kind of heat: no new hediff, no direct severity write)
    //   exempt  : pawns carrying RM_CompVaporDrifter (groundHazardImmune) live in the steam
    // Design record: Transient/work_PLUME_20261003.md.
    public class PlumeFront : IExposable
    {
        public Vector2 pos;
        public Vector2 dir;      // unit vector
        public int ticksLeft;

        public void ExposeData()
        {
            Scribe_Values.Look(ref pos, "pos");
            Scribe_Values.Look(ref dir, "dir");
            Scribe_Values.Look(ref ticksLeft, "ticksLeft");
        }
    }

    public class RM_MapComponent_PlumeFronts : MapComponent
    {
        public const int StepTicks = RM_PlumeKernel.StepTicks;
        public const int MaxFronts = RM_PlumeKernel.MaxFronts;
        public const float SpawnChancePerCrust = 0.006f;
        public const float Radius = 3f;
        public const float CellsPerStep = RM_PlumeKernel.CellsPerStep;      // ~1 cell per 20 ticks
        public const int LifeTicks = RM_PlumeKernel.LifeTicks;
        public const int ExpiryTicks = RM_PlumeKernel.ExpiryTicks;
        public const float BaseGas = RM_PlumeKernel.BaseGas;             // BlindSmoke density added per cell per step at strength 1
        public const float BaseHeatOffset = RM_PlumeKernel.BaseHeatOffset;      // degrees C at strength 1
        public const float SoakChance = 0.12f;

        // Last tick any map had a live front: lets the Harmony postfix bail out without touching a map.
        public static int LastActiveTick = -999999;

        private List<PlumeFront> fronts = new List<PlumeFront>();
        private bool announced;
        private float bearing = -1f;
        private readonly RM_PlumeBook cellExpiry = new RM_PlumeBook();

        public int StatFrontsSpawned;
        public int StatSoakPuddles;

        private static ThingDef filthWater;

        public RM_MapComponent_PlumeFronts(Map map) : base(map) { }

        public int LiveFronts => fronts.Count;

        public static RM_MapComponent_PlumeFronts Of(Map map)
        {
            return map == null ? null : map.GetComponent<RM_MapComponent_PlumeFronts>();
        }

        // 1.6 has no wind direction: one fixed, seeded bearing per map (same choice as the Scarlands settling).
        private float Bearing
        {
            get
            {
                if (bearing < 0f)
                {
                    bearing = Rand.ValueSeeded(map.Tile * 7 + 51) * Mathf.PI * 2f;
                }
                return bearing;
            }
        }

        public static bool CellInPlume(Map map, IntVec3 c, int now)
        {
            RM_MapComponent_PlumeFronts comp = Of(map);
            if (comp == null || comp.fronts.Count == 0)
            {
                return false;
            }
            return comp.cellExpiry.InPlume(comp.fronts.Count, map.cellIndices.CellToIndex(c), now);
        }

        // Called by the cycle's FreezeBatch for every cell it crusts over.
        public void NoteCrusted(IntVec3 c)
        {
            if (!RM_PlumeKernel.CanSpawn(RM_TheForgeSettings.Active(RM_TheForgeSettings.plumeFrontsEnabled), fronts.Count)
                || !Rand.Chance(SpawnChancePerCrust))
            {
                return;
            }
            float ang = Bearing + Rand.Range(-0.4f, 0.4f);
            fronts.Add(new PlumeFront
            {
                pos = new Vector2(c.x + 0.5f, c.z + 0.5f),
                dir = new Vector2(Mathf.Cos(ang), Mathf.Sin(ang)),
                ticksLeft = LifeTicks
            });
            StatFrontsSpawned++;
            if (!announced)
            {
                announced = true;
                Messages.Message("White plumes are rolling off the new crust. They blind shooters, soak the ground and the heat inside them is hard to bear.",
                    new TargetInfo(c, map), MessageTypeDefOf.NeutralEvent);
            }
        }

        // Quicktest surface (RM_ForgeCycleDebugActions): a front at `c` now, ignoring chance and cap.
        public void DebugSpawn(IntVec3 c)
        {
            fronts.Add(new PlumeFront
            {
                pos = new Vector2(c.x + 0.5f, c.z + 0.5f),
                dir = new Vector2(Mathf.Cos(Bearing), Mathf.Sin(Bearing)),
                ticksLeft = LifeTicks
            });
            StatFrontsSpawned++;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (fronts.Count == 0)
            {
                if (cellExpiry.Expiry.Count > 0)
                {
                    cellExpiry.ClearAll();
                }
                announced = announced && RM_ForgeCycleUtility.CycleOn(map) != null && RM_ForgeCycleUtility.CycleOn(map).Phase == ForgeCyclePhase.Freeze;
                return;
            }
            int now = Find.TickManager.TicksGame;
            LastActiveTick = now;
            if (!map.IsHashIntervalTick(StepTicks))
            {
                return;
            }
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.plumeFrontsEnabled))
            {
                fronts.Clear();
                cellExpiry.ClearAll();
                return;
            }
            bool obscure = RM_TheForgeSettings.plumeObscureEnabled;
            bool soak = RM_TheForgeSettings.plumeSoakEnabled;
            for (int i = fronts.Count - 1; i >= 0; i--)
            {
                PlumeFront f = fronts[i];
                float px = f.pos.x, pz = f.pos.y;
                bool alive = RM_PlumeKernel.Step(ref px, ref pz, f.dir.x, f.dir.y, ref f.ticksLeft, map.Size.x, map.Size.z);
                f.pos = new Vector2(px, pz);
                IntVec3 center = new IntVec3(Mathf.FloorToInt(f.pos.x), 0, Mathf.FloorToInt(f.pos.y));
                if (!alive)
                {
                    fronts.RemoveAt(i);
                    continue;
                }
                foreach (IntVec3 c in GenRadial.RadialCellsAround(center, Radius, true))
                {
                    if (!c.InBounds(map))
                    {
                        continue;
                    }
                    cellExpiry.Mark(map.cellIndices.CellToIndex(c), now);
                    if (c.Filled(map))
                    {
                        continue;
                    }
                    if (obscure)
                    {
                        map.gasGrid.AddGas(c, GasType.BlindSmoke, RM_PlumeKernel.GasPerCell(RM_TheForgeSettings.plumeStrength));
                    }
                    if (soak && Rand.Chance(SoakChance) && c.Walkable(map))
                    {
                        if (filthWater == null)
                        {
                            filthWater = DefDatabase<ThingDef>.GetNamedSilentFail("Filth_Water");
                        }
                        if (filthWater != null && FilthMaker.TryMakeFilth(c, map, filthWater, 1))
                        {
                            StatSoakPuddles++;
                        }
                    }
                }
                for (int k = 0; k < 3; k++)
                {
                    Vector3 v = new Vector3(f.pos.x + Rand.Range(-Radius, Radius) * 0.7f, 0f, f.pos.y + Rand.Range(-Radius, Radius) * 0.7f);
                    if (v.ToIntVec3().InBounds(map))
                    {
                        FleckMaker.ThrowDustPuffThick(v, map, Rand.Range(2.2f, 3.4f), new Color(0.96f, 0.96f, 0.98f, 0.8f));
                    }
                }
            }
            cellExpiry.Prune(now);
        }

        public string DebugReport()
        {
            return "plumeLive=" + fronts.Count + " plumeSpawned=" + StatFrontsSpawned + " plumePuddles=" + StatSoakPuddles
                + " plumeCells=" + cellExpiry.Expiry.Count;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref fronts, "plumeFronts", LookMode.Deep);
            Scribe_Values.Look(ref announced, "plumeAnnounced", false);
            Scribe_Values.Look(ref bearing, "plumeBearing", -1f);
            Scribe_Values.Look(ref StatFrontsSpawned, "plumeStatSpawned", 0);
            Scribe_Values.Look(ref StatSoakPuddles, "plumeStatPuddles", 0);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && fronts == null)
            {
                fronts = new List<PlumeFront>();
            }
        }
    }

    public static class RM_PlumeUtility
    {
        // Vapour-adapted: carries the vapour-drifter comp (or is not flesh, so it has no heatstroke to speak of).
        public static bool IsExempt(Pawn p)
        {
            RM_CompVaporDrifter d = p.RaceProps != null && p.RaceProps.IsFlesh ? p.TryGetComp<RM_CompVaporDrifter>() : null;
            return RM_PlumeKernel.Exempt(p.RaceProps != null && p.RaceProps.IsFlesh, RM_TheForgeSettings.plumeAdaptedExempt,
                d != null && d.Props.groundHazardImmune);
        }

        public static float HeatOffset()
        {
            return RM_PlumeKernel.HeatOffset(RM_TheForgeSettings.plumeStrength);
        }
    }

    // The heat half: vanilla HediffGiver_Heat reads pawn.AmbientTemperature, so a front is just hotter air.
    [HarmonyPatch(typeof(Thing), nameof(Thing.AmbientTemperature), MethodType.Getter)]
    public static class RM_Patch_Plume_AmbientTemperature
    {
        public static void Postfix(Thing __instance, ref float __result)
        {
            if (Find.TickManager == null)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (!RM_PlumeKernel.RecentlyActive(now, RM_MapComponent_PlumeFronts.LastActiveTick))
            {
                return;
            }
            Pawn p = __instance as Pawn;
            if (p == null || !p.Spawned || !RM_TheForgeSettings.Active(RM_TheForgeSettings.plumeHeatEnabled))
            {
                return;
            }
            if (RM_MapComponent_PlumeFronts.CellInPlume(p.Map, p.Position, now) && !RM_PlumeUtility.IsExempt(p))
            {
                __result += RM_PlumeUtility.HeatOffset();
            }
        }
    }
}
