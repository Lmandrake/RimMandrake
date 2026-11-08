using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 4b — bed-down ignition
    /// (RUT_ruled_commissions_wave2.md §8c; the_pyrelands.md §4: "at the
    /// discharged end of the circuit their bed-down grounds smolder alight").
    ///
    /// 🔴 NO TAMED EXEMPTION. Owner, verbatim, 2026-09-10: "Make them both
    /// tameable... and that's insane. Fires all the time! I love it." A ranched
    /// furnace-beast smoulders its barn floor exactly as a wild one smoulders the
    /// grass — that hazard IS the reversed ban 5's counterweight (§8d), and it is
    /// the reason the furnace-hide's price is set at ranch supply rather than hunt
    /// scarcity (§12). Do not add a Faction check to this file.
    ///
    /// THE TRIGGER, VERIFIED RATHER THAN GUESSED (§8c asks for exactly that).
    /// There is no "rest cycle completed" event in the engine. What there IS is
    /// RestUtility.Awake(Pawn) — read at source, RimWorld/RestUtility.cs:459 —
    /// which returns false while the pawn's current job driver reports asleep.
    /// So the cycle is measured here: accumulate ticks while not awake, and fire
    /// the roll on the transition back to awake, provided the sleep was a real
    /// one (FurnaceMinRestTicks). That also means a beast downed for an hour and
    /// then back on its feet smoulders the ground it lay on, which is correct for
    /// a creature whose hide is the heat store.
    ///
    /// Smoulder, not blaze (§8c): one or two cells at Fire.MinFireSize, and the
    /// ground is handed to the FireEcology scorched register through vanilla's own
    /// TerrainGrid.Notify_TerrainBurned — the same call Fire.TryBurnFloor makes —
    /// so RM_FE_Ground_*'s burnedDef (deep ash) does the converting and this file
    /// hard-codes no terrain defName.
    ///
    /// ASLEEP IN GRASS (owner card 2026-11-08 01:01, "it ignites grass it sleeps
    /// in"). While the beast sleeps on a cell holding a plant that can burn now,
    /// past a half-hour grace it rolls every 250 ticks at an MTB of 1.5 h (so about
    /// two hours of sleep on average, never at once) and sets that plant alight at
    /// the fire-front's size. A bare floor never rolls. The beast itself cannot
    /// burn (flammability 0, heat damage absorbed by Patch_FurnaceBeastHeatImmunity).
    /// Same switch, same no-tamed-exemption rule as the wake roll.
    /// </summary>
    public class CompProperties_FurnaceBedIgnition : CompProperties
    {
        public CompProperties_FurnaceBedIgnition()
        {
            compClass = typeof(CompFurnaceBedIgnition);
        }
    }

    public class CompFurnaceBedIgnition : ThingComp
    {
        private int restingTicks;

        // ProbeSleep only, not saved: how long the beast had slept when its sleep last set the grass alight (-1 never),
        // so the row tells this roll from the wake roll's smoulder.
        private int sleepLitAfterTicks = -1;

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);

            if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.furnaceThermalEnabled)
            {
                return;
            }
            if (!(parent is Pawn beast) || !beast.Spawned || beast.Dead)
            {
                return;
            }

            RM_RestOutcome rest = RM_FurnaceKernel.RestStep(ref restingTicks, beast.Awake(), delta, PyrelandsTuning.FurnaceMinRestTicks);
            if (rest == RM_RestOutcome.Resting)
            {
                if (parent.IsHashIntervalTick(PyrelandsTuning.FurnaceSleepIgnitionCheckTicks, delta))
                {
                    IgniteGrassSleptIn(beast);
                }
                return;
            }
            if (rest != RM_RestOutcome.WokeRested)
            {
                return;
            }
            if (!Rand.Chance(PyrelandsTuning.FurnaceBedIgnitionChance))
            {
                return;
            }

            SmoulderBedGround(beast);
        }

        private void IgniteGrassSleptIn(Pawn beast)
        {
            Map map = beast.Map;
            IntVec3 cell = beast.Position;
            Plant plant = cell.GetPlant(map);
            if (!RM_FurnaceKernel.SleepIgnitionDue(false, restingTicks, plant != null && plant.FlammableNow,
                    PyrelandsTuning.FurnaceSleepIgnitionGraceTicks))
            {
                return;
            }
            if (!Rand.MTBEventOccurs(PyrelandsTuning.FurnaceSleepIgnitionMtbTicks, 1f, PyrelandsTuning.FurnaceSleepIgnitionCheckTicks))
            {
                return;
            }
            if (FireUtility.TryStartFireIn(cell, map, PyrelandsTuning.FurnaceSleepIgnitionFireSize, beast))
            {
                map.terrainGrid.Notify_TerrainBurned(cell);
                sleepLitAfterTicks = restingTicks;
            }
        }

        /// <summary>Script probe (jawa/static_call, Pawn by ThingID): "spawned=;awake=;job=;restingTicks=;cell=x,z;plant=;
        /// flammablePlant=;fireOnCell=;rest=;litAfterTicks=" for the sleep-ignition row (pyre_furnacebeast_sleep_ignites).</summary>
        public static string ProbeSleep(Pawn pawn)
        {
            if (pawn == null || !pawn.Spawned)
            {
                return "spawned=false";
            }
            Map map = pawn.Map;
            IntVec3 c = pawn.Position;
            Plant plant = c.GetPlant(map);
            CompFurnaceBedIgnition comp = pawn.TryGetComp<CompFurnaceBedIgnition>();
            return "spawned=true"
                 + ";awake=" + pawn.Awake()
                 + ";job=" + (pawn.CurJobDef?.defName ?? "none")
                 + ";restingTicks=" + (comp?.restingTicks ?? -1)
                 + ";cell=" + c.x + "," + c.z
                 + ";plant=" + (plant?.def.defName ?? "none")
                 + ";flammablePlant=" + (plant != null && plant.FlammableNow)
                 + ";fireOnCell=" + (c.GetFirstThing<Fire>(map) != null)
                 + ";rest=" + (pawn.needs?.rest?.CurLevel.ToString("0.00") ?? "none")
                 + ";litAfterTicks=" + (comp?.sleepLitAfterTicks ?? -1);
        }

        private static void SmoulderBedGround(Pawn beast)
        {
            Map map = beast.Map;
            if (map == null)
            {
                return;
            }

            // PYRELANDS_ULLAI_GIANT_BUILD_1: a bigger beast lies on more ground (classic ratio 1 = 1..2 cells).
            float ratio = PyrelandsTuning.FurnaceSizeRatio(beast);
            RM_FurnaceKernel.BedCells(ratio, PyrelandsTuning.FurnaceBedIgnitionMinCells, PyrelandsTuning.FurnaceBedIgnitionMaxCells,
                out int lo, out int hi, out float spread);
            int cells = Rand.RangeInclusive(lo, hi);

            for (int i = 0; i < cells; i++)
            {
                // i == 0 is the cell it actually slept on; any extra is adjacent.
                IntVec3 cell = i == 0
                    ? beast.Position
                    : beast.Position + GenRadial.RadialPattern[Rand.Range(1, GenRadial.NumCellsInRadius(spread))];

                if (!cell.InBounds(map))
                {
                    continue;
                }

                // instigator: the beast. A TAMED beast therefore charges the
                // colony's own arson debt in MapComponent_BurnLine — the ranch's
                // operating cost, made mechanical (§8d).
                if (FireUtility.TryStartFireIn(cell, map, PyrelandsTuning.SmoulderFireSize, beast))
                {
                    map.terrainGrid.Notify_TerrainBurned(cell);
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref restingTicks, "restingTicks", 0);
        }
    }
}
