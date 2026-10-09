// Webwork kernel: the Verse-free decisions of the urraveth remains, the egg-clutch relay, the emergent spawn, the biome score and
// the nest/site placement tests. The mod calls these with the same expressions it used inline; src/RimMandrake/Utils/
// selftest_webwork_fuzz.py compiles THIS file (no RimWorld/Unity) and fuzzes it. A `using Verse;` here breaks that build on purpose.
using System;
using System.Collections.Generic;

namespace RimMandrake.Webwork
{
    public enum CreakEvent { None, Started, Settled, Tick, Collapse }
    public enum ExamineOutcome { Nothing, ReadChapter, Complete }
    public enum RelayPlan { NotDue, DyingNest, Reschedule, Place }

    /// <summary>The wrapped urraveth skeleton: load, creak, collapse, support cascade, chapters.</summary>
    public static class RM_UrravethKernel
    {
        public const float HeavyDamageFraction = 0.35f;   // PROVISIONAL: "heavily damaged"
        public const int RareTicks = 250;
        public const int MinWindowTicks = 250;
        public const float TicksPerHour = 2500f;
        public const int MinExamineTicks = 60;
        public static readonly string[] ChapterOrder = { "pinned", "bound", "cut", "eaten" };

        /// <summary>Two footprints are neighbours when b has a cell inside a expanded by one (overlap and diagonals count).</summary>
        public static bool Adjacent(int aMinX, int aMinZ, int aMaxX, int aMaxZ, int bMinX, int bMinZ, int bMaxX, int bMaxZ)
        {
            return bMinX <= aMaxX + 1 && bMaxX >= aMinX - 1 && bMinZ <= aMaxZ + 1 && bMaxZ >= aMinZ - 1;
        }

        /// <summary>A neighbour of strictly lower rank holds this piece up.</summary>
        public static bool IsSupporter(int neighbourRank, int myRank) { return neighbourRank < myRank; }

        /// <summary>A neighbour of strictly higher rank is held up by this piece.</summary>
        public static bool IsSupported(int neighbourRank, int myRank) { return neighbourRank > myRank; }

        public static float ItemLoad(float mass, int stackCount, float itemMassPerLoad)
        {
            return mass * stackCount / Math.Max(1f, itemMassPerLoad);
        }

        public static bool HeavilyDamaged(int hitPoints, int maxHitPoints)
        {
            return hitPoints < maxHitPoints * HeavyDamageFraction;
        }

        /// <summary>Everything standing on the piece plus every lost or heavily damaged supporter, each counting a full capacity.</summary>
        public static float Load(float occupantLoad, int lostSupports, float loadCapacity, int heavySupporters)
        {
            float load = occupantLoad;
            load += lostSupports * loadCapacity;
            load += heavySupporters * loadCapacity;
            return load;
        }

        public static bool Overloaded(float load, float loadCapacity) { return load >= loadCapacity; }

        public static int WindowTicks(float warningHours)
        {
            return Math.Max(MinWindowTicks, (int)Math.Round(warningHours * TicksPerHour));
        }

        public static int ExamineTicks(int baseTicks, bool wrapped)
        {
            return Math.Max(MinExamineTicks, baseTicks) * (wrapped ? 1 : 2);
        }

        /// <summary>A pawn counts as near when its horizontal distance is within the radius plus half the piece's longer side.</summary>
        public static bool PawnNear(int dx, int dz, float nearRadius, int sizeX, int sizeZ)
        {
            float d = (float)Math.Sqrt(dx * dx + dz * dz);
            return d <= nearRadius + Math.Max(sizeX, sizeZ) * 0.5f;
        }

        /// <summary>One load evaluation covering <paramref name="ticks"/> ticks. creakTicksLeft &lt; 0 means not creaking. The nearness
        /// test is only asked while creaking and still overloaded (it walks every pawn on the map).</summary>
        public static CreakEvent Step(ref int creakTicksLeft, bool over, Func<bool> anyPawnNear, int ticks, int windowTicks)
        {
            if (creakTicksLeft < 0)
            {
                if (over)
                {
                    creakTicksLeft = windowTicks;
                    return CreakEvent.Started;
                }
                return CreakEvent.None;
            }
            if (!over)
            {
                creakTicksLeft = -1;
                return CreakEvent.Settled;
            }
            if (!anyPawnNear())
            {
                return CreakEvent.None;   // unwatched bones hold; nothing collapses while nobody is near
            }
            creakTicksLeft -= ticks;
            return creakTicksLeft <= 0 ? CreakEvent.Collapse : CreakEvent.Tick;
        }

        /// <summary>A removed piece loads every piece it held up; one that is now overloaded and quiet starts to creak.</summary>
        public static bool StartsCreakingOnLoss(bool enabled, bool creaking, bool overloaded)
        {
            return enabled && !creaking && overloaded;
        }

        public static bool CanOpenLastWrapping(bool isSkull, bool wrapped, bool hasReading, bool complete, bool spawned, bool everyPieceBare)
        {
            return isSkull && !wrapped && hasReading && !complete && spawned && everyPieceBare;
        }

        public static ExamineOutcome Examine(bool hasExt, bool hasReading, bool spawned, bool wrapped, bool canOpenLast)
        {
            if (!hasExt || !hasReading || !spawned) return ExamineOutcome.Nothing;
            if (wrapped) return ExamineOutcome.ReadChapter;
            if (canOpenLast) return ExamineOutcome.Complete;
            return ExamineOutcome.Nothing;
        }

        /// <summary>Thrixweave dropped by a read piece: nothing when the setting is not positive.</summary>
        public static int WeaveDropped(int perPiece, bool defKnown) { return defKnown && perPiece > 0 ? perPiece : 0; }

        public static bool ExamineAllowed(bool enabled, bool wrapped, bool canOpenLast)
        {
            return enabled && (wrapped || canOpenLast);
        }

        /// <summary>Chapters are kept once each, in the order the bones tell them; unknown chapters are kept last-in.</summary>
        public static bool RecordChapter(List<string> chapters, string chapter)
        {
            if (!string.IsNullOrEmpty(chapter) && !chapters.Contains(chapter))
            {
                chapters.Add(chapter);
                return true;
            }
            return false;
        }

        public static List<string> Ordered(List<string> chapters)
        {
            var o = new List<string>();
            foreach (string c in ChapterOrder) if (chapters.Contains(c)) o.Add(c);
            return o;
        }

        /// <summary>GenMath.RoundRandom with the random draw passed in: the floor, plus one with probability = the fraction.</summary>
        public static int RoundRandom(float f, float u)
        {
            int n = (int)Math.Floor(f);
            f -= n;
            if (u < f) n++;
            return n;
        }

        public static int CollapseDamage(int roll, float multiplier, float u) { return RoundRandom(roll * multiplier, u); }

        /// <summary>The outline ring: a cell is on it when its normalised ellipse radius is within 0.09 of one.</summary>
        public static bool OutlineCell(int cellX, int cellZ, int rectMinX, int rectMinZ, int rectWidth, int rectHeight)
        {
            float cx = rectMinX + rectWidth / 2f, cz = rectMinZ + rectHeight / 2f;
            float a = rectWidth / 2f + 1f, b = rectHeight / 2f + 1f;
            float dx = (cellX + 0.5f - cx) / a, dz = (cellZ + 0.5f - cz) / b;
            float r = (float)Math.Sqrt(dx * dx + dz * dz);
            return Math.Abs(r - 1f) <= 0.09f;
        }

        /// <summary>A site rectangle must keep the edge margin on every side (max cells inclusive).</summary>
        public static bool SiteInMargin(int minX, int minZ, int maxX, int maxZ, int mapX, int mapZ, int edgeMargin)
        {
            return !(minX < edgeMargin || minZ < edgeMargin || maxX >= mapX - edgeMargin || maxZ >= mapZ - edgeMargin);
        }

        /// <summary>The Mod Settings gate for a new site: enabled, then the chance (Rand.Chance semantics).</summary>
        public static bool RollSite(bool enabled, float chance, float u) { return enabled && Chance(chance, u); }

        /// <summary>Rand.Chance with the draw passed in.</summary>
        public static bool Chance(float p, float u)
        {
            if (p >= 1f) return true;
            if (p <= 0f) return false;
            return u < p;
        }
    }

    /// <summary>The nest wall's egg-clutch relay timer and the nest cluster placement tests.</summary>
    public static class RM_EggRelayKernel
    {
        public const float TicksPerDay = 60000f;
        public const float MinMultiplier = 0.01f;

        public static int IntervalTicks(float days, float multiplier)
        {
            float mult = Math.Max(MinMultiplier, multiplier);
            return Math.Max(1, (int)Math.Round(days * TicksPerDay * mult));
        }

        /// <summary>The comp's rare tick: nothing before the due tick; a map with no mother is a dying nest and keeps its due tick;
        /// otherwise the timer is re-armed whether or not a clutch is laid (no def, or clutches still standing nearby, lay none).</summary>
        public static RelayPlan Plan(int now, int nextRelayTick, bool motherAlive, bool clutchDefKnown, bool clutchNearby)
        {
            if (now < nextRelayTick) return RelayPlan.NotDue;
            if (!motherAlive) return RelayPlan.DyingNest;
            if (!clutchDefKnown || clutchNearby) return RelayPlan.Reschedule;
            return RelayPlan.Place;
        }

        /// <summary>An existing clutch counts as nearby within twice the search radius.</summary>
        public static bool ClutchNearby(int dx, int dz, int searchRadius)
        {
            float radius = searchRadius * 2f;
            float radiusSq = radius * radius;
            return dx * dx + dz * dz <= radiusSq;
        }

        public static bool RingWantsMore(int placed, int wanted) { return placed < wanted; }

        public static bool NeedsFallback(int placed) { return placed == 0; }

        public static bool InBoundsWithMargin(int x, int z, int mapX, int mapZ, int edgeMargin)
        {
            return x >= edgeMargin && z >= edgeMargin && x < mapX - edgeMargin && z < mapZ - edgeMargin;
        }

        /// <summary>A rich-soil centre is preferred; the plain fallback only when none rolled.</summary>
        public static bool RichEnough(float fertility, float threshold) { return fertility >= threshold; }
    }

    /// <summary>The emergent ollathrix spawn gate and the startup scaling the Webwork applies to defs.</summary>
    public static class RM_EmergentKernel
    {
        /// <summary>Fires only on a harvest destruction (Vanish or Deconstruct; the caller decides) on a real map, with the setting on and the (multiplied) chance rolled.</summary>
        public static bool Fires(bool enabled, bool hadMap, bool isVanish, float baseChance, float multiplier, float u)
        {
            if (!enabled) return false;
            if (!hadMap || !isVanish) return false;
            return RM_UrravethKernel.Chance(baseChance * multiplier, u);
        }

        public static int ScaledInterval(int baseTicks, float multiplier) { return (int)(baseTicks * multiplier); }
    }

    /// <summary>Where the Webwork competes during worldgen: a hot, very wet, low band.</summary>
    public static class RM_WebworkBiomeKernel
    {
        public const float TempMin = 30f, TempMax = 60f, RainMin = 1800f;
        public const float MaxElevation = 1000f;
        public const float BaseScore = 28f;
        public const float DegreeWeight = 1.2f;
        public const float RainfallDivisor = 200f;

        public static float Score(bool enabled, bool noTile, bool water, float temperature, float rainfall, float elevation, bool mountainous)
        {
            if (!enabled) return 0f;
            if (noTile || water) return -100f;
            if (temperature < TempMin || temperature > TempMax) return 0f;
            if (rainfall < RainMin) return 0f;
            if (elevation > MaxElevation) return 0f;
            if (mountainous) return 0f;
            return BaseScore
                 + (temperature - TempMin) * DegreeWeight
                 + (rainfall - RainMin) / RainfallDivisor;
        }
    }
}
