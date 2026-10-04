using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Aerial
{
    /// <summary>
    /// Aerial art, per cable style (owner review 2026-10-04 B5/B6/B12/B16; owner spec MESSYCONDUIT_STYLED_POLES_1: each look
    /// owns its ground cables, its poles and its hanging cables; B19 split Jawa and Star Wars into two looks):
    ///   * Scrapper (StarWarsJawa): the crude hacked-together scrap mast, a thick dark scrap cable overhead;
    ///   * Industrial (StarWars): thick BLACK rubber cable overhead, tough industrial steel poles;
    ///   * Modern (ExtensionCord): BLACK hanging power lines (the ground cords stay multi-coloured), modern poles;
    ///   * Futuristic (Cybertek): sleek steel cable overhead, sleek angular steel poles.
    /// A span reads the style's own SpanWire (Aerial/Styles/&lt;Look&gt;/SpanWire) and falls back to the cable named in
    /// <see cref="SpanFallback"/>; a pole reads Aerial/Styles/&lt;Look&gt;/&lt;base name&gt; and, until that art lands
    /// (artpipe), draws the shared pole art TINTED for the look (a stand-in, recorded in <see cref="PoleStandIns"/>).
    /// Fallen cords and the hanging drop of a cut wire use the span cable, never the floor cord (B11).
    /// Rebuilt in place on a style change (EnsureCurrent).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class AerialMaterials
    {
        public const string Dir = "RimMandrake/MessyConduit/";
        public const string AerialDir = "RimMandrake/MessyConduit/Aerial/";
        public const string AerialStyleDir = AerialDir + "Styles/";
        public static Material Span;
        public static Material Shadow;
        public static Material Fallen;
        public static Material Glow;
        public static Material FrayLive;
        public static Material FrayDead;
        public static string SpanPath, BuiltKey = "", Look = "Scrapper";
        /// <summary>Span ribbon width (cells) for the look: Star Wars cable is thick, modern and Cybertek lines thin. PROVISIONAL.</summary>
        public static float SpanWidth = 0.17f;
        /// <summary>State read: the texture each pole def draws now, and which poles are tinted stand-ins.</summary>
        public static readonly Dictionary<string, string> PoleTex = new Dictionary<string, string>();
        public static readonly List<string> PoleStandIns = new List<string>();
        public static Color PoleTint = Color.white;

        static AerialMaterials() { Build(); }

        public static bool EnsureCurrent()
        {
            string key = CordMaterials.BuiltKey;
            if (key == BuiltKey) return false;
            Build();
            return true;
        }

        public static string LookOf(CordStyle s)
        {
            switch (s)
            {
                case CordStyle.ExtensionCord: return "Modern";
                case CordStyle.Cybertek: return "Futuristic";
                case CordStyle.StarWars: return "Industrial";
                default: return "Scrapper";
            }
        }

        public static string SpanFallback(string look)
        {
            switch (look)
            {
                case "Futuristic": return CordMaterials.StyleDir + "Cybertek/Strand";
                case "Scrapper": return Dir + "Strand_Jawa";
                default: return CordMaterials.StyleDir + "StarWars/Strand_BlackRubber";   // black for Industrial AND modern lines
            }
        }

        public static float WidthOf(string look)
        {
            switch (look)
            {
                case "Industrial": return 0.17f;
                case "Scrapper": return 0.14f;
                default: return 0.095f;
            }
        }

        /// <summary>Stand-in tint until per-look pole art exists (the shared art IS the Scrapper mast): dark steel for
        /// Industrial, a pale weathered grey for Modern, cool bright steel for Futuristic. PROVISIONAL.</summary>
        public static Color TintOf(string look)
        {
            switch (look)
            {
                case "Industrial": return new Color(0.52f, 0.55f, 0.60f, 1f);
                case "Modern": return new Color(0.86f, 0.84f, 0.80f, 1f);
                case "Futuristic": return new Color(0.80f, 0.88f, 0.97f, 1f);
                default: return Color.white;
            }
        }

        public static void Build()
        {
            CordMaterials.EnsureCurrent();
            Look = LookOf(MessyConduitSettings.style);
            SpanWidth = WidthOf(Look);
            string own = AerialStyleDir + Look + "/SpanWire";
            SpanPath = Exists(own) ? own : SpanFallback(Look);
            Span = Tiled(SpanPath) ?? Tiled(Dir + "Strand_Jawa");
            Fallen = Span;
            Shadow = Tiled(AerialDir + "SpanShadow", new Color(1f, 1f, 1f, 0.7f)) ?? Tiled(Dir + "StrandShadow", new Color(1f, 1f, 1f, 0.45f));
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", false);
            Glow = glow != null ? MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow)) : null;
            FrayLive = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayLive) ?? Plain(Dir + "EndFrayed_Live", Color.white);
            FrayDead = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayDead) ?? Plain(Dir + "EndFrayed_Dead", new Color(0.62f, 0.58f, 0.55f, 1f));
            ApplyPoles();
            BuiltKey = CordMaterials.BuiltKey;
        }

        // ------------------------------------------------------------------ poles follow the look (B6/B16)
        private static readonly Dictionary<ThingDef, GraphicData> originals = new Dictionary<ThingDef, GraphicData>();
        private static readonly Dictionary<ThingDef, string> origTops = new Dictionary<ThingDef, string>();
        private static readonly Dictionary<ThingDef, string> tops = new Dictionary<ThingDef, string>();

        public static string TopPathFor(ThingDef d) => d != null && tops.TryGetValue(d, out string p) ? p : null;

        /// <summary>Per-look pole geometry, measured from each look's own art when it lands (128x512 canvas drawn 1x4 cells,
        /// base at the bottom): insulator height (attachZ) and the centre of the cropped top overlay (topOffsetZ), both in
        /// cells above the cell centre. Key "Look/defName". Absent = the def's own values (the shared Scrapper art).</summary>
        public static readonly Dictionary<string, Vector2> PoleGeometry = PoleGeometryTable.Build();

        private static readonly Dictionary<ThingDef, Vector2> origGeom = new Dictionary<ThingDef, Vector2>();

        private static void ApplyGeometry(ThingDef d, bool real)
        {
            AerialAnchorExtension ext = d.GetModExtension<AerialAnchorExtension>();
            if (ext == null) return;
            if (!origGeom.ContainsKey(d)) origGeom[d] = new Vector2(ext.attachZ, ext.topOffsetZ);
            Vector2 g = origGeom[d];
            if (real && PoleGeometry.TryGetValue(Look + "/" + d.defName, out Vector2 m)) g = m;
            ext.attachZ = g.x;
            ext.topOffsetZ = g.y;
        }

        private static void ApplyPoles()
        {
            PoleTex.Clear();
            PoleStandIns.Clear();
            PoleTint = TintOf(Look);
            foreach (ThingDef d in new[] { AerialDefOf.RM_AerialMast, AerialDefOf.RM_AerialLampMast, AerialDefOf.RM_AerialWallBracket })
            {
                if (d?.graphicData == null) continue;
                if (!originals.ContainsKey(d))
                {
                    originals[d] = d.graphicData;
                    origTops[d] = d.GetModExtension<AerialAnchorExtension>()?.topTexPath;
                }
                GraphicData orig = originals[d];
                string baseName = orig.texPath.Substring(orig.texPath.LastIndexOf('/') + 1);
                string own = AerialStyleDir + Look + "/" + baseName;
                var use = new GraphicData();
                use.CopyFrom(orig);
                bool real = Exists(own);
                if (real) { use.texPath = own; use.color = Color.white; }
                else
                {
                    use.color = PoleTint;
                    if (Look != "Scrapper") PoleStandIns.Add(d.defName);
                }
                d.graphicData = use;
                d.graphic = use.Graphic;
                ApplyGeometry(d, real);
                PoleTex[d.defName] = use.texPath + (real || Look == "Scrapper" ? "" : " (tinted stand-in)");
                string ot = origTops[d];
                if (!ot.NullOrEmpty())
                {
                    string ownTop = AerialStyleDir + Look + "/" + ot.Substring(ot.LastIndexOf('/') + 1);
                    tops[d] = real && Exists(ownTop) ? ownTop : ot;
                }
            }
            if (Current.ProgramState == ProgramState.Playing && Find.Maps != null)
                foreach (Map map in Find.Maps)
                    foreach (Thing t in map.listerThings.AllThings)
                        if (originals.ContainsKey(t.def)) t.Notify_ColorChanged();
        }

        private static bool Exists(string path)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(path, false);
            return t != null && t != BaseContent.BadTex;
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

        private static readonly Dictionary<string, Material> topMats = new Dictionary<string, Material>();

        /// <summary>The mast head drawn above pawns, in the look's art (or the shared art in the look's stand-in tint).</summary>
        public static Material Top(string texPath)
        {
            if (texPath.NullOrEmpty()) return null;
            bool own = texPath.StartsWith(AerialStyleDir);
            Color c = own ? Color.white : PoleTint;
            string key = texPath + "|" + c;
            if (topMats.TryGetValue(key, out Material m)) return m;
            Texture2D tex = ContentFinder<Texture2D>.Get(texPath, true);
            m = tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, c));
            topMats[key] = m;
            return m;
        }
    }
}
