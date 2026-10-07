// Abyss pure kernel, part 2: the timers and state machines that used to live inside map components and comps - the gust controller,
// the gharrek's feeding, the storm call, the soundscape's scheduling and the hidden-ship cover with its probe bookkeeping. Each is a
// small struct of exactly the fields the component Scribes, plus a Step function the component calls with its engine reads as
// plain arguments; the component keeps only the side effects (spawn, letter, sound). Randomness comes in as delegates so a fuzz can
// script it. NO `using Verse;` / `using UnityEngine;` here: the fuzz project compiles this file on plain net8.0.
// Part 1 (arithmetic): RM_AbyssKernel.cs.
using System;

namespace RimMandrake.Abyss
{
    /// <summary>RM_MapComponent_GustController: a gust opens when the wind runs 30% over its slow average, closes at 10% over (hysteresis).</summary>
    public struct GustState
    {
        public float average;                 // -1 = never sampled
        public int startTick, endTick, count;

        public static GustState Fresh() { return new GustState { average = -1f, startTick = -99999, endTick = -99999, count = 0 }; }
    }

    public static class RM_GustKernel
    {
        public const int SampleInterval = 10;
        public const float StartRatio = 1.30f;
        public const float EndRatio = 1.10f;
        public const int MinGustTicks = 120;
        public const int MaxGustTicks = 900;
        public const int CooldownTicks = 600;

        public static bool IsGust(in GustState s, int now) { return now < s.endTick; }

        /// <summary>A proof/debug gust: at least MinGustTicks, never shortens one in progress.</summary>
        public static void Force(ref GustState s, int now, int ticks)
        {
            if (!IsGust(s, now))
            {
                s.startTick = now;
                s.count++;
            }
            s.endTick = Math.Max(s.endTick, now + Math.Max(MinGustTicks, ticks));
        }

        /// <summary>One wind sample (the component calls this every SampleInterval ticks).</summary>
        public static void Sample(ref GustState s, int now, float speed)
        {
            if (s.average < 0f) s.average = speed;
            s.average += (speed - s.average) * 0.01f;
            float baseline = Math.Max(0.05f, s.average);

            if (IsGust(s, now))
            {
                bool minDone = now - s.startTick >= MinGustTicks;
                if (now - s.startTick >= MaxGustTicks || (minDone && speed <= baseline * EndRatio))
                    s.endTick = now;
            }
            else if (now - s.endTick >= CooldownTicks && speed >= baseline * StartRatio)
            {
                s.startTick = now;
                s.endTick = now + MaxGustTicks;   // trimmed by the end test above
                s.count++;
            }
        }

        /// <summary>
        /// CompGharrek.CompTick (every 15 ticks): open and awake in a gust (fed once per gust), dormant out of one. With the feeders
        /// setting off the gill is simply open and awake. Returns the nutrition gained this step.
        /// </summary>
        public static float GharrekStep(bool feedersEnabled, bool gust, int gustCount, float nutritionPerGust, ref int lastFedGust, out bool dormant, out bool open)
        {
            if (!feedersEnabled) { dormant = false; open = true; return 0f; }
            float fed = 0f;
            if (gust)
            {
                dormant = false;
                if (gustCount != lastFedGust)
                {
                    lastFedGust = gustCount;
                    fed = nutritionPerGust;
                }
            }
            else dormant = true;
            open = gust;
            return fed;
        }
    }

    // ───────────────────────── the storm call ─────────────────────────

    public struct StormState
    {
        public int nextRumbleTick, pendingFlashTick;
        public bool pendingSumm;

        public static StormState Fresh() { return new StormState { nextRumbleTick = -1, pendingFlashTick = -1, pendingSumm = false }; }
    }

    public struct StormOut
    {
        public bool rumble, flash, summ;
    }

    public static class RM_StormKernel
    {
        public const int RumbleMin = 3000, RumbleMax = 9000;
        public const int FlashDelayMin = 180, FlashDelayMax = 300;
        public const float SummChance = 0.2f;

        /// <summary>
        /// RM_MapComponent_Dark.StormCallTick. A rumble schedules a flash 180..300 ticks later; the flash may bring a summ. Out of a
        /// Witchfire storm (or with the option off) the whole schedule is dropped.
        /// rangeInclusive(a,b) is Rand.RangeInclusive; chance(p) is Rand.Chance.
        /// </summary>
        public static StormOut Step(ref StormState s, int now, bool storm, bool enabled, float darkStrength, Func<int, int, int> rangeInclusive, Func<float, bool> chance)
        {
            var o = new StormOut();
            if (!storm || !enabled) { s = StormState.Fresh(); return o; }
            if (s.nextRumbleTick < 0) s.nextRumbleTick = now + rangeInclusive(RumbleMin, RumbleMax);

            if (s.pendingFlashTick >= 0 && now >= s.pendingFlashTick)
            {
                o.flash = true;
                if (s.pendingSumm) o.summ = true;
                s.pendingFlashTick = -1; s.pendingSumm = false;
            }
            else if (s.pendingFlashTick < 0 && now >= s.nextRumbleTick)
            {
                o.rumble = true;
                s.pendingFlashTick = now + rangeInclusive(FlashDelayMin, FlashDelayMax);
                s.pendingSumm = chance(RM_DarkKernel.Clamp01(SummChance * darkStrength));
                s.nextRumbleTick = now + rangeInclusive(RumbleMin, RumbleMax);
            }
            return o;
        }
    }

    // ───────────────────────── the soundscape scheduler ─────────────────────────

    public struct SoundState
    {
        public int lastGustCount, pendingRustleTick, nextGrainTick;

        public static SoundState Fresh() { return new SoundState { lastGustCount = -1, pendingRustleTick = -1, nextGrainTick = -1 }; }
    }

    public struct SoundOut
    {
        public bool impact, rustle, grain;
    }

    public static class RM_SoundKernel
    {
        public const int RustleDelayMin = 45, RustleDelayMax = 90;
        public const int GrainTickMin = 240, GrainTickMax = 900;

        /// <summary>
        /// RM_MapComponent_AbyssSoundscape.MapComponentTick, as which sounds are DUE (the component plays them only when on screen).
        /// gustCount is -2 when the map has no gust controller. grainMultiplier/etchStrength come from the weather and the settings.
        /// </summary>
        public static SoundOut Step(ref SoundState s, int now, int gustCount, float grainMultiplier, float etchStrength, Func<int, int, int> rangeInclusive)
        {
            var o = new SoundOut();
            if (gustCount != -2)
            {
                if (s.lastGustCount < 0) s.lastGustCount = gustCount;
                if (gustCount != s.lastGustCount)
                {
                    s.lastGustCount = gustCount;
                    o.impact = true;
                    s.pendingRustleTick = now + rangeInclusive(RustleDelayMin, RustleDelayMax);
                }
            }
            if (s.pendingRustleTick >= 0 && now >= s.pendingRustleTick)
            {
                s.pendingRustleTick = -1;
                o.rustle = true;
            }
            if (now % 60 == 0) o.grain = GrainStep(ref s, now, grainMultiplier, etchStrength, rangeInclusive);
            return o;
        }

        private static bool GrainStep(ref SoundState s, int now, float grainMultiplier, float etchStrength, Func<int, int, int> rangeInclusive)
        {
            if (grainMultiplier <= 0f || etchStrength <= 0.001f) { s.nextGrainTick = -1; return false; }
            if (s.nextGrainTick < 0) { s.nextGrainTick = now + rangeInclusive(GrainTickMin, GrainTickMax); return false; }
            if (now < s.nextGrainTick) return false;
            s.nextGrainTick = now + (int)Math.Round(rangeInclusive(GrainTickMin, GrainTickMax) / grainMultiplier);
            return true;
        }
    }

    // ───────────────────────── hidden-ship cover ─────────────────────────

    public struct CoverState
    {
        public float cover;
        public int coveredTicks, cooldownUntil, nextProbeTick;

        public static CoverState Fresh() { return new CoverState { cover = 0f, coveredTicks = 0, cooldownUntil = -1, nextProbeTick = -1 }; }
    }

    public enum CoverEvent
    {
        None,
        Lapsed,         // MaxCoveredTicks of cover: it wears thin, cooldown starts
        SpawnProbe      // time for a probe (the component tries; it may find no kind or no edge cell)
    }

    public static class RM_CoverKernel
    {
        public const int TicksPerDay = 60000;          // GenDate.TicksPerDay
        public const int Interval = 250;
        public const float DaysToFullCover = 6f;
        public const int MaxCoveredTicks = 15 * TicksPerDay;
        public const int CooldownTicks = 3 * TicksPerDay;
        public const float CoveredThreshold = 0.6f;
        public const int FreeLamps = 4;
        public const int ProbeMin = 3 * TicksPerDay, ProbeMax = 6 * TicksPerDay;
        public const int ProbeStay = TicksPerDay;
        public const int ScanInterval = 60;
        public const int ReportTicks = 600;

        /// <summary>Gain per Interval of quiet; loss is twice that per Interval of noise (more than FreeLamps lit lamps).</summary>
        public const float Rate = Interval / (DaysToFullCover * TicksPerDay);

        public static bool IsCovered(bool enabled, float cover) { return enabled && cover >= CoveredThreshold; }

        public static void Collapse(ref CoverState s, bool cooldown, int now)
        {
            s.cover = 0f;
            s.coveredTicks = 0;
            s.nextProbeTick = -1;
            if (cooldown) s.cooldownUntil = now + CooldownTicks;
        }

        /// <summary>
        /// MapComponentTick's every-Interval half. applies = enabled, player home, Abyss; probeAlive = a probe is out right now.
        /// rangeExclusive(a,b) is Rand.Range(int,int).
        /// </summary>
        public static CoverEvent Step(ref CoverState s, int now, bool applies, bool hasEngine, int litLamps, bool probesEnabled, bool probeAlive, Func<int, int, int> rangeExclusive)
        {
            if (!applies || !hasEngine)
            {
                Collapse(ref s, false, now);
                return CoverEvent.None;
            }
            if (s.cooldownUntil > now) return CoverEvent.None;

            bool quiet = litLamps <= FreeLamps;
            if (s.cover < 1f && quiet)
                s.cover = Math.Min(1f, s.cover + Rate);
            else if (!quiet)
                s.cover = Math.Max(0f, s.cover - Rate * 2f);

            if (s.cover >= CoveredThreshold)
            {
                s.coveredTicks += Interval;
                if (s.coveredTicks >= MaxCoveredTicks)
                {
                    Collapse(ref s, true, now);
                    return CoverEvent.Lapsed;
                }
                if (probesEnabled)
                {
                    if (s.nextProbeTick < 0) s.nextProbeTick = now + rangeExclusive(ProbeMin, ProbeMax);
                    if (now >= s.nextProbeTick && !probeAlive)
                    {
                        s.nextProbeTick = now + rangeExclusive(ProbeMin, ProbeMax);
                        return CoverEvent.SpawnProbe;
                    }
                }
            }
            else
            {
                s.coveredTicks = 0;
                s.nextProbeTick = -1;
            }
            return CoverEvent.None;
        }

        /// <summary>The probe's scan (every ScanInterval): the seen counter climbs while it sees movement or a lit lamp, and drains otherwise.</summary>
        public static int ProbeSeen(int seenTicks, bool seen)
        {
            return seen ? seenTicks + ScanInterval : Math.Max(0, seenTicks - ScanInterval);
        }

        public static bool ProbeReports(int seenTicks) { return seenTicks >= ReportTicks; }

        public static bool ProbeLeaves(int now, int spawnTick) { return now - spawnTick > ProbeStay; }
    }
}
