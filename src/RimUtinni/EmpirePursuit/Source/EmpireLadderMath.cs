/* EMPIRE_ESCALATION_LADDER_1 — the ladder's pure arithmetic, kept free of Find.* so the
 * offline selftest (SelfTest/Program.cs) can call the real code. Design:
 * design/Jawa/proposals/empire_escalation_ladder_design_2026-10-02.md §2-§4, with the owner's
 * 2026-10-03 card rulings: moving = full reset to rung 1 with a permanent leak floor.
 * Every number here is PROVISIONAL (first guess from the design doc, not tuned). */
using System;

namespace RuthlessPursuingMechanoids
{
    public static class EmpireLadderMath
    {
        public const int QuietRung = 0;
        public const int ProbeRung = 1;
        public const int SpotterRung = 2;
        public const int StrikeRung = 3;
        public const int TopRung = 6;

        /// <summary>Design §2 timer coupling: Hidden ×2.0 · Discreet ×1.4 · Noticed ×1.0 ·
        /// Marked ×0.7 · Exposed ×0.5. Band edges match Visibility's BandFor (20/40/60/80).
        /// A negative visibility means "Visibility mod absent" and returns 1.</summary>
        public static float BandIntervalMultiplier(float visibility)
        {
            if (visibility < 0f) return 1f;
            if (visibility < 20f) return 2.0f;
            if (visibility < 40f) return 1.4f;
            if (visibility < 60f) return 1.0f;
            if (visibility < 80f) return 0.7f;
            return 0.5f;
        }

        /// <summary>Design §3: rungs 3+ come at half the base interval ("rapidly"); a probe that
        /// left blind makes the next probe come later (×1.5).</summary>
        public static float RungIntervalFactor(int nextRung, bool lastProbeBlind)
        {
            float f = nextRung >= StrikeRung ? 0.5f : 1f;
            if (lastProbeBlind && nextRung == ProbeRung) f *= 1.5f;
            return f;
        }

        /// <summary>Rung N+1 fires next only if rung N succeeded from the Empire's side;
        /// otherwise rung N repeats. Never above the top rung, never below the floor.</summary>
        public static int NextRungAfter(int firedRung, bool empireSucceeded, int floor)
        {
            int next = empireSucceeded ? firedRung + 1 : firedRung;
            return Clamp(next, floor);
        }

        /// <summary>A remembered rung loses decayPerSeason rungs for each WHOLE season away.</summary>
        public static int DecayedRung(int rungAtDeparture, float seasonsAway, int decayPerSeason)
        {
            if (seasonsAway < 0f) seasonsAway = 0f;
            int lost = (int)Math.Floor(seasonsAway) * Math.Max(0, decayPerSeason);
            return Math.Max(0, rungAtDeparture - lost);
        }

        /// <summary>The rung a freshly generated map starts at. Owner ruling 2026-10-03: moving is a
        /// full reset to rung 1 (the probe), with a permanent leak floor. "Probes open every ladder"
        /// off starts at the strike. A remembered tile (returning to where they were looking) may
        /// start higher; pass remembered = -1 for none.</summary>
        public static int StartingRung(int floor, bool probesOpen, int remembered)
        {
            int start = probesOpen ? ProbeRung : StrikeRung;
            if (remembered > start) start = remembered;
            return Clamp(start, floor);
        }

        public static int Clamp(int rung, int floor)
        {
            if (rung < floor) rung = floor;
            if (rung < ProbeRung) rung = ProbeRung;
            if (rung > TopRung) rung = TopRung;
            return rung;
        }

        /// <summary>Probe sighting: a colonist or the ship counts as seen when in line of sight
        /// within range, unless the target stands in darkness (glow &lt; 0.3) and is farther than
        /// the close range. Pure predicate; the caller supplies LOS and glow.</summary>
        public static bool Sees(float distance, bool lineOfSight, float targetGlow,
                                float range = 26f, float darkRange = 6f)
        {
            if (!lineOfSight || distance > range) return false;
            if (targetGlow < 0.3f && distance > darkRange) return false;
            return true;
        }

        /// <summary>Aftermath's REPELLED rule mirrored (>= 60% of the raiders dead or downed),
        /// used when mandrake.rm.aftermath is absent or never classified the battle.</summary>
        public static bool Repelled(int raiders, int deadOrDowned)
        {
            if (raiders <= 0) return true;
            return deadOrDowned >= (int)Math.Ceiling(raiders * 0.6);
        }
    }
}
