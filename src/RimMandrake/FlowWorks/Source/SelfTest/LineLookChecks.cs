// RIMMANDRAKE_SPREAD_FLOWWORKS_LOOK_ALONG_LINE_NOT_PIPES_ONLY: the SHIPPED look-line decision (Machinery/RM_LineLook.cs) over
// a fake map that answers IRM_LineGraph the way the Verse adapter (PipeLook.MapLineGraph) does: pipe cells cardinal, members
// 8-way around or on a pipe cell, things touching 8-way, hose couplings listed. Owner walk 2026-11-22 station 24: a look
// picked on one part must reach the tank, the pump, the pipes, the sprinkler head, the faucet and the hose reel of its line.
// Each case prints what it read (parts, changed, the worst miss) against its limit.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using RimMandrake.FlowWorks.Machinery;

namespace RimMandrake.FlowWorks.SelfTest
{
    internal static class LineLookChecks
    {
        private static void Assert(bool ok, string msg)
        {
            if (!ok) throw new Exception(msg);
        }

        /// <summary>A placed part: a rect (x0..x1, z0..z1), its kind, whose, whether it is FlowWorks', its looks.</summary>
        internal sealed class P
        {
            public string Name;
            public int X0, Z0, X1, Z1;
            public RM_LinePart Kind;
            public bool Ours = true, Player = true, OnCellPart;
            public string Stored;
            public HashSet<string> Looks = new HashSet<string>(PipeStyles.Looks);
            public override string ToString() => Name;
        }

        /// <summary>The fake map: pipe cells (with their own pipe part), parts, hose couplings.</summary>
        internal sealed class Fake : IRM_LineGraph
        {
            public readonly Dictionary<(int, int), P> Pipes = new Dictionary<(int, int), P>();
            public readonly List<P> Things = new List<P>();
            public readonly List<(P reel, object other)> Hoses = new List<(P, object)>();
            public readonly Dictionary<(int, int), List<(int, int)>> Spans = new Dictionary<(int, int), List<(int, int)>>();

            public P Pipe(int x, int z, bool ours = true, bool player = true)
            {
                var p = new P { Name = "pipe" + x + "," + z, X0 = x, Z0 = z, X1 = x, Z1 = z, Kind = RM_LinePart.Pipe, Ours = ours, Player = player };
                Pipes[(x, z)] = p;
                return p;
            }

            public void Run(int x0, int x1, int z) { for (int x = x0; x <= x1; x++) Pipe(x, z); }

            public P Add(string name, RM_LinePart kind, int x0, int z0, int x1 = int.MinValue, int z1 = int.MinValue, bool ours = true, bool player = true)
            {
                var p = new P { Name = name, Kind = kind, X0 = x0, Z0 = z0, X1 = x1 == int.MinValue ? x0 : x1, Z1 = z1 == int.MinValue ? z0 : z1, Ours = ours, Player = player };
                Things.Add(p);
                return p;
            }

            /// <summary>A fitting (faucet, pole) or a foreign thing standing on a pipe cell.</summary>
            public P OnCell(string name, int x, int z, bool ours = true, bool player = true)
            {
                P p = Add(name, ours ? RM_LinePart.Fitting : RM_LinePart.None, x, z, ours: ours, player: player);
                p.OnCellPart = true;
                return p;
            }

            private static bool Live(P p) => p != null && p.Ours && p.Player;

            public RM_LinePart KindOf(object v)
            {
                if (v is ValueTuple<int, int> c) return Pipes.TryGetValue(c, out P pp) && Live(pp) ? RM_LinePart.Pipe : RM_LinePart.None;
                return v is P p && Live(p) ? p.Kind : RM_LinePart.None;
            }

            public IEnumerable<object> PipeNeighbours(object cell)
            {
                var (x, z) = ((int, int))cell;
                foreach (var n in new[] { (x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1) })
                    if (Pipes.ContainsKey(n)) yield return n;
                if (Spans.TryGetValue((x, z), out var extra)) foreach (var n in extra) yield return n;
            }

            private static int Gap(P a, int x, int z) => Math.Max(Math.Max(a.X0 - x, x - a.X1), Math.Max(a.Z0 - z, z - a.Z1));

            private static int Gap(P a, P b) => Math.Max(Math.Max(a.X0 - b.X1, b.X0 - a.X1), Math.Max(a.Z0 - b.Z1, b.Z0 - a.Z1));

            public IEnumerable<object> AroundCell(object cell)
            {
                var (x, z) = ((int, int))cell;
                // every thing on or 8-way around, as the adapter lists them: the cell's own PIPE things included (the adapter's
                // GetThingList holds the pipe Thing; visit 11, 2026-11-24, threw when the walk took one for a pipe cell)
                return Things.Concat(Pipes.Values).Where(t => Gap(t, x, z) <= 1);
            }

            public IEnumerable<object> PipeCellsAround(object part)
            {
                var p = (P)part;
                return Pipes.Keys.Where(c => Gap(p, c.Item1, c.Item2) <= 1).OrderBy(c => c.Item1).ThenBy(c => c.Item2).Cast<object>();
            }

            public IEnumerable<object> Touching(object part)
            {
                var p = (P)part;
                // fittings, foreign things and the pipe things beside it too, as the adapter lists them: the kernel filters
                return Things.Concat(Pipes.Values).Where(t => t != p && Gap(p, t) <= 1);
            }

            public IEnumerable<object> HoseJoins(object v)
            {
                foreach (var (reel, other) in Hoses)
                {
                    if (Equals(reel, v)) yield return other;
                    else if (Equals(other, v)) yield return reel;
                }
            }

            public IEnumerable<object> PartsOn(object cell)
            {
                var (x, z) = ((int, int))cell;
                if (Pipes.TryGetValue((x, z), out P pipe)) yield return pipe;
                foreach (P t in Things) if (t.OnCellPart && t.X0 == x && t.Z0 == z) yield return t;
            }

            public IEnumerable<object> FittingCells(object fitting)
            {
                var p = (P)fitting;
                if (Pipes.ContainsKey((p.X0, p.Z0))) yield return (p.X0, p.Z0);
            }

            public object Cell(int x, int z) => (x, z);

            /// <summary>What a pick changes, from these starts.</summary>
            public List<P> Pick(string look, out bool capped, int cap, params object[] starts) =>
                RM_LineLook.Changes(this, starts, look, cap, (o, l) => o is P p && p.Looks.Contains(l), o => (o as P)?.Stored, out capped)
                    .Cast<P>().ToList();

            public List<P> Pick(string look, params object[] starts) => Pick(look, out _, 4096, starts);
        }

        /// <summary>Station 24 as the owner walked it, plus the parts the walk did not show (a faucet, a reel's relay).</summary>
        internal static (Fake g, Dictionary<string, P> at) Station24()
        {
            var g = new Fake();
            var at = new Dictionary<string, P>();
            at["tank"] = g.Add("tank", RM_LinePart.Tank, 0, 0, 1, 0);          // a 2x1 tank
            g.Run(2, 3, 0);                                                     // pipe tank -> pump
            at["pump"] = g.Add("pump", RM_LinePart.Machine, 4, 0);
            g.Run(5, 7, 0);                                                     // pipe pump -> head
            at["head"] = g.Add("head", RM_LinePart.Machine, 7, 0);             // a sprinkler head ON the last pipe cell
            at["faucet"] = g.OnCell("faucet", 6, 0);
            at["reel"] = g.Add("reel", RM_LinePart.Reel, 4, -3, 5, -2);        // a 2x2 reel, body coupled to the pump
            g.Hoses.Add((at["reel"], at["pump"]));
            at["cabinet"] = g.Add("cabinet", RM_LinePart.None, 4, -8, ours: false);   // GSS's: the hose's free end lies on it
            g.Hoses.Add((at["reel"], at["cabinet"]));
            foreach (var kv in g.Pipes) at[kv.Value.Name] = kv.Value;
            return (g, at);
        }

        /// <summary>A class's text in whitespace-collapsed source: from its declaration to the next top-level type.</summary>
        private static string ClassBody(string src, string decl)
        {
            int i = src.IndexOf(decl, StringComparison.Ordinal);
            if (i < 0) return null;
            int j = src.IndexOf(" public class ", i + decl.Length, StringComparison.Ordinal);
            int k = src.IndexOf(" internal static class ", i + decl.Length, StringComparison.Ordinal);
            int end = new[] { j, k, src.Length }.Where(x => x > 0).Min();
            return src.Substring(i, end - i);
        }

        private static string Names(IEnumerable<P> ps) => string.Join(",", ps.Select(p => p.Name).OrderBy(n => n));

        public static void Run(Action<string, Action> Case)
        {
            Case("LineLook_station24_every_start_reaches_the_whole_line", () =>
            {
                // the regime he walked: tank - pipe - pump - pipe - head, a faucet on the pipe, a hose reel on the pump, the hose
                // running to a GSS cabinet. From EVERY part the pick must reach all 10 FlowWorks parts, and never the cabinet.
                var (g, at) = Station24();
                string[] want = { "tank", "pump", "head", "faucet", "reel", "pipe2,0", "pipe3,0", "pipe5,0", "pipe6,0", "pipe7,0" };
                var starts = new List<(string, object)>
                {
                    ("tank", at["tank"]), ("pump", at["pump"]), ("head", at["head"]), ("reel", at["reel"]),
                    ("pipe2,0", g.Cell(2, 0)), ("pipe6,0 (faucet's cell)", g.Cell(6, 0)), ("pipe7,0", g.Cell(7, 0)),
                };
                int worst = 0;
                string worstAt = "-";
                foreach (var (name, s) in starts)
                {
                    List<P> ch = g.Pick("Futuristic", s);
                    int miss = want.Count(w => ch.All(p => p.Name != w)) + ch.Count(p => !want.Contains(p.Name));
                    if (miss > worst) { worst = miss; worstAt = name + " -> " + Names(ch); }
                }
                Console.WriteLine($"      {starts.Count} starts x {want.Length} parts; worst miss {worst} (limit 0) at {worstAt}");
                Assert(worst == 0, "a start that does not reach exactly the line: " + worstAt);
            });

            Case("LineLook_pipe_thing_listed_by_touch_is_not_a_vertex", () =>
            {
                // RIMMANDRAKE_FIX_FLOWWORKS_LINE_LOOK_CAST_THROWS_WHEN_TANK_TOUCHES_PIPE (visit 11, 2026-11-24, ArchBig): the
                // adapter's Touching and AroundCell list every thing in the cells, the PIPE things too. The walk took such a pipe
                // Thing for a pipe vertex and cast it to a cell: InvalidCastException, no look changed. A pipe vertex is only ever
                // its cell (PipeNeighbours, PipeCellsAround); a pipe thing listed by touch is not a join. Regimes read: every
                // start of station 24 (tank, pump, head, reel, pipe, faucet's cell); a tank and a pump with pipes on all 8 sides;
                // two pipes that only touch diagonally (not one line: a pipe joins pipe cardinally, never by an 8-way touch).
                var (g, at) = Station24();
                int read = 0, threw = 0;
                string first = "-";
                foreach (object s in new object[] { at["tank"], at["pump"], at["head"], at["reel"], at["faucet"], g.Cell(2, 0), g.Cell(6, 0), g.Cell(7, 0) })
                {
                    read++;
                    try { g.Pick("Modern", s); }
                    catch (Exception e) { threw++; if (first == "-") first = s + ": " + e.GetType().Name; }
                }
                var h = new Fake();
                P tank = h.Add("tank", RM_LinePart.Tank, 0, 0), pump = h.Add("pump", RM_LinePart.Machine, 10, 0);
                for (int dx = -1; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++)
                    if (dx != 0 || dz != 0) { h.Pipe(dx, dz); h.Pipe(10 + dx, dz); }
                int ringTank = -1, ringPump = -1;
                foreach (var (s, set) in new[] { (tank, 0), (pump, 1) })
                {
                    read++;
                    try { int n = h.Pick("Modern", s).Count; if (set == 0) ringTank = n; else ringPump = n; }
                    catch (Exception e) { threw++; if (first == "-") first = s + " ring: " + e.GetType().Name; }
                }
                var d = new Fake();
                d.Pipe(0, 0); d.Pipe(1, 1);
                int diag = -1;
                read++;
                try { diag = d.Pick("Modern", d.Cell(0, 0)).Count; }
                catch (Exception e) { threw++; if (first == "-") first = "diagonal: " + e.GetType().Name; }
                Console.WriteLine($"      {read} starts read; threw {threw} (limit 0), first {first}; tank ring {ringTank} (want 9), pump ring {ringPump} (want 9), diagonal pair {diag} (want 1)");
                Assert(threw == 0, "a pipe thing listed by touch must not be walked as a pipe cell: " + first);
                Assert(ringTank == 9 && ringPump == 9, "a tank or pump ringed by pipe reaches its 8 pipes, each once");
                Assert(diag == 1, "two pipes touching only diagonally are not one line");
            });

            Case("LineLook_old_rule_pipes_only_is_red_here", () =>
            {
                // can-fail: the rule before this fix (a pipe restyles the cardinal same-def pipe run; a tank or pump only itself)
                // misses parts of station 24 from every start; the shipped Joins table must not reduce to it.
                var (g, at) = Station24();
                int oldFromPipe = 0;
                foreach (object c in new object[] { g.Cell(2, 0) })
                {
                    var seen = new HashSet<object> { c };
                    var q = new Queue<object>(new[] { c });
                    while (q.Count > 0) foreach (object n in g.PipeNeighbours(q.Dequeue())) if (seen.Add(n)) q.Enqueue(n);
                    oldFromPipe = seen.Count;
                }
                int shipped = g.Pick("Futuristic", g.Cell(2, 0)).Count;
                Console.WriteLine($"      old pipe-run rule from pipe2,0 reaches {oldFromPipe} part(s); shipped reaches {shipped} (must be 10)");
                Assert(oldFromPipe < 10 && shipped == 10, "the old rule and the shipped walk must differ on station 24");
                Assert(!RM_LineLook.Joins(RM_LinePart.Pipe, RM_LinePart.None) && RM_LineLook.Joins(RM_LinePart.Pipe, RM_LinePart.Machine),
                       "pipe-machine joins; pipe-nothing does not");
            });

            Case("LineLook_join_table_symmetric_and_as_the_net", () =>
            {
                var kinds = (RM_LinePart[])Enum.GetValues(typeof(RM_LinePart));
                int asym = 0, n = 0;
                foreach (var a in kinds) foreach (var b in kinds) { n++; if (RM_LineLook.Joins(a, b) != RM_LineLook.Joins(b, a)) asym++; }
                Console.WriteLine($"      {n} kind pairs; asymmetric {asym} (limit 0)");
                Assert(asym == 0, "Joins must read the same both ways");
                Assert(!RM_LineLook.Joins(RM_LinePart.Tank, RM_LinePart.Tank), "two touching tanks are not joined (the net moves nothing between them)");
                Assert(!RM_LineLook.Joins(RM_LinePart.Machine, RM_LinePart.Machine), "two touching machines are not joined");
                Assert(RM_LineLook.Joins(RM_LinePart.Machine, RM_LinePart.Tank), "a machine joins the tank it touches (its touch store)");
                Assert(!RM_LineLook.Joins(RM_LinePart.Fitting, RM_LinePart.Tank), "a fitting joins only through its pipe cell");
                foreach (var k in kinds) Assert(!RM_LineLook.Joins(RM_LinePart.None, k), "nothing joins a non-FlowWorks / foreign part");
                int casym = 0, touchReel = 0;
                foreach (var a in kinds) foreach (var b in kinds)
                {
                    if (RM_LineLook.Couples(a, b) != RM_LineLook.Couples(b, a)) casym++;
                    if (RM_LineLook.Joins(RM_LinePart.Reel, b)) touchReel++;
                }
                Console.WriteLine($"      hose couplings asymmetric {casym} (limit 0); kinds a reel joins by touch {touchReel} (limit 0)");
                Assert(casym == 0, "Couples must read the same both ways");
                Assert(touchReel == 0, "a reel joins only through its hose, never by standing beside a part");
                Assert(RM_LineLook.Couples(RM_LinePart.Reel, RM_LinePart.Tank) && RM_LineLook.Couples(RM_LinePart.Reel, RM_LinePart.Reel)
                       && RM_LineLook.Couples(RM_LinePart.Reel, RM_LinePart.Machine) && RM_LineLook.Couples(RM_LinePart.Reel, RM_LinePart.Pipe),
                    "a hose couples its reel to a tank, a machine, a pipe or a relay reel");
                Assert(!RM_LineLook.Couples(RM_LinePart.Tank, RM_LinePart.Pipe) && !RM_LineLook.Couples(RM_LinePart.Reel, RM_LinePart.None),
                    "can-fail: a coupling needs a reel at one end and a FlowWorks part at the other");
            });

            Case("LineLook_touch_joins_without_a_pipe", () =>
            {
                // a pump touching a tank (no pipe): one line; a tank touching that tank: not; a pump touching that pump: not
                var g = new Fake();
                P t1 = g.Add("t1", RM_LinePart.Tank, 0, 0), pump = g.Add("pump", RM_LinePart.Machine, 1, 1);
                P t2 = g.Add("t2", RM_LinePart.Tank, -1, 0), m2 = g.Add("m2", RM_LinePart.Machine, 2, 2);
                string a = Names(g.Pick("Modern", t1)), b = Names(g.Pick("Modern", pump));
                Console.WriteLine($"      from t1: {a}; from pump: {b} (want m2? no, t2? no)");
                Assert(a == "pump,t1" && b == "pump,t1", "tank-pump by touch: one line, the touching tank and machine stay out");
            });

            Case("LineLook_non_flowworks_on_a_cell_is_passed_over", () =>
            {
                // a wall / GSS thing standing ON a pipe cell mid-run: never changed, the pipe goes on through it
                var g = new Fake();
                g.Run(0, 6, 0);
                P wall = g.OnCell("wall", 3, 0, ours: false);
                P far = g.Add("tank", RM_LinePart.Tank, 7, 0);
                List<P> ch = g.Pick("Industrial", g.Cell(0, 0));
                Console.WriteLine($"      changed {ch.Count} (want 8: 7 pipes + the tank); wall changed: {ch.Contains(wall)}");
                Assert(ch.Count == 8 && ch.Contains(far) && !ch.Contains(wall), "a foreign thing on a pipe cell is skipped, not a break");
            });

            Case("LineLook_non_flowworks_conductor_is_not_a_join", () =>
            {
                // a VE / foreign pipe between two FlowWorks runs: the net conducts nothing through it, so neither does the look;
                // a foreign tank between two runs likewise (and is never restyled)
                var g = new Fake();
                g.Run(0, 2, 0); g.Pipe(3, 0, ours: false); g.Run(4, 6, 0);
                int a = g.Pick("Modern", g.Cell(0, 0)).Count;
                var h = new Fake();
                h.Run(0, 2, 0);
                P foreign = h.Add("theirs", RM_LinePart.Tank, 3, 0, player: false);
                h.Run(4, 6, 0);
                List<P> b = h.Pick("Modern", h.Cell(0, 0));
                Console.WriteLine($"      across a foreign pipe: {a} (want 3); across a foreign tank: {b.Count} (want 3), theirs changed: {b.Contains(foreign)}");
                Assert(a == 3 && b.Count == 3 && !b.Contains(foreign), "a non-FlowWorks or foreign conductor ends the line");
            });

            Case("LineLook_a_part_without_the_look_keeps_its_own", () =>
            {
                var (g, at) = Station24();
                at["head"].Looks.Remove("Futuristic");               // a kind with no Futuristic style
                at["pipe3,0"].Stored = "Futuristic";                 // already wearing it
                List<P> ch = g.Pick("Futuristic", at["pump"]);
                Console.WriteLine($"      changed {ch.Count} (want 8: 10 parts less the head with no style and the pipe already wearing it)");
                Assert(ch.Count == 8 && !ch.Contains(at["head"]) && !ch.Contains(at["pipe3,0"]), "no style: keeps; already: untouched");
                // the walk still passes THROUGH the head (it is a line part, only its art has no such look)
                at["head"].Looks.Add("Futuristic");
                Assert(g.Pick("Bogus", at["pump"]).Count == 0, "can-fail: a look no part has changes nothing");
            });

            Case("LineLook_one_tank_joins_several_runs", () =>
            {
                // a 2x2 tank with runs leaving west, east and north, each to a pump: picking on one far pump reaches all three
                var g = new Fake();
                g.Add("tank", RM_LinePart.Tank, 0, 0, 1, 1);
                g.Run(-4, -1, 0); g.Run(2, 5, 1);
                for (int z = 2; z <= 5; z++) g.Pipe(0, z);
                P w = g.Add("pw", RM_LinePart.Machine, -5, 0), e = g.Add("pe", RM_LinePart.Machine, 6, 1), n = g.Add("pn", RM_LinePart.Machine, 0, 6);
                List<P> ch = g.Pick("Modern", w);
                Console.WriteLine($"      from the west pump: {ch.Count} part(s) (want 16: tank, 12 pipes, 3 pumps)");
                Assert(ch.Count == 16 && ch.Contains(e) && ch.Contains(n), "one tank joins every run it touches");
            });

            Case("LineLook_hose_relay_and_free_end", () =>
            {
                // reel A on a tank, hose onto relay reel B, B's hose free end coupled to a second tank T2 (no pipe anywhere)
                var g = new Fake();
                P t1 = g.Add("t1", RM_LinePart.Tank, 0, 0), a = g.Add("A", RM_LinePart.Reel, 2, 0, 3, 1);
                P b = g.Add("B", RM_LinePart.Reel, 20, 0, 21, 1), t2 = g.Add("t2", RM_LinePart.Tank, 40, 0);
                g.Hoses.Add((a, t1)); g.Hoses.Add((a, b)); g.Hoses.Add((b, t2));
                string from = Names(g.Pick("Industrial", t2));
                Console.WriteLine($"      from t2: {from} (want A,B,t1,t2)");
                Assert(from == "A,B,t1,t2", "a hose coupling and a relay carry the line");
            });

            Case("LineLook_cap_cuts_nearest_first", () =>
            {
                var g = new Fake();
                g.Run(0, 99, 0);
                List<P> ch = g.Pick("Modern", out bool capped, 40, g.Cell(50, 0));
                int far = ch.Max(p => Math.Abs(p.X0 - 50));
                Console.WriteLine($"      100-pipe run, cap 40: changed {ch.Count} (limit 40), capped {capped}, farthest {far} from the start (limit 20)");
                Assert(ch.Count == 40 && capped && far <= 20, "the cap keeps the nearest parts and reports the cut");
                g.Pick("Modern", out bool c2, 100, g.Cell(0, 0));
                Assert(!c2, "can-fail: a run that fits is not reported capped");
            });

            Case("LineLook_multi_select_is_the_union", () =>
            {
                var g = new Fake();
                g.Run(0, 2, 0); g.Run(0, 2, 5);
                int one = g.Pick("Modern", g.Cell(0, 0)).Count, both = g.Pick("Modern", g.Cell(0, 0), g.Cell(2, 5)).Count;
                int same = g.Pick("Modern", g.Cell(0, 0), g.Cell(2, 0)).Count;
                Console.WriteLine($"      one start {one} (want 3), two lines {both} (want 6), two starts on one line {same} (want 3)");
                Assert(one == 3 && both == 6 && same == 3, "several selected parts: the union of their lines, no part twice");
            });

            Case("LineLook_pole_span_joins_runs", () =>
            {
                // pipe-pole span: two runs joined only by a span edge (the adapter lists span edges with the cardinal ones)
                var g = new Fake();
                g.Run(0, 2, 0); g.Run(10, 12, 0);
                g.Spans[(2, 0)] = new List<(int, int)> { (10, 0) };
                g.Spans[(10, 0)] = new List<(int, int)> { (2, 0) };
                int n = g.Pick("Modern", g.Cell(0, 0)).Count;
                Console.WriteLine($"      across a pole span: {n} (want 6)");
                Assert(n == 6, "a pole span carries the line");
            });

            Case("LineLook_reel_beside_is_not_coupled", () =>
            {
                // a reel standing 8-way beside a pipe, a tank and a pump, with its hose stored (no coupling): not on the line.
                // The same reel with its body coupled to the tank: on it.
                var g = new Fake();
                g.Run(0, 3, 0);
                P tank = g.Add("tank", RM_LinePart.Tank, 4, 0), pump = g.Add("pump", RM_LinePart.Machine, 0, 1);
                P reel = g.Add("reel", RM_LinePart.Reel, 1, 1, 2, 2);
                string loose = Names(g.Pick("Modern", g.Cell(0, 0)));
                bool fromReel = g.Pick("Modern", reel).Contains(tank);
                g.Hoses.Add((reel, tank));
                string coupled = Names(g.Pick("Modern", g.Cell(0, 0)));
                Console.WriteLine($"      loose reel: line {loose}; from the reel reaches the tank {fromReel} (want False); coupled: {coupled}");
                Assert(!loose.Contains("reel") && !fromReel, "a reel beside a part, hose not coupled, is not on its line");
                Assert(coupled.Contains("reel") && coupled.Contains("tank") && coupled.Contains("pump"), "can-fail: the coupled reel is on the line");
            });

            Case("LineLook_every_choose_style_gizmo_walks_the_line", () =>
            {
                // Wiring of the shipped mod to this decision: every FlowWorks line part's Choose style goes through the one line
                // menu (PipeLook.LineLookGizmo -> MapLineGraph -> RM_LineLook.Changes); none restyles a same-def run, one thing or
                // the selection alone; the parts that had no button (head, faucet, pole) carry the line gizmo.
                string pl = RiverSwitchFlipChecks.Src("Machinery/PipeLook.cs"), reel = RiverSwitchFlipChecks.Src("Hose/CompHoseReel.cs");
                var misses = new List<string>();
                int read = 0;
                foreach (string cls in new[] { "CompPipeLook", "CompTankLook", "CompLineLook" })
                {
                    read++;
                    string body = ClassBody(pl, "public class " + cls + " ");
                    if (body == null || !body.Contains("PipeLook.LineLookGizmo(parent)")) misses.Add(cls + " gizmo not the line menu");
                }
                read++;
                if (!reel.Contains("PipeLook.LineLookGizmo(parent)")) misses.Add("CompHoseReel gizmo not the line menu");
                if (reel.Contains("() => SetLook(l)")) misses.Add("CompHoseReel still has its own one-reel menu");
                read++;
                if (pl.Contains("PipeLook.RunOf(") || pl.Contains("SelectedTanks()")) misses.Add("a same-def run or selection-only restyle is still wired");
                read++;
                if (!pl.Contains("RM_LineLook.Changes(")) misses.Add("PipeLook does not decide through RM_LineLook.Changes");
                string defs = Path.GetDirectoryName(ContainerMatFixture.Root());
                foreach (var (file, def) in new[] { ("Sprinklers/RM_Sprinklers.xml", "RM_SprinklerHead"), ("Thirst/RM_PipeFaucet.xml", "RM_PipeFaucet"),
                                                    ("Machinery/RM_PipePoles.xml", "RM_PipePole") })
                {
                    read++;
                    XElement t = XDocument.Load(Path.Combine(defs, file)).Descendants("ThingDef").FirstOrDefault(e => (string)e.Element("defName") == def);
                    bool has = t?.Element("comps")?.Elements("li").Any(li => (string)li.Attribute("Class") == "RimMandrake.FlowWorks.Machinery.CompProperties_LineLook") == true;
                    if (!has) misses.Add(def + " has no line Choose style (CompProperties_LineLook)");
                }
                Console.WriteLine($"      read {read} wirings; misses {misses.Count} (limit 0): {string.Join("; ", misses)}");
                Assert(misses.Count == 0, "every Choose style walks the line");
            });

            Case("LineLook_fitting_start_walks_its_pipe", () =>
            {
                // the faucet clicked: the whole station-24 line; a faucet on no pipe: itself only; a faucet beside a pipe (not on
                // it) never joins it by touch
                var (g, at) = Station24();
                int whole = g.Pick("Industrial", g.Cell(2, 0)).Count, fromFaucet = g.Pick("Industrial", at["faucet"]).Count;
                P lone = g.OnCell("lone", 30, 30);
                P beside = g.OnCell("beside", 3, 1);
                string loneCh = Names(g.Pick("Industrial", lone));
                bool besideJoined = g.Pick("Industrial", g.Cell(2, 0)).Contains(beside);
                Console.WriteLine($"      from the faucet {fromFaucet} (want {whole}: the line from a pipe); lone faucet: {loneCh}; faucet beside the run joined {besideJoined} (want False)");
                Assert(whole == 10 && fromFaucet == whole, "a fitting clicked starts the walk at its pipe cell");
                Assert(loneCh == "lone" && !besideJoined, "a fitting on no pipe changes itself only, and joins nothing by touch");
            });
        }
    }
}
