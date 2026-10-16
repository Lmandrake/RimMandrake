using RimMandrake.EnvironmentalHazards;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Contagion
{
    // The Bloody Mess (RM_BloodyMess, the genome host) bursts into acid when it dies, like the red goo it was ported
    // from -- EXCEPT when it dies giving birth to the organs or limb it grew from a colonist's genome, because that
    // burst would burn the batch it just produced and the colonist standing beside it.
    // Owner by question card 2026-10-15 (Transient/phase0_twin_only_questions.md Q3): "Burst only when killed".
    //
    // The two deaths are told apart by AmoebaHostUtility.HostDyingInBirth, which is set around the one Kill call
    // that completes a gestation; Pawn.Kill runs the death action synchronously inside that call. Every other death
    // (combat, starvation, disease, execution) bursts. The burst itself is EnvironmentalHazards' scaled explosion,
    // unchanged (and still obeys that kit's own on/off and damage settings).
    //
    //   <deathAction Class="RimMandrake.EnvironmentalHazards.DeathActionProperties_ScaledExplosion">
    //     <workerClass>RimMandrake.Contagion.DeathActionWorker_RM_GenomeHostBurst</workerClass>
    //     ...
    public class DeathActionWorker_RM_GenomeHostBurst : DeathActionWorker_ScaledExplosion
    {
        public override void PawnDied(Corpse corpse, Lord prevLord)
        {
            Pawn dead = corpse?.InnerPawn;
            bool diesGivingBirth = dead != null && dead == AmoebaHostUtility.HostDyingInBirth;
            if (!RM_DraftprintKernel.HostDeathBursts(diesGivingBirth))
            {
                return;
            }
            base.PawnDied(corpse, prevLord);
        }
    }
}
