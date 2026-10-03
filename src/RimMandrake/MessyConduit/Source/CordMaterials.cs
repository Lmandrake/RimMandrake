using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>
    /// Cord art, per selectable style (owner, 2026-10-02: several art styles for players). Textures live under
    /// Textures/RimMandrake/MessyConduit/: the Jawa default set at the folder root (phase 1a names), every other
    /// family under Styles/&lt;Family&gt;/ with fixed slot names (Strand[_Variant], Junction_T, Junction_X, Plug,
    /// StubWall, StubRock, EndFrayed_Dead), wired by src/RimMandrake/Utils/mockups/messy_conduit/wire_style_art.py.
    /// A slot a family has no art for falls back to the Jawa root piece (listed in <see cref="Fallbacks"/>).
    ///
    /// Materials are rebuilt in place when the style or the extension-cord colour mode changes
    /// (<see cref="EnsureCurrent"/>, called by MessyConduitSettings.Apply before the map meshes regenerate), so a
    /// style change needs no restart. Strand strips tile along their length (wrap mode Repeat).
    /// A family with several strands (extension-cord colours, Star Wars cable kinds) picks one per power net,
    /// seeded per net (<see cref="VariantFor"/>).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class CordMaterials
    {
        public const string Dir = "RimMandrake/MessyConduit/";
        public const string StyleDir = Dir + "Styles/";

        public static Material Strand;
        public static Material Shadow;
        /// <summary>A strand hanging over a wall face (wall terminal tail): drawn after the wall.</summary>
        public static Material StrandFace;
        public static Material SparkGlow;
        /// <summary>Additive glow pulsed at a LIVE end every frame (also while paused).</summary>
        public static Material LiveGlow;
        private static Dictionary<DecalKind, Material> decals = new Dictionary<DecalKind, Material>();
        /// <summary>Phase 1b: the far-zoom (LOD) strand, a separate Material instance so it lands in its own
        /// sub-mesh; the selection highlight (white band tinted warm, drawn over the cords).</summary>
        public static Material StrandLod, Highlight;

        private static Material[] strandV = new Material[0], faceV = new Material[0], lodV = new Material[0];
        private static readonly HashSet<Material> lods = new HashSet<Material>();
        private static readonly Dictionary<Texture2D, Material> lodCache = new Dictionary<Texture2D, Material>();

        /// <summary>State read (StyleProbe): what the current build resolved.</summary>
        public static string BuiltKey = "";
        public static int Rebuilds;
        public static string[] StrandPaths = new string[0];
        public static readonly Dictionary<string, string> SlotPaths = new Dictionary<string, string>();
        public static readonly List<string> Fallbacks = new List<string>();
        public static readonly List<string> Missing = new List<string>();

        /// <summary>Render queues. Every SectionLayer submesh gets the SAME bounds
        /// (MapDrawLayer.RefreshSubMeshBounds, decompiled 1.6), so transparent submeshes tie on sort
        /// distance and their altitude alone does not order them: an explicit queue does. Shadow under
        /// strand, end pieces over strand, face pieces (wall/rock stubs, hanging tails) last.</summary>
        public static int StrandQueue, ShadowQueue, PieceQueue, FaceQueue;

        public static readonly string[] ExtCordColors = { "Orange", "Green", "Brown", "Yellow", "Blue" };
        public static readonly string[] StarWarsKinds = { "BlackRubber", "CorrugatedSteel", "CoiledBlack" };
        /// <summary>Star Wars per-net pick weights (out of 10): thick black rubber most, steel and coiled rarer.</summary>
        private static readonly int[] StarWarsWeights = { 6, 2, 2 };

        static CordMaterials()
        {
            Texture2D jawa = ContentFinder<Texture2D>.Get(Dir + "Strand_Jawa", reportFailure: true);
            int q = jawa != null ? MaterialPool.MatFrom(new MaterialRequest(jawa, ShaderDatabase.Transparent)).renderQueue : 3000;
            StrandQueue = q;
            ShadowQueue = q - 1;
            PieceQueue = q + 1;
            FaceQueue = q + 2;
            Highlight = MaterialPool.MatFrom(new MaterialRequest(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(1f, 0.85f, 0.35f, 0.42f)) { renderQueue = FaceQueue + 1 });
            Build();
        }

        public static string Family(CordStyle s)
        {
            switch (s)
            {
                case CordStyle.ExtensionCord: return "ExtCord";
                case CordStyle.Cybertek: return "Cybertek";
                case CordStyle.StarWars: return "StarWars";
                default: return "Jawa";
            }
        }

        public static string CurrentKey() =>
            MessyConduitSettings.style + "/" + MessyConduitSettings.extCordColorMode + "/" + Mathf.Clamp(MessyConduitSettings.extCordColor, 0, ExtCordColors.Length - 1);

        /// <summary>Rebuild if the style or the colour mode changed since the last build. True if it rebuilt.</summary>
        public static bool EnsureCurrent()
        {
            if (BuiltKey == CurrentKey()) return false;
            Build();
            return true;
        }

        /// <summary>The strand texture paths of a style (one per per-net variant).</summary>
        public static string[] StrandPathsFor(CordStyle s)
        {
            switch (s)
            {
                case CordStyle.Cybertek: return new[] { StyleDir + "Cybertek/Strand" };
                case CordStyle.ExtensionCord:
                    if (MessyConduitSettings.extCordColorMode == ExtCordColorMode.Single)
                        return new[] { StyleDir + "ExtCord/Strand_" + ExtCordColors[Mathf.Clamp(MessyConduitSettings.extCordColor, 0, ExtCordColors.Length - 1)] };
                    var l = new string[ExtCordColors.Length];
                    for (int i = 0; i < l.Length; i++) l[i] = StyleDir + "ExtCord/Strand_" + ExtCordColors[i];
                    return l;
                case CordStyle.StarWars:
                    var w = new string[StarWarsKinds.Length];
                    for (int i = 0; i < w.Length; i++) w[i] = StyleDir + "StarWars/Strand_" + StarWarsKinds[i];
                    return w;
                default: return new[] { Dir + "Strand_Jawa" };
            }
        }

        /// <summary>Path of a decal slot for a style; Jawa slot names at the root, others under Styles/.</summary>
        public static string SlotPath(CordStyle s, string slot)
        {
            if (s == CordStyle.StarWarsJawa) return Dir + JawaName(slot);
            return StyleDir + Family(s) + "/" + slot;
        }

        private static string JawaName(string slot)
        {
            switch (slot)
            {
                case "Junction_T": return "Junction_Tape";
                case "Junction_X": return "Junction_Tin";
                default: return slot;
            }
        }

        public static readonly string[] Slots = { "Plug", "Junction_T", "Junction_X", "StubWall", "StubRock", "PowerStrip", "EndFrayed_Dead", "EndFrayed_Live" };

        public static void Build()
        {
            CordStyle style = MessyConduitSettings.style;
            Fallbacks.Clear();
            Missing.Clear();
            SlotPaths.Clear();
            // ---- strands (per-net variants)
            string[] paths = StrandPathsFor(style);
            var sv = new List<Material>(); var fv = new List<Material>(); var lv = new List<Material>(); var used = new List<string>();
            foreach (string p in paths)
            {
                Texture2D tex = Tex(p);
                if (tex == null) { Missing.Add(p); continue; }
                tex.wrapMode = TextureWrapMode.Repeat;
                sv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = StrandQueue }));
                fv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = FaceQueue }));
                if (!lodCache.TryGetValue(tex, out Material lod))
                {
                    lod = new Material(sv[sv.Count - 1]) { name = "RM_MessyCords_StrandLod_" + tex.name };
                    lodCache[tex] = lod;
                    lods.Add(lod);
                }
                lv.Add(lod);
                used.Add(p);
            }
            if (sv.Count == 0)
            {
                // the whole family is missing: draw the Jawa strand rather than nothing
                Fallbacks.Add("Strand");
                Texture2D tex = Tex(Dir + "Strand_Jawa");
                if (tex != null)
                {
                    tex.wrapMode = TextureWrapMode.Repeat;
                    sv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = StrandQueue }));
                    fv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = FaceQueue }));
                    if (!lodCache.TryGetValue(tex, out Material lod)) { lod = new Material(sv[0]) { name = "RM_MessyCords_StrandLod_" + tex.name }; lodCache[tex] = lod; lods.Add(lod); }
                    lv.Add(lod);
                    used.Add(Dir + "Strand_Jawa");
                }
            }
            strandV = sv.ToArray(); faceV = fv.ToArray(); lodV = lv.ToArray();
            StrandPaths = used.ToArray();
            Strand = strandV.Length > 0 ? strandV[0] : null;
            StrandFace = faceV.Length > 0 ? faceV[0] : null;
            StrandLod = lodV.Length > 0 ? lodV[0] : null;
            // ---- shadow and glow are shared by every family
            Shadow = TiledMat(Dir + "StrandShadow", ShadowQueue);
            SparkGlow = Mat(Dir + "SparkGlow", PieceQueue, null, "SparkGlow");
            Texture2D glow = Tex(Dir + "SparkGlow");
            LiveGlow = glow != null ? MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow)) : null;
            // ---- decals
            var d = new Dictionary<DecalKind, Material>();
            d[DecalKind.Plug] = SlotMat(style, "Plug", PieceQueue);
            d[DecalKind.JunctionTape] = SlotMat(style, "Junction_T", PieceQueue);
            d[DecalKind.JunctionTin] = SlotMat(style, "Junction_X", PieceQueue);
            d[DecalKind.StubWall] = SlotMat(style, "StubWall", FaceQueue);
            d[DecalKind.StubRock] = SlotMat(style, "StubRock", FaceQueue);
            d[DecalKind.PowerStrip] = SlotMat(style, "PowerStrip", PieceQueue);
            // a dead end's fray is dulled further so it reads cold beside the live one
            d[DecalKind.FrayDead] = SlotMat(style, "EndFrayed_Dead", PieceQueue, new Color(0.62f, 0.58f, 0.55f, 1f));
            d[DecalKind.FrayLive] = SlotMat(style, "EndFrayed_Live", PieceQueue);
            // phase 1b B6: LEDs dark when the net is dead. Until PowerStrip_Lit/_Dark art lands (artpipe), the
            // dark strip is the strip tinted down.
            Texture2D stripDark = Tex(Dir + "PowerStrip_Dark");
            d[DecalKind.PowerStripDark] = stripDark != null
                ? MaterialPool.MatFrom(new MaterialRequest(stripDark, ShaderDatabase.Transparent) { renderQueue = PieceQueue })
                : SlotMat(style, "PowerStrip", PieceQueue, new Color(0.42f, 0.40f, 0.40f, 1f), "PowerStripDark");
            decals = d;
            BuiltKey = CurrentKey();
            Rebuilds++;
        }

        private static Texture2D Tex(string path)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(path, reportFailure: false);
            return t == null || t == BaseContent.BadTex ? null : t;
        }

        /// <summary>The family's piece, or the Jawa root piece when the family has none (recorded).</summary>
        private static Material SlotMat(CordStyle s, string slot, int queue, Color? color = null, string key = null)
        {
            string path = SlotPath(s, slot);
            Texture2D tex = Tex(path);
            if (tex == null && s != CordStyle.StarWarsJawa)
            {
                Fallbacks.Add(key ?? slot);
                path = SlotPath(CordStyle.StarWarsJawa, slot);
                tex = Tex(path);
            }
            SlotPaths[key ?? slot] = tex == null ? null : path;
            if (tex == null) { Missing.Add(path); return null; }
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, color ?? Color.white) { renderQueue = queue });
        }

        private static Material Mat(string path, int queue, Color? color, string key)
        {
            Texture2D tex = Tex(path);
            SlotPaths[key] = tex == null ? null : path;
            if (tex == null) { Missing.Add(path); return null; }
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, color ?? Color.white) { renderQueue = queue });
        }

        private static Material TiledMat(string path, int queue)
        {
            Texture2D tex = Tex(path);
            SlotPaths["StrandShadow"] = tex == null ? null : path;
            if (tex == null) { Missing.Add(path); return null; }
            tex.wrapMode = TextureWrapMode.Repeat;
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = queue });
        }

        public static int VariantCount => strandV.Length;

        /// <summary>The strand variant for a net seed: uniform over the extension-cord colours, weighted for the
        /// Star Wars kinds, always 0 for a single-strand family or the single-colour mode.</summary>
        public static int VariantFor(int netSeed)
        {
            int n = strandV.Length;
            if (n <= 1) return 0;
            uint h = unchecked((uint)netSeed * 2654435761u);
            h ^= h >> 15;
            if (MessyConduitSettings.style == CordStyle.StarWars && n == StarWarsWeights.Length)
            {
                int r = (int)(h % 10u), acc = 0;
                for (int i = 0; i < n; i++) { acc += StarWarsWeights[i]; if (r < acc) return i; }
                return 0;
            }
            return (int)(h % (uint)n);
        }

        public static Material StrandFor(int v) => v >= 0 && v < strandV.Length ? strandV[v] : Strand;
        public static Material StrandFaceFor(int v) => v >= 0 && v < faceV.Length ? faceV[v] : StrandFace;
        public static Material StrandLodFor(int v) => v >= 0 && v < lodV.Length ? lodV[v] : StrandLod;

        public static bool IsLod(Material m) => m != null && lods.Contains(m);

        public static Material Decal(DecalKind k) => decals.TryGetValue(k, out Material m) ? m : null;

        public static bool IsFace(DecalKind k) => k == DecalKind.StubWall || k == DecalKind.StubRock;

        /// <summary>A style is selectable when its strand art is installed (every strand variant present).</summary>
        public static bool StyleInstalled(CordStyle s)
        {
            foreach (string p in StrandPathsFor(s)) if (Tex(p) == null) return false;
            return true;
        }

        /// <summary>Settings-screen swatch: the style's first strand texture (null if not installed).</summary>
        public static Texture2D Swatch(CordStyle s, int variant = 0)
        {
            string[] p = StrandPathsFor(s);
            return Tex(p[Mathf.Clamp(variant, 0, p.Length - 1)]);
        }
    }
}
