using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Aerial art. Spans reuse the floor strand of the selected cord style (design 2.8: no new span art; lane C
    /// 2026-10-02: the span follows the style, its first strand variant, so an extension-cord net strings the
    /// first colour overhead); the ground shadow is the real Aerial/SpanShadow strip. Mast, mast top and wall
    /// bracket are real artpipe art (wire_style_art.py); the lamp mast, its top and the tap clamp are still the
    /// procedural placeholders of export_aerial_textures.py. Rebuilt in place on a style change (EnsureCurrent).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class AerialMaterials
    {
        public const string Dir = "RimMandrake/MessyConduit/";
        public const string AerialDir = "RimMandrake/MessyConduit/Aerial/";
        public static Material Span;
        public static Material Shadow;
        public static Material Fallen;
        public static Material Glow;
        public static Material FrayLive;
        public static Material FrayDead;
        public static string SpanPath, BuiltKey = "";

        static AerialMaterials() { Build(); }

        public static bool EnsureCurrent()
        {
            string key = CordMaterials.BuiltKey;
            if (key == BuiltKey) return false;
            Build();
            return true;
        }

        public static void Build()
        {
            CordMaterials.EnsureCurrent();
            SpanPath = CordMaterials.StrandPaths.Length > 0 ? CordMaterials.StrandPaths[0] : Dir + "Strand_Jawa";
            Span = Tiled(SpanPath);
            Fallen = Span;
            Shadow = Tiled(AerialDir + "SpanShadow", new Color(1f, 1f, 1f, 0.7f)) ?? Tiled(Dir + "StrandShadow", new Color(1f, 1f, 1f, 0.45f));
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", false);
            Glow = glow != null ? MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow)) : null;
            FrayLive = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayLive) ?? Plain(Dir + "EndFrayed_Live", Color.white);
            FrayDead = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayDead) ?? Plain(Dir + "EndFrayed_Dead", new Color(0.62f, 0.58f, 0.55f, 1f));
            BuiltKey = CordMaterials.BuiltKey;
        }

        private static Material Tiled(string path, Color? c = null)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
            if (tex == null) return null;
            tex.wrapMode = TextureWrapMode.Repeat;
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, c ?? Color.white));
        }

        private static Material Plain(string path, Color c)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, true);
            return tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, c));
        }

        private static readonly System.Collections.Generic.Dictionary<string, Material> tops = new System.Collections.Generic.Dictionary<string, Material>();

        public static Material Top(string texPath)
        {
            if (texPath.NullOrEmpty()) return null;
            if (tops.TryGetValue(texPath, out Material m)) return m;
            Texture2D tex = ContentFinder<Texture2D>.Get(texPath, true);
            m = tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent));
            tops[texPath] = m;
            return m;
        }
    }
}
