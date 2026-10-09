// Verse-free kernel of the Watchers mod: the watch job's step state machine, the nearest-pawn scan, the think-tree gates (watch giver,
// relocate-to-medium), the hide-duration and flinch-radius arithmetic, the extension's config validation, the fragility rule, the sign's
// validity rule and the bounded alarm ripple.
// RM_JobDriver_Watch, RM_WatcherUtility, RM_JobGiver_Watch, RM_CompWatcher, RM_WatcherExtension, RM_WatcherSign and RM_WatcherAlarm call these with
// the same expressions; SelfTest/WatcherFuzz.cs compiles this file alone. Keep it free of Verse/RimWorld/UnityEngine/HarmonyLib
// (a `using Verse;` here breaks the self-test build, which is the guard rail).
using System;
using System.Collections.Generic;

namespace RimMandrake.Watchers
{
    /// <summary>What one 30-tick step of the watch job decided. The driver applies the flags in a fixed order: DropHunt, Hide (and
    /// RaiseAlarm with it), RestoreSign, Emerge, Face, then the End flags last.</summary>
    [Flags]
    public enum StepFlags
    {
        None = 0,
        EndInterrupted = 1,
        EndSucceeded = 2,
        DropHunt = 4,
        Hide = 8,
        RestoreSign = 16,
        Emerge = 32,
        ResetWatchClock = 64,
        Face = 128,
        /// <summary>This hide was caused by a body or the geophone (not a cue, not a neighbour's alarm): start a new alarm ripple.</summary>
        RaiseAlarm = 256,
    }

    public struct StepIn
    {
        public bool watchersEnabled, onMedium, hidden, hideAndFlinch, turnToFace, hasNearest, inFlinch, geophone, signMissing, hungry;
        /// <summary>A Hunt designation is on it. It never sends it under (a visible watcher is an ordinary target, owner ruling 2026-10-08);
        /// it is dropped the moment the watcher is under, because a hidden watcher cannot be targeted.</summary>
        public bool huntMarked;
        /// <summary>A neighbour's alarm ripple reached it and has not lapsed: it goes under and stays under like a cue.</summary>
        public bool alarmed;
        /// <summary>Any of the member's optional non-body cues holds (RM_WatcherKernel.Cues != None): it sends it under and keeps it
        /// under, exactly like the geophone.</summary>
        public bool cue;
        public int now, hiddenUntil, watchStart, maxWatchTicks;
    }

    public static class RM_WatcherKernel
    {
        public const int StepInterval = 30;
        public const int CheckInterval = 250;
        public const int NoMediumRecheckTicks = 7500;

        /// <summary>One step of the watch job.</summary>
        public static StepFlags DecideStep(StepIn s)
        {
            if (!s.watchersEnabled || !s.onMedium) return StepFlags.EndInterrupted;
            StepFlags f = StepFlags.None;
            if (!s.hidden)
            {
                if (s.hideAndFlinch && (s.inFlinch || s.geophone || s.cue || s.alarmed))
                {
                    f |= StepFlags.Hide;
                    if (s.huntMarked) f |= StepFlags.DropHunt;
                    if (s.inFlinch || s.geophone) f |= StepFlags.RaiseAlarm;
                    return f;
                }
                if (s.turnToFace && s.hasNearest) f |= StepFlags.Face;
                if (s.now - s.watchStart >= s.maxWatchTicks) f |= StepFlags.EndSucceeded;
                return f;
            }
            if (s.signMissing) f |= StepFlags.RestoreSign;
            if (!s.hideAndFlinch || s.hungry || (s.now >= s.hiddenUntil && !s.inFlinch && !s.geophone && !s.cue && !s.alarmed))
            {
                f |= StepFlags.Emerge | StepFlags.ResetWatchClock;
                if (s.hungry) f |= StepFlags.EndSucceeded;
            }
            else if (s.huntMarked) f |= StepFlags.DropHunt;
            return f;
        }

        /// <summary>How long a freshly hidden watcher stays down: the rolled range value scaled by the player's emerge-delay slider.</summary>
        public static int HiddenUntil(int now, int rolledTicks, float emergeDelayScale)
        {
            return now + (int)(rolledTicks * emergeDelayScale);
        }

        public static float FlinchRadius(float flinchRadius, float scale)
        {
            return flinchRadius * scale;
        }

        /// <summary>Nearest other creature inside the watch radius (first of equals); inFlinch is set when ANY creature inside the watch radius
        /// is within the flinch radius. Distances are squared.</summary>
        public static int Nearest(IList<float> distSq, float watchRadius, float flinchRadius, out bool inFlinch)
        {
            inFlinch = false;
            float watchSq = watchRadius * watchRadius;
            float flinchSq = flinchRadius * flinchRadius;
            int best = -1;
            float bestSq = float.MaxValue;
            for (int i = 0; i < distSq.Count; i++)
            {
                float d = distSq[i];
                if (d > watchSq) continue;
                if (d <= flinchSq) inFlinch = true;
                if (d < bestSq) { bestSq = d; best = i; }
            }
            return best;
        }

        /// <summary>The cheap gates of the think-tree watch giver (evaluated first, so the random roll and the map-wide active-watcher scan only run
        /// for an animal that could actually start a watch).</summary>
        public static bool WatchGiverPre(bool hasExt, bool watchersEnabled, bool spawned, bool downed, bool inMentalState, bool hasMap,
            bool hasComp, bool onMedium, bool hideAndFlinch, bool turnToFace, bool hasFoodNeed, float foodPercent,
            float emergeWhenFoodBelow)
        {
            if (!hasExt || !watchersEnabled) return false;
            if (!spawned || downed || inMentalState || !hasMap) return false;
            if (!hasComp) return false;
            if (!onMedium) return false;
            if (!hideAndFlinch && !turnToFace) return false;
            if (hasFoodNeed && foodPercent < emergeWhenFoodBelow) return false;
            return true;
        }

        /// <summary>The giver's last two gates: the wander roll and the per-map cap on animals in a watch job.</summary>
        public static bool WatchGiverCapOk(bool wanderRoll, int activeWatchers, int maxActivePerMap)
        {
            return !wanderRoll && activeWatchers < maxActivePerMap;
        }

        /// <summary>The whole giver decision (Pre then CapOk).</summary>
        public static bool WatchGiverAllows(bool hasExt, bool watchersEnabled, bool spawned, bool downed, bool inMentalState, bool hasMap,
            bool hasComp, bool onMedium, bool hideAndFlinch, bool turnToFace, bool hasFoodNeed, float foodPercent,
            float emergeWhenFoodBelow, bool wanderRoll, int activeWatchers, int maxActivePerMap)
        {
            return WatchGiverPre(hasExt, watchersEnabled, spawned, downed, inMentalState, hasMap, hasComp, onMedium, hideAndFlinch,
                turnToFace, hasFoodNeed, foodPercent, emergeWhenFoodBelow) && WatchGiverCapOk(wanderRoll, activeWatchers, maxActivePerMap);
        }

        /// <summary>The 250-tick comp check: should an idle off-medium watcher be sent looking for its medium.</summary>
        public static bool ShouldSeekMedium(bool watchersEnabled, bool stayOnMedium, bool hasMedium, bool downed, bool inMentalState,
            bool noMediumReachable, bool onMedium, bool hasCurrentJob, bool currentJobIsIdle)
        {
            if (!watchersEnabled || !stayOnMedium || !hasMedium || downed || inMentalState || noMediumReachable || onMedium) return false;
            if (hasCurrentJob && !currentJobIsIdle) return false;
            return true;
        }

        /// <summary>Config errors of an RM_WatcherExtension (empty list = sound).</summary>
        public static List<string> ConfigErrors(bool hasHiddenHediff, bool hasSignDef, bool signClassOk, float flinchRadius, float watchRadius,
            int hideMin, int hideMax, int maxWatchTicks, float wanderChance, float emergeWhenFoodBelow, float geophoneMinBodySize, float maxLethalDamage)
        {
            var e = new List<string>();
            if (!hasHiddenHediff) e.Add("hiddenHediff is null (it could never hide)");
            if (!hasSignDef) e.Add("signDef is null (a hidden watcher must leave a sign)");
            else if (!signClassOk) e.Add("signDef thingClass is not RM_WatcherSign");
            if (flinchRadius <= 0f || watchRadius < flinchRadius) e.Add("need 0 < flinchRadius <= watchRadius");
            if (hideMin <= 0 || hideMax < hideMin) e.Add("hideTicks range invalid");
            if (maxWatchTicks <= 0) e.Add("maxWatchTicks must be positive");
            if (wanderChance < 0f || wanderChance > 1f) e.Add("wanderChance must be a probability in 0..1");
            if (emergeWhenFoodBelow < 0f || emergeWhenFoodBelow > 1f) e.Add("emergeWhenFoodBelow must be a food fraction in 0..1 (above 1 it would never watch at all)");
            if (geophoneMinBodySize < 0f) e.Add("geophoneMinBodySize must not be negative (0 turns the geophone off)");
            if (!(maxLethalDamage > 0f)) e.Add("maxLethalDamage must be positive (it is the fragility ceiling every member is audited against)");
            return e;
        }

        // ------------------------------------------------------------------ fragility (owner ruling 2026-10-08, DEATH card)
        // "Should take almost no damage to destroy them." The engine kills a pawn whose summed injury severity reaches
        // Pawn_HealthTracker.LethalDamageThreshold = 150 x Pawn.HealthScale, and HealthScale = life stage healthScaleFactor x race
        // baseHealthScale (RimSage, decompiled 1.6). The audit reads the adult (factor 1), the sturdiest stage.

        public const float LethalDamagePerHealthScale = 150f;

        public static float LethalDamage(float baseHealthScale, float lifeStageHealthFactor)
        {
            return LethalDamagePerHealthScale * baseHealthScale * lifeStageHealthFactor;
        }

        /// <summary>Errors of the startup fragility audit (empty = fragile enough).</summary>
        public static List<string> FragilityErrors(float baseHealthScale, float maxLethalDamage)
        {
            var e = new List<string>();
            float lethal = LethalDamage(baseHealthScale, 1f);
            if (!(lethal <= maxLethalDamage))
                e.Add("an adult dies at " + lethal + " damage, above maxLethalDamage " + maxLethalDamage
                    + " (owner ruling 2026-10-08: almost no damage destroys a watcher; lower race baseHealthScale)");
            return e;
        }

        // ------------------------------------------------------------------ the sign's validity (orphan and duplicate repair)
        /// <summary>A sign stands only while its owner is alive, spawned, in the watch job, and that job's sign is this one. Anything else is an
        /// orphan (owner dead, gone, or out of the job) or a duplicate (the job holds another sign), and the sign removes itself.</summary>
        public static bool SignValid(bool hasOwner, bool ownerSpawned, bool ownerDead, bool ownerInWatchJob, bool jobSignIsThis)
        {
            return hasOwner && ownerSpawned && !ownerDead && ownerInWatchJob && jobSignIsThis;
        }

        // ------------------------------------------------------------------ the alarm ripple (owner ruling 2026-10-08: yes, bounded)
        // A watcher that goes under for a body or the geophone, or dies, starts an alarm event. The event reaches at most maxCount others in
        // total, each a short delay after the one that passed it on, at most maxHops passes from the origin, only within hopRadius of the one
        // passing it on and maxDistFromOrigin of where it began, and never after maxAgeTicks. Each event id is new; a watcher reached by an
        // event is never reached by it again, and a watcher going under because of an alarm never starts a new event. So it cannot loop.

        public struct AlarmLimits
        {
            public int maxCount, maxHops, maxAgeTicks, minDelayTicks, maxDelayTicks, holdTicks;
            public float hopRadius, maxDistFromOrigin;
        }

        /// <summary>The shipped limits (PROVISIONAL numbers; the ruling fixed "about 5", delays, and hop/age/distance limits).</summary>
        public static AlarmLimits DefaultAlarmLimits()
        {
            return new AlarmLimits { maxCount = 5, maxHops = 2, maxAgeTicks = 600, minDelayTicks = 15, maxDelayTicks = 60, holdTicks = 300,
                hopRadius = 8f, maxDistFromOrigin = 12f };
        }

        /// <summary>Is the event still live at this tick.</summary>
        public static bool AlarmLive(int now, int startTick, AlarmLimits L)
        {
            return now - startTick < L.maxAgeTicks;
        }

        /// <summary>Which candidates one pass of the event reaches, nearest to the passer first. hop = how many passes have already
        /// happened before this one (0 at the origin). reachedSoFar = how many watchers the event has already reached. Distances are squared.
        /// eligible = an awake visible watcher in its watch job (a hidden, dead or busy one is skipped, not counted).</summary>
        public static List<int> AlarmPick(IList<float> distSqFromPasser, IList<float> distSqFromOrigin, IList<bool> eligible, IList<bool> alreadyReached,
            int hop, int reachedSoFar, int now, int startTick, AlarmLimits L)
        {
            var picked = new List<int>();
            if (!AlarmLive(now, startTick, L) || hop >= L.maxHops) return picked;
            int room = L.maxCount - reachedSoFar;
            if (room <= 0) return picked;
            float hopSq = L.hopRadius * L.hopRadius, originSq = L.maxDistFromOrigin * L.maxDistFromOrigin;
            var order = new List<int>();
            for (int i = 0; i < distSqFromPasser.Count; i++)
            {
                if (!eligible[i] || alreadyReached[i]) continue;
                if (distSqFromPasser[i] > hopSq || distSqFromOrigin[i] > originSq) continue;
                order.Add(i);
            }
            order.Sort((a, b) => distSqFromPasser[a] != distSqFromPasser[b] ? distSqFromPasser[a].CompareTo(distSqFromPasser[b]) : a.CompareTo(b));
            for (int k = 0; k < order.Count && picked.Count < room; k++) picked.Add(order[k]);
            return picked;
        }

        /// <summary>When a pass lands: a rolled delay in [minDelayTicks, maxDelayTicks] after the passer was reached (rolled01 in [0,1]).</summary>
        public static int AlarmDeliverTick(int passerTick, float rolled01, AlarmLimits L)
        {
            float r = rolled01 < 0f ? 0f : rolled01 > 1f ? 1f : rolled01;
            return passerTick + L.minDelayTicks + (int)(r * (L.maxDelayTicks - L.minDelayTicks));
        }

        // ------------------------------------------------------------------ optional non-body cues (owner ruling 2026-10-08: "Full set")
        // Each cue is per member (absent in XML = that member ignores it) and each kind has its own Mod Settings toggle. While a cue holds,
        // the watcher goes under and stays under (StepIn.cue). A reading the driver did not take (cue off) is never consulted.

        /// <summary>The ordinary emergence rule for shade: a shade-lover (shadeMin) is out only where shade &gt;= shadeMin. Roofed = full shade;
        /// otherwise the brighter of the sun-heat grid's cast/roof shade (when that grid is active) and the sky itself (night = shade).</summary>
        public static float ShadeReading(bool roofed, bool gridActive, float gridShade, float skyGlow)
        {
            if (roofed) return 1f;
            float sky = 1f - Clamp01(skyGlow);
            return gridActive ? Math.Max(Clamp01(gridShade), sky) : sky;
        }

        /// <summary>Which cues hold this step. Distances are squared; float.MaxValue means "none on the map".</summary>
        public static CueKind Cues(CueIn c)
        {
            CueKind k = CueKind.None;
            if (c.gasOn && c.gasPercent >= c.gasMin) k |= CueKind.Gas;
            if (c.heatOn && c.tempC >= c.heatAboveC) k |= CueKind.Heat;
            if (c.fireOn && c.fireDistSq <= c.fireRadius * c.fireRadius) k |= CueKind.Fire;
            if (c.steamOn && c.steamDistSq <= c.steamRadius * c.steamRadius) k |= CueKind.Steam;
            if (c.shadeOn && c.shade < c.shadeMin) k |= CueKind.Shade;
            if (c.buriedOn && c.buriedDistSq <= c.buriedRadius * c.buriedRadius) k |= CueKind.Buried;
            if (c.lightOn && c.glow >= c.lightAbove) k |= CueKind.Light;
            return k;
        }

        /// <summary>Config errors of the optional cues block (empty = sound). has* = that cue's node is present in the member's XML.</summary>
        public static List<string> CueConfigErrors(bool hasGas, int gasTypeCount, float gasMin, bool hasHeat, float heatAboveC, bool hasFire,
            float fireRadius, bool hasSteam, int steamThingCount, float steamRadius, bool hasShade, float shadeMin, bool hasBuried,
            int buriedHediffCount, float buriedRadius, bool hasLight, float lightAbove)
        {
            var e = new List<string>();
            if (hasGas && gasTypeCount == 0) e.Add("cues.gas has no gasTypes (it could never fire)");
            if (hasGas && !(gasMin > 0f && gasMin <= 1f)) e.Add("cues.gas.minPercent must be in (0, 1] (0 would fire in clean air)");
            if (hasHeat && !(heatAboveC > -273f && heatAboveC < 1000f)) e.Add("cues.heat.aboveC must be a real temperature");
            if (hasFire && !(fireRadius > 0f)) e.Add("cues.fire.radius must be positive");
            if (hasSteam && steamThingCount == 0) e.Add("cues.steam has no things (it could never fire)");
            if (hasSteam && !(steamRadius > 0f)) e.Add("cues.steam.radius must be positive");
            if (hasShade && !(shadeMin > 0f && shadeMin <= 1f)) e.Add("cues.shade.minShade must be in (0, 1] (0 would never send it under)");
            if (hasBuried && buriedHediffCount == 0) e.Add("cues.buried has no hediffs (it could never fire)");
            if (hasBuried && !(buriedRadius > 0f)) e.Add("cues.buried.radius must be positive");
            if (hasLight && !(lightAbove > 0f && lightAbove <= 1f)) e.Add("cues.light.minGlow must be in (0, 1] (0 would fire in total darkness)");
            return e;
        }

        /// <summary>The water/medium audit run once at startup per member. Errors: a medium it can never stand on. Warnings: an avoid-wander
        /// medium (vanilla's shallow water and our deep sand) without race waterSeeker, which vanilla wander refuses outright; and an IsWater
        /// medium with a swimmingGraphicData, which outranks the stationary peek pose in every state (PawnRenderNodeWorker_AnimalBody).</summary>
        public static void MediumAudit(bool anyImpassable, bool anyAvoidWander, bool anyWater, bool waterSeeker, bool hasSwimmingGraphic,
            List<string> errors, List<string> warnings)
        {
            if (anyImpassable) errors.Add("a medium terrain is impassable: the watcher can never stand on it, so it can never watch or hide");
            if (anyAvoidWander && !waterSeeker) warnings.Add("a medium terrain is avoidWander (water) and the race is not waterSeeker: vanilla wander will refuse it");
            if (anyWater && hasSwimmingGraphic) warnings.Add("a medium terrain is IsWater and a life stage has swimmingGraphicData: the swimming sprite outranks the peek pose there");
        }

        private static float Clamp01(float v) { return v < 0f ? 0f : v > 1f ? 1f : v; }
    }

    [Flags]
    public enum CueKind
    {
        None = 0,
        Gas = 1,
        Heat = 2,
        Fire = 4,
        Steam = 8,
        Shade = 16,
        Buried = 32,
        Light = 64,
    }

    /// <summary>One step's cue readings. xOn = the member carries cue x AND its Mod Settings toggle is on.</summary>
    public struct CueIn
    {
        public bool gasOn, heatOn, fireOn, steamOn, shadeOn, buriedOn, lightOn;
        public float gasPercent, gasMin, tempC, heatAboveC, fireDistSq, fireRadius, steamDistSq, steamRadius, shade, shadeMin,
            buriedDistSq, buriedRadius, glow, lightAbove;
    }
}
