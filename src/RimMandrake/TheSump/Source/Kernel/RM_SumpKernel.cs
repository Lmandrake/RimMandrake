// Verse-free kernels of The Sump: the kethrel's scrap-shell decisions, the tar vault's seal ledger and the Deep Black mere's
// randomized flood fill. The kethrel comp, the vault comp and the mere gen step call these with the same expressions;
// SelfTest/SumpFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine (a `using Verse;` here breaks the
// self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.TheSump
{
    // ════════════════════════ the kethrel's shell ════════════════════════

    public enum KethrelAction { None, Molt, PickUp, Seek }

    public static class RM_KethrelKernel
    {
        public const float MoltFailBase = 0.45f;
        public const float MoltFailPerSkill = 0.03f;
        public const float MoltFailMin = 0.02f;
        public const float MoltFailMax = 0.9f;

        /// <summary>Carried kilograms at which the shell steps up to stage 1, 2, 3...: the highest threshold reached.</summary>
        public static int StageForLoad(IList<float> stageLoadKg, float kg)
        {
            int s = 0;
            for (int i = 0; i < stageLoadKg.Count; i++)
            {
                if (kg >= stageLoadKg[i]) s = i + 1;
            }
            return s;
        }

        public static float HediffSeverity(int stage) { return stage + 0.01f; }

        /// <summary>The stage changed: the hediff and the sprite set must be refreshed.</summary>
        public static bool StageChanged(int oldStage, int newStage) { return newStage != oldStage; }

        /// <summary>What a rare tick does. Order: switched off / dead / unspawned / downed do nothing; a full load molts; no tar nearby does nothing;
        /// an item in pickup reach is taken; otherwise an idle animal walks to a wanted item it can reach. The probes are lazy and evaluated in
        /// that order (scanning the map is not free), each only if everything before it let the tick go on.</summary>
        public static KethrelAction Decide(bool enabled, bool dead, bool spawned, bool downed, Func<float> loadKg, float moltLoadKg, Func<bool> tarNearby,
            Func<bool> itemInPickupReach, Func<bool> idle, Func<bool> seekItemReachable)
        {
            if (!enabled || dead || !spawned || downed) return KethrelAction.None;
            if (loadKg() >= moltLoadKg) return KethrelAction.Molt;
            if (!tarNearby()) return KethrelAction.None;
            if (itemInPickupReach()) return KethrelAction.PickUp;
            if (idle() && seekItemReachable()) return KethrelAction.Seek;
            return KethrelAction.None;
        }

        /// <summary>Is a loose thing something it wants to wear?</summary>
        public static bool Wanted(bool thingOk, bool isItem, bool forbiddenForIt, bool isWeaponOrListed, float marketValueTotal, float valueCeiling,
            bool takeColonyProperty, bool onHomeArea)
        {
            if (!thingOk || !isItem || forbiddenForIt) return false;
            if (!isWeaponOrListed) return false;
            if (marketValueTotal > valueCeiling) return false;
            if (!takeColonyProperty && onHomeArea) return false;
            return true;
        }

        /// <summary>Tar is recognised by name: terrain or filth whose defName contains "Tar".</summary>
        public static bool IsTarName(string defName) { return defName != null && defName.Contains("Tar"); }

        /// <summary>Chance a coaxed molt ends in a panicked charge.</summary>
        public static float FailChance(int animalsSkill, float difficulty)
        {
            float v = MoltFailBase * difficulty - MoltFailPerSkill * animalsSkill;
            return v < MoltFailMin ? MoltFailMin : v > MoltFailMax ? MoltFailMax : v;
        }

        /// <summary>The handler is the able colonist with the highest Animals skill (the first of equals); -1 when none can.</summary>
        public static int BestHandler(IList<int> skills, IList<bool> able)
        {
            int best = -1, bestSkill = -1;
            for (int i = 0; i < skills.Count; i++)
            {
                if (!able[i]) continue;
                if (skills[i] > bestSkill) { bestSkill = skills[i]; best = i; }
            }
            return best;
        }

        public static string StageLabel(int s)
        {
            switch (s)
            {
                case 1: return "light shell";
                case 2: return "heavy shell";
                case 3: return "full carapace";
                default: return "bare";
            }
        }
    }

    // ════════════════════════ the tar vault ════════════════════════

    public enum ExtractPlan { Ignore, Clean, Ruined }

    /// <summary>The vault's record of what it has sealed. Seal/unseal are done by the caller through the two delegates.</summary>
    public sealed class RM_VaultLedger<T> where T : class
    {
        public List<T> sealedThings = new List<T>();

        public bool IsSealed(T t) { return sealedThings.Contains(t); }

        /// <summary>One scan: every present thing not yet sealed is sealed; every sealed thing no longer present, null or destroyed is
        /// forgotten (and unsealed if it still exists).</summary>
        public void Scan(IList<T> present, Func<T, bool> destroyed, Action<T> seal, Action<T> unseal)
        {
            for (int i = 0; i < present.Count; i++)
            {
                T t = present[i];
                if (sealedThings.Contains(t)) continue;
                sealedThings.Add(t);
                seal(t);
            }
            for (int i = sealedThings.Count - 1; i >= 0; i--)
            {
                T t = sealedThings[i];
                if (t != null && !destroyed(t) && present.Contains(t)) continue;
                sealedThings.RemoveAt(i);
                if (t != null && !destroyed(t)) unseal(t);
            }
        }

        /// <summary>Extraction: a sealed target comes out clean when a solvent is on hand (one is spent), ruined otherwise.</summary>
        public ExtractPlan Plan(T target, bool targetDestroyed, bool solventOnHand)
        {
            if (target == null || targetDestroyed || !sealedThings.Contains(target)) return ExtractPlan.Ignore;
            return solventOnHand ? ExtractPlan.Clean : ExtractPlan.Ruined;
        }

        public void Forget(T target) { sealedThings.Remove(target); }

        public static int RuinedStack(int count) { return Math.Max(1, count); }

        public static bool ScanDue(bool enabled, int scanIntervalTicks, int ticksGame)
        {
            if (!enabled) return false;
            if (scanIntervalTicks <= 0 || ticksGame % scanIntervalTicks != 0) return false;
            return true;
        }
    }

    // ════════════════════════ the Deep Black mere ════════════════════════

    public interface IMereRng
    {
        /// <summary>Uniform integer in [minInclusive, maxExclusive).</summary>
        int Range(int minInclusive, int maxExclusive);
    }

    public interface IMereGrid
    {
        int Width { get; }
        int Height { get; }
        /// <summary>Open ordinary ground: in bounds, not on the edge, not water, nothing built on it.</summary>
        bool CanCarry(int x, int z);
    }

    public static class RM_MereKernel
    {
        public const int MinMereCells = 180;
        public const int MaxMereCells = 420;
        public const int MinEdgeDistance = 12;
        public const int MaxGrowAttempts = 4000;

        public static int EdgeDistance(int x, int z, int width, int height)
        {
            int distX = Math.Min(x, width - 1 - x);
            int distZ = Math.Min(z, height - 1 - z);
            return Math.Min(distX, distZ);
        }

        public static bool IsSeedCandidate(IMereGrid g, int x, int z)
        {
            return EdgeDistance(x, z, g.Width, g.Height) >= MinEdgeDistance && g.CanCarry(x, z);
        }

        public static int Key(int x, int z, int width) { return z * width + x; }

        /// <summary>Randomized flood fill: repeatedly pop a random frontier cell and grow into one open cardinal neighbour, picked
        /// uniformly among the eligible ones by reservoir sampling. A frontier cell with no eligible neighbour is dropped.</summary>
        public static HashSet<int> GrowBlob(IMereGrid g, int seedX, int seedZ, IMereRng rng, int targetSize, int maxAttempts)
        {
            int w = g.Width;
            var placed = new HashSet<int> { Key(seedX, seedZ, w) };
            var frontier = new List<int> { Key(seedX, seedZ, w) };
            int attempts = maxAttempts;
            while (placed.Count < targetSize && frontier.Count > 0 && attempts-- > 0)
            {
                int pick = rng.Range(0, frontier.Count);
                int from = frontier[pick];
                int fx = from % w, fz = from / w;
                int target = -1, seen = 0;
                for (int i = 0; i < 4; i++)
                {
                    int nx = fx + (i == 0 ? 0 : i == 1 ? 1 : i == 2 ? 0 : -1);
                    int nz = fz + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? -1 : 0);
                    if (nx < 0 || nz < 0 || nx >= w || nz >= g.Height) continue;
                    int nk = Key(nx, nz, w);
                    if (placed.Contains(nk) || !g.CanCarry(nx, nz)) continue;
                    seen++;
                    if (rng.Range(0, seen) == 0) target = nk;
                }
                if (target < 0)
                {
                    frontier.RemoveAt(pick);
                    continue;
                }
                placed.Add(target);
                frontier.Add(target);
            }
            return placed;
        }

        /// <summary>The cells just outside the blob (cardinal neighbours, in bounds, not in the blob).</summary>
        public static HashSet<int> RimOf(IMereGrid g, HashSet<int> blob)
        {
            int w = g.Width;
            var rim = new HashSet<int>();
            foreach (int k in blob)
            {
                int x = k % w, z = k / w;
                for (int i = 0; i < 4; i++)
                {
                    int nx = x + (i == 0 ? 0 : i == 1 ? 1 : i == 2 ? 0 : -1);
                    int nz = z + (i == 0 ? 1 : i == 1 ? 0 : i == 2 ? -1 : 0);
                    if (nx < 0 || nz < 0 || nx >= w || nz >= g.Height) continue;
                    int nk = Key(nx, nz, w);
                    if (!blob.Contains(nk)) rim.Add(nk);
                }
            }
            return rim;
        }

        /// <summary>A mere smaller than the landmark minimum is not made at all.</summary>
        public static bool Acceptable(int blobCells) { return blobCells >= MinMereCells; }
    }
}
