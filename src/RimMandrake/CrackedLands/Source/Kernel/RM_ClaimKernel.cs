using System;
using System.Collections.Generic;

namespace RimMandrake.CrackedLands
{
    // CRACKEDLANDS_SALVAGE_CLAIM_CREW_1: the Verse-free rules of the floodline claim. The owner's cards: the rival crew
    // TRADES (2026-10-08), is an existing scavenger-type faction, and comes on a chance per flood, about 1 in 3 (2026-10-09).
    public static class RM_ClaimKernel
    {
        // TUNED: the crew walks in a quarter to three quarters of a day after the recede: the player gets a head start.
        public const int ArrivalDelayMinTicks = 15000;
        public const int ArrivalDelayMaxTicks = 45000;
        // TUNED: a short-lived shop, about a day on the claim.
        public const int StayTicks = 60000;
        // TUNED: digging one piece out of the mud takes half an in-game hour, so the race can be won by either side.
        public const int DigTicks = 1250;
        // TUNED: once hostile they strip the claim for at most a third of a day, then run.
        public const int StealCapTicks = 20000;
        // TUNED: a crew of two to four.
        public const int CrewMin = 2;
        public const int CrewMax = 4;

        /// <summary>Whether this recede draws the crew. <paramref name="roll"/> is uniform on [0,1).</summary>
        public static bool CrewComes(bool enabled, double roll, float chance, int openClaims)
        {
            return enabled && openClaims > 0 && roll < chance;
        }

        /// <summary>A piece is OPEN (its stake stands, the crew may race for it) while it lies unclaimed where the mud
        /// exposed it. Anything allowed, ordered hauled or moved is claimed. Same test as RM_CanyonRulesKernel.SalvageTaken.</summary>
        public static bool Open(bool spawned, bool sameMap, bool atItsCell, bool stillUnclaimed)
        {
            return RM_CanyonRulesKernel.SalvageTaken(spawned, sameMap, atItsCell, stillUnclaimed);
        }

        /// <summary>Hostile, the crew no longer respects a claim: anything still lying where it was exposed is theirs.</summary>
        public static bool Stealable(bool spawned, bool sameMap, bool atItsCell)
        {
            return spawned && sameMap && atItsCell;
        }

        /// <summary>The first name in <paramref name="order"/> with an eligible faction, or null: the crew stays away.</summary>
        public static string PickFaction(IList<string> order, Func<string, bool> eligible)
        {
            if (order == null)
            {
                return null;
            }
            for (int i = 0; i < order.Count; i++)
            {
                if (eligible(order[i]))
                {
                    return order[i];
                }
            }
            return null;
        }
    }
}
