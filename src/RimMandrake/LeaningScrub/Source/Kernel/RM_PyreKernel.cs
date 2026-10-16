// Verse-free kernel of the calling-pyre (RM_CallingPyre.cs): which belief allows the rite, and how big it burns and how many
// giants it calls. SelfTest/LeaningScrubTonightCheck.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
//
// Owner rulings: Q7 (card 2026-10-15, "Ritual plus all three beliefs": forbidden, last rite, venerated) and N3 (card, FINAL:
// "Only fire- and ritual-themed ones" offer the precept). Numbers are PROVISIONAL (owner ruling 2026-10-03).
using System;

namespace RimMandrake.LeaningScrub
{
    public static class RM_PyreKernel
    {
        public const int BeliefNone = 0;
        public const int BeliefForbidden = 1;
        public const int BeliefLastRite = 2;
        public const int BeliefVenerated = 3;

        public const string Ok = null;
        public const string ReasonOff = "off";
        public const string ReasonNoBelief = "nobelief";
        public const string ReasonForbidden = "forbidden";
        public const string ReasonNoEnemies = "noenemies";

        // Forbidden never; last rite only with enemies on the map; venerated any time. An ideoligion that holds the ritual but
        // no calling-pyre belief (edited by hand) is refused: the belief is what says when the herds may be called.
        public static string Gate(bool featureOn, int belief, int hostilesOnMap)
        {
            if (!featureOn) return ReasonOff;
            switch (belief)
            {
                case BeliefForbidden: return ReasonForbidden;
                case BeliefLastRite: return hostilesOnMap > 0 ? Ok : ReasonNoEnemies;
                case BeliefVenerated: return Ok;
                default: return ReasonNoBelief;
            }
        }

        private static int Tier(int outcomeIndex, int tiers)
        {
            return Math.Max(0, Math.Min(tiers - 1, outcomeIndex));
        }

        // Fires set in the colony's own fields, by outcome (0 worst .. 3 best). PROVISIONAL. Every tier clears the
        // fire-stamp threshold (5 open fires clustered), so every pyre calls the herd.
        private static readonly int[] Fires = { 6, 10, 16, 24 };

        public static int FireCount(int outcomeIndex)
        {
            return Fires[Tier(outcomeIndex, Fires.Length)];
        }

        // Giants that walk in from the map edge, by outcome. PROVISIONAL.
        public static int HerdCount(int outcomeIndex, float factor)
        {
            if (float.IsNaN(factor) || factor < 0f) factor = 0f;
            int n = (int)Math.Round((2 + Tier(outcomeIndex, 4)) * factor);
            return Math.Max(factor > 0f ? 1 : 0, Math.Min(n, 40));
        }

        // How many of the arriving giants come in enraged, falling on everyone. The worse the rite, the more of them: a
        // terrible pyre sends the whole herd raging; the best keeps three in four on the fire. PROVISIONAL.
        public static int RagingCount(int outcomeIndex, int herd)
        {
            if (herd <= 0) return 0;
            int t = Tier(outcomeIndex, 4);
            int n;
            switch (t)
            {
                case 0: n = herd; break;
                case 1: n = (herd + 1) / 2; break;
                case 2: n = (herd + 2) / 3; break;
                default: n = herd / 4; break;
            }
            return Math.Max(0, Math.Min(herd, n));
        }
    }
}
