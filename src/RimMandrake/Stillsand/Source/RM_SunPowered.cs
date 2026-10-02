using System.Collections.Generic;
using HarmonyLib;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_GLASS_LENS_CHAIN_1 §3, §4, §6 — sun-fed work tables.
    //
    // The sun furnace, the lens bench and the solar oven burn no fuel and draw
    // no power: the sun is their fuel. One comp carries the rule, two hooks
    // enforce it:
    //   - a Harmony postfix on Building_WorkTable.UsableForBillsAfterFueling,
    //     which both WorkGiver_DoBill (start) and JobDriver_DoBill's FailOn
    //     (CurrentlyUsableForBills → UsableForBillsAfterFueling) read, so a
    //     sun table refuses bills in shade, at night or in the gale and a job
    //     already running stops when the sun goes;
    //   - RM_StatPart_SunPowered on WorkTableWorkSpeedFactor (patched in by
    //     Patches/RM_GlassChain_StatParts.xml), so output scales with the sun.
    //
    // Sun: on a pinned-sun map (CreatureBehaviors' RM_MapComponent_PinnedSun)
    // the intensity is sin(elevation) of the fixed sun, i.e. it scales with the
    // tile's latitude; anywhere else it is vanilla's sky glow. Shade: roofed
    // cells are dark; on a sun-heat map the shade grid's ShadeAt (roof, cast
    // and gear shade) dims it further. The tables themselves are defined with
    // fillPercent under the grid's caster threshold, so they never shade
    // their own cell. Weathers that block the sun are listed BY NAME (the
    // gale is STILLSAND_DUNE_GALE_1's and may not exist yet), the same rule
    // the muurrok's mirror beam uses.
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_SunPowered : CompProperties
    {
        /// <summary>Below this sun factor (0..1) the table cannot work at all.</summary>
        public float minSunFactor = 0.3f;

        /// <summary>When true, work speed scales with the sun factor (full sun = 1).
        /// When false, the sun is only a gate (the lens bench).</summary>
        public bool scaleWorkSpeed = true;

        /// <summary>Work speed multiplier at full sun, before the settings slider.</summary>
        public float workSpeedAtFullSun = 1f;

        /// <summary>WeatherDef defNames that stop the table outright.</summary>
        public List<string> noSunWeathers = new List<string> { "Sandstorm", "RM_DuneGale", "RM_Gale" };

        /// <summary>Which Mod Settings toggle gates this table.</summary>
        public RM_SunTableKind kind = RM_SunTableKind.furnace;

        public RM_CompProperties_SunPowered()
        {
            compClass = typeof(RM_CompSunPowered);
        }
    }

    public enum RM_SunTableKind
    {
        furnace,
        lensBench,
        oven,
    }

    public class RM_CompSunPowered : ThingComp
    {
        private const int RecheckIntervalTicks = 120;

        private int lastCheckTick = -99999;
        private float cachedFactor;
        private string cachedReason;

        public RM_CompProperties_SunPowered Props => (RM_CompProperties_SunPowered)props;

        public bool EnabledInSettings => RM_GlassChainSettings.TableEnabled(Props.kind);

        /// <summary>0..1: how much usable sun reaches this table right now.</summary>
        public float SunFactor
        {
            get
            {
                Refresh();
                return cachedFactor;
            }
        }

        public bool CanWork => EnabledInSettings && SunFactor >= Props.minSunFactor;

        /// <summary>Multiplier on WorkTableWorkSpeedFactor.</summary>
        public float WorkSpeedFactor
        {
            get
            {
                if (!Props.scaleWorkSpeed)
                {
                    return 1f;
                }
                return Mathf.Max(0.05f, SunFactor) * Props.workSpeedAtFullSun
                       * RM_GlassChainSettings.sunWorkSpeedMultiplier;
            }
        }

        private void Refresh()
        {
            int now = Find.TickManager?.TicksGame ?? 0;
            if (now - lastCheckTick < RecheckIntervalTicks)
            {
                return;
            }
            lastCheckTick = now;
            cachedFactor = RM_SunPower.FactorAt(parent, Props.noSunWeathers, out cachedReason);
        }

        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            if (!EnabledInSettings)
            {
                return "Disabled in Mod Settings (Stillsand: glass and lenses).";
            }
            float f = SunFactor;
            if (f < Props.minSunFactor)
            {
                return "Not working: " + (cachedReason ?? "too little sun") + " (sun "
                       + f.ToStringPercent() + ", needs " + Props.minSunFactor.ToStringPercent() + ").";
            }
            return "Sun: " + f.ToStringPercent()
                   + (Props.scaleWorkSpeed ? " (work speed x" + WorkSpeedFactor.ToStringPercent() + ")" : "");
        }
    }

    public static class RM_SunPower
    {
        /// <summary>Sun intensity 0..1 over the whole map, before shade and weather.</summary>
        public static float Intensity(Map map)
        {
            if (map == null)
            {
                return 0f;
            }
            RM_MapComponent_PinnedSun pinned = RM_MapComponent_PinnedSun.For(map);
            if (pinned != null && pinned.IsActive)
            {
                float elev = pinned.SunElevationDegrees;
                if (float.IsNaN(elev))
                {
                    return 0f;
                }
                return Mathf.Clamp01(Mathf.Sin(elev * Mathf.Deg2Rad));
            }
            return Mathf.Clamp01(GenCelestial.CurCelestialSunGlow(map));
        }

        /// <summary>Usable sun at a thing's position, 0..1, with the reason it is low.</summary>
        public static float FactorAt(Thing t, List<string> noSunWeathers, out string reason)
        {
            reason = null;
            Map map = t?.Map;
            if (map == null || !t.Spawned)
            {
                reason = "not spawned";
                return 0f;
            }
            IntVec3 c = t.Position;
            if (c.Roofed(map))
            {
                reason = "under a roof";
                return 0f;
            }
            WeatherDef w = map.weatherManager?.curWeather;
            if (w != null && noSunWeathers != null && noSunWeathers.Contains(w.defName))
            {
                reason = "the sun is blotted out (" + w.label + ")";
                return 0f;
            }
            float sun = Intensity(map);
            if (sun <= 0f)
            {
                reason = "no sun";
                return 0f;
            }
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            float shade = grid != null ? Mathf.Clamp01(grid.ShadeAt(c)) : 0f;
            float f = sun * (1f - shade);
            if (shade >= 0.5f)
            {
                reason = "in shade";
            }
            else if (f < 0.3f)
            {
                reason = "the sun is too low";
            }
            return f;
        }
    }

    /// <summary>Scales a sun table's work speed with the sun, and cancels the vanilla
    /// outdoor and bad-temperature penalties for it: a sun table only works outdoors
    /// in the heat, so penalising it for both would be charging it for being itself.</summary>
    public class RM_StatPart_SunPowered : StatPart
    {
        public override void TransformValue(StatRequest req, ref float val)
        {
            if (!req.HasThing || !(req.Thing.TryGetComp<RM_CompSunPowered>() is RM_CompSunPowered comp))
            {
                return;
            }
            if (StatPart_WorkTableOutdoors.Applies(req.Thing))
            {
                val /= StatPart_WorkTableOutdoors.WorkRateFactor;
            }
            if (StatPart_WorkTableTemperature.Applies(req.Thing))
            {
                val /= StatPart_WorkTableTemperature.WorkRateFactor;
            }
            if (req.Thing.Spawned)
            {
                val *= comp.WorkSpeedFactor;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            if (!req.HasThing || !(req.Thing.TryGetComp<RM_CompSunPowered>() is RM_CompSunPowered comp)
                || !req.Thing.Spawned)
            {
                return null;
            }
            return "Sun-fed (outdoor and heat penalties do not apply): x" + comp.WorkSpeedFactor.ToStringPercent();
        }
    }

    /// <summary>Building_WorkTable.UsableForBillsAfterFueling is not virtual, so the sun
    /// gate is a postfix. Armed from RM_GlassChainMod's constructor.</summary>
    public static class Patch_WorkTable_SunGate
    {
        public static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            if (!__result)
            {
                return;
            }
            RM_CompSunPowered comp = __instance.TryGetComp<RM_CompSunPowered>();
            if (comp != null && !comp.CanWork)
            {
                __result = false;
            }
        }
    }
}
