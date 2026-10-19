// UNDERPASS_REACH_FIX_DECK_VIEW_SAYS_NO: reachability, the pocket grid and A* agree under and beside suspension decks.
// The reach side is PRODUCTION RM_PocketGridMath (ViewDepth, UsesFloorView, ReachGridView, Label, LadderEdge, JoinedByLadders,
// ReachVetoedWhole) + RM_TrenchStrideMath; the A* side is a flood over PRODUCTION RM_CliffMaskMath.AllowedBits on the view the
// path request plans on, as RM_CliffMask.Swap and RM_TrenchStride's swap choose it (pinned at the call sites below).
// Every pawn here is one square wide (the narrow-pocket rule is CliffMaskChecks'); every ladder is lowered and usable.
// NOT proven here (live row owed): a real CanReach / A* call under a built deck in game.
using System;
using System.Collections.Generic;
using System.IO;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class UnderpassReachChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private const int Person = 2, Titan = 4;
        private const int North = 0, East = 1, South = 2, West = 3;

        private sealed class World
        {
            public int w, h;
            public byte[] climb;
            public readonly Dictionary<int, int> decks = new Dictionary<int, int>();   // cell -> deck notches (suspension, intact)
            public readonly List<(int c, int rot)> ladders = new List<(int c, int rot)>();

            public bool Passes(int i) => decks.TryGetValue(i, out int n) && RM_SpanMath.ClearsUnderpass(climb[i], n);

            public int Deepest()
            {
                int best = -1;
                foreach (KeyValuePair<int, int> d in decks)
                    if (Passes(d.Key) && d.Value > best) best = d.Value;
                return best;
            }

            /// <summary>RM_PocketGrid.EffectiveDepth(map, eng, floorView) on this world.</summary>
            public byte[] View(bool floor)
            {
                var o = new byte[w * h];
                for (int i = 0; i < o.Length; i++)
                {
                    bool decked = decks.TryGetValue(i, out int n);
                    o[i] = (byte)RM_PocketGridMath.ViewDepth(climb[i], decked, n, decked && Passes(i), floor);
                }
                return o;
            }
        }

        private sealed class Walker
        {
            public string name;
            public int x, z, k, stride;
            public bool inFloorBand;
        }

        private static World NewWorld(int w, int h) => new World { w = w, h = h, climb = new byte[w * h] };

        private static void Rect(byte[] g, int w, int x0, int z0, int rw, int rh, byte d)
        {
            for (int x = x0; x < x0 + rw; x++)
                for (int z = z0; z < z0 + rh; z++)
                    g[z * w + x] = d;
        }

        private static int Other(World wd, int c, int rot)
        {
            int x = c % wd.w + RM_LadderWallMath.FX[rot], z = c / wd.w + RM_LadderWallMath.FZ[rot];
            return x < 0 || z < 0 || x >= wd.w || z >= wd.h ? -1 : z * wd.w + x;
        }

        /// <summary>Cardinal flood over the mask bits A* gets (RM_CliffMaskMath.AllowedBits), a lowered ladder joining its square
        /// to the shallower one across the wall it hangs on (RM_ClimbJoins.Structural via RM_LadderWallMath.Joins).</summary>
        private static HashSet<int> Flood(World wd, byte[] g, int k, int start, byte[] ladderDepth)
        {
            int w = wd.w, h = wd.h;
            bool Join(int i, int j)
            {
                foreach ((int c, int rot) in wd.ladders)
                {
                    int o = Other(wd, c, rot);
                    if (o < 0 || !((c == i && o == j) || (c == j && o == i))) continue;
                    if (RM_LadderWallMath.Joins(rot, ladderDepth[c], o % w - c % w, o / w - c / w, ladderDepth[o])) return true;
                }
                return false;
            }
            var seen = new HashSet<int> { start };
            var q = new Queue<int>();
            q.Enqueue(start);
            while (q.Count > 0)
            {
                int i = q.Dequeue();
                int x = i % w, z = i / w;
                var d9 = new int[9];
                for (int dz = -1; dz <= 1; dz++)
                    for (int dx = -1; dx <= 1; dx++)
                    {
                        int nx = x + dx, nz = z + dz;
                        d9[RM_CliffMaskMath.N9(dx, dz)] = nx < 0 || nz < 0 || nx >= w || nz >= h ? 0 : g[nz * w + nx];
                    }
                byte bits = RM_CliffMaskMath.AllowedBits(d9, k, b =>
                {
                    int nx = x + RM_CliffMaskMath.Dx[b], nz = z + RM_CliffMaskMath.Dz[b];
                    return nx >= 0 && nz >= 0 && nx < w && nz < h && Join(i, nz * w + nx);
                });
                for (int b = 0; b < 4; b++)
                {
                    if ((bits & (1 << b)) == 0) continue;
                    int nx = x + RM_CliffMaskMath.Dx[b], nz = z + RM_CliffMaskMath.Dz[b];
                    if (nx < 0 || nz < 0 || nx >= w || nz >= h) continue;
                    int j = nz * w + nx;
                    if (seen.Add(j)) q.Enqueue(j);
                }
            }
            return seen;
        }

        private static int ViewStride(World wd, bool floor, int stride) =>
            stride <= 0 ? 0 : RM_TrenchStrideMath.CanonicalStride(RM_TrenchStrideMath.RunWidths(wd.View(floor), wd.w, wd.h), stride);

        private static byte[] Bridge(World wd, byte[] depth, int s) =>
            s > 0 ? RM_TrenchStrideMath.BridgedDepth(depth, RM_TrenchStrideMath.RunWidths(depth, wd.w, wd.h), s) : depth;

        /// <summary>The pawn's view flags: (floor view differs, the cliff floor view, the strider's floor view).</summary>
        private static (bool differs, bool uses, bool striderFloor) Flags(World wd, Walker p, bool oldRule)
        {
            int i = p.z * wd.w + p.x;
            int deepest = wd.Deepest();
            bool differs = deepest >= 0;
            bool onDeck = !p.inFloorBand && wd.decks.ContainsKey(i);
            // the rule before this fix (RM_SuspensionUnderpass.UsesFloorView): any dug undecked square chose the floor view
            bool uses = differs && (oldRule
                ? p.inFloorBand || (!onDeck && wd.climb[i] > 0)
                : RM_PocketGridMath.UsesFloorView(true, p.inFloorBand, onDeck, wd.climb[i], deepest));
            // RM_TrenchStride.SteppedOver reads the deck view's widths
            bool bridged = p.stride > 0 && RM_TrenchStrideMath.Bridged(RM_TrenchStrideMath.RunWidths(wd.View(false), wd.w, wd.h)[i], p.stride);
            return (differs, uses, RM_TrenchStrideMath.StriderUsesFloorView(uses, p.inFloorBand, bridged));
        }

        /// <summary>The connectivity A* plans on: RM_CliffMask.Swap (under masks when underDerived and UsesFloorView), then the
        /// stride swap (its view by StriderUsesFloorView, kept only when that view bridges something).</summary>
        private static (byte[] depth, byte[] ladderDepth) AStarView(World wd, Walker p, bool oldRule)
        {
            var f = Flags(wd, p, oldRule);
            bool sf = f.differs && f.striderFloor;
            int s = ViewStride(wd, sf, p.stride);
            if (s > 0)
                return (Bridge(wd, wd.View(sf), s), wd.View(sf));
            bool floor = f.differs && f.uses;
            return (wd.View(floor), wd.View(floor));
        }

        /// <summary>RM_SuperdeepTrap.RelativeVeto on the grid RM_PocketGrid.ForPawn hands this pawn (one square wide, vanilla
        /// says yes). oldGrid: the grid before this fix (always the deck view).</summary>
        private static bool Vetoed(World wd, Walker p, int dest, bool oldRule, bool oldGrid)
        {
            var f = Flags(wd, p, oldRule);
            (bool floor, int s) = oldGrid ? (false, ViewStride(wd, false, p.stride))
                : RM_PocketGridMath.ReachGridView(f.differs, f.uses, f.striderFloor, v => ViewStride(wd, v, p.stride));
            byte[] ld = wd.View(floor);
            byte[] depth = Bridge(wd, ld, s);
            var l = RM_PocketGridMath.Label(depth, wd.w, wd.h, p.k);
            int start = p.z * wd.w + p.x;
            if (l.SameComponent(start, dest)) return false;
            int cs = l.label[start], cd = l.label[dest];
            var edges = new List<(int a, int b)>();
            foreach ((int c, int rot) in wd.ladders)
            {
                int o = Other(wd, c, rot);
                if (o >= 0 && RM_PocketGridMath.LadderEdge(rot, ld[c], l.label[c], ld[o], l.label[o], true))
                    edges.Add((l.label[c], l.label[o]));
            }
            bool sp = !l.surface[cs], dp = !l.surface[cd];
            bool LadderIn(int comp) => edges.Exists(e => e.a == comp);
            bool sOut = sp && !RM_PocketGridMath.Trapped(true, LadderIn(cs), true);
            bool dIn = dp && LadderIn(cd);
            return RM_PocketGridMath.ReachVetoedWhole(sp, false, sOut, dp, false, dIn, () => RM_PocketGridMath.JoinedByLadders(cs, cd, edges));
        }

        /// <summary>Every destination square: reach's verdict against the A* flood. Returns the disagreements.</summary>
        private static List<string> Compare(World wd, Walker p, bool oldRule, bool oldGrid, ref int pairs)
        {
            var bad = new List<string>();
            (byte[] depth, byte[] ladderDepth) = AStarView(wd, p, oldRule);
            HashSet<int> astar = Flood(wd, depth, p.k, p.z * wd.w + p.x, ladderDepth);
            for (int d = 0; d < wd.w * wd.h; d++)
            {
                pairs++;
                bool vetoed = Vetoed(wd, p, d, oldRule, oldGrid);
                if (vetoed == astar.Contains(d))
                    bad.Add(p.name + " -> (" + d % wd.w + "," + d / wd.w + "): reach " + (vetoed ? "vetoed" : "allowed")
                        + ", A* " + (astar.Contains(d) ? "reaches" : "does not"));
            }
            return bad;
        }

        private static bool AStarReaches(World wd, Walker p, int x, int z, bool oldRule)
        {
            (byte[] depth, byte[] ladderDepth) = AStarView(wd, p, oldRule);
            return Flood(wd, depth, p.k, p.z * wd.w + p.x, ladderDepth).Contains(z * wd.w + x);
        }

        /// <summary>11×7: a 5-wide 4 m trench (x = 3..7) crossed at z = 3 by a surface suspension deck (it clears 2 m: the floor
        /// band passes under), a ladder on the trench's west wall at z = 1 hung toward the bank.</summary>
        private static World UnderDeck()
        {
            World wd = NewWorld(11, 7);
            Rect(wd.climb, wd.w, 3, 0, 5, wd.h, 8);
            for (int x = 3; x <= 7; x++) wd.decks[3 * wd.w + x] = 0;
            wd.ladders.Add((1 * wd.w + 3, West));
            return wd;
        }

        /// <summary>16×10 (TrenchStrideChecks' layout): a 1-wide 4 m trench at x = 3 with a deck on it at z = 6, a 5-wide pit
        /// x = 8..12 crossed by a deck along z = 4; both decks clear 2 m.</summary>
        private static World TitanTrench()
        {
            World wd = NewWorld(16, 10);
            Rect(wd.climb, wd.w, 3, 0, 1, wd.h, 8);
            Rect(wd.climb, wd.w, 8, 0, 5, wd.h, 8);
            wd.decks[6 * wd.w + 3] = 0;
            for (int x = 8; x <= 12; x++) wd.decks[4 * wd.w + x] = 0;
            return wd;
        }

        /// <summary>13×7: banks x = 0..1 and 11..12, 4 m ledges x = 2..3 and 9..10, a 7 m core x = 4..8, a sunken deck at 4 m
        /// across the core along z = 3 (it clears 2 m over the core: the floor band passes under).</summary>
        private static World Sunken()
        {
            World wd = NewWorld(13, 7);
            Rect(wd.climb, wd.w, 2, 0, 2, wd.h, 8);
            Rect(wd.climb, wd.w, 9, 0, 2, wd.h, 8);
            Rect(wd.climb, wd.w, 4, 0, 5, wd.h, 14);
            for (int x = 4; x <= 8; x++) wd.decks[3 * wd.w + x] = 8;
            return wd;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("Underpass_reach_agrees_with_the_pathfinder_under_and_beside_decks", () =>
            {
                var scenes = new List<(string name, World wd, Walker[] walkers)>
                {
                    ("under a surface deck", UnderDeck(), new[]
                    {
                        new Walker { name = "in the hole", x = 5, z = 1, k = Person },
                        new Walker { name = "on the deck", x = 5, z = 3, k = Person },
                        new Walker { name = "under the deck (floor band)", x = 5, z = 3, k = Person, inFloorBand = true },
                        new Walker { name = "on the bank by the ladder", x = 2, z = 1, k = Person },
                        new Walker { name = "at the ladder's foot", x = 3, z = 1, k = Person },
                    }),
                    ("titan beside a deck", TitanTrench(), new[]
                    {
                        new Walker { name = "titan astride the narrow trench", x = 3, z = 2, k = Titan, stride = 1 },
                        new Walker { name = "titan in the pit", x = 10, z = 2, k = Titan, stride = 1 },
                        new Walker { name = "titan on the pit's deck", x = 10, z = 4, k = Titan, stride = 1 },
                        new Walker { name = "titan under the pit's deck", x = 10, z = 4, k = Titan, stride = 1, inFloorBand = true },
                        new Walker { name = "person in the pit", x = 10, z = 2, k = Person },
                    }),
                    ("sunken bridge between ledges", Sunken(), new[]
                    {
                        new Walker { name = "on ledge A", x = 2, z = 3, k = Person },
                        new Walker { name = "on the sunken deck", x = 6, z = 3, k = Person },
                        new Walker { name = "in the core", x = 6, z = 1, k = Person },
                        new Walker { name = "under the sunken deck", x = 6, z = 3, k = Person, inFloorBand = true },
                    }),
                };
                int pairs = 0, oldBad = 0;
                foreach (var sc in scenes)
                    foreach (Walker p in sc.walkers)
                    {
                        List<string> bad = Compare(sc.wd, p, false, false, ref pairs);
                        Assert(bad.Count == 0, sc.name + ": " + bad.Count + " disagreements, first " + (bad.Count > 0 ? bad[0] : ""));
                        int ignored = 0;
                        oldBad += Compare(sc.wd, p, false, true, ref ignored).Count;
                    }
                Assert(pairs == 77 * 5 + 160 * 5 + 91 * 4, "every walker against every square (" + pairs + ")");
                Assert(oldBad > 0, "can-fail: the deck-view grid disagreed with A* (" + oldBad + " pairs)");

                World u = UnderDeck();
                var hole = new Walker { name = "in the hole", x = 5, z = 1, k = Person };
                Assert(AStarReaches(u, hole, 5, 5, false) && !Vetoed(u, hole, 5 * u.w + 5, false, false),
                    "in the hole: under the deck to the far side, and reach agrees");
                Assert(Vetoed(u, hole, 5 * u.w + 5, false, true), "can-fail: the deck-view grid refused that walk (the bug)");
                var bank = new Walker { name = "bank", x = 2, z = 1, k = Person };
                Assert(AStarReaches(u, bank, 4, 1, false) && !AStarReaches(u, bank, 4, 5, false) && Vetoed(u, bank, 5 * u.w + 4, false, false),
                    "from the bank: down the ladder, but the far side is a second walk (the deck view, agreed)");
                var deck = new Walker { name = "deck", x = 5, z = 3, k = Person };
                Assert(AStarReaches(u, deck, 10, 3, false) && !AStarReaches(u, deck, 5, 5, false), "on the deck: across, never down");

                World t = TitanTrench();
                var pit = new Walker { name = "pit", x = 10, z = 2, k = Titan, stride = 1 };
                Assert(AStarReaches(t, pit, 10, 7, false) && !Vetoed(t, pit, 7 * t.w + 10, false, false),
                    "titan in the pit: walks under the deck, and reach agrees");
                var astride = new Walker { name = "astride", x = 3, z = 2, k = Titan, stride = 1 };
                Assert(AStarReaches(t, astride, 14, 4, false) && !Vetoed(t, astride, 4 * t.w + 14, false, false),
                    "titan astride the narrow trench: over it and across the pit's deck");

                World s = Sunken();
                var ledge = new Walker { name = "ledge", x = 2, z = 3, k = Person };
                Assert(AStarReaches(s, ledge, 10, 3, false) && !Vetoed(s, ledge, 3 * s.w + 10, false, false),
                    "on ledge A: across the sunken deck to ledge B, and reach agrees");
                Assert(!AStarReaches(s, ledge, 10, 3, true), "can-fail: the old floor-view rule read the sunken deck as the core below it");
                var core = new Walker { name = "core", x = 6, z = 1, k = Person };
                Assert(AStarReaches(s, core, 6, 5, false) && !Vetoed(s, core, 5 * s.w + 6, false, false), "in the core: under the sunken deck");
            });

            Case("Underpass_reach_view_rules_and_wiring", () =>
            {
                Assert(RM_PocketGridMath.ViewDepth(14, true, 8, true, false) == 8 && RM_PocketGridMath.ViewDepth(14, true, 8, true, true) == 14,
                    "a passing deck: its height in the deck view, the floor in the floor view");
                Assert(RM_PocketGridMath.ViewDepth(3, true, 0, false, true) == 0 && RM_PocketGridMath.ViewDepth(5, false, 0, false, false) == 5,
                    "can-fail: a deck that does not pass under is ground in both views; no deck, the climb depth");
                Assert(RM_PocketGridMath.UsesFloorView(true, false, false, 14, 8) && !RM_PocketGridMath.UsesFloorView(true, false, false, 8, 8),
                    "deeper than the deepest passing deck: floor view; level with a sunken deck: deck view");
                Assert(RM_PocketGridMath.UsesFloorView(true, true, true, 0, 99) && !RM_PocketGridMath.UsesFloorView(true, false, true, 14, -1)
                    && !RM_PocketGridMath.UsesFloorView(false, true, false, 14, 0) && !RM_PocketGridMath.UsesFloorView(true, false, false, 0, -1),
                    "floor band: floor view; on a deck, the setting off or on the surface: deck view");
                Assert(RM_PocketGridMath.ReachGridView(true, true, false, f => f ? 0 : 2) == (false, 2)
                    && RM_PocketGridMath.ReachGridView(true, true, true, f => 0) == (true, 0)
                    && RM_PocketGridMath.ReachGridView(false, true, true, f => f ? 3 : 0) == (false, 0),
                    "the stride view wins when it bridges something; else the cliff view; no passing deck, the deck view");

                string grid = Src("Superdeep", "RM_PocketGrid.cs");
                Assert(grid.Contains("(bool floor, int s) = RM_PocketGridMath.ReachGridView(differs, uses, striderFloor, f => RM_TrenchStride.ViewStride(p, map, f));")
                    && grid.Contains("return For(map, s, floor);"), "ForPawn picks the grid by the path request's view");
                Assert(grid.Contains("byte[] depth = EffectiveDepth(map, eng, floorView);") && grid.Contains("floorGrids"),
                    "a floor-view grid is labelled on the floor view");
                Assert(grid.Contains("floorView ? Pits.RM_SuspensionUnderpass.FloorViewDepthAt(map, eng, c) : RM_SuperdeepTrap.StepDepthAt(map, eng, c)"),
                    "its ladder edges read the same view's depths as the masks");
                string under = Src("Pits", "Suspension", "RM_SuspensionPatches.cs");
                Assert(under.Contains("return RM_PocketGridMath.UsesFloorView(true, false, false, d, d > 0 ? DeepestPassingDeck(map, eng) : -1);"),
                    "UsesFloorView decides by the math");
                Assert(!under.Contains("return eng != null && eng.ClimbDepthAt(p.Position) > 0;"), "can-fail: any dug square no longer means the floor view");
                string mask = Src("Superdeep", "RM_CliffMask.cs");
                Assert(mask.Contains("if (m.underDerived && Pits.RM_SuspensionUnderpass.UsesFloorView(p))"), "the cliff swap reads the same rule");
                string st = Src("Superdeep", "RM_TrenchStride.cs");
                Assert(st.Contains("RM_TrenchStrideMath.StriderUsesFloorView(Pits.RM_SuspensionUnderpass.UsesFloorView(p), Pits.RM_SuspensionUnderpass.InFloorBand(p),")
                    && st.Contains("if (s == 0 || !m.derived[v][s])"), "the stride swap is the composition ReachGridView models");
                string trap = Src("Superdeep", "RM_SuperdeepTrap.cs");
                Assert(trap.Contains("RM_PocketGrid g = RM_PocketGrid.ForPawn(map, p);"), "the reach veto reads ForPawn");
            });
        }
    }
}
