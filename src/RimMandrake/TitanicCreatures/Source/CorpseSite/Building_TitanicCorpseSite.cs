using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #4: "T3 corpse becomes a map landmark harvested over days
    /// (camps, spoilage, scavenger draw) - never an instant meat mountain."
    /// This class is the landmark and the spoilage clock; the "over days"
    /// harvesting is JobDriver_HarvestTitanicCorpse /
    /// WorkGiver_HarvestTitanicCorpse working against HarvestOneSession below.
    ///
    /// Spawned in place of the vanilla Corpse by
    /// Patch_Corpse_SpawnSetup_TitanicSite / TitanicCorpseSiteUtility, sized
    /// per Defs/ThingDefs/RM_TitanicCorpseSite.xml (4x4, matching the T3
    /// footprint).
    ///
    /// SCOPED DOWN, follow-up owed (see build report): "camps" and "scavenger
    /// draw" from the ruling are NOT implemented here - both require naming an
    /// actual faction/pawnkind to spawn, which is out of this engine-only
    /// build's scope (no creature or faction is named anywhere in the item).
    /// The spoilage clock and the multi-session harvest ARE implemented.
    /// </summary>
    public class Building_TitanicCorpseSite : Building
    {
        private string sourceLabel;
        private ThingDef meatDef;
        private int meatRemaining;
        private ThingDef leatherDef;
        private int leatherRemaining;
        private int lastSpoilageTick = -1;

        private const int TicksPerSpoilageStep = GenDate.TicksPerDay;
        private const float MeatSpoilageFractionPerDay = 0.15f;
        private const float LeatherSpoilageFractionPerDay = 0.08f; // hide/leather keeps longer than meat

        private const int HarvestMeatPerSession = 25;
        private const int HarvestLeatherPerSession = 10;

        public bool HasYield => meatRemaining > 0 || leatherRemaining > 0;

        public void Setup(string sourceLabelArg, ThingDef meatDefArg, int meatTotal, ThingDef leatherDefArg, int leatherTotal)
        {
            sourceLabel = sourceLabelArg;
            meatDef = meatDefArg;
            meatRemaining = meatTotal;
            leatherDef = leatherDefArg;
            leatherRemaining = leatherTotal;
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            if (!respawningAfterLoad)
            {
                lastSpoilageTick = Find.TickManager.TicksGame;
            }
        }

        public override void TickRare()
        {
            base.TickRare();
            int now = Find.TickManager.TicksGame;
            if (lastSpoilageTick < 0)
            {
                lastSpoilageTick = now;
                return;
            }
            if (now - lastSpoilageTick < TicksPerSpoilageStep)
            {
                return;
            }
            lastSpoilageTick = now;
            ApplyDailySpoilage();
        }

        /// <summary>
        /// A fixed fraction of what's LEFT is lost each day rather than a hard
        /// vanish-at-tick-N deadline, so an untouched site decays away over
        /// roughly a week instead of lasting forever or disappearing on a
        /// cliff edge - the "spoilage clock" the ruling names, without
        /// building a new per-stack rot simulation for a one-off Building.
        /// </summary>
        private void ApplyDailySpoilage()
        {
            int meatLoss = Mathf.CeilToInt(meatRemaining * MeatSpoilageFractionPerDay);
            int leatherLoss = Mathf.CeilToInt(leatherRemaining * LeatherSpoilageFractionPerDay);
            meatRemaining = Mathf.Max(0, meatRemaining - meatLoss);
            leatherRemaining = Mathf.Max(0, leatherRemaining - leatherLoss);
            if (!HasYield)
            {
                Destroy();
            }
        }

        /// <summary>
        /// One work session's worth of extraction - never the whole pool, so
        /// harvesting a T3 corpse genuinely takes multiple visits/days rather
        /// than one long toil that behaves like an instant butcher underneath.
        /// </summary>
        public System.Collections.Generic.List<Thing> HarvestOneSession(Pawn worker)
        {
            var results = new System.Collections.Generic.List<Thing>();

            int meatTake = Mathf.Min(meatRemaining, HarvestMeatPerSession);
            if (meatTake > 0 && meatDef != null)
            {
                Thing meat = ThingMaker.MakeThing(meatDef);
                meat.stackCount = meatTake;
                results.Add(meat);
                meatRemaining -= meatTake;
            }

            int leatherTake = Mathf.Min(leatherRemaining, HarvestLeatherPerSession);
            if (leatherTake > 0 && leatherDef != null)
            {
                Thing leather = ThingMaker.MakeThing(leatherDef);
                leather.stackCount = leatherTake;
                results.Add(leather);
                leatherRemaining -= leatherTake;
            }

            if (!HasYield)
            {
                Destroy();
            }
            return results;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref sourceLabel, "sourceLabel");
            Scribe_Defs.Look(ref meatDef, "meatDef");
            Scribe_Values.Look(ref meatRemaining, "meatRemaining");
            Scribe_Defs.Look(ref leatherDef, "leatherDef");
            Scribe_Values.Look(ref leatherRemaining, "leatherRemaining");
            Scribe_Values.Look(ref lastSpoilageTick, "lastSpoilageTick", -1);
        }

        public override string GetInspectString()
        {
            var sb = new StringBuilder(base.GetInspectString());
            if (sb.Length > 0)
            {
                sb.AppendLine();
            }
            sb.Append("RM_TitanicCorpseSite_Source".Translate(sourceLabel));
            sb.AppendLine();
            sb.Append("RM_TitanicCorpseSite_Remaining".Translate(meatRemaining, leatherRemaining));
            return sb.ToString();
        }
    }
}
