using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Bacta
{
    public class CompProperties_BactaImmersion : CompProperties
    {
        /// <summary>Size of the fluid fill quad drawn over the suspended pawn, in cells.</summary>
        public Vector2 fluidBarSize = new Vector2(0.55f, 1.45f);

        /// <summary>Offset of that quad from the building centre, in cells.</summary>
        public Vector2 fluidBarOffset = Vector2.zero;

        public CompProperties_BactaImmersion()
        {
            compClass = typeof(CompBactaImmersion);
        }
    }

    /// <summary>
    /// The ruled mechanism (BACTA_TANK_CORE_1, owner card 2): "Healing, not regeneration."
    ///
    /// What it does, and the law each line obeys:
    ///   - fresh wounds and burns close fast, and are tend-equivalent immediately so bleeding
    ///     stops instead of killing the pawn while it works;
    ///   - permanent physical injuries and scars lose severity slowly and are removed at zero;
    ///   - damaged organs are covered by the two lines above, because a damaged organ IS a
    ///     Hediff_Injury on an organ part;
    ///   - infections gain extra immunity ONLY where medicine could have helped;
    ///   - bacta is consumed while it works, and the tank stops when dry.
    ///
    /// What it must never do:
    ///   - regrow a missing part. See the explicit guard in TryHealPawn: Hediff_MissingPart is
    ///     skipped by NAME, not by accident of the type checks below, because "does not regrow
    ///     them" is an owner ruling and a future edit must trip over it.
    ///   - touch the brain, or anything mental. Any hediff on a part tagged
    ///     ConsciousnessSource is skipped outright, and nothing but Hediff_Injury and tendable
    ///     immunizable diseases is touched at all — mental states are not hediffs, and psychic
    ///     or mood hediffs match neither branch.
    ///
    /// Cost: one pass every 250 ticks over the occupant's hediff list. No per-tick scan, and
    /// no scan at all with the tank empty or unoccupied.
    /// </summary>
    public class CompBactaImmersion : ThingComp
    {
        [Unsaved(false)]
        private CompRefuelable cachedFluid;

        [Unsaved(false)]
        private CompPowerTrader cachedPower;

        [Unsaved(false)]
        private CompAffectedByFacilities cachedFacilities;

        /// <summary>Last pass did something a player would call healing. Drives the inspect line.</summary>
        private bool workedLastPass;

        public CompProperties_BactaImmersion Props => (CompProperties_BactaImmersion)props;

        public CompRefuelable Fluid
        {
            get
            {
                if (cachedFluid == null)
                {
                    cachedFluid = parent.TryGetComp<CompRefuelable>();
                }
                return cachedFluid;
            }
        }

        public CompPowerTrader Power
        {
            get
            {
                if (cachedPower == null)
                {
                    cachedPower = parent.TryGetComp<CompPowerTrader>();
                }
                return cachedPower;
            }
        }

        public bool HasFluid => Fluid != null && Fluid.Fuel > 0f;

        public bool Powered => Power == null || Power.PowerOn;

        public float FluidPercent => (Fluid == null) ? 0f : Fluid.FuelPercentOfMax;

        public CompAffectedByFacilities Facilities
        {
            get
            {
                if (cachedFacilities == null)
                {
                    cachedFacilities = parent.TryGetComp<CompAffectedByFacilities>();
                }
                return cachedFacilities;
            }
        }

        /// <summary>
        /// BACTA_SIDE_ITEMS_1: a linked, powered RSW_MedicalDroid speeds the tank's own
        /// healing pass. Read directly off the vanilla facility link list
        /// (CompAffectedByFacilities.LinkedFacilitiesListForReading + IsFacilityActive — the
        /// same "KR pattern" CompProperties_AffectedByFacilities already wires for
        /// VitalsMonitor on this tank, RSW_BactaTank.xml) rather than through the generic
        /// StatDef-offset plumbing VitalsMonitor itself uses: the tank's healing is entirely
        /// custom code, never vanilla TendUtility, so there is no natural StatDef consumer to
        /// hook a stat offset into. A direct link check is the simplest correct thing.
        /// </summary>
        public bool DroidAssisting
        {
            get
            {
                if (!BactaSettings.medicalDroidEnabled)
                {
                    return false;
                }
                CompAffectedByFacilities facilities = Facilities;
                if (facilities == null)
                {
                    return false;
                }
                List<Thing> linked = facilities.LinkedFacilitiesListForReading;
                for (int i = 0; i < linked.Count; i++)
                {
                    if (linked[i].def == BactaDefOf.RSW_MedicalDroid && facilities.IsFacilityActive(linked[i]))
                    {
                        return true;
                    }
                }
                return false;
            }
        }

        private Building_BactaTank Tank => parent as Building_BactaTank;

        private Pawn Occupant => Tank?.ContainedPawn;

        /// <summary>Everything that must be true for the fluid to be doing anything at all.</summary>
        public bool Active
        {
            get
            {
                if (!BactaSettings.healingEnabled)
                {
                    return false;
                }
                return Occupant != null && HasFluid && Powered;
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref workedLastPass, "workedLastPass", defaultValue: false);
        }

        public override void CompTick()
        {
            // tickerType is Normal (CompRefuelable's ConfigErrors demands it for any
            // per-tick consumption path), so CompTickRare never fires. Gate by hand.
            if (!parent.Spawned || !parent.IsHashIntervalTick(BactaTuning.ImmersionIntervalTicks))
            {
                return;
            }

            Pawn pawn = Occupant;
            if (pawn == null)
            {
                workedLastPass = false;
                return;
            }

            if (!Powered)
            {
                workedLastPass = false;
                return;
            }

            if (!HasFluid)
            {
                workedLastPass = false;
                if (BactaSettings.autoEjectEnabled)
                {
                    Tank?.EjectOccupant("RSW_BactaTankEjectedNoFluid", MessageTypeDefOf.NegativeEvent);
                }
                return;
            }

            if (!BactaSettings.healingEnabled)
            {
                // All-off: the tank is a powered box that holds a pawn and nothing else.
                workedLastPass = false;
                return;
            }

            bool didSomething = TryHealPawn(pawn);
            workedLastPass = didSomething;

            if (didSomething)
            {
                float perPass = BactaSettings.fluidCostPerDay
                    * ((float)BactaTuning.ImmersionIntervalTicks / BactaTuning.TicksPerDay);
                Fluid.ConsumeFuel(perPass);
            }
            else if (BactaSettings.autoEjectEnabled)
            {
                Tank?.EjectOccupant("RSW_BactaTankEjectedHealed", MessageTypeDefOf.PositiveEvent);
            }
        }

        /// <summary>
        /// One aggregate pass. Returns true if anything was actually healed, which is both the
        /// fluid-drain condition and the "still work to do" condition for auto-eject.
        ///
        /// The guarded law-abiding mechanism itself (never regrow a missing part, never touch
        /// the brain/mind, scar erasure and infection-assist gates) lives in
        /// BactaHealingUtility.ApplyHealingDose — BACTA_SIDE_ITEMS_1 extracted it out of this
        /// method unchanged so the field consumables (CompUseEffect_BactaHeal) could reuse the
        /// exact same code at item scale instead of reimplementing it. This method's own job
        /// is just computing the tank's per-pass amounts, including the optional
        /// RSW_MedicalDroid speed bonus.
        /// </summary>
        private bool TryHealPawn(Pawn pawn)
        {
            float intervalDays = (float)BactaTuning.ImmersionIntervalTicks / BactaTuning.TicksPerDay;
            float droidMult = DroidAssisting ? BactaSettings.medicalDroidHealMultiplier : 1f;
            float woundHeal = BactaSettings.woundHealPerDay * intervalDays * droidMult;
            float scarHeal = BactaSettings.scarHealPerDay * intervalDays * droidMult;
            float immunityGain = BactaSettings.immunityGainPerDay * intervalDays * droidMult;

            return BactaHealingUtility.ApplyHealingDose(pawn, woundHeal, scarHeal,
                BactaSettings.tendQuality, immunityGain,
                BactaSettings.scarErasureEnabled, BactaSettings.infectionAssistEnabled);
        }

        public override void PostDraw()
        {
            base.PostDraw();

            if (!parent.Spawned || Fluid == null)
            {
                return;
            }

            float pct = FluidPercent;
            if (pct <= 0.001f)
            {
                return;
            }

            // The fluid itself: a translucent pale-blue column over the suspended pawn,
            // its height the fluid level. Drawn between the pawn (Building altitude, via
            // the tank's DynamicDrawPhaseAt) and the glass shell (CompBactaShell, at
            // MoteOverhead), so the pawn reads as being inside the liquid.
            Vector3 centre = parent.DrawPos;
            centre.y = AltitudeLayer.MoteOverhead.AltitudeFor() - 0.01f;
            centre.x += Props.fluidBarOffset.x;
            centre.z += Props.fluidBarOffset.y;

            GenDraw.DrawFillableBar(new GenDraw.FillableBarRequest
            {
                center = centre,
                size = Props.fluidBarSize,
                fillPercent = pct,
                filledMat = BactaMaterials.FluidFilled,
                unfilledMat = BactaMaterials.FluidUnfilled,
                margin = 0f,
                rotation = Rot4.North
            });
        }

        public override string CompInspectStringExtra()
        {
            if (Occupant == null)
            {
                return null;
            }
            if (!Powered)
            {
                return "RSW_BactaTankNoPower".Translate();
            }
            if (!HasFluid)
            {
                return "RSW_BactaTankNoFluid".Translate();
            }
            if (!BactaSettings.healingEnabled)
            {
                return "RSW_BactaTankHealingDisabled".Translate();
            }
            string line = workedLastPass
                ? "RSW_BactaTankImmersing".Translate(Occupant.LabelShort)
                : "RSW_BactaTankNothingToHeal".Translate(Occupant.LabelShort);
            if (DroidAssisting)
            {
                line += "\n" + "RSW_BactaTankDroidAssisting".Translate();
            }
            return line;
        }
    }

    /// <summary>
    /// Materials for the fluid quad. Built once at startup; SolidColorMaterials caches, but
    /// a static here keeps it off the draw path entirely.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class BactaMaterials
    {
        public static readonly Material FluidFilled =
            SolidColorMaterials.SimpleSolidColorMaterial(BactaTuning.FluidColor);

        public static readonly Material FluidUnfilled =
            SolidColorMaterials.SimpleSolidColorMaterial(new Color(0.1f, 0.12f, 0.13f, 0.15f));
    }
}
