// Verse-free kernel of the Contagion sky: the Burn clock and its tells (RM_MapComponent_ContagionSky), the Burn's pressure
// classification and dive choice (RM_GameCondition_ContagionBurn), the Cloud Repulsor's warm-up (CompCloudRepulsor) and the
// Coalescence's formation gate. The comps call these with the same expressions; SelfTest/ContagionFuzz.cs compiles this file
// alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Contagion
{
    public struct SkyState
    {
        public int nextBurnTick;   // -1 = not scheduled
        public bool tellsBegun;
        public int bloomSinceTick; // -1 = no bloom clock
        public static SkyState Fresh { get { return new SkyState { nextBurnTick = -1, tellsBegun = false, bloomSinceTick = -1 }; } }
    }

    [Flags]
    public enum SkyAct { None = 0, TryCoalescence = 1, Scheduled = 2, Tell = 4, TellFirst = 8, StartBurn = 16, Reset = 32, BurnHeld = 64 }

    public enum BurnEffect { None = 0, Damage = 1, DamageAndDive = 2, Dose = 3 }

    public enum RepulsorStep { Reset = 0, Warming = 1, Holding = 2 }

    public static class RM_SkyKernel
    {
        public const int Interval = 250;

        // ---- the Burn clock -----------------------------------------------------------------------
        // The gap to the next Burn: mean/freq * roll(0.5..1.5) days, never shorter than the lead plus one poll.
        public static int RollGap(float meanDays, float frequency, float roll, int tellLeadTicks, int interval, int ticksPerDay)
        {
            float freq = Math.Max(0.05f, frequency);
            float days = meanDays / freq * roll;
            return Math.Max(tellLeadTicks + interval, (int)(days * ticksPerDay));
        }

        public static bool InTellWindow(int now, int nextBurnTick, int tellLeadTicks)
        {
            int lead = Math.Max(0, tellLeadTicks);
            return now >= nextBurnTick - lead && now < nextBurnTick;
        }

        // One poll (the caller has already gated on now % interval == 0). rollGap() is only called when a gap is needed.
        public static SkyAct Tick(ref SkyState s, int now, bool hasExt, bool burnActive, bool burnEnabled, bool tellsEnabled,
                                   int tellLeadTicks, Func<int> rollGap, out int ticksToBurn)
        {
            ticksToBurn = 0;
            if (!hasExt)
            {
                s = SkyState.Fresh;
                return SkyAct.Reset;
            }
            if (burnActive)
            {
                s = SkyState.Fresh;
                return SkyAct.BurnHeld;
            }
            SkyAct a = SkyAct.TryCoalescence;
            if (s.bloomSinceTick < 0) s.bloomSinceTick = now;
            if (!burnEnabled)
            {
                s.nextBurnTick = -1;
                s.tellsBegun = false;
                return a;
            }
            if (s.nextBurnTick < 0)
            {
                s.nextBurnTick = now + rollGap();
                s.tellsBegun = false;
                return a | SkyAct.Scheduled;
            }
            if (InTellWindow(now, s.nextBurnTick, tellLeadTicks))
            {
                ticksToBurn = s.nextBurnTick - now;
                if (tellsEnabled) a |= SkyAct.Tell | (!s.tellsBegun ? SkyAct.TellFirst : SkyAct.None);
                s.tellsBegun = true;
                return a;
            }
            if (now >= s.nextBurnTick)
            {
                a |= SkyAct.StartBurn;
                s.nextBurnTick = -1;
                s.tellsBegun = false;
            }
            return a;
        }

        // A Burn already running is stretched so at least minTicks remain; a longer one is left alone.
        public static int StretchBurn(int ticksLeft, int minTicks) { return ticksLeft < minTicks ? minTicks : ticksLeft; }

        // ---- the Coalescence's formation gate -----------------------------------------------------
        // Needs Burns to be on: the Coalescence is killed by the next Burn, and its letter promises that counterplay.
        public static bool CoalescenceGate(bool enabled, bool burnEnabled, bool hasDef, int now, int bloomSinceTick, int longBloomTicks, bool oneAlready)
        {
            if (!enabled || !burnEnabled || !hasDef) return false;
            if (now - bloomSinceTick < longBloomTicks) return false;
            return !oneAlready;
        }

        // ---- the Burn's pressure -------------------------------------------------------------------
        // Out under the open sky: unroofed, not water, not under a tree.
        public static bool Exposed(bool inBounds, bool roofed, bool water, bool tree)
        {
            if (!inBounds) return false;
            if (roofed) return false;
            if (water) return false;
            return !tree;
        }

        // What the Burn does to one pawn standing exposed. A native is hurt unless armoured, and dives unless a leaker;
        // a non-native living thing (not a mechanoid, with a health tracker) takes the dose.
        public static BurnEffect Classify(bool isNative, bool armored, bool leaker, bool nonMechanoidWithHealth)
        {
            if (isNative)
            {
                if (armored) return BurnEffect.None;
                return leaker ? BurnEffect.Damage : BurnEffect.DamageAndDive;
            }
            return nonMechanoidWithHealth ? BurnEffect.Dose : BurnEffect.None;
        }

        public static bool PressureActive(bool hasExt, bool burnEnabled, bool weatherArrived, float damageFactor)
        {
            return hasExt && burnEnabled && weatherArrived && damageFactor > 0f;
        }

        // A dive is skipped for the downed, drafted, mentally broken, or one already running for shelter.
        public static bool MayDive(bool downed, bool drafted, bool inMentalState, bool hasJobs, bool alreadyRunningForShelter)
        {
            if (downed || drafted || inMentalState || !hasJobs) return false;
            return !alreadyRunningForShelter;
        }

        // Of the sheltered, standable cells in radial order, only the first four are tried; the first reachable wins.
        // Returns the index into `sheltered` or -1. reachable(i) is only asked of the tried ones.
        public static int PickDive(int shelteredCount, Func<int, bool> reachable)
        {
            int tried = 0;
            for (int i = 0; i < shelteredCount; i++)
            {
                if (++tried > 4) return -1;
                if (reachable(i)) return i;
            }
            return -1;
        }

        // ---- the Cloud Repulsor --------------------------------------------------------------------
        // One poll: off or unpowered resets the warm-up; warming accrues; warm holds (and the caller re-asserts the effect).
        public static RepulsorStep RepulsorTick(ref int warmTicks, bool enabled, bool powered, int interval, int warmupTicks)
        {
            if (!enabled || !powered) { warmTicks = 0; return RepulsorStep.Reset; }
            if (warmTicks < warmupTicks) { warmTicks += interval; return RepulsorStep.Warming; }
            return RepulsorStep.Holding;
        }
    }
}
