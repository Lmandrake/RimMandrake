using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §4.1: "any worn apparel / equipped weapon whose CompDeepfire.coats
    // > 0, and any RM_StatusGoodExtension-tagged def (the hook for later
    // goods; Deepfire is detected by comp, not by extension)." CompDeepfire
    // does not exist yet (piece 1, painting -- deferred to
    // DEEPFIRE_PAINT_LIVE_VERIFY_1), so THIS build ships the engine keyed
    // purely off the extension: a generic, reusable "purple engine" that is
    // genuinely inert (display score always 0, exactly the standing Mod
    // Settings rule's "all-off degrades gracefully") until either (a) a
    // future good is tagged with this extension, or (b) piece 1 ships and
    // adds a CompDeepfire branch here (a one-line addition once that comp's
    // shape exists -- not a new design question).
    public class StatusGoodExtension : DefModExtension
    {
        // 0..3, analogous to Deepfire's coat count. A def with this
        // extension always contributes this fixed level; CompDeepfire (once
        // it exists) will contribute its live coat count instead.
        public int statusLevel = 1;
    }

    public static class SumptuaryUtility
    {
        public static int DisplayScoreFor(Pawn pawn)
        {
            if (pawn == null) return 0;
            int score = 0;
            if (pawn.apparel != null)
            {
                foreach (Apparel a in pawn.apparel.WornApparel)
                {
                    score += GoodLevel(a);
                }
            }
            if (pawn.equipment?.Primary != null)
            {
                score += GoodLevel(pawn.equipment.Primary);
            }
            return UnityEngine.Mathf.Min(score, LuminousPigmentSettings.displayCap);
        }

        private static int GoodLevel(Thing t)
        {
            StatusGoodExtension ext = t.def.GetModExtension<StatusGoodExtension>();
            return ext?.statusLevel ?? 0;
        }

        // Royalty title seniority -> Ideology leader/moral-guide role ->
        // otherwise common (spec §4.1's rank judgement, cheapest first).
        public static bool IsTitled(Pawn pawn)
        {
            if (pawn?.royalty != null && pawn.royalty.AllTitlesInEffectForReading.Count > 0) return true;
            if (pawn?.Ideo != null && pawn.Ideo.GetRole(pawn) != null) return true;
            return false;
        }

        // Spec §4.1: "A colony with neither DLC has no titled pawns;
        // ranklessColoniesEnjoyIt (default on) then lets every pawn take the
        // wearer's pleasure." With the setting off and neither DLC active,
        // there is no "who else" for the engine's status comparison to mean
        // anything, so the wearer's own pleasure thought is suppressed too.
        public static bool RanklessColonyThoughtAllowed()
        {
            if (LuminousPigmentSettings.ranklessColoniesEnjoyIt) return true;
            return ModsConfig.RoyaltyActive || ModsConfig.IdeologyActive;
        }
    }
}
