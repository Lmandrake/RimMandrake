using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// TREE_SHADE_BUILD_CROWNS_ON_STILTS (design/RimMandrake/tree_shade_model_2026-10-19.md §4.5; owner card 2026-10-19
    /// Q3: "(2) + an experiment with (3)"), the readable sign of shade, two layers:
    /// - The shade overlay: a toggle in the bottom-right play-settings row, like vanilla's roof and fertility overlays
    ///   (a CellBoolDrawer). Under Direct Sun it shades exactly the cells ExposureAt reads, from the same exposure array,
    ///   deeper blue for deeper shade, so what the player sees is what the pawn feels. Without Direct Sun it shows the
    ///   shade grid the shade-seeking animals read.
    /// - The ground tint under canopy: a subtle, always-on darkening of the ground where a crown's shadow falls, drawn at
    ///   filth altitude (under plants and pawns, which write depth). No new art. Its own setting.
    /// Both rebuild their mesh only when the grid recomputes (GridVersion), never per frame.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RM_ShadeOverlay
    {
        /// <summary>The overlay toggle; not saved, like a fresh game's vanilla overlays.</summary>
        public static bool showShadeOverlay;

        /// <summary>A procedural icon (a sun with a dark half): no texture file.</summary>
        public static readonly Texture2D Icon = MakeIcon();

        private static Texture2D MakeIcon()
        {
            const int N = 32;
            Texture2D t = new Texture2D(N, N, TextureFormat.RGBA32, false);
            Color sun = new Color(1f, 0.82f, 0.35f, 1f);
            Color shade = new Color(0.22f, 0.3f, 0.55f, 1f);
            for (int y = 0; y < N; y++)
            {
                for (int x = 0; x < N; x++)
                {
                    float dx = x - N / 2f + 0.5f;
                    float dy = y - N / 2f + 0.5f;
                    float d = Mathf.Sqrt(dx * dx + dy * dy);
                    Color c = d <= N * 0.42f ? (dx + dy < 0f ? shade : sun) : Color.clear;
                    t.SetPixel(x, y, c);
                }
            }
            t.Apply();
            t.name = "RM_ShadeOverlayIcon";
            return t;
        }

        public static void Postfix_PlaySettings(WidgetRow row, bool worldView)
        {
            if (worldView || row == null || !RM_CreatureBehaviorsSettings.shadeGridEnabled
                || !RM_CreatureBehaviorsSettings.shadeOverlayButton)
            {
                return;
            }
            row.ToggleableIcon(ref showShadeOverlay, Icon,
                "Show shade: where Direct Sun is blocked, and how much (deeper blue is deeper shade). "
              + "It shows exactly the shade your creatures feel: roofs, trees, rock, walls, tents.",
                SoundDefOf.Mouseover_ButtonToggle);
        }
    }

    /// <summary>The overlay and tint drawers of one map's shade grid (RM_MapComponent_ShadeGrid.MapComponentUpdate).</summary>
    public class RM_ShadeOverlayDrawers
    {
        private const float OverlayMinShade = 0.05f;
        private const float TintMinCanopy = 0.5f;
        private const float TintAlpha = 0.16f;
        private const int MaxCellsPerMesh = 16383;

        private readonly RM_MapComponent_ShadeGrid grid;
        private readonly Map map;
        private CellBoolDrawer overlay;
        private int overlayVersion = -1;

        private readonly List<Mesh> tintMeshes = new List<Mesh>();
        private int tintVersion = -1;
        private static Material tintMat;

        public RM_ShadeOverlayDrawers(RM_MapComponent_ShadeGrid grid, Map map)
        {
            this.grid = grid;
            this.map = map;
        }

        public void Update()
        {
            if (map != Find.CurrentMap || RimWorld.Planet.WorldRendererUtility.WorldRendered || !RM_CreatureBehaviorsSettings.shadeGridEnabled)
            {
                return;
            }
            if (RM_ShadeOverlay.showShadeOverlay && RM_CreatureBehaviorsSettings.shadeOverlayButton)
            {
                if (overlay == null)
                {
                    overlay = new CellBoolDrawer(i => grid.OverlayShade(i) >= OverlayMinShade, () => Color.white,
                        i => Color.Lerp(new Color(0.55f, 0.75f, 1f), new Color(0.05f, 0.1f, 0.6f), grid.OverlayShade(i)),
                        map.Size.x, map.Size.z, 0.45f);
                }
                if (overlayVersion != grid.GridVersion)
                {
                    overlay.SetDirty();
                    overlayVersion = grid.GridVersion;
                }
                overlay.MarkForDraw();
                overlay.CellBoolDrawerUpdate();
            }
            if (RM_CreatureBehaviorsSettings.treeCanopyShadeEnabled && RM_CreatureBehaviorsSettings.canopyGroundTint)
            {
                if (tintVersion != grid.GridVersion)
                {
                    RebuildTint();
                    tintVersion = grid.GridVersion;
                }
                if (tintMat == null)
                {
                    tintMat = SolidColorMaterials.SimpleSolidColorMaterial(new Color(0f, 0.03f, 0.02f, TintAlpha), false);
                }
                for (int k = 0; k < tintMeshes.Count; k++)
                {
                    Graphics.DrawMesh(tintMeshes[k], Vector3.zero, Quaternion.identity, tintMat, 0);
                }
            }
        }

        private void RebuildTint()
        {
            for (int k = 0; k < tintMeshes.Count; k++)
            {
                tintMeshes[k].Clear();
            }
            int w = map.Size.x;
            int h = map.Size.z;
            float y = AltitudeLayer.Filth.AltitudeFor() - 0.01f;
            List<Vector3> verts = new List<Vector3>();
            List<int> tris = new List<int>();
            int mesh = 0;
            int cells = 0;
            for (int z = 0; z < h; z++)
            {
                for (int x = 0; x < w; x++)
                {
                    if (grid.CanopyShadeAtIndex(z * w + x) < TintMinCanopy)
                    {
                        continue;
                    }
                    int b = verts.Count;
                    verts.Add(new Vector3(x, y, z));
                    verts.Add(new Vector3(x, y, z + 1));
                    verts.Add(new Vector3(x + 1, y, z + 1));
                    verts.Add(new Vector3(x + 1, y, z));
                    tris.Add(b); tris.Add(b + 1); tris.Add(b + 2);
                    tris.Add(b); tris.Add(b + 2); tris.Add(b + 3);
                    if (++cells >= MaxCellsPerMesh)
                    {
                        Flush(mesh++, verts, tris);
                        cells = 0;
                    }
                }
            }
            Flush(mesh, verts, tris);
        }

        private void Flush(int index, List<Vector3> verts, List<int> tris)
        {
            if (verts.Count == 0)
            {
                return;
            }
            while (tintMeshes.Count <= index)
            {
                tintMeshes.Add(new Mesh { name = "RM_CanopyTint" });
            }
            Mesh m = tintMeshes[index];
            m.SetVertices(verts);
            m.SetTriangles(tris, 0);
            verts.Clear();
            tris.Clear();
        }
    }
}
