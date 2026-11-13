using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Pyrelands
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

        /// <summary>How far from the stolen fire the ember may be carried: it goes to the farthest fuelled cell inside this.</summary>
        public int spreadDistance = PyrelandsTuning.FireHawkSpreadDistance;

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

        // The last ember drop, for the live probe (jawa/comp_read): where, when, and whether a fire took. A drop up to eighteen cells
        // past a ragged front often lands within a few cells of other flames, so "a new fire away from the blaze" cannot be told
        // from the fire map alone.
        private IntVec3 lastDropCell = IntVec3.Invalid;
        private int lastDropTick = -1;
        private bool lastDropLit;
        private int drops;
        private int dropsLit;

        // JobDriver_RUT_FireHawkCarryEmber's toils: 0 go to the fire, 1 take the ember, 2 carry it, 3 drop it. From the carry
        // toil on, the hawk holds the burning twig.
        private const int CarryToilIndex = 2;
        // Fire-coloured, so the text reads as the same thing as the glow thrown beside it.
        private static readonly Color EmberDropTextColor = new Color(1f, 0.55f, 0.15f);

        public void Notify_EmberDropped(IntVec3 cell, bool lit)
        {
            lastDropCell = cell;
            lastDropTick = Find.TickManager.TicksGame;
            lastDropLit = lit;
            drops++;
            if (lit)
            {
                dropsLit++;
                // The player's only sign of cause and effect: a new fire up to eighteen cells from the blaze, and nobody
                // to blame.
                // Thrown like RM_JobDriver_Burrow's "Burrowed!" (3.65 s before it fades), at the fire it lit.
                if (parent.Spawned)
                {
                    MoteMaker.ThrowText(cell.ToVector3Shifted(), parent.Map, "RM_EmberDroppedMote".Translate(), EmberDropTextColor, 3.65f);
                }
            }
        }

        private bool CarryingEmber
        {
            get
            {
                JobDriver driver = (parent as Pawn)?.jobs?.curDriver;
                return driver is JobDriver_RUT_FireHawkCarryEmber && driver.CurToilIndex >= CarryToilIndex;
            }
        }

        /// <summary>The inspect pane: "Carrying a burning twig" while the ember is in flight, else (after a first drop) how
        /// long ago the last one fell. Built only when the pane is open on the hawk.</summary>
        public override string CompInspectStringExtra()
        {
            if (CarryingEmber) return "RM_FireHawkCarrying".Translate().ToString();
            if (drops <= 0 || lastDropTick < 0) return null;
            return "RM_FireHawkLastDrop".Translate((Find.TickManager.TicksGame - lastDropTick).ToStringTicksToPeriod()).ToString();
        }

        public CompProperties_FireHawkSpread Props => (CompProperties_FireHawkSpread)props;

        public bool CanSortieNow =>
            RM_FurnaceKernel.SortieReady(Find.TickManager.TicksGame, lastSortieTick, PyrelandsTuning.FireHawkCooldownTicks);

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
            Scribe_Values.Look(ref lastDropCell, "lastDropCell", IntVec3.Invalid);
            Scribe_Values.Look(ref lastDropTick, "lastDropTick", -1);
            Scribe_Values.Look(ref lastDropLit, "lastDropLit", false);
            Scribe_Values.Look(ref drops, "drops", 0);
            Scribe_Values.Look(ref dropsLit, "dropsLit", 0);
        }
    }
}
