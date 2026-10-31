using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ColdStorage
{
    /// <summary>
    /// COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES: an item that ages only while it is kept cold (§5: frost-aged roe and
    /// meat, at or below -25 °C for 15 days; pickled roe that must be chilled after brining). Each tick sample adds the
    /// time since the last one when the item's ambient temperature (a cold storage unit's held temperature, through
    /// Patch_Thing_AmbientTemperature) is at or below <see cref="CompProperties_ColdAging.maxTemperature"/>; warm time
    /// pauses it and loses nothing. When the cold time reaches the aging time (scaled by the aging setting, off when
    /// seal aging is off) the stack becomes <see cref="CompProperties_ColdAging.agesInto"/>, ingredients kept. As with
    /// CompSealed, transitions are queued and run from GameComponent_ColdStorage, never inside a ThingOwner tick.
    /// </summary>
    public class CompColdAging : ThingComp
    {
        /// <summary>One sample adds at most a day: a stack that did not tick (a caravan) does not age a season at once.</summary>
        private const int MaxStep = 60000;

        private static readonly List<CompColdAging> pending = new List<CompColdAging>();

        public int coldTicks;
        public int lastSampleTick = -1;
        private bool queued;

        public CompProperties_ColdAging Props => (CompProperties_ColdAging)props;

        public int AgingTicks => ColdStorageKernel.AgingTicks(Props.agingDays, RM_ColdStorageSettings.agingTimeMultiplier, RM_ColdStorageSettings.sealAgingEnabled);

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref coldTicks, "coldTicks", 0);
            Scribe_Values.Look(ref lastSampleTick, "coldLastSample", -1);
        }

        public override void PreAbsorbStack(Thing otherStack, int count)
        {
            base.PreAbsorbStack(otherStack, count);
            CompColdAging o = (otherStack as ThingWithComps)?.GetComp<CompColdAging>();
            if (o != null)
            {
                coldTicks = ColdStorageKernel.MergedColdTicks(coldTicks, parent.stackCount, o.coldTicks, count);
            }
        }

        public override void PostSplitOff(Thing piece)
        {
            base.PostSplitOff(piece);
            CompColdAging o = (piece as ThingWithComps)?.GetComp<CompColdAging>();
            if (o != null)
            {
                o.coldTicks = coldTicks;
                o.lastSampleTick = lastSampleTick;
            }
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            Sample();
        }

        public override void CompTickInterval(int delta)
        {
            base.CompTickInterval(delta);
            Sample();
        }

        public override void CompTickLong()
        {
            base.CompTickLong();
            Sample();
        }

        private void Sample()
        {
            if (queued || Find.TickManager == null || parent.Destroyed)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now == lastSampleTick)
            {
                return;
            }
            if (parent.MapHeld != null)
            {
                coldTicks = ColdStorageKernel.ColdAccrue(coldTicks, lastSampleTick, now, parent.AmbientTemperature, Props.maxTemperature, MaxStep);
            }
            lastSampleTick = now;
            int need = AgingTicks;
            if (need >= 0 && coldTicks >= need)
            {
                queued = true;
                pending.Add(this);
            }
        }

        internal static void ClearPending()
        {
            pending.Clear();
        }

        internal static void RunPending()
        {
            if (pending.Count == 0)
            {
                return;
            }
            CompColdAging[] batch = pending.ToArray();
            pending.Clear();
            foreach (CompColdAging c in batch)
            {
                c.queued = false;
                if (!c.parent.Destroyed)
                {
                    CompSealed.Replace(c.parent, c.Props.agesInto);
                }
            }
        }

        public override string CompInspectStringExtra()
        {
            int need = AgingTicks;
            string limit = Props.maxTemperature.ToStringTemperature("F0");
            if (need < 0)
            {
                return "RM_ColdStorage_ColdAgingOff".Translate(Props.agesInto.label);
            }
            int left = Mathf.Max(0, need - coldTicks);
            return "RM_ColdStorage_ColdAging".Translate(Props.agesInto.label, limit, left.ToStringTicksToPeriod());
        }
    }

    public class CompProperties_ColdAging : CompProperties
    {
        /// <summary>What it becomes after <see cref="agingDays"/> of cold.</summary>
        public ThingDef agesInto;

        public float agingDays = 15f;

        /// <summary>Time counts only at or below this temperature (°C).</summary>
        public float maxTemperature = -25f;

        public CompProperties_ColdAging()
        {
            compClass = typeof(CompColdAging);
        }

        public override IEnumerable<string> ConfigErrors(ThingDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
            {
                yield return e;
            }
            if (agesInto == null)
            {
                yield return "CompProperties_ColdAging has no agesInto";
            }
            if (agingDays <= 0f)
            {
                yield return "CompProperties_ColdAging agingDays is not positive";
            }
            if (parentDef.category != ThingCategory.Item)
            {
                yield return "CompProperties_ColdAging on a non-item def";
            }
            if (parentDef.tickerType == TickerType.Never)
            {
                yield return "CompProperties_ColdAging on a def that never ticks";
            }
        }
    }
}
