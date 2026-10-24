// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 part (b) -- the player's choice OFF the Utinni (design
// atmospheric_base_god_patterns_2026-10-24.md §3; owner ruling: off the Utinni there are no gods, only neutral, unnamed,
// player-selectable patterns, gentle by default). Three choices, all pure kernel so the selftest drives them:
//   * the PATTERN SET: which neutral scheme the default mood runs (index 0 = Lamplight, the shipped default);
//   * the TEMPO: Slow (x1.5 periods), Shipped, Lively (x0.67). The pattern's clock runs at 1/factor, which stretches
//     every period of every layer alike and never touches a palette (§3: "periods only, never palettes");
//   * the INTENSITY: Gentle (the shipped default) clamps an index to the scheme's inner entries -- never below the
//     first entry bright enough to work under, never on the top flare of a palette of four or more; Full is as authored.
// Palettes are authored dim to bright, so "inner" is an index range. Applied to the default mood only: a pushed mood
// (a scenario's, a mod's, a god's aboard the Utinni) is never re-tempoed or clamped by the player's off-ship choice.
// No game types.
using System;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_Tempo { Slow = 0, Shipped = 1, Lively = 2 }
    public enum RM_Intensity { Gentle = 0, Full = 1 }

    public static class RM_PatternChoice
    {
        /// <summary>The working-light floor: an entry whose max channel is under this is too dim to work under
        /// (GlowGrid reads the max channel; the vanilla lamp is 214). The same floor the Lamplight selftest holds.</summary>
        public const int WorkingFloor = 176;

        /// <summary>The neutral set, in menu order. Index 0 is the shipped default. Every name is an
        /// RM_AtmosphericSchemeDef in Defs/RM_AtmosphericSchemes.xml (the proof's D11 row holds the two in step).</summary>
        public static readonly string[] NeutralSchemes =
        {
            "RM_Scheme_Lamplight", "RM_Scheme_Fireflies", "RM_Scheme_Tidewater", "RM_Scheme_Lanternwalk",
            "RM_Scheme_Rings", "RM_Scheme_Duskfall",
        };

        public static readonly string[] TempoLabels = { "Slow", "Shipped", "Lively" };
        public static readonly string[] IntensityLabels = { "Gentle", "Full" };

        public static int ClampSet(int i) => i < 0 || i >= NeutralSchemes.Length ? 0 : i;
        public static string NeutralScheme(int i) => NeutralSchemes[ClampSet(i)];

        public static double TempoFactor(int tempo)
        {
            switch (tempo)
            {
                case (int)RM_Tempo.Slow: return 1.5;
                case (int)RM_Tempo.Lively: return 0.67;
                default: return 1.0;
            }
        }

        /// <summary>The pattern clock at this tempo: a period P plays as P x factor.</summary>
        public static double TempoTime(double t, int tempo) => t / TempoFactor(tempo);

        private static int Max(RM_SchemeData s, int i) => Math.Max(s.r[i], Math.Max(s.g[i], s.b[i]));

        /// <summary>Gentle's index range: lo = the first entry at or above the working floor (the brightest entry if
        /// none is, and then hi = lo), hi = the last entry but one when there are four or more, else the last; lo &lt;= hi always.</summary>
        public static void GentleRange(RM_SchemeData s, out int lo, out int hi)
        {
            int n = s.Count;
            lo = 0; hi = n - 1;
            if (n <= 1) { hi = 0; return; }
            int bright = 0;
            lo = -1;
            for (int i = 0; i < n; i++)
            {
                if (Max(s, i) > Max(s, bright)) bright = i;
                if (lo < 0 && Max(s, i) >= WorkingFloor) lo = i;
            }
            if (lo < 0) { lo = hi = bright; return; }   // no working light at all: hold the brightest
            hi = n >= 4 ? n - 2 : n - 1;
            if (hi < lo) hi = lo;
        }

        /// <summary>The index the player's intensity lets through: Full passes it, Gentle clamps it into GentleRange.</summary>
        public static int Apply(RM_SchemeData s, int idx, int intensity)
        {
            if (intensity == (int)RM_Intensity.Full || s.Count == 0) return idx;
            GentleRange(s, out int lo, out int hi);
            return idx < lo ? lo : idx > hi ? hi : idx;
        }

        /// <summary>Every entry Gentle can show is a working light and none is black.</summary>
        public static bool GentleIsWorking(RM_SchemeData s)
        {
            if (s.Count == 0) return false;
            GentleRange(s, out int lo, out int hi);
            for (int i = lo; i <= hi; i++) if (Max(s, i) < WorkingFloor) return false;
            return true;
        }
    }
}
