// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phases 3-4 -- the pure half of territory (L5) and the tremor (L6).
//
// Spec design/RimMandrake/atmospheric_base_mod_definition.md §2.6 steps 2-3:
//   * the top two moods by rank take TERRITORY over the union of their groups, the boundary advancing on its own slow
//     clock (L5: blend by allocation, never by colour-mixing -- every fixture shows exactly one claimant's palette);
//   * moods ranked third and below become TREMOR -- brief flickers, each in the claimant's own palette, capped at three
//     contributors (L6), and never loud enough to be mistaken for territory (north star never_tremor_reads_as_territory).
// Rank is READ, never computed here (§2.5, item "watch out"): it is used only to ORDER claims. How much ground the
// leader holds is a Mod Setting (leadShare), not a function of the rank's magnitude.
// No game types: an emitter is an id and a position. The selftest drives every function here directly.
//
// The boundary. Fixtures in the union are ordered by their bearing around the union's centre; the louder claimant
// holds a WEDGE of ceil(leadShare * N) consecutive fixtures in that order, the other claimant the rest, and the wedge
// turns once per periodSeconds -- two fronts sweeping round the ship like the hands of a clock. Owner rulings this
// meets by construction:
//   * it reads on an IRREGULAR scatter (the authored canvas "will be irregular", 2026-09-17): a share of the fixtures,
//     not a share of the floor, so both presences hold ground however the lights are placed -- even on 11 fixtures;
//   * it MOVES (territory_boundary_moves: "a static split is a different and lesser thing"): every fixture changes
//     hands at least twice in a turn, the centre of the ship included. (A straight line cut at a fixed share would
//     leave the fixtures near the centre with the louder claimant for ever -- a static heartland.)
// The wedge advances in StepsPerTurn discrete steps, so between steps the allocation is identical and nothing is
// rewritten; only fixtures a front crossed change (§2.6 step 6: cost tracks the moving front, not the grid).
// `ragged` adds a fixed per-fixture bearing offset (up to ragged * 180 degrees) so a front is not a ruler line; at 0
// the louder claimant's fixtures are exactly contiguous in bearing, which the selftest asserts.
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public struct RM_TerritoryTuning
    {
        public float periodSeconds;   // one full turn of the boundary
        public float leadShare;       // fraction of the union the louder claimant holds
        public float ragged;          // per-fixture offset, fraction of the canvas extent

        public static RM_TerritoryTuning Clamp(RM_TerritoryTuning t)
        {
            return new RM_TerritoryTuning
            {
                periodSeconds = Math.Max(RM_TerritoryKernel.MinPeriodSeconds, float.IsNaN(t.periodSeconds) ? 0f : t.periodSeconds),
                leadShare = Math.Min(RM_TerritoryKernel.MaxLeadShare, Math.Max(RM_TerritoryKernel.MinLeadShare, float.IsNaN(t.leadShare) ? 0.5f : t.leadShare)),
                ragged = Math.Min(RM_TerritoryKernel.MaxRagged, Math.Max(0f, float.IsNaN(t.ragged) ? 0f : t.ragged)),
            };
        }
    }

    public struct RM_TremorTuning
    {
        public int cap;               // contributors, never more than RM_TremorKernel.LawCap (L6)
        public float slotSeconds;     // a fixture may flicker once in a slot of this length
        public float flickerSeconds;  // how long one flicker lasts
        public int oneIn;             // a fixture flickers in 1 of this many slots
        public float maxFraction;     // at most this share of the driven fixtures flicker at one instant (>= 1 fixture)

        public static RM_TremorTuning Clamp(RM_TremorTuning t)
        {
            float slot = Math.Max(RM_TremorKernel.MinSlotSeconds, float.IsNaN(t.slotSeconds) ? 0f : t.slotSeconds);
            return new RM_TremorTuning
            {
                cap = Math.Min(RM_TremorKernel.LawCap, Math.Max(0, t.cap)),
                slotSeconds = slot,
                flickerSeconds = Math.Min(RM_TremorKernel.MaxFlickerSeconds, Math.Min(slot * 0.25f, Math.Max(0.1f, float.IsNaN(t.flickerSeconds) ? 0.1f : t.flickerSeconds))),
                oneIn = Math.Max(1, t.oneIn),
                maxFraction = Math.Min(RM_TremorKernel.MaxFraction, Math.Max(0f, float.IsNaN(t.maxFraction) ? 0f : t.maxFraction)),
            };
        }
    }

    public static class RM_TerritoryKernel
    {
        public const float MinPeriodSeconds = 240f;   // a boundary that turns faster than this is a light show, not a front
        public const float MinLeadShare = 0.5f;
        public const float MaxLeadShare = 0.8f;       // the quieter of the two always keeps a fifth: two presences, not one
        public const float MaxRagged = 0.25f;
        public const int StepsPerTurn = 240;

        // ---------------------------------------------------------------- ordering by rank (read, never computed)

        /// <summary>Negative when a outranks b. Higher rank first; equal rank broken by claimant ordinal, so the order
        /// never depends on push order or list order.</summary>
        public static int CompareRank(float rankA, string claimantA, float rankB, string claimantB)
        {
            if (rankA > rankB) return -1;
            if (rankA < rankB) return 1;
            return string.CompareOrdinal(claimantA ?? "", claimantB ?? "");
        }

        /// <summary>Indices of the claims in rank order (loudest first).</summary>
        public static int[] RankOrder(IList<float> ranks, IList<string> claimants)
        {
            int n = ranks.Count;
            var idx = new int[n];
            for (int i = 0; i < n; i++) idx[i] = i;
            Array.Sort(idx, (x, y) => CompareRank(ranks[x], claimants[x], ranks[y], claimants[y]));
            return idx;
        }

        /// <summary>A stable salt for a pair of claimants, so two gods start their front at their own angle and the
        /// same two gods always do.</summary>
        public static int PairSalt(string lead, string other)
        {
            uint h = 2166136261U;
            string s = (lead ?? "") + "\u0001" + (other ?? "");
            for (int i = 0; i < s.Length; i++) { h ^= s[i]; h *= 16777619U; }
            return unchecked((int)RM_SchemeKernel.Mix(h));
        }

        // ---------------------------------------------------------------- the boundary's own clock

        public static long ClockStep(double time, float periodSeconds)
        {
            double p = Math.Max(MinPeriodSeconds, periodSeconds);
            return (long)Math.Floor(time / p * StepsPerTurn);
        }

        public static double Angle(long step, int pairSalt)
        {
            double phase = RM_SchemeKernel.Frac01(pairSalt, 11);
            long k = ((step % StepsPerTurn) + StepsPerTurn) % StepsPerTurn;
            return 2.0 * Math.PI * (k / (double)StepsPerTurn + phase);
        }

        public static int LeadCount(int n, float leadShare)
        {
            if (n <= 0) return 0;
            if (n == 1) return 1;
            int k = (int)Math.Ceiling(n * (double)Math.Min(MaxLeadShare, Math.Max(MinLeadShare, leadShare)) - 1e-9);
            return Math.Max(1, Math.Min(n - 1, k));   // with two or more fixtures, both claimants hold ground
        }

        /// <summary>Bearing (radians) of each fixture around the union's centre, with the ragged offset. Pure.</summary>
        public static double[] Bearings(IList<int> ids, IList<float> x, IList<float> z, float ragged)
        {
            int n = ids.Count;
            var bear = new double[n];
            if (n == 0) return bear;
            double cx = 0, cz = 0;
            for (int i = 0; i < n; i++) { cx += x[i]; cz += z[i]; }
            cx /= n; cz /= n;
            for (int i = 0; i < n; i++)
                bear[i] = Math.Atan2(z[i] - cz, x[i] - cx) + ragged * Math.PI * (RM_SchemeKernel.Frac01(ids[i], 13) - 0.5);
            return bear;
        }

        /// <summary>The fixtures in bearing order (ties by id): the order the wedge walks.</summary>
        public static int[] BearingOrder(IList<int> ids, IList<float> x, IList<float> z, float ragged)
        {
            double[] bear = Bearings(ids, x, z, ragged);
            int n = ids.Count;
            var order = new int[n];
            for (int i = 0; i < n; i++) order[i] = i;
            Array.Sort(order, (p, q) =>
            {
                int c = bear[p].CompareTo(bear[q]);
                return c != 0 ? c : ids[p].CompareTo(ids[q]);
            });
            return order;
        }

        /// <summary>Where the wedge starts in the bearing order at this step.</summary>
        public static int WedgeStart(int n, long step, int pairSalt)
        {
            if (n <= 0) return 0;
            double u = Angle(step, pairSalt) / (2.0 * Math.PI);
            u -= Math.Floor(u);
            return Math.Min(n - 1, (int)Math.Floor(u * n));
        }

        /// <summary>Who holds each fixture of the union at this clock step: true = the louder claimant. Pure.</summary>
        public static bool[] Allocate(IList<int> ids, IList<float> x, IList<float> z, long step, int pairSalt, RM_TerritoryTuning tuning)
        {
            int n = ids.Count;
            var lead = new bool[n];
            if (n == 0) return lead;
            RM_TerritoryTuning t = RM_TerritoryTuning.Clamp(tuning);
            int[] order = BearingOrder(ids, x, z, t.ragged);
            int k = LeadCount(n, t.leadShare);
            int start = WedgeStart(n, step, pairSalt);
            for (int i = 0; i < k; i++) lead[order[(start + i) % n]] = true;
            return lead;
        }
    }

    /// <summary>One tremor contributor as the kernel sees it: its palette size, a salt, and the fixtures it may touch.</summary>
    public struct RM_TremorSource
    {
        public int paletteCount;
        public int salt;
        public IList<int> members;
    }

    public static class RM_TremorKernel
    {
        public const int LawCap = 3;              // L6: "the two or three most agitated silent gods"
        public const float MaxFraction = 0.10f;   // never_tremor_reads_as_territory: a tenth is the hard ceiling
        public const float MinSlotSeconds = 4f;
        public const float MaxFlickerSeconds = 2f;

        /// <summary>Does this fixture flicker for this contributor at this time, and to which palette entry. Pure.</summary>
        public static bool Flickers(int emitter, int salt, int paletteCount, double time, RM_TremorTuning t, out int index)
        {
            index = 0;
            if (paletteCount <= 0) return false;
            double shifted = time + RM_SchemeKernel.Frac01(emitter ^ salt, 17) * t.slotSeconds;
            long slot = (long)Math.Floor(shifted / t.slotSeconds);
            uint h = RM_SchemeKernel.Mix(emitter ^ salt, unchecked((int)slot));
            if (h % (uint)t.oneIn != 0) return false;
            if (shifted - slot * (double)t.slotSeconds >= t.flickerSeconds) return false;
            index = (int)((h >> 8) % (uint)paletteCount);
            return true;
        }

        public static int InstantCap(int drivenCount, float maxFraction)
        {
            if (drivenCount <= 0) return 0;
            return Math.Max(1, (int)Math.Floor(drivenCount * (double)Math.Min(MaxFraction, Math.Max(0f, maxFraction)) + 1e-4));   // 0.04f is 0.03999..: 300 x 4% is 12, not 11
        }

        /// <summary>Which fixtures flicker now: id -> (contributor index, palette index). Contributors are given loudest
        /// first; beyond LawCap (or tuning.cap) they are ignored. A fixture two contributors want goes to the louder. At
        /// most InstantCap(drivenCount) fixtures flicker at once, chosen by a stable hash, never by list order.</summary>
        public static Dictionary<int, KeyValuePair<int, int>> Assign(IList<RM_TremorSource> sources, double time, int drivenCount, RM_TremorTuning tuning)
        {
            var outp = new Dictionary<int, KeyValuePair<int, int>>();
            RM_TremorTuning t = RM_TremorTuning.Clamp(tuning);
            if (sources == null || t.cap == 0 || !(t.maxFraction > 0f)) return outp;
            var cand = new List<KeyValuePair<uint, int>>();
            for (int s = 0; s < sources.Count && s < t.cap; s++)
            {
                RM_TremorSource src = sources[s];
                if (src.members == null) continue;
                for (int i = 0; i < src.members.Count; i++)
                {
                    int id = src.members[i];
                    if (outp.ContainsKey(id)) continue;
                    if (!Flickers(id, src.salt, src.paletteCount, time, t, out int idx)) continue;
                    outp[id] = new KeyValuePair<int, int>(s, idx);
                    cand.Add(new KeyValuePair<uint, int>(RM_SchemeKernel.Mix(id, 23), id));
                }
            }
            int cap = InstantCap(drivenCount, t.maxFraction);
            if (outp.Count > cap)
            {
                cand.Sort((p, q) => p.Key != q.Key ? p.Key.CompareTo(q.Key) : p.Value.CompareTo(q.Value));
                for (int i = cap; i < cand.Count; i++) outp.Remove(cand[i].Value);
            }
            return outp;
        }
    }
}
