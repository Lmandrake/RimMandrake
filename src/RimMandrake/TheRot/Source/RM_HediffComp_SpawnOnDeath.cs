using RimWorld;
using RimWorld.Planet;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.TheRot
{
    // Phase 0 donor retirement: replaces AlphaBehavioursAndEvents.HediffComp_TurnWhenDead and
    // HediffComp_RemoveFromMechsAndGhouls (Alpha Animals, juanosarg/AlphaAnimals 1.7 source) on RM_SwarmlingImplantation.
    //
    // RM_HediffComp_SpawnOnDeath: the host dies with the hediff above minSeverity -> count pawns of pawnKind burst
    // from the corpse (manhunter-permanent if hostile), blood filth around it, Hive_Spawn sound, corpse destroyed.
    // The burst itself is the readable sign. Differences from the donor, on purpose: pawnKind is a def reference
    // (a typo fails at load, not at the death), count is an IntRange, and a corpse that is gone or off-map is a no-op
    // instead of a NullReferenceException.
    public class RM_HediffCompProperties_SpawnOnDeath : HediffCompProperties
    {
        public PawnKindDef pawnKind;
        public IntRange count = new IntRange(1, 1);
        public float minSeverity = 0.85f;
        public bool hostile = true;
        public bool keepGender;
        public int bloodFilth = 20;

        public RM_HediffCompProperties_SpawnOnDeath()
        {
            compClass = typeof(RM_HediffComp_SpawnOnDeath);
        }

        public override System.Collections.Generic.IEnumerable<string> ConfigErrors(HediffDef parentDef)
        {
            foreach (string e in base.ConfigErrors(parentDef))
                yield return e;
            if (pawnKind == null)
                yield return "RM_HediffCompProperties_SpawnOnDeath: pawnKind is null";
            if (count.min < 0 || count.max < count.min)
                yield return "RM_HediffCompProperties_SpawnOnDeath: bad count " + count;
        }
    }

    public class RM_HediffComp_SpawnOnDeath : HediffComp
    {
        public RM_HediffCompProperties_SpawnOnDeath Props => (RM_HediffCompProperties_SpawnOnDeath)props;

        public override void Notify_PawnDied(DamageInfo? dinfo, Hediff culprit = null)
        {
            base.Notify_PawnDied(dinfo, culprit);
            if (Props.pawnKind == null || parent.Severity <= Props.minSeverity)
                return;
            Corpse corpse = Pawn.Corpse;
            Map map = corpse?.MapHeld;
            if (corpse == null || corpse.Destroyed || map == null)
                return;
            IntVec3 at = corpse.PositionHeld;

            Faction faction = Props.hostile ? Find.FactionManager.FirstFactionOfDef(FactionDefOf.AncientsHostile) : null;
            int n = Props.count.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                Gender? gender = Props.keepGender && Props.pawnKind.RaceProps.hasGenders ? Pawn.gender : (Gender?)null;
                Pawn spawn = PawnGenerator.GeneratePawn(new PawnGenerationRequest(
                    Props.pawnKind, faction, PawnGenerationContext.NonPlayer,
                    forceGenerateNewPawn: true, canGeneratePawnRelations: false, colonistRelationChanceFactor: 0f,
                    allowAddictions: false, fixedGender: gender));
                if (!PawnUtility.TrySpawnHatchedOrBornPawn(spawn, corpse))
                {
                    Find.WorldPawns.PassToWorld(spawn, PawnDiscardDecideMode.Discard);
                    continue;
                }
                if (Props.hostile)
                    spawn.mindState.mentalStateHandler.TryStartMentalState(MentalStateDefOf.ManhunterPermanent, null, true);
            }

            for (int i = 0; i < Props.bloodFilth; i++)
            {
                if (CellFinder.TryFindRandomReachableNearbyCell(at, map, 2, TraverseParms.For(TraverseMode.NoPassClosedDoors), null, null, out IntVec3 c))
                    FilthMaker.TryMakeFilth(c, map, ThingDefOf.Filth_Blood);
            }
            SoundDef burst = DefDatabase<SoundDef>.GetNamedSilentFail("Hive_Spawn");
            burst?.PlayOneShot(new TargetInfo(at, map));
            corpse.Destroy();
        }
    }

    // Replaces AlphaBehavioursAndEvents.HediffComp_RemoveFromMechsAndGhouls. The donor removed the hediff in
    // CompPostMake, which runs inside HediffMaker.MakeHediff BEFORE the hediff is in the set, so its RemoveHediff
    // was a no-op and AddHediff added it anyway (MEASURED 2026-10-15 RimSage: HediffMaker.MakeHediff -> PostMake,
    // HediffSet.AddDirect adds afterwards). CompShouldRemove is the vanilla removal path: the health tick drops it,
    // and it also covers a host that becomes a ghoul after infection.
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
