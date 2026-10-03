using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Aerial art. Spans reuse the floor strand (Strand_Jawa) and its shadow (design 2.8: no new art). Mast heads,
    /// mast bodies, the bracket and the clamp are PROCEDURAL PLACEHOLDERS exported by
    /// src/RimMandrake/Utils/mockups/messy_conduit/export_aerial_textures.py until the artpipe jobs
    /// (RM_MessyConduit_Jawa_AerialMast / _AerialMastTop / _AerialLampMast / _WallBracket / _TapClamp) are finished:
    /// swap = drop the generated PNGs over the same paths.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class AerialMaterials
    {
        public const string Dir = "RimMandrake/MessyConduit/";
        public const string AerialDir = "RimMandrake/MessyConduit/Aerial/";
        public static readonly Material Span;
        public static readonly Material Shadow;
        public static readonly Material Fallen;
        public static readonly Material Glow;
        public static readonly Material FrayLive;
        public static readonly Material FrayDead;

        static AerialMaterials()
        {
            Span = Tiled(Dir + "Strand_Jawa");
            Fallen = Tiled(Dir + "Strand_Jawa");
            Shadow = Tiled(Dir + "StrandShadow", new Color(1f, 1f, 1f, 0.45f));
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", false);
            if (glow != null) Glow = MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow));
            FrayLive = Plain(Dir + "EndFrayed_Live", Color.white);
            FrayDead = Plain(Dir + "EndFrayed_Dead", new Color(0.62f, 0.58f, 0.55f, 1f));
        }

        private static Material Tiled(string path, Color? c = null)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, true);
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
