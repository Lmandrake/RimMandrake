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

        /// <summary>Index of the newest sample at least ticksAgo old, else the oldest sample, else -1.</summary>
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
            return ticks.Count > 0 ? 0 : -1;
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

        // ------------------------------------------------------------ the Tribes' incidents

        /// <summary>The switches every Tribes incident that answers the burn obeys (FIRE_CLOCK_FIX_RAIDS_IGNORE_THE_SWITCH): its own
        /// toggle, the mechanics gate, the burn line it reads (frozen when off) and the "Fire clock" setting, whose tooltip promises
        /// flame harvest, fire raid and fire rite never fire when it is off.</summary>
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

        /// <summary>The rite lights where its lead stands; if that lit nothing it tries the rite origin once.</summary>
        public static bool RiteRetryAtOrigin(int lit, bool leadIsAtOrigin)
        {
            return lit == 0 && !leadIsAtOrigin;
        }
    }
}
