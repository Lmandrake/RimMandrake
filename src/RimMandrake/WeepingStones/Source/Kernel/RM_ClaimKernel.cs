// Verse-free kernel of the condenser quests' exclusive claim (RM_QuestPart_CondenserClaim / RM_CondenserQuestUtil) and
// the faction-slot resolution (RM_FactionSlotDef.Resolve). The quest classes call these with the same expressions;
// SelfTest/WeepingStonesFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;
using System.Linq;

namespace RimMandrake.WeepingStones
{
    public enum RM_FactionSlotFallback : byte { Collector, Settlers, Hunters }

    public struct FactionInfo
    {
        public int id;
        public string defName;
        public bool isPlayer, defeated, temporary, hidden, humanlike, hostile, permanentEnemy;
        public int techLevel;     // (int)TechLevel
        public int goodwill;
    }

    public static class RM_ClaimKernel
    {
        // ---- the claim --------------------------------------------------------------------------
        // True while the claiming quest exists and is not historical; otherwise the claim is released (newClaim = -1).
        public static bool ClaimStillHeld(int claimQuestId, bool claimQuestExists, bool claimQuestHistorical, out int newClaim)
        {
            newClaim = claimQuestId;
            if (claimQuestId < 0) return false;
            if (claimQuestExists && !claimQuestHistorical) return true;
            newClaim = -1;
            return false;
        }

        public static bool OffersOpen(bool condenserEnabled, bool questsEnabled, bool hasWorld, bool ended, bool questsSettled, bool claimHeld)
        {
            if (!condenserEnabled || !questsEnabled) return false;
            if (!hasWorld || ended || questsSettled) return false;
            return !claimHeld;
        }

        // A not-yet-accepted offer withdraws when the crab is gone or the matter is taken.
        public static bool Withdraws(bool crabGone, bool hasWorld, bool ended, bool questsSettled, bool claimHeld, int claimQuestId, int myQuestId)
        {
            bool taken = !hasWorld || ended || questsSettled || (claimHeld && claimQuestId != myQuestId);
            return crabGone || taken;
        }

        // Accepting a claim quest withdraws every OTHER offer that is still unaccepted, at once (not at the next 250-tick
        // poll), so two offers cannot both be accepted inside one polling window.
        public static bool RivalWithdrawsOnAccept(bool otherIsClaimQuest, bool otherNotYetAccepted, int otherQuestId, int acceptedQuestId)
        {
            return otherIsClaimQuest && otherNotYetAccepted && otherQuestId != acceptedQuestId;
        }

        // Cleanup: release my claim; a success settles the matter for the world.
        public static void Cleanup(ref int claimQuestId, ref bool questsSettled, int myQuestId, bool endedSuccess)
        {
            if (claimQuestId == myQuestId) claimQuestId = -1;
            if (endedSuccess) questsSettled = true;
        }

        // ---- the faction slot -------------------------------------------------------------------
        public static bool Usable(FactionInfo f, int excludeId, bool wantsHostile)
        {
            if (f.isPlayer || f.defeated || f.temporary || f.hidden || !f.humanlike) return false;
            if (f.id == excludeId) return false;
            return f.hostile == wantsHostile;
        }

        public static FactionInfo? Resolve(IList<FactionInfo> factions, IList<string> preferred, RM_FactionSlotFallback fallback, int excludeId)
        {
            bool wantsHostile = fallback == RM_FactionSlotFallback.Hunters;
            List<FactionInfo> all = factions.Where(f => Usable(f, excludeId, wantsHostile)).ToList();
            if (all.Count == 0) return null;
            for (int i = 0; i < preferred.Count; i++)
            {
                string want = preferred[i];
                IEnumerable<FactionInfo> hits = all.Where(f => f.defName == want);
                if (hits.Any()) return hits.OrderByDescending(f => f.goodwill).First();
            }
            switch (fallback)
            {
                case RM_FactionSlotFallback.Collector:
                    return Pick(all.Where(f => !f.permanentEnemy).OrderByDescending(f => f.techLevel).ThenByDescending(f => f.goodwill));
                case RM_FactionSlotFallback.Hunters:
                    return Pick(all.OrderByDescending(f => f.permanentEnemy).ThenByDescending(f => f.techLevel));
                default:
                    return Pick(all.Where(f => !f.permanentEnemy).OrderBy(f => f.techLevel > IndustrialTech).ThenByDescending(f => f.goodwill));
            }
        }

        public const int IndustrialTech = 4;   // (int)TechLevel.Industrial

        private static FactionInfo? Pick(IEnumerable<FactionInfo> ordered)
        {
            foreach (FactionInfo f in ordered) return f;
            return null;
        }
    }
}
