using Verse;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 3 — the fire-hawk's twig, as ruled in
    /// RUT_ruled_commissions_wave2.md §7c.
    ///
    /// The comp itself holds no behaviour: it is the species marker, the tuning
    /// carrier and the cooldown clock. The behaviour is
    /// JobGiver_RUT_FireHawkCarryEmber (which decides) and
    /// JobDriver_RUT_FireHawkCarryEmber (which flies it). Splitting it this way is
    /// what lets the think-tree insertion be species-agnostic — the job-giver
    /// gates on "does this pawn have the comp", so a second twig-carrier needs one
    /// XML node and no C#.
    ///
    /// 🔴 THE COOLDOWN IS NOT A NICETY. The Pyrelands is ruled to be always
    /// burning; an igniter with no cooldown on a map that always has a flame to
    /// steal is a fire timer. The cooldown is charged when the sortie STARTS, not
    /// when it succeeds, so a hawk that fails to find a lawful cell still pays.
    /// </summary>
    public class CompProperties_FireHawkSpread : CompProperties
    {
        /// <summary>How far the hawk looks for a fire to steal from. There is no
        /// behaviour at all without one — the spread-only law (§7c, RATIFIED
        /// owner 2026-09-10).</summary>
        public float scanRadius = PyrelandsTuning.FireHawkScanRadius;

        /// <summary>How many cells beyond the stolen fire the ember is carried.</summary>
        public int spreadDistance = PyrelandsTuning.FireHawkSpreadDistance;

        public int cooldownTicks = PyrelandsTuning.FireHawkCooldownTicks;

        /// <summary>A twig, not a bomb.</summary>
        public float startFireSize = PyrelandsTuning.SmoulderFireSize;

        public CompProperties_FireHawkSpread()
        {
            compClass = typeof(CompFireHawkSpread);
        }
    }

    public class CompFireHawkSpread : ThingComp
    {
        private int lastSortieTick = -99999;

        public CompProperties_FireHawkSpread Props => (CompProperties_FireHawkSpread)props;

        public bool CanSortieNow =>
            Find.TickManager.TicksGame - lastSortieTick >= PyrelandsMechanicsSettings.fireHawkCooldownTicks;

        /// <summary>Called by the job-giver the moment the job is handed out, so
        /// an aborted or failed sortie costs the same cooldown a successful one
        /// does.</summary>
        public void Notify_SortieStarted()
        {
            lastSortieTick = Find.TickManager.TicksGame;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref lastSortieTick, "lastSortieTick", -99999);
        }
    }
}
