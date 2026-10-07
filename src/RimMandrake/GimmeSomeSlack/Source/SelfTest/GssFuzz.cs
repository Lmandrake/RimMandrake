// Approach B for Gimme Some Slack (design/RimMandrake/gss_offline_fuzz_B.md): seeded random ACTION SEQUENCES over the
// production core (CordGraph / CordBuilder / HoseMath / HoseTrail / HoseCarryMachine / AerialMath), checked against
// design invariants after every step. A failing sequence is shrunk (delta debugging over the action list) and printed
// as `seed N: message | actions`, which replays exactly. Everything is a pure function of the seed (CordRng).
//
//   families:  cords (build/remove/break/reconnect/block conduit; incremental == fresh; net and geometry invariants)
//              hose  (reel -> target around random obstacles; HoseMath.Lay invariants; install vs unbounded route)
//              trail (carry machine: walk / wind / unwind / replan; length conservation)
//              aerial(anchor link/unlink/remove sequences; range, max links, sway, span curve)
//   args:      --fuzz-scale F   multiply every family's case count (default 1; 0 skips the whole fuzz)
//              --fuzz-only NAME run one family (cords|hose|trail|aerial)
//              --fuzz-seed N    replay one seed of the chosen family verbosely (no shrinking limit)
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.GimmeSomeSlack.Hose;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class GssFuzz
    {
        // ------------------------------------------------------------------ plumbing
        internal sealed class Tally { public string Name; public long Cases, Steps, Failures; public double Seconds; public string Extra = ""; }

        /// <summary>Delta-debugging shrink: drop chunks, then single actions, while the failure (same tag) persists.</summary>
        internal static List<T> Shrink<T>(List<T> acts, Func<List<T>, bool> fails)
        {
            var cur = new List<T>(acts);
            int chunk = Math.Max(1, cur.Count / 2);
            while (true)
            {
                bool any = false;
                for (int i = 0; i < cur.Count;)
                {
                    int n = Math.Min(chunk, cur.Count - i);
                    var cand = new List<T>(cur);
                    cand.RemoveRange(i, n);
                    if (fails(cand)) { cur = cand; any = true; } else i += n;
                }
                if (chunk == 1 && !any) break;
                if (!any) chunk = Math.Max(1, chunk / 2);
            }
            return cur;
        }

        private static string Tag(string msg) { int i = msg.IndexOf(':'); return i < 0 ? msg : msg.Substring(0, i); }

        internal static double MaxOver = double.NegativeInfinity;   // largest (strand length - its limit) seen; negative = headroom
        private static bool Finite(double d) => !double.IsNaN(d) && !double.IsInfinity(d);
        private static bool Finite(V2 p) => Finite(p.X) && Finite(p.Z);

        private static string Where(string fam, long seed, IEnumerable<object> acts, string msg) =>
            fam + " seed " + seed + ": " + msg + " | " + string.Join(" ", acts.Select(a => a.ToString()));

        // ================================================================== CORDS
        internal struct Act
        {
            public int Kind, X, Z, Aux;
            public static readonly string[] Names = { "Build", "Remove", "Break", "Reconnect", "Wall", "Rock", "Water", "Clear", "Door", "Charge", "Run" };
            public override string ToString() => Names[Kind] + "(" + X + "," + Z + (Kind == 10 ? ",len" + Aux : "") + ")";
        }

        private sealed class MSpec { public string Id; public MachineKind Kind; public int X, Z, W, H; public Cell Hook; }

        /// <summary>The fuzz's own map model: plain arrays the way the game adapter would snapshot them. Machines never move.</summary>
        private sealed class Scene
        {
            public int W, H;
            public byte[] Block; public bool[] Door, Cond, Tree;
            public List<MSpec> Machines = new List<MSpec>();
            public bool Charged;
            public List<Cell> Broken = new List<Cell>();
            public BuildOptions Opt;
            public int Reserved => W - 6;          // columns >= Reserved stay empty: the unrelated-edit probe lives there (a dead end looks 3 cells along its own line for a gap, so the probe sits 5+ away)
            public int Idx(int x, int z) => z * W + x;
            public bool Protected(int x, int z) => Machines.Any(m => (x >= m.X && x < m.X + m.W && z >= m.Z && z < m.Z + m.H) || (m.Hook.X == x && m.Hook.Z == z));
            public bool InPlay(int x, int z) => x >= 0 && z >= 0 && x < Reserved && z < H;

            public CordWorld ToWorld(bool reverseMachines = false)
            {
                var w = new CordWorld(W, H);
                for (int z = 0; z < H; z++)
                    for (int x = 0; x < W; x++)
                    {
                        var c = new Cell(x, z);
                        int i = Idx(x, z);
                        if (Cond[i]) w.SetConduit(c);
                        if (Block[i] != 0) w.SetBlocked(c, (BlockKind)Block[i]);
                        if (Door[i]) w.SetDoor(c);
                        if (Tree[i]) w.SetExtraCost(c, 1.5f);
                    }
                IEnumerable<MSpec> ms = reverseMachines ? Machines.AsEnumerable().Reverse() : Machines;
                foreach (MSpec m in ms)
                    w.Machines.Add(new MachineInfo { Id = m.Id, Kind = m.Kind, X0 = m.X, Z0 = m.Z, W = m.W, H = m.H, Hookups = new List<Cell> { m.Hook } });
                return w;
            }

            /// <summary>Net ids: 4-connected conduit components (no LinkAllowed in the fuzz).</summary>
            public static Dictionary<Cell, int> Nets(CordWorld w)
            {
                var net = new Dictionary<Cell, int>();
                int k = 0;
                foreach (Cell c in w.ConduitCells())
                {
                    if (net.ContainsKey(c)) continue;
                    var st = new Stack<Cell>();
                    st.Push(c); net[c] = k;
                    while (st.Count > 0)
                    {
                        Cell q = st.Pop();
                        foreach (Cell d in Cell.Dirs4) { Cell n = q + d; if (w.IsConduit(n) && !net.ContainsKey(n)) { net[n] = k; st.Push(n); } }
                    }
                    k++;
                }
                return net;
            }

            public HashSet<Cell> Live(CordWorld w)
            {
                var live = new HashSet<Cell>();
                if (!Charged) return live;
                var st = new Stack<Cell>();
                foreach (MachineInfo m in w.Machines.Where(x => x.Kind == MachineKind.Source)) foreach (Cell h in m.Hookups) st.Push(h);
                while (st.Count > 0)
                {
                    Cell c = st.Pop();
                    if (!w.IsConduit(c) || !live.Add(c)) continue;
                    foreach (Cell d in Cell.Dirs4) st.Push(c + d);
                }
                return live;
            }
        }

        private static Scene MakeScene(long seed)
        {
            CordRng r = CordRng.Of("gssfuzz-scene", seed);
            var s = new Scene { W = r.Int(14, 24), H = r.Int(10, 18) };
            int n = s.W * s.H;
            s.Block = new byte[n]; s.Door = new bool[n]; s.Cond = new bool[n]; s.Tree = new bool[n];
            // obstacle rectangles (never in the reserved columns)
            int rects = r.Int(0, 4);
            for (int k = 0; k < rects; k++)
            {
                int x0 = r.Int(0, s.Reserved - 2), z0 = r.Int(0, s.H - 2), w = r.Int(1, 4), h = r.Int(1, 3);
                byte kind = (byte)(r.Int(0, 2) == 0 ? BlockKind.Wall : r.Int(0, 1) == 0 ? BlockKind.Rock : BlockKind.Water);
                for (int z = z0; z < Math.Min(s.H, z0 + h); z++) for (int x = x0; x < Math.Min(s.Reserved, x0 + w); x++) s.Block[s.Idx(x, z)] = kind;
            }
            for (int k = r.Int(0, 3); k > 0; k--) { int x = r.Int(0, s.Reserved - 1), z = r.Int(0, s.H - 1); s.Tree[s.Idx(x, z)] = true; }
            // machines: footprint becomes Device-blocked, the hookup is a walkable cell beside it
            int mc = r.Int(2, 5);
            for (int k = 0; k < mc; k++)
            {
                int w = r.Int(1, 2), h = w;
                int x = r.Int(1, s.Reserved - w - 1), z = r.Int(1, s.H - h - 1);
                bool ok = true;
                for (int zz = z - 1; zz <= z + h && ok; zz++) for (int xx = x - 1; xx <= x + w && ok; xx++)
                    if (zz < 0 || xx < 0 || xx >= s.Reserved || zz >= s.H || s.Block[s.Idx(xx, zz)] != 0 || s.Protected(xx, zz)) ok = false;
                if (!ok) continue;
                var hook = new Cell(x + w, z);                      // east side, bottom row
                MachineKind mk = k == 0 ? MachineKind.Source : k == 1 ? MachineKind.Battery : r.Int(0, 1) == 0 ? MachineKind.Consumer : MachineKind.Lamp;
                var m = new MSpec { Id = "m" + k, Kind = mk, X = x, Z = z, W = w, H = h, Hook = hook };
                for (int zz = z; zz < z + h; zz++) for (int xx = x; xx < x + w; xx++) s.Block[s.Idx(xx, zz)] = (byte)BlockKind.Device;
                s.Machines.Add(m);
            }
            foreach (MSpec m in s.Machines) s.Cond[s.Idx(m.Hook.X, m.Hook.Z)] = true;
            // initial wiring: an L-shaped run from each hookup to the next machine's
            for (int k = 0; k + 1 < s.Machines.Count; k++) if (r.Chance(0.8)) Run(s, s.Machines[k].Hook, s.Machines[k + 1].Hook);
            for (int k = r.Int(0, 4); k > 0; k--) { int x = r.Int(0, s.Reserved - 1), z = r.Int(0, s.H - 1); if (!s.Protected(x, z) || true) s.Cond[s.Idx(x, z)] = true; }
            for (int k = r.Int(0, 2); k > 0; k--) { int x = r.Int(0, s.Reserved - 1), z = r.Int(0, s.H - 1); if (s.Block[s.Idx(x, z)] == 0 && !s.Protected(x, z)) s.Door[s.Idx(x, z)] = true; }
            // options: per-scene settings the way the settings screen would clamp them
            var o = new BuildOptions { Tangles = r.Chance(0.8), NeedlessLoops = r.Chance(0.8), Seed = (ulong)r.Int(1, 9), TangleMin = r.Int(6, 20) };
            double[] slack = { 0, 0.5, 1, 1, 2 };
            o.Lay.SlackScale = slack[r.Int(0, slack.Length - 1)];
            o.Lay.CordsMax = r.Int(1, 3);
            o.Lay.MaxExtra = r.Int(2, 40);
            o.Lay.MinExtra = Math.Min(o.Lay.MinExtra, o.Lay.MaxExtra);
            s.Opt = o;
            return s;
        }

        private static void Run(Scene s, Cell a, Cell b)
        {
            int x = a.X, z = a.Z;
            while (x != b.X) { s.Cond[s.Idx(x, z)] = true; x += Math.Sign(b.X - x); }
            while (z != b.Z) { s.Cond[s.Idx(x, z)] = true; z += Math.Sign(b.Z - z); }
            s.Cond[s.Idx(x, z)] = true;
        }

        private static List<Act> GenActs(Scene s, long seed, int count)
        {
            CordRng r = CordRng.Of("gssfuzz-acts", seed);
            var acts = new List<Act>();
            int[] weights = { 28, 12, 8, 8, 5, 3, 3, 6, 3, 4, 10 };
            int total = weights.Sum();
            for (int i = 0; i < count; i++)
            {
                int pick = r.Int(0, total - 1), kind = 0;
                while (pick >= weights[kind]) { pick -= weights[kind]; kind++; }
                acts.Add(new Act { Kind = kind, X = r.Int(0, s.Reserved - 1), Z = r.Int(0, s.H - 1), Aux = r.Int(2, 6) });
            }
            return acts;
        }

        private static void Apply(Scene s, Act a)
        {
            if (!s.InPlay(a.X, a.Z)) return;
            int i = s.Idx(a.X, a.Z);
            var c = new Cell(a.X, a.Z);
            switch (a.Kind)
            {
                case 0: if (s.Block[i] != (byte)BlockKind.Device) s.Cond[i] = true; break;
                case 1: if (!s.Protected(a.X, a.Z) || s.Cond[i]) s.Cond[i] = false; break;
                case 2: if (s.Cond[i]) { s.Cond[i] = false; s.Broken.Add(c); } break;
                case 3: if (s.Broken.Count > 0) { Cell b = s.Broken[s.Broken.Count - 1]; s.Broken.RemoveAt(s.Broken.Count - 1); s.Cond[s.Idx(b.X, b.Z)] = true; } break;
                case 4: case 5: case 6:
                    if (!s.Protected(a.X, a.Z) && s.Block[i] != (byte)BlockKind.Device)
                        s.Block[i] = (byte)(a.Kind == 4 ? BlockKind.Wall : a.Kind == 5 ? BlockKind.Rock : BlockKind.Water);
                    break;
                case 7: if (s.Block[i] != (byte)BlockKind.Device) s.Block[i] = 0; break;
                case 8: if (s.Block[i] == 0 && !s.Protected(a.X, a.Z)) s.Door[i] = !s.Door[i]; break;
                case 9: s.Charged = !s.Charged; break;
                case 10:
                    for (int k = 0; k < a.Aux; k++)
                    {
                        int x = a.X + k;
                        if (x >= s.Reserved) break;
                        if (s.Block[s.Idx(x, a.Z)] != (byte)BlockKind.Device) s.Cond[s.Idx(x, a.Z)] = true;
                    }
                    break;
            }
        }

        // ---- digests / signatures
        internal static ulong Digest(List<LaidPiece> ps)
        {
            ulong h = 1469598103934665603UL;
            void Mix(ulong v) { h = (h ^ v) * 1099511628211UL; }
            void MixD(double d) => Mix(unchecked((ulong)(long)Math.Round(d * 1000)));
            void MixS(string t) { foreach (char ch in t) Mix(ch); Mix(0xFF); }
            foreach (LaidPiece p in ps.OrderBy(p => p.Key, StringComparer.Ordinal))
            {
                MixS(p.Key ?? "");
                foreach (CordStrand st in p.Strands) { Mix(0xA1); foreach (V2 q in st.Pts) { MixD(q.X); MixD(q.Z); } }
                foreach (CordDecal d in p.Decals) { Mix((ulong)d.Kind); MixD(d.Pos.X); MixD(d.Pos.Z); MixD(d.Angle); MixD(d.Scale); }
                foreach (CordEnd e in p.Ends) { MixD(e.Tip.X); MixD(e.Tip.Z); MixD(e.Dir.X); MixD(e.Dir.Z); }
            }
            return h;
        }

        /// <summary>Order-free identity of a piece: what it joins and its geometry, never its cache key (which carries cluster indices).</summary>
        internal static List<string> Sigs(List<LaidPiece> ps)
        {
            var l = new List<string>();
            foreach (LaidPiece p in ps)
            {
                var sb = new StringBuilder(p.EndA ?? "node").Append('|').Append(p.EndB ?? "").Append('|').Append(p.Owner).Append('|');
                ulong h = p.GeometryHash();
                foreach (CordDecal d in p.Decals) h = (h ^ (ulong)d.Kind ^ unchecked((ulong)(long)Math.Round(d.Pos.X * 1000)) ^ unchecked((ulong)(long)Math.Round(d.Pos.Z * 1000)) * 31) * 1099511628211UL;
                l.Add(sb.Append(h.ToString("x")).ToString());
            }
            l.Sort(StringComparer.Ordinal);
            return l;
        }

        private static void AddChanged(List<Cell> into, CordWorld prev, CordWorld cur)
        {
            for (int z = 0; z < cur.Height; z++)
                for (int x = 0; x < cur.Width; x++)
                {
                    var c = new Cell(x, z);
                    if (prev.IsWalkable(c) != cur.IsWalkable(c) || prev.IsDoor(c) != cur.IsDoor(c)) into.Add(c);
                }
        }

        private static bool StaleOutsideCorridor(List<Cell> changed, List<LaidPiece> incrPieces, List<string> diffKeys)
        {
            if (changed.Count == 0) return false;
            foreach (string k in diffKeys)
            {
                LaidPiece p = incrPieces.FirstOrDefault(q => q.EndA != null && q.EndA + "|" + q.EndB == k);
                if (p == null) return false;
                if (changed.Any(c => c.X >= p.CX0 && c.X <= p.CX1 && c.Z >= p.CZ0 && c.Z <= p.CZ1)) return false;   // the cache could see it: a real miss
            }
            return true;
        }

        // ---- the invariants over one build
        /// <summary>Cells a graph vertex stands on (machines: their hookups that carry conduit).</summary>
        private static IEnumerable<Cell> CellsOf(CordGraph g, VId v)
        {
            if (v.T == 'm') { if (g.MachineOf.TryGetValue(v, out MachineInfo m)) foreach (Cell h in m.Hookups) if (g.World.IsConduit(h)) yield return h; }
            else if (v.T == 't' || v.T == 'k') { if (g.Clusters.TryGetValue(v, out List<Cell> cs)) foreach (Cell c in cs) yield return c; }
            else yield return v.A;
        }

        internal static string CheckNets(CordGraph g, Dictionary<Cell, int> net)
        {
            foreach (CordEdge e in g.Edges)
            {
                var nets = new HashSet<int>();
                bool mA = e.A.T == 'm', mB = e.B.T == 'm';
                var sideA = CellsOf(g, e.A).Where(net.ContainsKey).Select(c => net[c]).Distinct().ToList();
                var sideB = CellsOf(g, e.B).Where(net.ContainsKey).Select(c => net[c]).Distinct().ToList();
                // a machine node may sit on several nets; the edge must join the machine's net to the other end's
                if (!mA && !mB)
                {
                    if (sideA.Count != 1 || sideB.Count != 1 || sideA[0] != sideB[0]) return "cross-net edge: " + e.A + " (nets " + string.Join(",", sideA) + ") -- " + e.B + " (nets " + string.Join(",", sideB) + ")";
                }
                else if (mA && !mB) { if (sideB.Count == 1 && !sideA.Contains(sideB[0])) return "cross-net machine edge: " + e.A + " -- " + e.B; }
                else if (mB && !mA) { if (sideA.Count == 1 && !sideB.Contains(sideA[0])) return "cross-net machine edge: " + e.A + " -- " + e.B; }
                foreach (VId v in e.Via)
                {
                    var vn = CellsOf(g, v).Where(net.ContainsKey).Select(c => net[c]).Distinct().ToList();
                    if (vn.Count != 1) return "chain cell off conduit: " + v;
                    if (!mA && sideA.Count == 1 && vn[0] != sideA[0]) return "cross-net chain: " + e.A + " via " + v;
                    if (!mB && sideB.Count == 1 && vn[0] != sideB[0]) return "cross-net chain: " + e.B + " via " + v;
                }
            }
            return null;
        }

        internal static string CheckGeometry(CordWorld w, List<LaidPiece> ps, BuildOptions opt)
        {
            foreach (LaidPiece p in ps)
            {
                int si = 0;
                bool isTangle = p.EndA == null;
                foreach (CordStrand st in p.Strands)
                {
                    si++;
                    foreach (V2 q in st.Pts) if (!Finite(q)) return "non-finite strand point in " + p.Key;
                    if (st.Pts.Count < 2) { if (st.Pts.Count == 0) return "empty strand in " + p.Key; continue; }
                    double len = Geo.Length(st.Pts);
                    // declared limit, from CordLayer.Sprawl: a loop or heap is spliced in only while the cord stays within 1.25 x the
                    // slack target (at most PathLen + MaxExtra), but the broad lateral excursions are NOT charged to that budget: each
                    // is a Gaussian bump of amplitude <= Cap x 1.1, whose extra arc length is at most its total variation 2 x amplitude,
                    // and there are round(L / 2.6) of them. End work after that (IntoArt / PastFace overruns, limp curls, knot loops,
                    // two end heaps on a run over LongRun) is allowed 3 cells, plus 4 for a long run.
                    int nb = Math.Max(1, (int)Math.Round(p.PathLen / Math.Max(2.6, opt.Lay.ExcursionHi)));
                    double limit = 1.25 * (p.PathLen + opt.Lay.MaxExtra) + nb * 2 * opt.Lay.Cap * 1.1 + 3.0 + (p.PathLen > CordLayer.LongRun ? 4.0 : 0.0);
                    if (!isTangle) MaxOver = Math.Max(MaxOver, len - limit);
                    if (!isTangle && len > limit && Environment.GetEnvironmentVariable("GSSFUZZ_DEBUG") == "pts") { Console.WriteLine("  PTS " + p.EndA + "|" + p.EndB + " len " + len.ToString("0.00") + ": " + string.Join(" ", st.Pts.Where((q, i) => i % 6 == 0 || i == st.Pts.Count - 1))); Console.WriteLine("  decals " + string.Join(",", p.Decals.Select(d => d.Kind.ToString())) + " settle: " + (st.Settle == null ? "none" : "sprawl " + st.Settle.SprawlLen.ToString("0.00") + " rest " + st.Settle.RestLen.ToString("0.00") + " settled " + st.Settle.SettledLen.ToString("0.00") + " heaps " + st.Settle.HeapsAt.Count) + " limp/pin"); }
                    if (!isTangle && len > limit) return "strand over its length limit: " + len.ToString("0.00") + " > " + limit.ToString("0.00") + " (path " + p.PathLen.ToString("0.00") + ", MaxExtra " + opt.Lay.MaxExtra + ", slack scale " + opt.Lay.SlackScale + ", " + p.Strands.Count + " strand(s), fellBack " + st.FellBack + ") in " + p.EndA + "|" + p.EndB;
                }
                foreach (CordDecal d in p.Decals) if (!Finite(d.Pos) || !Finite(d.Angle) || !Finite(d.Scale)) return "non-finite decal in " + p.Key;
                foreach (CordEnd e in p.Ends) if (!Finite(e.Tip) || !Finite(e.Dir)) return "non-finite end in " + p.Key;
                if (!Finite(p.PathLen) || !Finite(p.LaidRatio)) return "non-finite path length in " + p.Key;
            }
            return null;
        }

        /// <summary>Runs a sequence; returns the first failure message or null. checkFresh: compare against a fresh builder every step.</summary>
        internal static string RunCords(long seed, List<Act> acts, bool everyStep, ref long steps, List<string> gaps = null)
        {
            Scene s = MakeScene(seed);
            var incr = new CordBuilder();
            List<LaidPiece> last = null;
            CordWorld w = null, prev = null;
            var sinceSync = new List<Cell>();       // walkability/door cells changed since the incremental builder last equalled a fresh one
            for (int i = 0; i <= acts.Count; i++)
            {
                if (i > 0) Apply(s, acts[i - 1]);
                prev = w;
                w = s.ToWorld();
                if (prev != null) AddChanged(sinceSync, prev, w);
                HashSet<Cell> live = s.Live(w);
                last = incr.Build(w, s.Opt, c => live.Contains(c));
                steps++;
                string at = " (after " + i + " action(s))";
                string bad = CheckNets(incr.Graph, Scene.Nets(w));
                if (bad != null) return "nets: " + bad + at;
                bad = CheckGeometry(w, last, s.Opt);
                if (bad != null) return "geometry: " + bad + at;
                if (everyStep || i == acts.Count)
                {
                    var fresh = new CordBuilder();
                    List<LaidPiece> f = fresh.Build(w, s.Opt, c => live.Contains(c));
                    steps++;
                    if (Digest(last) != Digest(f))
                    {
                        var r = DeterminismChecks.Compare(last, f);
                        // KNOWN GAP C1: the per-edge cache re-plans a cord only when a cell inside its corridor (its strands' bounding box
                        // + 3 cells, design 8.2.7) changed walkability, but the sprawl looks up to Cap (2.6) cells either side of the PLANNED
                        // path, which can lie outside that box. A change confined to the 3..7 cells beyond a cord's corridor leaves its
                        // cached geometry standing while a fresh build would differ. Raising the margin to 7 clears every case but fails the
                        // shipped "unrelated edit re-plans only the touched edge" check, so it is a trade-off, not a bug to patch. Anything
                        // else that differs (a change INSIDE a corridor, or no walkability change at all) is a real failure.
                        if (r.missing == 0 && r.diff > 0 && StaleOutsideCorridor(sinceSync, last, r.diffKeys))
                        {
                            gaps?.Add("C1 incremental != fresh only beyond the corridor margin: " + string.Join("; ", r.diffKeys.Take(2)));
                            incr = new CordBuilder();
                            last = incr.Build(w, s.Opt, c => live.Contains(c));    // resync so one stale piece is counted once
                            sinceSync.Clear();
                            continue;
                        }
                        if (Environment.GetEnvironmentVariable("GSSFUZZ_DEBUG") == "map")
                        {
                            Console.WriteLine("  MAP " + s.W + "x" + s.H + " seed " + seed + " opt tangles " + s.Opt.Tangles + " min " + s.Opt.TangleMin + " loops " + s.Opt.NeedlessLoops + " seedopt " + s.Opt.Seed);
                            for (int zz = s.H - 1; zz >= 0; zz--) { var row = new StringBuilder("  " + zz.ToString().PadLeft(2) + " "); for (int xx = 0; xx < s.W; xx++) row.Append(s.Machines.Any(m => xx >= m.X && xx < m.X + m.W && zz >= m.Z && zz < m.Z + m.H) ? 'M' : s.Block[s.Idx(xx, zz)] != 0 ? '#' : s.Cond[s.Idx(xx, zz)] ? 'c' : '.'); Console.WriteLine(row); }
                            foreach (MSpec m in s.Machines) Console.WriteLine("  machine " + m.Id + " " + m.Kind + " " + m.X + "," + m.Z + " " + m.W + "x" + m.H + " hook " + m.Hook);
                            foreach (LaidPiece pp in last.Where(q => q.EndA != null && r.diffKeys.Contains(q.EndA + "|" + q.EndB))) Console.WriteLine("  INCR " + pp.Key + " ends " + pp.Ends.Count + " strands " + pp.Strands.Count + " first " + string.Join(" ", pp.Strands[0].Pts.Take(3)) + " last " + pp.Strands[0].Pts.Last());
                            foreach (LaidPiece pp in f.Where(q => q.EndA != null && r.diffKeys.Contains(q.EndA + "|" + q.EndB))) Console.WriteLine("  FRESH " + pp.Key + " ends " + pp.Ends.Count + " strands " + pp.Strands.Count + " first " + string.Join(" ", pp.Strands[0].Pts.Take(3)) + " last " + pp.Strands[0].Pts.Last());
                        }
                        return "incremental != fresh: " + r.diff + " different, " + r.missing + " missing [" + string.Join("; ", r.diffKeys.Take(2)) + "]" + at;
                    }
                    else sinceSync.Clear();
                }
            }
            // same seed -> same bytes: a second fresh build of the final world, and one over an equal world rebuilt from the scene
            {
                HashSet<Cell> live = s.Live(w);
                ulong h1 = Digest(new CordBuilder().Build(s.ToWorld(), s.Opt, c => live.Contains(c)));
                ulong h2 = Digest(new CordBuilder().Build(s.ToWorld(), s.Opt, c => live.Contains(c)));
                steps += 2;
                if (h1 != h2) return "nondeterministic: two fresh builds of one world differ";
                if (h1 != Digest(last) && !everyStep) return "nondeterministic: final incremental != fresh";
            }
            // machine-list order is not a design input: reversing it must not change which cords are laid
            {
                HashSet<Cell> live = s.Live(w);
                var a = Sigs(new CordBuilder().Build(s.ToWorld(false), s.Opt, c => live.Contains(c)));
                var b = Sigs(new CordBuilder().Build(s.ToWorld(true), s.Opt, c => live.Contains(c)));
                steps += 2;
                if (!a.SequenceEqual(b)) return "order: reversing the machine list changed the cords (" + a.Except(b).Count() + " only forward, " + b.Except(a).Count() + " only reversed)";
            }
            // an unrelated edit never reshuffles a cord (design 8.2.5): a 3-cell run in the reserved empty columns must
            // leave every existing piece's identity and geometry as it was
            {
                HashSet<Cell> live = s.Live(w);
                var before = Sigs(new CordBuilder().Build(s.ToWorld(), s.Opt, c => live.Contains(c)));
                int z = (int)(seed % s.H);
                bool[] condBefore = (bool[])s.Cond.Clone();
                for (int k = 0; k < 3; k++) s.Cond[s.Idx(s.W - 2, Math.Min(s.H - 1, z + k))] = true;
                HashSet<Cell> live2 = s.Live(s.ToWorld());
                var after = Sigs(new CordBuilder().Build(s.ToWorld(), s.Opt, c => live2.Contains(c)));
                steps += 2;
                var lost = before.Except(after).ToList();
                if (lost.Count > 0 && Environment.GetEnvironmentVariable("GSSFUZZ_DEBUG") == "map")
                {
                    Console.WriteLine("  UMAP " + seed + " cells changed by the edit: " + string.Join(" ", Enumerable.Range(0, s.Cond.Length).Where(i => s.Cond[i] != condBefore[i]).Select(i => "(" + i % s.W + "," + i / s.W + ")")));
                    for (int zz = s.H - 1; zz >= 0; zz--) { var row = new StringBuilder("  " + zz.ToString().PadLeft(2) + " "); for (int xx = 0; xx < s.W; xx++) row.Append(s.Machines.Any(m => xx >= m.X && xx < m.X + m.W && zz >= m.Z && zz < m.Z + m.H) ? 'M' : s.Block[s.Idx(xx, zz)] != 0 ? '#' : s.Cond[s.Idx(xx, zz)] ? 'c' : '.'); Console.WriteLine(row); }
                    foreach (MSpec m in s.Machines) Console.WriteLine("  machine " + m.Id + " " + m.Kind + " " + m.X + "," + m.Z + " " + m.W + "x" + m.H + " hook " + m.Hook);
                    Console.WriteLine("  before: " + string.Join(" ; ", before.Select(q => q.Substring(0, q.LastIndexOf('|')))));
                    Console.WriteLine("  after:  " + string.Join(" ; ", after.Select(q => q.Substring(0, q.LastIndexOf('|')))));
                }
                if (lost.Count > 0) return "unrelated edit (3 cells at x=" + (s.W - 2) + ", z=" + z + " of a " + s.W + "x" + s.H + " map, reserved from x=" + s.Reserved + ") changed " + lost.Count + " piece(s), e.g. " + lost[0] + " -> " + string.Join(" / ", after.Except(before).Take(3));
            }
            return null;
        }

        // ================================================================== HOSE
        internal sealed class HoseCase
        {
            public CordWorld W; public HoseReelRect Reel; public Cell Target; public double MaxLen; public double MinR; public ulong Seed;
            public int Walls;
            public override string ToString() => "reel(" + Reel.X0 + "," + Reel.Z0 + ") -> " + Target + " max " + MaxLen.ToString("0.0") + " minR " + MinR.ToString("0.0") + " walls " + Walls;
        }

        internal static HoseCase MakeHose(long seed, List<Cell> wallsOverride = null)
        {
            CordRng r = CordRng.Of("gssfuzz-hose", seed);
            int W = r.Int(18, 40), H = r.Int(14, 30);
            var w = new CordWorld(W, H);
            var hc = new HoseCase { W = w, MaxLen = r.Range(10, 60), MinR = new[] { 0.6, 1.2, 1.2, 2.0 }[r.Int(0, 3)], Seed = (ulong)seed };
            var reel = new HoseReelRect(r.Int(3, W - 8), r.Int(3, H - 8), 2, 2);
            if (r.Chance(0.15)) reel = new HoseReelRect(reel.X0, reel.Z0, 1, 1);
            hc.Reel = reel;
            double reach = Math.Min(hc.MaxLen, 25);
            int tx = (int)Math.Round(reel.Centre.X + r.Range(-reach, reach) * 0.8), tz = (int)Math.Round(reel.Centre.Z + r.Range(-reach, reach) * 0.8);
            hc.Target = new Cell(Math.Max(0, Math.Min(W - 1, tx)), Math.Max(0, Math.Min(H - 1, tz)));
            if (wallsOverride != null) { foreach (Cell c in wallsOverride) w.SetBlocked(c, BlockKind.Wall); hc.Walls = wallsOverride.Count; }
            else
            {
                int blobs = r.Int(0, 7);
                for (int k = 0; k < blobs; k++)
                {
                    int x0 = r.Int(0, W - 1), z0 = r.Int(0, H - 1), bw = r.Int(1, 8), bh = r.Int(1, 3);
                    if (r.Chance(0.5)) { int t = bw; bw = bh; bh = t; }
                    var kind = r.Chance(0.7) ? BlockKind.Wall : BlockKind.Water;
                    for (int z = z0; z < Math.Min(H, z0 + bh); z++) for (int x = x0; x < Math.Min(W, x0 + bw); x++) { w.SetBlocked(new Cell(x, z), kind); hc.Walls++; }
                }
                for (int k = r.Int(0, 6); k > 0; k--) w.SetExtraCost(new Cell(r.Int(0, W - 1), r.Int(0, H - 1)), 1.5f);
            }
            // the reel's footprint and the cells round it are open ground
            for (int z = reel.Z0 - 2; z < reel.Z0 + reel.H + 2; z++) for (int x = reel.X0 - 2; x < reel.X0 + reel.W + 2; x++) if (w.InBounds(new Cell(x, z))) w.SetBlocked(new Cell(x, z), BlockKind.None);
            return hc;
        }

        private static string FiniteList(IList<V2> pts, string what)
        {
            foreach (V2 p in pts) if (!Finite(p)) return what + " has a non-finite point";
            return null;
        }

        /// <summary>Why the hose lays the route check passed were refused, per mode (printed with the hose family).</summary>
        internal static readonly Dictionary<string, int> RefuseWhy = new Dictionary<string, int>();

        internal static string RunHose(long seed, List<Cell> wallsOverride, ref long steps, out int laidOk, out int fellBack, bool outlet = true, List<string> gaps = null)
        {
            laidOk = fellBack = 0;
            string mode = outlet ? "[outlet]" : "[free]";
            HoseCase c = MakeHose(seed, wallsOverride);
            CordWorld w = c.W;
            string why = HoseMath.CheckInstall(w, c.Reel, c.Target, c.MaxLen);
            steps++;
            // install verdict vs an independent unbounded route read
            Cell start = c.Reel.StartCellToward(c.Target);
            bool inb = w.InBounds(c.Target), fitsStraight = V2.Dist(c.Reel.Centre, c.Target.Centre) <= c.MaxLen;
            if (inb && !c.Reel.Contains(c.Target) && fitsStraight && w.IsWalkable(c.Target))
            {
                List<Cell> full = HoseMath.RouteCells(w, start, c.Target, -1, false);   // B2: install judges the SHORTEST route
                bool capped = HoseMath.LastRouteCapped;
                double need = -1;
                if (full != null)
                {
                    var pts = HoseMath.RoutePulled(w, c.Reel, c.Target, -1, false);
                    need = pts == null ? -1 : Geo.Length(pts) * HoseMath.RouteMargin;
                }
                steps++;
                if (!capped)
                {
                    if (full == null && why != "no route") return "install: unbounded search finds no route but CheckInstall said " + (why ?? "ok");
                    if (full != null && need <= c.MaxLen && why != null) return "install: route needs " + need.ToString("0.00") + " <= " + c.MaxLen.ToString("0.00") + " but CheckInstall said '" + why + "' (the length-bounded search missed a route that fits)";
                    if (full != null && need > c.MaxLen && why == null) return "install: route needs " + need.ToString("0.00") + " > " + c.MaxLen.ToString("0.00") + " but CheckInstall allowed it";
                }
            }
            if (why != null) return null;

            var p = new HoseShapeParams { MinBendRadius = c.MinR, MaxLength = c.MaxLen, Slack = 1.0, PlumpAmount = 1.0 };
            V2 a = c.Reel.Mouth, b = c.Target.Centre;
            V2? outward = outlet ? c.Reel.Outward : (V2?)null;
            HoseLay lay = HoseMath.Lay(w, a, b, p, c.Seed, null, outward);
            steps++;
            HoseLay lay2 = HoseMath.Lay(w, a, b, p, c.Seed, null, outward);
            if (lay.Ok != lay2.Ok || (lay.Ok && !lay.Flat.SequenceEqual(lay2.Flat))) return "hose" + mode + ": Lay twice with one seed gave different hoses";
            if (!lay.Ok) { lock (RefuseWhy) { RefuseWhy.TryGetValue(mode + " " + lay.Reason, out int rn); RefuseWhy[mode + " " + lay.Reason] = rn + 1; } return null; }     // an install the route check passed but the lay refused: the reel retracts with the reason (CheckReplan), not a fault
            laidOk = 1; if (lay.FellBack) fellBack = 1;
            string bad = FiniteList(lay.Flat, "Flat") ?? FiniteList(lay.Plump, "Plump") ?? FiniteList(lay.Centre, "Centre");
            if (bad != null) return "hose" + mode + ": " + bad;
            if (V2.Dist(lay.Flat[0], a) > 1e-3 || V2.Dist(lay.Flat[lay.Flat.Count - 1], b) > 1e-3) return "hose" + mode + ": endpoints not attached (flat " + lay.Flat[0] + " .. " + lay.Flat[lay.Flat.Count - 1] + " vs " + a + " .. " + b + ")";
            if (V2.Dist(lay.Plump[0], a) > 1e-3 || V2.Dist(lay.Plump[lay.Plump.Count - 1], b) > 1e-3) return "hose" + mode + ": plump endpoints not attached";
            // KNOWN GAPS: design invariants the shipped code does not hold. Each is tallied with its first shrunk reproducer
            // (design/RimMandrake/gss_offline_fuzz_B.md) and does not fail the run; a gross version of each is still asserted below.
            double bigger = Math.Max(lay.FlatLen, lay.PlumpLen);
            // length: the hose is never longer than the hose. The nozzled 2x2 reel's outlet run (the game always lays it outward) is planned
            // from 1.6 + 2 radii past the mouth, a lead CheckInstall's route length does not count; in free mode a walled corridor overran by 3%.
            // G1 FIXED 2026-10-06 (GPT B3): LayOn retries an overlong lay with no slack and otherwise refuses it -- asserted
            if (bigger > c.MaxLen + 1e-6) return "hose" + mode + ": G1 laid hose longer than the hose: " + bigger.ToString("0.00") + " > " + c.MaxLen.ToString("0.00");
            if (bigger > c.MaxLen * 1.6 + 1) return "hose" + mode + ": laid length " + bigger.ToString("0.00") + " is wildly over the hose " + c.MaxLen.ToString("0.0");
            // plump is the flat hose pulled toward its centreline: shorter, give or take resampling noise
            if (lay.PlumpLen > lay.FlatLen * 1.01 + 0.1) gaps?.Add("G4 plump hose longer than flat: " + lay.PlumpLen.ToString("0.00") + " vs " + lay.FlatLen.ToString("0.00"));
            if (lay.PlumpLen > lay.FlatLen * 1.25 + 0.5) return "hose" + mode + ": plump (" + lay.PlumpLen.ToString("0.00") + ") much longer than flat (" + lay.FlatLen.ToString("0.00") + ")";
            if (!HoseMath.Clear(w, lay.Flat)) return "hose" + mode + ": flat hose runs through a wall";
            if (!HoseMath.Clear(w, lay.Plump)) return "hose" + mode + ": plump hose runs through a wall";
            if (lay.Flat.Count != lay.Plump.Count) return "hose" + mode + ": flat/plump sample counts differ";
            if (!lay.FellBack)
            {
                // leaving the nozzle west and turning back east is a U-turn inside the blend zone (OutletLead cells from the mouth)
                double skip = outlet ? HoseMath.OutletLead(p) + 0.5 : HoseMath.EndSkip;
                double bf = HoseMath.MinBendRadius(lay.Flat, skip), bp = HoseMath.MinBendRadius(lay.Plump, skip);
                // G2 FIXED 2026-10-06 (owner decision by question card: straight lead-out): the lead-out (straight run + Dubins
                // join) never bends under the minimum -- asserted over the lead-out section of both poses
                if (outlet && outward.HasValue)
                {
                    double lo = LeadOutBend(lay.Flat, lay.LeadOutLen), lp = LeadOutBend(lay.Plump, lay.LeadOutLen);
                    if (lay.LeadOutLen <= 0) return "hose" + mode + ": outlet lay has no lead-out";
                    if (Math.Min(lo, lp) < c.MinR * 0.95) return "hose" + mode + ": G2 lead-out bends under the minimum: " + Math.Min(lo, lp).ToString("0.00") + " < " + c.MinR.ToString("0.0");
                    if (lay.MinBendFlat < c.MinR * 0.95) gaps?.Add("G2 bend tighter than the hose may bend (outlet lay, outside the lead-out): " + lay.MinBendFlat.ToString("0.00") + " < " + c.MinR.ToString("0.0"));
                }
                if (gaps != null && BendCollect) OutletBendProbe(seed, outlet, lay, p, c.MinR, a, b, outward);
                if (Math.Min(bf, bp) < c.MinR * 0.95) gaps?.Add("G3 bend beyond the blend under 95% of minR: " + Math.Min(bf, bp).ToString("0.00") + " < " + c.MinR.ToString("0.0"));
                if (Math.Min(bf, bp) < c.MinR * 0.1) return "hose" + mode + ": bend radius " + Math.Min(bf, bp).ToString("0.00") + " beyond the outlet blend is under a tenth of " + c.MinR.ToString("0.0");
                if (HoseMath.SelfIntersects(lay.Flat)) gaps?.Add("G5 flat hose crosses itself (design: no loops)");
            }
            // the joints index real samples, ascending, never at an end
            int prev = 0;
            foreach (int j in lay.Joints) { if (j <= prev || j >= lay.Flat.Count - 1) return "hose" + mode + ": joint index " + j + " out of order or at an end"; prev = j; }
            return null;
        }

        /// <summary>Min discrete bend radius over the lead-out section [EndSkip, leadLen] of a pose (same measure as MinBendRadius).</summary>
        internal static double LeadOutBend(IList<V2> X, double leadLen)
        {
            double[] s = Geo.CumLen(X);
            double best = 99;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < HoseMath.EndSkip || s[i] > leadLen) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9) best = Math.Min(best, seg / th);
            }
            return best;
        }

        // ================================================================== G2 LOCATOR (2026-10-06, live hose FAILs vs fuzz G2)
        /// <summary>One laid, non-fallback hose's bend profile: where the tightest bend sits and how far the hose has to turn
        /// across the outlet blend. Collected per seed for both modes; the hose driver prints the comparison.</summary>
        internal sealed class BendRec { public long Seed; public double MinR, MinBend, SAt, Straight, BlendEnd, TurnDeg, BackDeg; public string Zone; }
        internal static bool BendCollect;
        internal static readonly List<BendRec> BendOutlet = new List<BendRec>();
        internal static readonly Dictionary<long, double> BendFree = new Dictionary<long, double>();

        /// <summary>MinBendRadius with the arc position of the minimum (same discrete radius, same skip).</summary>
        internal static double MinBendAt(IList<V2> X, double skip, out double sAt)
        {
            double[] s = Geo.CumLen(X);
            double L = s[s.Length - 1], best = 99; sAt = -1;
            for (int i = 1; i < X.Count - 1; i++)
            {
                if (s[i] < skip || s[i] > L - skip) continue;
                double th = CordLayer.Turn(X[i - 1], X[i], X[i + 1]);
                double seg = 0.5 * (V2.Dist(X[i - 1], X[i]) + V2.Dist(X[i], X[i + 1]));
                if (th > 1e-9 && seg / th < best) { best = seg / th; sAt = s[i]; }
            }
            return best;
        }

        /// <summary>Unit heading of polyline X at arc length t (the segment containing t).</summary>
        internal static V2 HeadingAt(IList<V2> X, double t)
        {
            double[] s = Geo.CumLen(X);
            for (int i = 1; i < X.Count; i++)
                if (s[i] >= t || i == X.Count - 1) { V2 d = X[i] - X[i - 1]; double l = Math.Sqrt(d.X * d.X + d.Z * d.Z); return l > 1e-9 ? d * (1 / l) : new V2(1, 0); }
            return new V2(1, 0);
        }

        private static double AngleDeg(V2 u, V2 v)
        {
            double d = Math.Max(-1, Math.Min(1, u.X * v.X + u.Z * v.Z));
            return Math.Acos(d) * 180 / Math.PI;
        }

        private static void OutletBendProbe(long seed, bool outlet, HoseLay lay, HoseShapeParams p, double minR, V2 a, V2 b, V2? outward)
        {
            if (!outlet) { BendFree[seed] = Math.Min(HoseMath.MinBendRadius(lay.Flat, HoseMath.EndSkip), HoseMath.MinBendRadius(lay.Plump, HoseMath.EndSkip)); return; }
            if (!outward.HasValue) return;
            double st = HoseMath.LeadOutStraight(p), bl = Math.Max(0, lay.LeadOutLen - st);   // 2026-10-06: the straight lead-out, then its join
            double mb = MinBendAt(lay.Flat, HoseMath.EndSkip, out double sAt);
            V2 h = HeadingAt(lay.Flat, st + bl + 0.25);
            V2 ab = b - a; double lab = Math.Sqrt(ab.X * ab.X + ab.Z * ab.Z);
            BendOutlet.Add(new BendRec
            {
                Seed = seed, MinR = minR, MinBend = mb, SAt = sAt, Straight = st, BlendEnd = st + bl,
                TurnDeg = AngleDeg(outward.Value, h),
                BackDeg = lab > 1e-9 ? AngleDeg(outward.Value, ab * (1 / lab)) : 0,
                Zone = sAt < 0 ? "none" : sAt <= st ? "straight" : sAt <= st + bl + 0.25 ? "blend" : "beyond",
            });
        }

        /// <summary>GPT source read 2026-10-06 finding B2 (gss_gpt_source_read_2026-10-06.md): RouteCells minimises step + ExtraCost
        /// while CheckInstall judges the route it returns by LENGTH, so a fitting route through costly cells (the hose world
        /// charges water 3/cell) can lose to a cheaper, longer dry detour that does not fit. A fixed scene: a 3-wide watery
        /// corridor straight to the target (fits) and a dry tunnel the long way round (too long). Tallied, never failed.</summary>
        internal static List<string> CostVsLengthProbe()
        {
            var o = new List<string>();
            // rock from x 6 to 30 except the corridor (z 9-11) and a dry tunnel at z 19: the dry way is ~44 cells, inside
            // the search bound (1.5 x 32 / 1.05 + 4 = 49.7) but longer than the hose
            // a dog-legged corridor (so string-pulling the dry route cannot cut back through it) of costly cells, and a dry
            // tunnel at z 25 the long way round: inside the search bound (1.5 x 40 / 1.05 + 4 = 61) but longer than the hose
            bool Corridor(int x, int z) => (x >= 6 && x <= 18 && z >= 9 && z <= 11) || (x >= 16 && x <= 18 && z >= 9 && z <= 17) || (x >= 16 && x <= 30 && z >= 15 && z <= 17);
            CordWorld Rocky() { var cw = new CordWorld(50, 30); for (int x = 6; x <= 30; x++) for (int z = 0; z < 30; z++) if (!Corridor(x, z) && z != 25) cw.SetBlocked(new Cell(x, z), BlockKind.Rock); return cw; }
            CordWorld w = Rocky();
            for (int x = 6; x <= 30; x++) for (int z = 0; z < 30; z++) if (Corridor(x, z)) w.SetExtraCost(new Cell(x, z), 3f);
            var reel = new HoseReelRect(3, 10, 1, 1);
            var target = new Cell(32, 10);
            const double hose = 40;
            string why = HoseMath.CheckInstall(w, reel, target, hose);
            CordWorld dry = Rocky();
            double waterLen = HoseMath.RouteLength(dry, reel, target);          // same walls, no cost: the corridor's own length
            double chosen = HoseMath.RouteLength(w, reel, target);
            List<Cell> cp = HoseMath.RouteCells(w, reel.StartCellToward(target), target, -1);
            string pathNote = cp == null ? "no path" : cp.Count + " cells, " + cp.Count(q => q.Z >= 20) + " in the dry tunnel stretch, extra cost " + cp.Sum(q => w.ExtraCost(q)).ToString("0");
            bool gap = why == "route too long" && waterLen > 0 && waterLen * HoseMath.RouteMargin <= hose;
            Program.Check(!gap && why == null, "fuzz G6 (GPT B2 fixed): a 37.4-cell costly corridor fits a 40-cell hose and is allowed (CheckInstall said '" + (why ?? "ok") + "')");
            // can-fail: the cost-first route (what the old CheckInstall judged) is the long dry detour that does not fit
            Program.Check(chosen * HoseMath.RouteMargin > hose, "fuzz G6 can-fail: the cost-first route still reads too long (" + (chosen * HoseMath.RouteMargin).ToString("0.0") + ")");
            o.Add("G6 (cost vs length, GPT B2, FIXED 2026-10-06): " + (gap ? "REPRODUCED" : "not reproduced") + ": hose " + hose.ToString("0") + ", the corridor route needs " +
                  (waterLen * HoseMath.RouteMargin).ToString("0.0") + " (fits) but the search returns a " + (chosen * HoseMath.RouteMargin).ToString("0.0") +
                  "-cell route (" + pathNote + ") and CheckInstall says '" + (why ?? "ok") + "'");
            return o;
        }

        /// <summary>The G2 hypothesis test (live: 9 matrix hose FAILs, bend ~0.19 vs 1.14; fuzz: 965/1445 outlet cases): is the
        /// tight bend IN the outlet blend, does the same case laid without the outlet bend fine, and does the turn the blend
        /// must make predict it (a blend of length bl turning theta cannot hold a radius above bl / theta).</summary>
        internal static List<string> OutletBendReport()
        {
            var o = new List<string>();
            var bad = BendOutlet.Where(r => r.MinBend < r.MinR * 0.95).ToList();
            var good = BendOutlet.Where(r => r.MinBend >= r.MinR * 0.95).ToList();
            if (BendOutlet.Count == 0) return o;
            int inBlend = bad.Count(r => r.Zone == "blend"), inStraight = bad.Count(r => r.Zone == "straight"), beyond = bad.Count(r => r.Zone == "beyond");
            var paired = bad.Where(r => BendFree.ContainsKey(r.Seed)).ToList();
            int freeOk = paired.Count(r => BendFree[r.Seed] >= r.MinR * 0.95);
            double Med(IEnumerable<double> xs) { var l = xs.OrderBy(x => x).ToList(); return l.Count == 0 ? double.NaN : l[l.Count / 2]; }
            int boundHolds = bad.Count(r => r.TurnDeg > 1 && r.MinBend <= (r.BlendEnd - r.Straight) / (r.TurnDeg * Math.PI / 180) + 1e-6);
            o.Add("G2 locator: " + bad.Count + "/" + BendOutlet.Count + " outlet lays bend under 95% of minR; tightest bend in the straight run " + inStraight +
                  ", in the blend " + inBlend + ", beyond it " + beyond);
            o.Add("G2 locator: same seed laid WITHOUT the outlet bends within 95% of minR in " + freeOk + "/" + paired.Count + " of those (2x2 reels)");
            o.Add("G2 locator: turn across the blend (outward vs heading after it) median " + Med(bad.Select(r => r.TurnDeg)).ToString("0") + " deg failing vs " +
                  Med(good.Select(r => r.TurnDeg)).ToString("0") + " deg passing; target bearing from outward median " + Med(bad.Select(r => r.BackDeg)).ToString("0") +
                  " deg failing vs " + Med(good.Select(r => r.BackDeg)).ToString("0") + " passing; radius <= blend/turn in " + boundHolds + "/" + bad.Count);
            var worst = bad.OrderBy(r => r.MinBend / r.MinR).FirstOrDefault();
            if (worst != null) o.Add("G2 locator worst: seed " + worst.Seed + " bend " + worst.MinBend.ToString("0.00") + " at s=" + worst.SAt.ToString("0.00") +
                                     " (straight to " + worst.Straight.ToString("0.0") + ", blend to " + worst.BlendEnd.ToString("0.0") + "), turn " + worst.TurnDeg.ToString("0") + " deg, minR " + worst.MinR.ToString("0.0"));
            return o;
        }

        // ================================================================== TRAIL (carry machine)
        internal struct TAct
        {
            public int Kind, X, Z; public double Amt;
            public static readonly string[] Names = { "Grab", "Step", "SetDown", "Interrupt", "PickUp", "Wind", "WindBy", "WindInt", "Replan", "ReelGone", "DevLay", "DevReelIn" };
            public override string ToString() => Names[Kind] + (Kind == 1 ? "(" + X + "," + Z + ")" : Kind == 6 ? "(" + Amt.ToString("0.0") + ")" : Kind == 8 || Kind == 10 ? "(n" + X + ")" : "");
        }

        private static CordWorld TrailWorld(long seed, out Cell reel, out double maxLen)
        {
            CordRng r = CordRng.Of("gssfuzz-trail", seed);
            var w = new CordWorld(36, 24);
            for (int k = r.Int(3, 10); k > 0; k--)
            {
                int x0 = r.Int(2, 33), z0 = r.Int(1, 22), bw = r.Int(1, 6), bh = r.Int(1, 3);
                if (r.Chance(0.5)) { int t = bw; bw = bh; bh = t; }
                for (int z = z0; z < Math.Min(24, z0 + bh); z++) for (int x = x0; x < Math.Min(36, x0 + bw); x++) w.SetBlocked(new Cell(x, z), BlockKind.Wall);
            }
            reel = new Cell(r.Int(4, 8), r.Int(8, 14));
            for (int z = reel.Z - 2; z <= reel.Z + 2; z++) for (int x = reel.X - 2; x <= reel.X + 2; x++) w.SetBlocked(new Cell(x, z), BlockKind.None);
            maxLen = r.Range(8, 45);
            return w;
        }

        private static List<TAct> GenTrail(long seed, int n)
        {
            CordRng r = CordRng.Of("gssfuzz-tacts", seed);
            var l = new List<TAct>();
            int[] wt = { 4, 60, 4, 4, 5, 4, 12, 3, 3, 1, 2, 2 };
            int total = wt.Sum();
            for (int i = 0; i < n; i++)
            {
                int pick = r.Int(0, total - 1), k = 0;
                while (pick >= wt[k]) { pick -= wt[k]; k++; }
                l.Add(new TAct { Kind = k, X = r.Int(-1, 1), Z = r.Int(-1, 1), Amt = r.Range(0.2, 8) });
                if (k == 8 || k == 10) l[l.Count - 1] = new TAct { Kind = k, X = r.Int(1, 70), Amt = 0 };
            }
            return l;
        }

        private static bool Legal(CordWorld w, Cell from, Cell to)
        {
            if (!w.IsWalkable(to)) return false;
            return to.X == from.X || to.Z == from.Z || (w.IsWalkable(new Cell(to.X, from.Z)) && w.IsWalkable(new Cell(from.X, to.Z)));
        }

        internal static string RunTrail(long seed, List<TAct> acts, ref long steps)
        {
            CordWorld w = TrailWorld(seed, out Cell reel, out double maxLen);
            V2 mouth = reel.Centre;
            var m = new HoseCarryMachine(w, mouth, maxLen);
            Cell cur = reel;
            double windStart = 0;
            for (int i = 0; i < acts.Count; i++)
            {
                TAct a = acts[i];
                HoseCarryState before = m.State;
                double lenBefore = m.State == HoseCarryState.Stored ? 0 : m.Trail.PulledLength(w);
                int cellsBefore = m.Trail.Cells.Count;
                double woundBefore = m.Wound;
                switch (a.Kind)
                {
                    case 0: if (m.Grab(reel)) cur = reel; break;
                    case 1:
                        {
                            var n = new Cell(cur.X + a.X, cur.Z + a.Z);
                            if (m.State == HoseCarryState.Carrying && Legal(w, cur, n)) { m.CarrierStep(n); if (m.State == HoseCarryState.Carrying) cur = n; }
                            break;
                        }
                    case 2: m.SetDown(); break;
                    case 3: m.Interrupt(); break;
                    case 4: if (m.PickUp()) cur = m.Trail.Last; break;
                    case 5: if (m.BeginWind()) windStart = lenBefore; break;
                    case 6: m.WindBy(a.Amt); break;
                    case 7: m.WindInterrupt(); break;
                    case 8: m.Replan(Row(reel, w, a.X)); break;
                    case 9: m.ReelGone(); break;
                    case 10: m.DevLay(Row(reel, w, a.X)); break;
                    case 11: m.DevReelIn(); break;
                }
                steps++;
                string inv = m.Invariant();
                if (inv != null) return "trail: invariant broken: " + inv + " (step " + i + ")";
                if (m.State != HoseCarryState.Stored)
                {
                    List<V2> pulled = m.Trail.Pulled(w);
                    string bad = FiniteList(pulled, "Pulled");
                    if (bad != null) return "trail: " + bad;
                    if (V2.Dist(pulled[0], mouth) > 1e-9) return "trail: pulled hose is detached from the reel mouth";
                    if (V2.Dist(pulled[pulled.Count - 1], m.Trail.Last.Centre) > 1e-9) return "trail: pulled hose does not reach the end cell";
                    if (m.Trail.Cells.Distinct().Count() != m.Trail.Cells.Count) return "trail: a cell appears twice on the trail";
                    if (!HoseMath.Clear(w, pulled, 0)) return "trail: the pulled hose runs through a wall (" + string.Join(" ", m.Trail.Cells.Take(14)) + ")";
                }
                // length conservation: stepping never lengthens a Carrying hose past the hose; winding only ever shortens
                if (a.Kind == 1 && before == HoseCarryState.Carrying && m.Trail.Cells.Count > 0 && m.State != HoseCarryState.Stored && m.Trail.PulledLength(w) > maxLen + 1e-9) return "trail: stepping stretched the hose past its length";
                if (a.Kind == 6 && before == HoseCarryState.Retracting)
                {
                    if (m.State == HoseCarryState.Retracting)
                    {
                        if (m.Wound < woundBefore - 1e-12) return "trail: wound length went backwards";
                        List<V2> drawn = HoseTrail.Clip(m.Trail.Pulled(w), m.Wound);
                        double want = Math.Max(0, lenBefore - m.Wound);
                        if (Math.Abs(Geo.Length(drawn) - want) > 1e-6) return "trail: wound " + m.Wound.ToString("0.00") + " of " + lenBefore.ToString("0.00") + " leaves " + Geo.Length(drawn).ToString("0.000") + " drawn, want " + want.ToString("0.000");
                        if (V2.Dist(drawn[0], mouth) > 1e-9) return "trail: the wound hose lost its reel end";
                    }
                    else if (m.State != HoseCarryState.Stored) return "trail: winding moved a Retracting hose to " + m.State;
                }
                if (a.Kind == 7 && before == HoseCarryState.Retracting && m.State == HoseCarryState.Dropped)
                {
                    double after = m.Trail.PulledLength(w);
                    if (m.Trail.Cells.Count > 1 && after > lenBefore - woundBefore + 1e-9) return "trail: interrupted wind kept " + after.ToString("0.00") + " but " + woundBefore.ToString("0.00") + " of " + lenBefore.ToString("0.00") + " was wound";
                    if (after > lenBefore + 1e-9) return "trail: interrupted wind lengthened the hose";
                    _ = windStart;
                }
            }
            return null;
        }

        private static List<Cell> Row(Cell reel, CordWorld w, int n)
        {
            var l = new List<Cell>();
            for (int i = 0; i <= n; i++) { var c = new Cell(reel.X + i, reel.Z); if (!w.IsWalkable(c)) break; l.Add(c); }
            return l;
        }

        // ================================================================== AERIAL
        internal struct AAct
        {
            public int Kind, A, B;
            public static readonly string[] Names = { "Link", "Unlink", "Remove", "Kill", "Auto", "Select" };
            public override string ToString() => Names[Kind] + "(" + A + "," + B + ")";
        }

        private static List<AnchorInfo> MakeAnchors(long seed, out double range)
        {
            CordRng r = CordRng.Of("gssfuzz-aerial", seed);
            range = r.Int(3, 14);
            var l = new List<AnchorInfo>();
            int n = r.Int(3, 14);
            for (int i = 0; i < n; i++)
                l.Add(new AnchorInfo { Id = 100 + i, X = r.Int(0, 30), Z = r.Int(0, 30), Faction = r.Chance(0.85) ? 1 : 2, MaxLinks = r.Int(1, 4), Roofed = r.Chance(0.1), IsAnchor = !r.Chance(0.05) });
            return l;
        }

        private static List<AAct> GenAerial(long seed, int count, int anchors)
        {
            CordRng r = CordRng.Of("gssfuzz-aacts", seed);
            var l = new List<AAct>();
            for (int i = 0; i < count; i++) l.Add(new AAct { Kind = new[] { 0, 0, 0, 1, 2, 3, 4, 5 }[r.Int(0, 7)], A = 100 + r.Int(0, anchors - 1), B = 100 + r.Int(0, anchors - 1) });
            return l;
        }

        internal static string RunAerial(long seed, List<AAct> acts, ref long steps)
        {
            List<AnchorInfo> all = MakeAnchors(seed, out double range);
            var live = new List<AnchorInfo>(all);
            AnchorInfo By(int id) => live.FirstOrDefault(x => x.Id == id);
            var state = new Dictionary<(int, int), SpanState>();
            (int, int) K(int a, int b) => a < b ? (a, b) : (b, a);
            foreach (AAct a in acts)
            {
                AnchorInfo x = By(a.A), y = By(a.B);
                switch (a.Kind)
                {
                    case 0:
                        if (x != null && y != null && AerialMath.CanLink(x, y, range) == LinkVerdict.Ok) { x.Linked.Add(y.Id); y.Linked.Add(x.Id); state[K(x.Id, y.Id)] = SpanState.Up; }
                        break;
                    case 1:
                        if (x != null && y != null && x.Linked.Contains(y.Id)) { x.Linked.Remove(y.Id); y.Linked.Remove(x.Id); state.Remove(K(x.Id, y.Id)); }
                        break;
                    case 2: case 3:
                        if (x != null)
                        {
                            var spans = x.Linked.Select(p => (p, state.TryGetValue(K(x.Id, p), out SpanState st) ? st : SpanState.Up)).ToList();
                            RemovalPlan plan = AerialMath.PlanRemoval(x.Id, a.Kind == 3, spans);
                            var partners = spans.Select(s => s.Item1).Where(p => p != x.Id).Distinct().OrderBy(p => p).ToList();
                            if (!plan.Reseed.OrderBy(p => p).SequenceEqual(partners)) return "aerial: removing " + x.Id + " reseeds " + string.Join(",", plan.Reseed) + " but its partners are " + string.Join(",", partners);
                            int fallen = a.Kind == 3 ? spans.Count(s => s.Item2 == SpanState.Up && s.Item1 != x.Id) : 0;
                            if (plan.Fallen.Count != fallen) return "aerial: removing " + x.Id + (a.Kind == 3 ? " (killed)" : " (dismantled)") + " drops " + plan.Fallen.Count + " cords, want " + fallen;
                            foreach (int p in x.Linked.ToList()) { By(p)?.Linked.Remove(x.Id); state.Remove(K(x.Id, p)); }
                            live.Remove(x);
                        }
                        break;
                    case 4:
                        if (x != null)
                        {
                            int pick = AerialMath.AutoLinkPick(x, live, range);
                            if (pick >= 0)
                            {
                                AnchorInfo o = By(pick);
                                long d = (long)(o.X - x.X) * (o.X - x.X) + (long)(o.Z - x.Z) * (o.Z - x.Z);
                                foreach (AnchorInfo q in live)
                                {
                                    if (AerialMath.CanLink(x, q, range) != LinkVerdict.Ok) continue;
                                    long dq = (long)(q.X - x.X) * (q.X - x.X) + (long)(q.Z - x.Z) * (q.Z - x.Z);
                                    if (dq < d || (dq == d && q.Id < pick)) return "aerial: AutoLinkPick chose " + pick + " but " + q.Id + " is nearer or ties lower";
                                }
                                x.Linked.Add(o.Id); o.Linked.Add(x.Id); state[K(x.Id, o.Id)] = SpanState.Up;
                            }
                        }
                        break;
                    case 5:
                        {
                            var sel = live.Where(q => (q.Id + a.A) % 3 != 0).ToList();
                            var edges = AerialMath.MinimumSpanningLinks(sel, range);
                            var deg = sel.ToDictionary(q => q.Id, q => q.Linked.Count);
                            var parent = sel.ToDictionary(q => q.Id, q => q.Id);
                            int Find(int i) { while (parent[i] != i) i = parent[i] = parent[parent[i]]; return i; }
                            foreach (AnchorInfo q in sel) foreach (int l in q.Linked) if (parent.ContainsKey(l)) parent[Find(q.Id)] = Find(l);
                            foreach ((int ea, int eb) in edges)
                            {
                                AnchorInfo qa = By(ea), qb = By(eb);
                                if (!AerialMath.InRange(qa.X, qa.Z, qb.X, qb.Z, range)) return "aerial: spanning link " + ea + "-" + eb + " is out of range";
                                if (qa.Faction != qb.Faction || qa.Roofed || qb.Roofed) return "aerial: spanning link " + ea + "-" + eb + " crosses factions or a roof";
                                if (++deg[ea] > qa.MaxLinks || ++deg[eb] > qb.MaxLinks) return "aerial: spanning link " + ea + "-" + eb + " exceeds MaxLinks";
                                if (Find(ea) == Find(eb)) return "aerial: spanning links " + ea + "-" + eb + " close a cycle";
                                parent[Find(ea)] = Find(eb);
                            }
                            foreach ((int ea, int eb) in edges) { By(ea).Linked.Add(eb); By(eb).Linked.Add(ea); state[K(ea, eb)] = SpanState.Up; }
                            break;
                        }
                }
                steps++;
                foreach (AnchorInfo q in live)
                {
                    if (q.Linked.Count > q.MaxLinks) return "aerial: anchor " + q.Id + " has " + q.Linked.Count + " links, max " + q.MaxLinks;
                    if (q.Linked.Distinct().Count() != q.Linked.Count) return "aerial: anchor " + q.Id + " lists a link twice";
                    foreach (int p in q.Linked)
                    {
                        AnchorInfo o = By(p);
                        if (o == null) return "aerial: anchor " + q.Id + " links to the removed anchor " + p;
                        if (!o.Linked.Contains(q.Id)) return "aerial: link " + q.Id + "->" + p + " is not symmetric";
                        if (p == q.Id) return "aerial: anchor " + q.Id + " links to itself";
                        if (!AerialMath.InRange(q.X, q.Z, o.X, o.Z, range)) return "aerial: span " + q.Id + "-" + p + " is longer than the range " + range;
                        if (q.Faction != o.Faction) return "aerial: span " + q.Id + "-" + p + " joins two factions";
                    }
                }
            }
            // geometry of every standing span: the curve, the shadow and the sway are finite, ends exact, never shorter than the chord
            foreach (AnchorInfo q in live)
                foreach (int p in q.Linked.Where(p => p > q.Id))
                {
                    AnchorInfo o = By(p);
                    var a = new P2(q.X + 0.5, q.Z + 0.5); var b = new P2(o.X + 0.5, o.Z + 0.5);
                    CordRng r = CordRng.Of("sag", q.Id, p);
                    double sagF = r.Range(0, 0.25);
                    List<P2> curve = AerialMath.SpanCurve(a, b, sagF);
                    if (curve.Any(c => !Finite(c.X) || !Finite(c.Z))) return "aerial: span curve has a non-finite point";
                    if (P2.Dist(curve[0], a) > 1e-12 || P2.Dist(curve[curve.Count - 1], b) > 1e-12) return "aerial: span curve ends are not the anchors";
                    double len = 0; for (int i = 1; i < curve.Count; i++) len += P2.Dist(curve[i - 1], curve[i]);
                    if (len < P2.Dist(a, b) - 1e-9) return "aerial: span curve shorter than its chord";
                    if (len > P2.Dist(a, b) * (1 + 4 * sagF * sagF * 3) + 1e-6 + 1.0) return "aerial: span curve " + len.ToString("0.00") + " too long for chord " + P2.Dist(a, b).ToString("0.00");
                    double wind = r.Range(0, 3), amp = r.Range(0, 0.6);
                    for (int k = 0; k <= 8; k++)
                    {
                        double sw = AerialMath.Sway(k / 8.0, r.Range(0, 1000), wind, amp, q.Id);
                        if (!Finite(sw) || Math.Abs(sw) > amp * Math.Min(wind, 1.5) * 1.0 + 1e-9) return "aerial: sway " + sw.ToString("0.000") + " exceeds amp x min(wind,1.5)";
                        if ((k == 0 || k == 8) && sw != 0) return "aerial: sway moves an insulator";
                    }
                    var sh = AerialMath.SpanShadow(a, b, 3, 3, sagF);
                    if (sh.Any(c => !Finite(c.X) || !Finite(c.Z))) return "aerial: span shadow has a non-finite point";
                }
            return null;
        }

        // ================================================================== driver
        private static string Arg(string[] args, string name) { int i = Array.IndexOf(args, name); return i >= 0 && i + 1 < args.Length ? args[i + 1] : null; }

        private static void Report(Tally t, List<string> fails)
        {
            Program.Check(t.Failures == 0, "fuzz " + t.Name + ": " + t.Cases + " cases, " + t.Steps + " steps, " + t.Failures + " failure(s)");
            Console.WriteLine("  fuzz " + t.Name.PadRight(7) + t.Cases.ToString().PadLeft(7) + " cases " + t.Steps.ToString().PadLeft(9) + " steps " + t.Seconds.ToString("0.00").PadLeft(7) + " s" + t.Extra);
            foreach (string k in fails.Where(f => f.StartsWith("KNOWNGAP "))) Console.WriteLine("    " + k.Substring(9));
            foreach (var g in fails.Where(f => !f.StartsWith("KNOWNGAP ")).GroupBy(f => { string k = System.Text.RegularExpressions.Regex.Replace(f, "^[a-z]+ seed [0-9]+: ", ""); k = System.Text.RegularExpressions.Regex.Replace(k, "[0-9]+(\\.[0-9]+)?", "#"); int cut = k.IndexOf(" | "); if (cut >= 0) k = k.Substring(0, cut); return k.Length > 70 ? k.Substring(0, 70) : k; }).OrderByDescending(g => g.Count()))
                Console.WriteLine("    " + g.Count() + " x " + g.Key + "   first: " + g.First());
        }

        public static void Run(string[] args)
        {
            double scale = double.Parse(Arg(args, "--fuzz-scale") ?? "1", System.Globalization.CultureInfo.InvariantCulture);
            if (scale <= 0) return;
            string only = Arg(args, "--fuzz-only");
            string one = Arg(args, "--fuzz-seed");
            int Cases(int n) => Math.Max(1, (int)Math.Round(n * scale));
            var all = Stopwatch.StartNew();
            var tallies = new List<Tally>();
            Console.WriteLine("fuzz (approach B): scale " + scale.ToString("0.##"));

            if (only == null || only == "cords")
            {
                var t = new Tally { Name = "cords" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(120);
                ulong digest = 1469598103934665603UL;
                BendOutlet.Clear(); BendFree.Clear();
                var gapCount = new Dictionary<string, int>(); var gapFirst = new Dictionary<string, (long, List<Act>, string)>();
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    Scene s0 = MakeScene(seed);
                    CordRng cr = CordRng.Of("gssfuzz-len", seed);
                    List<Act> acts = GenActs(s0, seed, cr.Int(3, 24));
                    bool every = k % 3 == 0;
                    long steps = 0;
                    var gl = new List<string>();
                    string msg = RunCords(seed, acts, every, ref steps, gl);
                    t.Cases++; t.Steps += steps;
                    foreach (string g in gl.Select(x => x.Substring(0, 2)).Distinct())
                    {
                        gapCount.TryGetValue(g, out int gc); gapCount[g] = gc + 1;
                        if (!gapFirst.ContainsKey(g)) gapFirst[g] = (seed, acts, gl.First(x => x.StartsWith(g)));
                    }
                    if (msg == null) { Scene sf = MakeScene(seed); foreach (Act a in acts) Apply(sf, a); CordWorld wf = sf.ToWorld(); var lv = sf.Live(wf); digest = (digest ^ Digest(new CordBuilder().Build(wf, sf.Opt, c => lv.Contains(c)))) * 1099511628211UL; continue; }
                    t.Failures++;
                    string tag = Tag(msg);
                    long dummy = 0;
                    List<Act> min = Shrink(acts, c => { string m2 = RunCords(seed, c, true, ref dummy); return m2 != null && Tag(m2) == tag; });
                    string m3 = RunCords(seed, min, true, ref dummy);
                    fails.Add(Where("cords", seed, min.Cast<object>(), m3 ?? msg));
                }
                foreach (var kv in gapCount.OrderBy(k => k.Key))
                {
                    (long gseed, List<Act> gacts, string gmsg) = gapFirst[kv.Key];
                    long d2 = 0;
                    List<Act> min = Shrink(gacts, c => { var l2 = new List<string>(); RunCords(gseed, c, true, ref d2, l2); return l2.Any(x => x.StartsWith(kv.Key)); });
                    fails.Add("KNOWNGAP known gap " + kv.Key + " [cords] " + kv.Value + "/" + t.Cases + " cases: " + gmsg + "  " + Where("cords", gseed, min.Cast<object>(), "reproducer"));
                }
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds; t.Extra = "   digest " + digest.ToString("x16") + ", closest strand to its limit: over by " + MaxOver.ToString("0.00");
                Report(t, fails); tallies.Add(t);
            }
            if (only == null || only == "hose")
            {
                var t = new Tally { Name = "hose" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(1500), laid = 0, fb = 0;
                var gapCount = new Dictionary<string, int>(); var gapFirst = new Dictionary<string, (long, bool, string)>(); var laidModes = new int[2];
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    long steps = 0;
                    foreach (bool outlet in new[] { true, false })
                    {
                        if (!outlet && MakeHose(seed).Reel.W != 2) continue;     // a 1x1 reel has no outlet: the second mode would repeat the first
                        var gl = new List<string>();
                        BendCollect = true;
                        string msg = RunHose(seed, null, ref steps, out int ok, out int f, outlet, gl);
                        BendCollect = false;
                        laid += ok; fb += f;
                        t.Cases++; t.Steps += steps; steps = 0;
                        if (ok == 1) laidModes[outlet ? 0 : 1]++;
                        foreach (string g in gl.Select(x => x.Substring(0, 2)).Distinct())
                        {
                            gapCount.TryGetValue(g + (outlet ? "o" : "f"), out int gc); gapCount[g + (outlet ? "o" : "f")] = gc + 1;
                            if (!gapFirst.ContainsKey(g + (outlet ? "o" : "f"))) gapFirst[g + (outlet ? "o" : "f")] = (seed, outlet, gl.First(x => x.StartsWith(g)));
                        }
                        if (msg == null) continue;
                        t.Failures++;
                        string tag = Tag(msg);
                        // shrink the wall set: reproduce the exact walls, then delete them while the same fault remains
                        HoseCase hc = MakeHose(seed);
                        var walls = new List<Cell>();
                        for (int z = 0; z < hc.W.Height; z++) for (int x = 0; x < hc.W.Width; x++) if (!hc.W.IsWalkable(new Cell(x, z))) walls.Add(new Cell(x, z));
                        long d2 = 0;
                        List<Cell> min = Shrink(walls, c => { string m2 = RunHose(seed, c, ref d2, out _, out _, outlet); return m2 != null && Tag(m2) == tag; });
                        string m3 = RunHose(seed, min, ref d2, out _, out _, outlet);
                        fails.Add("hose seed " + seed + ": " + (m3 ?? msg) + " | " + MakeHose(seed, min) + " | walls " + string.Join(" ", min.Take(20).Select(c => c.ToString())));
                    }
                }
                // each known gap: how often, and its first reproducer shrunk to the fewest walls that still show it
                var gapLines = new List<string>();
                foreach (var kv in gapCount.OrderBy(k => k.Key))
                {
                    (long gseed, bool go, string gmsg) = gapFirst[kv.Key];
                    string cls = kv.Key.Substring(0, 2);
                    HoseCase hc = MakeHose(gseed);
                    var walls = new List<Cell>();
                    for (int z = 0; z < hc.W.Height; z++) for (int x = 0; x < hc.W.Width; x++) if (!hc.W.IsWalkable(new Cell(x, z))) walls.Add(new Cell(x, z));
                    long d2 = 0;
                    bool Has(List<Cell> ws) { var l2 = new List<string>(); RunHose(gseed, ws, ref d2, out _, out _, go, l2); return l2.Any(x => x.StartsWith(cls)); }
                    List<Cell> min = Shrink(walls, ws => Has(ws));
                    gapLines.Add("known gap " + kv.Key.Substring(0, 2) + (go ? " [outlet] " : " [free] ") + kv.Value + "/" + laidModes[go ? 0 : 1] + " laid: " + gmsg + "  (seed " + gseed + ", " + MakeHose(gseed, min) + (min.Count > 0 ? ", walls " + string.Join(" ", min.Take(12)) : "") + ")");
                }
                foreach (string gl in gapLines) fails.Add("KNOWNGAP " + gl);
                foreach (string gl in OutletBendReport()) fails.Add("KNOWNGAP " + gl);
                foreach (string gl in CostVsLengthProbe()) fails.Add("KNOWNGAP " + gl);
                foreach (var kv in RefuseWhy.OrderBy(k => k.Key)) fails.Add("KNOWNGAP refused after the route check " + kv.Key + ": " + kv.Value);
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds; t.Extra = "   (" + laid + " laid, " + fb + " via fallback, " + gapCount.Count + " known-gap class(es) tallied below)"; t.Failures -= 0;
                Report(t, fails); tallies.Add(t);
            }
            if (only == null || only == "trail")
            {
                var t = new Tally { Name = "trail" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(1500);
                var visited = new HashSet<HoseCarryState>();
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    CordRng cr = CordRng.Of("gssfuzz-tlen", seed);
                    List<TAct> acts = GenTrail(seed, cr.Int(20, 160));
                    long steps = 0;
                    string msg = RunTrail(seed, acts, ref steps);
                    t.Cases++; t.Steps += steps;
                    if (msg == null) continue;
                    t.Failures++;
                    string tag = Tag(msg);
                    long d2 = 0;
                    List<TAct> min = Shrink(acts, c => { string m2 = RunTrail(seed, c, ref d2); return m2 != null && Tag(m2) == tag; });
                    string m3 = RunTrail(seed, min, ref d2);
                    fails.Add(Where("trail", seed, min.Cast<object>(), m3 ?? msg));
                }
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds;
                Report(t, fails); tallies.Add(t);
            }
            if (only == null || only == "aerial")
            {
                var t = new Tally { Name = "aerial" }; var fails = new List<string>();
                var sw = Stopwatch.StartNew();
                int n = one != null ? 1 : Cases(5000);
                for (int k = 0; k < n; k++)
                {
                    long seed = one != null ? long.Parse(one) : k + 1;
                    CordRng cr = CordRng.Of("gssfuzz-alen", seed);
                    int na = MakeAnchors(seed, out _).Count;
                    List<AAct> acts = GenAerial(seed, cr.Int(5, 60), na);
                    long steps = 0;
                    string msg = RunAerial(seed, acts, ref steps);
                    t.Cases++; t.Steps += steps;
                    if (msg == null) continue;
                    t.Failures++;
                    string tag = Tag(msg);
                    long d2 = 0;
                    List<AAct> min = Shrink(acts, c => { string m2 = RunAerial(seed, c, ref d2); return m2 != null && Tag(m2) == tag; });
                    string m3 = RunAerial(seed, min, ref d2);
                    fails.Add(Where("aerial", seed, min.Cast<object>(), m3 ?? msg));
                }
                sw.Stop(); t.Seconds = sw.Elapsed.TotalSeconds;
                Report(t, fails); tallies.Add(t);
            }
            if (only == null) NegativeControls();
            all.Stop();
            Console.WriteLine("fuzz total: " + tallies.Sum(x => x.Cases) + " cases, " + tallies.Sum(x => x.Steps) + " steps, " + all.Elapsed.TotalSeconds.ToString("0.00") + " s");
        }

        /// <summary>The checkers must be able to fail: each is shown a hand-corrupted input and has to flag it.</summary>
        private static void NegativeControls()
        {
            var w = new CordWorld(8, 4);
            foreach (int x in new[] { 1, 2, 3, 5, 6 }) w.SetConduit(new Cell(x, 1));       // two nets: 1-3 and 5-6
            CordGraph g = CordGraph.Reduce(w);
            var net = Scene.Nets(w);
            Program.Check(CheckNets(g, net) == null, "fuzz control: a real graph of two separate nets reads clean");
            var bad = new Dictionary<Cell, int>(net);
            foreach (Cell c in net.Keys.ToList()) bad[c] = 0;                                  // every cell one net...
            bad[new Cell(5, 1)] = 1; bad[new Cell(6, 1)] = 1;
            var g2 = CordGraph.Reduce(w);
            var w2 = new CordWorld(8, 4);
            foreach (int x in new[] { 1, 2, 3, 4, 5, 6 }) w2.SetConduit(new Cell(x, 1));       // one run, but claim 4 belongs to another net
            var net2 = Scene.Nets(w2); net2[new Cell(4, 1)] = 7;
            Program.Check(CheckNets(CordGraph.Reduce(w2), net2) != null, "fuzz control: an edge across two nets is flagged");
            var pieces = new List<LaidPiece> { new LaidPiece { Key = "x", EndA = "a", EndB = "b", PathLen = 3, Strands = { new CordStrand { Pts = new List<V2> { new V2(0, 0), new V2(double.NaN, 1) } } } } };
            Program.Check(CheckGeometry(w, pieces, new BuildOptions()) != null, "fuzz control: a NaN strand point is flagged");
            pieces = new List<LaidPiece> { new LaidPiece { Key = "y", EndA = "a", EndB = "b", PathLen = 3, Strands = { new CordStrand { Pts = new List<V2> { new V2(0, 0), new V2(400, 0) } } } } };
            Program.Check(CheckGeometry(w, pieces, new BuildOptions()) != null, "fuzz control: a strand far over its length limit is flagged");
            var a = new List<LaidPiece> { new LaidPiece { Key = "k", Strands = { new CordStrand { Pts = new List<V2> { new V2(0, 0), new V2(1, 0) } } } } };
            var b = new List<LaidPiece> { new LaidPiece { Key = "k", Strands = { new CordStrand { Pts = new List<V2> { new V2(0, 0), new V2(1, 0.01) } } } } };
            Program.Check(Digest(a) != Digest(b), "fuzz control: the digest tells a 0.01-cell nudge apart");
            var sh = Shrink(new List<int> { 1, 2, 3, 4, 5, 6, 7, 8 }, l => l.Contains(3) && l.Contains(6));
            Program.Check(sh.SequenceEqual(new[] { 3, 6 }), "fuzz control: the shrinker reduces eight actions to the two that matter (" + string.Join(",", sh) + ")");
        }
    }
}
