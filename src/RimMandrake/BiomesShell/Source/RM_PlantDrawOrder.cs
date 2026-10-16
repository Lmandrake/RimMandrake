using System.Collections.Generic;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // ════════════════════════════════════════════════════════════════════
    // GIANT_MUSHROOM_DRAW_FIX_SOUTH_GOES_FRONT — owner, 2026-10-16: "if you are more south, you go in front."
    //
    // MEASURED from decompiled 1.6:
    //   * Plant.Print prints every quad through Printer_Plane.PrintPlane at y = def.Altitude, with
    //     topVerticesAltitudeBias 0.1 (the quad's north edge is 0.1 nearer the camera than its south edge).
    //   * Altitudes.AltitudeFor: layers sit 0.3659 apart (AltInc 0.0366 is a tenth of a layer), so the 0.1 tilt
    //     never crosses a layer: a plant on a higher altitudeLayer draws over a lower-layer plant WHEREVER they stand.
    //   * The Rot's giant mushrooms sit on four layers (def dump 2026-10-04): LowPlant (AB_WitchesOyster,
    //     AB_AgaricusDomeCap, AB_LilacBeacon, ...), Building (AB_GlowingAgarilux, RM_PaleTree), BuildingOnTop
    //     (AB_GiantAgarilux, AB_DribblingCap, AB_SlimyPholiota, AB_RecurvedStropharia, AB_ArbuscularMycorrhiza),
    //     Skyfaller (AB_AgariluxPrime). All CutoutPlant (depth-written), all MapMeshOnly.
    //   * Inside one layer the tilt orders two plants by their quads' bottoms only when both have the same height
    //     (the slope is 0.1 / quad height), so a small plant can still draw over the cap of a big southern one.
    //
    // THE FIX: on a map whose biome is ours (owner 2026-10-15: biome mechanics are promised in our biomes only),
    // every plant on LowPlant..BuildingOnTop prints FLAT on BuildingOnTop, at a depth that falls with its foot's
    // z. The plant whose foot is further south is nearer the camera at every pixel where two plants overlap,
    // whatever their sizes or donor layers. Ground cover (FloorEmplacement) stays under; pawns, items and
    // Skyfaller-layer canopies stay over, as before. Draw order only: nothing else reads the printed y.
    // ════════════════════════════════════════════════════════════════════
    public static class PlantDrawOrderMath
    {
        // Mirrored by src/RimMandrake/BiomesShell/selftest_plant_draw_order.py (it parses these four constants).
        public const int MinLayer = 11;          // AltitudeLayer.LowPlant
        public const int CommonLayer = 17;       // AltitudeLayer.BuildingOnTop, the layer Alpha Biomes gives its giants
        public const float Band = 0.30f;         // of the 0.3659 between CommonLayer and Item (18)
        public const float MaxCarriedOffset = 0.01f;   // vanilla's snow-overlay lift (0.000366) rides along; more is foreign

        /// <summary>The foot of a printed quad: where vanilla's single-mesh branch plants the bottom of the plant
        /// (center.z - visualSize/2, with visualSize = quad side / drawSize.x).</summary>
        public static float Foot(float centerZ, float quadSide, float drawSizeX)
        {
            return centerZ - 0.5f * quadSide / (drawSizeX > 0.01f ? drawSizeX : 1f);
        }

        /// <summary>Lift above the common layer's altitude: Band at the map's south edge, 0 at its north edge.</summary>
        public static float BandOffset(float footZ, int mapSizeZ)
        {
            float t = (footZ + 1f) / (mapSizeZ + 2f);
            if (t < 0f) t = 0f;
            else if (t > 1f) t = 1f;
            return Band * (1f - t);
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_PlantDrawOrder
    {
        // One-map cache: Print runs section by section for one map at a time. Keyed by reference, never uniqueID
        // (a new game restarts the ids, so a cached id could name another game's map in another biome).
        private static Map lastMap;
        private static bool lastMapOurs;
        private static readonly float commonAltitude = ((AltitudeLayer)PlantDrawOrderMath.CommonLayer).AltitudeFor();

        static RM_PlantDrawOrder()
        {
            MethodInfo target = AccessTools.Method(typeof(Plant), nameof(Plant.Print), new[] { typeof(SectionLayer) });
            if (target == null)
            {
                Log.Error(RM_BiomesMod.LogPrefix + "plant draw order: Plant.Print(SectionLayer) not found; nothing patched.");
                return;
            }
            new Harmony("mandrake.rm.biomes.plantdraworder").Patch(target,
                transpiler: new HarmonyMethod(typeof(RM_PlantDrawOrder), nameof(Transpiler)));
        }

        public static IEnumerable<CodeInstruction> Transpiler(IEnumerable<CodeInstruction> instructions)
        {
            MethodInfo print = AccessTools.Method(typeof(Printer_Plane), nameof(Printer_Plane.PrintPlane));
            MethodInfo ours = AccessTools.Method(typeof(RM_PlantDrawOrder), nameof(PrintPlaneOrdered));
            int replaced = 0;
            foreach (CodeInstruction ins in instructions)
            {
                if (ins.Calls(print))
                {
                    // ldarg.0 takes over any branch label, so a jump still lands before the extra argument.
                    var self = new CodeInstruction(OpCodes.Ldarg_0) { labels = ins.labels, blocks = ins.blocks };
                    ins.labels = new List<Label>();
                    ins.blocks = new List<ExceptionBlock>();
                    yield return self;
                    yield return new CodeInstruction(OpCodes.Call, ours);
                    replaced++;
                    continue;
                }
                yield return ins;
            }
            if (replaced == 0)
                Log.Error(RM_BiomesMod.LogPrefix + "plant draw order: no PrintPlane call found in Plant.Print; nothing patched.");
            else
                Log.Message(RM_BiomesMod.LogPrefix + "plant draw order: " + replaced + " PrintPlane call(s) in Plant.Print routed.");
        }

        public static void PrintPlaneOrdered(MapDrawLayer layer, Vector3 center, Vector2 size, Material mat, float rot,
            bool flipUv, Vector2[] uvs, Color32[] colors, float topVerticesAltitudeBias, float uvzPayload, Plant plant)
        {
            if (Applies(plant))
            {
                float carried = center.y - plant.def.Altitude;
                if (carried > PlantDrawOrderMath.MaxCarriedOffset || carried < -PlantDrawOrderMath.MaxCarriedOffset) carried = 0f;
                float foot = PlantDrawOrderMath.Foot(center.z, size.y, plant.def.graphicData?.drawSize.x ?? 1f);
                center.y = commonAltitude + PlantDrawOrderMath.BandOffset(foot, plant.Map.Size.z) + carried;
                topVerticesAltitudeBias = 0f;
            }
            Printer_Plane.PrintPlane(layer, center, size, mat, rot, flipUv, uvs, colors, topVerticesAltitudeBias, uvzPayload);
        }

        private static bool Applies(Plant plant)
        {
            if (!RM_BiomesSettings.plantDrawOrderSouthInFront || plant?.def == null) return false;
            int alt = (int)plant.def.altitudeLayer;
            if (alt < PlantDrawOrderMath.MinLayer || alt > PlantDrawOrderMath.CommonLayer) return false;
            Map map = plant.Map;
            if (map == null) return false;
            if (map != lastMap)
            {
                string pkg = map.Biome?.modContentPack?.PackageId;
                lastMapOurs = pkg != null && pkg.ToLowerInvariant().StartsWith("mandrake.");
                lastMap = map;
            }
            return lastMapOurs;
        }

        /// <summary>Settings changed: reprint every map's things so the switch shows at once.</summary>
        public static void Reprint()
        {
            if (Current.Game?.Maps == null) return;
            foreach (Map map in Current.Game.Maps)
                map?.mapDrawer?.WholeMapChanged(MapMeshFlagDefOf.Things);
        }
    }
}
