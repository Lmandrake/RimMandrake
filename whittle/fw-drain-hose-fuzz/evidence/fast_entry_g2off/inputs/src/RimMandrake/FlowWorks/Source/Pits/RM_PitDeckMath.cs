using System;
using System.Collections.Generic;

namespace RimMandrake.FlowWorks.Pits
{
    /// <summary>The cover deck's flood-fill, Verse-free so the SelfTest drives what the game runs.</summary>
    public static class RM_PitDeckMath
    {
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
