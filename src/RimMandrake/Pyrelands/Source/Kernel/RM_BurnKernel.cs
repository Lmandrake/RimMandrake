using System;
using System.Collections.Generic;

namespace RimMandrake.Pyrelands
{
    // Verse-free decisions of the Pyrelands burn-line (MapComponent_BurnLine, PyrelandsFireFront) and of the two Tribes incidents
    // that read it (IncidentWorker_FireRaid / IncidentWorker_FlameHarvest / PyrelandsFireRite in mandrake.rut.pyrelandsmechanics):
    // the measurement cadence and centroid, the burn-history ring, the arson-debt book, the standing-burn keep-alive clock, the
    // fire-front clock, the fresh map's opening front and the line geometry, the lawful-cell test, the raid and harvest gates, the raid's goodwill plan, the raid
    // points and the rite's gate / party size. The mods call these with the same expressions; the offline fuzz drives them.

    public enum RM_ReseedDecision { FiresPresent, Quiet, Retry, Reseed }

    public enum RM_FrontAction { Disabled, Armed, Wait, Fire }

    public enum RM_OpeningAction { Done, Skip, Light }

    public enum RM_RaidPlan { Refuse, InsultFirst, RaidNow }

    public enum RM_FollowBurnAction { Stay, GoAnchor, GoNearestAsh }

    public static class RM_BurnKernel
    {
        /// <summary>Maps measure on different ticks: (tick + the map's unique id) on the watch interval.</summary>
        public static bool MeasureDue(int now, int mapId, int intervalTicks)
        {
            return (now + mapId) % intervalTicks == 0;
        }

        /// <summary>Integer centroid (truncating division) of the free-standing fires; false when nothing burns.</summary>
        public static bool Centroid(int sumX, int sumZ, int count, out int cx, out int cz)
        {
            if (count > 0)
            {
                cx = sumX / count;
                cz = sumZ / count;
                return true;
            }
            cx = cz = 0;
            return false;
        }

        public static bool AnyBurn(int fireCount, bool centerValid)
        {
            return fireCount > 0 && centerValid;
        }

        // ------------------------------------------------------------ burn history

        /// <summary>One burn-centre sample per intervalTicks while anything burns; samples older than keepTicks are dropped.</summary>
        public static bool RecordHistory<T>(IList<int> ticks, IList<T> cells, int now, T center, int intervalTicks, int keepTicks)
        {
            if (ticks.Count > 0 && now - ticks[ticks.Count - 1] < intervalTicks)
            {
                return false;
            }
            ticks.Add(now);
            cells.Add(center);
            PruneHistory(ticks, cells, now, keepTicks);
            return true;
        }

        /// <summary>Drop every sample older than keepTicks. BURN_HISTORY_FIX_ANCHOR_NEVER_AGES: run on READ as well as on record, or a
        /// fireless map (no new sample, so no prune) keeps answering an arbitrarily old anchor and herds walk to a burn long gone.
        /// Returns how many samples were dropped.</summary>
        public static int PruneHistory<T>(IList<int> ticks, IList<T> cells, int now, int keepTicks)
        {
            int dropped = 0;
            while (ticks.Count > 0 && now - ticks[0] > keepTicks)
            {
                ticks.RemoveAt(0);
                cells.RemoveAt(0);
                dropped++;
            }
            return dropped;
        }

        /// <summary>Index of the newest sample at least ticksAgo old, else -1. HERD_ANCHOR_FIX_FALLS_BACK_TO_FRESH_ASH: it used to
        /// fall back to the oldest sample, so on a map whose every burn was younger than the lag (the first two days of every fresh
        /// map, the opening front) the ullai anchor was a burn an hour old and the herd walked into fresh ash (bar
        /// ullai_graze_old_burns: "not to fresh ash"). No sample old enough now answers no anchor: the herd stays on ash.</summary>
        public static int HistoryIndexAgo(IList<int> ticks, int now, int ticksAgo)
        {
            int cutoff = now - ticksAgo;
            for (int i = ticks.Count - 1; i >= 0; i--)
            {
                if (ticks[i] <= cutoff)
                {
                    return i;
                }
            }
            return -1;
        }

        /// <summary>BurnCenterAgo's read: prune samples older than keepTicks, then the index of the newest sample at least ticksAgo
        /// old in what is left, else -1 (BURN_HISTORY_FIX_ANCHOR_NEVER_AGES and HistoryIndexAgo above).</summary>
        public static int IndexAgoPruned<T>(IList<int> ticks, IList<T> cells, int now, int keepTicks, int ticksAgo)
        {
            PruneHistory(ticks, cells, now, keepTicks);
            return HistoryIndexAgo(ticks, now, ticksAgo);
        }

        /// <summary>ProbeBurnHistory's read: IndexAgoPruned, then the summary of what is left. Every count and index is read AFTER
        /// the prune (RIMMANDRAKE_FIX_PYRE_BURN_HISTORY_PROBE_COUNTS_BEFORE_IT_PRUNES: the probe read the count first and indexed
        /// [n - 1] past the end once the prune had shortened the lists). Empty: samples 0, ticks -1, newestAt -1. Returns agoAt.</summary>
        public static int ProbeHistory<T>(IList<int> ticks, IList<T> cells, int now, int keepTicks, int ticksAgo,
            out int samples, out int oldestTick, out int newestTick, out int newestAt)
        {
            int agoAt = IndexAgoPruned(ticks, cells, now, keepTicks, ticksAgo);
            samples = ticks.Count;
            newestAt = samples - 1;
            oldestTick = samples > 0 ? ticks[0] : -1;
            newestTick = samples > 0 ? ticks[newestAt] : -1;
            return agoAt;
        }

        /// <summary>RM_JobGiver_FollowBurn's decision once its chance roll has passed (PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER): with a burn
        /// record (the anchor = HistoryIndexAgo's sample about lagDays old) a herd member on ash within settle+radius of it stays, any
        /// other walks to the anchor; with no record it stays on ash or drifts to the nearest ash. distToAnchor is horizontal distance
        /// (IntVec3.InHorDistOf: within means &lt;=).</summary>
        public static RM_FollowBurnAction FollowBurnDecision(bool anchorValid, bool onAsh, float distToAnchor, float settleRadius, float radius)
        {
            if (anchorValid)
            {
                return onAsh && distToAnchor <= settleRadius + radius ? RM_FollowBurnAction.Stay : RM_FollowBurnAction.GoAnchor;
            }
            return onAsh ? RM_FollowBurnAction.Stay : RM_FollowBurnAction.GoNearestAsh;
        }

        /// <summary>Test drive only: every history sample made `ticks` older (the compressed two-day lag). Returns the samples shifted.</summary>
        public static int BackdateHistory(IList<int> ticks, int byTicks)
        {
            for (int i = 0; i < ticks.Count; i++)
            {
                ticks[i] -= byTicks;
            }
            return ticks.Count;
        }

        // ------------------------------------------------------------ arson debt

        /// <summary>A fire counts against the colony when something lit it and that thing's faction is the player's.</summary>
        public static bool PlayerAttributed(bool hasInstigator, bool instigatorHasFaction, bool factionIsPlayer)
        {
            return hasInstigator && instigatorHasFaction && factionIsPlayer;
        }

        /// <summary>One watch interval of the debt: player-attributed free fires add (to the cap), otherwise it decays toward 0.</summary>
        public static float ArsonStep(float debt, int playerFires, float perFirePerCheck, float cap, float decayPerCheck)
        {
            if (playerFires > 0)
            {
                return Math.Min(cap, debt + playerFires * perFirePerCheck);
            }
            if (debt > 0f)
            {
                return Math.Max(0f, debt - decayPerCheck);
            }
            return debt;
        }

        /// <summary>The debt can never exceed the cap, so a raid threshold above it would never be reached: it counts as the cap.</summary>
        public static float EffectiveRaidThreshold(float threshold, float cap)
        {
            return Math.Min(threshold, cap);
        }

        // ------------------------------------------------------------ standing burn keep-alive

        /// <summary>The biome keeps one burn alive: after quietTicks with no fire it tries to light one, at most once per retryTicks.</summary>
        public static RM_ReseedDecision KeepAlive(int fireCount, ref int ticksSinceAnyFire, int intervalTicks, int quietTicks, int now,
            int lastAttemptTick, int retryTicks)
        {
            if (fireCount > 0)
            {
                ticksSinceAnyFire = 0;
                return RM_ReseedDecision.FiresPresent;
            }
            ticksSinceAnyFire += intervalTicks;
            if (ticksSinceAnyFire < quietTicks)
            {
                return RM_ReseedDecision.Quiet;
            }
            if (now - lastAttemptTick < retryTicks)
            {
                return RM_ReseedDecision.Retry;
            }
            return RM_ReseedDecision.Reseed;
        }

        /// <summary>Where the BIOME may light: in bounds, unfogged, unroofed, able to take fire, outside home, far from the colony.</summary>
        public static bool LawfulBurnCell(bool inBounds, bool fogged, bool roofed, float chanceToStartFire, bool inHomeArea, bool farFromColony)
        {
            if (!inBounds || fogged || roofed)
            {
                return false;
            }
            if (chanceToStartFire <= 0f)
            {
                return false;
            }
            if (inHomeArea)
            {
                return false;
            }
            return farFromColony;
        }

        public static bool TooCloseToColony(int distSq, float minDistFromColony)
        {
            return distSq < minDistFromColony * minDistFromColony;
        }

        // ------------------------------------------------------------ fire front clock and geometry

        /// <summary>Days until the next front: uniform in [minDays, maxDays] (roll01 is the 0..1 roll).</summary>
        public static int ScheduleTicks(float minDays, float maxDays, float roll01, int ticksPerDay)
        {
            float days = minDays + roll01 * (maxDays - minDays);
            return (int)Math.Round(days * ticksPerDay);
        }

        /// <summary>The fire clock. Off re-arms from now (so switching it on never fires a months-overdue timer); unarmed arms; due fires
        /// and re-arms. schedule() is called only when the clock arms.</summary>
        public static RM_FrontAction FrontTick(ref int nextFrontTick, int now, bool enabled, Func<int> schedule)
        {
            if (!enabled)
            {
                nextFrontTick = -1;
                return RM_FrontAction.Disabled;
            }
            if (nextFrontTick < 0)
            {
                nextFrontTick = now + schedule();
                return RM_FrontAction.Armed;
            }
            if (now < nextFrontTick)
            {
                return RM_FrontAction.Wait;
            }
            nextFrontTick = now + schedule();
            return RM_FrontAction.Fire;
        }

        /// <summary>PYRE_OPENING_FRONT: the opening front of a fresh map. Done stays done; the fire clock off, or a map older than
        /// the window (no longer fresh), drops it for good (Skip: the caller marks it done, so switching the clock on later never
        /// lights a late "opening"); otherwise Light (the caller marks it done only once a cell took, so it retries each watch
        /// interval inside the window). ageTicks is ticks since map generation (or since a test re-arm).</summary>
        public static RM_OpeningAction OpeningFront(bool done, bool enabled, int ageTicks, int windowTicks)
        {
            if (done)
            {
                return RM_OpeningAction.Done;
            }
            if (!enabled || ageTicks > windowTicks)
            {
                return RM_OpeningAction.Skip;
            }
            return RM_OpeningAction.Light;
        }

        /// <summary>Offsets of a front line of exactly `width` cells through the origin at a bearing (degrees): one cell per step along the
        /// dominant axis, the other axis rounded, so every cell is distinct and 8-adjacent to the next at any angle (a unit EUCLIDEAN
        /// step truncated to cells folded a diagonal 9-wide front onto about 5 cells).</summary>
        public static void FrontLine(float angleDeg, int width, out int[] dx, out int[] dz)
        {
            int half = width / 2;
            dx = new int[Math.Max(0, width)];
            dz = new int[Math.Max(0, width)];
            double rad = angleDeg * Math.PI / 180.0;
            double sx = Math.Sin(rad), sz = Math.Cos(rad);
            double m = Math.Max(Math.Abs(sx), Math.Abs(sz));
            if (m < 1e-9)
            {
                sx = 0.0;
                sz = 1.0;
                m = 1.0;
            }
            double ux = sx / m, uz = sz / m;
            int n = 0;
            for (int i = -half; i < width - half; i++)
            {
                dx[n] = (int)Math.Round(ux * i, MidpointRounding.AwayFromZero);
                dz[n] = (int)Math.Round(uz * i, MidpointRounding.AwayFromZero);
                n++;
            }
        }

        // ------------------------------------------------------------ yesterday's fire (PYRE_OPENING_FRONT, 2026-11-07)
        // A fresh map showed no burn line at all on arrival (map s): a 5-cell opening line lit in thick grass reads as a camp
        // fire, not a front. The map now starts with a half-disc scar on one edge, burned from the edge inward, and the
        // opening front lights along its ragged leading arc (PyrelandsYesterdayFire).

        /// <summary>The scar's nominal radius: the rolled radius, shrunk so its farthest ragged reach stays minFrontDist from
        /// the nearest reference point (map centre, landing spot); 0 when that leaves less than floorRadius (a small map).</summary>
        public static float ScarRadius(float rolled, float clearance, float minFrontDist, float ragged, float floorRadius)
        {
            float room = (clearance - minFrontDist) / (1f + Math.Max(0f, ragged));
            float r = Math.Min(rolled, room);
            return r >= floorRadius && r > 0f ? r : 0f;
        }

        /// <summary>The scar's edge radius at one bearing: the nominal radius pushed out or in by up to `ragged` of itself by the
        /// bearing's noise (clamped to -1..1), so the boundary is one ragged line with no islands.</summary>
        public static float ScarBoundary(float radius, float noise, float ragged)
        {
            float n = noise < -1f ? -1f : noise > 1f ? 1f : noise;
            return Math.Max(0f, radius * (1f + ragged * n));
        }

        /// <summary>The burn stamp of a scar cell `depth01` of the way from the map edge (0, burned first) to the front (1, burned
        /// last): the age runs from oldestAge down to youngestAge. Clamped at tick 0, so a new game's scar reads as burned at the
        /// start (a stamp is a game tick and BurnBonus reads a negative one as never burned); a later map gets the gradient.</summary>
        public static int ScarStampTick(int now, float depth01, int oldestAge, int youngestAge)
        {
            float t = depth01 < 0f ? 0f : depth01 > 1f ? 1f : depth01;
            int age = (int)Math.Round(oldestAge + (youngestAge - oldestAge) * t);
            return Math.Max(0, now - Math.Max(0, age));
        }

        /// <summary>A cell on the leading arc, not the flanks: its bearing from the scar centre lies within the cone around the
        /// inward normal (nx, nz) whose half-angle has cosine minCos. The centre cell itself is not on any arc.</summary>
        public static bool ArcFacing(float dx, float dz, float nx, float nz, float minCos)
        {
            double len = Math.Sqrt((double)dx * dx + (double)dz * dz);
            if (len < 1e-6) return false;
            return (dx * nx + dz * nz) / len >= minCos;
        }

        /// <summary>Every how-many'th arc cell (sorted by bearing) gets a fire: at least minStride, and wider when the arc holds
        /// more than cap cells, so the line reads as a line without lighting every cell or more than cap.</summary>
        public static int ArcStride(int candidates, int cap, int minStride)
        {
            int s = Math.Max(1, minStride);
            if (cap > 0 && candidates > cap * s)
            {
                s = (candidates + cap - 1) / cap;
            }
            return s;
        }

        /// <summary>A scar site is worth burning when at least minShare of its sampled cells can burn (not rock, roof or water).</summary>
        public static bool ScarSiteUsable(int burnable, int sampled, float minShare)
        {
            return sampled > 0 && burnable >= minShare * sampled;
        }

        /// <summary>A scar site on map edge `edge` (0 north, 1 east, 2 south, 3 west: CompassIndex / 2) `along01` of the way along
        /// it (west to east, south to north): the centre cell on the edge row or column, and the inward normal pointing into the map.</summary>
        public static void ScarEdgeFrame(int edge, float along01, int sizeX, int sizeZ, out int cx, out int cz, out int nx, out int nz)
        {
            float a = along01 < 0f ? 0f : along01 > 1f ? 1f : along01;
            int ax = Math.Max(0, Math.Min(sizeX - 1, (int)Math.Round(a * (sizeX - 1))));
            int az = Math.Max(0, Math.Min(sizeZ - 1, (int)Math.Round(a * (sizeZ - 1))));
            switch (edge & 3)
            {
                case 0: cx = ax; cz = sizeZ - 1; nx = 0; nz = -1; break;
                case 1: cx = sizeX - 1; cz = az; nx = -1; nz = 0; break;
                case 2: cx = ax; cz = 0; nx = 0; nz = 1; break;
                default: cx = 0; cz = az; nx = 1; nz = 0; break;
            }
        }

        /// <summary>A cell's bearing from the scar centre, in radians off the inward normal (nx, nz): 0 straight in, +-pi/2 along
        /// the map edge. The ragged edge's noise is read at this bearing times the radius (arc length), so it is one line.</summary>
        public static float ScarBearing(float dx, float dz, float nx, float nz)
        {
            return (float)Math.Atan2(nx * dz - nz * dx, dx * nx + dz * nz);
        }

        /// <summary>The chance a scar cell `depth01` from the edge has re-sprouted: edgeChance where the fire started, falling
        /// straight to 0 at endDepth, and 0 beyond it (the young char right behind the front).</summary>
        public static float ScarSproutChance(float depth01, float edgeChance, float endDepth)
        {
            if (endDepth <= 0f || edgeChance <= 0f) return 0f;
            float d = depth01 < 0f ? 0f : depth01;
            return d >= endDepth ? 0f : edgeChance * (1f - d / endDepth);
        }

        // ------------------------------------------------------------ the Tribes' incidents

        /// <summary>The switches every Tribes incident that answers the burn obeys (FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH): its own
        /// toggle, the mechanics gate, the burn line it reads (frozen when off) and the "Fire clock" setting, whose tooltip promises
        /// flame harvest, fire raid and fire rite never fire when it is off.</summary>
        /// <summary>Warn about the burn nearing home: inside the range, not already on it, and not warned lately.</summary>
        public static bool ApproachWarnDue(int nearestCells, int warnCells, int now, int lastWarnTick, int cooldownTicks)
        {
            return nearestCells > 0 && nearestCells <= warnCells && now - lastWarnTick >= cooldownTicks;
        }

        /// <summary>Which of the 8 compass words (0 north, clockwise) lies from home toward the fire; z grows north.</summary>
        public static int CompassIndex(int dx, int dz)
        {
            if (dx == 0 && dz == 0) return 0;
            double deg = System.Math.Atan2(dx, dz) * 180.0 / System.Math.PI;
            if (deg < 0) deg += 360.0;
            return (int)((deg + 22.5) / 45.0) % 8;
        }

        public static bool TribesIncidentSwitchesOn(bool ownEnabled, bool mechanicsGateOn, bool burnLineEnabled, bool fireClockEnabled)
        {
            return ownEnabled && mechanicsGateOn && burnLineEnabled && fireClockEnabled;
        }

        /// <summary>IncidentWorker_FireRaid.CanFireNowSub after the base checks: enabled, a Pyrelands watch, debt at the (capped) threshold, a
        /// Tribes faction that is already hostile or could be soured.</summary>
        public static bool RaidCanFire(bool enabled, bool baseCan, bool pyrelandsWatch, float debt, float threshold, float cap,
            bool tribesPresent, bool hostile, bool hasGoodwill)
        {
            if (!enabled || !baseCan || !pyrelandsWatch)
            {
                return false;
            }
            if (debt < EffectiveRaidThreshold(threshold, cap))
            {
                return false;
            }
            if (!tribesPresent)
            {
                return false;
            }
            return hostile || hasGoodwill;
        }

        /// <summary>TryExecuteWorker, first half: no Tribes or no way to turn them hostile refuses; already hostile raids; otherwise the
        /// goodwill hit comes first.</summary>
        public static RM_RaidPlan RaidPlan(bool tribesPresent, bool hostile, bool hasGoodwill)
        {
            if (!tribesPresent)
            {
                return RM_RaidPlan.Refuse;
            }
            if (hostile)
            {
                return RM_RaidPlan.RaidNow;
            }
            return hasGoodwill ? RM_RaidPlan.InsultFirst : RM_RaidPlan.Refuse;
        }

        /// <summary>After the insult: only a faction that is now hostile raids; otherwise the debt stands for the next burn.</summary>
        public static bool RaidAfterInsult(bool hostileNow)
        {
            return hostileNow;
        }

        /// <summary>The raid is a fraction of the storyteller's points (with a floor); an unset budget takes the default threat points.</summary>
        public static float RaidPoints(float points, float defaultPoints, float factor, float minPoints)
        {
            if (points <= 0f)
            {
                points = defaultPoints;
            }
            return Math.Max(minPoints, points * factor);
        }

        /// <summary>IncidentWorker_FlameHarvest.CanFireNowSub after the base checks: a burning Pyrelands map with enough fires and a
        /// Tribes faction that is not hostile.</summary>
        public static bool HarvestCanFire(bool enabled, bool baseCan, bool pyrelandsWatch, bool anyBurn, int fireCount, int minFires,
            bool tribesPresent, bool hostile)
        {
            if (!enabled || !baseCan || !pyrelandsWatch)
            {
                return false;
            }
            if (!anyBurn || fireCount < minFires)
            {
                return false;
            }
            return tribesPresent && !hostile;
        }

        /// <summary>PyrelandsFireRite.TrySend gate: the rite is on and the roll lands under the fraction.</summary>
        public static bool RiteRoll(bool enabled, float roll01, float fraction)
        {
            return enabled && !(roll01 >= fraction);
        }

        /// <summary>Rite party size: a max below the min is raised to the min.</summary>
        public static void RitePartyRange(int min, int max, out int lo, out int hi)
        {
            lo = min;
            hi = max < min ? min : max;
        }

        /// <summary>RITE_HARVEST_FIX_PICKS_PAST_FULL: how much more scorch-fruit one rite harvester wants. At or below 0 it is full and
        /// neither picks up nor cuts another pod (a cut pod it will not carry is left to spoil).</summary>
        public static int RiteHarvestWanted(int carryPerPawn, int carried)
        {
            return carryPerPawn - carried;
        }

        /// <summary>RITE_HARVEST_FIX_PICKS_PAST_FULL: a pod or loose fruit is in the rite's range when it lies within the radius of the
        /// rite's ORIGIN (the duty focus), never of the harvester, so the range cannot chain across the map.</summary>
        public static bool RiteHarvestInRange(int dxFromOrigin, int dzFromOrigin, float radius)
        {
            return radius > 0f && (float)dxFromOrigin * dxFromOrigin + (float)dzFromOrigin * dzFromOrigin <= radius * radius;
        }

        public static int RiteHarvestTicks(float hours, float ticksPerHour)
        {
            return Math.Max(1, (int)Math.Round(hours * ticksPerHour));
        }

        // ------------------------------------------------------------ the wind carries the fire
        // RIMMANDRAKE_RESCUE_PYRELANDS_BLACK_RAIN_DOUSES_NEEDED_FIRE (2026-11-16). Vanilla fire spreads evenly to all eight
        // neighbours, so a fire in the grass carpet is a ring, not a line: in the visit-1 walk saves one opening front burned
        // 78% of a 250 x 250 map in 4 days and the map burned again in week 2 (bar burn_line_walks: "a line of grass fire
        // walking ... It must not read as a scattered wildfire"; bar grass_carpets_and_regreens: "no bare-dirt expanses").
        // On Pyrelands ground the wind carries the fire instead: each fire lights at most ONE cell, downwind, once. A burn
        // then keeps near the width it was lit with (FlankPlan below lets its flanks wander), and no fire makes two downwind. The whole-map model that checks it:
        // src/RimMandrake/Pyrelands/pyre_burn_sim.py (selftest_pyrelands_burn_ecology.py).

        /// <summary>The eight compass steps clockwise from north (+z): N, NE, E, SE, S, SW, W, NW.</summary>
        public static readonly int[] Dir8X = { 0, 1, 1, 1, 0, -1, -1, -1 };
        public static readonly int[] Dir8Z = { 1, 1, 0, -1, -1, -1, 0, 1 };

        /// <summary>The least ticks after it is lit that a fire is carried on (CarryAge adds up to WindCarryExtraTicks). Vanilla's
        /// own pace: a 0.1 fire on ember grass (Flammability 1.6, +0.132 a 150-tick beat) passes size 1 on its 7th beat (1,050
        /// ticks) and vanilla spreads within one more interval.</summary>
        public const int WindCarryTicks = 1200;

        /// <summary>The most the ground slows a carry. With WindCarryTicks the mean is 1,400 ticks a cell, 43 cells a day, the pace
        /// the walk saves measured; the longest, 1,600, stays under an ember-grass fire's life (28 HP: 12 to 13 beats, 1,800).</summary>
        public const int WindCarryExtraTicks = 400;

        /// <summary>How far downwind a spark is tried when the next cell is bare. Bar burn_line_walks ("never out for long"): a
        /// line must cross thin grass. 2 is vanilla's own spark reach (GenRadial.ManualRadialPattern[10..20], two cells out).</summary>
        public const int WindCarryReach = 2;

        /// <summary>The cells a fire tries, in order, when the wind (blowing TOWARD bearingDeg, 0 = north, clockwise) carries it
        /// on: the compass step nearest the bearing and its neighbour on the side the bearing leans to (that neighbour first
        /// with chance = the lean over 45 degrees, so the mean heading is the wind), then the neighbour on the other side; then
        /// the same three one cell further, out to `reach`. Never sideways, never back. dx and dz hold 3 x reach offsets.
        /// roll2 only settles which side "leans" when the bearing sits exactly on a compass step.</summary>
        public static void WindProbes(float bearingDeg, float roll01, float roll2, int reach, int[] dx, int[] dz)
        {
            double b = bearingDeg % 360.0;
            if (b < 0) b += 360.0;
            double steps = Math.Floor(b / 45.0 + 0.5);
            int n = (int)steps % 8;
            double delta = b - 45.0 * steps;                    // -22.5 .. 22.5
            int side = delta > 0 ? 1 : delta < 0 ? -1 : (roll2 < 0.5f ? 1 : -1);
            int lean = (n + side + 8) % 8, far = (n - side + 8) % 8;
            bool leanFirst = roll01 < Math.Abs(delta) / 45.0;
            int first = leanFirst ? lean : n, second = leanFirst ? n : lean;
            int k = 0;
            for (int d = 1; d <= reach; d++)
            {
                dx[k] = Dir8X[first] * d; dz[k++] = Dir8Z[first] * d;
                dx[k] = Dir8X[second] * d; dz[k++] = Dir8Z[second] * d;
                dx[k] = Dir8X[far] * d; dz[k++] = Dir8Z[far] * d;
            }
        }

        // ------------------------------------------------------------ a line closes its own gaps
        // RIMMANDRAKE_WIDEN_PYRE_FIRE_TRAILS_RUN_AS_RULER_STRAIGHT_LANES (Pyrelands visit 5, 2026-11-22): the scar's arc lights every
        // 3rd or 4th cell (ArcStride), and each fire carried one cell downwind and never aside, so the burn walked as one-cell lanes
        // with grass standing between them for good, ruler-straight under a wind on a compass step (bar burn_line_walks: "a natural
        // grass fire"). Two rules close the gaps and keep the line no wider than it was lit:
        //   merge: a probe that holds a fire already ends the carry with nothing lit; the lane runs on in that fire. Without it a
        //          gap cell lit beside a lane shoves every lane beside it one cell out, and the flank creeps at 45 degrees (a flood:
        //          the model burned 10,600 cells against 1,440 in a day);
        //   heal:  the carried fire lights one more cell beside its new cell, only into a gap that another lane or a recent burn
        //          closes within HealReach. Its own trail never lies on those rays, so the outermost lane never heals outward.
        // A sideways wobble of the carry was tried and dropped (measured 2026-11-22): the flanks diffuse, and the 9-cell scene of
        // bar fire_walks_with_wind put a fire in its outer lanes on 1 to 2 of 40 seeds. Model: pyre_burn_sim.carry_plan (the
        // fuzz's CarryPlanChecksum ties the two); check: selftest_pyrelands_burn_front_lanes.py.

        /// <summary>How far across a carried fire looks for the lane that closes a gap. The widest gap a lit line leaves: the
        /// scar's arc at its largest (radius 50 pushed out by YesterdayFireRagged 0.22, about 165 arc cells over the cap of 32 fires,
        /// measured on the model's arc) lights every 6th cell, 5 cells between fires.</summary>
        public const int HealReach = 5;

        /// <summary>How lately a cell must have burned to close a gap: one day. The lanes of one line pass a row at different
        /// times: the arc's flank lanes start up to r (1 - cos 60) = 25 rows behind its middle, 25 carries x 1,200 ticks =
        /// 30,000 ticks. A day covers that twice and stays under FireFrontMinDays (2), so a finished front's trail is not
        /// taken for this one's.</summary>
        public const int HealRecentTicks = 60000;

        public enum RM_CarryCell { Bare, Fuel, Burning }

        /// <summary>A cell closes a gap: a fire burns on it, or it burned within windowTicks (burnTick -1 = never).</summary>
        public static bool RecentBurn(bool burning, int burnTick, int now, int windowTicks)
        {
            return burning || (burnTick >= 0 && now - burnTick <= windowTicks);
        }

        /// <summary>The four steps a carried fire looks along for a gap in its own line, from the compass step nearest the
        /// bearing: the two at 90 degrees (beside), then the two at 135 degrees (beside and behind: they close the checkerboard
        /// a line lit across a diagonal wind leaves). rollSide picks which side comes first.</summary>
        public static void HealDirs(float bearingDeg, float rollSide, int[] dx, int[] dz)
        {
            double b = bearingDeg % 360.0;
            if (b < 0) b += 360.0;
            int n = (int)Math.Floor(b / 45.0 + 0.5) % 8;
            int s1 = rollSide < 0.5f ? 1 : -1, s2 = -s1;
            int[] dirs = { (n + 2 * s1 + 8) % 8, (n + 2 * s2 + 8) % 8, (n + 3 * s1 + 8) % 8, (n + 3 * s2 + 8) % 8 };
            for (int i = 0; i < 4; i++)
            {
                dx[i] = Dir8X[dirs[i]];
                dz[i] = Dir8Z[dirs[i]];
            }
        }

        /// <summary>The cells one carried fire lights, as offsets from it, written to outX/outZ (room for 2); returns how many.
        /// cell(dx, dz) says what lies there; anchor(dx, dz) is RecentBurn there. 1. Carry: the first WindProbes cell that holds
        /// Fuel; a probe that holds a fire ends the carry with nothing lit (merge). 2. Heal: from that cell T, the first HealDirs
        /// step s whose cell T+s holds Fuel and whose ray T+k*s, k = 2 .. healReach + 1, meets an anchor: that gap cell too
        /// (healed = true). The ray passes bare cells, as the carry's own reach does: a ray stopped at the first bare cell left
        /// 0.38 of a 70%-cover burn in one-cell strands against vanilla's own fire's 0.23; passing them, 0.27.</summary>
        public static int CarryPlan(float bearingDeg, float roll01, float roll2, float rollSide, int reach, int healReach,
            Func<int, int, RM_CarryCell> cell, Func<int, int, bool> anchor, int[] outX, int[] outZ, out bool healed)
        {
            healed = false;
            int[] px = new int[3 * reach], pz = new int[3 * reach];
            WindProbes(bearingDeg, roll01, roll2, reach, px, pz);
            int n = 0;
            for (int i = 0; i < px.Length; i++)
            {
                RM_CarryCell st = cell(px[i], pz[i]);
                if (st == RM_CarryCell.Burning) break;
                if (st == RM_CarryCell.Fuel)
                {
                    outX[0] = px[i];
                    outZ[0] = pz[i];
                    n = 1;
                    break;
                }
            }
            if (n == 0 || healReach <= 0) return n;
            int tx = outX[0], tz = outZ[0];
            int[] hx = new int[4], hz = new int[4];
            HealDirs(bearingDeg, rollSide, hx, hz);
            for (int d = 0; d < 4; d++)
            {
                if (cell(tx + hx[d], tz + hz[d]) != RM_CarryCell.Fuel) continue;
                for (int k = 2; k <= healReach + 1; k++)
                {
                    int ax = tx + k * hx[d], az = tz + k * hz[d];
                    if (anchor(ax, az))
                    {
                        outX[1] = tx + hx[d];
                        outZ[1] = tz + hz[d];
                        healed = true;
                        return 2;
                    }
                }
            }
            return 1;
        }

        // ------------------------------------------------------------ a burn's edges are the ground's
        // RIMMANDRAKE_WIDEN_PYRE_LONE_FIRE_INTO_A_FRONT (Pyrelands visit 7, 2026-11-23): under the carry alone a burn keeps the width it
        // was lit with and every fire carries at one age, so a lone fire walked as a one-cell lane 20-27 cells long, and a front ran
        // as a flat-sided band with a ruler-straight head (bar burn_line_walks: "like a natural grass fire"). Two rules, both read
        // from a smooth noise of the ground (no state to save; one field per map):
        //   CarryAge:  the ground's noise slows the carry, so a head runs ahead here and lags there;
        //   FlankPlan: the outermost fire of a burn opens one cell aside, or is not carried on. The odds lean with the burn's own
        //              width: a lone fire fans out into a front, a front wanders in and out, and none floods.
        // Refuted on the way (measured 2026-11-23 in the model): one lean roll for a whole row (more strands, not fewer); the width
        // read in the fire's own row only (the foremost tip of a ragged head took itself for a lone fire, and the burn widened 70
        // cells crossing a map). Model: pyre_burn_sim.flank_plan, carry_extra (the fuzz's FlankPlanChecksum ties them); check:
        // selftest_pyrelands_burn_front_lanes.py.

        /// <summary>The live width at which a flank opens and closes evenly. The model's sweep holds every other row from 10 to 14; of
        /// those 10 has the fewest fires, so it calls down the fewest black rains (48 maps, 40 days: 7.4 a map, 8.2 to 8.6 at
        /// 12 and 14, 5.5 under the carry alone, 16 under vanilla's spread on 24 of them) and the most room under the
        /// 27-fire limit of fire_walks_with_wind's scene (24).</summary>
        public const int FlankWidth = 10;

        /// <summary>The lean's ceiling, of 1024 (512 is even). Above 512 a burn wider than FlankWidth closes a little more often
        /// than it opens, so the mod's own 24-cell front ends no wider than under the carry alone.</summary>
        public const int FlankLeanCap = 576;

        /// <summary>A burn this narrow opens in any row and never closes: a lone fire fans out at once. Under the 9-cell line of bar
        /// fire_walks_with_wind, whose outer lanes must hold no fire.</summary>
        public const int FlankNarrow = 8;

        /// <summary>One row in this many may change a flank: it leaves the wind by one cell in four. At three, the 9-cell scene of
        /// bar fire_walks_with_wind put a fire in its outer lanes on 2 of 500 runs; at four on none.</summary>
        public const int FlankRows = 4;

        /// <summary>Rows ahead of and behind the fire in which its burn's width is read. A head is ragged by a few rows and the
        /// scar's arc by more; at 8 an arc's end still took itself for a lone fire, at 10 not (both read before the width was read from live fire).</summary>
        public const int FlankLook = 10;

        /// <summary>Rows ahead and behind in which burn on a side means this fire is not the outermost one there.</summary>
        public const int FlankBeside = 2;

        /// <summary>Of the 5 cells ahead of and beyond the one it opens into, this many must hold fuel: a burn fans out in grass
        /// and not in the thin regrowth of a fresh scar (a line dies there, as under the carry alone).</summary>
        public const int FlankFuel = 2;

        /// <summary>Cells between the points of the flanks' noise: a flank bends every few cells. The model's sweep held from 4 to 10
        /// (the longer, the straighter the edge).</summary>
        public const int FlankPatch = 5;

        /// <summary>Cells between the points of the pace's noise. At 10 a 60-cell head stood straight for 20 lanes, at 8 for 11.</summary>
        public const int PacePatch = 8;

        private static int FloorDiv(int a, int b)
        {
            int q = a / b;
            return a % b != 0 && (a < 0) != (b < 0) ? q - 1 : q;
        }

        /// <summary>0 .. 1023 from a point of the ground; wraps at 32 bits (the model computes the same).</summary>
        public static int GroundHash(int ix, int iz, int seed)
        {
            unchecked
            {
                uint h = (uint)ix * 374761393u + (uint)iz * 668265263u + (uint)seed * 1274126177u;
                h = (h ^ (h >> 13)) * 1274126177u;
                return (int)((h ^ (h >> 16)) >> 22);
            }
        }

        /// <summary>Smooth noise of the ground, 0 .. 1023: bilinear between hashed points `patch` cells apart.</summary>
        public static int GroundNoise(int x, int z, int seed, int patch)
        {
            int ix = FloorDiv(x, patch), iz = FloorDiv(z, patch);
            int fx = x - ix * patch, fz = z - iz * patch;
            int a = GroundHash(ix, iz, seed), b = GroundHash(ix + 1, iz, seed);
            int c = GroundHash(ix, iz + 1, seed), d = GroundHash(ix + 1, iz + 1, seed);
            return ((a * (patch - fx) + b * fx) * (patch - fz) + (c * (patch - fx) + d * fx) * fz) / (patch * patch);
        }

        /// <summary>A plant with this many hit points or fewer may not outlive the fire's next beat: Fire.DoFireDamage at full size
        /// (1.75) deals (0.0125 + 0.0036 x 1.75) x 150 = 2.8, rounded at random to 2 or 3.</summary>
        public const int FuelSpentHp = 3;

        /// <summary>Ticks after it is lit that a fire on this cell is carried on: WindCarryTicks plus what the ground slows it. A fire
        /// whose plant is nearly spent does not wait for the ground: a lightning strike's flame burst takes 10 of the 28 hit points of
        /// the grass it lights, and that grass is gone before the slowest carry. fuelHp 0: the plant is gone, or none burns here.</summary>
        public static int CarryAge(int x, int z, int seed, int fuelHp)
        {
            if (fuelHp <= FuelSpentHp) return WindCarryTicks;
            int v = Math.Max(0, Math.Min(1023, 512 + (GroundNoise(x, z, unchecked(seed + 7), PacePatch) - 512) * 2));
            return WindCarryTicks + v * WindCarryExtraTicks / 1024;
        }

        private static bool LiveNear(Func<int, int, RM_CarryCell> cell, int ax, int az, int nx, int nz, int rows)
        {
            for (int j = -rows; j <= rows; j++)
            {
                if (cell(ax - nx * j, az - nz * j) == RM_CarryCell.Burning) return true;
            }
            return false;
        }

        private static bool AnchorNear(Func<int, int, bool> anchor, int ax, int az, int nx, int nz, int rows)
        {
            for (int j = -rows; j <= rows; j++)
            {
                if (anchor(ax - nx * j, az - nz * j)) return true;
            }
            return false;
        }

        /// <summary>What the outermost fire of a burn does at its flank, after CarryPlan (n cells planned in outX/outZ, healed). (x, z)
        /// is the fire's own cell. Returns the new count: n, or n + 1 = 2 (the burn opens one cell beside the carried one), or 0 (the
        /// flank closes: this fire is not carried on).
        /// 1. The burn's width here: 1 + how far LIVE fire runs to each side of this fire, gaps up to healReach passed, read within
        ///    FlankLook rows (read from burned ground too, the last lane past a lake took itself for a wide front and was put out). 2. One row in FlankRows may change the flank (every row while the burn is FlankNarrow or less).
        /// 3. On a side with no burn beside: the ground's noise against a lean that grows with the width. It closes only where the
        ///    burn goes on without it: over half of the FlankNarrow lanes inward hold fuel, fire or fresh burn in the next two rows
        ///    (at a lake's edge, the lanes beside it are ending). 4. It opens only into
        ///    grass (FlankFuel).</summary>
        public static int FlankPlan(float bearingDeg, float rollSide, int x, int z, int seed, int healReach,
            Func<int, int, RM_CarryCell> cell, Func<int, int, bool> anchor, int[] outX, int[] outZ, int n, bool healed)
        {
            if (healReach <= 0) return n;
            double b = bearingDeg % 360.0;
            if (b < 0) b += 360.0;
            int step = (int)Math.Floor(b / 45.0 + 0.5) % 8;
            int nx = Dir8X[step], nz = Dir8Z[step];
            int s1 = rollSide < 0.5f ? 2 : -2;
            int width = 1;
            for (int side = 0; side < 2; side++)
            {
                int d = (step + (side == 0 ? s1 : -s1) + 8) % 8, run = 0;
                for (int k = 1; k <= FlankWidth && k - run <= healReach + 1; k++)
                {
                    if (LiveNear(cell, Dir8X[d] * k, Dir8Z[d] * k, nx, nz, FlankLook)) run = k;
                }
                width += run;
            }
            bool narrow = width <= FlankNarrow;
            int rows = narrow ? 1 : FlankRows;
            int along = FloorDiv(x * nx + z * nz, nx * nx + nz * nz), block = FloorDiv(along, rows);
            if (along - block * rows != GroundHash(block, rows, unchecked(seed + 3)) % rows) return n;
            int lean = Math.Min(FlankLeanCap, 512 * width / FlankWidth);
            int noise = GroundNoise(x, z, seed, FlankPatch);
            for (int side = 0; side < 2; side++)
            {
                int d = (step + (side == 0 ? s1 : -s1) + 8) % 8, sx = Dir8X[d], sz = Dir8Z[d];
                bool beside = false;
                for (int k = 1; k <= healReach + 1 && !beside; k++) beside = AnchorNear(anchor, sx * k, sz * k, nx, nz, FlankBeside);
                if (beside) continue;
                if (!narrow && noise < 2 * lean - 512)
                {
                    int on = 0;
                    for (int k = 1; k <= FlankNarrow; k++)
                    {
                        bool goes = false;
                        for (int d2 = 1; d2 <= 2 && !goes; d2++)
                        {
                            int gx = nx * d2 - sx * k, gz = nz * d2 - sz * k;
                            goes = cell(gx, gz) != RM_CarryCell.Bare || anchor(gx, gz);
                        }
                        if (goes) on++;
                    }
                    if (2 * on > FlankNarrow) return 0;
                }
                if (healed || n == 0 || noise < lean) continue;
                int ux = outX[0] + sx, uz = outZ[0] + sz;
                if (cell(ux, uz) != RM_CarryCell.Fuel) continue;
                int fuel = 0;
                if (cell(ux + nx, uz + nz) == RM_CarryCell.Fuel) fuel++;
                if (cell(ux + sx, uz + sz) == RM_CarryCell.Fuel) fuel++;
                if (cell(ux + nx + sx, uz + nz + sz) == RM_CarryCell.Fuel) fuel++;
                if (cell(ux + sx - nx, uz + sz - nz) == RM_CarryCell.Fuel) fuel++;
                if (cell(ux + 2 * sx, uz + 2 * sz) == RM_CarryCell.Fuel) fuel++;
                if (fuel < FlankFuel) continue;
                outX[n] = ux;
                outZ[n] = uz;
                return n + 1;
            }
            return n;
        }

        /// <summary>Is this fire due to be carried on? Only a free-standing ground fire on Pyrelands ground, once, at its age.</summary>
        public static bool WindCarryDue(bool enabled, bool freeStanding, bool onPyrelandsGround, bool alreadyCarried, int ticksSinceSpawn, int carryAge)
        {
            return enabled && freeStanding && onPyrelandsGround && !alreadyCarried && ticksSinceSpawn >= carryAge;
        }

        /// <summary>Does vanilla's own even spread still run for this fire? Not where the wind carries it.</summary>
        public static bool VanillaSpreadRuns(bool enabled, bool freeStanding, bool onPyrelandsGround)
        {
            return !(enabled && freeStanding && onPyrelandsGround);
        }

        /// <summary>The bearing of a line lit ACROSS the wind (FrontLine's angle), so the whole line walks abreast.</summary>
        public static float AcrossWind(float windBearingDeg)
        {
            return (windBearingDeg + 90f) % 360f;
        }

        /// <summary>The wind's bearing when yesterday's fire came in from map edge `edge` (0 north, 1 east, 2 south, 3 west):
        /// it blows inward, the way that fire walked.</summary>
        public static float WindFromScarEdge(int edge)
        {
            switch (edge & 3)
            {
                case 0: return 180f;
                case 1: return 270f;
                case 2: return 0f;
                default: return 90f;
            }
        }

        /// <summary>Does (dx, dz) lie downwind of a fire, inside the cone a carried line can ever reach? WindProbes' nearest
        /// compass step is at most 22.5 degrees off the bearing and its two neighbours 45 beyond that, so no chain of carries
        /// leaves 67.5 degrees either side of the wind (tan 67.5 = 2.4142). A flank that opens (FlankPlan) or a healed gap adds a
        /// cell aside now and then; no burned cell of the model's lone fires lay beyond the cone more than 8 cells from where it
        /// was lit. The burn-approach warning reads it, again as the fire walks.</summary>
        public static bool Downwind(int dx, int dz, float windX, float windZ)
        {
            float along = dx * windX + dz * windZ, across = Math.Abs(dx * windZ - dz * windX);
            return along > 0f && across <= along * 2.4143f;
        }

        /// <summary>The fires that were carried on and still burn (the saved set; a despawned fire's id is dropped).</summary>
        public static List<int> CarriedStillBurning(ICollection<int> carried, ICollection<int> live)
        {
            var keep = new List<int>();
            if (carried == null || live == null) return keep;
            foreach (int id in live)
            {
                if (carried.Contains(id)) keep.Add(id);
            }
            return keep;
        }

        /// <summary>Index of the fire nearest the centroid, so "where the burn is" is a cell that burns: with two lines on the
        /// map the plain centroid lies in the unburned grass between them (bar ullai_graze_old_burns: the herd walks to where
        /// it BURNED). -1 with no fire.</summary>
        public static int NearestToCentroid(IList<int> xs, IList<int> zs, int cx, int cz)
        {
            int best = -1;
            long bestD = long.MaxValue;
            for (int i = 0; i < xs.Count; i++)
            {
                long ddx = xs[i] - cx, ddz = zs[i] - cz, d = ddx * ddx + ddz * ddz;
                if (d < bestD) { bestD = d; best = i; }
            }
            return best;
        }

        /// <summary>The rite lights where its lead stands; if that lit nothing it tries the rite origin once.</summary>
        public static bool RiteRetryAtOrigin(int lit, bool leadIsAtOrigin)
        {
            return lit == 0 && !leadIsAtOrigin;
        }
    }
}
