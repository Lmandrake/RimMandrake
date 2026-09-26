using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// FURNACEBEAST_THERMAL_CYCLE_1, part 2 — the capacitor itself.
    ///
    /// 🔑 OWNER, 2026-09-14, verbatim: "let's make them build up heat in the Deep
    /// Desert and intentionally coming into the Pyrelands to help it burn and
    /// absorb yet more heat … then they migrate all the way to the near
    /// terminator where they eat everything in sight while they slowly bleed out
    /// all that heat … Like a slow thermal capacitor cycle."
    ///
    /// This comp is the STATE that cycle runs on: one number, 0 (cold, empty) to
    /// 1 (fully charged), saved with the pawn. It is the thing the shipped
    /// description already promises the player can see — "glowing brighter at the
    /// seams between its plates" — and until now the description promised a
    /// number that did not exist.
    ///
    /// THREE CONSEQUENCES, and no more:
    ///
    ///   1. CHARGE. Ambient temperature above ChargeAmbientC charges it, faster
    ///      the hotter it is; standing next to live fire charges it hard. That is
    ///      what makes walking into a burn a rational act for the beast rather
    ///      than flavour text.
    ///   2. BLEED. Ambient below BleedAmbientC discharges it. Between the two
    ///      thresholds the charge holds — a capacitor, not a thermometer.
    ///   3. RADIANT PUSH. A charged beast pushes real heat into its cell,
    ///      proportional to charge. ⚠️ This is deliberately SMALL and it is NOT a
    ///      duplicate of the vanilla CompHeatPusher the beast also carries: that
    ///      one is flat and unconditional, this one is the part that goes away as
    ///      the beast runs down. A beast at zero charge pushes nothing.
    ///
    /// 🔑 WHY A ThingComp AND NOT A HediffComp. A hediff is health state and is
    /// lost, re-added and re-scribed through downing, tending and anaesthesia; a
    /// capacitor is not health. A ThingComp on the race is saved with the pawn
    /// unconditionally and survives everything short of death. The warmth AURA
    /// stays a hediff (on the pawns standing near it) — that is a different
    /// thing and the two must not be confused.
    /// </summary>
    public class CompProperties_FurnaceThermalCharge : CompProperties
    {
        public CompProperties_FurnaceThermalCharge()
        {
            compClass = typeof(CompFurnaceThermalCharge);
        }
    }

    public class CompFurnaceThermalCharge : ThingComp
    {
        private float charge;

        /// <summary>0 = run down and cold, 1 = fully banked. Read by
        /// CompFurnaceWarmthAura (how far the warmth reaches) and by
        /// JobGiver_RUT_FurnaceThermalCycle (seek fire, or leave it alone).</summary>
        public float Charge => charge;

        public bool WantsHeat => charge < PyrelandsTuning.FurnaceChargeSeekBelow;

        public bool IsFullyCharged => charge >= PyrelandsTuning.FurnaceChargeAvoidAbove;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref charge, "furnaceThermalCharge", 0f);
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);

            if (!RM_PyrelandsSettings.pyrelandsEnabled || !RM_PyrelandsSettings.furnaceThermalEnabled)
            {
                return;
            }
            if (!parent.IsHashIntervalTick(PyrelandsTuning.FurnaceChargeIntervalTicks, delta))
            {
                return;
            }
            if (!(parent is Pawn beast) || !beast.Spawned || beast.Dead)
            {
                return;
            }

            UpdateCharge(beast);
            PushRadiantHeat(beast);
        }

        private void UpdateCharge(Pawn beast)
        {
            float ambient = beast.AmbientTemperature;
            float step;

            if (ambient >= PyrelandsTuning.FurnaceChargeAmbientC)
            {
                // Charge rate scales with how far above the threshold it is, so a
                // 40 degC afternoon in the Deep Desert charges slowly over weeks
                // and a burning grass cell charges in minutes. Capped so a
                // freak 1000 degC reading cannot fill the capacitor in one tick.
                float over = Mathf.Min(
                    ambient - PyrelandsTuning.FurnaceChargeAmbientC,
                    PyrelandsTuning.FurnaceChargeAmbientSpanC);
                step = PyrelandsTuning.FurnaceChargePerCheckAtFullHeat
                     * (over / PyrelandsTuning.FurnaceChargeAmbientSpanC);
            }
            else if (ambient <= PyrelandsTuning.FurnaceBleedAmbientC)
            {
                float under = Mathf.Min(
                    PyrelandsTuning.FurnaceBleedAmbientC - ambient,
                    PyrelandsTuning.FurnaceBleedAmbientSpanC);
                step = -PyrelandsTuning.FurnaceBleedPerCheckAtFullCold
                     * (under / PyrelandsTuning.FurnaceBleedAmbientSpanC);
            }
            else
            {
                // The dead band. A capacitor at rest holds its charge.
                step = 0f;
            }

            // Standing in the burn is the fast lane, and it is what makes the
            // Pyrelands leg of the cycle worth the walk. Counted rather than
            // measured as temperature: AmbientTemperature at a burning cell is
            // already high, but a beast walking the EDGE of a front would
            // otherwise gain almost nothing.
            if (AdjacentFireCount(beast) > 0)
            {
                step += PyrelandsTuning.FurnaceChargePerCheckNearFire;
            }

            charge = Mathf.Clamp01(charge + step);
        }

        private static int AdjacentFireCount(Pawn beast)
        {
            int count = 0;
            List<Thing> fires = beast.Map.listerThings.ThingsOfDef(ThingDefOf.Fire);
            float radiusSq = PyrelandsTuning.FurnaceChargeFireRadius * PyrelandsTuning.FurnaceChargeFireRadius;
            for (int i = 0; i < fires.Count; i++)
            {
                if ((fires[i].Position - beast.Position).LengthHorizontalSquared <= radiusSq)
                {
                    count++;
                }
            }
            return count;
        }

        private void PushRadiantHeat(Pawn beast)
        {
            if (charge <= 0.01f)
            {
                return;
            }
            // Per-check, not per-second: the interval is FurnaceChargeIntervalTicks,
            // and PushHeat's argument is an energy quantity, so the constant is
            // already calibrated for this cadence rather than for CompHeatPusher's.
            GenTemperature.PushHeat(
                beast.PositionHeld, beast.MapHeld,
                PyrelandsTuning.FurnaceRadiantHeatPerCheckAtFullCharge * charge);
        }

        public override string CompInspectStringExtra()
        {
            if (!RM_PyrelandsSettings.pyrelandsEnabled || !RM_PyrelandsSettings.furnaceThermalEnabled)
            {
                return null;
            }
            return "RM_FurnaceHeatCharge".Translate() + ": " + charge.ToStringPercent("F0");
        }
    }
}
