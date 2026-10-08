// Verse-free kernel of the ancient mirror field (SOLAR_MIRRORS_MOD_DESIGN_1 §3.4, SOLAR_MIRRORS_BUILD_1): the configuration space
// (n mirrors x d detents, one detent each), the exhaustive solver mapgen runs before it places a field, the acceptance rule, and
// the hint walk. A configuration is coded base d, mirror 0 in the lowest digit. One re-aim job turns ONE mirror to ANY of its
// detents, so the number of jobs between two configurations is their Hamming distance, every configuration reaches every other
// (the reset path always exists), and the shortest route to a solution is the distance to the nearest one. The light itself is
// the caller's: Solve asks `eval` for each configuration (mapgen evaluates it with the real light pass on the real map).
// The fuzz in SelfTest/ compiles this file alone: no Verse, RimWorld or UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.SolarMirrors
{
    public sealed class RM_FieldReport
    {
        public int mirrors, detents, configurations;
        public int startCode;
        public bool startSolved;
        public int solutionCount;
        public int minReAims = -1;          // Hamming distance from the start to the nearest solution; -1 with none
        public int bestSolution = -1;       // that nearest solution (lowest code on a tie)
        public int bestDepth;               // its deepest relay (0 = every stone lit straight from the sun)
        public readonly List<int> solutions = new List<int>();
        public readonly List<int> depths = new List<int>();
    }

    public static class RM_MirrorFieldKernel
    {
        public const int MaxConfigurations = 4096;

        public delegate bool Evaluate(int[] config, out int maxDepth);

        /// <summary>d^n, or -1 when it exceeds MaxConfigurations (or n/d are out of range).</summary>
        public static int Configurations(int n, int d)
        {
            if (n < 1 || d < 1)
            {
                return -1;
            }
            long c = 1;
            for (int i = 0; i < n; i++)
            {
                c *= d;
                if (c > MaxConfigurations)
                {
                    return -1;
                }
            }
            return (int)c;
        }

        public static void Decode(int code, int n, int d, int[] into)
        {
            for (int i = 0; i < n; i++)
            {
                into[i] = code % d;
                code /= d;
            }
        }

        public static int Encode(int[] config, int n, int d)
        {
            int code = 0;
            for (int i = n - 1; i >= 0; i--)
            {
                code = code * d + config[i];
            }
            return code;
        }

        public static int Hamming(int a, int b, int n, int d)
        {
            int h = 0;
            for (int i = 0; i < n; i++)
            {
                if (a % d != b % d)
                {
                    h++;
                }
                a /= d;
                b /= d;
            }
            return h;
        }

        /// <summary>Evaluate every configuration once. Null when the space is too large.</summary>
        public static RM_FieldReport Solve(int n, int d, int[] start, Evaluate eval)
        {
            int total = Configurations(n, d);
            if (total < 0)
            {
                return null;
            }
            RM_FieldReport r = new RM_FieldReport { mirrors = n, detents = d, configurations = total, startCode = Encode(start, n, d) };
            int[] cfg = new int[n];
            for (int code = 0; code < total; code++)
            {
                Decode(code, n, d, cfg);
                if (eval(cfg, out int depth))
                {
                    r.solutions.Add(code);
                    r.depths.Add(depth);
                }
            }
            r.solutionCount = r.solutions.Count;
            Rebase(r, r.startCode);
            return r;
        }

        /// <summary>Recompute the start-dependent fields for another start (no re-evaluation).</summary>
        public static void Rebase(RM_FieldReport r, int startCode)
        {
            r.startCode = startCode;
            r.minReAims = -1;
            r.bestSolution = -1;
            r.bestDepth = 0;
            for (int k = 0; k < r.solutions.Count; k++)
            {
                int h = Hamming(r.startCode, r.solutions[k], r.mirrors, r.detents);
                if (r.minReAims < 0 || h < r.minReAims)
                {
                    r.minReAims = h;
                    r.bestSolution = r.solutions[k];
                    r.bestDepth = r.depths[k];
                }
            }
            r.startSolved = r.minReAims == 0;
        }

        /// <summary>A start whose nearest solution is at least `want` jobs away, chosen by `seed` among all such
        /// configurations; -1 when none exists.</summary>
        public static int PickStart(RM_FieldReport r, int want, int seed)
        {
            if (r == null || r.solutionCount == 0)
            {
                return -1;
            }
            List<int> ok = new List<int>();
            for (int code = 0; code < r.configurations; code++)
            {
                Nearest(r.solutions, code, r.mirrors, r.detents, out int dist);
                if (dist >= Math.Max(1, want))
                {
                    ok.Add(code);
                }
            }
            if (ok.Count == 0)
            {
                return -1;
            }
            return ok[new Random(seed).Next(ok.Count)];
        }

        /// <summary>Design §3.4 acceptance: at least one solution, an unsolved start, the nearest solution at least
        /// `wantReAims` jobs away, and its relay depth within the cap. The reset path needs no test: every configuration
        /// reaches every other (one job per mirror changed).</summary>
        public static bool Acceptable(RM_FieldReport r, int wantReAims, int depthCap, out string why)
        {
            why = null;
            if (r == null)
            {
                why = "configuration space too large";
            }
            else if (r.solutionCount == 0)
            {
                why = "no configuration lights every stone";
            }
            else if (r.startSolved)
            {
                why = "the start is already solved";
            }
            else if (r.minReAims < wantReAims)
            {
                why = "the nearest solution is " + r.minReAims + " re-aims away, want " + wantReAims;
            }
            else if (r.bestDepth > depthCap)
            {
                why = "the nearest solution needs a chain " + r.bestDepth + " deep, cap " + depthCap;
            }
            return why == null;
        }

        /// <summary>The solution nearest to `code` (lowest code on a tie), or -1 with none. Its distance in `dist`.</summary>
        public static int Nearest(IList<int> solutions, int code, int n, int d, out int dist)
        {
            int best = -1;
            dist = -1;
            for (int k = 0; k < solutions.Count; k++)
            {
                int h = Hamming(code, solutions[k], n, d);
                if (best < 0 || h < dist || (h == dist && solutions[k] < best))
                {
                    best = solutions[k];
                    dist = h;
                }
            }
            return best;
        }

        /// <summary>The hint's next useful move: the lowest-numbered mirror whose detent differs from the nearest solution,
        /// and the detent it wants. False when already solved or there is no solution.</summary>
        public static bool NextMove(IList<int> solutions, int[] current, int n, int d, out int mirror, out int detent)
        {
            mirror = -1;
            detent = -1;
            int code = Encode(current, n, d);
            int target = Nearest(solutions, code, n, d, out int dist);
            if (target < 0 || dist == 0)
            {
                return false;
            }
            for (int i = 0; i < n; i++)
            {
                int want = target % d;
                if (want != current[i])
                {
                    mirror = i;
                    detent = want;
                    return true;
                }
                target /= d;
            }
            return false;
        }

        /// <summary>Design §3.4 escalating hints: 0 = how many stones are lit; 1 (after minReAims jobs) = which stone is
        /// missing light; 2 (after twice that) = the next useful detent.</summary>
        public static int HintLevel(int reAimsDone, int minReAims)
        {
            int step = Math.Max(1, minReAims);
            if (reAimsDone >= 2 * step)
            {
                return 2;
            }
            return reAimsDone >= step ? 1 : 0;
        }
    }
}
