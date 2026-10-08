// Verse-free kernel of the sleeper pan (RM_CompPanSleeper.cs): when a pan animal digs in, stays sealed and wakes. SelfTest/
// FloodedCanyonFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.FloodedCanyon
{
    public sealed class PanState
    {
        public bool InitialSealDone, SealedAsleep;
        public int DryAccumTicks;
    }

    public static class RM_PanKernel
    {
        public enum Do { Nothing, Seal, Wake, ToSleep }

        // One check. Returns what to do to the dormancy comp; the state is already updated for it (a Seal also clears the dry clock).
        public static Do Check(PanState s, bool noComp, bool dead, bool startsDormant, bool wokeUpBefore, bool awake, bool canSeal, bool waterNear,
                               bool wakeSetting, bool digInSetting, bool flooding, int checkIntervalTicks, float dryHoursToDigIn)
        {
            if (noComp || dead) return Do.Nothing;
            if (!s.InitialSealDone)
            {
                s.InitialSealDone = true;
                if (startsDormant && !wokeUpBefore && canSeal) { s.SealedAsleep = true; s.DryAccumTicks = 0; return Do.Seal; }
            }
            if (s.SealedAsleep)
            {
                if (wokeUpBefore) { s.SealedAsleep = false; s.DryAccumTicks = 0; return Do.Nothing; }
                if (waterNear && wakeSetting) { s.SealedAsleep = false; s.DryAccumTicks = 0; return Do.Wake; }
                if (awake && canSeal) return Do.ToSleep;
                return Do.Nothing;
            }
            if (!digInSetting || !awake) return Do.Nothing;
            if (waterNear || flooding) { s.DryAccumTicks = 0; return Do.Nothing; }
            s.DryAccumTicks += checkIntervalTicks;
            if (s.DryAccumTicks >= dryHoursToDigIn * 2500f && canSeal) { s.SealedAsleep = true; s.DryAccumTicks = 0; return Do.Seal; }
            return Do.Nothing;
        }
    }
}
