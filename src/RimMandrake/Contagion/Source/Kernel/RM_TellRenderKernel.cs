// Verse-free kernel of the VISIBLE Burn tells (owner Q6, 2026-10-15, by card: "Build the visible Burn tell motion ->
// Build the visible sink and shake"): how far a gawpsack has settled, and how a rattlegrope shakes. The renderers in
// RM_ContagionTellRender.cs call these every frame with the sky clock's state; SelfTest/ContagionFuzz.cs compiles this
// file alone, so it must stay free of Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Contagion
{
    public static class RM_TellRenderKernel
    {
        // 0 = floating as normal, 1 = fully settled. Settles over rampTicks from the first tell, stays down through the
        // Burn, and rises over rampTicks after the Burn ends (lastBurnEndTick, -1 = none seen). Tells off: never moves.
        public static float SinkFraction(bool tellsOn, bool tellsBegun, int now, int nextBurnTick, int tellLeadTicks,
            bool burnActive, int lastBurnEndTick, int rampTicks)
        {
            if (!tellsOn) return 0f;
            if (burnActive) return 1f;
            int ramp = Math.Max(1, rampTicks);
            if (tellsBegun && nextBurnTick > now)
            {
                float elapsed = Math.Max(0, tellLeadTicks) - (nextBurnTick - now);
                return Clamp01(elapsed / ramp);
            }
            if (lastBurnEndTick >= 0 && now >= lastBurnEndTick && now - lastBurnEndTick < ramp)
            {
                return 1f - (now - lastBurnEndTick) / (float)ramp;
            }
            return 0f;
        }

        // A rattlegrope shakes only between the first tell and the Burn (the rattle is the forecast; it stops when the
        // light arrives). Tells off: never.
        public static bool Shaking(bool tellsOn, bool tellsBegun, bool burnActive)
        {
            return tellsOn && tellsBegun && !burnActive;
        }

        // Sideways shake offset in cells: bursts of fast rattling (a third of every 90-tick cycle at full amplitude, the
        // rest at a quarter), phase-shifted per plant by seed so a stand never moves in lockstep. |result| <= amplitude.
        public static float ShakeOffset(int ticks, int seed, float amplitude)
        {
            if (amplitude <= 0f) return 0f;
            int s = seed & 0x7FFF;
            int cyc = ((ticks + s) % 90 + 90) % 90;
            float env = cyc < 30 ? 1f : 0.25f;
            return (float)(amplitude * env * Math.Sin((ticks + s) * 1.7));
        }

        private static float Clamp01(float v) { return v < 0f ? 0f : (v > 1f ? 1f : v); }
    }
}
