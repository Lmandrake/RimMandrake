// CRACKEDLANDS_THREE_HEIGHT_FLORA_1 — the three flora laws as pure arithmetic (no Verse, no Unity), so the
// SelfTest fuzz can sweep them whole. The mod's RM_ThreeHeightFlora.cs reads the map and calls these.
//
//   Veqma      shade law  (ruled 2026-10-09 by card: a glow limit on the plant def, so it holds anywhere,
//                          player-sown included). The glow is the cell's DAYLIGHT glow, a pure function of
//                          geometry and never of the clock: a roofed cell sees only artificial light; an open
//                          cell loses one eighth of the sky for every light-blocking neighbour (a wall foot
//                          has three, an inside corner five), so the shade line is the lee of the walls.
//   Qirra mat  flood law  opens only on open, dry-land ground a recede wetted within the soak window.
//   Talus clasp wall law  roots only where at least one cardinal neighbour is natural wall rock.
namespace RimMandrake.CrackedLands
{
    public static class RM_FloraLawKernel
    {
        /// <summary>Sky lost per light-blocking neighbour (of eight).</summary>
        public const float ShadePerBlocker = 0.125f;

        /// <summary>Slack so a limit written as 0.625 admits exactly three blockers despite float sums.</summary>
        public const float GlowEpsilon = 0.0001f;

        public static float DaylightGlow(bool roofed, float artificialGlow, int blockedNeighbours)
        {
            if (artificialGlow < 0f) artificialGlow = 0f;
            if (artificialGlow > 1f) artificialGlow = 1f;
            if (roofed)
            {
                return artificialGlow;
            }
            if (blockedNeighbours < 0) blockedNeighbours = 0;
            if (blockedNeighbours > 8) blockedNeighbours = 8;
            float sky = 1f - ShadePerBlocker * blockedNeighbours;
            return sky > artificialGlow ? sky : artificialGlow;
        }

        public static bool GlowAllowed(float glow, float maxGlow)
        {
            return glow <= maxGlow + GlowEpsilon;
        }

        /// <summary>A recede marks a cell wet until a tick; the cell counts as recently wetted strictly before it.</summary>
        public static bool RecentlyWet(int wetUntilTick, int now)
        {
            return wetUntilTick > 0 && now < wetUntilTick;
        }

        /// <summary>The flood law: wetted within the window, open sky, dry land (not water) under it.</summary>
        public static bool QirraCellOk(bool recentlyWet, bool roofed, bool water)
        {
            return recentlyWet && !roofed && !water;
        }

        /// <summary>The wall law: at least one of the four cardinal neighbours is natural wall rock.</summary>
        public static bool ClaspCellOk(int naturalWallCardinals)
        {
            return naturalWallCardinals >= 1;
        }

        /// <summary>How many mats a recede wakes: a share of the good cells, never above the cap.</summary>
        public static int QirraWant(int goodCells, float share, int cap)
        {
            if (goodCells <= 0 || share <= 0f || cap <= 0)
            {
                return 0;
            }
            if (share > 1f) share = 1f;
            int want = (int)(goodCells * share + 0.5f);
            if (want < 1) want = 1;
            if (want > goodCells) want = goodCells;
            return want > cap ? cap : want;
        }

        /// <summary>Extra mined pieces beside a clasp: the base yield times the bonus, rounded down, at least one when the
        /// bonus is on and the base yields anything.</summary>
        public static int MiningBonus(int baseYield, float bonusFactor)
        {
            if (baseYield <= 0 || bonusFactor <= 0f)
            {
                return 0;
            }
            int extra = (int)(baseYield * bonusFactor);
            return extra < 1 ? 1 : extra;
        }

        /// <summary>The map-wide gap between two pried cracks, so a wall of clasps never floods the letter stack.</summary>
        public static bool PryAllowedNow(int lastPryTick, int now, int minGapTicks)
        {
            return lastPryTick < 0 || now - lastPryTick >= minGapTicks;
        }

        /// <summary>One TickLong's chance (2000 ticks) of an event with mean time between of MTB days (60000 ticks/day).</summary>
        public static float ChancePerLongTick(float mtbDays)
        {
            if (mtbDays <= 0f)
            {
                return 0f;
            }
            float p = 2000f / (mtbDays * 60000f);
            return p > 1f ? 1f : p;
        }
    }
}
