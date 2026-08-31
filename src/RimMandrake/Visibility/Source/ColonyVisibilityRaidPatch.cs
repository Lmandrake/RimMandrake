using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Visibility
{
    /// <summary>
    /// COLONY_VISIBILITY_BUILD_1, F12 half. Supersedes COLONY_VISIBILITY_STAT_1's
    /// transpiler-based single-call-site swap (formerly
    /// src/RimUtinni/Doctrine/Source/DoctrineCore/ColonyVisibilityRaidPatch.cs)
    /// with the owner's 2026-08-31 ruling ("THREAT-SCOPED patching... the
    /// Postfix replaces threat points for HOSTILE events only") and Annex A's
    /// simpler multiplicative formula (design/Jawa/worldbuilding/
    /// colony_visibility_stat.md §3 Annex A: "We do NOT rewrite the wealth
    /// curves... Visibility multiplies the output: points ×=
    /// VisibilityToThreatCurve(vis)") - which replaces STAT_1's more
    /// complex "reimplement vanilla's pawn-power term, replace the wealth
    /// term" approach entirely. Multiplying the already-resolved points
    /// value needs no reimplementation of vanilla's math at all.
    ///
    /// CHOKE POINT (verified via RimSage, not guessed - a fresh research
    /// pass for this item after STAT_1 flagged the dominant raid path as
    /// genuinely open):
    ///
    ///   `IncidentCategoryDef` carries no hostility flag (`IncidentCategoryDef.cs`:
    ///   just needsParmsPoints/tale/canUseAnomalyChance), and filtering on
    ///   `needsParmsPoints`/`ThreatBig` is PROVABLY wrong: `ProblemCauser`
    ///   (`Defs/Royalty/IncidentDefs/Incidents_Map_Misc.xml`) is a
    ///   quest-giving incident tagged `category>ThreatBig`, and
    ///   `ThrumboPasses`/`HerdMigration` (both `category=Misc`) also have
    ///   `needsParmsPoints=true` despite being explicitly out of scope. No
    ///   category-based filter at `DefaultParmsNow`/`GenerateParms` can
    ///   separate these correctly.
    ///
    ///   The reliable choke point is `IncidentWorker.TryExecute(IncidentParms
    ///   parms)` (`Source/RimWorld/IncidentWorker.cs:183`) - called once per
    ///   FIRING incident, with `this` the CONCRETE worker subclass and
    ///   `parms.points` already resolved but NOT YET CONSUMED
    ///   (`IncidentWorker_Raid.TryExecuteWorker` reads it first thing).
    ///   `IncidentParms` is a class, so mutating `parms.points` in a Prefix
    ///   changes what the real worker body consumes. Gating on concrete
    ///   worker TYPE (not category) cleanly separates hostile from benign:
    ///   `IncidentWorker_RaidEnemy`, `IncidentWorker_Infestation`,
    ///   `IncidentWorker_AggressiveAnimals` (manhunter packs),
    ///   `IncidentWorker_MechCluster`. This single choke point ALSO covers
    ///   `TimedDetectionRaids`' own boosted raid (it constructs and fires an
    ///   `IncidentWorker_RaidEnemy` the same way), so the separate transpiler
    ///   STAT_1 needed for that one site is no longer necessary - one Prefix
    ///   replaces it.
    /// </summary>
    public static class ColonyVisibilityRaidPatch
    {
        /// <summary>
        /// Annex A's ruled curve (colony_visibility_stat.md §3 Annex A,
        /// 2026-08-30 BENCH merge, closed by the 2026-08-31 owner ruling):
        /// "first-guess curve 0→0.55 · 25→0.80 · 50→1.00 · 75→1.25 ·
        /// 100→1.60". Supersedes the earlier §4.2 illustrative table
        /// (0.3x..3.5x), which Annex A's own "replace, don't stack" note
        /// obsoletes. Still explicitly NOT TUNED - §5's tuning protocol
        /// (throwaway-save rig, measure at Visibility ∈ {0,25,50,75,100} ×
        /// 3 wealth bands) has not been run.
        /// </summary>
        private static readonly SimpleCurve VisibilityToThreatCurve = new SimpleCurve
        {
            new CurvePoint(0f, 0.55f),
            new CurvePoint(25f, 0.80f),
            new CurvePoint(50f, 1.00f),
            new CurvePoint(75f, 1.25f),
            new CurvePoint(100f, 1.60f),
        };

        public static void Apply(Harmony harmony)
        {
            var tryExecuteTarget = AccessTools.Method(typeof(IncidentWorker), nameof(IncidentWorker.TryExecute));
            if (tryExecuteTarget == null)
            {
                Log.Error("[RimMandrake.Visibility] IncidentWorker.TryExecute not found by reflection - "
                    + "vanilla API has moved. Colony Visibility threat-point multiplier NOT applied.");
            }
            else
            {
                harmony.Patch(tryExecuteTarget,
                    prefix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Prefix_ScaleHostilePoints)));
            }

            var launchTarget = AccessTools.Method(typeof(GravshipUtility), nameof(GravshipUtility.GenerateGravship));
            if (launchTarget == null)
            {
                Log.Error("[RimMandrake.Visibility] GravshipUtility.GenerateGravship not found by reflection - "
                    + "vanilla API has moved. Ta'Baa launch-reset hook NOT applied.");
            }
            else
            {
                harmony.Patch(launchTarget,
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_ResetVisibilityOnLaunch)));
            }
        }

        /// <summary>
        /// Multiplies parms.points BEFORE the concrete worker consumes it -
        /// only for the hostile worker types named above. Every other
        /// IncidentWorker (quests, thrumbo passes, herd migrations, trade
        /// caravans, ambient benign events) passes through untouched, per
        /// the owner's threat-scoped ruling.
        /// </summary>
        public static void Prefix_ScaleHostilePoints(IncidentWorker __instance, IncidentParms parms)
        {
            if (parms == null || parms.points <= 0f) return;
            if (!(__instance is IncidentWorker_RaidEnemy
                  || __instance is IncidentWorker_Infestation
                  || __instance is IncidentWorker_AggressiveAnimals
                  || __instance is IncidentWorker_MechCluster))
            {
                return;
            }

            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            float visibility = component?.shipVisibility ?? 10f;
            float shkaarMultiplier = component?.ShkaarEscalationMultiplier ?? 1f;

            float factor = VisibilityToThreatCurve.Evaluate(visibility) * shkaarMultiplier;
            float before = parms.points;
            parms.points = Mathf.Clamp(parms.points * factor, StorytellerUtility.GlobalPointsMin(), 10000f);

            if (Prefs.DevMode)
            {
                Log.Message($"[RimMandrake.Visibility] {__instance.GetType().Name} points {before:F0} -> "
                    + $"{parms.points:F0} (visibility {visibility:F1}, factor {factor:F2})");
            }
        }

        /// <summary>Ta'Baa's launch reset (design doc §2 "Resets it"). Fires
        /// once per successful gravship launch - GenerateGravship is the
        /// moment the ship map is actually detached and turned into a
        /// Gravship world object (verified via RimSage,
        /// Source/RimWorld/GravshipUtility.cs, carried over unchanged from
        /// COLONY_VISIBILITY_STAT_1's build).</summary>
        public static void Postfix_ResetVisibilityOnLaunch(Building_GravEngine engine)
        {
            Current.Game?.GetComponent<GameComponent_ColonyVisibility>()?.ResetOnLaunch();
        }
    }
}
