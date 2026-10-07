// Verse-free kernel of the Forge's grand cycle (FORGE_CYCLE_MECHANICS_1): the phase order, phase lengths, the hiss and
// wave/flood schedules, batch sizing, and the crust bookkeeping (queue + frozen set) behind the freeze, the cracks and the
// melt-back. RM_GameCondition_ForgeCycle.cs calls these with the same expressions; SelfTest/TheForgeFuzz.cs compiles this
// file alone, so it must stay free of Verse/RimWorld/UnityEngine. (Math.Round/Ceiling here match Mathf.RoundToInt/CeilToInt.)
using System;
using System.Collections.Generic;

namespace RimMandrake.TheForge
{
    public enum ForgeCyclePhase
    {
        StillHeat = 0,
        GasWash = 1,
        Rain = 2,
        Freeze = 3,
        Growth = 4,
        Cracks = 5,
        Melt = 6,
    }

    public static class RM_CycleKernel
    {
        public const float TicksPerHour = 2500f;
        public const int CycleInterval = 60;
        public const float FreezeShare = 0.6f;
        public const float CrackShare = 0.5f;
        public const float MeltShare = 0.8f;

        // ---- order ------------------------------------------------------------------------------------
        // Nothing crusted (no lava on this map, or the freeze is switched off): growth, cracks and melt have nothing to stand
        // on, so the cycle closes early from the freeze.
        public static ForgeCyclePhase Next(ForgeCyclePhase phase, int frozenCount)
        {
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat: return ForgeCyclePhase.GasWash;
                case ForgeCyclePhase.GasWash: return ForgeCyclePhase.Rain;
                case ForgeCyclePhase.Rain: return ForgeCyclePhase.Freeze;
                case ForgeCyclePhase.Freeze: return frozenCount > 0 ? ForgeCyclePhase.Growth : ForgeCyclePhase.StillHeat;
                case ForgeCyclePhase.Growth: return ForgeCyclePhase.Cracks;
                case ForgeCyclePhase.Cracks: return ForgeCyclePhase.Melt;
                default: return ForgeCyclePhase.StillHeat;
            }
        }

        // Only a cycle that ran its melt counts.
        public static bool CountsAsCycle(ForgeCyclePhase leaving) { return leaving == ForgeCyclePhase.Melt; }

        public static int PhaseEnd(int now, float hoursRolled)
        {
            return now + Math.Max(CycleInterval, (int)Math.Round(hoursRolled * TicksPerHour));
        }

        // The cycle ticks on a 60-tick hash; with the cycle (or the pulse it rides) off no phase advances.
        public static bool CycleTickRuns(bool hashInterval, bool hasExtension, bool hasMap) { return hashInterval && hasExtension && hasMap; }
        public static bool Advances(bool cycleActive, bool pulseGateOpen) { return cycleActive && pulseGateOpen; }
        public static bool PhaseIsOver(int now, int phaseEndTick) { return now >= phaseEndTick; }

        // The ordinary short pulse bursts belong to the still heat only; with the cycle off the pulse behaves as it always did.
        public static bool AllowRandomBurst(bool cycleActive, bool hasExtension, ForgeCyclePhase phase)
        {
            return !cycleActive || !hasExtension || phase == ForgeCyclePhase.StillHeat;
        }

        public static bool UsesFreezeWeather(bool hasExtension, bool cycleActive, ForgeCyclePhase phase, bool hasWeather)
        {
            return hasExtension && cycleActive && phase == ForgeCyclePhase.Freeze && hasWeather;
        }

        // ---- telegraph and schedules ------------------------------------------------------------------
        public static bool HissDue(bool hissSent, int phaseEndTick, int now, float leadHours, bool gasWashOn)
        {
            return !hissSent && phaseEndTick - now <= leadHours * TicksPerHour && gasWashOn;
        }

        public static bool WaveDue(int wavesLeft, int now, int nextWaveTick) { return wavesLeft > 0 && now >= nextWaveTick; }

        // After a wave (wavesLeft already decremented): the rest are spread evenly over what remains of the phase.
        public static int NextWaveTick(int now, int phaseEndTick, int wavesLeft)
        {
            int span = Math.Max(1, phaseEndTick - now);
            return now + (wavesLeft > 0 ? span / (wavesLeft + 1) : span);
        }

        public static int WaveCount(int rolled, bool gasWashOn) { return gasWashOn ? Math.Max(1, rolled) : 0; }
        public static int FloodCount(int rolled) { return Math.Max(0, rolled); }
        public static int FirstFloodTick(int now) { return now + (int)Math.Round(0.5f * TicksPerHour); }
        public static float FloodVolume(int tiles, float volumePerTile) { return Math.Max(1, tiles) * Math.Max(0.0001f, volumePerTile); }

        // Spread a whole phase's work over the first `share` of its length: how many to do on this step.
        public static int BatchSize(int remaining, int now, int end, int phaseStart, float share)
        {
            int ticksLeft = Math.Max(CycleInterval, (int)Math.Round((end - phaseStart) * share) - (now - phaseStart));
            int batchesLeft = Math.Max(1, ticksLeft / CycleInterval);
            return Math.Max(1, (int)Math.Ceiling(remaining / (float)batchesLeft));
        }

        // The gentle melt-back used when the cycle is switched off while crust stands.
        public const int GentleBatch = 200;
    }

    /// <summary>The crust bookkeeping: the transient work queue and its phase tag, driven against the frozen set. Everything that
    /// touches terrain is a callback, so a harness can stand in for the map. T is IntVec3 in the game.</summary>
    public sealed class RM_CrustWork<T>
    {
        public List<T> Queue;
        public int QueuePhase = -1;

        // EnterPhase clears the queue but leaves the tag, as the old fields did.
        public void Reset() { Queue = null; }

        private bool Stale(ForgeCyclePhase phase) { return Queue == null || QueuePhase != (int)phase; }

        // Returns true while work remains.
        public bool Freeze(HashSet<T> frozen, IEnumerable<T> allCells, Func<T, bool> isFreezable, Action<List<T>> shuffle, int maxFrozen,
            int now, int phaseStart, int phaseEnd, Action<T> crustOne)
        {
            if (Stale(ForgeCyclePhase.Freeze))
            {
                Queue = new List<T>();
                foreach (T c in allCells)
                {
                    if (isFreezable(c)) Queue.Add(c);
                }
                shuffle(Queue);
                int room = Math.Max(0, maxFrozen - frozen.Count);
                if (Queue.Count > room) Queue.RemoveRange(room, Queue.Count - room);
                QueuePhase = (int)ForgeCyclePhase.Freeze;
            }
            if (Queue.Count == 0) return false;
            int n = Math.Min(Queue.Count, RM_CycleKernel.BatchSize(Queue.Count, now, phaseEnd, phaseStart, RM_CycleKernel.FreezeShare));
            for (int i = 0; i < n; i++)
            {
                T c = Queue[Queue.Count - 1];
                Queue.RemoveAt(Queue.Count - 1);
                if (!isFreezable(c)) continue;
                frozen.Add(c);
                crustOne(c);
            }
            return Queue.Count > 0;
        }

        public bool Crack(HashSet<T> frozen, Func<T, bool> needsCrack, Action<T> setCrack, Action<List<T>> shuffle, int now, int phaseStart, int phaseEnd)
        {
            if (Stale(ForgeCyclePhase.Cracks))
            {
                Queue = new List<T>(frozen);
                shuffle(Queue);
                QueuePhase = (int)ForgeCyclePhase.Cracks;
            }
            if (Queue.Count == 0) return false;
            int n = Math.Min(Queue.Count, RM_CycleKernel.BatchSize(Queue.Count, now, phaseEnd, phaseStart, RM_CycleKernel.CrackShare));
            for (int i = 0; i < n; i++)
            {
                T c = Queue[Queue.Count - 1];
                Queue.RemoveAt(Queue.Count - 1);
                if (!needsCrack(c)) continue;
                setCrack(c);
            }
            return Queue.Count > 0;
        }

        // Returns the number of cells processed as ours (StatCellsMelted); lossAt is the last cell where meltCell reported a loss.
        public int Melt(HashSet<T> frozen, Func<T, bool> isOurs, Func<T, bool> meltCell, Action<List<T>> shuffle, int batch, out bool anyLoss, out T lossAt)
        {
            anyLoss = false;
            lossAt = default(T);
            if (frozen.Count == 0) return 0;
            if (Stale(ForgeCyclePhase.Melt))
            {
                Queue = new List<T>(frozen);
                shuffle(Queue);
                QueuePhase = (int)ForgeCyclePhase.Melt;
            }
            int melted = 0;
            int n = Math.Min(Queue.Count, batch);
            for (int i = 0; i < n; i++)
            {
                T c = Queue[Queue.Count - 1];
                Queue.RemoveAt(Queue.Count - 1);
                frozen.Remove(c);
                // Someone else's temp terrain now sits here (a lava flow, a bridge): not ours to remove.
                if (!isOurs(c)) continue;
                if (meltCell(c))
                {
                    anyLoss = true;
                    lossAt = c;
                }
                melted++;
            }
            // Stale entries (already removed from the frozen set elsewhere) leave the queue empty early; resync from the set.
            if (Queue.Count == 0) Queue = null;
            return melted;
        }
    }
}
