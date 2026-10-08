using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.2/§3.3's numbers. DEEPFIRE_MOD_SETTINGS_1 moved the live-tuned
    // ones into LuminousPigmentSettings (coat radius/intensity, glowMinValue,
    // costs, clustering, worn-glow tick interval, combat/beauty/floor
    // numbers) -- those fields below now serve only as Scribe defaults and
    // as the settings arrays' seed values. The rest (engine-shape constants:
    // stack-split art guard, dark-test thresholds mirroring private GlowGrid
    // math) are not spec §7 keys and stay plain constants here.
    public static class DeepfirePaintDefaults
    {
        // index 0 unused (0 coats = no light); 1..3 coats.
        public static readonly float[] CoatRadius = { 0f, 1.5f, 2.0f, 2.5f };
        public static readonly float[] CoatIntensity = { 0f, 0.45f, 0.70f, 1.00f };

        // HSV value floor so a near-black dye still crosses GlowGrid's
        // GameGlowLitThreshold (0.3f, RimSage-verified Verse/GlowGrid.cs).
        public const float GlowMinValue = 0.45f;

        // DEEPFIRE_FLOOR_PAINT_1 (spec §3.3/§3.5/§3.6, §7 keys clusterBlock,
        // costFloorCell, floorBeautyPerCell, floorRoomBonusPer10,
        // floorRoomBonusCap). Wired to LuminousPigmentSettings by
        // DEEPFIRE_MOD_SETTINGS_1; these are Scribe/seed defaults only.
        // ClusterRadiusBonus is NOT a spec §7 key -- internal tuning, stays
        // a plain constant.
        public const int ClusterBlock = 3;              // 1 = one light per cell/thing
        public const float ClusterRadiusBonus = 1f;     // "radius = coat radius + 1" (only for a cluster of 2+ cells)
        public const int CostFloorCell = 1;
        public const float FloorBeautyPerCell = 0.5f;
        public const float FloorRoomBonusPer10 = 2f;
        public const float FloorRoomBonusCap = 10f;

        // DEEPFIRE_FIRSTCOAT_BONUS_1 (spec §3.5 "everything else" /
        // RM_StatPart_Deepfire on Beauty). Wired to LuminousPigmentSettings
        // by DEEPFIRE_MOD_SETTINGS_1; Scribe/seed defaults only.
        public const float FirstCoatBeautyFlat = 3f;
        public const float FirstCoatBeautyPct = 0.25f;
        public const int FirstCoatBeautySizeCap = 4;

        // DEEPFIRE_WORN_GLOW_1 (spec §3.4, §7 keys wornLightTickInterval,
        // glowTargetFactor, glowDodgePenalty). Wired to LuminousPigmentSettings
        // by DEEPFIRE_MOD_SETTINGS_1; Scribe/seed defaults only.
        // LacquerWorkTicks/LacquerArtisticXP/WornRescanInterval and the
        // dark-test thresholds below are NOT spec §7 keys -- internal tuning.
        public const int WornLightTickInterval = 15;     // cell-change poll for a glowing pawn's proxy
        public const int WornRescanInterval = 250;       // backstop sweep (load, missed notifies, death)
        public const int LacquerWorkTicks = 1000;        // "1000 ticks" at the press / styling station
        public const float LacquerArtisticXP = 100f;     // same as the designator job (paint's own skill)
        public const float GlowTargetFactor = 1.25f;     // ranged: x factorFromTargetSize in the dark
        public const float TargetSizeFactorMin = 0.5f;   // vanilla ShotReport clamp (RimSage Verse/ShotReport.cs)
        public const float TargetSizeFactorMax = 2f;
        public const float GlowDodgePenalty = 0.08f;     // melee: final MeleeDodgeChance offset in the dark

        // "Dark without our light" (spec §3.4): sky glow <= 0.35 outdoors,
        // and the ground glow from every OTHER light < 0.3 (GlowGrid's
        // GameGlowLitThreshold). The last three mirror private GlowGrid /
        // ComputeGlowGridsJob constants (RimSage Verse/GlowGrid.cs,
        // Verse/Glow/ComputeGlowGridsJob.cs SetGlowFromDist) so our own
        // light's contribution at its centre cell can be subtracted.
        public const float DarkSkyGlowMax = 0.35f;
        public const float DarkGroundGlowMax = 0.3f;
        public const float GroundGlowFactor = 3.6f;
        public const float MaxNonOverlitGroundGlow = 0.5f;
        public const float GlowFalloffLerp = 0.4f;
    }

    public static class DeepfireColorUtility
    {
        public static float RadiusForCoats(int coats)
        {
            int i = Mathf.Clamp(coats, 0, CompDeepfire.MaxCoats);
            return LuminousPigmentSettings.coatRadius[i];
        }

        // Spec §3.1: "the glow colour is the draw colour with its HSV value
        // floored at glowMinValue". Spec §3.2: coats scale intensity, not
        // just radius -- table col "intensity (x glow colour)".
        public static Color GlowColorFor(Color drawColor, int coats)
        {
            int i = Mathf.Clamp(coats, 0, CompDeepfire.MaxCoats);
            float intensity = LuminousPigmentSettings.coatIntensity[i];

            Color.RGBToHSV(drawColor, out float h, out float s, out float v);
            v = Mathf.Max(v, LuminousPigmentSettings.glowMinValue);
            Color lit = Color.HSVToRGB(h, s, v);

            return new Color(lit.r * intensity, lit.g * intensity, lit.b * intensity, 1f);
        }
    }

    // DEEPFIRE_MOD_SETTINGS_1, spec §7 "floorsPaintable / wallsPaintable /
    // furniturePaintable / apparelPaintable / weaponsPaintable -- target
    // classes". Floors are gated separately (Designator_Deepfire.
    // CanDesignateFloor -- there is no Thing to classify); this covers
    // everything CanDesignateThing sees. Same class boundaries as
    // DeepfireCostUtility.CostFor, checked in the same order (art items are
    // furniture/apparel/weapons that also carry CompArt -- they follow
    // whichever bucket they'd cost as).
    public static class DeepfireTargetClassUtility
    {
        public static bool IsPaintable(Thing t)
        {
            switch (RM_DeepfireRules.PaintableClassOf(t.def.IsApparel, t.def.IsWeapon, t.def.building != null && t.def.building.isWall))
            {
                case PaintClass.Apparel: return LuminousPigmentSettings.apparelPaintable;
                case PaintClass.Weapon: return LuminousPigmentSettings.weaponsPaintable;
                case PaintClass.Wall: return LuminousPigmentSettings.wallsPaintable;
                default: return LuminousPigmentSettings.furniturePaintable;
            }
        }
    }

    // Spec §3.3's per-target Deepfire cost table and the "find nearby
    // Deepfire" fetch (PaintUtility.FindNearbyDyes shape, our own resource).
    public static class DeepfireCostUtility
    {
        public static int CostFor(Thing t)
        {
            PaintClass pc = RM_DeepfireRules.ClassOf(t.TryGetComp<CompArt>() != null, t.def.IsApparel, t.def.IsWeapon,
                t.def.building != null && t.def.building.isWall);
            return RM_DeepfireRules.Cost(pc, t.def.size.x, t.def.size.z, LuminousPigmentSettings.costArt, LuminousPigmentSettings.costApparel,
                LuminousPigmentSettings.costWeapon, LuminousPigmentSettings.costWallCell, LuminousPigmentSettings.costFurnitureBase,
                LuminousPigmentSettings.costFurniturePerExtraCell, LuminousPigmentSettings.costFurnitureCap);
        }

        // Single-stack fetch (MVP for step 5's proof) -- the stack must hold
        // the whole cost on its own. Multi-stack queueing (vanilla
        // WorkGiver_PaintBuilding's own shape) is a nice-to-have, not
        // required by any step-5 proof row.
        public static Thing FindNearbyDeepfire(Pawn pawn, int minCount, bool forced)
        {
            ThingDef deepfireDef = ThingDef.Named("RM_Deepfire");
            if (deepfireDef == null) return null;

            List<Thing> list = pawn.Map.listerThings.ThingsOfDef(deepfireDef);
            Thing best = null;
            int bestDist = int.MaxValue;
            for (int i = 0; i < list.Count; i++)
            {
                Thing th = list[i];
                if (th.stackCount < minCount) continue;
                if (th.IsForbidden(pawn)) continue;
                if (!pawn.CanReserveAndReach(th, PathEndMode.ClosestTouch, Danger.Some, 1, -1, null, forced)) continue;

                int d = (th.Position - pawn.Position).LengthHorizontalSquared;
                if (d < bestDist)
                {
                    bestDist = d;
                    best = th;
                }
            }
            return best;
        }
    }
}
