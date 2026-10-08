// Verse-free kernel of the ancient mirror field (SOLAR_MIRRORS_MOD_DESIGN_1 §3.4, SOLAR_MIRRORS_BUILD_1): the configuration space
// (n mirrors x d detents, one detent each), the exhaustive solver mapgen runs before it places a field, the acceptance rule, and
// the hint walk. A configuration is coded base d, mirror 0 in the lowest digit. One re-aim job turns ONE mirror to ANY of its
// detents, so the number of jobs between two configurations is their Hamming distance, every configuration reaches every other
// (the reset path always exists), and the shortest route to a solution is the distance to the nearest one. The light itself is
// the caller's: Solve asks `eval` for each configuration (mapgen evaluates it with the real light pass on the real map).
// The stones keep their lit state down to a lower threshold (hysteresis, design §3.4), so a configuration can HOLD every stone
// lit without lighting it from dark. The evaluator reports both levels: existence and hints use the strict set (every stone
// >= litAt from dark), while the start and the "nearest solution >= N re-aims" guarantee use the held set (every stone
// >= unlitBelow), which is the only safe lower bound on how many jobs a colony needs (SOLAR_MIRRORS_BUILD_1 validation D3).
// Generate is the whole layout search mapgen runs (RM_MirrorFieldBuilder), behind delegates, so it is fuzzed too.
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
        public int minStrict = -1;          // Hamming distance from the start to the nearest STRICT solution; -1 with none
        public readonly List<int> solutions = new List<int>();   // strict: every stone lit from dark
        public readonly List<int> depths = new List<int>();
        public readonly List<int> holds = new List<int>();       // every stone at least held lit (strict ones included)
    }

    /// <summary>What Generate settled on: the report, each mirror's detent target ids, the start code; or why not.</summary>
    public sealed class RM_FieldLayout
    {
        public RM_FieldReport report;
        public List<List<int>> detents;
        public int start = -1;
        public string why;
        public int attempts;
        public int evaluations;
        public bool Ok => report != null && start >= 0 && why == null;
    }

    public static class RM_MirrorFieldKernel
    {
        public const int MaxConfigurations = 4096;

        public delegate bool Evaluate(int[] config, out int maxDepth);

        /// <summary>Light levels a configuration reaches: Dark (some stone below the hold threshold), Held (every stone at
        /// least held lit, not every one lit from dark), Lit (every stone lit from dark).</summary>
        public const int Dark = 0, Held = 1, Lit = 2;

        public delegate int EvaluateLevel(int[] config, out int maxDepth);

        // ── settings-shaped clamps (mapgen reads these, so the fuzz can sweep out-of-range settings) ──
        public static int FieldMirrors(int setting) { return setting < 4 ? 4 : setting > 6 ? 6 : setting; }
        public static int FieldMinReAims(int setting) { return setting < 2 ? 2 : setting > 4 ? 4 : setting; }
        public static int FieldDetents(int extension) { return extension < 2 ? 2 : extension; }

        /// <summary>The level of one configuration from the stones' light: Lit when every stone reaches litAt, Held when
        /// every stone reaches unlitBelow (the hysteresis keeps a lit stone lit there), else Dark. No stones = Lit.</summary>
        public static int LevelOf(float[] stoneLight, int count, float litAt, float unlitBelow)
        {
            int level = Lit;
            for (int k = 0; k < count; k++)
            {
                float l = stoneLight[k];
                if (l >= litAt)
                {
                    continue;
                }
                if (l >= unlitBelow)
                {
                    level = Held;
                    continue;
                }
                return Dark;
            }
            return level;
        }

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

        /// <summary>Evaluate every configuration once, pass/fail only (held == lit). Null when the space is too large.</summary>
        public static RM_FieldReport Solve(int n, int d, int[] start, Evaluate eval)
        {
            return Solve(n, d, start, (int[] cfg, out int depth) => eval(cfg, out depth) ? Lit : Dark);
        }

        /// <summary>Evaluate every configuration once. Null when the space is too large (or n/d out of range).</summary>
        public static RM_FieldReport Solve(int n, int d, int[] start, EvaluateLevel eval)
        {
            int total = Configurations(n, d);
            if (total < 0 || start == null || start.Length < n)
            {
                return null;
            }
            RM_FieldReport r = new RM_FieldReport { mirrors = n, detents = d, configurations = total, startCode = Encode(start, n, d) };
            int[] cfg = new int[n];
            for (int code = 0; code < total; code++)
            {
                Decode(code, n, d, cfg);
                int level = eval(cfg, out int depth);
                if (level >= Held)
                {
                    r.holds.Add(code);
                }
                if (level >= Lit)
                {
                    r.solutions.Add(code);
                    r.depths.Add(depth);
                }
            }
            r.solutionCount = r.solutions.Count;
            Rebase(r, r.startCode);
            return r;
        }

        /// <summary>Recompute the start-dependent fields for another start (no re-evaluation). minReAims and startSolved
        /// read the held set (the lower bound); bestSolution/bestDepth/minStrict the strict one.</summary>
        public static void Rebase(RM_FieldReport r, int startCode)
        {
            r.startCode = startCode;
            r.minReAims = -1;
            r.minStrict = -1;
            r.bestSolution = -1;
            r.bestDepth = 0;
            for (int k = 0; k < r.solutions.Count; k++)
            {
                int h = Hamming(r.startCode, r.solutions[k], r.mirrors, r.detents);
                if (r.minStrict < 0 || h < r.minStrict)
                {
                    r.minStrict = h;
                    r.bestSolution = r.solutions[k];
                    r.bestDepth = r.depths[k];
                }
            }
            IList<int> lower = r.holds.Count > 0 ? r.holds : r.solutions;
            for (int k = 0; k < lower.Count; k++)
            {
                int h = Hamming(r.startCode, lower[k], r.mirrors, r.detents);
                if (r.minReAims < 0 || h < r.minReAims)
                {
                    r.minReAims = h;
                }
            }
            r.startSolved = r.minReAims == 0;
        }

        /// <summary>A start whose nearest HELD configuration is at least `want` jobs away, chosen by `seed` among all such
        /// configurations; -1 when none exists or there is no strict solution.</summary>
        public static int PickStart(RM_FieldReport r, int want, int seed)
        {
            if (r == null || r.solutionCount == 0)
            {
                return -1;
            }
            IList<int> lower = r.holds.Count > 0 ? r.holds : r.solutions;
            List<int> ok = new List<int>();
            for (int code = 0; code < r.configurations; code++)
            {
                Nearest(lower, code, r.mirrors, r.detents, out int dist);
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

        /// <summary>In-place Fisher-Yates with the caller's generator (rand(k) in 0..k-1).</summary>
        public static void Shuffle<T>(IList<T> list, Func<int, int> rand)
        {
            for (int i = list.Count - 1; i > 0; i--)
            {
                int j = rand(i + 1);
                T t = list[i];
                list[i] = list[j];
                list[j] = t;
            }
        }

        /// <summary>The layout search mapgen runs on one planned site (design §3.4). Targets are opaque ids: stoneTarget(k)
        /// is stone k's, candidates(i) lists mirror i's possible detent targets (fresh each attempt; stones, other mirrors,
        /// decoys). Each attempt hides an intended solution (stone k is a detent of mirror (k + shift) mod n), fills each
        /// mirror up to d distinct detents, applies them (apply), solves every configuration with the real light (eval),
        /// depthCap is the raw maxChain setting,
        /// picks a start at least `want` jobs from every HELD configuration, and keeps it only if Acceptable. Bounded:
        /// at most `attempts` attempts and attempts x d^n evaluations. rand(k) returns 0..k-1.</summary>
        public static RM_FieldLayout Generate(int n, int d, int stones, int want, int depthCap, int attempts, Func<int, int> rand,
            Func<int, List<int>> candidates, Func<int, int> stoneTarget, Action<List<List<int>>> apply, EvaluateLevel eval,
            int maxEvaluations = int.MaxValue)
        {
            int perSolve = Configurations(n, d);
            RM_FieldLayout result = new RM_FieldLayout { why = "no layout" };
            if (n < 1 || d < 1)
            {
                result.why = "no mirrors or no detents";
                return result;
            }
            for (int attempt = 0; attempt < attempts; attempt++)
            {
                // a whole solve per attempt: stop before one that would pass the caller's budget (mapgen cost, pass 2)
                if (perSolve > 0 && (long)result.evaluations + perSolve > maxEvaluations)
                {
                    result.why = "evaluation budget spent";
                    break;
                }
                result.attempts++;
                List<List<int>> det = new List<List<int>>();
                int shift = rand(n);
                bool enough = true;
                for (int i = 0; i < n && enough; i++)
                {
                    List<int> cand = candidates(i) ?? new List<int>();
                    List<int> mine = new List<int>();
                    int stoneFor = ((i - shift) % n + n) % n;
                    if (stoneFor < stones)
                    {
                        mine.Add(stoneTarget(stoneFor));
                    }
                    Shuffle(cand, rand);
                    for (int c = 0; c < cand.Count && mine.Count < d; c++)
                    {
                        if (!mine.Contains(cand[c]))
                        {
                            mine.Add(cand[c]);
                        }
                    }
                    if (mine.Count < d)
                    {
                        enough = false;
                        break;
                    }
                    Shuffle(mine, rand);
                    det.Add(mine);
                }
                if (!enough)
                {
                    result.why = "too few detent targets";
                    continue;
                }
                apply(det);
                RM_FieldReport r = Solve(n, d, new int[n], (int[] cfg, out int depth) =>
                {
                    result.evaluations++;
                    return eval(cfg, out depth);
                });
                int s0 = PickStart(r, want, rand(int.MaxValue));
                if (s0 < 0)
                {
                    result.why = r == null ? "space too large" : r.solutionCount == 0 ? "no configuration lights every stone" : "every start is too close to a solution";
                    continue;
                }
                Rebase(r, s0);
                // The pass fires depths 0 .. DepthCap(setting)-1, so that is the deepest chain a solution may need; the raw
                // setting is clamped the way the pass clamps it (an out-of-range setting must not refuse every layout).
                if (!Acceptable(r, want, RM_MirrorKernel.DepthCap(depthCap) - 1, out string why))
                {
                    result.why = why;
                    continue;
                }
                result.report = r;
                result.detents = det;
                result.start = s0;
                result.why = null;
                return result;
            }
            return result;
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
                why = "the start is already solved (or held lit)";
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
