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
            Shadow = Tiled(AerialDir + "SpanShadow", new Color(1f, 1f, 1f, 0.32f)) ?? Tiled(Dir + "StrandShadow", new Color(1f, 1f, 1f, 0.45f));
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", false);
            Glow = glow != null ? MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow)) : null;
            FrayLive = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayLive) ?? Plain(Dir + "EndFrayed_Live", Color.white);
            FrayDead = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayDead) ?? Plain(Dir + "EndFrayed_Dead", new Color(0.62f, 0.58f, 0.55f, 1f));
            ApplyPoles();
            BuiltKey = CordMaterials.BuiltKey;
            // B24: machine hookups to masts / brackets / switches print in the look's cable (ConduitVisuals.PrintCable)
            if (Current.ProgramState == ProgramState.Playing && Find.Maps != null)
                foreach (Map map in Find.Maps) map.mapDrawer.WholeMapChanged((ulong)MapMeshFlagDefOf.Things);
        }

        // ------------------------------------------------------------------ poles follow the look (B6/B16)
        private static readonly Dictionary<ThingDef, GraphicData> originals = new Dictionary<ThingDef, GraphicData>();
        private static readonly Dictionary<ThingDef, string> origTops = new Dictionary<ThingDef, string>();
        private static readonly Dictionary<ThingDef, string> tops = new Dictionary<ThingDef, string>();

        /// <summary>Round 4 (owner 2026-10-04: "Light controls present on light mast, but no illumination present"): where each
        /// look's lamp-mast BULB is, (x, z) cells from the cell centre, read off its AerialLampMast.png (256x512 drawn 2x4,
        /// graphic top at z 3.5: z = 3.5 - row/128, x = (col - 128)/128). The lit head is drawn there while the glower glows,
        /// so the lamp reads as lit even at noon, when the glow grid's light is invisible outdoors (vanilla lamps alike).</summary>
        public static readonly Dictionary<string, Vector2> LampHead = new Dictionary<string, Vector2>
        {
            { "Scrapper", new Vector2(0.64f, 2.06f) }, { "Industrial", new Vector2(0.56f, 2.06f) },
            { "Modern", new Vector2(0.65f, 2.63f) }, { "Futuristic", new Vector2(0.60f, 2.53f) }
        };

        private static readonly Dictionary<int, Material> glowByColour = new Dictionary<int, Material>();

        /// <summary>The additive head glow in the glower's own colour (cached per colour; darklight stays blue).</summary>
        public static Material HeadGlow(Color c)
        {
            if (Glow == null) return null;
            int key = ((int)(c.r * 255) << 16) | ((int)(c.g * 255) << 8) | (int)(c.b * 255);
            if (!glowByColour.TryGetValue(key, out Material m))
                glowByColour[key] = m = MaterialPool.MatFrom(new MaterialRequest(Glow.mainTexture, ShaderDatabase.MoteGlow, c));
            return m;
        }

        public static string TopPathFor(ThingDef d) => d != null && tops.TryGetValue(d, out string p) ? p : null;

        /// <summary>Per-look pole geometry, measured from each look's own art when it lands (128x512 canvas drawn 1x4 cells,
        /// base at the bottom): insulator height (attachZ) and the centre of the cropped top overlay (topOffsetZ), both in
        /// cells above the cell centre. Key "Look/defName". Absent = the def's own values (the shared Scrapper art).</summary>
        public static readonly Dictionary<string, Vector2> PoleGeometry = PoleGeometryTable.Build();

        private static readonly Dictionary<ThingDef, Vector2> origGeom = new Dictionary<ThingDef, Vector2>();

        /// <summary>Insulator TIPS on each look's crossarm, measured from the look's own art (PoleGeometryTable, generated):
        /// (x across the arm, z height) in cells from the cell centre. Spans end exactly on these (B23).</summary>
        public static readonly Dictionary<string, Vector2[]> InsulatorTable = PoleGeometryTable.Insulators();
        private static readonly HashSet<ThingDef> realArt = new HashSet<ThingDef>();

        /// <summary>The anchor's insulator tips now, as offsets from its BasePoint: the look's measured crossarm when its
        /// own art is drawn; a wall bracket's measured insulator; else the def's attachZ with its insulatorSpread
        /// (-s/2, 0, +s/2), or one insulator at the centre.</summary>
        public static List<P2> InsulatorsFor(CompAerialAnchor a)
        {
            var r = new List<P2>();
            ThingDef d = a?.parent?.def;
            if (d == null) return r;
            if (BracketInsulator(a) is Vector2 bi) { r.Add(new P2(bi.x, bi.y)); return r; }
            if (realArt.Contains(d) && InsulatorTable.TryGetValue(Look + "/" + d.defName, out Vector2[] xs) && xs.Length > 0)
            {
                foreach (Vector2 v in xs) r.Add(new P2(v.x, v.y));
                return r;
            }
            float s = a.Ext?.insulatorSpread ?? 0f, z = a.Ext?.attachZ ?? 0f;
            if (s > 0.001f) { r.Add(new P2(-s / 2, z)); r.Add(new P2(0, z)); r.Add(new P2(s / 2, z)); }
            else r.Add(new P2(0, z));
            return r;
        }

        private static readonly string[] RotNames = { "North", "East", "South", "West" };
        public static readonly Dictionary<string, P2> BracketTable = BracketGeometryTable.Build();
        public static readonly Dictionary<string, double> BracketPlateEdge = BracketGeometryTable.PlateEdge();
        public static readonly Dictionary<string, double> BracketPlateDepth = BracketGeometryTable.PlateDepth();

        /// <summary>Round 2 (owner 2026-10-04): the look's per-facing bracket draw offset, plate on the wall's outer edge
        /// (AerialMath.BracketDrawOffset); null = no measured art (the def's own offsets stand).</summary>
        public static Vector3? BracketDrawOffset(string look, int rot)
        {
            if (!BracketPlateEdge.TryGetValue(look + "/" + RotNames[rot & 3], out double e)) return null;
            BracketPlateDepth.TryGetValue(look + "/" + RotNames[rot & 3], out double dp);
            P2 o = AerialMath.BracketDrawOffset(rot, e, dp);
            return new Vector3((float)o.X, 0f, (float)o.Z);
        }

        /// <summary>A wall bracket drawing its look's own per-facing art: where its insulator is, as an offset from the
        /// graphic centre (BracketGeometryTable, measured per Look/rotation). Null = the stand-in (the def's attachZ).</summary>
        public static Vector2? BracketInsulator(CompAerialAnchor a)
        {
            ThingDef d = a?.parent?.def;
            if (d == null || d != AerialDefOf.RM_AerialWallBracket || !realArt.Contains(d)) return null;
            return BracketTable.TryGetValue(Look + "/" + RotNames[a.parent.Rotation.AsInt & 3], out P2 v) ? new Vector2((float)v.X, (float)v.Z) : (Vector2?)null;
        }

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
                // the wall bracket's own art is one image per facing (Graphic_Multi: _north/_east/_south; west mirrors east)
                bool multi = d == AerialDefOf.RM_AerialWallBracket;
                bool real = multi ? Exists(own + "_north") && Exists(own + "_east") && Exists(own + "_south") : Exists(own);
                if (real) realArt.Add(d); else realArt.Remove(d);
                if (real)
                {
                    use.texPath = own; use.color = Color.white;
                    if (multi)
                    {
                        use.graphicClass = typeof(Graphic_Multi);
                        // round 2: per-look offsets so the plate sits on the wall's OUTER edge and the arm leans out
                        use.drawOffsetNorth = BracketDrawOffset(Look, 0) ?? orig.drawOffsetNorth;
                        use.drawOffsetEast = BracketDrawOffset(Look, 1) ?? orig.drawOffsetEast;
                        use.drawOffsetSouth = BracketDrawOffset(Look, 2) ?? orig.drawOffsetSouth;
                        use.drawOffsetWest = BracketDrawOffset(Look, 3) ?? orig.drawOffsetWest;
                    }
                }
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
