using System.Collections.Generic;
using System.Linq;
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
        // Annex A's ruled curve (0→0.55 · 25→0.80 · 50→1.00 · 75→1.25 ·
        // 100→1.60) now lives on GameComponent_ColonyVisibility.ThreatFactor
        // (moved 2026-09-02, COLONY_VISIBILITY_BUILD_1: that file has no
        // HarmonyLib/RimWorld.Planet dependency, so it can be selftested
        // offline without pulling those references into the SelfTest
        // project - this file's Prefix just consumes it below).

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
                // Prefix, not postfix: GenerateGravship despawns the grav engine
                // (Thing.DeSpawn inside Gravship's own ctor / CopyCellContents)
                // before returning, so engine.Map is already null by the time any
                // postfix on this method runs. Harmony guarantees every prefix
                // runs before the original, so this is the last point the engine
                // is still on its map.
                harmony.Patch(launchTarget,
                    prefix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Prefix_RecordTileMemoryOnLaunch)),
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_ResetVisibilityOnLaunch)));
            }

            // Tile-memory decay (owner card, "the desert remembers"): record
            // the dial at the departure tile, restore a decayed fraction on
            // arrival. Same launch choke point for departure; both arrival
            // methods for the two ways a gravship trip ends (landing on an
            // already-generated map vs. generating a brand new one).
            var arriveExistingTarget = AccessTools.Method(typeof(GravshipUtility), nameof(GravshipUtility.ArriveExistingMap));
            if (arriveExistingTarget == null)
            {
                Log.Error("[RimMandrake.Visibility] GravshipUtility.ArriveExistingMap not found by reflection - "
                    + "vanilla API has moved. Tile-memory restore (existing map) NOT applied.");
            }
            else
            {
                harmony.Patch(arriveExistingTarget,
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_ApplyTileMemoryOnArrival)));
            }

            var arriveNewTarget = AccessTools.Method(typeof(GravshipUtility), nameof(GravshipUtility.ArriveNewMap));
            if (arriveNewTarget == null)
            {
                Log.Error("[RimMandrake.Visibility] GravshipUtility.ArriveNewMap not found by reflection - "
                    + "vanilla API has moved. Tile-memory restore (new map) NOT applied.");
            }
            else
            {
                harmony.Patch(arriveNewTarget,
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_ApplyTileMemoryOnArrival)));
            }

            // F17 interface layer, inspect-tag piece only (design doc §3.3):
            // an extra gizmo on the grav engine showing the current band.
            // The reign-calendar clause and band-crossing letters (§3.1/3.2)
            // are NOT built here - both depend on Ninefold's own
            // signed-letter/calendar infrastructure
            // (NINEFOLD_ENGINE_M0_1: event hooks/corpus letters not built,
            // reserved for the owner's voice redline), which doesn't exist
            // in code yet. Firing an unsigned letter here would violate F9's
            // "no unsigned crossings" rule the design doc itself cites -
            // Notify_BandCrossed below is the wired trigger point for
            // whoever builds that layer, deliberately inert until then.
            var gizmoTarget = AccessTools.Method(typeof(Building_GravEngine), nameof(Building_GravEngine.GetGizmos));
            if (gizmoTarget == null)
            {
                Log.Error("[RimMandrake.Visibility] Building_GravEngine.GetGizmos not found by reflection - "
                    + "vanilla API has moved. Visibility inspect-tag gizmo NOT applied.");
            }
            else
            {
                harmony.Patch(gizmoTarget,
                    postfix: new HarmonyMethod(typeof(ColonyVisibilityRaidPatch), nameof(Postfix_AddInspectGizmo)));
            }
        }

        /// <summary>
        /// Departure half of tile-memory decay - a PREFIX on GenerateGravship
        /// (see the registration comment above for why), so it runs before
        /// Postfix_ResetVisibilityOnLaunch and reads shipVisibility before
        /// ResetOnLaunch clamps it to the 5-15 floor - the memory reflects
        /// what the tile actually looked like while occupied, not the
        /// post-launch reset value.
        /// </summary>
        public static void Prefix_RecordTileMemoryOnLaunch(Building_GravEngine engine)
        {
            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            if (component == null || engine?.Map == null)
            {
                return;
            }
            component.RecordTileDeparture(engine.Map.Tile);
        }

        /// <summary>Arrival half of tile-memory decay - both ArriveExistingMap and ArriveNewMap resolve the
        /// destination via gravship.destinationTile, set before either runs (GravshipUtility.TravelTo).</summary>
        public static void Postfix_ApplyTileMemoryOnArrival(Gravship gravship)
        {
            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            if (component == null || gravship == null)
            {
                return;
            }
            component.ApplyTileMemoryOnArrival(gravship.destinationTile);
        }

        /// <summary>
        /// F17 §3.3's inspect tag: "Clicking the colony's home structure...
        /// shows the current band name plus, once unlocked, whichever god's
        /// hand is heaviest" - the god-attribution half needs Ninefold's
        /// godStates ledger (not built), so this ships band-name-only, with
        /// the extension point named in the disabled reason rather than
        /// silently doing nothing.
        /// </summary>
        public static void Postfix_AddInspectGizmo(ref IEnumerable<Gizmo> __result, Building_GravEngine __instance)
        {
            GameComponent_ColonyVisibility component = Current.Game?.GetComponent<GameComponent_ColonyVisibility>();
            if (component == null)
            {
                return;
            }

            // Plain strings, not keyed .Translate() calls: no Languages/
            // English XML exists for this mod yet, and a missing-key
            // fallback would just print the raw key - authoring real
            // localization is out of scope for this pass.
            string desc = $"Colony Visibility: {component.shipVisibility:F0}/100 ({component.Band})\n\n"
                + "How exposed this ship's presence is to the wider desert. Crosses bands at "
                + "20/40/60/80. God-attribution (whose hand is heaviest right now) is not shown yet - "
                + "reserved for Ninefold's godStates ledger.";
            Command_Action gizmo = new Command_Action
            {
                defaultLabel = $"Visibility: {component.Band}",
                defaultDesc = desc,
                icon = TexCommand.Attack, // reused vanilla icon, no new art authored this pass
                action = delegate
                {
                    Find.WindowStack.Add(new Dialog_MessageBox(desc));
                },
            };
            __result = __result.Concat(new Gizmo[] { gizmo });
        }

        /// <summary>
        /// F17 §3.2's band-crossing letter TRIGGER POINT - deliberately not
        /// wired to Adjust() yet. Firing a real letter here needs F9's
        /// signing/attribution (which god, per the divine_satiation_engine
        /// ledger) and that ledger is Ninefold's own unbuilt TODO
        /// (NINEFOLD_ENGINE_M0_1). An unsigned letter would violate F9's own
        /// rule the design doc cites ("No unsigned crossings"), so this stays
        /// a named, callable stub rather than fabricated flavor text.
        /// Call from Adjust() (pass before/after Band) once a real signer
        /// exists.
        /// </summary>
        public static void Notify_BandCrossed_NotYetWired(VisibilityBand before, VisibilityBand after)
        {
            // Intentionally inert. See doc comment.
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

            float factor = GameComponent_ColonyVisibility.ThreatFactor(visibility) * shkaarMultiplier;
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
        /// Source/RimWorld/GravshipUtility.cs). The tile-memory departure
        /// record (Prefix_RecordTileMemoryOnLaunch) runs first, as a prefix
        /// on the same method, and reads shipVisibility before this clamps
        /// it.</summary>
        public static void Postfix_ResetVisibilityOnLaunch(Building_GravEngine engine)
        {
            Current.Game?.GetComponent<GameComponent_ColonyVisibility>()?.ResetOnLaunch();
        }
    }
}
