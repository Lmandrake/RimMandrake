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
        private static readonly List<Hediff> tmpHediffs = new List<Hediff>();

        [Unsaved(false)]
        private CompRefuelable cachedFluid;

        [Unsaved(false)]
        private CompPowerTrader cachedPower;

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
        /// </summary>
        private bool TryHealPawn(Pawn pawn)
        {
            if (pawn.health == null || pawn.Dead)
            {
                return false;
            }

            float intervalDays = (float)BactaTuning.ImmersionIntervalTicks / BactaTuning.TicksPerDay;
            float woundHeal = BactaSettings.woundHealPerDay * intervalDays;
            float scarHeal = BactaSettings.scarHealPerDay * intervalDays;
            float immunityGain = BactaSettings.immunityGainPerDay * intervalDays;

            bool did = false;

            tmpHediffs.Clear();
            tmpHediffs.AddRange(pawn.health.hediffSet.hediffs);

            for (int i = 0; i < tmpHediffs.Count; i++)
            {
                Hediff hediff = tmpHediffs[i];
                if (hediff == null || hediff.pawn != pawn)
                {
                    continue;
                }

                // ---- LAW: bacta never regrows anything. -------------------------------
                // Owner, 2026-09-13: "Does heal organs, does not regrow them. Healing, not
                // regeneration." A missing finger, ear, kidney or leg is NOT a thing this
                // comp may ever remove. Do not delete this branch to "simplify" the type
                // checks below — it is the ruling, written where an editor will hit it.
                if (hediff is Hediff_MissingPart)
                {
                    continue;
                }

                // ---- LAW: physical only, never the brain and never the mind. ----------
                if (IsBrainOrMind(hediff))
                {
                    continue;
                }

                if (hediff is Hediff_Injury injury)
                {
                    if (injury.IsPermanent())
                    {
                        // Scars and permanent physical injuries: slow erasure.
                        if (!BactaSettings.scarErasureEnabled)
                        {
                            continue;
                        }

                        injury.Severity -= scarHeal;
                        did = true;

                        if (injury.Severity <= 0.001f)
                        {
                            pawn.health.RemoveHediff(injury);
                        }
                        continue;
                    }

                    // Fresh wound, burn, or damaged organ (an organ injury is a
                    // Hediff_Injury whose Part is the organ — same branch, by design).
                    if (injury.TendableNow(ignoreTimer: true) && !injury.IsTended())
                    {
                        // Tend-equivalent immediately: the ruled point of the tank is that a
                        // pawn brought back alive stops dying of blood loss on the way.
                        injury.Tended(BactaSettings.tendQuality, BactaSettings.tendQuality);
                        did = true;
                    }

                    if (injury.Severity > 0f)
                    {
                        injury.Heal(woundHeal);
                        did = true;

                        if (injury.Severity <= 0.001f)
                        {
                            pawn.health.RemoveHediff(injury);
                        }
                    }
                    continue;
                }

                // ---- Infections: only where medicine would have helped. ---------------
                // Owner verbatim: "as long as medicine would aid the infections. Some
                // infections remain in effect." The test is the game's own: a disease with
                // a TendDuration comp that can develop natural immunity is one a doctor
                // could fight. Anything chronic, untendable, or immunity-less is left alone.
                if (!BactaSettings.infectionAssistEnabled)
                {
                    continue;
                }

                if (hediff.TryGetComp<HediffComp_TendDuration>() == null)
                {
                    continue;
                }

                if (!hediff.def.PossibleToDevelopImmunityNaturally())
                {
                    continue;
                }

                if (hediff.TendableNow(ignoreTimer: true) && !hediff.IsTended())
                {
                    hediff.Tended(BactaSettings.tendQuality, BactaSettings.tendQuality);
                    did = true;
                }

                if (BoostImmunity(pawn, hediff, immunityGain))
                {
                    did = true;
                }
            }

            tmpHediffs.Clear();
            return did;
        }

        /// <summary>
        /// Nudges the pawn's real immunity record for this disease. Deliberately reaches
        /// ImmunityListForReading rather than GetImmunityRecord: the latter can hand back a
        /// freshly-built detached record for gene-granted immunity, and writing to that
        /// would look like it worked and do nothing.
        /// </summary>
        private static bool BoostImmunity(Pawn pawn, Hediff hediff, float amount)
        {
            if (amount <= 0f || pawn.health.immunity == null)
            {
                return false;
            }

            List<ImmunityRecord> records = pawn.health.immunity.ImmunityListForReading;
            for (int i = 0; i < records.Count; i++)
            {
                ImmunityRecord record = records[i];
                if (record.hediffDef != hediff.def)
                {
                    continue;
                }
                if (record.immunity >= 1f)
                {
                    return false;
                }
                record.immunity = Mathf.Clamp01(record.immunity + amount);
                return true;
            }
            return false;
        }

        /// <summary>
        /// True for anything bacta must not touch on neurological grounds.
        ///
        /// The brain test is structural, not by defName: the brain is the body part tagged
        /// ConsciousnessSource, in every body def including modded and alien ones, so an
        /// injury sitting on it is skipped whatever that part happens to be called.
        /// Mental damage needs no test of its own — mental states are not hediffs at all,
        /// and psychic/mood hediffs match neither the Hediff_Injury branch nor the
        /// tendable-immunizable disease branch, so they are never reached.
        /// </summary>
        private static bool IsBrainOrMind(Hediff hediff)
        {
            BodyPartRecord part = hediff.Part;
            if (part?.def?.tags == null)
            {
                return false;
            }
            return part.def.tags.Contains(BodyPartTagDefOf.ConsciousnessSource);
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
            return workedLastPass
                ? "RSW_BactaTankImmersing".Translate(Occupant.LabelShort)
                : "RSW_BactaTankNothingToHeal".Translate(Occupant.LabelShort);
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
