// Verse-free kernel of the Grey Sea's lamp watch (RM_MapComponent_GreyLampWatch): how long each worklight has burned, and the
// watcher (half the burn clock), scrape-sign (three quarters) and giant (the full clock) responses with their per-lamp latches
// and the reset of a lamp that goes dark or is lost. The mod supplies the responses themselves. SelfTest/TerminalBiomesFuzz.cs
// compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.TerminalBiomes
{
    public sealed class LampWatchBook
    {
        public Dictionary<int, int> Lit = new Dictionary<int, int>();
        public HashSet<int> Watched = new HashSet<int>();
        public HashSet<int> Scraped = new HashSet<int>();
        public HashSet<int> Answered = new HashSet<int>();

        public static int ThresholdTicks(float burnHours) { return (int)Math.Round(burnHours * 2500f); }

        public int LitTicksOf(int id) { int v; return Lit.TryGetValue(id, out v) ? v : 0; }

        // The lamps lit right now each gain `ticks`; the responses fire at their fractions of the burn clock; a lamp that was
        // not seen (dark, unpowered, destroyed) forgets its clock and latches.
        public void Advance(IList<int> litNow, int ticks, int threshold, bool watcherOn, bool giantOn, Action<int> watch, Action<int> scrape, Func<int, bool> answer)
        {
            var seen = new HashSet<int>();
            foreach (int id in litNow)
            {
                seen.Add(id);
                int lit = LitTicksOf(id) + ticks;
                Lit[id] = lit;
                float f = lit / (float)Math.Max(1, threshold);
                if (f >= 0.5f && watcherOn) watch(id);
                if (f >= 0.75f && watcherOn && Scraped.Add(id)) scrape(id);
                if (f >= 1f && giantOn && !Answered.Contains(id) && answer(id)) Answered.Add(id);
            }
            var gone = new List<int>();
            foreach (int id in Lit.Keys) if (!seen.Contains(id)) gone.Add(id);
            foreach (int id in gone) { Lit.Remove(id); Watched.Remove(id); Scraped.Remove(id); Answered.Remove(id); }
        }
    }
}
