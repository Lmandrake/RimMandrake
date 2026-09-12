using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Sarlacc
{
    public class CompProperties_SarlaccAnchoredMouth : CompProperties
    {
        /// <summary>Mean time between strikes, in days — "it strikes rarely, and only to tithe" (draft §2.2/§3).</summary>
        public float mtbStrikeDays = 20f;

        public float strikeDamageMin = 40f;
        public float strikeDamageMax = 70f;

        public CompProperties_SarlaccAnchoredMouth()
        {
            compClass = typeof(CompSarlaccAnchoredMouth);
        }
    }

    /// <summary>
    /// Stage II's rare tithe-strike: an anchored sarlacc does not chase (draft §2.2), it
    /// only reaches whoever stands beside its mouth. Runs on the rare tick (250 ticks).
    /// </summary>
    public class CompSarlaccAnchoredMouth : ThingComp
    {
        public CompProperties_SarlaccAnchoredMouth Props => (CompProperties_SarlaccAnchoredMouth)props;

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!RSW_SarlaccSettings.anchoredTitheEnabled)
            {
                return;
            }
            if (!parent.Spawned)
            {
                return;
            }
            if (!Rand.MTBEventOccurs(Props.mtbStrikeDays, GenDate.TicksPerDay, 250f))
            {
                return;
            }

            Pawn target = null;
            foreach (IntVec3 cell in GenAdj.CellsAdjacent8Way(parent))
            {
                if (!cell.InBounds(parent.Map))
                {
                    continue;
                }
                foreach (Thing thing in cell.GetThingList(parent.Map))
                {
                    if (thing is Pawn pawn && !pawn.Downed && !pawn.Dead)
                    {
                        target = pawn;
                        break;
                    }
                }
                if (target != null)
                {
                    break;
                }
            }
            if (target == null)
            {
                return;
            }

            float amount = Rand.Range(Props.strikeDamageMin, Props.strikeDamageMax);
            DamageInfo dinfo = new DamageInfo(DamageDefOf.Bite, amount, 0f, -1f, parent);
            target.TakeDamage(dinfo);
            Messages.Message(
                "The anchored sarlacc's mouth struck " + target.LabelShort + ".",
                target,
                MessageTypeDefOf.NegativeEvent);
        }
    }
}
