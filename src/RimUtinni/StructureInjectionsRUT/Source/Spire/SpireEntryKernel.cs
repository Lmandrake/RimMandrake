using System.Collections.Generic;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // SPIRE_DUNGEONS_MERGE_DARK_TOWER: the rule behind the Spire's seal, with no engine types so the
    // selftest compiles this exact file. "Trust" is the arc's conduct-stage at VOUCHED or later
    // (design/Jawa/cathedral_concealment_arc_spec.md section 1: 0 WARY, 1 TOLERATED, 2 VOUCHED).
    public static class SpireEntryKernel
    {
        public const int VouchedStage = 2;

        public static bool TrustStands(int stage)
        {
            return stage >= VouchedStage;
        }

        // Mod Setting off: the seal opens as the Spire is built, the way the flesh seal does.
        public static bool SealOpens(bool gated, int stage)
        {
            return !gated || TrustStands(stage);
        }

        // A Cathedral map loaded right now speaks for the stage, up or down (a dark flip drops it);
        // with none loaded the last reading stands. Several maps: the warmest, since trust is the
        // Cathedral's one relationship with the clan and a map it has not been pushed to reads low.
        public static int Fold(int recorded, IEnumerable<int> observed)
        {
            int best = -1;
            foreach (int stage in observed)
            {
                if (stage > best)
                {
                    best = stage;
                }
            }
            return best < 0 ? recorded : best;
        }
    }
}
