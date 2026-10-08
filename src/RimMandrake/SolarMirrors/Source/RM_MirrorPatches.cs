using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using System.Linq;
using UnityEngine;
using Verse;

namespace RimMandrake.SolarMirrors
{
    // SOLAR_MIRRORS_MOD_DESIGN_1 §2.4 / §5 E1: the two vanilla patches. Shade, exposure and sun
    // path cost are NOT patched: the light reaches CreatureBehaviors' shade grid through its public
    // light-source hook (IRM_LightLayer / RegisterLightSource), implemented by
    // RM_MapComponent_MirrorLight.

    /// <summary>Design §2.4: the one funnel for gameplay glow (plant growth, sowing, work in the
    /// dark). It never brightens the rendered ground; RM_MapComponent_MirrorLight draws that.
    /// PROVISIONAL: glow + light, capped at 1, so the Long Shade's 0.8 sky reads 1.0 in a beam.</summary>
    [HarmonyPatch(typeof(GlowGrid), nameof(GlowGrid.GroundGlowAt))]
    public static class RM_Patch_GlowGrid_GroundGlowAt
    {
        public static void Postfix(IntVec3 c, bool ignoreSky, Map ___map, ref float __result)
        {
            if (ignoreSky || __result >= 1f || !RM_SolarMirrorsSettings.glowEffect)
            {
                return;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(___map);
            if (comp == null || !comp.AnyLight)
            {
                return;
            }
            float l = comp.LightAt(c);
            if (l > 0f)
            {
                __result = Mathf.Min(1f, __result + l);
            }
        }
    }

    /// <summary>Design §5 E1: a light-gated bench (the solar furnace) takes bills only while
    /// concentrated mirror light falls on it. WorkGiver_DoBill and Building_WorkTable's
    /// CurrentlyUsableForBills both go through UsableForBillsAfterFueling.</summary>
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsableForBillsAfterFueling))]
    public static class RM_Patch_WorkTable_UsableForBills
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            RM_CompLightReceiver r = __instance.GetComp<RM_CompLightReceiver>();
            if (r != null && r.Props.gatesBills && !r.BillsAllowed)
            {
                __result = false;
            }
        }
    }

    /// <summary>Design §2.6 / §3.3 (SOLAR_MIRRORS_BUILD_1): concentrated light (several beams, light above 1) adds to the
    /// SAME vanilla felt-temperature offset CreatureBehaviors gives plain sun, capped by the biome's maxHeatOffsetC.
    /// Never a new kind of heat or a new hediff. Runs after CreatureBehaviors' postfix on the same getter.</summary>
    [HarmonyPatch(typeof(Thing), nameof(Thing.AmbientTemperature), MethodType.Getter)]
    public static class RM_Patch_Thing_AmbientTemperature_Concentration
    {
        [HarmonyPriority(Priority.Low)]
        public static void Postfix(Thing __instance, ref float __result)
        {
            if (!RM_SolarMirrorsSettings.concentrationHeat || !(__instance is Pawn pawn) || !pawn.Spawned)
            {
                return;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(pawn.Map);
            if (comp == null || !comp.AnyLight)
            {
                return;
            }
            float l = comp.LightAt(pawn.Position);
            if (l <= 1f)
            {
                return;
            }
            try
            {
                RM_MapComponent_ShadeGrid grid = RM_SunHeatPatches.ActiveGridFor(pawn);
                RM_SunHeatExtension ext = grid?.HeatExtension;
                if (ext == null || grid.EffectiveHeatKind == RM_HeatKind.ambient)
                {
                    return;
                }
                float size = RM_SunHeatMath.BodySizeFactor(pawn.BodySize, ext.bodySizeExponent, ext.minBodySizeFactor, ext.maxBodySizeFactor);
                float perUnit = grid.EffectiveHeatOffsetC * RM_CreatureBehaviorsSettings.sunHeatStrength * size;
                float applied = RM_SunHeatPatches.SunOffsetFor(pawn, grid);
                __result += RM_MirrorKernel.ConcentrationExtraC(l, perUnit, ext.maxHeatOffsetC, applied, RM_SolarMirrorsSettings.concentrationCap);
            }
            catch (System.Exception e)
            {
                Log.ErrorOnce("[RM SolarMirrors] concentration heat: " + e, 0x51A2C0);
            }
        }
    }

    /// <summary>Design §5 E4 (SOLAR_MIRRORS_BUILD_1): a hostile standing in a strong beam shoots worse, unless goggles
    /// or a gene protect the eyes. Added to ShootingAccuracyPawn at startup (RM_SolarMirrorsStartup).</summary>
    public class RM_StatPart_MirrorDazzle : StatPart
    {
        private static float FactorFor(StatRequest req)
        {
            if (!RM_SolarMirrorsSettings.dazzle || !(req.Thing is Pawn p) || !p.Spawned || !p.HostileTo(Faction.OfPlayer))
            {
                return 1f;
            }
            RM_MapComponent_MirrorLight comp = RM_MapComponent_MirrorLight.For(p.Map);
            if (comp == null || !comp.AnyLight)
            {
                return 1f;
            }
            float l = comp.LightAt(p.Position);
            if (l < 0.5f || RM_GlareBlind.EyesProtected(p))
            {
                return 1f;
            }
            return RM_MirrorKernel.DazzleFactor(l, RM_SolarMirrorsSettings.dazzleMaxPenalty);
        }

        public override void TransformValue(StatRequest req, ref float val)
        {
            val *= FactorFor(req);
        }

        public override string ExplanationPart(StatRequest req)
        {
            float f = FactorFor(req);
            return f < 1f ? "RM_SolarMirrors_Dazzle_Explain".Translate() + ": x" + f.ToStringPercent() : null;
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_SolarMirrorsStartup
    {
        static RM_SolarMirrorsStartup()
        {
            StatDef acc = StatDefOf.ShootingAccuracyPawn;
            if (acc != null)
            {
                acc.parts ??= new System.Collections.Generic.List<StatPart>();
                if (!acc.parts.Any(sp => sp is RM_StatPart_MirrorDazzle))
                {
                    acc.parts.Add(new RM_StatPart_MirrorDazzle { parentStat = acc });
                }
            }
            ApplyHeliostatPower();
        }

        private static readonly AccessTools.FieldRef<CompProperties_Power, float> basePower =
            AccessTools.FieldRefAccess<CompProperties_Power, float>("basePowerConsumption");

        /// <summary>The settings dial for heliostat draw (design §3.5), written into every tracking mirror def's power
        /// comp, so the info card and newly built heliostats show it; built ones pick it up on the next light pass.</summary>
        public static void ApplyHeliostatPower()
        {
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                RM_CompProperties_Mirror m = d.GetCompProperties<RM_CompProperties_Mirror>();
                CompProperties_Power p = d.GetCompProperties<CompProperties_Power>();
                if (m != null && m.tracks && p != null)
                {
                    basePower(p) = RM_SolarMirrorsSettings.heliostatPower;
                }
            }
        }
    }
}
