// Verse-free kernel of Aftermath: what a battle's raiders count as (dead / exited / not yet arrived), the prisoner-held clock across every
// map, the queue discipline (one per faction, two total), the mental-break window and the rule eligibility tests. BattleRecord,
// AftermathRuleRunner and AftermathRuleEligibility call these with the same expressions; SelfTestFuzz/AftermathFuzz.cs compiles this file
// with the plain enum files and BattleOutcomeClassifier.cs alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib (a `using Verse;`
// here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.Aftermath
{
    /// <summary>What one poll sees of one raider.</summary>
    public struct RM_RaiderObs
    {
        public bool deadOrDowned, spawned, seenSpawned;
        public RM_RaiderObs(bool deadOrDowned, bool spawned, bool seenSpawned) { this.deadOrDowned = deadOrDowned; this.spawned = spawned; this.seenSpawned = seenSpawned; }
    }

    public static class RM_AftermathKernel
    {
        /// <summary>
        /// A raider that has not been seen on the map yet (still in a drop pod or a transport) is neither "exited" nor accounted for until this
        /// many ticks after the battle opened (PROVISIONAL tuning: a drop pod lands within a few hundred ticks; this is deliberately generous).
        /// </summary>
        public const int ArrivalGraceTicks = 1000;
        public const int TicksPerDay = 60000;
        public const int FallbackPollIntervalTicks = 250;
        public const int HousekeepingIntervalTicks = 5000;

        public static bool GraceExpired(int openedTick, int now) { return now - openedTick >= ArrivalGraceTicks; }

        public static int CountDeadOrDowned(IList<RM_RaiderObs> raiders)
        {
            int n = 0;
            for (int i = 0; i < raiders.Count; i++) if (raiders[i].deadOrDowned) n++;
            return n;
        }

        /// <summary>
        /// Alive, standing, off the map, and known to have been on it: a pawn that has not arrived yet does not count as having exited
        /// (a drop-pod raid polled mid-flight used to close at once as "Routed") unless the arrival grace has run out.
        /// </summary>
        public static int CountSurvivedAndExited(IList<RM_RaiderObs> raiders, bool graceExpired)
        {
            int n = 0;
            for (int i = 0; i < raiders.Count; i++)
            {
                RM_RaiderObs r = raiders[i];
                if (!r.deadOrDowned && !r.spawned && (r.seenSpawned || graceExpired)) n++;
            }
            return n;
        }

        /// <summary>Every raider is dead / downed, or has left after being seen (or the grace ran out): nobody is still fighting or still to arrive.</summary>
        public static bool AllAccountedFor(IList<RM_RaiderObs> raiders, bool graceExpired)
        {
            for (int i = 0; i < raiders.Count; i++)
            {
                RM_RaiderObs r = raiders[i];
                if (r.deadOrDowned) continue;
                if (r.spawned) return false;
                if (!r.seenSpawned && !graceExpired) return false;
            }
            return true;
        }

        // ---- rule eligibility (the Def-shaped wrappers in AftermathRuleEligibility pass these plain values) ----

        public static bool OutcomeEligible(bool kindIsBattleOutcome, bool outcomeListed, int survivors, int minSurvivors)
        {
            return kindIsBattleOutcome && outcomeListed && survivors >= minSurvivors;
        }

        public static bool HeldEligible(bool kindIsPrisonerHeld, float heldDays, float minHeldDays) { return kindIsPrisonerHeld && heldDays >= minHeldDays; }

        /// <summary>§2.2: at most maxPerFaction live queued aftermaths for one faction and maxTotal overall; "live" = fires after now.</summary>
        public static bool PassesDiscipline(int liveForFaction, int liveTotal, int maxPerFaction, int maxTotal)
        {
            if (liveForFaction >= maxPerFaction) return false;
            if (liveTotal >= maxTotal) return false;
            return true;
        }

        /// <summary>Rule 6: a mental break counts when it comes 0..window ticks after the battle closed.</summary>
        public static bool InMentalBreakWindow(int sinceBattleTicks, int windowTicks) { return !(sinceBattleTicks < 0 || sinceBattleTicks > windowTicks); }

        public static int WindowTicks(float days) { return (int)(days * TicksPerDay); }

        public static int DelayTicks(float days) { return (int)(days * TicksPerDay); }
    }

    /// <summary>
    /// Rule 4's per-prisoner clock: when a prisoner was first seen held, and whether the rule already fired for this captivity. The set polled is
    /// every prisoner on EVERY map at once - polling map by map dropped the other maps' prisoners from tracking on each pass and restarted
    /// their clocks, so with two or more maps no prisoner was ever held "long enough".
    /// </summary>
    public sealed class RM_PrisonerClock
    {
        private readonly Dictionary<int, int> firstSeen = new Dictionary<int, int>();
        private readonly HashSet<int> fired = new HashSet<int>();

        public int Tracked { get { return firstSeen.Count; } }

        /// <summary>Update tracking from the full current prisoner set: forget anyone no longer held (a recapture starts afresh), start clocks for new ones.</summary>
        public void Poll(int now, ICollection<int> currentAcrossAllMaps)
        {
            if (firstSeen.Count > 0)
            {
                var gone = new List<int>();
                foreach (int id in firstSeen.Keys) if (!Contains(currentAcrossAllMaps, id)) gone.Add(id);
                foreach (int id in gone) { firstSeen.Remove(id); fired.Remove(id); }
            }
            foreach (int id in currentAcrossAllMaps) if (!firstSeen.ContainsKey(id)) firstSeen[id] = now;
        }

        private static bool Contains(ICollection<int> c, int id)
        {
            var hs = c as HashSet<int>;
            if (hs != null) return hs.Contains(id);
            foreach (int x in c) if (x == id) return true;
            return false;
        }

        public bool HasFired(int id) { return fired.Contains(id); }
        public void MarkFired(int id) { fired.Add(id); }

        /// <summary>Days held as of now; 0 for an untracked prisoner.</summary>
        public float HeldDays(int id, int now)
        {
            int t;
            return firstSeen.TryGetValue(id, out t) ? (now - t) / (float)RM_AftermathKernel.TicksPerDay : 0f;
        }
    }
}
