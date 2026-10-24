// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 T3 part (c) -- the Nine's two rules, pure kernel so the selftest drives them.
//   * THE GATE (owner ruling, review package §9.12): a god's named pattern exists only aboard a Utinni gravship. A
//     signature reading (a scheme some RM_SignatureDef names) may show only on a map whose scenario decides for it
//     (RM_MapComponent_AtmosphericBase.scenarioDecides, the mod's existing Utinni detection) AND that carries a player
//     grav engine. Anywhere else a pushed god mood is inert: it is dropped from the ranking, so the neutral default (or
//     another mood) shows, and nothing in the settings ever names a god (the neutral set is RM_PatternChoice's alone).
//   * THE FLOOR (owner ruling §9.14, "Full is Full; Gentle keeps a floor"): Full plays a god's reading as authored, so
//     a dark god reaches true black. Gentle lifts any index whose max channel is under GodFloor to the first entry at
//     or above it. This is NOT the neutral working-light floor (RM_PatternChoice.WorkingFloor, 176): a god's reading is
//     an omen, not a working light, and that clamp would flatten Ishko and Oomo to one constant entry.
// No game types.
using System;

namespace RimMandrake.AtmosphericBase
{
    public static class RM_GodGate
    {
        /// <summary>Gentle's floor for a god's reading, as a max channel. PROVISIONAL (agent's choice, not in the design
        /// doc): 48 lifts only the near-black entries (Ishko's Black and Smoulder, Zizzik's Void) and leaves every god's
        /// deep tone (Oomo's Deep, Ozzik's Mourning, Rekko's Patina, all 52-82) alone.</summary>
        public const int GodFloor = 48;

        /// <summary>May this mood show? A neutral scheme always may; a god's reading only aboard a Utinni gravship.</summary>
        public static bool MayShow(bool isSignature, bool scenarioDecides, bool hasGravEngine)
            => !isSignature || (scenarioDecides && hasGravEngine);

        private static int Max(RM_SchemeData s, int i) => Math.Max(s.r[i], Math.Max(s.g[i], s.b[i]));

        /// <summary>Gentle's lowest index: the first entry at or above GodFloor (the brightest entry if none is).</summary>
        public static int GentleLow(RM_SchemeData s)
        {
            int n = s.Count, bright = 0;
            for (int i = 0; i < n; i++)
            {
                if (Max(s, i) >= GodFloor) return i;
                if (Max(s, i) > Max(s, bright)) bright = i;
            }
            return bright;
        }

        /// <summary>The index a god's reading shows at this intensity: Full passes it, Gentle lifts it to GentleLow.
        /// The top is never clamped -- an eye, a beam, a spark is the god's signature, not a flare to tame.</summary>
        public static int Apply(RM_SchemeData s, int idx, int intensity)
        {
            if (intensity == (int)RM_Intensity.Full || s.Count == 0) return idx;
            int lo = GentleLow(s);
            return idx < lo ? lo : idx;
        }

        /// <summary>Under Gentle no shown entry is below the floor (when the palette has any entry at or above it).</summary>
        public static bool GentleKeepsFloor(RM_SchemeData s)
        {
            if (s.Count == 0) return false;
            for (int i = 0; i < s.Count; i++)
                if (Max(s, Apply(s, i, (int)RM_Intensity.Gentle)) < GodFloor && Max(s, GentleLow(s)) >= GodFloor) return false;
            return true;
        }
    }
}
