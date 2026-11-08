using Verse;

namespace RimMandrake.Patches
{
    // The pawn half of RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES (math and measurements: SouthDrawsFrontKernel.cs).
    // Pawn_DrawTracker.DrawPos calls this where it read SeededYOffset (SouthDrawsFrontPatches routes the call). DrawPos is
    // read many times a frame per pawn: field reads and arithmetic only, no allocation.
    public static class SouthDrawsFrontPawn
    {
        public static float OrderedYOffset(Pawn_DrawTracker tracker, Pawn pawn)
        {
            if (!RM_PatchesSettings.southDrawsFront || pawn == null)
                return tracker.SeededYOffset;
            Map map = pawn.Map;
            if (map == null)
                return tracker.SeededYOffset;   // carried, in a container or a caravan: vanilla
            float flight = pawn.flight != null && pawn.flight.Flying ? pawn.flight.PositionOffsetFactor : 0f;
            // The tweened position is where the pawn stands (DrawPos computes it first); jitter, lean and the flying
            // lift move the picture, never the order.
            return SouthDrawsFrontKernel.PawnYOffset(tracker.tweener.TweenedPos.z, map.Size.z, flight);
        }
    }
}
