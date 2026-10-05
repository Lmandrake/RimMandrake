using System.Collections.Generic;
using HarmonyLib;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // LONGSHADE_SHEET_STRUCTURAL_RULINGS_1 — the half-buried-in-sand graphic.
    // Owner 2026-10-04: thraia "Swimming graphic will be used when half-buried
    // in sand"; drazzik "Needs a beneath-sand-waiting image (swimming)".
    //
    // Vanilla 1.6 already owns the art slot: PawnKindLifeStage.swimmingGraphicData,
    // drawn by PawnRenderNodeWorker_AnimalBody when Pawn.DrawNonHumanlikeSwimmingGraphic
    // is true — which vanilla only allows on WATER terrain (and only with a
    // WaterCellCost). The same property also suppresses the ground shadow
    // (PawnRenderer.DrawShadowInternal), which is right for a buried body.
    //
    // So the whole mechanism is one postfix on that getter: for a race carrying
    // RM_SandBuriedGraphicExtension, standing on a sand swim terrain (and, by
    // default, not moving), the swimming slot is drawn. It can only turn a FALSE
    // into TRUE; it never touches movement, pathing, Swimming or WaterCellCost.
    // Corpses are untouched (an unspawned pawn never draws the swim slot).
    // Setting: RM_CreatureBehaviorsSettings.sandBuriedGraphicEnabled (entry 47).
    // ════════════════════════════════════════════════════════════════════
    public class RM_SandBuriedGraphicExtension : DefModExtension
    {
        /// <summary>Terrains the creature buries in. Empty means the sand-swim default set
        /// (Sand, SoftSand, RM_DeepSand — RM_SandSwimUtility.IsSwimTerrain).</summary>
        public List<TerrainDef> buryTerrains;

        /// <summary>True (default): buried only while still — a resting / waiting body. False:
        /// drawn buried whenever it stands on bury terrain, moving or not.</summary>
        public bool onlyWhenStill = true;
    }

    [StaticConstructorOnStartup]
    public static class RM_Patch_SandBuriedGraphic
    {
        public static bool patched;

        static RM_Patch_SandBuriedGraphic()
        {
            var target = AccessTools.PropertyGetter(typeof(Pawn), nameof(Pawn.DrawNonHumanlikeSwimmingGraphic));
            if (target == null)
            {
                Log.Warning("[RM CreatureBehaviors] sand-buried graphic: Pawn.DrawNonHumanlikeSwimmingGraphic not found; buried graphics stay off (vanilla behaviour).");
                return;
            }
            new Harmony("mandrake.rm.creaturebehaviors.sandburied").Patch(target,
                postfix: new HarmonyMethod(typeof(RM_Patch_SandBuriedGraphic), nameof(Postfix)));
            patched = true;
        }

        public static void Postfix(Pawn __instance, ref bool __result)
        {
            if (__result)
            {
                return;
            }
            RM_SandBuriedGraphicExtension ext = __instance.def?.GetModExtension<RM_SandBuriedGraphicExtension>();
            if (ext == null || !__instance.Spawned)
            {
                return;
            }
            PawnKindLifeStage stage = __instance.ageTracker?.CurKindLifeStage;
            bool moving = __instance.pather != null && __instance.pather.Moving;
            bool onTerrain;
            if (ext.buryTerrains != null && ext.buryTerrains.Count > 0)
            {
                TerrainDef t = __instance.Position.GetTerrain(__instance.Map);
                onTerrain = t != null && ext.buryTerrains.Contains(t);
            }
            else
            {
                onTerrain = RM_SandSwimUtility.IsSwimTerrain(__instance.Position, __instance.Map, null);
            }
            __result = RM_SandBuriedGraphic.ShouldDrawBuried(
                RM_CreatureBehaviorsSettings.sandBuriedGraphicEnabled, false, true,
                __instance.RaceProps.Humanlike, stage?.swimmingGraphicData != null,
                ext.onlyWhenStill, moving, onTerrain);
        }
    }
}
