// Webwork kernel: the Verse-free decisions of the urraveth remains, the egg-clutch relay, the emergent spawn, the biome score, the web-network layout (RM_WebNetKernel) and
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

    /// <summary>
    /// WEBWORK_TERRAIN_WEATHER_PASS_1: the Verse-free layout of a Webwork map's web. Spider sites (the nest plus a few more), the
    /// cable network between them (a spanning tree plus through-cables edge to edge), each cable rasterised as an
    /// 8-connected sagging line, the silk-carpet disc at each site, and the local-web budget. RM_GenStep_WebworkWeb places
    /// what this plans; the fuzz checks the plan's invariants. Numbers are invented first values (live-balance pass owed).
    /// </summary>
    public static class RM_WebNetKernel
    {
        public const int SiteMargin = 12;
        public const int MinSiteSpacing = 28;
        public const int ExtraSitesMin = 2, ExtraSitesMax = 3;
        public const int CarpetRadiusMin = 4, CarpetRadiusMax = 6;
        public const int ThroughCables = 2;
        public const float StrandsPerCell = 0.004f;
        public const int StrandReach = 3;
        public const float SagMin = 0.03f, SagMax = 0.08f;

        public static bool InMargin(int x, int z, int w, int h, int margin)
        {
            return x >= margin && z >= margin && x < w - margin && z < h - margin;
        }

        public static long Dist2(int ax, int az, int bx, int bz)
        {
            long dx = ax - bx, dz = az - bz;
            return dx * dx + dz * dz;
        }

        public static bool Spaced(int x, int z, List<(int x, int z)> sites, int minSpacing)
        {
            long m = (long)minSpacing * minSpacing;
            foreach (var s in sites) if (Dist2(x, z, s.x, s.z) < m) return false;
            return true;
        }

        /// <summary>The nest first (when there is one), then up to `extra` more sites: inside the margin, spaced from every
        /// earlier site, and accepted by `ok` (the map's standability test). Rejection sampling; may return fewer on a
        /// cramped map, never one that breaks the margin or the spacing.</summary>
        public static List<(int x, int z)> PlanSites((int x, int z)? nest, int w, int h, int extra, Random rng,
            Func<int, int, bool> ok, int attempts = 300)
        {
            var sites = new List<(int x, int z)>();
            if (nest.HasValue) sites.Add(nest.Value);
            if (w <= 2 * SiteMargin || h <= 2 * SiteMargin) return sites;
            int added = 0;
            for (int i = 0; i < attempts && added < extra; i++)
            {
                int x = rng.Next(SiteMargin, w - SiteMargin), z = rng.Next(SiteMargin, h - SiteMargin);
                if (!Spaced(x, z, sites, MinSiteSpacing)) continue;
                if (ok != null && !ok(x, z)) continue;
                sites.Add((x, z));
                added++;
            }
            return sites;
        }

        /// <summary>Prim's minimum spanning tree over the sites: n-1 index pairs joining them all.</summary>
        public static List<(int a, int b)> SpanningEdges(List<(int x, int z)> sites)
        {
            var edges = new List<(int a, int b)>();
            int n = sites.Count;
            if (n < 2) return edges;
            var inTree = new bool[n];
            var best = new long[n];
            var from = new int[n];
            for (int i = 0; i < n; i++) { best[i] = long.MaxValue; from[i] = -1; }
            best[0] = 0;
            for (int k = 0; k < n; k++)
            {
                int u = -1;
                for (int i = 0; i < n; i++) if (!inTree[i] && (u < 0 || best[i] < best[u])) u = i;
                inTree[u] = true;
                if (from[u] >= 0) edges.Add((from[u], u));
                for (int v = 0; v < n; v++)
                {
                    if (inTree[v]) continue;
                    long d = Dist2(sites[u].x, sites[u].z, sites[v].x, sites[v].z);
                    if (d < best[v]) { best[v] = d; from[v] = u; }
                }
            }
            return edges;
        }

        /// <summary>Where a ray from (x,z) along (dx,dz) leaves the map, clamped to the last in-bounds cell.</summary>
        public static (int x, int z) RayToEdge(int x, int z, double dx, double dz, int w, int h)
        {
            double t = double.MaxValue;
            if (dx > 1e-9) t = Math.Min(t, (w - 1 - x) / dx);
            if (dx < -1e-9) t = Math.Min(t, -x / dx);
            if (dz > 1e-9) t = Math.Min(t, (h - 1 - z) / dz);
            if (dz < -1e-9) t = Math.Min(t, -z / dz);
            if (t == double.MaxValue) t = 0;
            int ex = (int)Math.Round(x + dx * t), ez = (int)Math.Round(z + dz * t);
            return (Math.Max(0, Math.Min(w - 1, ex)), Math.Max(0, Math.Min(h - 1, ez)));
        }

        /// <summary>`count` through-cables, each an edge-to-edge line through a site (or the centre when there is none), returned as
        /// two segments that meet at that site.</summary>
        public static List<((int x, int z) a, (int x, int z) b)> ThroughSegments(List<(int x, int z)> sites, int w, int h, int count, Random rng)
        {
            var segs = new List<((int x, int z), (int x, int z))>();
            for (int k = 0; k < count; k++)
            {
                (int x, int z) s = sites.Count > 0 ? sites[rng.Next(sites.Count)] : (w / 2, h / 2);
                double ang = rng.NextDouble() * Math.PI;
                double dx = Math.Cos(ang), dz = Math.Sin(ang);
                segs.Add((RayToEdge(s.x, s.z, dx, dz, w, h), s));
                segs.Add((s, RayToEdge(s.x, s.z, -dx, -dz, w, h)));
            }
            return segs;
        }

        /// <summary>The sag of a cable of this length: a fraction SagMin..SagMax of it, either side (u in [0,1), sign from flip).</summary>
        public static float Sag(int length, double u, bool flip)
        {
            float f = (float)(SagMin + (SagMax - SagMin) * Math.Max(0, Math.Min(1, u)));
            return (flip ? -1f : 1f) * f * length;
        }

        /// <summary>A line from (x0,z0) to (x1,z1) bowed sideways by `sag` cells at its middle (a sine arc), as 8-connected
        /// cells with no repeats, starting at the first point and ending at the second.</summary>
        public static List<(int x, int z)> Raster(int x0, int z0, int x1, int z1, float sag)
        {
            var cells = new List<(int x, int z)>();
            var seen = new HashSet<(int, int)>();
            int n = Math.Max(Math.Abs(x1 - x0), Math.Abs(z1 - z0));
            double len = Math.Sqrt(Dist2(x0, z0, x1, z1));
            double px = len > 0 ? -(z1 - z0) / len : 0, pz = len > 0 ? (x1 - x0) / len : 0;
            (int x, int z) prev = (x0, z0);
            Add(cells, seen, prev);
            int steps = Math.Max(1, n);
            for (int i = 1; i <= steps; i++)
            {
                double t = (double)i / steps;
                double off = (i == steps) ? 0 : sag * Math.Sin(Math.PI * t);
                var c = ((int)Math.Round(x0 + (x1 - x0) * t + px * off), (int)Math.Round(z0 + (z1 - z0) * t + pz * off));
                if (i == steps) c = (x1, z1);
                // bridge any gap so the line stays 8-connected
                while (Math.Max(Math.Abs(c.Item1 - prev.x), Math.Abs(c.Item2 - prev.z)) > 1)
                {
                    prev = (prev.x + Math.Sign(c.Item1 - prev.x), prev.z + Math.Sign(c.Item2 - prev.z));
                    Add(cells, seen, prev);
                }
                prev = c;
                Add(cells, seen, prev);
            }
            return cells;
        }

        private static void Add(List<(int x, int z)> cells, HashSet<(int, int)> seen, (int x, int z) c)
        {
            if (seen.Add((c.x, c.z))) cells.Add(c);
        }

        public static int CarpetRadius(Random rng) { return rng.Next(CarpetRadiusMin, CarpetRadiusMax + 1); }

        /// <summary>Is the cell (dx,dz) from a site of carpet radius r carpeted? Everything within r; a rough rim one cell further
        /// where the cell hash says so; never beyond r+1.</summary>
        public static bool CarpetAt(int dx, int dz, int r, int cellHash)
        {
            long d2 = (long)dx * dx + (long)dz * dz;
            if (d2 <= (long)r * r) return true;
            if (d2 <= (long)(r + 1) * (r + 1)) return (cellHash & 1) == 0;
            return false;
        }

        /// <summary>How many local webs a w x h map gets at this density multiplier (0 or less: none).</summary>
        public static int StrandBudget(int w, int h, float multiplier)
        {
            if (multiplier <= 0f || w <= 0 || h <= 0) return 0;
            return (int)Math.Round((double)w * h * StrandsPerCell * multiplier);
        }

        /// <summary>A strand's offset from its anchor cell: each axis in [-StrandReach, StrandReach], never (0,0).</summary>
        public static (int dx, int dz) StrandOffset(Random rng)
        {
            int dx, dz;
            do { dx = rng.Next(-StrandReach, StrandReach + 1); dz = rng.Next(-StrandReach, StrandReach + 1); } while (dx == 0 && dz == 0);
            return (dx, dz);
        }
    }

    /// <summary>WEBWORK_RESELL (owner, Webwork Q8, 2026-10-22): the rare-trader resale of thrixweave.</summary>
    public static class RM_ThrixweaveResaleKernel
    {
        public const float DefaultChance = 0.25f;
        /// <summary>A trader stocks thrixweave only while the sole-source strip is on (off: vanilla stocking already
        /// sells it), the resale is on, the chance is positive and the roll lands under it.</summary>
        public static bool Stocks(bool stripOn, bool resaleOn, float chance, double roll)
        {
            return stripOn && resaleOn && chance > 0f && roll < chance;
        }
        /// <summary>Units generated: the count rolled by the generator, clamped to [0, stackLimit].</summary>
        public static int Count(int rolled, int stackLimit) { return Math.Max(0, Math.Min(rolled, stackLimit)); }
    }
}
