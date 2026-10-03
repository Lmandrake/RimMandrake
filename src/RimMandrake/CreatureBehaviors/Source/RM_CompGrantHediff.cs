using RimWorld;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>ROT_WOUND_SHARING_WIRING_1: gives a pawn a permanent racial hediff when it spawns (so a HediffComp such as
    /// RM_HediffComp_KinMending has a carrier), and shows one inspect line saying what the wiring does.</summary>
    public class CompProperties_GrantHediff : CompProperties
    {
        public HediffDef hediff;
        public string inspectLine;

        public CompProperties_GrantHediff()
        {
            compClass = typeof(RM_CompGrantHediff);
        }
    }

    public class RM_CompGrantHediff : ThingComp
    {
        private CompProperties_GrantHediff Props => (CompProperties_GrantHediff)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (Props.hediff == null || !(parent is Pawn pawn) || pawn.health == null)
            {
                return;
            }
            if (pawn.health.hediffSet.GetFirstHediffOfDef(Props.hediff) == null)
            {
                pawn.health.AddHediff(Props.hediff);
            }
        }

        public override string CompInspectStringExtra()
        {
            return Props.inspectLine.NullOrEmpty() ? null : Props.inspectLine;
        }
    }
}
