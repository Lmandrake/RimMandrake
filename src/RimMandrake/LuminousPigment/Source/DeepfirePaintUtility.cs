using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.2/§3.3's numbers. Plain constants, not Mod Settings yet --
    // wiring sliders for these is spec §10 step 12's job (Mod Settings
    // screen), explicitly out of scope for step 5. Move these into
    // LuminousPigmentSettings when that step lands; nothing here should be
    // read from two places once it does.
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
        // floorRoomBonusCap). Settings wiring is DEEPFIRE_MOD_SETTINGS_1's.
        public const int ClusterBlock = 3;              // 1 = one light per cell/thing
        public const float ClusterRadiusBonus = 1f;     // "radius = coat radius + 1" (only for a cluster of 2+ cells)
        public const int CostFloorCell = 1;
        public const float FloorBeautyPerCell = 0.5f;
        public const float FloorRoomBonusPer10 = 2f;
        public const float FloorRoomBonusCap = 10f;

        // DEEPFIRE_FIRSTCOAT_BONUS_1 (spec §3.5 "everything else" /
        // RM_StatPart_Deepfire on Beauty). Settings wiring is
        // DEEPFIRE_MOD_SETTINGS_1's.
        public const float FirstCoatBeautyFlat = 3f;
        public const float FirstCoatBeautyPct = 0.25f;
        public const int FirstCoatBeautySizeCap = 4;

        // DEEPFIRE_WORN_GLOW_1 (spec §3.4, §7 keys wornLightTickInterval,
        // glowTargetFactor, glowDodgePenalty). Settings wiring is
        // DEEPFIRE_MOD_SETTINGS_1's.
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
            return DeepfirePaintDefaults.CoatRadius[i];
        }

        // Spec §3.1: "the glow colour is the draw colour with its HSV value
        // floored at glowMinValue". Spec §3.2: coats scale intensity, not
        // just radius -- table col "intensity (x glow colour)".
        public static Color GlowColorFor(Color drawColor, int coats)
        {
            int i = Mathf.Clamp(coats, 0, CompDeepfire.MaxCoats);
            float intensity = DeepfirePaintDefaults.CoatIntensity[i];

            Color.RGBToHSV(drawColor, out float h, out float s, out float v);
            v = Mathf.Max(v, DeepfirePaintDefaults.GlowMinValue);
            Color lit = Color.HSVToRGB(h, s, v);

            return new Color(lit.r * intensity, lit.g * intensity, lit.b * intensity, 1f);
        }
    }

    // Spec §3.3's per-target Deepfire cost table and the "find nearby
    // Deepfire" fetch (PaintUtility.FindNearbyDyes shape, our own resource).
    public static class DeepfireCostUtility
    {
        public static int CostFor(Thing t)
        {
            if (t.TryGetComp<CompArt>() != null) return 3; // art item
            if (t.def.IsApparel) return 3;
            if (t.def.IsWeapon) return 3;
            if (t.def.building != null && t.def.building.isWall) return 1; // wall cell

            // furniture/building: 1x1 = 2, larger = 2 + 1/extra cell, cap 6.
            int cells = System.Math.Max(1, t.def.size.x * t.def.size.z);
            if (cells <= 1) return 2;
            return System.Math.Min(6, 2 + (cells - 1));
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
