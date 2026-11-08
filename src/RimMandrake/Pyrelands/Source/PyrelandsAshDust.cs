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
    /// <summary>Plant def extension: the ash-dust overlay for each graphic the plant draws (a Graphic_Random folder, a staged
    /// folder), printed over the plant while its cell holds a loose-ash drift. Same file names as the base, so the random
    /// variant index matches. A graphic with no pair (the charred leafless one) takes no dust.</summary>
    public class RM_AshDustExtension : DefModExtension
    {
        public List<RM_AshDustPair> overlays = new List<RM_AshDustPair>();
    }

    public class RM_AshDustPair
    {
        public string basePath;
        public string overlayPath;
    }

    /// <summary>
    /// Ash fall lays loose-ash filth, and filth draws below LowPlant: on map w (2026-11-08) a six-hour ash fall laid ~3,000
    /// drifts on the grass carpet and a player saw none of them (shots/af_s1_4.png). Vanilla already prints a second,
    /// silhouette-matched plane over a plant when its cell's snow is deep (Plant.Print: GetSnowDepth &gt; 0.8, then
    /// SnowOverlayGraphic). A transpiler swaps those two reads for ours, so a dusted grass cell prints its ash overlay through
    /// vanilla's own code path, at vanilla's own positions and wind sway: light at one layer of ash, full at two or more. Snow
    /// still wins where it lies. The filth's own spawn, thickening, washing and expiry dirty the section mesh, so the dust comes
    /// and goes with the drift (black rain washes it off the grass).
    /// Outdoor ash on natural ground is the land, not dirt (BeautyOutdoors 0): nobody sweeps the grass or the yard after a
    /// fall unless ordered. Floors and roofed cells are still cleaned.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class PyrelandsAshDust
    {
        private const float LightAlpha = 0.6f;
        private static readonly Dictionary<Graphic, Graphic[]> pairs = new Dictionary<Graphic, Graphic[]>();
        private static readonly Dictionary<ThingDef, RM_AshDustExtension> exts = new Dictionary<ThingDef, RM_AshDustExtension>();
        private static int swappedDepth, swappedOverlay;

        static PyrelandsAshDust()
        {
            var h = new Harmony("mandrake.rm.pyrelands.ashdust");
            try
            {
                h.Patch(AccessTools.Method(typeof(Plant), nameof(Plant.Print)),
                    transpiler: new HarmonyMethod(typeof(PyrelandsAshDust), nameof(Transpiler_Print)));
                if (swappedDepth == 0 || swappedOverlay == 0)
                {
                    Log.Error("[RimMandrake.Pyrelands] ash dust: Plant.Print no longer reads GetSnowDepth/SnowOverlayGraphic ("
                              + swappedDepth + ", " + swappedOverlay + " swapped); ash on grass will not show.");
                }
                else
                {
                    Log.Message("[RimMandrake.Pyrelands] ash dust: armed; grass on a loose-ash drift prints its ash overlay ("
                                + swappedDepth + "+" + swappedOverlay + " reads swapped)");
                }
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] ash dust: Plant.Print patch FAILED, ash on grass will not show: " + e.Message);
            }
            try
            {
                h.Patch(AccessTools.Method(typeof(WorkGiver_CleanFilth), nameof(WorkGiver_CleanFilth.HasJobOnThing)),
                    postfix: new HarmonyMethod(typeof(PyrelandsAshDust), nameof(Postfix_CleanFilth)));
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] ash dust: cleaning patch FAILED, colonists will sweep ash off the grass: " + e.Message);
            }
        }

        public static IEnumerable<CodeInstruction> Transpiler_Print(IEnumerable<CodeInstruction> codes)
        {
            MethodInfo snowDepth = AccessTools.Method(typeof(GridsUtility), nameof(GridsUtility.GetSnowDepth));
            MethodInfo snowOverlay = AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.SnowOverlayGraphic));
            MethodInfo ourDepth = AccessTools.Method(typeof(PyrelandsAshDust), nameof(SnowOrDustDepth));
            MethodInfo ourOverlay = AccessTools.Method(typeof(PyrelandsAshDust), nameof(OverlayFor));
            foreach (CodeInstruction ci in codes)
            {
                if (ci.Calls(snowDepth))
                {
                    ci.opcode = OpCodes.Call;
                    ci.operand = ourDepth;
                    swappedDepth++;
                }
                else if (ci.Calls(snowOverlay))
                {
                    ci.opcode = OpCodes.Call;
                    ci.operand = ourOverlay;
                    swappedOverlay++;
                }
                yield return ci;
            }
        }

        private static RM_AshDustExtension ExtOf(ThingDef def)
        {
            if (def == null) return null;
            if (!exts.TryGetValue(def, out RM_AshDustExtension ext))
            {
                ext = def.GetModExtension<RM_AshDustExtension>();
                exts[def] = ext;
            }
            return ext;
        }

        /// <summary>The loose-ash thickness dusting this plant, 0 for none (or no overlay for its def).</summary>
        private static int DustOn(Plant p, Map map, IntVec3 c)
        {
            if (p == null || map == null || ExtOf(p.def) == null || !c.InBounds(map)) return 0;
            return PyrelandsDriftField.Thickness(map, c);
        }

        /// <summary>Plant.Print's snow read: real snow first, else "deep" on a dusted grass cell so the overlay prints.</summary>
        public static float SnowOrDustDepth(IntVec3 c, Map map)
        {
            float snow = c.GetSnowDepth(map);
            if (snow > 0.8f) return snow;
            return DustOn(c.GetPlant(map), map, c) > 0 ? 1f : snow;
        }

        /// <summary>Plant.Print's overlay read: the snow overlay under deep snow, else the ash overlay for the drawn graphic.</summary>
        public static Graphic OverlayFor(Plant p)
        {
            Map map = p.Map;
            if (map == null || p.Position.GetSnowDepth(map) > 0.8f) return p.SnowOverlayGraphic;
            int thick = DustOn(p, map, p.Position);
            if (thick <= 0) return p.SnowOverlayGraphic;
            Graphic[] pair = PairFor(p);
            return pair == null ? null : pair[thick >= 2 ? 1 : 0];
        }

        private static Graphic[] PairFor(Plant p)
        {
            Graphic g = p.Graphic;
            if (g == null) return null;
            if (pairs.TryGetValue(g, out Graphic[] pair)) return pair;
            pair = null;
            RM_AshDustExtension ext = ExtOf(p.def);
            if (ext?.overlays != null)
            {
                foreach (RM_AshDustPair o in ext.overlays)
                {
                    if (o == null || o.overlayPath.NullOrEmpty() || !string.Equals(o.basePath, g.path, StringComparison.Ordinal)) continue;
                    try
                    {
                        pair = new[]
                        {
                            GraphicDatabase.Get(g.GetType(), o.overlayPath, ShaderDatabase.TransparentPlant, g.drawSize,
                                new Color(1f, 1f, 1f, LightAlpha), Color.white),
                            GraphicDatabase.Get(g.GetType(), o.overlayPath, ShaderDatabase.TransparentPlant, g.drawSize,
                                Color.white, Color.white),
                        };
                    }
                    catch (Exception e)
                    {
                        Log.WarningOnce("[RimMandrake.Pyrelands] ash dust: overlay " + o.overlayPath + " failed: " + e.Message, 0x46E21);
                        pair = null;
                    }
                    break;
                }
            }
            pairs[g] = pair;
            return pair;
        }

        public static void Postfix_CleanFilth(ref bool __result, Thing t, bool forced)
        {
            if (!__result || forced || t == null || t.def != PyrelandsDriftField.AshDef || !t.Spawned) return;
            Map map = t.Map;
            IntVec3 c = t.Position;
            if (RM_FireEcoKernel.AshIsGround(map.roofGrid.Roofed(c), map.terrainGrid.TerrainAt(c).IsFloor)) __result = false;
        }
    }
}
