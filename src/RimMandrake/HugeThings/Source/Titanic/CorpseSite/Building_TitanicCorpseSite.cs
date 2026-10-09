using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.HugeThings;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Card #4: "T3 corpse becomes a map landmark harvested over days
    /// (camps, spoilage, scavenger draw) - never an instant meat mountain."
    /// This class is the landmark and the spoilage clock; the "over days"
    /// harvesting is JobDriver_HarvestTitanicCorpse /
    /// WorkGiver_HarvestTitanicCorpse working against MakeSessionProducts / CommitHarvest below.
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

        private const int TicksPerSpoilageStep = RM_TitanicKernel.TicksPerDay;
        // Defaults live in RM_TitanicCreaturesSettings (meat spoils faster
        // than leather by default) - read from there at point of use so a
        // settings change takes effect on sites already standing.

        // CORPSE_SITE_SAFETY_1 (B3.12): a pool whose def is gone (a removed mod) is not yield; it can never be harvested or drain.
        public bool HasYield => (meatRemaining > 0 && meatDef != null) || (leatherRemaining > 0 && leatherDef != null);
        private static bool loggedMissingDef;

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
            if (!HasYield)
            {
                Destroy(); // CORPSE_SITE_SAFETY_1 (B3.12): emptied by a load-time reconcile or a mod removal
                return;
            }
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
            int meatLoss = RM_TitanicKernel.SpoilLoss(meatRemaining, RM_HugeThingsSettings.corpseSiteMeatSpoilagePerDay);
            int leatherLoss = RM_TitanicKernel.SpoilLoss(leatherRemaining, RM_HugeThingsSettings.corpseSiteLeatherSpoilagePerDay);
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
        /// CORPSE_SITE_SAFETY_1 (B3.11): this only MAKES the products; the pool is reduced by CommitHarvest with what was actually
        /// placed, so an unplaceable remainder stays in the pool.
        /// </summary>
        public System.Collections.Generic.List<Thing> MakeSessionProducts()
        {
            var results = new System.Collections.Generic.List<Thing>();
            int meatTake = RM_TitanicKernel.HarvestTake(meatRemaining, RM_HugeThingsSettings.corpseSiteHarvestMeatPerSession);
            if (meatTake > 0 && meatDef != null)
            {
                Thing meat = ThingMaker.MakeThing(meatDef);
                meat.stackCount = meatTake;
                results.Add(meat);
            }
            int leatherTake = RM_TitanicKernel.HarvestTake(leatherRemaining, RM_HugeThingsSettings.corpseSiteHarvestLeatherPerSession);
            if (leatherTake > 0 && leatherDef != null)
            {
                Thing leather = ThingMaker.MakeThing(leatherDef);
                leather.stackCount = leatherTake;
                results.Add(leather);
            }
            return results;
        }

        /// <summary>Takes `delivered` units of `def` out of its pool (never below zero).</summary>
        public void CommitHarvest(ThingDef def, int delivered)
        {
            if (def == null || delivered <= 0) return;
            if (def == meatDef) meatRemaining = Mathf.Max(0, meatRemaining - delivered);
            else if (def == leatherDef) leatherRemaining = Mathf.Max(0, leatherRemaining - delivered);
        }

        /// <summary>Ends a session: an emptied site goes.</summary>
        public void FinishSession()
        {
            if (!HasYield && !Destroyed)
            {
                Destroy();
            }
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
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                // CORPSE_SITE_SAFETY_1 (B3.12): a pool whose def no longer loads is zeroed (an empty site is removed on its next
                // rare tick, never during load).
                if ((meatDef == null && meatRemaining > 0) || (leatherDef == null && leatherRemaining > 0))
                {
                    if (!loggedMissingDef)
                    {
                        loggedMissingDef = true;
                        Log.Warning("[RimMandrake.TitanicCreatures] a titan corpse site's meat or leather def no longer exists; that pool is emptied.");
                    }
                    if (meatDef == null) meatRemaining = 0;
                    if (leatherDef == null) leatherRemaining = 0;
                }
            }
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
