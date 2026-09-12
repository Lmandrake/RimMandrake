using RimWorld;
using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
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
    /// so RM_FE_Ground_*'s burnedDef ash ladder does the converting and this file
    /// hard-codes no terrain defName.
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

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);

            if (!PyrelandsMechanicsSettings.furnaceBedIgnitionEnabled)
            {
                return;
            }
            if (!(parent is Pawn beast) || !beast.Spawned || beast.Dead)
            {
                return;
            }

            if (!beast.Awake())
            {
                restingTicks += delta;
                return;
            }

            if (restingTicks <= 0)
            {
                return;
            }

            int slept = restingTicks;
            restingTicks = 0;

            if (slept < PyrelandsTuning.FurnaceMinRestTicks)
            {
                return;
            }
            if (!Rand.Chance(PyrelandsMechanicsSettings.furnaceBedIgnitionChance))
            {
                return;
            }

            SmoulderBedGround(beast);
        }

        private static void SmoulderBedGround(Pawn beast)
        {
            Map map = beast.Map;
            if (map == null)
            {
                return;
            }

            int cells = Rand.RangeInclusive(
                PyrelandsTuning.FurnaceBedIgnitionMinCells,
                PyrelandsTuning.FurnaceBedIgnitionMaxCells);

            for (int i = 0; i < cells; i++)
            {
                // i == 0 is the cell it actually slept on; any extra is adjacent.
                IntVec3 cell = i == 0
                    ? beast.Position
                    : beast.Position + GenAdj.AdjacentCells[Rand.Range(0, GenAdj.AdjacentCells.Length)];

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
