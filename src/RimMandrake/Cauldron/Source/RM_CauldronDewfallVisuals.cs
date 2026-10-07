using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    [DefOf]
    public static class RM_CauldronVisualsDefOf
    {
        public static WeatherDef RM_Dewfall;
        public static ThingDef RM_Filth_DewBeads;

        static RM_CauldronVisualsDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_CauldronVisualsDefOf));
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_ENRICHMENT_VISUALS_1 V1 + V2 — what dewfall does to the ground and the garden.
    // Spec: design/Jawa/worldbuilding/biomes/cauldron_enrichment_audio_visuals_spec_2026-10-02.md §3.
    // Owner ruling 2026-10-03: the no-green ban LIFTS during dewfall (the garden briefly blooms in
    // wrong colours; "green is a mistake" becomes an event).
    //
    // V1 BEADS. While the map's weather is RM_Dewfall, every BeadIntervalTicks a few random
    // unroofed, outdoor, standable land cells OUTSIDE the home area get RM_Filth_DewBeads (a real
    // filth Thing: hover reads "chemical dew"). Outside the home area so dewfall never becomes a
    // cleaning chore; the filth evaporates on its own (disappearsInDays in the def). Map-wide cap.
    // Beads do not dose anyone: a contact effect would be a mechanic, not in this item.
    //
    // V2 SATURATION. A plant carrying RM_DewfallGraphicExtension swaps to its dew graphic while the
    // map is in dewfall (postfix on Plant.Graphic, returning the dew variant only where vanilla would
    // return the plant's normal graphic, so polluted/leafless still win). Plants are printed into the
    // section mesh, so the transition remeshes Things once each way. DORMANT until art exists: a
    // variant whose texture is not on disk is skipped, and with none the patch is not installed.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_CauldronDewfall : MapComponent
    {
        // PROVISIONAL tuning (spec V1: INVENTED 250 ticks / 6 cells / cap ~400).
        private const int BeadIntervalTicks = RM_YieldKernel.BeadIntervalTicks;
        private const float BeadsPerInterval = RM_YieldKernel.BeadsPerInterval;
        private const int BeadCap = RM_YieldKernel.BeadCap;

        private bool lastDew;
        private bool initialised;

        public RM_MapComponent_CauldronDewfall(Map map) : base(map) { }

        private bool DewNow => map.weatherManager?.curWeather == RM_CauldronVisualsDefOf.RM_Dewfall;

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            lastDew = DewNow;      // the mesh is built fresh on load, already in the current weather
            initialised = true;
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % BeadIntervalTicks != 0) return;
            bool dew = DewNow;
            if (!initialised) { lastDew = dew; initialised = true; }
            bool flipped = RM_YieldKernel.DewFlip(initialised, lastDew, dew);
            if (flipped)
            {
                lastDew = dew;
                if (RM_YieldKernel.RemeshOnFlip(true, RM_CauldronSettings.dewfallSaturationEnabled, RM_DewfallSaturation.Active))
                    map.mapDrawer.WholeMapChanged(MapMeshFlagDefOf.Things);
            }
            if (dew && RM_CauldronSettings.dewfallBeadsEnabled) SpawnBeads();
        }

        private void SpawnBeads()
        {
            ThingDef bead = RM_CauldronVisualsDefOf.RM_Filth_DewBeads;
            float density = RM_CauldronSettings.dewfallBeadDensity;
            if (density <= 0f) return;
            int cap = RM_YieldKernel.BeadCap_(density);
            if (!RM_YieldKernel.BeadsSpawn(density, map.listerThings.ThingsOfDef(bead).Count, cap)) return;
            int n = GenMath.RoundRandom(BeadsPerInterval * density);
            for (int i = 0; i < n; i++)
            {
                IntVec3 c = CellFinder.RandomCell(map);
                if (!CanBead(c)) continue;
                FilthMaker.TryMakeFilth(c, map, bead, 1);
            }
        }

        private bool CanBead(IntVec3 c)
        {
            if (c.Roofed(map) || c.Fogged(map) || !c.Standable(map)) return false;
            TerrainDef t = c.GetTerrain(map);
            if (t == null || t.IsWater) return false;
            if (map.areaManager.Home[c]) return false;
            Room room = c.GetRoom(map);
            return RM_YieldKernel.CanBead(false, false, true, true, false, false, room != null, room != null && room.PsychologicallyOutdoors);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            // nothing saved: lastDew is re-read from the weather on load (FinalizeInit)
        }
    }

    /// <summary>V2: names the dew variant of a garden plant. graphicClass null = the plant's own class.</summary>
    public class RM_DewfallGraphicExtension : DefModExtension
    {
        public string texPath;
        public System.Type graphicClass;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (texPath.NullOrEmpty()) yield return "RM_DewfallGraphicExtension has no texPath";
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_DewfallSaturation
    {
        private static readonly Dictionary<ThingDef, Graphic> dewGraphics = new Dictionary<ThingDef, Graphic>();

        public static bool Active => dewGraphics.Count > 0;

        static RM_DewfallSaturation()
        {
            var missing = new List<string>();
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.plant == null || d.graphicData == null) continue;
                var ext = d.GetModExtension<RM_DewfallGraphicExtension>();
                if (ext == null) continue;
                System.Type cls = ext.graphicClass ?? d.graphicData.graphicClass;
                bool onDisk = cls == typeof(Graphic_Random)
                    ? ContentFinder<Texture2D>.GetAllInFolder(ext.texPath).Any()
                    : ContentFinder<Texture2D>.Get(ext.texPath, false) != null;
                if (!onDisk) { missing.Add(d.defName); continue; }
                var gd = new GraphicData();
                gd.CopyFrom(d.graphicData);
                gd.texPath = ext.texPath;
                gd.graphicClass = cls;
                dewGraphics[d] = gd.Graphic;
            }
            if (missing.Count > 0)
                Log.Message("[RM Cauldron] dewfall variants not on disk yet (no swap for): " + string.Join(", ", missing));
            if (dewGraphics.Count == 0) return;   // dormant: no patch on the hot getter at all
            new Harmony("mandrake.rm.cauldron.dewfall").Patch(
                AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.Graphic)),
                postfix: new HarmonyMethod(typeof(RM_DewfallSaturation), nameof(Postfix_Graphic)));
        }

        public static void Postfix_Graphic(Plant __instance, ref Graphic __result)
        {
            if (!RM_CauldronSettings.dewfallSaturationEnabled) return;
            if (!dewGraphics.TryGetValue(__instance.def, out Graphic dew)) return;
            if (__result != __instance.def.graphic) return;     // polluted / leafless keep their own look
            Map m = __instance.MapHeld;
            if (m?.weatherManager?.curWeather != RM_CauldronVisualsDefOf.RM_Dewfall) return;
            __result = dew;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_ENRICHMENT_VISUALS_1 V3 — assay flecks on old metal trees.
    //
    // ThingComp.PostPrintOnto never fires on a plant: Plant.Print overrides Thing.Print wholesale with
    // no comp loop (RimSage, 1.6). So a postfix on Plant.Print prints ONE extra plane of a fleck
    // overlay over the tree, chosen by the tree's assay band (RM_CompMetalYield.GradeFraction): below
    // lightFrom none, below heavyFrom light, else heavy. Static: baked into the section mesh with the
    // plant, zero per-frame cost; vanilla re-prints a plant as it grows, so the band follows growth.
    //
    // Registration: Plant.Print seeds Rand with Position.GetHashCode() and, for a single-mesh plant,
    // its FIRST draws are Gen.RandomHorizontalVector(0.05) for the offset and then Rand.Bool for the UV
    // flip. This replays the same seed and draws so the overlay sits exactly on the trunk. Only
    // maxMeshCount 1 plants (both trees) take flecks.
    //
    // Gated on metal yield + assay grade + assayFlecksEnabled. DORMANT until the overlay art exists:
    // with neither texture on disk the patch is not installed.
    // ════════════════════════════════════════════════════════════════════
    public class RM_AssayFlecksExtension : DefModExtension
    {
        public string lightTexPath;
        public string heavyTexPath;
        public float lightFrom = 1f / 3f;
        public float heavyFrom = 2f / 3f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (lightTexPath.NullOrEmpty() && heavyTexPath.NullOrEmpty())
                yield return "RM_AssayFlecksExtension names no overlay texture";
            if (heavyFrom < lightFrom) yield return "RM_AssayFlecksExtension heavyFrom must be >= lightFrom";
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_AssayFlecks
    {
        // Two altitude steps above the plant (vanilla's snow overlay uses one).
        private const float OverlayYOffset = 0.0007317074f;

        private static readonly Dictionary<ThingDef, (RM_AssayFlecksExtension ext, Material light, Material heavy)> table =
            new Dictionary<ThingDef, (RM_AssayFlecksExtension, Material, Material)>();

        public static bool Active => table.Count > 0;

        static RM_AssayFlecks()
        {
            var missing = new List<string>();
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d.plant == null) continue;
                var ext = d.GetModExtension<RM_AssayFlecksExtension>();
                if (ext == null) continue;
                if (d.plant.maxMeshCount != 1) { Log.Warning("[RM Cauldron] assay flecks need maxMeshCount 1: " + d.defName); continue; }
                Material light = Mat(ext.lightTexPath, missing);
                Material heavy = Mat(ext.heavyTexPath, missing);
                if (light == null && heavy == null) continue;
                table[d] = (ext, light, heavy);
            }
            if (missing.Count > 0)
                Log.Message("[RM Cauldron] assay fleck overlays not on disk yet: " + string.Join(", ", missing));
            if (table.Count == 0) return;
            new Harmony("mandrake.rm.cauldron.assayflecks").Patch(
                AccessTools.Method(typeof(Plant), nameof(Plant.Print)),
                postfix: new HarmonyMethod(typeof(RM_AssayFlecks), nameof(Postfix_Print)));
        }

        private static Material Mat(string path, List<string> missing)
        {
            if (path.NullOrEmpty()) return null;
            if (ContentFinder<Texture2D>.Get(path, false) == null)
            {
                if (!missing.Contains(path)) missing.Add(path);
                return null;
            }
            return MaterialPool.MatFrom(path, ShaderDatabase.Transparent);
        }

        public static void Postfix_Print(Plant __instance, SectionLayer layer)
        {
            if (!RM_YieldKernel.FlecksOn(RM_CauldronSettings.assayFlecksEnabled, RM_CauldronSettings.assayGradeEnabled,
                    RM_CauldronSettings.metalYieldEnabled)) return;
            if (!table.TryGetValue(__instance.def, out var row)) return;
            RM_CompMetalYield comp = __instance.TryGetComp<RM_CompMetalYield>();
            if (comp == null) return;
            float frac = comp.GradeFraction();
            RM_AssayBand band = RM_YieldKernel.FleckBand(frac, row.ext.lightFrom, row.ext.heavyFrom, row.light != null, row.heavy != null);
            Material mat = band == RM_AssayBand.Heavy ? row.heavy : band == RM_AssayBand.Light ? row.light : null;
            if (mat == null) return;

            ThingDef def = __instance.def;
            float visual = def.plant.visualSizeRange.LerpThroughRange(__instance.Growth);
            float size = def.graphicData.drawSize.x * visual;
            Vector3 v = __instance.TrueCenter();
            bool flip;
            Rand.PushState();
            try
            {
                Rand.Seed = __instance.Position.GetHashCode();
                v += Gen.RandomHorizontalVector(0.05f);
                float z0 = __instance.Position.z;
                if (v.z - visual / 2f < z0) v.z = z0 + visual / 2f;
                flip = Rand.Bool;
            }
            finally
            {
                Rand.PopState();
            }
            v.y += OverlayYOffset;
            Printer_Plane.PrintPlane(layer, v, new Vector2(size, size), mat, 0f, flip);
        }
    }
}
