using Verse;

namespace Droidworks
{
    public class HediffCompProperties_PoweredDown : HediffCompProperties
    {
        public HediffCompProperties_PoweredDown() =>
            compClass = typeof(HediffComp_PoweredDown);
    }

    /// <summary>
    /// State 3: downed/off. The hediff's stage pins Consciousness setMax 0.10
    /// (XML). This comp is the "will NOT self-reboot" half: severity never
    /// decays, natural healing never removes it. Removal happens only through
    /// the reboot recipe (doctor) or a shop bench job.
    /// </summary>
    public class HediffComp_PoweredDown : HediffComp
    {
        public override void CompPostTick(ref float severityAdjustment)
        {
            severityAdjustment = 0f;              // no decay, ever
            parent.Severity = 1f;
        }
    }
}
