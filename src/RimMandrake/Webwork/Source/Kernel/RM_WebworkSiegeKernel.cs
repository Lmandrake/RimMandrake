// WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE: the Verse-free decisions of the Webwork siege (design/RimMandrake/
// webwork_spider_siege_2026-10-22.md). RM_WebworkSiege.cs calls these; src/RimMandrake/Utils/selftest_webwork_fuzz.py compiles
// THIS file (no RimWorld/Unity) and fuzzes it as the `siege` family. A `using Verse;` here breaks that build on purpose.
using System;

namespace RimMandrake.Webwork
{
    /// <summary>Why a map may or may not be besieged. Only Eligible lets the siege fire.</summary>
    public enum SiegeEligibility { Eligible, Disabled, WebworkMapItself, NotNeighbour, ShadeUnmeasurable, NotShaded }

    public static class RM_WebworkSiegeKernel
    {
        public const float PointsPerSpider = 160f;      // RM_Ollathrix combatPower
        public const int MinSpiders = 2;                // PROVISIONAL
        public const int MaxSpiders = 8;                // PROVISIONAL, before siegeStrength
        public const int BaseSpinTicks = 600;           // PROVISIONAL: 10 s of game time per spun web
        public const int MinSpinTicks = 60;
        public const int MaxSpunPerSiege = 400;         // PROVISIONAL
        public const int PressAfterSpun = 60;           // PROVISIONAL
        public const int PressAfterTicks = 18 * 2500;   // PROVISIONAL: 18 game hours
        public const float PressRadius = 12f;           // PROVISIONAL: a spun web this close to a colony building
        public const int YieldPerCut = 2;               // PROVISIONAL: thrixweave per siege web cut
        public const int MinShadeSamples = 50;          // fewer sampled open cells than this = unmeasurable
        public const int TicksPerDay = 60000;
        public const int TicksPerHour = 2500;

        /// <summary>The siege's gate, in order. The test hook skips only the neighbour and shade tests (never the master
        /// switch, never "this is the Webwork itself"). Fail closed: a map the shade grid cannot answer for is not shaded.</summary>
        public static SiegeEligibility Eligibility(bool enabled, bool testIgnoreMapChecks, bool isWebworkMap, bool bordersWebwork,
            bool shadeMeasurable, int sampledOpenCells, int shadedOpenCells, float minShadedFraction)
        {
            if (!enabled) return SiegeEligibility.Disabled;
            if (isWebworkMap) return SiegeEligibility.WebworkMapItself;
            if (testIgnoreMapChecks) return SiegeEligibility.Eligible;
            if (!bordersWebwork) return SiegeEligibility.NotNeighbour;
            if (!shadeMeasurable || sampledOpenCells < MinShadeSamples) return SiegeEligibility.ShadeUnmeasurable;
            if (ShadedFraction(sampledOpenCells, shadedOpenCells) < minShadedFraction) return SiegeEligibility.NotShaded;
            return SiegeEligibility.Eligible;
        }

        public static float ShadedFraction(int sampled, int shaded)
        {
            if (sampled <= 0) return 0f;
            int s = Math.Max(0, Math.Min(shaded, sampled));
            return (float)s / sampled;
        }

        /// <summary>points / 160 x strength, clamped to [2, max(2, round(8 x strength))].</summary>
        public static int SpiderCount(float points, float strength)
        {
            float st = Math.Max(0.05f, strength);
            int hi = Math.Max(MinSpiders, (int)Math.Round(MaxSpiders * st, MidpointRounding.AwayFromZero));
            double raw = Math.Max(0f, points) / PointsPerSpider * st;
            int n = (int)Math.Round(raw, MidpointRounding.AwayFromZero);
            return Math.Max(MinSpiders, Math.Min(hi, n));
        }

        /// <summary>Work ticks for one web at a spin-speed multiplier (faster = fewer ticks).</summary>
        public static int SpinTicks(float speed)
        {
            float sp = Math.Max(0.05f, speed);
            return Math.Max(MinSpinTicks, (int)Math.Round(BaseSpinTicks / sp));
        }

        /// <summary>A candidate spin cell's score: nearer the colony is better, beside the siege's own silk better (the web grows
        /// from web), beside an anchor (tree, wall, rock) better, far from the spinner slightly worse. Higher wins.</summary>
        public static float SpinScore(float distToColony, float distFromSpinner, int adjacentSiegeWebs, int adjacentAnchors)
        {
            int webs = Math.Max(0, Math.Min(8, adjacentSiegeWebs));
            int anchors = Math.Max(0, Math.Min(8, adjacentAnchors));
            return -Math.Max(0f, distToColony) - 0.25f * Math.Max(0f, distFromSpinner) + 3f * Math.Min(webs, 2) + 1.5f * Math.Min(anchors, 2);
        }

        public static bool MaySpinMore(int spunSoFar) { return spunSoFar < MaxSpunPerSiege; }

        /// <summary>Spin -> Press: a web reached the colony, or enough spun, or long enough passed.</summary>
        public static bool ShouldPress(bool webNearColony, int spun, int ticksSinceArrival)
        {
            return webNearColony || spun >= PressAfterSpun || ticksSinceArrival >= PressAfterTicks;
        }

        /// <summary>Time-out break: siegeMaxDays since arrival (losses break through the lord's own half-lost trigger).</summary>
        public static bool TimedOut(int ticksSinceArrival, float maxDays)
        {
            return ticksSinceArrival >= (int)(Math.Max(0.1f, maxDays) * TicksPerDay);
        }

        /// <summary>How much thrixweave one cut of a siege web may drop, given how much this siege has already yielded.</summary>
        public static int YieldGranted(int alreadyYielded, int cap, int perCut)
        {
            if (cap <= 0 || perCut <= 0) return 0;
            int left = cap - Math.Max(0, alreadyYielded);
            return left <= 0 ? 0 : Math.Min(perCut, left);
        }

        public static int CocoonDeathTicks(float hours)
        {
            return Math.Max(TicksPerHour, (int)Math.Round(Math.Max(1f, hours) * TicksPerHour));
        }

        public static bool CocoonKills(int ticksInside, float hours)
        {
            return ticksInside >= CocoonDeathTicks(hours);
        }

        public static float CocoonHoursLeft(int ticksInside, float hours)
        {
            return Math.Max(0f, (CocoonDeathTicks(hours) - ticksInside) / (float)TicksPerHour);
        }

        public static string Describe(SiegeEligibility e)
        {
            switch (e)
            {
                case SiegeEligibility.Eligible: return "eligible";
                case SiegeEligibility.Disabled: return "the siege setting is off";
                case SiegeEligibility.WebworkMapItself: return "this is a Webwork map";
                case SiegeEligibility.NotNeighbour: return "the map's tile does not border the Webwork";
                case SiegeEligibility.ShadeUnmeasurable: return "the shade grid cannot answer for this map (fails closed)";
                case SiegeEligibility.NotShaded: return "too little of the open ground is shaded";
                default: return e.ToString();
            }
        }
    }
}
