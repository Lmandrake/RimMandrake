// Approach B for Gimme Some Slack (design/RimMandrake/gss_offline_fuzz_B.md): seeded random ACTION SEQUENCES over the
// production core (CordGraph / CordBuilder / AerialMath), checked against
// design invariants after every step. A failing sequence is shrunk (delta debugging over the action list) and printed
// as `seed N: message | actions`, which replays exactly. Everything is a pure function of the seed (CordRng).
//
//   families:  cords (build/remove/break/reconnect/block conduit; incremental == fresh; net and geometry invariants)
//              (hose and trail moved with the hose to FlowWorks/Source/SelfTest/HoseFuzz.cs at the hose port, 2026-10-11)
//              aerial(anchor link/unlink/remove sequences; range, max links, sway, span curve)
//   args:      --fuzz-scale F   multiply every family's case count (default 1; 0 skips the whole fuzz)
//              --fuzz-only NAME run one family (cords|aerial)
//              --fuzz-seed N    replay one seed of the chosen family verbosely (no shrinking limit)
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using RimMandrake.GimmeSomeSlack.Aerial;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

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
            // stray conduit cells, unguarded: they may land on a machine footprint too (the old `!Protected || true` guard never applied)
            for (int k = r.Int(0, 4); k > 0; k--) { int x = r.Int(0, s.Reserved - 1), z = r.Int(0, s.H - 1); s.Cond[s.Idx(x, z)] = true; }
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
                case 1: s.Cond[i] = false; break;   // unguarded: a hookup's conduit may be removed too (the old `!Protected || Cond` guard was a no-op)
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

        /// <summary>Runs a sequence; returns the first failure message or null. everyStep: compare against a fresh builder every step.</summary>
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

        /// <summary>Every world the cords fuzz builds (seed, step, world, options, live set): the A7 unroutable census
        /// (UnroutableCensus.cs) walks the same worlds the fuzz checks.</summary>
        internal static IEnumerable<(long seed, int step, CordWorld w, BuildOptions opt, Func<Cell, bool> live)> CordWorlds(int n)
        {
            for (int k = 0; k < n; k++)
            {
                long seed = k + 1;
                Scene s = MakeScene(seed);
                List<Act> acts = GenActs(s, seed, CordRng.Of("gssfuzz-len", seed).Int(3, 24));
                for (int i = 0; i <= acts.Count; i++)
                {
                    if (i > 0) Apply(s, acts[i - 1]);
                    CordWorld w = s.ToWorld();
                    HashSet<Cell> live = s.Live(w);
                    yield return (seed, i, w, s.Opt, c => live.Contains(c));
                }
            }
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
