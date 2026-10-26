// Gimme Some Slack core: Verse-free (see CordMath.cs header).
// GSS_SLICE_FIX_LONE_REBUILD_HITS_140MS (live round 7, 2026-10-26): a frame's Rebuild timed only its snapshot and Build
// (lastRebuildMs 2-5 ms), but after publishing it re-derived, over EVERY piece on the map, the net seeds (a string-keyed
// union-find), and for EVERY section a signature string joining each piece's long cache key and a full walk of its strand
// points. That tail was untimed, grew with the map's total cords rather than with what changed, and allocated megabytes
// of strings per frame of a planned build, so the slices fed Mono's stop-the-world collector (the lone 140 ms slice). The
// tail lives here so the SelfTest drives it at the live scale (RebuildTailChecks).
using System;
using System.Collections.Generic;
using RimMandrake.Shared.Slack;

namespace RimMandrake.GimmeSomeSlack.Core
{
    internal static class RebuildTail
    {
        /// <summary>The token a piece end joins its net by ("type:x,z" -> "x,z"); the owner cell for an end-less piece.</summary>
        private static string Tok(string end) { int i = end.LastIndexOf(':'); return i >= 0 ? end.Substring(i + 1) : end; }

        private static void Tokens(LaidPiece p)
        {
            if (p.NetTokA != null) return;
            string own = p.Owner.X + "," + p.Owner.Z;
            p.NetTokB = p.EndB != null ? Tok(p.EndB) : null;
            p.NetTokA = p.EndA != null ? Tok(p.EndA) : own;   // set last: NetTokA != null marks the memo filled
        }

        /// <summary>Union the pieces by the cells they touch (edge ends, node/coil/tangle owner cells); a component's seed is
        /// a stable FNV hash of its smallest cell token -- pure geometry, no vanilla PowerNet (which is not built yet while a
        /// loaded map's sections first regenerate). Bit-identical to the component's former ComputeNetSeeds (SelfTest), with
        /// each piece's tokens kept on the piece (a reused piece is not re-tokenised) and each root hashed once.</summary>
        internal static Dictionary<LaidPiece, int> NetSeeds(List<LaidPiece> ps)
        {
            var parent = new Dictionary<string, string>(ps.Count * 2);
            string Find(string x)
            {
                if (!parent.TryGetValue(x, out string px)) { parent[x] = x; return x; }
                while (px != x) { string g = parent[px]; parent[x] = g; x = px; px = g; }   // path halving, no recursion
                return x;
            }
            void Union(string a, string b)
            {
                string ra = Find(a), rb = Find(b);
                if (ra == rb) return;
                if (string.CompareOrdinal(ra, rb) < 0) parent[rb] = ra; else parent[ra] = rb;
            }
            foreach (LaidPiece p in ps)
            {
                Tokens(p);
                Find(p.NetTokA);
                if (p.NetTokB != null) Union(p.NetTokA, p.NetTokB);
            }
            var hashOf = new Dictionary<string, int>();
            var res = new Dictionary<LaidPiece, int>(ps.Count);
            foreach (LaidPiece p in ps)
            {
                string root = Find(p.NetTokA);         // roots are the ordinal-smallest token (Union keeps the smaller)
                if (!hashOf.TryGetValue(root, out int hv))
                {
                    uint h = 2166136261u;
                    foreach (char c in root) h = unchecked((h ^ c) * 16777619u);
                    hashOf[root] = hv = unchecked((int)h);
                }
                res[p] = hv;
            }
            return res;
        }

        private const ulong Prime = 1099511628211UL, Basis = 1469598103934665603UL;
        private static ulong Mix(ulong h, ulong v) => unchecked((h ^ v) * Prime);

        /// <summary>A piece's own part of a section signature: its cache key and its geometry (GeometryHash), computed once
        /// per piece object (a published piece is never changed; a reused piece keeps its memo).</summary>
        internal static ulong PieceSig(LaidPiece p)
        {
            if (p.SigMemoSet) return p.SigMemo;
            ulong h = Basis;
            string k = p.Key ?? "";
            foreach (char c in k) h = Mix(h, c);
            h = Mix(h, (ulong)k.Length);
            h = Mix(h, p.GeometryHash());
            p.SigMemo = h;
            p.SigMemoSet = true;
            return h;
        }

        /// <summary>A section's owned-set signature as a 64-bit hash, allocation-free: per piece in print order its key and
        /// geometry, net seed and material index, then (eligibility on) each strand's static/dynamic bits in print order.
        /// Carries exactly what the former string signature carried (key@geometry#seed%mat, then " e" + one char per strand);
        /// 0 means "no pieces here" (the former empty string). <paramref name="elig"/> null = sway and ripple both off.</summary>
        internal static ulong SectionSig(List<LaidPiece> l, Dictionary<LaidPiece, int> seeds, Dictionary<LaidPiece, int> mats, Func<CordStrand, int> elig)
        {
            if (l == null) return 0UL;
            ulong h = Basis;
            foreach (LaidPiece p in l)
            {
                h = Mix(h, PieceSig(p));
                h = Mix(h, (ulong)(uint)(seeds.TryGetValue(p, out int v) ? v : 0));
                h = Mix(h, (ulong)(uint)(mats.TryGetValue(p, out int g) ? g : -1));
            }
            h = Mix(h, (ulong)l.Count);
            if (elig != null)
            {
                h = Mix(h, 0x65UL);
                foreach (LaidPiece p in l)
                    foreach (CordStrand st in p.Strands)
                        h = Mix(h, st.Pts == null || st.Pts.Count < 2 ? 0x2dUL : (ulong)(0x100 | elig(st)));
            }
            return h == 0UL ? 1UL : h;
        }
    }
}
