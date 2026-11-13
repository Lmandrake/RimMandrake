using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Pits
{
    /// <summary>The cover deck's flood-fill, Verse-free so the SelfTest drives what the game runs.</summary>
    public static class RM_PitDeckMath
    {
        /// <summary>Owner 2026-11-12: "please ensure they can only be placed where there are two sides adjacent to solid
        /// ground, to avoid "covered pit bridges" being built". A cover rests on solid ground on at least this many of its
        /// four sides (PlaceWorker_PitCoverOnSuperdeep).</summary>
        public const int MinBankSides = 2;

        /// <summary>How many of the four sides (direction 0..3) <paramref name="solidOn"/> says are solid ground.</summary>
        public static int BankSides(Func<int, bool> solidOn)
        {
            int n = 0;
            for (int d = 0; d < 4; d++)
            {
                if (solidOn(d))
                {
                    n++;
                }
            }
            return n;
        }

        public static bool RestsOnBanks(Func<int, bool> solidOn) => BankSides(solidOn) >= MinBankSides;

        /// <summary>Every cover connected to <paramref name="start"/>, breadth first in direction order. No size cap: a cap cut
        /// big decks into partial ones that each found a different lead and collapsed in pieces (COVER_DECK_TUNE_QUADRATIC_CENSUS,
        /// GPT C4-F6). Null as soon as a cover meets <paramref name="stopAt"/>.</summary>
        public static List<TCover> Flood<TCell, TCover>(TCell start, Func<TCell, TCover> coverAt, Func<TCell, int, TCell> step, int directions,
            Func<TCover, bool> stopAt = null) where TCover : class
        {
            var deck = new List<TCover>();
            var seen = new HashSet<TCell> { start };
            var open = new Queue<TCell>();
            open.Enqueue(start);
            while (open.Count > 0)
            {
                TCell c = open.Dequeue();
                TCover cover = coverAt(c);
                if (cover == null)
                {
                    continue;
                }
                if (stopAt != null && stopAt(cover))
                {
                    return null;
                }
                deck.Add(cover);
                for (int i = 0; i < directions; i++)
                {
                    TCell n = step(c, i);
                    if (seen.Add(n) && coverAt(n) != null)
                    {
                        open.Enqueue(n);
                    }
                }
            }
            return deck;
        }
    }
}
