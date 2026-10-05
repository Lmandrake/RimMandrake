using System.Collections.Generic;
using HarmonyLib;
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
    /// Per-build style (design messyconduit_style_per_build_design.md, stage 1): each anchor carries its own look in the
    /// engine's style field (StylePicker); its pole art is that style def's graphic, and its geometry, top overlay, lamp
    /// head and cable are looked up by ITS look here. A span draws in its poles' look (the older pole's when they differ,
    /// ConduitStyles.SpanLook); a span reads the look's own SpanWire (Aerial/Styles/&lt;Look&gt;/SpanWire) and falls back
    /// to the cable named in <see cref="SpanFallback"/>. Fallen cords and the hanging drop of a cut wire use the
    /// anchor's span cable, never the floor cord (B11). The globals Look/Span/SpanWidth are the DEFAULT look's (the
    /// `style` Mod Setting): legacy unstyled anchors and the switch hookup cable. Rebuilt on a settings change.
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
        public static float SpanWidth = 0.10f;

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
                case "Industrial": return 0.10f;   // round 5 (owner: "Make the industrial black cables for the poles narrower: they are extremely thick right now"): 0.17 -> 0.10
                case "Scrapper": return 0.14f;
                default: return 0.095f;
            }
        }

        public static void Build()
        {
            CordMaterials.EnsureCurrent();
            byLook.Clear();
            topMats.Clear();
            // the DEFAULT look's set stays in the old globals: hookup cables to switches (ConduitVisuals, stage 2 styles them)
            // and the probes' "look"/"spanPath" fields read it
            LookMats def = For(LookOf(MessyConduitSettings.style));
            Look = def.Look;
            SpanWidth = def.Width;
            SpanPath = def.SpanPath;
            Span = def.Span;
            Fallen = Span;
            Shadow = Tiled(AerialDir + "SpanShadow", new Color(1f, 1f, 1f, 0.32f)) ?? Tiled(Dir + "StrandShadow", new Color(1f, 1f, 1f, 0.45f));
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", false);
            Glow = glow != null ? MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow)) : null;
            FrayLive = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayLive) ?? Plain(Dir + "EndFrayed_Live", Color.white);
            FrayDead = CordMaterials.Decal(RimMandrake.MessyConduit.Core.DecalKind.FrayDead) ?? Plain(Dir + "EndFrayed_Dead", new Color(0.62f, 0.58f, 0.55f, 1f));
            RecordPoleTex();
            BuiltKey = CordMaterials.BuiltKey;
            if (Current.ProgramState == ProgramState.Playing && Find.Maps != null)
                foreach (Map map in Find.Maps)
                {
                    // a default-look change redraws every UNSTYLED (legacy) anchor in the new default: its Thing.Graphic is
                    // cached per thing (styleGraphicInt), so drop that cache; styled anchors keep their own look
                    foreach (Thing t in map.listerThings.AllThings)
                        if (StyleIndex.Is(t.def) && StylePicker.RawStyle(t) == null) styleGraphic(t) = null;
                    // B24: machine hookups to masts / brackets / switches print in the look's cable (ConduitVisuals.PrintCable)
                    map.mapDrawer.WholeMapChanged((ulong)MapMeshFlagDefOf.Things);
                }
        }

        private static readonly AccessTools.FieldRef<Thing, Graphic> styleGraphic = AccessTools.FieldRefAccess<Thing, Graphic>("styleGraphicInt");

        /// <summary>One look's overhead cable: its own SpanWire (Aerial/Styles/&lt;Look&gt;/SpanWire) else the fallback cable,
        /// at the look's width. Built once per look per settings key (cleared by Build).</summary>
        public sealed class LookMats
        {
            public string Look, SpanPath;
            public Material Span;
            public float Width;
        }

        private static readonly Dictionary<string, LookMats> byLook = new Dictionary<string, LookMats>();

        public static LookMats For(string look)
        {
            if (!AerialStyles.IsLook(look)) look = "Scrapper";
            if (byLook.TryGetValue(look, out LookMats m)) return m;
            m = new LookMats { Look = look, Width = WidthOf(look) };
            string own = AerialStyleDir + look + "/SpanWire";
            m.SpanPath = Exists(own) ? own : SpanFallback(look);
            m.Span = Tiled(m.SpanPath, null, true) ?? Tiled(Dir + "Strand_Jawa", null, true);
            byLook[look] = m;
            return m;
        }

        /// <summary>The look an anchor is drawn in (its own style; an unstyled legacy anchor draws the default look).</summary>
        public static string LookOf(CompAerialAnchor a) => a?.parent == null ? Look : StylePicker.LookOfThing(a.parent);

        /// <summary>The look a span between two anchors draws in. The run rule keeps a run in one look, so both ends nearly
        /// always agree; when they do not (the moment between a new link and its run check) the larger run wins, a tie goes
        /// to the older (ConduitStyles.SpanLook, owner 2026-10-04). Each side is measured without this span.</summary>
        public static string SpanLookOf(CompAerialAnchor a, CompAerialAnchor b)
        {
            string la = LookOf(a), lb = LookOf(b);
            if (la == lb) return la;
            RM_MapComponent_ConduitRuns runs = a.Map?.GetComponent<RM_MapComponent_ConduitRuns>();
            if (runs == null) return ConduitStyles.SpanLook(la, 0, a.thingIDNumber, lb, 0, b.thingIDNumber, StylePicker.DefaultLook);
            ConduitStyles.Run ra = RM_MapComponent_ConduitRuns.Info(runs.RunOf(a.parent, null, a.parent, b.parent));
            ConduitStyles.Run rb = RM_MapComponent_ConduitRuns.Info(runs.RunOf(b.parent, null, a.parent, b.parent));
            return ConduitStyles.SpanLook(la, ra.Area, ra.Oldest, lb, rb.Area, rb.Oldest, StylePicker.DefaultLook);
        }

        public static LookMats SpanMats(CompAerialAnchor a, CompAerialAnchor b) => For(SpanLookOf(a, b));

        // ------------------------------------------------------------------ poles: geometry by (look, building)
        // Stage 1 of the per-build style design: no shared ThingDef is edited any more. Each anchor draws its own style's
        // graphic (the engine's Thing.Graphic), and every number below is looked up by the ANCHOR's look.

        /// <summary>State read: the texture each anchor def draws in the DEFAULT look (unstyled/legacy anchors), from the
        /// style defs. Per-anchor textures: AerialProbe "styles".</summary>
        public static readonly Dictionary<string, string> PoleTex = new Dictionary<string, string>();
        /// <summary>Kept for the probes: every look has its own pole art now, so no tinted stand-ins (always empty).</summary>
        public static readonly List<string> PoleStandIns = new List<string>();

        private static void RecordPoleTex()
        {
            PoleTex.Clear();
            foreach (string dn in AerialStyles.StyledDefs)
            {
                ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(dn);
                ThingStyleDef st = StylePicker.StyleFor(d, Look);
                PoleTex[dn] = st?.graphicData?.texPath ?? d?.graphicData?.texPath;
            }
        }


        /// <summary>Per-look pole geometry, measured from each look's own art (PoleGeometryTable, generated): insulator height
        /// (attachZ) and the centre of the cropped top overlay (topOffsetZ), cells above the cell centre. Key "Look/defName".</summary>
        public static readonly Dictionary<string, Vector2> PoleGeometry = PoleGeometryTable.Build();

        /// <summary>Insulator TIPS on each look's crossarm, measured from the look's own art (PoleGeometryTable, generated):
        /// (x across the arm, z height) in cells from the cell centre. Spans end exactly on these (B23).</summary>
        public static readonly Dictionary<string, Vector2[]> InsulatorTable = PoleGeometryTable.Insulators();

        /// <summary>The anchor's insulator height in its look (the def's attachZ when the look has no measured row).</summary>
        public static float AttachZ(CompAerialAnchor a) =>
            AerialStyles.TryLookup(PoleGeometry, LookOf(a), a.def.defName, out Vector2 g) ? g.x : a.Ext.attachZ;

        /// <summary>The centre of the anchor's top overlay in its look.</summary>
        public static float TopOffsetZ(CompAerialAnchor a) =>
            AerialStyles.TryLookup(PoleGeometry, LookOf(a), a.def.defName, out Vector2 g) ? g.y : a.Ext.topOffsetZ;

        /// <summary>The mast head drawn above pawns, in the anchor's look (Aerial/Styles/&lt;Look&gt;/&lt;top base name&gt;), else
        /// the def's shared top.</summary>
        public static string TopPathFor(CompAerialAnchor a)
        {
            string ot = a?.Ext?.topTexPath;
            if (ot.NullOrEmpty()) return null;
            string own = AerialStyleDir + LookOf(a) + "/" + ot.Substring(ot.LastIndexOf('/') + 1);
            return Exists(own) ? own : ot;
        }

        /// <summary>The anchor's insulator tips now, as offsets from its BasePoint: a wall bracket's measured insulator; the
        /// look's measured crossarm; else the def's attachZ with its insulatorSpread (-s/2, 0, +s/2), or one insulator.</summary>
        public static List<P2> InsulatorsFor(CompAerialAnchor a)
        {
            var r = new List<P2>();
            ThingDef d = a?.parent?.def;
            if (d == null) return r;
            if (BracketInsulator(a) is Vector2 bi) { r.Add(new P2(bi.x, bi.y)); return r; }
            if (AerialStyles.TryLookup(InsulatorTable, LookOf(a), d.defName, out Vector2[] xs) && xs.Length > 0)
            {
                foreach (Vector2 v in xs) r.Add(new P2(v.x, v.y));
                return r;
            }
            float s = a.Ext?.insulatorSpread ?? 0f, z = AttachZ(a);
            if (s > 0.001f) { r.Add(new P2(-s / 2, z)); r.Add(new P2(0, z)); r.Add(new P2(s / 2, z)); }
            else r.Add(new P2(0, z));
            return r;
        }

        private static readonly string[] RotNames = { "North", "East", "South", "West" };
        public static readonly Dictionary<string, P2> BracketTable = BracketGeometryTable.Build();
        public static readonly Dictionary<string, double> BracketPlateEdge = BracketGeometryTable.PlateEdge();
        public static readonly Dictionary<string, double> BracketPlateDepth = BracketGeometryTable.PlateDepth();

        /// <summary>Round 2 (owner 2026-10-04): the look's per-facing bracket draw offset, plate on the wall's outer edge
        /// (AerialMath.BracketDrawOffset); null = no measured art. Written into the bracket style defs at startup
        /// (StylePicker.InjectBracketOffsets).</summary>
        public static Vector3? BracketDrawOffset(string look, int rot)
        {
            if (!BracketPlateEdge.TryGetValue(look + "/" + RotNames[rot & 3], out double e)) return null;
            BracketPlateDepth.TryGetValue(look + "/" + RotNames[rot & 3], out double dp);
            P2 o = AerialMath.BracketDrawOffset(rot, e, dp);
            return new Vector3((float)o.X, 0f, (float)o.Z);
        }

        /// <summary>A wall bracket: where its insulator is in its look, as an offset from the graphic centre
        /// (BracketGeometryTable, measured per Look/rotation). Null = not a bracket, or no measured row (def attachZ).</summary>
        public static Vector2? BracketInsulator(CompAerialAnchor a)
        {
            ThingDef d = a?.parent?.def;
            if (d == null || d != AerialDefOf.RM_AerialWallBracket) return null;
            return AerialStyles.TryLookup(BracketTable, LookOf(a), RotNames[a.parent.Rotation.AsInt & 3], out P2 v) ? new Vector2((float)v.X, (float)v.Z) : (Vector2?)null;
        }

        private static bool Exists(string path)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(path, false);
            return t != null && t != BaseContent.BadTex;
        }

        /// <summary>Round 6: the render queue of everything drawn OVERHEAD (span cable, mast heads) -- above hoses, cords and
        /// the tap clamp, so a hose lying under a wire is never painted over it (Core.DrawOrder).</summary>
        public static int OverheadQueue => RimMandrake.MessyConduit.Core.DrawOrder.OverheadQueue(CordMaterials.StrandQueue);

        private static Material Tiled(string path, Color? c = null, bool overhead = false)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, false);
            if (tex == null) return null;
            tex.wrapMode = TextureWrapMode.Repeat;
            var req = new MaterialRequest(tex, ShaderDatabase.Transparent, c ?? Color.white);
            if (overhead) req.renderQueue = OverheadQueue;
            return MaterialPool.MatFrom(req);
        }

        private static Material Plain(string path, Color c)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, true);
            return tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, c));
        }

        private static readonly Dictionary<string, Material> topMats = new Dictionary<string, Material>();

        /// <summary>The mast head drawn above pawns (TopPathFor picks the anchor's look).</summary>
        public static Material Top(string texPath)
        {
            if (texPath.NullOrEmpty()) return null;
            Color c = Color.white;
            string key = texPath;
            if (topMats.TryGetValue(key, out Material m)) return m;
            Texture2D tex = ContentFinder<Texture2D>.Get(texPath, true);
            m = tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent, c) { renderQueue = OverheadQueue });
            topMats[key] = m;
            return m;
        }
    }
}
