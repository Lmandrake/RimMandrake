// COVER_SCAN_TAME_QUADRATIC_ID_MINIMA: the cover trigger's scan on a deck with many local id minima. Every minimum used to walk
// the whole deck before it could say it was not the lead. Production RM_PitDeckMath.Flood on a fake grid; the wiring is pinned below.
using System;
using System.Collections.Generic;
using System.IO;
using RimMandrake.FlowWorks.Pits;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class PitDeckChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private sealed class Cov
        {
            public int id, cell;
        }

        private sealed class Deck
        {
            public int w, h;
            public Cov[] covers;
            public long looks;
            public Cov At(int c)
            {
                looks++;
                return c < 0 ? null : covers[c];
            }
            public int Step(int c, int d)
            {
                int x = c % w, z = c / w;
                if (d == 0) return z + 1 < h ? c + w : -1;
                if (d == 1) return x + 1 < w ? c + 1 : -1;
                if (d == 2) return z > 0 ? c - w : -1;
                return x > 0 ? c - 1 : -1;
            }
            public List<Cov> Full(int start) => RM_PitDeckMath.Flood<int, Cov>(start, At, Step, 4);
            public List<Cov> IfLead(int start)
            {
                int id = covers[start].id;
                return RM_PitDeckMath.Flood<int, Cov>(start, At, Step, 4, c => c.id < id);
            }
            // One scan of the trigger: the cardinal cheap test, then the flood from each local minimum.
            public long Scan(bool early, out int leads)
            {
                looks = 0;
                leads = 0;
                for (int c = 0; c < covers.Length; c++)
                {
                    bool minimum = true;
                    for (int d = 0; d < 4; d++)
                    {
                        Cov n = At(Step(c, d));
                        if (n != null && n.id < covers[c].id) minimum = false;
                    }
                    if (!minimum) continue;
                    if (early)
                    {
                        if (IfLead(c) != null) leads++;
                    }
                    else
                    {
                        bool lead = true;
                        foreach (Cov k in Full(c)) if (k.id < covers[c].id) lead = false;
                        if (lead) leads++;
                    }
                }
                return looks;
            }
        }

        private static Deck Make(int w, int h, Func<int, int> id)
        {
            var d = new Deck { w = w, h = h, covers = new Cov[w * h] };
            for (int c = 0; c < w * h; c++) d.covers[c] = new Cov { id = id(c), cell = c };
            return d;
        }

        private static Deck Checker(int w)
        {
            // Every black cell is a local minimum, the shape of a deck built in two passes.
            int half = (w * w + 1) / 2;
            int[] ids = new int[w * w];
            int black = 0, white = half;
            for (int c = 0; c < w * w; c++) ids[c] = ((c % w) + (c / w)) % 2 == 0 ? black++ : white++;
            return Make(w, w, c => ids[c]);
        }

        private static Deck Shuffled(int w, int seed)
        {
            int[] ids = new int[w * w];
            for (int c = 0; c < ids.Length; c++) ids[c] = c;
            var rng = new Random(seed);
            for (int c = ids.Length - 1; c > 0; c--)
            {
                int o = rng.Next(c + 1);
                int t = ids[c]; ids[c] = ids[o]; ids[o] = t;
            }
            return Make(w, w, c => ids[c]);
        }

        private static Deck BitReversedStrip(int bits)
        {
            int n = 1 << bits;
            return Make(n, 1, c =>
            {
                int r = 0;
                for (int b = 0; b < bits; b++) if ((c >> b & 1) != 0) r |= 1 << (bits - 1 - b);
                return r;
            });
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("PitDeck_many_id_minima_scan_stays_near_linear", () =>
            {
                Action<string, Deck, Deck> grows = (name, small, big) =>
                {
                    long s = small.Scan(true, out int ls), b = big.Scan(true, out int lb), old = big.Scan(false, out int lo);
                    Assert(ls == 1 && lb == 1 && lo == 1, name + ": one lead on a deck, got " + ls + "," + lb + "," + lo);
                    double perCoverSmall = (double)s / small.covers.Length, perCover = (double)b / big.covers.Length;
                    Assert(perCover < perCoverSmall * 1.6, name + ": cost per cover grows with the deck: " + perCoverSmall + " -> " + perCover + " looks");
                    Assert(old > b * 8, name + ": the walk-the-whole-deck form costs far more, or this measures nothing: " + old + " vs " + b);
                };
                grows("checkerboard", Checker(20), Checker(40));
                grows("shuffled", Shuffled(20, 11), Shuffled(40, 11));
                grows("bit-reversed corridor", BitReversedStrip(9), BitReversedStrip(11));
            });

            Case("PitDeck_lead_and_cell_list_are_unchanged", () =>
            {
                foreach (int seed in new[] { 1, 2, 3, 4, 5 })
                {
                    Deck d = Shuffled(13, seed);
                    int leadCell = -1;
                    for (int c = 0; c < d.covers.Length; c++) if (d.covers[c].id == 0) leadCell = c;
                    for (int c = 0; c < d.covers.Length; c++)
                    {
                        List<Cov> got = d.IfLead(c), full = d.Full(c);
                        Assert(full.Count == d.covers.Length, "the full flood finds every cover");
                        if (c != leadCell)
                        {
                            Assert(got == null, "a cover that is not the lowest id never comes back as lead");
                            continue;
                        }
                        Assert(got != null && got.Count == full.Count, "the lead gets the whole deck");
                        for (int i = 0; i < got.Count; i++) Assert(ReferenceEquals(got[i], full[i]), "in the same order as the full flood");
                    }
                }
                // Two separated decks: each has its own lead, and a hole stops the flood.
                Deck split = Make(5, 1, c => c == 2 ? -1 : 10 - c);
                split.covers[2] = null;
                Assert(split.Full(0).Count == 2 && split.IfLead(1) != null && split.IfLead(0) == null, "a gap splits the deck");
                Assert(split.IfLead(4) != null && split.IfLead(3) == null, "the far deck has its own lead");
            });

            Case("PitDeck_the_trigger_uses_the_early_exit", () =>
            {
                string trigger = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Trigger", "CompPitCoverTrigger.cs"));
                string cover = RiverSwitchFlipChecks.Src(Path.Combine("Pits", "Building_PitCover.cs"));
                Assert(trigger.Contains("List<Building_PitCover> deck = RM_PitCoverUtility.DeckIfLead(self);"), "RunScan floods through DeckIfLead");
                Assert(trigger.Contains("if (deck == null) return;"), "and stops when it is not the lead");
                Assert(cover.Contains("c => c.thingIDNumber < id);"), "DeckIfLead stops at a lower id");
                Assert(cover.Contains("return RM_PitDeckMath.Flood(start.Position, c => CoverAt(map, c), (c, d) => c + GenAdj.CardinalDirections[d], 4);"), "Deck is the same flood with no stop");
            });
        }
    }
}
