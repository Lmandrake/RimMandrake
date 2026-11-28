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

        /// <summary>The live script's reading (live_crown_shadow_experiment.py, by jawa/static_call): what the drawer of this
        /// map did, one line of key=value pairs. Read only.</summary>
        public static string CrownShadowReport(Map map)
        {
            RM_MapComponent_ShadeGrid g = map?.GetComponent<RM_MapComponent_ShadeGrid>();
            if (g == null)
            {
                return "grid=none";
            }
            return g.CrownShadowReport();
        }

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

    /// <summary>One drawn crown shadow (RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE): its square's centre
    /// and half side in world units, and the crown's opacity.</summary>
    public struct RM_RenderedCrown
    {
        public readonly float x;
        public readonly float z;
        public readonly float half;
        public readonly float opacity;

        public RM_RenderedCrown(float x, float z, float half, float opacity)
        {
            this.x = x;
            this.z = z;
            this.half = half;
            this.opacity = opacity;
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
        private Material tintMat;   // per drawer, made on the main thread at first draw (a static Material warns at startup)

        // RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE: the drawn crown shadows, one map-sized soft alpha layer
        // (RM_SunHeatMath.StampCrownShadow keeps the max, so overlapping crowns cast one shadow, not a darker one) drawn
        // as one quad, rebuilt on GridVersion like the tint. The first try drew one alpha-blended quad per crown; in a
        // forest the overlaps stacked to near black (2026-11-27, ArchSmall, 138 greatboles).
        private const float CrownShadowAlpha = 0.42f;
        private const int TexelsPerCell = 3;
        private Texture2D shadowLayer;
        private float[] shadowAlpha;
        private Color32[] shadowPixels;
        private Mesh shadowQuad;
        private Material shadowMat;
        private int shadowVersion = -1;
        private int shadowsBuilt;
        private int shadowsDrawnLastFrame;
        private int shadowMeshCount;
        private double shadowRebuildMs;
        private readonly System.Diagnostics.Stopwatch drawWatch = new System.Diagnostics.Stopwatch();
        private double drawUsSum;
        private int drawFrames;
        private float frameSecSum;
        private int frameCount;

        public RM_ShadeOverlayDrawers(RM_MapComponent_ShadeGrid grid, Map map)
        {
            this.grid = grid;
            this.map = map;
        }

        /// <summary>The live script's one-line reading (RM_ShadeOverlay.CrownShadowReport): shadows built and drawn last
        /// frame, meshes, last rebuild ms, mean drawer µs per frame and mean frame ms since the last reset. reset=true
        /// starts a new sample.</summary>
        public string Report(bool reset)
        {
            string r = string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "enabled={0} built={1} drawn={2} meshes={3} rebuildMs={4:0.###} drawUsMean={5:0.###} frameMsMean={6:0.###} frames={7}",
                RM_CreatureBehaviorsSettings.renderedCrownShadows, shadowsBuilt, shadowsDrawnLastFrame, shadowMeshCount,
                shadowRebuildMs, drawFrames > 0 ? drawUsSum / drawFrames : 0.0,
                frameCount > 0 ? frameSecSum * 1000f / frameCount : 0f, frameCount);
            if (reset)
            {
                drawUsSum = 0;
                drawFrames = 0;
                frameSecSum = 0f;
                frameCount = 0;
            }
            return r;
        }

        public void Update()
        {
            if (map != Find.CurrentMap || RimWorld.Planet.WorldRendererUtility.WorldRendered || !RM_CreatureBehaviorsSettings.shadeGridEnabled)
            {
                return;
            }
            frameSecSum += Time.unscaledDeltaTime;
            frameCount++;
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
                // The tint skips the drawn shadows' cells, so a switch of the drawn shadow rebuilds it too.
                int tintKey = grid.GridVersion * 2 + (RM_CreatureBehaviorsSettings.renderedCrownShadows ? 1 : 0);
                if (tintVersion != tintKey)
                {
                    RebuildTint();
                    tintVersion = tintKey;
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
            DrawCrownShadows();
        }

        private void DrawCrownShadows()
        {
            shadowsDrawnLastFrame = 0;
            if (!RM_CreatureBehaviorsSettings.treeCanopyShadeEnabled || !RM_CreatureBehaviorsSettings.renderedCrownShadows)
            {
                return;
            }
            drawWatch.Restart();
            if (shadowVersion != grid.GridVersion)
            {
                RebuildShadows();
                shadowVersion = grid.GridVersion;
            }
            if (shadowsBuilt > 0)
            {
                if (shadowMat == null)
                {
                    shadowMat = MaterialPool.MatFrom(shadowLayer, ShaderDatabase.Transparent,
                        new Color(0f, 0.02f, 0.03f, CrownShadowAlpha));
                }
                Graphics.DrawMesh(shadowQuad, Vector3.zero, Quaternion.identity, shadowMat, 0);
                shadowsDrawnLastFrame = shadowsBuilt;
            }
            drawWatch.Stop();
            drawUsSum += drawWatch.Elapsed.TotalMilliseconds * 1000.0;
            drawFrames++;
        }

        private void RebuildShadows()
        {
            System.Diagnostics.Stopwatch w = System.Diagnostics.Stopwatch.StartNew();
            int tw = map.Size.x * TexelsPerCell;
            int th = map.Size.z * TexelsPerCell;
            if (shadowLayer == null)
            {
                shadowLayer = new Texture2D(tw, th, TextureFormat.RGBA32, false)
                {
                    name = "RM_CrownShadowLayer",
                    wrapMode = TextureWrapMode.Clamp,
                    filterMode = FilterMode.Bilinear
                };
                shadowAlpha = new float[tw * th];
                shadowPixels = new Color32[tw * th];
                // Just under the tint (filth altitude, under plants and pawns, which write depth).
                float y = AltitudeLayer.Filth.AltitudeFor() - 0.012f;
                shadowQuad = new Mesh { name = "RM_CrownShadowQuad" };
                shadowQuad.SetVertices(new List<Vector3>
                {
                    new Vector3(0f, y, 0f), new Vector3(0f, y, map.Size.z),
                    new Vector3(map.Size.x, y, map.Size.z), new Vector3(map.Size.x, y, 0f)
                });
                shadowQuad.SetUVs(0, new List<Vector2>
                {
                    new Vector2(0f, 0f), new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(1f, 0f)
                });
                shadowQuad.SetTriangles(new[] { 0, 1, 2, 0, 2, 3 }, 0);
                shadowQuad.RecalculateBounds();
            }
            System.Array.Clear(shadowAlpha, 0, shadowAlpha.Length);
            List<RM_RenderedCrown> crowns = grid.RenderedCrowns;
            int built = 0;
            for (int c = 0; c < crowns.Count; c++)
            {
                RM_RenderedCrown rc = crowns[c];
                if (RM_SunHeatMath.StampCrownShadow(shadowAlpha, tw, th, TexelsPerCell, rc.x, rc.z, rc.half,
                    RM_SunHeatMath.CrownShadowCore, rc.opacity) > 0)
                {
                    built++;
                }
            }
            // An empty layer is uploaded too, so a forest that is gone leaves no stale shadow.
            for (int i = 0; i < shadowAlpha.Length; i++)
            {
                shadowPixels[i] = new Color32(255, 255, 255, (byte)(shadowAlpha[i] * 255f + 0.5f));
            }
            shadowLayer.SetPixels32(shadowPixels);
            shadowLayer.Apply(false);
            shadowsBuilt = built;
            shadowMeshCount = built > 0 ? 1 : 0;
            shadowRebuildMs = w.Elapsed.TotalMilliseconds;
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
                    int ci = z * w + x;
                    if (grid.CanopyShadeAtIndex(ci) < TintMinCanopy)
                    {
                        continue;
                    }
                    if (RM_CreatureBehaviorsSettings.renderedCrownShadows && grid.RenderedCrownOwnsIndex(ci))
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
