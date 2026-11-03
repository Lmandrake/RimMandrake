using System;
using System.Collections.Generic;
using System.Text;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Biomes
{
    // ════════════════════════════════════════════════════════════════════
    // CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD. Design: design/RimMandrake/canopy_zoom_investigation_2026-10-18.md (option A).
    // Owner, 2026-10-18: "scroll out from the map enough that only the top forest canopy is seen" and
    // "Titanic trees should be seen only as the solid trunk".
    //
    // A tree whose def carries RM_CanopyExtension draws two pictures:
    //   * its TRUNK, always: Plant.Graphic is swapped for the trunk pool, so vanilla Plant.Print (growth size, wind,
    //     variant pick, shadow, RM_PlantDrawOrder) prints the trunk exactly where the whole tree used to stand;
    //   * its CANOPY, in RM_SectionLayer_Canopy: one quad per tree at the same centre, size and variant index as the
    //     trunk, on ItemImportant+5 (above every plant, BELOW LayingPawn and Pawn, so pawns stay on top). The layer's
    //     DrawLayer runs only when the camera shows fewer than canopyThresholdPx screen pixels per cell, fading in
    //     over canopyFadePx (Transparent shader, alpha on the material colour). Zooming builds no mesh: free.
    //   * GetBoundaryRect is the true extent of every canopy printed (design §4.1: a 16-cell crown reaching out of its
    //     17x17 section would otherwise vanish while still on screen).
    //
    // MEASURED from decompiled 1.6 (D:\ClaudeWork\rimmandrake\decomp\rw16\all):
    //   * Plant.Print, maxMeshCount 1: Rand.Seed = Position.GetHashCode(); centre = TrueCenter() +
    //     Gen.RandomHorizontalVector(0.05f) (two Rand.Range calls), lifted so its foot is not below Position.z;
    //     flip = Rand.Bool; then Rand.Range(0, SubGraphicsCount) picks the Graphic_Random variant; quad side =
    //     drawSize.x * visualSizeRange.LerpThroughRange(growth). CanopyMath.Place replays that sequence.
    //   * CameraDriver.CellSizePixels = UI.screenHeight / (RootSize * 2).
    //   * MapDrawLayer.RefreshSubMeshBounds = GetBoundaryRect().ExpandedBy(2) (Unity culls on it).
    //   * SectionLayer_Things.Regenerate's filters (fog, snow/sand hide depth, thin ice) are copied here.
    // ════════════════════════════════════════════════════════════════════
    public static class CanopyMath
    {
        // Mirrored by src/RimMandrake/BiomesShell/selftest_canopy.py, which parses these constants.
        // Defaults: hidden at vanilla's starting zoom (RootSize 24: 22.5 px/cell at 1080p, 30 at 1440p); solid at its
        // furthest (RootSize 60: 9 px/cell at 1080p, 12 at 1440p). 14/4 left 1440p half-faded at full zoom-out. On a 4K
        // screen vanilla's furthest is 18 px/cell: the slider or Camera+'s wider range reaches the canopy there.
        public const float DefaultThresholdPx = 18f;   // canopy starts to show below 18 px per cell (RootSize 30 at 1080p)
        public const float DefaultFadePx = 5f;         // solid at 13 px per cell (RootSize 41.5 at 1080p, 55.4 at 1440p)
        public const float MinThresholdPx = 4f;
        public const float MaxThresholdPx = 40f;
        public const float MaxFadePx = 12f;
        public const int ArtPxPerCell = 32;            // owner's density exception for canopy art (design §4.3)
        public const float VanillaJitter = 0.05f;      // Plant.Print single-mesh RandomHorizontalVector(0.05f)

        /// <summary>Canopy opacity at a camera showing <paramref name="cellPx"/> pixels per cell: 0 at or above the
        /// threshold, 1 at or below threshold - fade, linear between. A fade under 0.01 px is a hard switch.</summary>
        public static float Alpha(float cellPx, float thresholdPx, float fadePx)
        {
            if (float.IsNaN(cellPx)) return 0f;
            if (fadePx < 0.01f) return cellPx < thresholdPx ? 1f : 0f;
            float t = (thresholdPx - cellPx) / fadePx;
            if (t <= 0f) return 0f;
            if (t >= 1f) return 1f;
            return t;
        }

        public static float CellSizePixels(float screenHeight, float rootSize)
        {
            return rootSize > 0.001f ? screenHeight / (rootSize * 2f) : float.PositiveInfinity;
        }

        /// <summary>The RootSize at which the camera shows <paramref name="cellPx"/> pixels per cell.</summary>
        public static float RootSizeFor(float screenHeight, float cellPx)
        {
            return screenHeight / (2f * Math.Max(0.01f, cellPx));
        }

        /// <summary>Vanilla's single-mesh foot rule: a quad whose foot falls below its cell's south edge is lifted so
        /// the foot sits on it.</summary>
        public static float AnchoredZ(float centerZ, int posZ, float visualSize)
        {
            return centerZ - visualSize / 2f < posZ ? posZ + visualSize / 2f : centerZ;
        }

        /// <summary>Cells a square quad of side <paramref name="side"/> centred at (cx, cz) touches.</summary>
        public static void QuadCells(float cx, float cz, float side, out int minX, out int minZ, out int maxX, out int maxZ)
        {
            float h = side / 2f;
            minX = (int)Math.Floor(cx - h);
            minZ = (int)Math.Floor(cz - h);
            maxX = (int)Math.Ceiling(cx + h) - 1;
            maxZ = (int)Math.Ceiling(cz + h) - 1;
            if (maxX < minX) maxX = minX;
            if (maxZ < minZ) maxZ = minZ;
        }
    }

    /// <summary>On a tree ThingDef: its trunk and canopy pools (Graphic_Random folders with the same variant letters
    /// as the def's own pool, so a tree's trunk and canopy are the same picture's two halves).</summary>
    public class RM_CanopyExtension : DefModExtension
    {
        public string trunkTexPath;
        public string canopyTexPath;
        public float canopyScale = 1f;

        [Unsaved] private Graphic trunk;
        [Unsaved] private Graphic canopy;
        [Unsaved] private bool built;

        public Graphic Trunk(ThingDef def) { Build(def); return trunk; }
        public Graphic Canopy(ThingDef def) { Build(def); return canopy; }

        private void Build(ThingDef def)
        {
            if (built) return;
            built = true;
            GraphicData gd = def.graphicData;
            if (gd == null) return;
            Vector2 size = gd.drawSize;
            Shader plantShader = def.graphic?.Shader ?? ShaderDatabase.CutoutPlant;
            if (!trunkTexPath.NullOrEmpty())
                trunk = GraphicDatabase.Get<Graphic_Random>(trunkTexPath, plantShader, size, gd.color, gd.colorTwo);
            if (!canopyTexPath.NullOrEmpty())
                canopy = GraphicDatabase.Get<Graphic_Random>(canopyTexPath, ShaderDatabase.Transparent, size, Color.white);
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors()) yield return e;
            if (trunkTexPath.NullOrEmpty()) yield return "RM_CanopyExtension: trunkTexPath is empty";
            if (canopyTexPath.NullOrEmpty()) yield return "RM_CanopyExtension: canopyTexPath is empty";
            if (canopyScale <= 0f) yield return "RM_CanopyExtension: canopyScale must be > 0";
        }
    }

    [StaticConstructorOnStartup]
    public static class RM_Canopy
    {
        private static readonly HashSet<Material> canopyMats = new HashSet<Material>();
        private static int alphaFrame = -1;
        private static float frameAlpha;

        // State reads for canopy_debug.py (jawa/static_call into RM_CanopyProof).
        public static float LastAlpha;
        public static float LastCellPx;
        public static int LastDrawFrame = -1;
        public static int DrawCalls;
        public static int SkippedDraws;
        public static int TrunkSwaps;

        static RM_Canopy()
        {
            var getter = AccessTools.PropertyGetter(typeof(Plant), nameof(Plant.Graphic));
            if (getter == null)
            {
                Log.Error(RM_BiomesMod.LogPrefix + "canopy: Plant.Graphic getter not found; trunks are not swapped.");
                return;
            }
            new Harmony("mandrake.rm.biomes.canopy").Patch(getter,
                postfix: new HarmonyMethod(typeof(RM_Canopy), nameof(GraphicPostfix)));
            int n = 0;
            foreach (ThingDef d in DefDatabase<ThingDef>.AllDefsListForReading)
                if (d.plant != null && d.HasModExtension<RM_CanopyExtension>()) n++;
            Log.Message(RM_BiomesMod.LogPrefix + "canopy: " + n + " tree def(s) draw trunk + zoom-gated canopy.");
        }

        public static RM_CanopyExtension ExtFor(ThingDef def)
        {
            return def?.modExtensions == null ? null : def.GetModExtension<RM_CanopyExtension>();
        }

        /// <summary>Only the plant's plain pool is swapped: sowing, polluted, leafless and immature pictures stay.</summary>
        public static void GraphicPostfix(Plant __instance, ref Graphic __result)
        {
            if (!RM_BiomesSettings.canopyEnabled) return;
            ThingDef def = __instance.def;
            if (def == null || __result == null || !ReferenceEquals(__result, def.graphic)) return;
            RM_CanopyExtension ext = ExtFor(def);
            Graphic trunk = ext?.Trunk(def);
            if (trunk == null) return;
            __result = trunk;
            TrunkSwaps++;
        }

        public static void RegisterMaterial(Material m)
        {
            if (m != null) canopyMats.Add(m);
        }

        /// <summary>The canopy opacity for this frame; every canopy material carries it (set once per frame).</summary>
        public static float FrameAlpha()
        {
            int f = Time.frameCount;
            if (f == alphaFrame) return frameAlpha;
            alphaFrame = f;
            CameraDriver cam = Find.CameraDriver;
            float px = cam != null ? cam.CellSizePixels : float.PositiveInfinity;
            LastCellPx = px;
            frameAlpha = CanopyMath.Alpha(px, RM_BiomesSettings.canopyThresholdPx, RM_BiomesSettings.canopyFadePx);
            LastAlpha = frameAlpha;
            if (frameAlpha > 0f)
            {
                Color c = new Color(1f, 1f, 1f, frameAlpha);
                foreach (Material m in canopyMats)
                    if (m != null) m.color = c;
            }
            return frameAlpha;
        }

        /// <summary>Settings changed: reprint every map's things (trunk swap and canopy prints follow the switch).</summary>
        public static void Reprint()
        {
            if (Current.Game?.Maps == null) return;
            foreach (Map map in Current.Game.Maps)
                map?.mapDrawer?.WholeMapChanged(MapMeshFlagDefOf.Things);
        }
    }

    public class RM_SectionLayer_Canopy : SectionLayer
    {
        private CellRect bounds;
        public int printed;
        public int lastDrawFrame = -1;   // this section's own draw evidence (the probe reads it, not the global)

        public RM_SectionLayer_Canopy(Section section) : base(section)
        {
            relevantChangeTypes = (ulong)MapMeshFlagDefOf.Things | (ulong)MapMeshFlagDefOf.FogOfWar | (ulong)MapMeshFlagDefOf.Snow;
            bounds = section.CellRect;
        }

        public CellRect Bounds => bounds;

        public override CellRect GetBoundaryRect() => bounds;

        public override void DrawLayer()
        {
            if (printed == 0 || !RM_BiomesSettings.canopyEnabled) return;
            if (WorldComponent_GravshipController.CutsceneInProgress && !WorldComponent_GravshipController.GravshipRenderInProgess) return;
            if (RM_Canopy.FrameAlpha() <= 0f)
            {
                RM_Canopy.SkippedDraws++;
                return;
            }
            RM_Canopy.DrawCalls++;
            RM_Canopy.LastDrawFrame = lastDrawFrame = Time.frameCount;
            base.DrawLayer();
        }

        public override void Regenerate()
        {
            ClearSubMeshes(MeshParts.All);
            bounds = section.CellRect;
            printed = 0;
            if (!RM_BiomesSettings.canopyEnabled) return;
            Map map = Map;
            CellRect rect = section.CellRect;
            float y = AltitudeLayer.ItemImportant.AltitudeFor(5f);
            // North rows first: within one variant's sub-mesh a later quad draws over an earlier one (Transparent writes
            // no depth), so the more southern crown is in front, as RM_PlantDrawOrder orders the trunks. KNOWN LIMIT
            // (design §4.4; GPT review 2026-11-03): crowns of DIFFERENT variants sit in different sub-meshes, and other
            // sections in other meshes, so where two such crowns overlap their order is the draw order, not N->S.
            for (int z = rect.maxZ; z >= rect.minZ; z--)
            {
                for (int x = rect.minX; x <= rect.maxX; x++)
                {
                    IntVec3 c = new IntVec3(x, 0, z);
                    List<Thing> list = map.thingGrid.ThingsListAt(c);
                    for (int i = 0; i < list.Count; i++)
                    {
                        if (!(list[i] is Plant p) || p.Position != c) continue;
                        RM_CanopyExtension ext = RM_Canopy.ExtFor(p.def);
                        if (ext == null || !Shows(p, map)) continue;
                        // only over the trunk: a sowing, polluted, leafless or immature picture keeps its own look
                        if (!ReferenceEquals(p.Graphic, ext.Trunk(p.def))) continue;
                        if (PrintCanopy(p, ext, y)) printed++;
                    }
                }
            }
            if (printed > 0) FinalizeMesh(MeshParts.All);
        }

        private static bool Shows(Plant p, Map map)
        {
            ThingDef d = p.def;
            if (!d.seeThroughFog && map.fogGrid.IsFogged(p.Position)) return false;
            if (d.hideAtSnowOrSandDepth < 1f &&
                Math.Max(map.snowGrid.GetDepth(p.Position), p.Position.GetSandDepth(map)) > d.hideAtSnowOrSandDepth) return false;
            if (d.plant != null && !d.plant.showInFrozenWater && p.Position.GetTerrain(map) == TerrainDefOf.ThinIce) return false;
            return true;
        }

        private bool PrintCanopy(Plant p, RM_CanopyExtension ext, float y)
        {
            if (!Place(p, ext, out Graphic_Random pool, out Vector3 center, out float side, out bool flip, out int index)) return false;
            Material mat = pool.SubGraphicAtIndex(index).MatSingle;
            if (mat == null) return false;
            RM_Canopy.RegisterMaterial(mat);
            center.y = y;
            Printer_Plane.PrintPlane(this, center, new Vector2(side, side), mat, 0f, flip);
            bounds = bounds.Encapsulate(CanopyRect(center, side));
            return true;
        }

        public static CellRect CanopyRect(Vector3 center, float side)
        {
            CanopyMath.QuadCells(center.x, center.z, side, out int minX, out int minZ, out int maxX, out int maxZ);
            return CellRect.FromLimits(minX, minZ, maxX, maxZ);
        }

        /// <summary>Where Plant.Print puts this tree's quad, and which pool variant it picks.</summary>
        public static bool Place(Plant p, RM_CanopyExtension ext, out Graphic_Random pool, out Vector3 center, out float side,
            out bool flip, out int index)
        {
            pool = ext.Canopy(p.def) as Graphic_Random;
            center = default(Vector3);
            side = 0f;
            flip = false;
            index = 0;
            if (pool == null || pool.SubGraphicsCount == 0) return false;
            float visual = p.def.plant.visualSizeRange.LerpThroughRange(p.Growth);
            side = (p.def.graphicData?.drawSize.x ?? 1f) * visual * ext.canopyScale;
            Rand.PushState();
            try
            {
                Rand.Seed = p.Position.GetHashCode();
                center = p.TrueCenter() + Gen.RandomHorizontalVector(CanopyMath.VanillaJitter);
                center.z = CanopyMath.AnchoredZ(center.z, p.Position.z, visual);
                flip = Rand.Bool;
                index = Rand.Range(0, pool.SubGraphicsCount);
            }
            finally
            {
                Rand.PopState();
            }
            return true;
        }
    }

    /// <summary>The live probe canopy_debug.py drives through jawa/static_call. Writes only the camera and, when the
    /// current map has no canopy tree, spawns one mature RM_SweetlineTree near the map centre (quicktest maps only:
    /// every save but the canonical world saves is disposable).</summary>
    public static class RM_CanopyProof
    {
        public const string ProofTree = "RM_SweetlineTree";

        /// <summary>Place the camera on a canopy tree at "far" (fully shown) or "near" (hidden) zoom. Returns the
        /// target cell; the verdict is read a few frames later by <see cref="Read"/>.</summary>
        public static string Setup(Map map, string zoom)
        {
            if (map == null) return "FAIL no map";
            Plant tree = FindOrSpawn(map, out string how);
            if (tree == null) return "FAIL " + how;
            float h = UI.screenHeight;
            float thr = RM_BiomesSettings.canopyThresholdPx, fade = RM_BiomesSettings.canopyFadePx;
            float px = zoom == "far" ? Math.Max(1f, thr - fade - 1f) : thr + 6f;
            float size = CanopyMath.RootSizeFor(h, px);
            Find.CameraDriver.SetRootPosAndSize(tree.DrawPos, size);
            return "OK " + how + " tree=" + tree.ThingID + " at " + tree.Position + " zoom=" + zoom + " targetPx=" + px.ToString("F1")
                   + " rootSize=" + size.ToString("F1") + " screenHeight=" + h;
        }

        /// <summary>A verdict line: PASS/FAIL plus every number it rests on.</summary>
        public static string Read(Map map, string zoom)
        {
            if (map == null) return "FAIL no map";
            Plant tree = FindTree(map);
            if (tree == null) return "FAIL no canopy tree on the map (run Setup first)";
            var sb = new StringBuilder();
            float px = Find.CameraDriver.CellSizePixels;
            float alpha = CanopyMath.Alpha(px, RM_BiomesSettings.canopyThresholdPx, RM_BiomesSettings.canopyFadePx);
            RM_SectionLayer_Canopy layer = LayerFor(map, tree.Position);
            int drawn = layer?.lastDrawFrame ?? -1;
            int framesSinceDraw = drawn < 0 ? -1 : Time.frameCount - drawn;
            RM_CanopyExtension ext = RM_Canopy.ExtFor(tree.def);
            Graphic shown = tree.Graphic;
            bool trunkShown = ext != null && ReferenceEquals(shown, ext.Trunk(tree.def));
            CellRect sec = map.mapDrawer.SectionAt(tree.Position).CellRect;
            CellRect want = Crown(tree, map);
            // the layer's bounds hold the whole crown (design §4.1), and this crown does reach past its section
            bool covers = layer != null && want.Area > 0 && layer.Bounds.Contains(want.Min) && layer.Bounds.Contains(want.Max);
            bool pastSection = PastSection(tree, map);
            sb.Append("enabled=").Append(RM_BiomesSettings.canopyEnabled)
              .Append(" cellPx=").Append(px.ToString("F2")).Append(" alpha=").Append(alpha.ToString("F2"))
              .Append(" lastAlpha=").Append(RM_Canopy.LastAlpha.ToString("F2"))
              .Append(" printed=").Append(layer?.printed ?? -1)
              .Append(" bounds=").Append(layer != null ? layer.Bounds.ToString() : "none").Append(" section=").Append(sec)
              .Append(" crown=").Append(want).Append(" covers=").Append(covers).Append(" pastSection=").Append(pastSection)
              .Append(" framesSinceDraw=").Append(framesSinceDraw)
              .Append(" draws=").Append(RM_Canopy.DrawCalls).Append(" skipped=").Append(RM_Canopy.SkippedDraws)
              .Append(" trunkShown=").Append(trunkShown).Append(" trunkSwaps=").Append(RM_Canopy.TrunkSwaps);
            bool ok;
            if (zoom == "far")
                ok = RM_BiomesSettings.canopyEnabled && alpha >= 0.999f && RM_Canopy.LastAlpha >= 0.999f && layer != null
                     && layer.printed > 0 && covers && pastSection && framesSinceDraw >= 0 && framesSinceDraw < 30 && trunkShown;
            else
                ok = RM_BiomesSettings.canopyEnabled && alpha <= 0f && RM_Canopy.LastAlpha <= 0f && layer != null
                     && layer.printed > 0 && (framesSinceDraw < 0 || framesSinceDraw > 5) && trunkShown;
            return (ok ? "PASS " : "FAIL ") + zoom + " " + sb;
        }

        private static CellRect Crown(Plant tree, Map map)
        {
            RM_CanopyExtension ext = RM_Canopy.ExtFor(tree.def);
            if (ext != null && RM_SectionLayer_Canopy.Place(tree, ext, out _, out Vector3 c, out float side, out _, out _))
                return RM_SectionLayer_Canopy.CanopyRect(c, side).ClipInsideMap(map);
            return CellRect.Empty;
        }

        private static bool PastSection(Plant tree, Map map)
        {
            CellRect want = Crown(tree, map);
            CellRect sec = map.mapDrawer.SectionAt(tree.Position).CellRect;
            return want.Area > 0 && !(sec.Contains(want.Min) && sec.Contains(want.Max));
        }

        private static RM_SectionLayer_Canopy LayerFor(Map map, IntVec3 c)
        {
            Section s = map.mapDrawer.SectionAt(c);
            return s?.GetLayer(typeof(RM_SectionLayer_Canopy)) as RM_SectionLayer_Canopy;
        }

        private static Plant FindTree(Map map)
        {
            foreach (Thing t in map.listerThings.ThingsInGroup(ThingRequestGroup.Plant))
                if (t is Plant p && RM_Canopy.ExtFor(p.def) is RM_CanopyExtension ext && !map.fogGrid.IsFogged(p.Position)
                    && ReferenceEquals(p.Graphic, ext.Trunk(p.def))     // a sapling or leafless tree prints no canopy
                    && PastSection(p, map)) return p;                      // L1 proves the crown that leaves its section
            return null;
        }

        private static Plant FindOrSpawn(Map map, out string how)
        {
            Plant found = FindTree(map);
            if (found != null) { how = "found"; return found; }
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(ProofTree);
            if (def == null) { how = ProofTree + " is not loaded"; return null; }
            IntVec3 centre = map.Center;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, 30f, true))
            {
                if (!c.InBounds(map) || map.fogGrid.IsFogged(c) || !c.Standable(map) || c.GetEdifice(map) != null) continue;
                if (c.GetPlant(map) != null) c.GetPlant(map).Destroy();
                var p = (Plant)ThingMaker.MakeThing(def);
                p.Growth = 1f;
                GenSpawn.Spawn(p, c, map);
                if (!PastSection(p, map)) { p.Destroy(); continue; }   // its crown fits its section: try the next cell
                how = "spawned";
                return p;
            }
            how = "no free cell near the centre";
            return null;
        }
    }
}
