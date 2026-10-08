// Verse-free kernel of the churnmud mire (RM_MapComponent_TerrainMire.cs): one pawn's RM_Mired severity per 60-tick check.
// SelfTest/GreentideFuzz.cs compiles this file alone: no Verse/RimWorld/UnityEngine.
using System;

namespace RimMandrake.Greentide
{
    public static class RM_MireKernel
    {
        public const int CheckIntervalTicks = 60;

        public enum Outcome { Nothing, Add, Remove }

        // One check. onMire = standing on a mire terrain and not immune. hasHediff / severity describe the pawn's RM_Mired.
        // On mire: gain (rate * multiplier) per check, except that a pawn under stuckThreshold shakes off half a step with
        // selfStruggle chance, and a stuck pawn a full step with a tenth of that chance. Off mire: decay per check, removed at 0.
        // `chance(p)` is Rand.Chance. newSeverity is meaningful for Nothing/Add; Remove means the hediff goes.
        public static Outcome Step(bool onMire, bool hasHediff, float severity, float perTick, float multiplier, float struggle, float stuckThreshold,
                                   float decayOnExt, bool hasExt, Func<float, bool> chance, out float newSeverity)
        {
            newSeverity = severity;
            if (onMire)
            {
                Outcome o = hasHediff ? Outcome.Nothing : Outcome.Add;
                float rate = perTick * multiplier;
                bool stuck = severity >= stuckThreshold;
                if (stuck && chance(struggle * 0.1f)) newSeverity = Math.Max(0f, severity - rate);
                else if (!stuck && chance(struggle)) newSeverity = Math.Max(0f, severity - rate * 0.5f);
                else newSeverity = Math.Min(1f, severity + rate);
                return o;
            }
            if (hasHediff)
            {
                float decay = hasExt ? decayOnExt : 0.02f;
                newSeverity = severity - decay;
                if (newSeverity <= 0f) return Outcome.Remove;
            }
            return Outcome.Nothing;
        }
    }
}
