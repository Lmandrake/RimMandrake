// Verse-free kernel of the acoustic scanner: the banding of a pulse's hits into coarse probability blocks, the pulse gate
// (CanPulse's decision table), the cooldown arithmetic, the landed-ship test and the overlay lifetime. The sounder building,
// the overlay map component and RM_AcousticBanding call these with the same expressions; SelfTest/AcousticScannerFuzz.cs
// compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;` here breaks the
// self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.AcousticScanner
{
    public enum RM_AcousticTier : byte { Faint = 0, Moderate = 1, Strong = 2 }

    /// <summary>One square probability band of a pulse: a whole block of the coarse grid, as a rectangle inside the map.</summary>
    public struct RM_KBand
    {
        public int targetIndex;
        public RM_AcousticTier tier;
        public int x, z, w, h;
    }

    public struct RM_KCell
    {
        public int x, z;
        public RM_KCell(int x, int z) { this.x = x; this.z = z; }
    }

    /// <summary>Why a pulse is or is not allowed, in the order CanPulse checks them.</summary>
    public enum RM_PulseGate { Ready, Disabled, NotSpawned, NoPower, NotOnShip, Cooldown }

    public static class RM_AcousticKernel
    {
        /// <summary>Hard floor: a reading is ALWAYS banded, never exact (GRAVSHIP_ACOUSTIC_SCANNER_1).</summary>
        public const int MinBandSize = 7;
        public const int MaxBandSize = 25;
        public const int TicksPerHour = 2500;

        /// <summary>Strong when a block holds this share of the pulse's strongest block (PROVISIONAL tuning).</summary>
        public const float StrongShare = 0.6f;
        /// <summary>Moderate from this share (PROVISIONAL tuning).</summary>
        public const float ModerateShare = 0.25f;

        /// <summary>The block side a pulse really uses: whatever the settings file says, never under the floor.</summary>
        public static int EffectiveBand(int bandSize) { return Math.Max(bandSize, MinBandSize); }

        /// <summary>The settings slider's clamp.</summary>
        public static int ClampBandSetting(int bandSize) { return Math.Min(Math.Max(bandSize, MinBandSize), MaxBandSize); }

        private static int FloorDiv(int a, int b) { return a >= 0 ? a / b : -((-a + b - 1) / b); }

        public static RM_AcousticTier TierFor(float share) { return share >= StrongShare ? RM_AcousticTier.Strong : share >= ModerateShare ? RM_AcousticTier.Moderate : RM_AcousticTier.Faint; }

        /// <summary>
        /// Bands for one pulse. hitsPerTarget[t] are the heard cells of target t; weightPerTarget[t] their per-hit weight (missing = 1).
        /// ox / oz are the pulse's re-rolled grid origin in [0, EffectiveBand). A heard block, and every neighbour of it, becomes a
        /// band; a block that touches the map edge slides inward so every band keeps the full block size (a clipped band could be
        /// one cell wide, which reads as an exact hit). The band always contains the cells of its block that lie in the map.
        /// </summary>
        public static List<RM_KBand> Build(int mapW, int mapH, List<List<RM_KCell>> hitsPerTarget, List<float> weightPerTarget, int bandSize, int ox, int oz)
        {
            var result = new List<RM_KBand>();
            int b = EffectiveBand(bandSize);
            for (int t = 0; t < hitsPerTarget.Count; t++)
            {
                List<RM_KCell> hits = hitsPerTarget[t];
                if (hits == null || hits.Count == 0) continue;
                float w = t < weightPerTarget.Count ? weightPerTarget[t] : 1f;

                var blocks = new Dictionary<long, float>();
                for (int i = 0; i < hits.Count; i++)
                {
                    long key = Key(FloorDiv(hits[i].x + ox, b), FloorDiv(hits[i].z + oz, b));
                    float cur;
                    blocks.TryGetValue(key, out cur);
                    blocks[key] = cur + w;
                }

                float max = 0f;
                foreach (float v in blocks.Values) if (v > max) max = v;
                if (max <= 0f) continue;

                var tiers = new Dictionary<long, RM_AcousticTier>();
                foreach (KeyValuePair<long, float> kv in blocks)
                {
                    RM_AcousticTier tier = TierFor(kv.Value / max);
                    // A single-block reading with only one hit is never better than moderate.
                    if (blocks.Count == 1 && hits.Count == 1) tier = RM_AcousticTier.Moderate;
                    tiers[kv.Key] = tier;
                }
                // Halo: neighbours of any heard block read at least faint.
                foreach (long k in new List<long>(blocks.Keys))
                {
                    int kx = KeyX(k), kz = KeyZ(k);
                    for (int dx = -1; dx <= 1; dx++)
                        for (int dz = -1; dz <= 1; dz++)
                        {
                            long nk = Key(kx + dx, kz + dz);
                            if (!tiers.ContainsKey(nk)) tiers[nk] = RM_AcousticTier.Faint;
                        }
                }

                foreach (KeyValuePair<long, RM_AcousticTier> kv in tiers)
                {
                    int minX = KeyX(kv.Key) * b - ox;
                    int minZ = KeyZ(kv.Key) * b - oz;
                    // a block wholly outside the map has no band
                    if (minX + b <= 0 || minZ + b <= 0 || minX >= mapW || minZ >= mapH) continue;
                    int bw = Math.Min(b, mapW), bh = Math.Min(b, mapH);
                    int x0 = Math.Min(Math.Max(minX, 0), mapW - bw);
                    int z0 = Math.Min(Math.Max(minZ, 0), mapH - bh);
                    result.Add(new RM_KBand { targetIndex = t, tier = kv.Value, x = x0, z = z0, w = bw, h = bh });
                }
            }
            return result;
        }

        private static long Key(int x, int z) { return ((long)x << 32) | (uint)z; }
        private static int KeyX(long k) { return (int)(k >> 32); }
        private static int KeyZ(long k) { return (int)(uint)(k & 0xFFFFFFFFL); }

        /// <summary>The strongest tier among the bands of one target, Faint when it has none (the letter's per-target line).</summary>
        public static RM_AcousticTier BestTier(List<RM_KBand> bands, int targetIndex)
        {
            RM_AcousticTier best = RM_AcousticTier.Faint;
            for (int i = 0; i < bands.Count; i++)
                if (bands[i].targetIndex == targetIndex && bands[i].tier > best) best = bands[i].tier;
            return best;
        }

        public static int CooldownTicks(float cooldownHours) { return (int)Math.Round(cooldownHours * TicksPerHour); }

        public static int OverlayTicks(float overlayHours) { return (int)Math.Round(overlayHours * TicksPerHour); }

        /// <summary>Ticks left before the next pulse (positive = still cooling down).</summary>
        public static int TicksUntilReady(int lastPulseTick, int cooldownTicks, int now) { return lastPulseTick + cooldownTicks - now; }

        /// <summary>CanPulse's decision table, in its order: master switch, spawned, power (only when the building has a power comp), landed ship (only when required), cooldown.</summary>
        public static RM_PulseGate Gate(bool enabled, bool spawned, bool hasPowerComp, bool powerOn, bool requireLandedShip, bool onLandedShip, int ticksUntilReady)
        {
            if (!enabled) return RM_PulseGate.Disabled;
            if (!spawned) return RM_PulseGate.NotSpawned;
            if (hasPowerComp && !powerOn) return RM_PulseGate.NoPower;
            if (requireLandedShip && !onLandedShip) return RM_PulseGate.NotOnShip;
            if (ticksUntilReady > 0) return RM_PulseGate.Cooldown;
            return RM_PulseGate.Ready;
        }

        /// <summary>Landed means a grav engine stands on the map and every cell the sounder covers is still substructure.</summary>
        public static bool OnLandedShip(int gravEnginesOnMap, IList<bool> coveredCellIsSubstructure)
        {
            if (gravEnginesOnMap <= 0) return false;
            for (int i = 0; i < coveredCellIsSubstructure.Count; i++)
                if (!coveredCellIsSubstructure[i]) return false;
            return true;
        }

        /// <summary>The tick an overlay drawn at <paramref name="now"/> for <paramref name="durationTicks"/> runs out (at least one tick).</summary>
        public static int OverlayExpiry(int now, int durationTicks) { return now + Math.Max(1, durationTicks); }

        /// <summary>The overlay draws while it holds bands and has not run out.</summary>
        public static bool OverlayActive(int expiresTick, int now, int bandCount) { return expiresTick > 0 && now < expiresTick && bandCount > 0; }
    }
}
