// Verse-free kernel of the Vurrak, the false bank (RM_CompBankAmbusher.cs): who sets it off, and its per-check decisions.
// SelfTest/GreentideFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Greentide
{
    public static class RM_VurrakKernel
    {
        public enum Contact { Quiet, Revealed, Struck }
        public enum Gate { Unhide, CheckContact, Rest }

        // The pawns sharing the vurrak's cell: skipped when it is itself, dead, its own kind or flying (excluded[i]). The first one of
        // body size >= threshold strikes it off (index in `who`); otherwise the first light one only reveals it.
        public static Contact Verdict(int n, float[] bodySize, bool[] excluded, float threshold, out int who)
        {
            who = -1;
            int light = -1;
            for (int i = 0; i < n; i++)
            {
                if (excluded[i]) continue;
                if (bodySize[i] >= threshold) { who = i; return Contact.Struck; }
                if (light < 0) light = i;
            }
            who = light;
            return light >= 0 ? Contact.Revealed : Contact.Quiet;
        }

        // The check every few ticks. Switched off, tamed, dead, downed, in a mental break or without a job tracker: give the bank
        // up. Lying flat: it stays down only while it waits on bank ground, then watches the cell. Otherwise it goes about its day.
        public static Gate Decide(bool featureOn, bool wild, bool dead, bool downed, bool inMentalState, bool noJobs, bool disguised, bool waiting, bool onBank)
        {
            if (!featureOn || !wild || dead || downed || inMentalState || noJobs) return Gate.Unhide;
            if (disguised) return (!waiting || !onBank) ? Gate.Unhide : Gate.CheckContact;
            return Gate.Rest;
        }

        // Not disguised, not eating: after a reveal it stays visible for revealHoldTicks, then lies down again when idle.
        public static bool LiesDown(int now, int revealedUntil, bool idle) { return !(now < revealedUntil) && idle; }

        public static int RevealUntil(int now, int holdTicks) { return now + holdTicks; }

        // The first reveal anyone of ours sees pauses the game once: returns whether to record it as seen and whether to pause.
        public static bool FirstReveal(bool alreadySeen, int colonistsOnMap, bool pauseSetting, out bool markSeen)
        {
            markSeen = false;
            if (alreadySeen || colonistsOnMap == 0) return false;
            markSeen = true;
            return pauseSetting;
        }
    }
}
