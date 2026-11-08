using System;
using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>
    /// Ash is vanilla Odyssey sand on a map fire ecology runs on (the Pyrelands, or a biome opted in by the cross-biome setting).
    /// Owner, by card, 2026-11-08: "Rebuild ash on vanilla sand?" -> "Yes, rebuild on sand". The same morning on map x: "It seems
    /// like it's accumulating very slowly. If this were snow, I would have expected it to get thicker much faster."
    /// So ash is the map's SandGrid depth (0..1), laid and lost by vanilla's own code wherever it can be:
    ///   ash fall    the weather's own sandRate (AshFall.xml 1.2, heavy snow's snowRate; Cinderfall 0.54), deposited by
    ///               SteadyEnvironmentEffects.AddFallenSandAt, snow's path: 0.046 x rate x noise(0.5..1) a visit, a visit every
    ///               ~1,667 ticks, so ~0.048 depth a game hour at 1.2, as heavy snow. The rate setting and toggle scale it here.
    ///   fire        a burning cell's ash, one drift level (0.25) a dusting up to its drift-field target (FireEcologyHook.cs).
    ///   black rain  vanilla wears open-sky sand 1/180 a visit whenever none falls (5 days for a full cover). On an ash map that
    ///               wear is replaced: half of it dry (ash stays ~10 days) and 0.25 x rainRate on top, so black rain clears a
    ///               full cover in ~2.5 hours. Indoor and roofed cells keep vanilla's rules.
    ///   clearing    vanilla's clear-snow-and-sand job in the snow/sand clear area, untouched.
    ///   look        vanilla's SectionLayer_Sand draws snow's geometry (nine half-cell vertices a cell, the depth as the vertex
    ///               alpha; Verse/SectionLayer_Snow.cs is the same code), which read as fog on map x when snow's material was
    ///               tried for ash (shots cover1, t1-t16). So on an ash map it draws nothing and SectionLayer_PyrelandsAsh draws
    ///               the depth as the ash cover (its texture, frayed edge and tints of de23b05e44). Odyssey sand on every other
    ///               map is vanilla's in every respect.
    ///   footprints  CreatureBehaviors' track grid, the Stillsand's: the Pyrelands' BiomeDef carries an RM_TrackSurfaceExtension
    ///               with minSandDepth, so ash that deep takes prints and the grid buries or clears them as the ash moves.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsAsh
    {
        private const string NativeBiomeDefName = "RM_Pyrelands";

        private static WeatherDef ashFall, cinderfall;
        private static bool weathersResolved;

        // The cell SteadyEnvironmentEffects.DoCellSteadyEffects is visiting, so the SandGrid.AddDepth prefix can tell vanilla's
        // open-sky wear from every other writer. Main thread only, as the steady effects are.
        private static Map steadyMap;
        private static IntVec3 steadyCell;

        /// <summary>Session counters for the bridge (never saved).</summary>
        public static int WearReplaced, SandLayersSkipped;

        static PyrelandsAsh()
        {
            const string rule = "[RimMandrake.Pyrelands] ash on sand: ";
            if (!ModsConfig.OdysseyActive)
            {
                Log.Warning(rule + "Odyssey is not active, so there is no sand grid: the Pyrelands lays no ash on the ground.");
                return;
            }
            var h = new Harmony("mandrake.rm.pyrelands.ashsand");
            Patch(h, AccessTools.PropertyGetter(typeof(WeatherManager), nameof(WeatherManager.SandRate)), null,
                nameof(Postfix_SandRate), null, rule + "WeatherManager.SandRate", "ash fall lays no ash");
            Patch(h, AccessTools.Method(typeof(SteadyEnvironmentEffects), "DoCellSteadyEffects"), nameof(Prefix_DoCellSteadyEffects),
                null, nameof(Finalizer_DoCellSteadyEffects), rule + "SteadyEnvironmentEffects.DoCellSteadyEffects",
                "ash wears away as vanilla sand does and black rain does not wash it");
            Patch(h, AccessTools.Method(typeof(SandGrid), nameof(SandGrid.AddDepth)), nameof(Prefix_AddDepth), null, null,
                rule + "SandGrid.AddDepth", "ash wears away as vanilla sand does and black rain does not wash it");
            Patch(h, AccessTools.Method(typeof(SectionLayer_Sand), nameof(SectionLayer_Sand.Regenerate)), nameof(Prefix_SandLayer),
                null, null, rule + "SectionLayer_Sand.Regenerate", "vanilla sand draws over the ash cover");
            PatchLabels(h, rule);
        }

        private static void Patch(Harmony h, System.Reflection.MethodBase target, string prefix, string postfix, string finalizer,
            string what, string lost)
        {
            if (target == null)
            {
                Log.Error(what + " NOT FOUND, " + lost + ".");
                return;
            }
            try
            {
                h.Patch(target,
                    prefix: prefix != null ? new HarmonyMethod(typeof(PyrelandsAsh), prefix) : null,
                    postfix: postfix != null ? new HarmonyMethod(typeof(PyrelandsAsh), postfix) : null,
                    finalizer: finalizer != null ? new HarmonyMethod(typeof(PyrelandsAsh), finalizer) : null);
            }
            catch (Exception e)
            {
                Log.Error(what + " patch FAILED, " + lost + ": " + e.Message);
            }
        }

        // ── reads ────────────────────────────────────────────────────────

        /// <summary>Does this map's sand grid hold ash (drawn as ash, footprinted as ash)? Fire ecology runs on it and Odyssey's
        /// grid exists. The look follows this alone, so ash already lying stays ash with the mechanics toggle off.</summary>
        public static bool IsAshMap(Map map)
        {
            return map != null && map.sandGrid != null && ModsConfig.OdysseyActive && FireEcologyBiomeGate.On(map);
        }

        /// <summary>Do ash mechanics run on this map (laying, the slower wear, the rain's wash)? The Pyrelands toggle AND an ash map.</summary>
        public static bool AshRuns(Map map)
        {
            return PyrelandsMechanicsGate.On && IsAshMap(map);
        }

        public static float Depth(Map map, IntVec3 c)
        {
            return map?.sandGrid != null && ModsConfig.OdysseyActive ? map.sandGrid.GetDepth(c) : 0f;
        }

        /// <summary>Raise a cell's ash to <paramref name="depth"/>, never lowering it. Goes through SandGrid.AddDepth, so a wall or a
        /// sand terrain takes none and the mesh, path cost and track grid hear of it.</summary>
        public static void RaiseTo(Map map, IntVec3 c, float depth)
        {
            if (map?.sandGrid == null || !ModsConfig.OdysseyActive || !c.InBounds(map)) return;
            float have = map.sandGrid.GetDepth(c);
            if (depth > have + RM_FireEcoKernel.AshDepthEpsilon) map.sandGrid.AddDepth(c, Mathf.Min(1f, depth) - have);
        }

        private static void ResolveWeathers()
        {
            weathersResolved = true;
            ashFall = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_AshFall");
            cinderfall = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_Cinderfall");
        }

        private static bool IsAshWeather(WeatherDef w)
        {
            return w != null && (w == ashFall || w == cinderfall);
        }

        // ── patches ──────────────────────────────────────────────────────

        /// <summary>The ash weathers' share of the map's sand rate, scaled by the rate setting on an ash map with ash fall on and
        /// zeroed otherwise; plus an opted-in foreign biome's ambient ash. Any other weather's sand is vanilla's.</summary>
        public static void Postfix_SandRate(WeatherManager __instance, ref float __result)
        {
            if (!weathersResolved) ResolveWeathers();
            WeatherDef cur = __instance.curWeather, last = __instance.lastWeather;
            bool curAsh = IsAshWeather(cur), lastAsh = IsAshWeather(last);
            bool ambientMay = RM_PyrelandsSettings.crossBiomeEnabled;
            if (!curAsh && !lastAsh && !ambientMay) return;
            Map map = __instance.map;
            float rate = __result;
            if (curAsh || lastAsh)
            {
                float ashPart = Mathf.Lerp(lastAsh ? last.sandRate : 0f, curAsh ? cur.sandRate : 0f, __instance.TransitionLerpFactor);
                rate = rate - ashPart + RM_FireEcoKernel.AshWeatherSandRate(ashPart, AshRuns(map),
                    RM_PyrelandsSettings.ashfallAccumulationEnabled, RM_PyrelandsSettings.ashfallRateMultiplier);
            }
            if (ambientMay && map != null && ashFall != null && AshRuns(map))
            {
                float ambient = RM_FireEcoKernel.AmbientAshSandRate(true, map.Biome?.defName == NativeBiomeDefName,
                    RM_PyrelandsSettings.ashfallAccumulationEnabled, RM_PyrelandsSettings.crossBiomeCoverage, ashFall.sandRate,
                    RM_PyrelandsSettings.ashfallRateMultiplier, map.sandGrid.TotalDepth / Mathf.Max(1, map.Area));
                if (ambient > rate) rate = ambient;
            }
            __result = rate < 0f ? 0f : rate;
        }

        public static void Prefix_DoCellSteadyEffects(Map ___map, IntVec3 c)
        {
            steadyMap = ___map;
            steadyCell = c;
        }

        public static Exception Finalizer_DoCellSteadyEffects(Exception __exception)
        {
            steadyMap = null;
            return __exception;
        }

        /// <summary>Vanilla's open-sky sand wear (SteadyEnvironmentEffects: -1/180 on an unroofed outdoor cell when no sand falls)
        /// becomes the ash wear on an ash map: half of it dry, plus the rain's wash. Every other writer passes untouched.</summary>
        public static void Prefix_AddDepth(IntVec3 c, ref float depthToAdd)
        {
            Map map = steadyMap;
            if (map == null || depthToAdd != -RM_FireEcoKernel.VanillaSandWear || c != steadyCell || !AshRuns(map)) return;
            if (map.roofGrid.Roofed(c)) return;
            Room room = c.GetRoom(map);
            if (room != null && !room.UsesOutdoorTemperature) return;
            depthToAdd = -RM_FireEcoKernel.OutdoorSandWear(true, map.weatherManager.RainRate);
            WearReplaced++;
        }

        // SectionLayer.section is protected; read through a field ref resolved once (a rename fails the static ctor's patch loudly).
        private static readonly AccessTools.FieldRef<SectionLayer, Section> SectionOf = AccessTools.FieldRefAccess<SectionLayer, Section>("section");

        /// <summary>On an ash map vanilla's sand layer draws nothing: SectionLayer_PyrelandsAsh draws the same depth as ash.</summary>
        public static bool Prefix_SandLayer(SectionLayer_Sand __instance)
        {
            if (!IsAshMap(SectionOf(__instance)?.map)) return true;
            for (int i = 0; i < __instance.subMeshes.Count; i++)
            {
                __instance.subMeshes[i].Clear(MeshParts.All);
                __instance.subMeshes[i].disabled = true;
            }
            SandLayersSkipped++;
            return false;
        }

        // ── the hover label ──────────────────────────────────────────────
        // Owner, 2026-11-08, on the first ash-on-sand build: "Oops. It says "Windswept sand" on my hover over". Vanilla names
        // the sand grid in two places, both with Odyssey's keys: MouseoverReadout.MouseoverReadoutOnGUI ("Sand".Translate() +
        // " (thin) (walk speed ..)", bottom left) and CellInspectorDrawer.DrawMapInspector ("Sand_Label".Translate(), the cell
        // inspector's row). Both keys read "Windswept sand". A transpiler puts AshLabelKey after each ldstr, so on an ash map
        // the key becomes ours ("Ash") and vanilla's depth words (dusting/thin/medium/thick, WeatherBuildupUtility.
        // GetSandDescription, same bands) and walk speed follow unchanged. Every other map keeps Odyssey's text.

        /// <summary>The vanilla sand-label keys and our ash keys (Languages/English/Keyed/Pyrelands.xml).</summary>
        public const string SandKey = "Sand", SandLabelKey = "Sand_Label", KeyAsh = "RM_Ash", KeyAshLabel = "RM_Ash_Label";

        /// <summary>Sand-label sites the transpiler rewrote, one per Harmony run of it (2 after load; more if another mod
        /// re-patches a site). A bridge read, never saved.</summary>
        public static int LabelSitesPatched;

        /// <summary>The key vanilla should translate for the sand grid's label on the current map: ours on an ash map.</summary>
        public static string AshLabelKey(string vanillaKey)
        {
            if (!IsAshMap(Find.CurrentMap)) return vanillaKey;
            if (vanillaKey == SandLabelKey) return KeyAshLabel;
            if (vanillaKey == SandKey) return KeyAsh;
            return vanillaKey;
        }

        private static void PatchLabels(Harmony h, string rule)
        {
            PatchLabel(h, rule, AccessTools.Method(typeof(MouseoverReadout), nameof(MouseoverReadout.MouseoverReadoutOnGUI)));
            PatchLabel(h, rule, AccessTools.Method(typeof(CellInspectorDrawer), "DrawMapInspector"));
        }

        private static void PatchLabel(Harmony h, string rule, MethodInfo target)
        {
            string what = rule + (target == null ? "a sand-label site" : target.DeclaringType.Name + "." + target.Name);
            if (target == null)
            {
                Log.Error(what + " NOT FOUND, the hover on ash reads \"Windswept sand\".");
                return;
            }
            try
            {
                h.Patch(target, transpiler: new HarmonyMethod(typeof(PyrelandsAsh), nameof(Transpile_SandLabel)));
            }
            catch (Exception e)
            {
                Log.Error(what + " patch FAILED, the hover on ash reads \"Windswept sand\": " + e.Message);
            }
        }

        // The key each site carries, by its declaring type. Not handed over in a static: Harmony re-runs every transpiler on a
        // method whenever any mod patches that method again, long after PatchLabels.
        private static string SiteKey(MethodBase original) => original?.DeclaringType == typeof(MouseoverReadout) ? SandKey : SandLabelKey;

        public static IEnumerable<CodeInstruction> Transpile_SandLabel(IEnumerable<CodeInstruction> instructions, MethodBase original)
        {
            var mapper = AccessTools.Method(typeof(PyrelandsAsh), nameof(AshLabelKey));
            string want = SiteKey(original);
            int hits = 0;
            foreach (CodeInstruction ci in instructions)
            {
                yield return ci;
                if (ci.opcode == OpCodes.Ldstr && ci.operand is string s && s == want)
                {
                    hits++;
                    yield return new CodeInstruction(OpCodes.Call, mapper);
                }
            }
            if (hits != 1)
                Log.Error("[RimMandrake.Pyrelands] ash on sand: " + original?.DeclaringType?.Name + "." + original?.Name + " has " + hits
                          + " ldstr \"" + want + "\" (want 1): the vanilla code changed, the hover on ash may read \"Windswept sand\".");
            else LabelSitesPatched++;
        }

        // ── bridge reads (jawa/static_call) ──────────────────────────────

        /// <summary>The ash on the CURRENT map over <paramref name="rect"/> ("x,z,w,h", or "all"): "cells=N;ashed=N;deep=N;depthSum=F;
        /// max=F;ashMap=B;runs=B;sandRate=F;weather=D;wearReplaced=N". ashed = at least the visible depth (0.03); deep = at least
        /// one old drift level (0.25).</summary>
        public static string ProbeAsh(string rect)
        {
            Map m = Find.CurrentMap;
            if (m == null) return "error=no map";
            if (!TryRect(m, rect, out CellRect r)) return "error=bad rect '" + rect + "' (want x,z,w,h or all)";
            int cells = 0, ashed = 0, deep = 0;
            double sum = 0;
            float max = 0f;
            foreach (IntVec3 c in r)
            {
                float d = Depth(m, c);
                cells++;
                sum += d;
                if (d > max) max = d;
                if (d >= RM_FireEcoKernel.AshVisibleDepth) ashed++;
                if (d >= RM_FireEcoKernel.AshDepthPerLevel - RM_FireEcoKernel.AshDepthEpsilon) deep++;
            }
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "cells={0};ashed={1};deep={2};depthSum={3:0.000};max={4:0.000};ashMap={5};runs={6};sandRate={7:0.000};weather={8};wearReplaced={9}",
                cells, ashed, deep, sum, max, IsAshMap(m), AshRuns(m), m.weatherManager?.SandRate ?? 0f,
                m.weatherManager?.curWeather?.defName, WearReplaced);
        }

        /// <summary>Harness reset (jawa/static_call): every cell of the CURRENT map to no ash. Returns the cells that held some.</summary>
        public static int ClearAsh()
        {
            Map m = Find.CurrentMap;
            if (m?.sandGrid == null || !ModsConfig.OdysseyActive) return -1;
            int n = 0;
            foreach (IntVec3 c in m.AllCells)
            {
                if (m.sandGrid.GetDepth(c) <= 0f) continue;
                m.sandGrid.SetDepth(c, 0f);
                n++;
            }
            return n;
        }

        /// <summary>Review staging (jawa/static_call): raise the ash over <paramref name="rect"/> ("x,z,w,h") on the CURRENT map to
        /// <paramref name="depth"/>. Returns the cells that took it (a wall or a sand terrain takes none).</summary>
        public static int LayAsh(string rect, float depth)
        {
            Map m = Find.CurrentMap;
            if (m == null || !TryRect(m, rect, out CellRect r)) return -1;
            int n = 0;
            foreach (IntVec3 c in r)
            {
                RaiseTo(m, c, depth);
                if (Depth(m, c) >= depth - RM_FireEcoKernel.AshDepthEpsilon) n++;
            }
            return n;
        }

        private static bool TryRect(Map m, string rect, out CellRect r)
        {
            r = CellRect.Empty;
            if (rect.NullOrEmpty() || rect.Trim() == "all")
            {
                r = new CellRect(0, 0, m.Size.x, m.Size.z);
                return true;
            }
            string[] p = rect.Split(',');
            if (p.Length != 4 || !int.TryParse(p[0], out int x) || !int.TryParse(p[1], out int z) || !int.TryParse(p[2], out int w)
                || !int.TryParse(p[3], out int hgt) || w <= 0 || hgt <= 0)
            {
                return false;
            }
            r = new CellRect(x, z, w, hgt).ClipInsideMap(m);
            return true;
        }
    }
}
