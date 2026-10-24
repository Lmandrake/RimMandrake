// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 2 -- the pure half of schemes and the one-mood compositor.
//
// Spec design/RimMandrake/atmospheric_base_mod_definition.md §2.3 (scheme = palette, pattern, brightness, rate; DATA,
// and the pattern a pure function of (emitter, group, time) returning a palette INDEX) and §2.6 steps 1, 5, 6.
// No game types: a palette is int triples, an emitter is two ints. The selftest drives every function here directly.
//
// Why an index and never a colour: L4. RimWorld caches a Graphic/Material per exact colour, so the only colours that
// may ever reach a fixture are palette members. The pattern cannot produce a colour at all -- it can only point into
// the palette -- so interpolation is impossible by construction, and RM_PaletteGuard re-checks at the write.
//
// Brightness lives IN the palette (a darker entry is a dimmer light; GlowGrid.GroundGlowAt reads the max channel of
// the accumulated glow). Radius is never touched: the shared light ledger (_Shared/LightLedger) owns it
using System;
using System.Collections.Generic;

namespace RimMandrake.AtmosphericBase
{
    public enum RM_PatternKind
    {
        Steady = 0,      // palette[0], held. Only for a single-entry or a deliberately still scheme.
        RoomBreath = 1,  // catalog III-2 Lamplight: each group (room) walks the palette up and back on its own phase.
        Sparks = 2,      // catalog III-1 Fireflies: each fixture rests at [0] and now and then rises through the
                         // palette and back, independently; no wave anywhere.
    }

    public struct RM_SchemeData
    {
        public int[] r, g, b;           // the palette, parallel arrays
        public RM_PatternKind pattern;
        public float massPeriodSeconds; // RoomBreath: one full up-and-back. Sparks: the slot one spark may fall in.
        public float sparkSeconds;      // Sparks only: how long one rise-and-fall lasts
        public int sparkOneIn;          // Sparks only: a fixture sparks in 1 of this many slots
        public bool mayGoDark;          // L8: may an entry be full black
        public int flasherCount;        // L7: how many fixtures in the group play the fast role
        public float flasherPeriodSeconds;

        public int Count => r == null ? 0 : r.Length;
    }

    public static class RM_SchemeKernel
    {
        public const int MaxPalette = 8;       // "a small fixed set" (L4); the catalog runs P = 1..4

        // L11, as ruled 2026-10-23 (review package §9.5): white is ONE reserved token, the Narrator's, and anything near
        // it is banned from every scheme -- gods' palettes included, which all arrive as RM_AtmosphericSchemeDefs and
        // pass Errors() in ConfigErrors. "Near" is one distance check against the token, replacing the old
        // "all channels >= 200" floor, which let a cream (255,240,199) or a cool white (199,230,255) through.
        // 🔴 PROVISIONAL, TO BE CALIBRATED AT THE LIVE LOOK: the Narrator's exact white is chosen there, and so is the
        // distance. Until then both are conservative: pure white, and a Euclidean RGB radius of 100 (on 0-255
        // channels), which refuses the cream and the cool white above (58 and 61 away) and the Royalty ethereal light
        // (217,217,208) (71 away), and admits the default's brightest entry (255,210,148) (116 away).
        public const int NarratorWhiteR = 255, NarratorWhiteG = 255, NarratorWhiteB = 255;
        public const int ReservedWhiteDistance = 100;

        public static int DistanceSqToNarratorWhite(int r, int g, int b)
        {
            int dr = r - NarratorWhiteR, dg = g - NarratorWhiteG, db = b - NarratorWhiteB;
            return dr * dr + dg * dg + db * db;
        }

        /// <summary>L11: this colour is the Narrator's reserved white or near enough to be read as it.</summary>
        public static bool NearNarratorWhite(int r, int g, int b)
        {
            return DistanceSqToNarratorWhite(r, g, b) <= ReservedWhiteDistance * ReservedWhiteDistance;
        }

        // ---------------------------------------------------------------- validation (a def's ConfigErrors)

        public static List<string> Errors(RM_SchemeData s)
        {
            var e = new List<string>();
            int n = s.Count;
            if (n == 0) { e.Add("palette is empty"); return e; }
            if (s.g == null || s.b == null || s.g.Length != n || s.b.Length != n) { e.Add("palette channels differ in length"); return e; }
            if (n > MaxPalette) e.Add("palette has " + n + " colours; L4 allows at most " + MaxPalette);
            bool anyDark = false;
            for (int i = 0; i < n; i++)
            {
                if (s.r[i] < 0 || s.g[i] < 0 || s.b[i] < 0) e.Add("palette[" + i + "] has a negative channel");
                if (NearNarratorWhite(s.r[i], s.g[i], s.b[i]))
                    e.Add("palette[" + i + "] is within " + ReservedWhiteDistance + " of the Narrator's white, which L11 reserves for the Narrator");
                bool dark = s.r[i] == 0 && s.g[i] == 0 && s.b[i] == 0;
                anyDark |= dark;
                if (dark && !s.mayGoDark) e.Add("palette[" + i + "] is full black but mayGoDark is false");
                for (int j = 0; j < i; j++)
                    if (s.r[i] == s.r[j] && s.g[i] == s.g[j] && s.b[i] == s.b[j]) e.Add("palette[" + i + "] repeats palette[" + j + "]");
            }
            if (anyDark && s.pattern == RM_PatternKind.Steady)
                e.Add("a Steady scheme may not hold full black: L8 says a chosen dark always carries motion");
            if (s.pattern != RM_PatternKind.Steady && !(s.massPeriodSeconds > 0f)) e.Add("massPeriodSeconds must be > 0");
            if (s.pattern == RM_PatternKind.Sparks)
            {
                if (!(s.sparkSeconds > 0f) || s.sparkSeconds > s.massPeriodSeconds) e.Add("sparkSeconds must be > 0 and fit inside massPeriodSeconds");
                if (s.sparkOneIn < 1) e.Add("sparkOneIn must be >= 1");
            }
            if (s.flasherCount < 0) e.Add("flasherCount is negative");
            if (s.flasherCount > 0 && !(s.flasherPeriodSeconds > 0f)) e.Add("flasherPeriodSeconds must be > 0 when there are flashers");
            if (s.flasherCount > 0 && n < 2) e.Add("a flasher needs at least two palette entries to flash between");
            return e;
        }

        // ---------------------------------------------------------------- hashing (stable, platform-independent)

        public static uint Mix(uint x)
        {
            x ^= x >> 16; x *= 0x7feb352dU; x ^= x >> 15; x *= 0x846ca68bU; x ^= x >> 16;
            return x;
        }

        public static uint Mix(int a, int b)
        {
            return Mix(unchecked((uint)a * 0x9E3779B1U ^ Mix((uint)b + 0x632BE5ABU)));
        }

        /// <summary>A stable fraction in [0,1) from an int.</summary>
        public static double Frac01(int a, int salt)
        {
            return (Mix(a, salt) >> 8) / (double)(1 << 24);
        }

        // ---------------------------------------------------------------- the pattern: (emitter, group, time) -> index

        /// <summary>Up-and-back walk over n entries: 0,1,..,n-1,n-2,..,1 (length 2n-2), or {0} for n == 1.</summary>
        public static int PingPong(int n, int step)
        {
            if (n <= 1) return 0;
            int len = 2 * n - 2;
            int k = ((step % len) + len) % len;
            return k < n ? k : len - k;
        }

        public static int PaletteIndex(RM_SchemeData s, int emitter, int group, double time, bool flasher)
        {
            int n = s.Count;
            if (n <= 1) return 0;
            if (flasher)
            {
                double fp = s.flasherPeriodSeconds;
                long fstep = (long)Math.Floor(time / fp + Frac01(emitter, 3) * n);
                return (int)(fstep % n);
            }
            switch (s.pattern)
            {
                case RM_PatternKind.RoomBreath:
                {
                    int len = 2 * n - 2;
                    double u = time / s.massPeriodSeconds + Frac01(group, 1);
                    long step = (long)Math.Floor(u * len);
                    return PingPong(n, (int)(step % len));
                }
                case RM_PatternKind.Sparks:
                {
                    double p = s.massPeriodSeconds;
                    double shifted = time + Frac01(emitter, 2) * p;
                    long slot = (long)Math.Floor(shifted / p);
                    if (Mix(emitter, unchecked((int)slot)) % (uint)s.sparkOneIn != 0) return 0;
                    double within = shifted - slot * p;
                    if (within >= s.sparkSeconds) return 0;
                    int len = 2 * n - 1;                        // 0..n-1..0, rest at both ends
                    int k = Math.Min(len - 1, (int)Math.Floor(within / s.sparkSeconds * len));
                    return k < n ? k : len - 1 - k;
                }
                default:
                    return 0;
            }
        }

        /// <summary>L7: the framework picks which fixtures flash -- the flasherCount with the lowest hash, so the choice is
        /// stable while membership is stable and never depends on list order.</summary>
        public static HashSet<int> PickFlashers(IList<int> emitters, int flasherCount)
        {
            var set = new HashSet<int>();
            if (flasherCount <= 0 || emitters == null || emitters.Count == 0) return set;
            var order = new List<int>(emitters);
            order.Sort((x, y) => Mix(x, 7).CompareTo(Mix(y, 7)));
            for (int i = 0; i < order.Count && i < flasherCount; i++) set.Add(order[i]);
            return set;
        }

        // ---------------------------------------------------------------- the shipped default groups (§2.2 source 3)

        public const string GroupShip = "ship";
        public const string GroupRooms = "rooms";
        public const string GroupHalls = "halls";
        public const string GroupExterior = "exterior";
        public static readonly string[] DefaultGroups = { GroupShip, GroupRooms, GroupHalls, GroupExterior };

        public enum RM_Place { Room = 0, Hall = 1, Exterior = 2 }

        /// <summary>No room, or a room the game counts as outdoors, is exterior. A room whose role is the generic "None" or
        /// "Room" (vanilla gives a corridor no role of its own -- RoomRoles.xml has no hallway) is a hall. Anything with a
        /// function (bedroom, workshop, ...) is a room.</summary>
        public static RM_Place PlaceOf(bool hasRoom, bool outdoors, string roleDefName)
        {
            if (!hasRoom || outdoors) return RM_Place.Exterior;
            if (string.IsNullOrEmpty(roleDefName) || roleDefName == "None" || roleDefName == "Room") return RM_Place.Hall;
            return RM_Place.Room;
        }

        public static bool InDefaultGroup(string group, RM_Place place)
        {
            switch (group)
            {
                case GroupShip: return true;
                case GroupRooms: return place == RM_Place.Room;
                case GroupHalls: return place == RM_Place.Hall;
                case GroupExterior: return place == RM_Place.Exterior;
                default: return false;
            }
        }
    }

    /// <summary>§2.6 step 6: write and dirty only what changed. One slot per emitter holding what it is showing now;
    /// Want() answers true only when the new value differs, and records it.</summary>
    public class RM_ChangeTracker
    {
        // value -1 = the substrate (the fixture's own prior glow); otherwise a packed (scheme, palette index).
        private readonly Dictionary<int, long> showing = new Dictionary<int, long>();

        public const long Substrate = -1;

        public static long Pack(int schemeId, int index) => ((long)(uint)schemeId << 8) | (uint)(index & 0xFF);

        public bool Want(int emitter, long value)
        {
            // An emitter never seen is ALWAYS written once, substrate included: after a reload the fixture's saved
            // override still holds the last driven colour (CompGlower Scribes it), so "never seen" is not "showing its
            // own glow".
            if (showing.TryGetValue(emitter, out long cur) && cur == value) return false;
            showing[emitter] = value;
            return true;
        }

        public bool Shows(int emitter, out long value) => showing.TryGetValue(emitter, out value);
        public void Forget(int emitter) => showing.Remove(emitter);
        public void Clear() => showing.Clear();
        public int Count => showing.Count;
    }
}
