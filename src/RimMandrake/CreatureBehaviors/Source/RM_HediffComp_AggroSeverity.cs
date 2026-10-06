using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>GREENTIDE_THURROCK_HERD_BUILD_1 spec §6: holds a hediff's severity at one value while its pawn is in an
    /// aggro mental state (manhunter, berserk: Pawn.InAggroMentalState) and another value otherwise. A stage, or a
    /// second comp gated by its own minSeverity, can then key off "provoked" without new AI. Generic: names no race.
    /// The thurrock uses it so a second HediffComp_PeriodicAreaAttack (minSeverity 0.9, buildings only) fires only
    /// while it is provoked.</summary>
    public class RM_HediffCompProperties_AggroSeverity : HediffCompProperties
    {
        public float restSeverity = 0.5f;
        public float aggroSeverity = 1f;

        public RM_HediffCompProperties_AggroSeverity()
        {
            compClass = typeof(RM_HediffComp_AggroSeverity);
        }
    }

    public class RM_HediffComp_AggroSeverity : HediffComp
    {
        private RM_HediffCompProperties_AggroSeverity Props => (RM_HediffCompProperties_AggroSeverity)props;

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            base.CompPostTickInterval(ref severityAdjustment, delta);
            Pawn pawn = Pawn;
            if (pawn == null || pawn.Dead)
            {
                return;
            }
            float target = pawn.InAggroMentalState ? Props.aggroSeverity : Props.restSeverity;
            if (parent.Severity != target)
            {
                parent.Severity = target;
            }
        }
    }
}
