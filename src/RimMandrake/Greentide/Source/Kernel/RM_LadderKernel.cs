// Verse-free kernel of the greatbole harvest ladder (RM_CompGreatboleHarvestLadder.cs): the three thresholds on the removed
// fraction, with hysteresis. SelfTest/GreentideFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Greentide
{
    public static class RM_LadderKernel
    {
        public sealed class State
        {
            public bool ShakingArmed, HealingAnnounced, CatastropheDone;
        }

        [Flags]
        public enum Events { None = 0, Shaking = 1, Healing = 2, Catastrophe = 4 }

        // One poll. The shaking and the healing announcement fire on the way up through their threshold and re-arm only after the
        // fraction falls below the threshold minus the dead-zone; the catastrophe fires once, ever, when enabled.
        public static Events Poll(State s, float fraction, float shakeThr, float healThr, float catThr, bool catEnabled, float hysteresis)
        {
            Events e = Events.None;
            if (s.CatastropheDone) return e;
            if (!s.ShakingArmed && fraction >= shakeThr) { s.ShakingArmed = true; e |= Events.Shaking; }
            else if (s.ShakingArmed && fraction < shakeThr - hysteresis) s.ShakingArmed = false;
            if (!s.HealingAnnounced && fraction >= healThr) { s.HealingAnnounced = true; e |= Events.Healing; }
            else if (s.HealingAnnounced && fraction < healThr - hysteresis) s.HealingAnnounced = false;
            if (catEnabled && fraction >= catThr) { s.CatastropheDone = true; e |= Events.Catastrophe; }
            return e;
        }
    }
}
