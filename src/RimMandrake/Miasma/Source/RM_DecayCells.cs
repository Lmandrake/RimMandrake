using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Miasma
{
    // MIASMA_DECAY_CELLS_1 part A (design/Jawa/worldbuilding/biomes/miasma_bedazzle_review_2026-10-02.md §4 row 2, §5
    // idea 3; owner card 2026-10-02 + typed ruling). A decay cell is a bed of delta loam, silt and salt that makes
    // power from rotting goods fed to it; output falls as the feed is spent, and a cell that has digested its
    // lifetime of feed becomes a rotting bed (RM_RottingBed). Learned only by analyzing the old meter found in a
    // Miasma compost bed (vanilla ResearchProjectDef.requiredAnalyzed + CompAnalyzableUnlockResearch, the signal
    // chip's route); buildable anywhere after. Corpse disposal is part B (MIASMA_ROTTING_BED_CORPSES_1).

    public class RM_DecayCellExtension : DefModExtension
    {
        /// <summary>Feed units digested over the cell's life before it becomes a rotting bed. // INVENTED</summary>
        public float lifetimeFeed = 600f;
        /// <summary>Output at an almost-empty bed, as a fraction of full. // INVENTED</summary>
        public float minOutputFraction = 0.3f;
        public ThingDef spentDef;
    }

    public class RM_CompPowerPlantDecay : CompPowerPlant
    {
        private float digested;
        private float lastFuel = -1f;

        private RM_DecayCellExtension Ext => parent.def.GetModExtension<RM_DecayCellExtension>() ?? new RM_DecayCellExtension();

        public float Digested => digested;

        protected override float DesiredPowerOutput
        {
            get
            {
                if (!RM_MiasmaSettings.decayCellsEnabled || refuelableComp == null)
                {
                    return 0f;
                }
                float full = -Props.PowerConsumption * RM_MiasmaSettings.decayCellPowerMultiplier;
                float frac = refuelableComp.Props.fuelCapacity > 0f ? refuelableComp.Fuel / refuelableComp.Props.fuelCapacity : 0f;
                return full * DecayCellMath.OutputFraction(frac, Ext.minOutputFraction);
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            if (!parent.IsHashIntervalTick(250) || refuelableComp == null)
            {
                return;
            }
            ObserveFuel();
        }

        /// <summary>One digestion check (CompTick runs it every 250 ticks; RM_MiasmaProof drives it directly):
        /// a fuel drop since the last look is digestion, and a cell past its lifetime feed becomes a rotting bed.</summary>
        public void ObserveFuel()
        {
            if (refuelableComp == null)
            {
                return;
            }
            float fuel = refuelableComp.Fuel;
            if (lastFuel >= 0f && fuel < lastFuel)
            {
                digested += lastFuel - fuel;   // a refill raises fuel and is not digestion
            }
            lastFuel = fuel;
            if (digested >= Ext.lifetimeFeed && Ext.spentDef != null && parent.Spawned)
            {
                BecomeRottingBed();
            }
        }

        private void BecomeRottingBed()
        {
            Map map = parent.Map;
            IntVec3 pos = parent.Position;
            Rot4 rot = parent.Rotation;
            Faction faction = parent.Faction;
            ThingDef spent = Ext.spentDef;
            refuelableComp.ConsumeFuel(refuelableComp.Fuel);   // what is left rots into the bed
            parent.Destroy(DestroyMode.Vanish);
            Thing bed = GenSpawn.Spawn(ThingMaker.MakeThing(spent), pos, map, rot);
            bed.SetFaction(faction);
            Messages.Message("The decay cell is spent: its bed has gone over to rot.", bed, MessageTypeDefOf.NeutralEvent);
        }

        public override string CompInspectStringExtra()
        {
            string s = base.CompInspectStringExtra();
            string mine = "Digested: " + digested.ToString("0") + " / " + Ext.lifetimeFeed.ToString("0")
                          + (RM_MiasmaSettings.decayCellsEnabled ? "" : " (switched off in Mod Settings)");
            return s.NullOrEmpty() ? mine : s + "\n" + mine;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref digested, "digested", 0f);
            Scribe_Values.Look(ref lastFuel, "lastFuel", -1f);
        }
    }

    public static class DecayCellMath
    {
        /// <summary>Output fraction for a bed this full (0..1): zero when empty, minFraction just above empty,
        /// rising linearly to 1 when full.</summary>
        public static float OutputFraction(float fullness, float minFraction)
        {
            if (fullness <= 0f)
            {
                return 0f;
            }
            return Mathf.Lerp(minFraction, 1f, Mathf.Clamp01(fullness));
        }
    }

    /// <summary>
    /// The compost bed with the old meter in it: once per Miasma map, a heap of delta loam with the meter on top,
    /// on open ground away from the edge. Free tier; the meter is the only way to unlock decay cells.
    /// </summary>
    public class RM_MapComponent_DecayMeter : MapComponent
    {
        private bool seeded;

        public RM_MapComponent_DecayMeter(Map map) : base(map) { }

        public override void MapComponentTick()
        {
            if (seeded || Find.TickManager.TicksGame % 977 != 0)
            {
                return;
            }
            seeded = true;
            if (!RM_MiasmaSettings.decayCellsEnabled || map.Biome == null || map.Biome.defName != "RM_Miasma")
            {
                return;
            }
            ThingDef meter = DefDatabase<ThingDef>.GetNamedSilentFail("RM_OldCurrentMeter");
            ThingDef loam = DefDatabase<ThingDef>.GetNamedSilentFail("RM_DeltaLoam");
            if (meter == null || !CellFinder.TryFindRandomCellNear(map.Center, map, map.Size.x / 3,
                    c => c.Standable(map) && !c.Fogged(map) && c.GetFirstItem(map) == null && !c.Roofed(map), out IntVec3 cell)
                && !CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.GetFirstItem(map) == null, out cell))
            {
                return;
            }
            GenSpawn.Spawn(ThingMaker.MakeThing(meter), cell, map);
            if (loam != null)
            {
                Thing heap = ThingMaker.MakeThing(loam);
                heap.stackCount = Mathf.Min(loam.stackLimit, 25);
                GenPlace.TryPlaceThing(heap, cell, map, ThingPlaceMode.Near);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref seeded, "seeded", false);
        }
    }
}
