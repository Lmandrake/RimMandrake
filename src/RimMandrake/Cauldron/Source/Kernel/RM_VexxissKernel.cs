// Verse-free kernel of the vexxiss behaviours that have a real seam (CAULDRON_MECHANICS_BUILD_1 part 5, CAULDRON_ENRICHMENT_VISUALS_1
// V4): the fire-warden choice, the poisoned-water letter throttle, and the print ledger (stepping, cap, expiry) behind the
// footprint-grid prints. RM_CompVexxissBehaviour.cs and RM_VexxissPrints.cs call these with the same expressions;
// SelfTest/CauldronFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;
using System.Collections.Generic;

namespace RimMandrake.Cauldron
{
    public enum WardChoice { None = 0, AttackIgniter = 1, BeatFire = 2 }

    public static class RM_VexxissKernel
    {
        public const int MaxPrintEntries = 1500;
        public const int PrintExpiryCheckTicks = 250;

        // ---- fire warden ------------------------------------------------------------------------------
        public static bool WardCanAct(bool downed, bool awake, bool inMental, bool hasJobs, bool playerFactionDrafted, bool busyFighting)
        {
            if (downed || !awake || inMental) return false;
            if (!hasJobs) return false;
            if (playerFactionDrafted) return false;
            return !busyFighting;
        }

        // Not itself, spawned, alive, upright, on this map, not its own faction, within chase radius, reachable.
        public static bool IgniterAttackable(bool exists, bool isSelf, bool spawned, bool dead, bool downed, bool sameMap, bool sameFaction,
            float distSq, float chaseRadius, bool reachable)
        {
            if (!exists || isSelf) return false;
            if (!spawned || dead || downed || !sameMap) return false;
            if (sameFaction) return false;
            if (distSq > chaseRadius * chaseRadius) return false;
            return reachable;
        }

        public static WardChoice Ward(bool hasFire, bool attacksIgniterSetting, bool igniterAttackable, bool hasBeatFireVerb)
        {
            if (!hasFire) return WardChoice.None;
            if (attacksIgniterSetting && igniterAttackable) return WardChoice.AttackIgniter;
            return hasBeatFireVerb ? WardChoice.BeatFire : WardChoice.None;
        }

        // Nearest free-standing, reachable fire within the scan radius (d > max skips; d >= best skips); reachability is asked lazily.
        public static int NearestFire(float[] distSq, bool[] eligible, Func<int, bool> reachable, float radius)
        {
            float maxSq = radius * radius;
            int best = -1;
            float bestSq = float.MaxValue;
            for (int i = 0; i < distSq.Length; i++)
            {
                if (!eligible[i]) continue;
                if (distSq[i] > maxSq || distSq[i] >= bestSq) continue;
                if (!reachable(i)) continue;
                best = i;
                bestSq = distSq[i];
            }
            return best;
        }

        // The poisoned-water letter: toggle on, a colonist on the map, once per cooldown per animal.
        public static bool WarnWater(bool lettersOn, bool hasMap, bool anyColonist, int now, int lastLetterTick, int cooldownTicks)
        {
            if (!lettersOn || !hasMap || !anyColonist) return false;
            return !(now - lastLetterTick < cooldownTicks);
        }

        // ---- prints -----------------------------------------------------------------------------------
        // A new print only after moving printStepCells from the last one.
        public static bool StepFarEnough(bool lastValid, float distSq, float stepCells)
        {
            return !lastValid || !(distSq < stepCells * stepCells);
        }

        // On water the poisoned swap marks the passage; no prints on floors; only natural ground.
        public static bool PrintableTerrain(bool hasTerrain, bool water, bool natural) { return hasTerrain && !water && natural; }

        public static bool PrintAllowed(bool flying, bool downed) { return !(flying || downed); }
    }

    /// <summary>The print ledger: entries in laid order (so also expiry order for one lifetime), the newest entry per cell, a cap.</summary>
    public sealed class RM_PrintLedger<K, E> where E : class
    {
        public List<E> Entries = new List<E>();
        public readonly Dictionary<K, E> ByCell = new Dictionary<K, E>();
        private readonly Func<E, K> cellOf;
        private readonly Func<E, int> expiresOf;
        public int Evicted, Expired, Cleared;

        public RM_PrintLedger(Func<E, K> cellOf, Func<E, int> expiresOf)
        {
            this.cellOf = cellOf;
            this.expiresOf = expiresOf;
        }

        // Adds an entry; while over the cap the oldest is removed (clear(e) is asked for each removed current entry).
        public void Add(E e, int maxEntries, Action<E> clear)
        {
            Entries.Add(e);
            ByCell[cellOf(e)] = e;
            while (Entries.Count > maxEntries) { Evicted++; ExpireFirst(clear); }
        }

        // Removes the oldest entry; when it is still the newest on its cell, the cell's print is cleared.
        public void ExpireFirst(Action<E> clear)
        {
            E e = Entries[0];
            Entries.RemoveAt(0);
            if (ByCell.TryGetValue(cellOf(e), out E cur) && ReferenceEquals(cur, e))
            {
                ByCell.Remove(cellOf(e));
                Cleared++;
                clear(e);
            }
        }

        public void Tick(int now, Action<E> clear)
        {
            if (Entries.Count == 0 || now % RM_VexxissKernel.PrintExpiryCheckTicks != 0) return;
            while (Entries.Count > 0 && expiresOf(Entries[0]) <= now) { Expired++; ExpireFirst(clear); }
        }

        // After a load: drop nulls, rebuild the cell index from the saved order (the last entry on a cell wins).
        public void Rebuild()
        {
            if (Entries == null) Entries = new List<E>();
            Entries.RemoveAll(e => e == null);
            ByCell.Clear();
            foreach (E e in Entries) ByCell[cellOf(e)] = e;
        }
    }
}
