using Verse;
using Verse.AI;

namespace RimMandrake.RustCathedral
{
    // RUSTCATHEDRAL_RM_MOD_BUILD_1 §6: the Mod Settings toggle for the
    // absorbed cathedral roach's cleaning behaviour. Wrapped around
    // RimMandrake.CreatureBehaviors.RM_ThinkNode_EatCleanable in
    // RM_ThinkTree_CathedralRoach.xml (the RM_ copy only — the frozen
    // RUT_ThinkTree_CathedralRoach.xml twin is untouched and always on,
    // matching "carrying the world until the terminal paint"). Off: the
    // roach falls through to the tree's vanilla wander, same
    // graceful-degradation floor RM_ThinkNode_EatCleanable itself uses when
    // nothing cleanable is in range.
    public class RM_ThinkNode_ConditionalRoachCleaningEnabled : ThinkNode_Conditional
    {
        protected override bool Satisfied(Pawn pawn)
        {
            return RM_RustCathedralSettings.roachCleaningEnabled;
        }
    }
}
