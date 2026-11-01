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

        // Each reading is (map id, stage); -1 is a map off Cathedral ground and never wins. The warmest
        // loaded Cathedral map raises the reading, since trust is the Cathedral's one relationship with
        // the clan. Only the map that set the reading can lower it (a dark flip): a fresh Cathedral map
        // starts at 0 and has not been told, so it must not erase trust earned on a map now gone.
        // With no such map loaded the last reading stands.
        public static int Fold(int recorded, ref int sourceMap, IEnumerable<KeyValuePair<int, int>> observed)
        {
            int best = -1;
            int bestMap = -1;
            bool sourceSeen = false;
            foreach (KeyValuePair<int, int> reading in observed)
            {
                sourceSeen |= reading.Key == sourceMap;
                if (reading.Value > best || (reading.Value == best && reading.Key == sourceMap))
                {
                    best = reading.Value;
                    bestMap = reading.Key;
                }
            }
            if (best < 0 || !(sourceSeen || best > recorded))
            {
                return recorded;
            }
            sourceMap = bestMap;
            return best;
        }
    }
}
