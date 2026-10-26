// GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS (live round 7, 2026-10-26): with each frame's Build at 2-5 ms, one rebuild slice still
// read 140 ms. The component's Rebuild timed only the snapshot and the Build; after publishing it re-derived, over EVERY piece
// on the map, the net seeds (string tokens + union-find) and, for EVERY section, a string signature joining each piece's
// cache key with a full walk of its strand geometry. That tail was untimed, grew with the map's cords instead of with what
// changed, and allocated megabytes per frame of a planned build -- the garbage that drives Mono's stop-the-world collector.
// The reproduction: the live recipe (k finished lattices on the 325 map, one more spawned over frames, an AsyncLay Build per
// frame), then per frame the former tail (a verbatim copy below) against RebuildTail: identical seeds, identical dirty
// sections (with and without eligibility bits), and the new tail's cost and garbage far under the old.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class RebuildTailChecks
    {
        private const int SectionSize = 17;   // Verse.Section.Size

        // ---- the former tail, verbatim from RM_MapComponent_CordGraph before this fix ----
        private static Dictionary<LaidPiece, int> OldNetSeeds(List<LaidPiece> ps)
        {
            var parent = new Dictionary<string, string>();
            string Find(string x)
            {
                if (!parent.TryGetValue(x, out string px)) { parent[x] = x; return x; }
                while (px != x) { string g = parent[px]; parent[x] = g; x = px; px = g; }
                return x;
            }
            void Union(string a, string b)
            {
                string ra = Find(a), rb = Find(b);
                if (ra == rb) return;
                if (string.CompareOrdinal(ra, rb) < 0) parent[rb] = ra; else parent[ra] = rb;
            }
            string Tok(string end) { int i = end.LastIndexOf(':'); return i >= 0 ? end.Substring(i + 1) : end; }
            var first = new Dictionary<LaidPiece, string>();
            foreach (LaidPiece p in ps)
            {
                string own = p.Owner.X + "," + p.Owner.Z;
                string a = p.EndA != null ? Tok(p.EndA) : own;
                Find(a);
                if (p.EndB != null) Union(a, Tok(p.EndB));
                first[p] = a;
            }
            var res = new Dictionary<LaidPiece, int>();
            foreach (KeyValuePair<LaidPiece, string> kv in first)
            {
                string root = Find(kv.Value);
                uint h = 2166136261u;
                foreach (char c in root) h = unchecked((h ^ c) * 16777619u);
                res[kv.Key] = unchecked((int)h);
            }
            return res;
        }

        private static string OldSig(Dictionary<(int, int), List<LaidPiece>> d, (int, int) s, Dictionary<LaidPiece, int> seeds, Dictionary<LaidPiece, int> mats) =>
            d.TryGetValue(s, out List<LaidPiece> l)
                ? string.Join("\n", l.Select(p => p.Key + "@" + p.GeometryHash() + "#" + (seeds.TryGetValue(p, out int v) ? v : 0) +
                                                  "%" + (mats.TryGetValue(p, out int g) ? g : -1)))
                : "";

        private static string OldElig(Dictionary<(int, int), List<LaidPiece>> d, (int, int) s, Func<CordStrand, int> elig)
        {
            if (!d.TryGetValue(s, out List<LaidPiece> l)) return "";
            if (elig == null) return "";
            var sb = new System.Text.StringBuilder(" e");
            foreach (LaidPiece p in l)
                foreach (CordStrand st in p.Strands)
                {
                    if (st.Pts == null || st.Pts.Count < 2) { sb.Append('-'); continue; }
                    sb.Append((char)('a' + elig(st)));
                }
            return sb.ToString();
        }
        // ---- end of the former tail ----

        private static Dictionary<(int, int), List<LaidPiece>> BySection(List<LaidPiece> ps)
        {
            var d = new Dictionary<(int, int), List<LaidPiece>>();
            foreach (LaidPiece p in ps)
            {
                var s = (p.Owner.X / SectionSize, p.Owner.Z / SectionSize);
                if (!d.TryGetValue(s, out List<LaidPiece> l)) d[s] = l = new List<LaidPiece>();
                l.Add(p);
            }
            return d;
        }

        /// <summary>A material index per piece standing in for ComputeMaterials: keyed by the piece's key, some pieces absent
        /// (the -1 default), and it changes with the frame for a few so a material change must dirty its section.</summary>
        private static Dictionary<LaidPiece, int> Mats(List<LaidPiece> ps, int frame)
        {
            var m = new Dictionary<LaidPiece, int>();
            foreach (LaidPiece p in ps)
            {
                int h = (p.Key ?? "").Length + p.Owner.X * 3 + p.Owner.Z;
                if (h % 7 == 0) continue;
                m[p] = h % 11 == 0 ? (h + frame / 5) % 4 : h % 4;
            }
            return m;
        }

        internal static void Run()
        {
            Equivalence(Fixture(4), withElig: false);
            Equivalence(Fixture(4), withElig: true);
            Scale();
        }

        /// <summary>The frames of one spawn: lattice k laid over AsyncLay Builds on k finished lattices, each frame's published
        /// pieces.</summary>
        private static List<List<LaidPiece>> Fixture(int k)
        {
            Func<Cell, bool> live = c => false;
            var b = new CordBuilder();
            var (cells, lamps) = CordScaleBench.Lattice(k);
            var frames = new List<List<LaidPiece>> { b.Build(CordScaleBench.World(k, 0, 0), new BuildOptions(), live) };
            int nc = 0, nl = 0;
            var wall = Stopwatch.StartNew();
            while (true)
            {
                if (nc < cells.Count) nc = Math.Min(cells.Count, nc + 60);
                else if (nl < lamps.Count) nl = Math.Min(lamps.Count, nl + 12);
                frames.Add(b.Build(CordScaleBench.World(k, nc, nl), new BuildOptions { AsyncLay = true }, live));
                if (nc == cells.Count && nl == lamps.Count && b.LastPending == 0 && !b.LayRunning) break;
                if (wall.Elapsed.TotalSeconds > 120) break;
                System.Threading.Thread.Sleep(4);
            }
            return frames;
        }

        /// <summary>Seeds identical to the former union-find; per frame the sections the new 64-bit signatures dirty are exactly
        /// the sections the former strings dirtied (the component's compare: last printed signature, else the previous
        /// frame's set).</summary>
        private static void Equivalence(List<List<LaidPiece>> frames, bool withElig)
        {
            // a deterministic eligibility read that varies by strand and (for a few) by frame, standing in for sway/roof/ripple
            int frame = 0;
            Func<CordStrand, int> elig = withElig
                ? st => ((st.Lifted ? 1 : 0) | (st.OverFace ? 2 : 0) | ((int)(st.S0 * 1000) % 3 == 0 ? 4 : 0) |
                         ((int)(st.S0 * 1000) % 13 == frame % 13 ? 8 : 0))
                : null;
            string tag = withElig ? "elig on" : "elig off";
            var printedOld = new Dictionary<(int, int), string>();
            var printedNew = new Dictionary<(int, int), ulong>();
            var prevBy = new Dictionary<(int, int), List<LaidPiece>>();
            var prevSeedsO = new Dictionary<LaidPiece, int>();
            var prevSeedsN = new Dictionary<LaidPiece, int>();
            var prevMat = new Dictionary<LaidPiece, int>();
            int seedBad = 0, dirtyBad = 0, dirtied = 0, sections = 0, seedMerges = 0;
            string firstBad = null;
            foreach (List<LaidPiece> next in frames)
            {
                frame++;
                var nextBy = BySection(next);
                Dictionary<LaidPiece, int> so = OldNetSeeds(next), sn = RebuildTail.NetSeeds(next);
                if (so.Count != sn.Count || so.Any(kv => !sn.TryGetValue(kv.Key, out int v) || v != kv.Value)) seedBad++;
                if (so.Values.Distinct().Count() != prevSeedsO.Values.Distinct().Count()) seedMerges++;
                Dictionary<LaidPiece, int> mat = Mats(next, frame);
                var keys = new HashSet<(int, int)>(nextBy.Keys);
                keys.UnionWith(prevBy.Keys);
                keys.UnionWith(printedOld.Keys);
                keys.UnionWith(printedNew.Keys);
                foreach (var s in keys)
                {
                    sections++;
                    string cur = OldSig(nextBy, s, so, mat) + OldElig(nextBy, s, elig);
                    if (!printedOld.TryGetValue(s, out string was)) was = OldSig(prevBy, s, prevSeedsO, prevMat) + OldElig(prevBy, s, elig);
                    bool dOld = was != cur;
                    if (cur.Length == 0) printedOld.Remove(s); else printedOld[s] = cur;

                    ulong curN = RebuildTail.SectionSig(nextBy.TryGetValue(s, out List<LaidPiece> nl) ? nl : null, sn, mat, elig);
                    if (!printedNew.TryGetValue(s, out ulong wasN))
                        wasN = RebuildTail.SectionSig(prevBy.TryGetValue(s, out List<LaidPiece> pl) ? pl : null, prevSeedsN, prevMat, elig);
                    bool dNew = wasN != curN;
                    if (curN == 0UL) printedNew.Remove(s); else printedNew[s] = curN;

                    if (dOld) dirtied++;
                    if (dOld != dNew) { dirtyBad++; firstBad ??= $"frame {frame} section {s}: old dirty {dOld}, new dirty {dNew}"; }
                }
                prevBy = nextBy;
                prevSeedsO = so;
                prevSeedsN = sn;
                prevMat = mat;
            }
            Program.Check(seedBad == 0, $"tail ({tag}): RebuildTail.NetSeeds differs from the former union-find on {seedBad}/{frames.Count} frames");
            Program.Check(dirtyBad == 0, $"tail ({tag}): the 64-bit section signature dirtied differently from the former string on {dirtyBad} of {sections} section-frames ({firstBad})");
            // instrument sanity: the run must dirty sections and change nets, or the equality above proves nothing
            Program.Check(frames.Count > 5 && dirtied > frames.Count && seedMerges > 0,
                $"tail ({tag}): instrument blind -- {frames.Count} frames, {dirtied} dirty section-frames, {seedMerges} frames that changed the net count");
            Console.WriteLine($"rebuild tail ({tag}): {frames.Count} frames, {sections} section-frames, {dirtied} dirtied, seeds and dirty decisions identical: {seedBad + dirtyBad == 0}");
        }

        /// <summary>The live scale (k=8: eight finished lattices, the ninth spawning): per frame the former tail and the new one
        /// on the same published pieces, wall time and garbage.</summary>
        private static void Scale()
        {
            const int k = 8;
            List<List<LaidPiece>> frames = Fixture(k);
            var empty = new Dictionary<LaidPiece, int>();
            double oldWorst = 0, newWorst = 0, newWorstNoGc = 0, oldSum = 0, newSum = 0, newFirst = 0;
            long oldBytes = 0, newBytes = 0;
            int pieces = frames[frames.Count - 1].Count, n = 0;
            var sw = new Stopwatch();
            var printedOld = new Dictionary<(int, int), string>();
            var printedNew = new Dictionary<(int, int), ulong>();
            var prevBy = new Dictionary<(int, int), List<LaidPiece>>();
            Dictionary<LaidPiece, int> prevO = empty, prevN = empty, prevMat = empty;
            var keys = new HashSet<(int, int)>();
            foreach (List<LaidPiece> next in frames)
            {
                n++;
                var nextBy = BySection(next);
                Dictionary<LaidPiece, int> mat = Mats(next, n);
                // the former tail
                long a0 = GC.GetAllocatedBytesForCurrentThread();
                sw.Restart();
                Dictionary<LaidPiece, int> so = OldNetSeeds(next);
                var ok = new HashSet<(int, int)>(nextBy.Keys);
                ok.UnionWith(prevBy.Keys);
                ok.UnionWith(printedOld.Keys);
                foreach (var s in ok)
                {
                    string cur = OldSig(nextBy, s, so, mat) + OldElig(nextBy, s, null);
                    if (!printedOld.TryGetValue(s, out string was)) was = OldSig(prevBy, s, prevO, prevMat);
                    if (cur.Length == 0) printedOld.Remove(s); else printedOld[s] = cur;
                }
                double tOld = sw.Elapsed.TotalMilliseconds;
                long a1 = GC.GetAllocatedBytesForCurrentThread();
                // the new tail (the component's: seeds, then signatures into a reused key set)
                int gc0 = GC.CollectionCount(0);
                sw.Restart();
                Dictionary<LaidPiece, int> sn = RebuildTail.NetSeeds(next);
                keys.Clear();
                keys.UnionWith(nextBy.Keys);
                keys.UnionWith(prevBy.Keys);
                keys.UnionWith(printedNew.Keys);
                foreach (var s in keys)
                {
                    ulong cur = RebuildTail.SectionSig(nextBy.TryGetValue(s, out List<LaidPiece> nl) ? nl : null, sn, mat, null);
                    if (!printedNew.TryGetValue(s, out ulong was))
                        was = RebuildTail.SectionSig(prevBy.TryGetValue(s, out List<LaidPiece> pl) ? pl : null, prevN, prevMat, null);
                    if (cur == 0UL) printedNew.Remove(s); else printedNew[s] = cur;
                }
                double tNew = sw.Elapsed.TotalMilliseconds;
                long a2 = GC.GetAllocatedBytesForCurrentThread();
                bool gc = GC.CollectionCount(0) != gc0;
                if (n == 1) newFirst = tNew;   // a loaded map: every piece's memo fills once
                else
                {
                    oldWorst = Math.Max(oldWorst, tOld); newWorst = Math.Max(newWorst, tNew);
                    if (!gc) newWorstNoGc = Math.Max(newWorstNoGc, tNew);
                    oldSum += tOld; newSum += tNew;
                    oldBytes += a1 - a0; newBytes += a2 - a1;
                }
                prevBy = nextBy; prevO = so; prevN = sn; prevMat = mat;
            }
            int m = Math.Max(1, frames.Count - 1);
            Console.WriteLine($"rebuild tail k={k}: {pieces} pieces, {frames.Count} frames; former tail worst {oldWorst:0.00} ms mean {oldSum / m:0.00} ms " +
                              $"{oldBytes / m / 1024} KB/frame; new tail worst {newWorst:0.00} ms (no GC {newWorstNoGc:0.00}) mean {newSum / m:0.00} ms " +
                              $"{newBytes / m / 1024} KB/frame; first frame (memos fill) {newFirst:0.00} ms");
            Program.Check(pieces > 1000, $"tail scale: only {pieces} pieces at k={k} (instrument blind: the live map had ~2000)");
            // bound: a quarter of the 20 ms slice bar the live re-run reads, with room for a loaded machine (offline ~1-3 ms, the
            // former tail 22-24 ms worst on the same frames)
            Program.Check(newWorstNoGc < 5.0 && newWorstNoGc * 3 < oldWorst,
                $"tail scale: the new rebuild tail took {newWorstNoGc:0.00} ms on a frame without a collection (bound 5 ms and a third of the former {oldWorst:0.00} ms)");
            Program.Check(newBytes * 4 < oldBytes, $"tail scale: the new tail allocated {newBytes / m} B/frame against the former {oldBytes / m} B/frame (must be under a quarter)");
        }
    }
}
