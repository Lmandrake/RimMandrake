// PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 3 (design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md §P4):
// offline checks on the production collapse selector, fallen-run split and liveness rule (RM_DeckCollapseLinesMath, compiled
// in), the production hook and collapse paths (RM_MapComponent_SuspensionBridges.cs, RM_DeckCollapseLines.cs, read as text) and
// the Gimme Some Slack seam (GSS's RM_FallenWireShock.cs read as text). L1 of the item's verify for phase 3: collapse with a cord
// gives one fallen-wire event and splits the net once; a repeat teardown is idempotent; an unpowered cord shocks nobody; a hose
// on a collapsed deck is cut. Each case has a can-fail. NOT proven here: a pawn in the hole being knocked out by the dropped
// cord in a running game, and the hose reel winding in (L2 live rows, owed).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class DeckCollapseLinesChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        private static string Src(params string[] rel) => RiverSwitchFlipChecks.Src(Path.Combine(rel));

        private static string Body(string src, string signature)
        {
            int a = src.IndexOf(signature, StringComparison.Ordinal);
            Assert(a >= 0, "missing: " + signature);
            int open = src.IndexOf('{', a);
            int depth = 0;
            for (int i = open; i < src.Length; i++)
            {
                if (src[i] == '{') depth++;
                else if (src[i] == '}' && --depth == 0) return src.Substring(a, i - a + 1);
            }
            throw new Exception("unbalanced: " + signature);
        }

        /// <summary>One thing on a square of the row: its line tag (null = not a line), whether it transmits, whether it is gone.</summary>
        private sealed class T
        {
            public int X;
            public LineKind? Kind;
            public bool Source;
            public bool Gone;
        }

        /// <summary>generator(0) | conduit(1) | cord on a deck (2,3,4) | conduit(5) | lamp(6): one power net while the deck stands.</summary>
        private static List<T> Row() => new List<T>
        {
            new T { X = 0, Kind = null, Source = true },
            new T { X = 1, Kind = LineKind.RigidConduit },
            new T { X = 2, Kind = LineKind.FlexCord },
            new T { X = 3, Kind = LineKind.FlexCord },
            new T { X = 4, Kind = LineKind.FlexCord },
            new T { X = 5, Kind = LineKind.RigidConduit },
            new T { X = 6, Kind = null },
        };

        private static readonly int[] Deck = { 2, 3, 4 };

        /// <summary>Net id per cell along the row (-1 = gone): adjacent standing cells share a net.</summary>
        private static int[] Nets(List<T> row)
        {
            var id = new int[row.Count];
            int next = 0;
            for (int i = 0; i < row.Count; i++)
            {
                id[i] = row[i].Gone ? -1 : (i > 0 && !row[i - 1].Gone ? id[i - 1] : next++);
            }
            return id;
        }

        private static int NetCount(List<T> row) => Nets(row).Where(n => n >= 0).Distinct().Count();

        /// <summary>The collapse, as ClearDeckTop + RM_DeckCollapseLines.OnDeckCleared do it: per deck square, select the cords
        /// to drop (and record the square), then destroy everything on it.</summary>
        private static (int dropped, List<(int X, int Z)> fallen) Collapse(List<T> row, bool rulesOn)
        {
            int dropped = 0;
            var fallen = new List<(int X, int Z)>();
            foreach (int x in Deck)
            {
                List<T> sq = row.Where(t => t.X == x).ToList();
                List<T> cords = RM_DeckCollapseLinesMath.CordsToDrop(rulesOn, sq, t => t.Kind, t => t.Gone);
                if (cords.Count > 0)
                {
                    fallen.Add((x, 0));
                    dropped += cords.Count;
                }
                foreach (T t in sq) t.Gone = true;   // ClearDeckTop destroys every building on the square
            }
            return (dropped, fallen);
        }

        /// <summary>Live halves after a collapse: ends are the standing transmitters beside the run; an end is live when its net
        /// holds the generator.</summary>
        private static List<(RM_DeckCollapseLinesMath.Half half, bool live)> Fallen(List<T> row, List<(int X, int Z)> fallen)
        {
            int[] nets = Nets(row);
            var result = new List<(RM_DeckCollapseLinesMath.Half, bool)>();
            foreach (List<(int X, int Z)> run in RM_DeckCollapseLinesMath.Runs(fallen))
            {
                var ends = new List<(int X, int Z)>();
                foreach ((int X, int Z) c in run)
                {
                    foreach (int nx in new[] { c.X - 1, c.X + 1 })
                    {
                        if (nx >= 0 && nx < row.Count && !row[nx].Gone && !run.Contains((nx, 0)) && !ends.Contains((nx, 0))) ends.Add((nx, 0));
                    }
                }
                foreach (RM_DeckCollapseLinesMath.Half h in RM_DeckCollapseLinesMath.Split(run, ends))
                {
                    int net = nets[ends[h.End].X];
                    bool powered = row.Any(t => !t.Gone && t.Source && nets[t.X] == net);
                    result.Add((h, RM_DeckCollapseLinesMath.Live(true, true, true, powered)));
                }
            }
            return result;
        }

        public static void Run(Action<string, Action> Case)
        {
            Case("DeckCollapse_cord_drops_one_live_fallen_wire_and_the_net_splits_once", () =>
            {
                List<T> row = Row();
                Assert(NetCount(row) == 1, "standing: one net, the lamp is powered");
                (int dropped, List<(int X, int Z)> fallen) = Collapse(row, true);
                Assert(dropped == 3 && fallen.Count == 3, "can-fail: every cord on the three deck squares falls");
                Assert(NetCount(row) == 2, "can-fail: the net splits into exactly two, generator side and lamp side");
                var halves = Fallen(row, fallen);
                Assert(halves.Count == 2, "a cord cut out of the middle leaves one half per bank");
                Assert(halves.Sum(h => h.half.Cells.Count) == 3 && halves.All(h => h.half.Cells.Contains(h.half.Tip)), "every fallen square belongs to exactly one half, tip included");
                var live = halves.Where(h => h.live).ToList();
                Assert(live.Count == 1 && live[0].half.Cells.Contains((2, 0)), "can-fail: only the half hanging from the generator side is live");
                Assert(live[0].half.Tip.X == 3, "its tip is the square farthest down the run from its end");
                Assert(RM_DeckCollapseLinesMath.LiveMessage(live.Count) != null && RM_DeckCollapseLinesMath.LiveMessage(0) == null,
                    "one message for the live fall, none for a dead one");
                // production: one fallen-wire event per bind that made a live half; the deck squares are recorded through ClearDeckTop
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                string bind = Body(dl, "private void Bind()");
                Assert(bind.Contains("if (live > 0) { LiveFalls++;"), "can-fail: one event per collapse bind, not per square or per half");
                Assert(Body(dl, "public static int OnDeckCleared(Map map, IntVec3 c)").Contains("map.GetComponent<RM_MapComponent_FallenCords>()?.Notify_CordFell(c);"),
                    "the cleared square is handed to the fallen-cord component");
            });

            Case("DeckCollapse_repeat_teardown_is_idempotent", () =>
            {
                List<T> row = Row();
                (int first, List<(int X, int Z)> fallen) = Collapse(row, true);
                (int again, List<(int X, int Z)> more) = Collapse(row, true);
                Assert(first == 3 && again == 0 && more.Count == 0, "can-fail: a second clear of the same squares drops nothing");
                Assert(NetCount(row) == 2, "and splits nothing again");
                var doubled = fallen.Concat(fallen).ToList();
                var runs = RM_DeckCollapseLinesMath.Runs(doubled);
                Assert(runs.Count == 1 && runs[0].Count == 3, "a square recorded twice is one square of one run");
                var a = RM_DeckCollapseLinesMath.Split(runs[0], new List<(int X, int Z)> { (1, 0), (5, 0) });
                var b = RM_DeckCollapseLinesMath.Split(RM_DeckCollapseLinesMath.Runs(fallen)[0], new List<(int X, int Z)> { (1, 0), (5, 0) });
                Assert(a.Count == b.Count && a.Zip(b, (x, y) => x.End == y.End && x.Tip == y.Tip && x.Cells.SequenceEqual(y.Cells)).All(z => z),
                    "re-binding the same squares gives the same halves");
                // production guards: a square is recorded once; gone things are skipped; only a laid hose is cut
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(Body(dl, "public void Notify_CordFell(IntVec3 c)").Contains("if (pending.Contains(c) || Holds(c)) { return; }"), "can-fail: a fallen square is recorded once");
                Assert(dl.Contains("t => t.Destroyed || !t.Spawned"), "a cord already destroyed is not dropped again");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(false, new[] { (3, 0) }, 3, 0), "a hose already reeled in is not cut again");
            });

            Case("DeckCollapse_unpowered_or_disconnected_cord_shocks_nobody", () =>
            {
                List<T> row = Row();
                row[0].Source = false;                                   // the generator is off: no active source anywhere
                var (_, fallen) = Collapse(row, true);
                Assert(Fallen(row, fallen).All(h => !h.live), "can-fail: an unpowered cord falls dead");
                Assert(RM_DeckCollapseLinesMath.Live(true, true, true, true), "can-fail: all four true is live");
                Assert(!RM_DeckCollapseLinesMath.Live(true, true, true, false), "no active source: dead");
                Assert(!RM_DeckCollapseLinesMath.Live(true, false, true, true), "end gone: dead");
                Assert(!RM_DeckCollapseLinesMath.Live(true, true, false, true), "a net the map no longer holds (stale edge): dead");
                Assert(!RM_DeckCollapseLinesMath.Live(false, true, true, true), "rules off: dead");
                Assert(RM_DeckCollapseLinesMath.Split(new List<(int X, int Z)> { (2, 0), (3, 0) }, new List<(int X, int Z)>()).Count == 0,
                    "a run that hangs from nothing makes no half (dropped, never live)");
                Assert(RM_DeckCollapseLinesMath.Split(new List<(int X, int Z)> { (2, 0), (3, 0) }, new List<(int X, int Z)> { (9, 9) }).Count == 0,
                    "an end not beside the run holds nothing");
                // production: GSS gets only live halves, and liveness reads a REGISTERED net
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(Body(dl, "public IEnumerable<KeyValuePair<IntVec3, IntVec3>> LiveContacts()").Contains("if (!Live(h)) { continue; }"), "can-fail: dead halves give no contact");
                Assert(Body(dl, "public bool Live(RM_FallenCordHalf h)").Contains("map.powerNetManager.AllNetsListForReading.Contains(n)"), "a dropped net never reads powered");
            });

            Case("DeckCollapse_hose_across_a_collapsed_deck_is_reeled_in", () =>
            {
                var trail = new[] { (0, 0), (1, 0), (2, 0), (3, 0) };
                Assert(RM_DeckCollapseLinesMath.HoseCrosses(true, trail, 2, 0), "can-fail: a laid hose over the square is cut");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(true, trail, 2, 1), "a hose beside the deck is not");
                Assert(!RM_DeckCollapseLinesMath.HoseCrosses(true, null, 2, 0), "no path, no cut");
                Assert(!RM_DeckCollapseLinesMath.FallsAsWire(LineKind.Hose) && RM_DeckCollapseLinesMath.FallsAsWire(LineKind.FlexCord)
                    && !RM_DeckCollapseLinesMath.FallsAsWire(LineKind.RigidPipe), "only a cord falls as a wire");
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                string hook = Body(dl, "public static int OnDeckCleared(Map map, IntVec3 c)");
                Assert(hook.Contains("RM_DeckCollapseLinesMath.HoseCrosses(r.laid, PathOf(r), c.x, c.z)") && hook.Contains("r.Retract(HoseCutReason);"),
                    "can-fail: the hose router's own retract path cuts it");
                string reel = Src("Hose", "CompHoseReel.cs");
                Assert(Body(reel, "public void Retract(string why)").Contains("ReelIn();"), "retract winds the hose back onto its reel");
            });

            Case("DeckCollapse_every_collapse_path_clears_through_ClearDeckTop", () =>
            {
                string comp = Src("Pits", "Suspension", "RM_MapComponent_SuspensionBridges.cs");
                Assert(Body(comp, "public static void ClearDeckTop(Map map, IntVec3 c)").Contains("RM_DeckCollapseLines.OnDeckCleared(map, c);"), "can-fail: the hook is in the one funnel");
                Assert(Body(comp, "public void CollapseSpan(Building_SuspensionDeck from, string how)").Contains("ClearDeckTop(map, d.Position);"), "span collapse (broke, taken apart, lost anchor)");
                Assert(comp.Contains("if (st == SpanLoadState.Over && RM_SuspensionSettings.suspensionWeightCollapse)") && comp.Contains("foreach (IntVec3 c in cells) { ClearDeckTop(map, c); }"), "weight overload");
                string deck = Src("Pits", "Suspension", "Building_SuspensionDeck.cs");
                Assert(Body(deck, "public void DropAlone()").Contains("RM_MapComponent_SuspensionBridges.ClearDeckTop(map, pos);"), "the one-square swing-down");
                Assert(Body(deck, "public override void Destroy(DestroyMode mode = DestroyMode.Vanish)").Contains("b.CollapseSpan(this,"), "a broken or deconstructed square");
                string grav = Src("Pits", "Drawbridge", "RM_DrawbridgeGravship.cs");
                Assert(grav.Contains("comp.CollapseSpan(d, \"was torn loose when the gravship launched\");"), "the gravship launch tears an edge bridge loose");
                // a winch-lost crash is NOT a collapse: the leaf comes down whole and its cords rejoin through the leaf toggle
                string db = Src("Pits", "Drawbridge", "RM_Drawbridges.cs");
                string crash = Body(db, "public static void Crash(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)");
                Assert(!crash.Contains("ClearDeckTop") && crash.Contains("Apply(map, r, l);"), "can-fail: the crash lowers the leaf, destroying nothing");
                Assert(Body(db, "public static void Apply(Map map, SuspensionBridgeRecord r, DrawbridgeLeaf l)").Contains("NotifyToggled(map, changed);"), "lowering re-registers the cords");
            });

            Case("DeckCollapse_GSS_shock_seam_is_soft_and_load_safe", () =>
            {
                string csproj = Src("RimMandrake_FlowWorks.csproj");
                Assert(!csproj.Contains("GimmeSomeSlack.dll") && !csproj.Contains("RimMandrake_GimmeSomeSlack.csproj"), "can-fail: FlowWorks has no compile-time reference to GSS");
                Assert(csproj.Contains("Machinery\\RM_DeckCollapseLinesMath.cs") && csproj.Contains("Machinery\\RM_DeckCollapseLines.cs"), "both files are in the mod build");
                string dl = Src("Machinery", "RM_DeckCollapseLines.cs");
                Assert(dl.Contains("public const string GssShockType = \"RimMandrake.GimmeSomeSlack.Aerial.RM_FallenWireShock\";")
                    && dl.Contains("GenTypes.GetTypeInAnyAssembly(GssShockType)") && dl.Contains("if (t == null) { return;"), "looked up by name; absent GSS is a quiet no-op");
                string gss = Src("..", "..", "GimmeSomeSlack", "Source", "Aerial", "RM_FallenWireShock.cs");
                Assert(gss.Contains("namespace RimMandrake.GimmeSomeSlack.Aerial") && gss.Contains("public static class RM_FallenWireShock"), "the type name FlowWorks looks up is the real one");
                Assert(gss.Contains("public static void RegisterLiveWireSource(Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>> source)")
                    && dl.Contains("t.GetMethod(\"RegisterLiveWireSource\"") && dl.Contains("new[] { typeof(Func<Map, IEnumerable<KeyValuePair<IntVec3, IntVec3>>>) }"),
                    "can-fail: the entry point's signature matches the lookup");
                Assert(gss.Contains("public static void LiveWiresChanged(Map map)") && dl.Contains("t.GetMethod(\"LiveWiresChanged\""), "the change poke matches too");
                string rebuild = Body(gss, "public static void RebuildContacts(RM_MapComponent_Aerial aerial, Map map, Dictionary<int, IntVec3> contacts, List<IntVec3> tips)");
                Assert(rebuild.Contains("ExternalContacts(map, contacts, tips);"), "can-fail: GSS feeds the external wires into the same shock and ignition contacts");
            });
        }
    }
}
