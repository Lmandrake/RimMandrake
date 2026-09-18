using System.Collections.Generic;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F9 spike. Ant theft-hauling: "Ant raids haul
    // thornbugs away ALIVE — theft, not slaughter — so every loss is a
    // recoverable quest" (the_fever_wood.md §4). Card 1 (hidden plumbing
    // factions) is RULED FINE 2026-09-12 — the §4 war, its lords and this
    // theft job all stand per that ruling.
    //
    // Engine route CONFIRMED, one correction found: RimWorld/
    // JobDriver_Kidnap.cs is exactly the shape the spec named — it
    // subclasses JobDriver_TakeAndExitMap (RimWorld/
    // JobDriver_TakeAndExitMap.cs) and adds one FailOn: "Takee == null ||
    // (!Takee.Downed && Takee.Awake())" — reused verbatim below, since a
    // thornbug being hauled off must likewise be down or asleep, not
    // fighting back. CORRECTION: the spec's cited victim-finder,
    // RimWorld/KidnapAIUtility.cs's TryFindGoodKidnapVictim, filters
    // `pawn.RaceProps.Humanlike` at its own validator (line ~20) — it
    // cannot be reused for an animal target as written. Finding a
    // thornbug to haul now uses RM_HaulVictimAIUtility.TryFindGoodHaulVictim
    // (WIRED this pass) — the same predicate shape generalized off a
    // caller-supplied species filter instead of a hardcoded Humanlike
    // check; this is Lord/JobGiver work for the ants' LordJob, not this
    // JobDriver.
    //
    // SPIKE SCOPE: this proves the driver itself compiles and reuses the
    // confirmed FailOn/toil shape. NOT done here: the ants' hidden
    // FactionDef XML (blocked on the roster pass — Ants/Feralisks have no
    // PawnKindDef yet, so a FactionDef's pawnGroupMakers would have to
    // guess a defName), the LordJob/LordToil wiring that assigns this job
    // (crib RimWorld/LordToil_KidnapCover.cs's shape, generalized off
    // DutyDefOf.Kidnap to a Fever Wood-specific duty) — RM_JobDriver_
    // StunVictim (WIRED this pass) is the "unclamp stun" that downs a
    // victim non-lethally before this job can legally target it, but
    // nothing assigns either job yet — and the raid-back QuestScriptDef
    // (spec: "may trail by one build").
    public class RUT_HaulPawnAndExit : JobDriver_TakeAndExitMap
    {
        protected Pawn Takee => (Pawn)base.Item;

        public override string GetReport()
        {
            if (Takee == null)
            {
                return base.GetReport();
            }
            return JobUtility.GetResolvedJobReport(JobDefOf.Kidnap.reportString, Takee);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOn(() => Takee == null || (!Takee.Downed && Takee.Awake()));
            foreach (Toil item in base.MakeNewToils())
            {
                yield return item;
            }
        }
    }
}
