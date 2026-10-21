using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // WORLD_PATHS_READABLE (2026-10-20): roads and rivers that read on every one of our planet faces.
    //
    // How vanilla 1.6 draws them (RimSage, WorldDrawLayer_Roads / _Rivers / _Paths):
    //  * Roads: one mesh on WorldMaterials.Roads (shader Custom/Roads, queue 3540, 0.02 above the surface). For each
    //    RoadWorldLayerDef in `order` (Outline 0, Dirt 100, Stone 200, Gravel 300, Asphalt 400) every road tile emits a
    //    strip from each edge midpoint to the centre, VERTEX-COLOURED with that layer's `color`; its width is
    //    RoadDef.worldRenderSteps[layer].width, a fraction of the hex edge on each side of the midpoint, alpha 1 on the
    //    centre line falling to 0 at the side. In game the result is hard-edged (seen 2026-10-20, worldlook3/H): the
    //    outline shows as a dark casing round the next layer.
    //  * Rivers: two meshes, WorldMaterials.RiversBorder (queue 3520, width = widthOnWorld) and WorldMaterials.Rivers
    //    (3530, width = widthOnWorld - 0.2), shader Custom/Rivers (alpha-blended, _Alpha 0.8/1.0, specular), and ONE
    //    hard-coded vertex colour, WorldDrawLayer_Rivers.riverColor = (73,82,100), for both. On our pale faces that
    //    reads as a grey-green smear, not water (worldlook3/H, measured (170,182,145) over Greentide).
    //
    // What this does (Mod Settings "Planet: readable roads and rivers", default on; off restores the values captured
    // here at startup and the vanilla river material):
    //  * the five vanilla RoadWorldLayerDef colours and the vanilla RoadDef/RiverDef widths below;
    //  * rivers drawn with the ROAD material (hard edge, same look rules as roads, queues 3520/3530 kept so roads
    //    still cross over rivers), with a dark bank: the bank is the water colour x bankShade. The WATER colour stays
    //    whatever FlowWorks' River Colours chose (water by biome, 2026-10-20); only a river still in vanilla riverColor
    //    gets riverWater (the same blue-grey).
    // Roads are earth tones under a dark casing (owner 2026-10-20: a slate stone road on the Scald shore "looks like a
    // river, but it isn't"); no road layer is blue or teal, so blue reads as water only.
    // The ancient highway is old asphalt, left broken in pieces as the record has it (owner: "old asphalt broken from
    // long ago"); its pieces are deliberately not joined.
    // Values chosen by contrast against every face each tier crosses on the dev world (all tiers clear casing
    // WCAG >= 3 and fill dE76 >= 20 on every crossed land face, day side): design/Jawa/worldbuilding/world_paths_readable_2026-10-20.md.
    [StaticConstructorOnStartup]
    public static class RM_WorldPaths
    {
        // ---- the data -------------------------------------------------------------------------------------------
        public static readonly Dictionary<string, Color> LayerColor = new Dictionary<string, Color>
        {
            { "Outline", new Color(0.05f, 0.04f, 0.035f) },   // near-black warm casing, every road
            { "Dirt",    new Color(0.30f, 0.16f, 0.07f) },    // umber: dirt path and dirt road
            { "Stone",   new Color(0.18f, 0.15f, 0.12f) },    // grey-brown: stone road (was slate (0.15,0.25,0.25), read as a blue river on the Scald shore, owner 2026-10-20)
            { "Gravel",  new Color(0.08f, 0.08f, 0.085f) },   // old asphalt: ancient road / highway fill, dark grey-black (owner 2026-10-20: "it should show as old asphalt broken from long ago", not gold)
            { "Asphalt", new Color(0.42f, 0.41f, 0.38f) },    // pale worn stripe down the old asphalt
        };

        public static readonly Dictionary<string, Dictionary<string, float>> RoadWidth = new Dictionary<string, Dictionary<string, float>>
        {
            { "DirtPath",              new Dictionary<string, float> { { "Outline", 0.46f }, { "Dirt", 0.26f } } },
            { "DirtRoad",              new Dictionary<string, float> { { "Outline", 0.62f }, { "Dirt", 0.42f } } },
            { "StoneRoad",             new Dictionary<string, float> { { "Outline", 0.64f }, { "Stone", 0.44f } } },
            { "AncientAsphaltRoad",    new Dictionary<string, float> { { "Outline", 0.78f }, { "Gravel", 0.58f }, { "Asphalt", 0.14f } } },
            { "AncientAsphaltHighway", new Dictionary<string, float> { { "Outline", 1.00f }, { "Gravel", 0.80f }, { "Asphalt", 0.20f } } },
        };

        // widthOnWorld; the water itself is drawn 0.2 narrower (vanilla), so a creek at 0.32 shows a thin water line.
        public static readonly Dictionary<string, float> RiverWidth = new Dictionary<string, float>
        {
            { "Creek", 0.32f }, { "River", 0.46f }, { "LargeRiver", 0.62f }, { "HugeRiver", 0.82f },
        };

        public static Color32 riverWater = new Color32(20, 41, 77, 255);    // (0.08, 0.16, 0.30): the same blue-grey as FlowWorks' default water
        public static Color32 riverBank = new Color32(4, 9, 17, 255);       // riverWater x bankShade
        public static float bankShade = 0.22f;   // bank of a river another mod coloured = its water colour x this
        static readonly Color32 VanillaRiver = new Color32(73, 82, 100, 255);   // WorldDrawLayer_Rivers.riverColor

        // ---- vanilla, captured once ---------------------------------------------------------------------------
        static readonly Dictionary<RoadWorldLayerDef, Color> origLayer = new Dictionary<RoadWorldLayerDef, Color>();
        static readonly Dictionary<RoadDef.WorldRenderStep, float> origStep = new Dictionary<RoadDef.WorldRenderStep, float>();
        static readonly Dictionary<RiverDef, float> origRiver = new Dictionary<RiverDef, float>();

        static Material waterMat, bankMat;
        public static bool applied;
        public static string lastInfo = "never applied";

        static RM_WorldPaths()
        {
            foreach (RoadWorldLayerDef l in DefDatabase<RoadWorldLayerDef>.AllDefsListForReading) origLayer[l] = l.color;
            foreach (RoadDef r in DefDatabase<RoadDef>.AllDefsListForReading)
                if (r.worldRenderSteps != null)
                    foreach (RoadDef.WorldRenderStep s in r.worldRenderSteps) origStep[s] = s.width;
            foreach (RiverDef r in DefDatabase<RiverDef>.AllDefsListForReading) origRiver[r] = r.widthOnWorld;

            try
            {
                waterMat = new Material(WorldMaterials.Roads) { name = "RM_RiverWater", renderQueue = WorldMaterials.Rivers.renderQueue };
                bankMat = new Material(WorldMaterials.Roads) { name = "RM_RiverBank", renderQueue = WorldMaterials.RiversBorder.renderQueue };
                var h = new Harmony("mandrake.rm.biomes.worldpaths");
                MethodInfo getSub = AccessTools.Method(typeof(WorldDrawLayerBase), "GetSubMesh",
                    new[] { typeof(Material), typeof(int).MakeByRefType() });
                MethodInfo gen = AccessTools.Method(typeof(WorldDrawLayer_Paths), nameof(WorldDrawLayer_Paths.GeneratePaths));
                if (getSub == null || gen == null) throw new Exception("GetSubMesh/GeneratePaths not found");
                h.Patch(getSub, prefix: new HarmonyMethod(typeof(RM_WorldPaths), nameof(GetSubMeshPrefix)));
                h.Patch(gen, prefix: new HarmonyMethod(typeof(RM_WorldPaths), nameof(GeneratePathsPrefix)) { priority = Priority.Last });
            }
            catch (Exception e)
            {
                waterMat = bankMat = null;
                Log.Warning("[RimMandrake.Biomes] world river restyle patch failed, rivers keep the vanilla look: " + e.Message);
            }
            Apply("startup");
        }

        public static void Apply(string why)
        {
            bool on = RM_BiomesSettings.worldReadablePaths;
            int layers = 0, steps = 0, rivers = 0;
            foreach (KeyValuePair<RoadWorldLayerDef, Color> kv in origLayer)
            {
                if (on && LayerColor.TryGetValue(kv.Key.defName, out Color c)) { kv.Key.color = c; layers++; }
                else kv.Key.color = kv.Value;
            }
            foreach (RoadDef r in DefDatabase<RoadDef>.AllDefsListForReading)
            {
                if (r.worldRenderSteps == null) continue;
                RoadWidth.TryGetValue(r.defName, out Dictionary<string, float> w);
                foreach (RoadDef.WorldRenderStep s in r.worldRenderSteps)
                {
                    if (!origStep.TryGetValue(s, out float orig)) continue;
                    if (on && w != null && s.layer != null && w.TryGetValue(s.layer.defName, out float nw)) { s.width = nw; steps++; }
                    else s.width = orig;
                }
                r.ClearCachedData();   // GetLayerWidth caches per layer
            }
            foreach (KeyValuePair<RiverDef, float> kv in origRiver)
            {
                if (on && RiverWidth.TryGetValue(kv.Key.defName, out float rw)) { kv.Key.widthOnWorld = rw; rivers++; }
                else kv.Key.widthOnWorld = kv.Value;
            }
            applied = on;
            lastInfo = "readable world paths " + (on ? "ON" : "off") + " (" + why + "): " + layers + " road layer colours, "
                       + steps + " road widths, " + rivers + " river widths, river material swap "
                       + (waterMat != null && on ? "on" : "off");
            Log.Message("[RimMandrake.Biomes] " + lastInfo);
        }

        // Rivers ask for their two materials by identity; hand them the road-shader copies instead.
        static void GetSubMeshPrefix(WorldDrawLayerBase __instance, ref Material material)
        {
            if (!applied || waterMat == null || !(__instance is WorldDrawLayer_Rivers)) return;
            if (material == WorldMaterials.Rivers) material = waterMat;
            else if (material == WorldMaterials.RiversBorder) material = bankMat;
        }

        // Runs LAST (Priority.Last) so it sees the colour any other prefix chose. FlowWorks' River Colours
        // (RM_RiverColors.cs: blue-grey water, tinted inside the Contagion, Miasma, Wasteland and Rust Cathedral) sets the
        // water colour per tile; that colour is KEPT, and only the bank becomes a dark shade of it. Only when nobody
        // recoloured the river (the colour is still vanilla riverColor) does the water get riverWater.
        static void GeneratePathsPrefix(WorldDrawLayer_Paths __instance, LayerSubMesh subMesh, ref Color32 color)
        {
            if (!applied || waterMat == null || !(__instance is WorldDrawLayer_Rivers) || subMesh == null) return;
            bool vanilla = color.r == VanillaRiver.r && color.g == VanillaRiver.g && color.b == VanillaRiver.b;
            Color32 water = vanilla ? riverWater : color;
            if (subMesh.material == bankMat)
                color = vanilla ? riverBank : new Color32((byte)(water.r * bankShade), (byte)(water.g * bankShade), (byte)(water.b * bankShade), 255);
            else if (subMesh.material == waterMat) color = water;
        }
    }
}
