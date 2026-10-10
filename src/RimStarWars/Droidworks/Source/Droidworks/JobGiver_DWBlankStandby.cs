using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_FORMAT_TIERS_1 (bridge5 2026-10-09 A3 FAIL: a blank droid read "Wandering." after 600 ticks).
    /// A BLANK droid has every work tag disabled, so the main colonist block gives it nothing and the vanilla
    /// "Idle colonist" block (Core Humanlike.xml) sends it to JobGiver_WanderColony. Inserted at
    /// Humanlike_PostMain - after main work, before the idle block - this stands a blank droid in place instead.
    /// Everything earlier in the tree still runs: drafted and queued player orders, lord duties, and the
    /// recharge insert (Humanlike_PreMain), so a blank droid can still be ordered about and still docks.
    /// Non-droids and every other tier get null and fall through to vanilla untouched.
    /// </summary>
    public class JobGiver_DWBlankStandby : ThinkNode_JobGiver
    {
        public int ticks = 250;

        public override ThinkNode DeepCopy(bool resolve = true)
        {
            var copy = (JobGiver_DWBlankStandby)base.DeepCopy(resolve);
            copy.ticks = ticks;
            return copy;
        }

        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!DroidFormatTierUtility.IsDroid(pawn)) return null;
            DroidFormatTier? tier = DroidFormatTierUtility.TierOf(pawn);
            if (!tier.HasValue || !DroidworksKernel.TierStandsIdle(tier.Value)) return null;
            Job job = JobMaker.MakeJob(JobDefOf.Wait);
            job.expiryInterval = ticks;
            job.checkOverrideOnExpire = true;
            return job;
        }
    }
}
