// Verse-free kernel of the cycle-keeping creatures and the dhuvvox run clock (RM_CompForgeCycleDormancy, FORGE_CYCLE_MECHANICS_1
// + FORGE_GPT_ENRICHMENT_1 s7): when a pawn wakes or seals, the slowing window, the scuttle gap, which end tick the run counts
// down to, and the four phase voices' triggers. The comp / RM_ForgeVoices call these with the same expressions;
// SelfTest/TheForgeFuzz.cs compiles this file alone (no Verse/RimWorld/UnityEngine).
using System;

namespace RimMandrake.TheForge
{
    public enum DormancyAction { None = 0, WakeUp = 1, ToSleep = 2 }
    public enum SustainerKind { None = 0, StillThrob = 1, RainHiss = 2 }

    public struct DormancyState
    {
        public int awakeSinceTick;
        public bool initialCheckDone;
    }

    public struct DormancyResult
    {
        public DormancyAction action;
        public bool wokeByCycle;     // the wake was for a wanted wake (effects, sound), not only a refusal to stay sealed
        public bool curlBack;        // sealed after a settled run, not the first check
        public bool slowingUpdate;   // the awake branch ran (the slow hediff is reconciled)
    }

    public static class RM_DormancyKernel
    {
        public const float TicksPerHour = 2500f;

        public static bool ShouldBeAwake(bool hasMap, bool awakeDuringRain, bool raining, bool awakeDuringFlashWindow, bool flashWindowOpen)
        {
            if (!hasMap) return true;
            return (awakeDuringRain && raining) || (awakeDuringFlashWindow && flashWindowOpen);
        }

        public static bool WantAwake(bool dormancyEnabled, bool shouldBeAwake) { return !dormancyEnabled || shouldBeAwake; }

        public static bool CanSeal(bool noFaction, bool downed, bool inMentalState, bool drafted, bool hasEnemyTarget)
        {
            return noFaction && !downed && !inMentalState && !drafted && !hasEnemyTarget;
        }

        // One periodic check. dormantAwake is the stock comp's Awake flag.
        public static DormancyResult Check(ref DormancyState s, bool dormantAwake, bool wantAwake, bool canSeal, int now, float minAwakeHours)
        {
            DormancyResult r = new DormancyResult();
            if (!dormantAwake)
            {
                if (wantAwake || !canSeal)
                {
                    r.action = DormancyAction.WakeUp;
                    r.wokeByCycle = wantAwake;
                    s.awakeSinceTick = now;
                }
                return r;
            }
            // First check on a fresh pawn: the initial seal is issued here, with no minimum-awake wait. A pawn woken by something
            // else is stamped now and gets the full minimum awake time.
            bool firstCheck = !s.initialCheckDone;
            s.initialCheckDone = true;
            if (s.awakeSinceTick < 0) s.awakeSinceTick = now;
            r.slowingUpdate = true;
            if (wantAwake || !canSeal) return r;
            if (!firstCheck && now - s.awakeSinceTick < minAwakeHours * TicksPerHour) return r;
            r.action = DormancyAction.ToSleep;
            r.curlBack = !firstCheck;
            s.awakeSinceTick = -1;
            return r;
        }

        // The tick the run ends: the flash window's end while it is open, else the rain phase's end while it falls, else -1.
        public static int RunEnd(bool hasMap, bool awakeDuringFlashWindow, bool flashWindowOpen, int flashEnd, bool awakeDuringRain,
            bool cycleActiveAndRaining, int phaseEnd)
        {
            if (!hasMap) return -1;
            if (awakeDuringFlashWindow && flashWindowOpen) return flashEnd;
            if (awakeDuringRain && cycleActiveAndRaining) return phaseEnd;
            return -1;
        }

        public static bool SlowWanted(bool clockOn, bool wantAwake, int end, int now, float slowFinalHours)
        {
            if (!clockOn || !wantAwake) return false;
            int left = end - now;
            return end > 0 && left > 0 && left <= slowFinalHours * TicksPerHour;
        }

        // Scuttle gap: the interval, stretched up to slowFactor across the slowing window; jitter in [0.7, 1.3].
        public static int ScuttleDelay(int intervalTicks, int end, int now, float slowFinalHours, float slowFactor, float jitter)
        {
            int gap = Math.Max(10, intervalTicks);
            int left = end - now;
            float window = slowFinalHours * TicksPerHour;
            float f = 1f;
            if (end > 0 && left > 0 && left <= window)
            {
                float t = left / window;
                t = t < 0f ? 0f : t > 1f ? 1f : t;
                f = slowFactor + (1f - slowFactor) * t;
            }
            return (int)Math.Round(gap * f * jitter);
        }

        // ---- the four voices ---------------------------------------------------------------------------
        public const int CoughIntervalTicks = 240;
        public const int BasaltTickIntervalTicks = 90;
        public const int CrackPulseIntervalTicks = 360;

        public static SustainerKind SustainerFor(ForgeCyclePhase phase)
        {
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat:
                case ForgeCyclePhase.GasWash:
                    return SustainerKind.StillThrob;
                case ForgeCyclePhase.Rain:
                    return SustainerKind.RainHiss;
            }
            return SustainerKind.None;
        }

        [Flags]
        public enum VoiceEvent { None = 0, Stinger = 1, Cough = 2, BasaltTick = 4, CrackPulse = 8 }

        // One voice frame. lastPhase is (-1) before the first frame. Inactive frames only track the phase silently, so returning
        // to the map does not play a stinger for a change that happened while away.
        public static VoiceEvent Frame(ref int lastPhase, bool active, ForgeCyclePhase phase, bool hissSent, int now)
        {
            if (!active)
            {
                lastPhase = (int)phase;
                return VoiceEvent.None;
            }
            VoiceEvent e = VoiceEvent.None;
            if ((int)phase != lastPhase)
            {
                bool first = lastPhase < 0;
                lastPhase = (int)phase;
                if (!first) e |= VoiceEvent.Stinger;
            }
            switch (phase)
            {
                case ForgeCyclePhase.StillHeat:
                    if (hissSent && now % CoughIntervalTicks == 0) e |= VoiceEvent.Cough;
                    break;
                case ForgeCyclePhase.GasWash:
                    if (now % CoughIntervalTicks == 0) e |= VoiceEvent.Cough;
                    break;
                case ForgeCyclePhase.Freeze:
                case ForgeCyclePhase.Growth:
                    if (now % BasaltTickIntervalTicks == 0) e |= VoiceEvent.BasaltTick;
                    break;
                case ForgeCyclePhase.Cracks:
                case ForgeCyclePhase.Melt:
                    if (now % CrackPulseIntervalTicks == 0) e |= VoiceEvent.CrackPulse;
                    break;
            }
            return e;
        }
    }
}
