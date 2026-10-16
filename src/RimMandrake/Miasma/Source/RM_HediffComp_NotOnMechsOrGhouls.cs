using Verse;

namespace RimMandrake.Miasma
{
    // Phase 0 donor retirement: replaces AlphaBehavioursAndEvents.HediffComp_RemoveFromMechsAndGhouls on
    // RM_LockJawDisease. Same class lives in RimMandrake.TheRot (Miasma does not depend on TheRot or
    // CreatureBehaviors, and a shared linked file would put one full type name in two assemblies).
    // The donor removed the hediff in CompPostMake, which runs inside HediffMaker.MakeHediff BEFORE the hediff is in
    // the set, so its RemoveHediff was a no-op (MEASURED 2026-10-15 RimSage). CompShouldRemove is the vanilla removal
    // path: the health tick drops it, and it also covers a host that becomes a ghoul after infection.
    public class RM_HediffCompProperties_NotOnMechsOrGhouls : HediffCompProperties
    {
        public RM_HediffCompProperties_NotOnMechsOrGhouls()
        {
            compClass = typeof(RM_HediffComp_NotOnMechsOrGhouls);
        }
    }

    public class RM_HediffComp_NotOnMechsOrGhouls : HediffComp
    {
        public override bool CompShouldRemove =>
            Pawn != null && (Pawn.RaceProps.IsMechanoid || Pawn.IsGhoul);
    }
}
