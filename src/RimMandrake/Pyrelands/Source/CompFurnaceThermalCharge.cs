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

        public bool WantsHeat => RM_FurnaceKernel.WantsHeat(charge, PyrelandsTuning.FurnaceChargeSeekBelow);

        public bool IsFullyCharged => RM_FurnaceKernel.IsFullyCharged(charge, PyrelandsTuning.FurnaceChargeAvoidAbove);

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
            float step = ComputeChargeStep(beast.AmbientTemperature, AdjacentFireCount(beast) > 0);
            charge = RM_FurnaceKernel.ClampCharge(charge + step);
        }

        /// <summary>
        /// FURNACEBEAST_WORLD_MIGRATION_1 — the world leg's own entry point.
        ///
        /// 🔑 THIS IS THE SAME NUMBER, DRIVEN THE SAME WAY, not a second charge
        /// model. WorldObject_RM_FurnaceHerd calls this once per its own tick
        /// interval, on each member pawn's comp directly, while the pawn is
        /// held off-map (unspawned, so <see cref="CompTickInterval"/> above
        /// never runs for it — ThingComp.CompTickInterval only fires for a
        /// spawned Thing). No "near fire" bonus off-map: the burn-line concept
        /// (MapComponent_BurnLine) only exists once a Map does, so the
        /// Pyrelands leg's extra pull is expressed purely through that biome's
        /// own (hot) ambient temperature, not simulated fire-adjacency.
        /// </summary>
        public void ApplyWorldTick(float ambientAtTile)
        {
            charge = RM_FurnaceKernel.ClampCharge(charge + ComputeChargeStep(ambientAtTile, nearFire: false));
        }

        /// <summary>
        /// The capacitor's step math, factored out so the on-map tick (fed a
        /// real Thing.AmbientTemperature) and the off-map world tick (fed
        /// GenTemperature.GetTemperatureAtTile) are provably the same formula.
        /// </summary>
        internal static float ComputeChargeStep(float ambient, bool nearFire)
        {
            // Charge rate scales with how far above the threshold it is (capped so a freak reading cannot fill the
            // capacitor in one tick); a dead band holds; standing in the burn is the fast lane (counted, not measured:
            // a beast on the EDGE of a front would otherwise gain almost nothing). RM_FurnaceKernel.ChargeStep.
            return RM_FurnaceKernel.ChargeStep(ambient, nearFire,
                PyrelandsTuning.FurnaceChargeAmbientC, PyrelandsTuning.FurnaceChargeAmbientSpanC, PyrelandsTuning.FurnaceChargePerCheckAtFullHeat,
                PyrelandsTuning.FurnaceBleedAmbientC, PyrelandsTuning.FurnaceBleedAmbientSpanC, PyrelandsTuning.FurnaceBleedPerCheckAtFullCold,
                PyrelandsTuning.FurnaceChargePerCheckNearFire);
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
