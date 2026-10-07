// Verse-free kernel of the Wasteland storm layer (RM_MapComponent_WastelandStorms) and the named-storm phase machine
// (RM_MapComponent_StormPhases in RM_NamedStorms.cs): the fresh-fall memory, the per-batch fall count, the germination
// draw count, and the warning -> unleashed hand-off that holds the dose. Called by the mod with the same expressions;
// SelfTest/WastelandFuzz.cs compiles this file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;
using System.Collections.Generic;

namespace RimMandrake.Wasteland
{
    [Flags]
    public enum PhaseEvent { None = 0, Ended = 1, Began = 2, Unleash = 4, Warn = 8, Storm = 16, Disabled = 32 }

    public struct PhaseState
    {
        public int weather;      // -1 = no phase
        public int startTick;    // -1 = none
        public bool unleashed;
        public static PhaseState Idle { get { return new PhaseState { weather = -1, startTick = -1, unleashed = false }; } }
    }

    public static class RM_StormKernel
    {
        public const int MaxFreshFall = 4000;

        // ---- fresh fall memory ---------------------------------------------------------------
        // Below the cap: append. At the cap: overwrite a random remembered cell (randBelow(n) in [0,n)).
        public static void RememberFall<T>(List<T> freshFall, T cell, Func<int, int> randBelow)
        {
            if (freshFall.Count < MaxFreshFall) freshFall.Add(cell);
            else freshFall[randBelow(freshFall.Count)] = cell;
        }

        public static float FallPerBatch(float fallCellsPerDay, int fallIntervalTicks, int ticksPerDay, int numGridCells, float referenceMapCells)
        {
            return fallCellsPerDay * fallIntervalTicks / (float)ticksPerDay * (numGridCells / referenceMapCells);
        }

        // Fall does anything only if it pollutes or remembers; zero rate does nothing.
        public static bool FallActive(float fallCellsPerDay, bool pollute, bool remember)
        {
            return fallCellsPerDay > 0f && (pollute || remember);
        }

        public static bool Pollutes(bool ashFallPollutionEnabled, bool biotechActive) { return ashFallPollutionEnabled && biotechActive; }
        public static bool Remembers(bool germinationEnabled, bool hasAftermathPlant) { return germinationEnabled && hasAftermathPlant; }

        // Germination draws: round-random of count*fraction (the caller supplies the engine's RoundRandom).
        public static int GerminationDraws(int freshCount, float fraction, Func<float, int> roundRandom)
        {
            return freshCount == 0 ? 0 : roundRandom(freshCount * fraction);
        }

        // ---- storm dose ---------------------------------------------------------------------
        public static bool DoseActive(bool stormDoseEnabled, float airborneToxicFactor) { return stormDoseEnabled && airborneToxicFactor > 0f; }
        public static float DoseFactor(float airborneToxicFactor, float multiplier) { return airborneToxicFactor * multiplier; }

        // The storm layer runs the dose / fall of the current weather unless a named storm's warning holds it.
        public static bool LayerRuns(bool optedIn, bool wastelandOn, bool hasDoseExt, bool holding)
        {
            return wastelandOn && optedIn && hasDoseExt && !holding;
        }

        // ---- the phase machine ------------------------------------------------------------------
        public static bool IsHolding(bool enabled, bool hasWeather, PhaseState s, int weather)
        {
            return enabled && hasWeather && weather == s.weather && !s.unleashed;
        }

        public static int WarningTicks(int extWarningTicks, float factor) { return RoundToInt(extWarningTicks * factor); }
        private static int RoundToInt(float f) { return (int)Math.Round(f); }

        // Start a storm's warning (or, for a weather with no phase script, end any phase).
        public static PhaseEvent Begin(ref PhaseState s, int weather, bool hasExt, bool enabled, int warnTicks, int now)
        {
            if (!hasExt) { return End(ref s); }
            s.weather = weather;
            s.startTick = now;
            s.unleashed = !enabled || warnTicks <= 0;
            PhaseEvent e = PhaseEvent.Began;
            if (s.unleashed) e |= PhaseEvent.Unleash;
            return e;
        }

        public static PhaseEvent End(ref PhaseState s)
        {
            s = PhaseState.Idle;
            return PhaseEvent.Ended;
        }

        // One MapComponentTick. cur = current weather id (-1 none), curHasExt = it carries the phase script.
        public static PhaseEvent Tick(ref PhaseState s, int cur, bool curHasExt, bool enabled, int warnTicks, int now, out float progress)
        {
            progress = 0f;
            PhaseEvent e = PhaseEvent.None;
            if (!curHasExt)
            {
                if (s.weather != -1) e = End(ref s);
                return e;
            }
            if (cur != s.weather) e |= Begin(ref s, cur, true, enabled, warnTicks, now);
            if (!enabled) return e | PhaseEvent.Disabled;
            if (!s.unleashed)
            {
                if (now - s.startTick >= warnTicks)
                {
                    s.unleashed = true;
                    e |= PhaseEvent.Unleash;
                }
                else
                {
                    e |= PhaseEvent.Warn;
                    progress = (now - s.startTick) / (float)Math.Max(1, warnTicks);
                }
            }
            if (s.unleashed) e |= PhaseEvent.Storm;
            return e;
        }

        // Click interval shrinks start -> end over the warning.
        public static int ClickInterval(int startTicks, int endTicks, float progress)
        {
            float t = progress < 0f ? 0f : (progress > 1f ? 1f : progress);
            return RoundToInt(startTicks + (endTicks - startTicks) * t);
        }

        // First EMP / strike / flash lands a third of an interval after the hand-off.
        public static int HandoffDelay(int intervalTicks) { return intervalTicks / 3; }
    }
}
