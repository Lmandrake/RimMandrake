using Verse;

namespace RimMandrake.TitanicCreatures
{
    /// <summary>
    /// Carries no state and runs no per-tick work (perf rail - see the
    /// decompile's ⚠️ on Large Pawns' one genuine per-tick cost). It exists only
    /// as the thing Patch_Thing_Position_Wake can find with TryGetComp, so the
    /// wake fires exactly once per cell a tiered pawn actually enters, driven by
    /// the same Thing.Position assignment vanilla's own PathFollower already
    /// makes (Verse/AI/Pawn_PathFollower.cs TryEnterNextPathCell:
    /// "this.pawn.Position = nextCell;") - event-driven, not a scan.
    /// </summary>
    public class CompTitanicWake : ThingComp
    {
        public void Notify_EnteredCell()
        {
            Pawn pawn = parent as Pawn;
            // TITAN_WAKE_FIXES_1 (B3.8): no ground wake while airborne (1.6 Pawn.Flying).
            if (pawn == null || !pawn.Spawned || pawn.Map == null || pawn.Flying)
            {
                return;
            }
            TitanicTier tier = TitanicTierUtility.GetTier(pawn);
            if (tier == TitanicTier.None)
            {
                return;
            }
            TitanicWakeProcessor.ProcessFootprint(pawn, tier);
        }
    }
}
