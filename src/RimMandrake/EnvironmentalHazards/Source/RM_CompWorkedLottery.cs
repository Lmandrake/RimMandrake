using System;
using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S2 spike (sump_kit_spec.md "the dig lottery") and S6b
    // (§7b derrick pumping) — one comp class, two content uses, exactly as
    // the spec's New-C# roster table specs it ("shafts AND derricks"). Work-
    // accumulation shape cribbed from RimWorld/CompDeepDrill.cs (verified,
    // decompile: portionProgress float, TryProducePortion at a work
    // threshold) but yielding from a weighted RM_LotteryTableDef stratum,
    // not a fixed deep-resource grid.
    //
    // Owner card 2 (RULED 2026-09-12, sump_kit_spec.md "Open owner cards"):
    // era traps are disarmable — high skill gate, failure detonates. Exposed
    // here as TryDisarmPendingTrap(), a real callable API a JobDriver/
    // WorkGiver can drive; the actual interact-command UI wiring (float menu
    // option, work-type gating) is content/UI work for the full build, not
    // an engine-fact this spike needed to resolve — left owed, not silently
    // skipped, same as Miasma M6's GenStep/ThinkTree wiring.
    //
    // S3 tie-in (deep digs / greedy pumping wake the tar beast): this comp
    // fires a static event rather than calling into RM_CompStationEater
    // directly — that class does not exist yet (RM_GenStep_PlacedSetPieces,
    // the shared scatterer both this kit and Miasma M6 need, is unbuilt;
    // confirmed by grep, not assumed — MIASMA_MECHANICS_1's own spike pass
    // left it unbuilt too). The event lets this comp compile and be used
    // standalone now; S3's future build subscribes to it, no rewiring of
    // this file needed later.
    public class CompProperties_WorkedLottery : CompProperties
    {
        public RM_LotteryTableDef table;

        /// <summary>Work units for one completed portion. INVENTED default,
        /// same magnitude as CompDeepDrill's WorkPerPortionBase (10000)
        /// since this cribs that comp's shape.</summary>
        public float workPerPortion = 10000f;

        /// <summary>Per-stratum trap weight multiplier. INVENTED, per the
        /// spec's S2 depth gradient ("heavier trap weight").</summary>
        public float trapWeightMultiplierPerStratum = 1.3f;

        /// <summary>Stratum depth (0-indexed) at and past which a completed
        /// portion also rolls a beast-wake signal. INVENTED (spec: "stratum
        /// 4+"), stored 0-indexed here so 4 below means the spec's
        /// "stratum 4".</summary>
        public int beastWakeStratumThreshold = 4;

        /// <summary>Trap telegraph fuse, in ticks. INVENTED: 15 in-game
        /// seconds = 15 * 60 = 900 ticks (spec S2 "15-second fuse").</summary>
        public int trapFuseTicks = 900;

        public float trapExplosionRadius = 3.9f;

        public DamageDef trapDamageDef;

        /// <summary>S6b: this instance is a derrick/pump, not a dig shaft —
        /// content-facing distinction only (inspect string, disarm gating);
        /// the mechanic is identical. Per spec: "same comp, different yield
        /// table, so derricks and dig shafts share one class."</summary>
        public bool isPumpVariant;

        public CompProperties_WorkedLottery()
        {
            compClass = typeof(RM_CompWorkedLottery);
        }
    }

    public enum TrapDisarmResult
    {
        NoTrapArmed,
        Disarmed,
        Detonated
    }

    public class RM_CompWorkedLottery : ThingComp
    {
        private float portionProgress;
        private int stratumDepth;
        private int trapFuseTicksRemaining = -1;

        public CompProperties_WorkedLottery Props => (CompProperties_WorkedLottery)props;

        /// <summary>Fires (map, cell, stratumDepth) once a completed portion
        /// crosses beastWakeStratumThreshold, or a greedy pump variant is
        /// told to wake directly (NotifyGreedyPump). S3's future
        /// RM_CompStationEater / dormancy wake seam subscribes here.</summary>
        public static event Action<Map, IntVec3, int> BeastWakeRequested;

        public bool TrapArmed => trapFuseTicksRemaining >= 0;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref portionProgress, "portionProgress", 0f);
            Scribe_Values.Look(ref stratumDepth, "stratumDepth", 0);
            Scribe_Values.Look(ref trapFuseTicksRemaining, "trapFuseTicksRemaining", -1);
        }

        public override void CompTick()
        {
            base.CompTick();
            if (trapFuseTicksRemaining < 0)
            {
                return;
            }
            trapFuseTicksRemaining--;
            if (trapFuseTicksRemaining <= 0)
            {
                Detonate();
            }
        }

        /// <summary>Generic work-input seam — deliberately not tied to any
        /// one stat, so a colonist dig job and a pump's power-driven
        /// throughput can both feed the same comp (spec S6b: "a props field
        /// on RM_CompWorkedLottery reused for pump-shape work").</summary>
        public void AddWork(float amount, Pawn optionalWorker = null)
        {
            if (amount <= 0f || Props.table == null || parent.Map == null)
            {
                return;
            }
            portionProgress += amount;
            if (portionProgress < Props.workPerPortion)
            {
                return;
            }
            portionProgress -= Props.workPerPortion;
            RollPortion(optionalWorker);
        }

        /// <summary>S6b entry point: a derrick past its pump-volume threshold
        /// calls this directly, bypassing the lottery roll (greedy pumping
        /// wakes the beast, it does not sell a stratum find).</summary>
        public void NotifyGreedyPump()
        {
            if (parent.Map == null)
            {
                return;
            }
            BeastWakeRequested?.Invoke(parent.Map, parent.Position, stratumDepth);
        }

        private void RollPortion(Pawn worker)
        {
            RM_LotteryTableDef table = Props.table;
            if (table.strata.NullOrEmpty())
            {
                return;
            }

            int stratumIndex = Math.Min(stratumDepth, table.strata.Count - 1);
            RM_LotteryStratum stratum = table.strata[stratumIndex];
            if (!stratum.rows.NullOrEmpty()
                && stratum.rows.TryRandomElementByWeight(RowWeight, out RM_LotteryRow row))
            {
                if (row.isTrap)
                {
                    ArmTrap();
                }
                else if (row.thingDef != null)
                {
                    Thing thing = ThingMaker.MakeThing(row.thingDef);
                    thing.stackCount = row.countRange.RandomInRange;
                    GenPlace.TryPlaceThing(thing, parent.Position, parent.Map, ThingPlaceMode.Near);
                }
            }

            stratumDepth++;
            if (stratumDepth >= Props.beastWakeStratumThreshold)
            {
                BeastWakeRequested?.Invoke(parent.Map, parent.Position, stratumDepth);
            }
        }

        private float RowWeight(RM_LotteryRow row)
        {
            if (row.isTrap)
            {
                return row.weight * (float)Math.Pow(Props.trapWeightMultiplierPerStratum, stratumDepth);
            }
            return row.weight;
        }

        private void ArmTrap()
        {
            trapFuseTicksRemaining = Props.trapFuseTicks;
            // Telegraph per the sheet ("the click"): CompInspectStringExtra
            // surfaces the countdown below. A click SoundDef and a pause-
            // letter are content/audio authoring, not an engine mechanism —
            // left for the full build.
        }

        /// <summary>Owner card 2: disarmable, high skill gate, failure
        /// detonates. Callable now by any future JobDriver/WorkGiver; the
        /// float-menu/work-type wiring that reaches this method is owed to
        /// the full build.</summary>
        public TrapDisarmResult TryDisarmPendingTrap(Pawn pawn, SkillDef skill, int skillThresholdInclusive)
        {
            if (!TrapArmed)
            {
                return TrapDisarmResult.NoTrapArmed;
            }

            int skillLevel = pawn?.skills?.GetSkill(skill)?.Level ?? 0;
            if (skillLevel >= skillThresholdInclusive)
            {
                trapFuseTicksRemaining = -1;
                return TrapDisarmResult.Disarmed;
            }

            Detonate();
            return TrapDisarmResult.Detonated;
        }

        private void Detonate()
        {
            trapFuseTicksRemaining = -1;
            if (parent.Map == null)
            {
                return;
            }
            // GenExplosion.DoExplosion (verified, RimWorld/GenExplosion.cs) —
            // the same call any vanilla explosive trap uses. The armed-thing
            // variant Building_TrapExplosive itself cribs (surfacing intact
            // for the disarm interaction above) is content/placement work
            // for the full build, not this spike's engine-fact question.
            GenExplosion.DoExplosion(
                parent.Position,
                parent.Map,
                Props.trapExplosionRadius,
                Props.trapDamageDef ?? DamageDefOf.Bomb,
                parent);
        }

        public override string CompInspectStringExtra()
        {
            string label = Props.isPumpVariant ? "RM_LotteryPumpDepth" : "RM_LotteryStratumDepth";
            string result = label.Translate() + ": " + stratumDepth;
            if (TrapArmed)
            {
                result += "\n" + "RM_LotteryTrapArmed".Translate() + ": " + trapFuseTicksRemaining;
            }
            return result;
        }
    }
}
