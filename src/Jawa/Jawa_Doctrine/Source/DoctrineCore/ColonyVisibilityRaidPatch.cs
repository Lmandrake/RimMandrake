using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace JawaDoctrineCore
{
    /// <summary>
    /// COLONY_VISIBILITY_STAT_1, F12 half. Replaces vanilla's wealth term
    /// (PointsPerWealthCurve) in raid-point sizing with a Colony-Visibility-
    /// driven term, at ONE verified call site: TimedDetectionRaids's
    /// CompTickInterval. Also wires Ta'Baa's launch reset onto a real vanilla
    /// event.
    ///
    /// §4 of design/Jawa/worldbuilding/colony_visibility_stat.md names FOUR
    /// call sites, sourced from an earlier read of RimWorld source. Re-reading
    /// the LIVE 1.6 source via RimSage for this build found three of those
    /// four citations do not match current source, and are not load-bearing
    /// for ordinary raid-point sizing even where the cited line does exist.
    /// Full corrected read is in COLONY_VISIBILITY_STAT_1.md; short version:
    ///
    ///   VERIFIED, patched here: Planet/TimedDetectionRaids.cs,
    ///     CompTickInterval - "incidentParms.points =
    ///     StorytellerUtility.DefaultThreatPointsNow(...) * 1.5f" is an
    ///     unconditional, always-executed call. Correct and narrow.
    ///
    ///   NOT the real call site, NOT patched: IncidentWorker_RaidEnemy /
    ///     IncidentWorker_RaidFriendly .TryExecuteWorker (spec doc's
    ///     citation). The actual DefaultThreatPointsNow call in both classes
    ///     lives in ResolveRaidPoints, a DIFFERENT method - and even there it
    ///     is a defensive fallback ("RaidEnemy is resolving raid points. They
    ///     should always be set before initiating the incident.") that does
    ///     NOT execute in the ordinary flow: for a normal storyteller-fired
    ///     raid, parms.points is already set upstream by
    ///     StorytellerComp.GenerateParms -> StorytellerUtility.DefaultParmsNow
    ///     -> DefaultThreatPointsNow, before TryExecuteWorker/ResolveRaidPoints
    ///     ever runs. Patching that call would be a correct-looking,
    ///     compiling patch that is a no-op for essentially every real raid -
    ///     worse than not patching it, because it would look done.
    ///
    ///   NOT the real call site, NOT patched: QuestGen/QuestNode_GenerateThreats.cs
    ///     (spec doc's citation). The DefaultThreatPointsNow call at that line
    ///     only feeds storeThreatExampleAs, a cosmetic slate-text preview
    ///     string - not actual quest-raid point sizing. The real quest-threat
    ///     points computation is RimWorld.ThreatsGenerator.GetIncidentParms
    ///     (Source/RimWorld/ThreatsGenerator.cs), reached from
    ///     QuestPart_ThreatsGenerator.MakeIntervalIncidents - a different
    ///     method than the one named. Not built here: GetIncidentParms runs
    ///     BEFORE the specific incident type (RaidEnemy vs MechCluster) is
    ///     chosen, so a Visibility-only override at that seam can't cleanly
    ///     avoid also touching MechCluster point sizing - an out-of-scope
    ///     system by the design doc's own §4.4 rule. Real ambiguity, not
    ///     guessed past.
    ///
    ///   The DOMINANT path for an ordinary wealth-scaled raid
    ///     (StorytellerComp_RandomMain.GenerateParms -> DefaultParmsNow ->
    ///     DefaultThreatPointsNow, called BEFORE any IncidentWorker runs) is
    ///     NOT patched in this pass. Patching it narrowly requires
    ///     distinguishing "this DefaultParmsNow call is about to fire a raid"
    ///     from "...an ambush / mech cluster / manhunter pack / infestation /
    ///     etc", all of which share IncidentCategoryDefOf.ThreatBig and reach
    ///     DefaultParmsNow through the exact same call - i.e. the same
    ///     shared-function ambiguity §4.3 was written to dodge, one level up
    ///     the call graph. That is real, load-bearing uncertainty about
    ///     vanilla's behavior, not a guess this pass is willing to make. Left
    ///     for a future pass with its own ruling - see item file.
    /// </summary>
    public static class ColonyVisibilityRaidPatch
    {
        // Vanilla's own curves - all private static readonly SimpleCurve on
        // StorytellerUtility (confirmed via RimSage read of
        // Source/RimWorld/StorytellerUtility.cs). Reflected rather than
        // copied by value, so a future vanilla balance pass to these numbers
        // is inherited rather than silently going stale here.
        private static readonly SimpleCurve PointsPerWealthCurve =
            (SimpleCurve)AccessTools.Field(typeof(StorytellerUtility), "PointsPerWealthCurve").GetValue(null);
        private static readonly SimpleCurve PointsPerColonistByWealthCurve =
            (SimpleCurve)AccessTools.Field(typeof(StorytellerUtility), "PointsPerColonistByWealthCurve").GetValue(null);
        private static readonly SimpleCurve PointsFactorForColonyMechsCurve =
            (SimpleCurve)AccessTools.Field(typeof(StorytellerUtility), "PointsFactorForColonyMechsCurve").GetValue(null);
        private static readonly SimpleCurve PointsFactorForColonySubhumanCurve =
            (SimpleCurve)AccessTools.Field(typeof(StorytellerUtility), "PointsFactorForColonySubhumanCurve").GetValue(null);
        private static readonly SimpleCurve PointsFactorForPawnAgeYearsCurve =
            (SimpleCurve)AccessTools.Field(typeof(StorytellerUtility), "PointsFactorForPawnAgeYearsCurve").GetValue(null);

        /// <summary>
        /// design doc §4.2's replacement-factor table (illustrative anchors,
        /// not tuned - owner's call per the item's "decisions owed" #3).
        /// </summary>
        private static readonly SimpleCurve VisibilityFactorCurve = new SimpleCurve
        {
            new CurvePoint(0f, 0.3f),
            new CurvePoint(20f, 0.6f),
            new CurvePoint(40f, 1.0f),
            new CurvePoint(60f, 1.6f),
            new CurvePoint(80f, 2.4f),
            new CurvePoint(100f, 3.5f),
        };

        /// <summary>
        /// "~1.0x - parity anchor, roughly a mid-wealth vanilla colony" (§4.2).
        /// Anchored to vanilla's OWN mid-wealth point rather than a hardcoded
        /// points value, so it tracks vanilla if PointsPerWealthCurve is ever
        /// rebalanced.
        /// </summary>
        private static float ParityAnchorWealthPoints => PointsPerWealthCurve.Evaluate(400000f);

        public static void Apply(Harmony harmony)
        {
            var raidTarget = AccessTools.Method(typeof(TimedDetectionRaids), "CompTickInterval");
            if (raidTarget == null)
            {
                Log.Error("[JawaDoctrineCore] TimedDetectionRaids.CompTickInterval not found by reflection - "
                    + "vanilla API has moved. Colony Visibility raid-point replacement NOT applied.");
            }
            else
            {
                harmony.Patch(raidTarget,
                    transpiler: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Transpiler_SwapDefaultThreatPoints)));
            }

            var launchTarget = AccessTools.Method(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship));
            if (launchTarget == null)
            {
                Log.Error("[JawaDoctrineCore] GravshipUtility.GenerateGravship not found by reflection - "
                    + "vanilla API has moved. Ta'Baa launch-reset hook NOT applied.");
            }
            else
            {
                harmony.Patch(launchTarget,
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_ResetVisibilityOnLaunch)));
            }
        }

        /// <summary>
        /// Call-site transpiler: within TimedDetectionRaids.CompTickInterval
        /// ONLY, redirect the call to
        /// StorytellerUtility.DefaultThreatPointsNow to RaidThreatPointsNow
        /// (identical signature: static, one IIncidentTarget param, returns
        /// float - a pure callee swap, no stack shape change).
        ///
        /// A transpiler is used rather than a prefix/postfix on
        /// DefaultThreatPointsNow itself because that method has ~45 unrelated
        /// callers (insects, fleshmass, mechhive, quests, thrumbo herds...) -
        /// patching it directly would silently reshape all of them, exactly
        /// the failure mode §4.3 names. A postfix on CompTickInterval itself
        /// doesn't work either: incidentParms.points is consumed by
        /// IncidentDefOf.RaidEnemy.Worker.TryExecute(incidentParms) inside
        /// the SAME method, before a postfix on the outer method would run -
        /// the swap has to happen mid-method, which is what a transpiler is
        /// for.
        /// </summary>
        public static IEnumerable<CodeInstruction> Transpiler_SwapDefaultThreatPoints(IEnumerable<CodeInstruction> instructions)
        {
            var from = AccessTools.Method(typeof(StorytellerUtility), nameof(StorytellerUtility.DefaultThreatPointsNow));
            var to = AccessTools.Method(typeof(ColonyVisibilityRaidPatch), nameof(RaidThreatPointsNow));
            int swapped = 0;
            foreach (var ins in instructions)
            {
                if ((ins.opcode == OpCodes.Call || ins.opcode == OpCodes.Callvirt)
                    && ins.operand is MethodInfo mi && mi == from)
                {
                    ins.opcode = OpCodes.Call;
                    ins.operand = to;
                    swapped++;
                }
                yield return ins;
            }
            if (swapped != 1)
            {
                Log.Error($"[JawaDoctrineCore] ColonyVisibility transpiler expected exactly 1 call-site swap in "
                    + $"TimedDetectionRaids.CompTickInterval, found {swapped}. Vanilla method body has likely "
                    + "changed shape since this was verified - raid-point replacement may not be correctly "
                    + "applied. Re-check against current source rather than trusting this patch blind.");
            }
        }

        /// <summary>Ta'Baa's launch reset (design doc §2 "Resets it"). Fires
        /// once per successful gravship launch - GenerateGravship is the
        /// moment the ship map is actually detached and turned into a
        /// Gravship world object (verified via RimSage,
        /// Source/RimWorld/GravshipUtility.cs).</summary>
        public static void Postfix_ResetVisibilityOnLaunch(Building_GravEngine engine)
        {
            Current.Game?.GetComponent<GameComponent_ColonyVisibility>()?.ResetOnLaunch();
        }

        /// <summary>
        /// design doc §4.3's RaidThreatPointsNow. Reimplements vanilla's
        /// pawn-power term (num2) verbatim (verified against live 1.6
        /// StorytellerUtility.DefaultThreatPointsNow via RimSage) and
        /// substitutes a Visibility-driven term for the wealth term (num),
        /// per §4.2 - the wealth and pawn-power terms are summed inside
        /// vanilla's private method before any multiplier runs, so they
        /// cannot be un-mixed by calling vanilla and adjusting the result;
        /// this has to be a self-contained reimplementation.
        ///
        /// Sh'kaar's escalation-meter seam
        /// (GameComponent_ColonyVisibility.ShkaarEscalationMultiplier,
        /// default 1f/no-op) multiplies the Visibility term only, matching
        /// §4.2's "finalFactor = visibilityFactor(V) * shkaarEscalationMultiplier"
        /// before it joins num2 in vanilla's own
        /// num4/num5/threatScale/daysPassedFactor chain, clamped exactly as
        /// vanilla does.
        /// </summary>
        public static float RaidThreatPointsNow(IIncidentTarget target)
        {
            if (target is Map { IsPocketMap: not false } map)
            {
                target = map.PocketMapParent.sourceMap;
            }

            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            float visibility = component?.shipVisibility ?? 10f;
            float shkaarMultiplier = component?.ShkaarEscalationMultiplier ?? 1f;

            float visibilityFactor = VisibilityFactorCurve.Evaluate(visibility) * shkaarMultiplier;
            float finalFactor = visibilityFactor * ParityAnchorWealthPoints;

            float playerWealthForStoryteller = target.PlayerWealthForStoryteller;
            float num2 = 0f;
            foreach (Pawn item in target.PlayerPawnsForStoryteller)
            {
                if (item.IsQuestLodger())
                {
                    continue;
                }
                float num3 = 0f;
                if (item.IsFreeColonist)
                {
                    num3 = PointsPerColonistByWealthCurve.Evaluate(playerWealthForStoryteller);
                }
                else if (item.IsAnimal && item.Faction == Faction.OfPlayer && !item.Downed
                    && item.training.CanAssignToTrain(TrainableDefOf.Release).Accepted)
                {
                    num3 = 0.08f * item.kindDef.combatPower;
                    if (target is Caravan)
                    {
                        num3 *= 0.7f;
                    }
                }
                else if (item.IsColonyMech && !item.Downed)
                {
                    num3 = item.kindDef.combatPower * PointsFactorForColonyMechsCurve.Evaluate(playerWealthForStoryteller);
                }
                else if (item.IsSubhuman)
                {
                    num3 = item.kindDef.combatPower * PointsFactorForColonySubhumanCurve.Evaluate(playerWealthForStoryteller);
                }
                if (num3 > 0f)
                {
                    if (item.ParentHolder != null && item.ParentHolder is Building_CryptosleepCasket)
                    {
                        num3 *= 0.3f;
                    }
                    num3 = Mathf.Lerp(num3, num3 * item.health.summaryHealth.SummaryHealthPercent, 0.65f);
                    if (item.IsSlaveOfColony)
                    {
                        num3 *= 0.75f;
                    }
                    if (ModsConfig.BiotechActive && item.RaceProps.Humanlike)
                    {
                        num3 *= PointsFactorForPawnAgeYearsCurve.Evaluate(item.ageTracker.AgeBiologicalYearsFloat);
                    }
                    num2 += num3;
                }
            }

            float num4 = (finalFactor + num2) * target.IncidentPointsRandomFactorRange.RandomInRange;
            float totalThreatPointsFactor = Find.StoryWatcher.watcherAdaptation.TotalThreatPointsFactor;
            float num5 = Mathf.Lerp(1f, totalThreatPointsFactor, Find.Storyteller.difficulty.adaptationEffectFactor);
            return Mathf.Clamp(
                num4 * num5 * Find.Storyteller.difficulty.threatScale
                    * Find.Storyteller.def.pointsFactorFromDaysPassed.Evaluate(GenDate.DaysPassedSinceSettle),
                StorytellerUtility.GlobalPointsMin(), 10000f);
        }
    }
}
