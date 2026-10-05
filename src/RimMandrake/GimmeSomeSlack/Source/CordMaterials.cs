using System.Collections.Generic;
using RimMandrake.GimmeSomeSlack.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>
    /// Cord art, per selectable style (owner, 2026-10-02: several art styles for players). Textures live under
    /// Textures/RimMandrake/GimmeSomeSlack/: the Jawa default set at the folder root (phase 1a names), every other
    /// family under Styles/&lt;Family&gt;/ with fixed slot names (Strand[_Variant], Junction_T, Junction_X, Plug,
    /// StubWall, StubRock, EndFrayed_Dead), wired by src/RimMandrake/Utils/mockups/messy_conduit/wire_style_art.py.
    /// A slot a family has no art for falls back to the Jawa root piece (listed in <see cref="Fallbacks"/>).
    ///
    /// Materials are rebuilt in place when the style or the extension-cord colour mode changes
    /// (<see cref="EnsureCurrent"/>, called by GimmeSomeSlackSettings.Apply before the map meshes regenerate), so a
    /// style change needs no restart. Strand strips tile along their length (wrap mode Repeat).
    /// A family with several strands (extension-cord colours, Star Wars cable kinds) picks one per power net,
    /// seeded per net (<see cref="VariantFor"/>).
    /// </summary>
    [StaticConstructorOnStartup]
    public static class CordMaterials
    {
        public const string Dir = "RimMandrake/GimmeSomeSlack/";
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

        private static Material[] strandV = new Material[0], faceV = new Material[0], lodV = new Material[0], plantV = new Material[0];
        /// <summary>Optional shader sway (B7 option 1): the face strand built on ShaderDatabase.CutoutPlant. MaterialPool
        /// registers every CutoutPlant material with WindManager (decompiled 1.6 MaterialPool.MatFrom), which then
        /// writes _SwayHead into it every tick while the map is current.</summary>
        public static Material StrandPlant;
        private static readonly HashSet<Material> plants = new HashSet<Material>();
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

        public static readonly string[] ExtCordColors = Aerial.ConduitStyles.Colours;
        public static readonly string[] StarWarsKinds = Aerial.ConduitStyles.IndustrialKinds;

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
            BuildAll();
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
            GimmeSomeSlackSettings.style + "/" + GimmeSomeSlackSettings.extCordColorMode + "/" + Mathf.Clamp(GimmeSomeSlackSettings.extCordColor, 0, ExtCordColors.Length - 1);

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
                    if (GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single)
                        return new[] { StyleDir + "ExtCord/Strand_" + ExtCordColors[Mathf.Clamp(GimmeSomeSlackSettings.extCordColor, 0, ExtCordColors.Length - 1)] };
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
            CordStyle style = GimmeSomeSlackSettings.style;
            Fallbacks.Clear();
            Missing.Clear();
            SlotPaths.Clear();
            // ---- strands (per-net variants)
            string[] paths = StrandPathsFor(style);
            var sv = new List<Material>(); var fv = new List<Material>(); var lv = new List<Material>(); var pv = new List<Material>(); var used = new List<string>();
            foreach (string p in paths)
            {
                Texture2D tex = Tex(p);
                if (tex == null) { Missing.Add(p); continue; }
                tex.wrapMode = TextureWrapMode.Repeat;
                sv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = StrandQueue }));
                fv.Add(MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = FaceQueue }));
                pv.Add(PlantMat(tex));
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
                    pv.Add(PlantMat(tex));
                    if (!lodCache.TryGetValue(tex, out Material lod)) { lod = new Material(sv[0]) { name = "RM_MessyCords_StrandLod_" + tex.name }; lodCache[tex] = lod; lods.Add(lod); }
                    lv.Add(lod);
                    used.Add(Dir + "Strand_Jawa");
                }
            }
            strandV = sv.ToArray(); faceV = fv.ToArray(); lodV = lv.ToArray(); plantV = pv.ToArray();
            StrandPlant = plantV.Length > 0 ? plantV[0] : null;
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
            d[DecalKind.PowerStripDark] = StripDarkMat(style, true);
            decals = d;
            // B14 (owner review 2026-10-04): in the extension-cord look every connection piece takes its net's cord colour.
            // The shipped pieces carry ORANGE cord stubs; Styles/ExtCord/<Colour>/<slot> are the recoloured copies
            // (recolor_extcord_pieces.py). Variant i matches strand variant i (one entry in the single-colour mode).
            variantDecals = new Dictionary<DecalKind, Material>[0];
            PieceColors.Clear();
            if (style == CordStyle.ExtensionCord)
            {
                var vd = new List<Dictionary<DecalKind, Material>>();
                foreach (string p in used)
                {
                    string colour = p.Substring(p.LastIndexOf('_') + 1);
                    var dv = new Dictionary<DecalKind, Material>(d);
                    if (colour != "Orange")
                        foreach (var kv in ColourSlots)
                        {
                            string vp = StyleDir + "ExtCord/" + colour + "/" + kv.Value;
                            Texture2D vt = Tex(vp);
                            if (vt == null) { Missing.Add(vp); continue; }
                            Color? tint = kv.Key == DecalKind.FrayDead ? new Color(0.62f, 0.58f, 0.55f, 1f) : (Color?)null;
                            int q = IsFace(kv.Key) ? FaceQueue : PieceQueue;
                            dv[kv.Key] = MaterialPool.MatFrom(new MaterialRequest(vt, ShaderDatabase.Transparent, tint ?? Color.white) { renderQueue = q });
                        }
                    PieceColors.Add(colour);
                    vd.Add(dv);
                }
                variantDecals = vd.ToArray();
            }
            BuiltKey = CurrentKey();
            Rebuilds++;
        }

        /// <summary>The dark (dead net) power strip: the look's own PowerStrip_Off art where it exists (Modern,
        /// Styles/ExtCord/PowerStrip_Off, art stage 2026-10-04), else a root PowerStrip_Dark, else the strip tinted down.</summary>
        private static Material StripDarkMat(CordStyle style, bool record)
        {
            Texture2D own = style == CordStyle.StarWarsJawa ? null : Tex(StyleDir + Family(style) + "/PowerStrip_Off");
            Texture2D stripDark = own ?? Tex(Dir + "PowerStrip_Dark");
            if (stripDark != null)
            {
                if (record) SlotPaths["PowerStripDark"] = own != null ? StyleDir + Family(style) + "/PowerStrip_Off" : Dir + "PowerStrip_Dark";
                return MaterialPool.MatFrom(new MaterialRequest(stripDark, ShaderDatabase.Transparent) { renderQueue = PieceQueue });
            }
            return SlotMat(style, "PowerStrip", PieceQueue, new Color(0.42f, 0.40f, 0.40f, 1f), "PowerStripDark", record);
        }

        // ------------------------------------------------------------------ stage 2: every look's materials, built once
        // (design 5 stage 2: "build the cord materials for all four styles once at start-up; the cord layer picks a piece's
        // material by (style, colour or kind) instead of by the global setting"). Flat index g = ConduitStyles.Global(look,
        // variant). Every Material comes from MaterialPool with the SAME request the default-look set above uses, so a legacy
        // piece drawn through g gets the very Material object it drew before stage 2 (StyleProbe "cstyles" checks it).
        private static Material[] gStrand = new Material[0], gFace = new Material[0], gLod = new Material[0], gPlant = new Material[0];
        private static Dictionary<DecalKind, Material>[] gDecals = new Dictionary<DecalKind, Material>[0];
        /// <summary>State read: the strand texture path of each flat index; every slot path that fell back or is missing.</summary>
        public static string[] GlobalStrandPaths = new string[0];
        public static readonly List<string> GlobalMissing = new List<string>();

        public static CordStyle StyleOfLook(string look)
        {
            switch (look)
            {
                case "Industrial": return CordStyle.StarWars;
                case "Modern": return CordStyle.ExtensionCord;
                case "Futuristic": return CordStyle.Cybertek;
                default: return CordStyle.StarWarsJawa;
            }
        }

        /// <summary>The strand path of (look, variant) whatever the colour setting.</summary>
        public static string StrandPathOf(string look, int variant)
        {
            switch (look)
            {
                case "Industrial": return StyleDir + "StarWars/Strand_" + StarWarsKinds[Mathf.Clamp(variant, 0, StarWarsKinds.Length - 1)];
                case "Modern": return StyleDir + "ExtCord/Strand_" + ExtCordColors[Mathf.Clamp(variant, 0, ExtCordColors.Length - 1)];
                case "Futuristic": return StyleDir + "Cybertek/Strand";
                default: return Dir + "Strand_Jawa";
            }
        }

        public static void BuildAll()
        {
            int n = Aerial.ConduitStyles.GlobalCount;
            gStrand = new Material[n]; gFace = new Material[n]; gLod = new Material[n]; gPlant = new Material[n];
            gDecals = new Dictionary<DecalKind, Material>[n];
            GlobalStrandPaths = new string[n];
            GlobalMissing.Clear();
            for (int g = 0; g < n; g++)
            {
                Aerial.ConduitStyles.FromGlobal(g, out string look, out int v);
                CordStyle style = StyleOfLook(look);
                string path = StrandPathOf(look, v);
                Texture2D tex = Tex(path);
                if (tex == null) { GlobalMissing.Add(path); path = Dir + "Strand_Jawa"; tex = Tex(path); }
                GlobalStrandPaths[g] = path;
                if (tex != null)
                {
                    tex.wrapMode = TextureWrapMode.Repeat;
                    gStrand[g] = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = StrandQueue });
                    gFace[g] = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = FaceQueue });
                    gPlant[g] = PlantMat(tex);
                    if (!lodCache.TryGetValue(tex, out Material lod))
                    {
                        lod = new Material(gStrand[g]) { name = "RM_MessyCords_StrandLod_" + tex.name };
                        lodCache[tex] = lod;
                        lods.Add(lod);
                    }
                    gLod[g] = lod;
                }
                var d = new Dictionary<DecalKind, Material>();
                d[DecalKind.Plug] = SlotMat(style, "Plug", PieceQueue, null, null, false);
                d[DecalKind.JunctionTape] = SlotMat(style, "Junction_T", PieceQueue, null, null, false);
                d[DecalKind.JunctionTin] = SlotMat(style, "Junction_X", PieceQueue, null, null, false);
                d[DecalKind.StubWall] = SlotMat(style, "StubWall", FaceQueue, null, null, false);
                d[DecalKind.StubRock] = SlotMat(style, "StubRock", FaceQueue, null, null, false);
                d[DecalKind.PowerStrip] = SlotMat(style, "PowerStrip", PieceQueue, null, null, false);
                d[DecalKind.FrayDead] = SlotMat(style, "EndFrayed_Dead", PieceQueue, new Color(0.62f, 0.58f, 0.55f, 1f), null, false);
                d[DecalKind.FrayLive] = SlotMat(style, "EndFrayed_Live", PieceQueue, null, null, false);
                d[DecalKind.PowerStripDark] = StripDarkMat(style, false);
                if (look == "Modern" && ExtCordColors[v] != "Orange")
                    foreach (var kv in ColourSlots)
                    {
                        string vp = StyleDir + "ExtCord/" + ExtCordColors[v] + "/" + kv.Value;
                        Texture2D vt = Tex(vp);
                        if (vt == null) { GlobalMissing.Add(vp); continue; }
                        Color? tint = kv.Key == DecalKind.FrayDead ? new Color(0.62f, 0.58f, 0.55f, 1f) : (Color?)null;
                        d[kv.Key] = MaterialPool.MatFrom(new MaterialRequest(vt, ShaderDatabase.Transparent, tint ?? Color.white) { renderQueue = IsFace(kv.Key) ? FaceQueue : PieceQueue });
                    }
                gDecals[g] = d;
            }
        }

        public static int GlobalCount => gStrand.Length;
        public static Material StrandG(int g) => g >= 0 && g < gStrand.Length ? gStrand[g] ?? Strand : Strand;
        public static Material StrandFaceG(int g) => g >= 0 && g < gFace.Length ? gFace[g] ?? StrandFace : StrandFace;
        public static Material StrandLodG(int g) => g >= 0 && g < gLod.Length ? gLod[g] ?? StrandLod : StrandLod;
        public static Material StrandPlantG(int g) => g >= 0 && g < gPlant.Length ? gPlant[g] ?? StrandPlant : StrandPlant;
        public static Material DecalG(DecalKind k, int g) =>
            g >= 0 && g < gDecals.Length && gDecals[g] != null && gDecals[g].TryGetValue(k, out Material m) ? m : Decal(k);

        /// <summary>The flat index a LEGACY piece draws with: the default look, its pre-stage-2 per-net variant.</summary>
        public static int LegacyGlobal(int netSeed)
        {
            string look = Aerial.AerialMaterials.LookOf(GimmeSomeSlackSettings.style);
            return Aerial.ConduitStyles.Global(look, Aerial.ConduitStyles.LegacyVariant(look, netSeed,
                GimmeSomeSlackSettings.extCordColorMode == ExtCordColorMode.Single, GimmeSomeSlackSettings.extCordColor));
        }

        private static Texture2D Tex(string path)
        {
            Texture2D t = ContentFinder<Texture2D>.Get(path, reportFailure: false);
            return t == null || t == BaseContent.BadTex ? null : t;
        }

        /// <summary>The family's piece, or the Jawa root piece when the family has none (recorded).</summary>
        private static Material SlotMat(CordStyle s, string slot, int queue, Color? color = null, string key = null, bool record = true)
        {
            string path = SlotPath(s, slot);
            Texture2D tex = Tex(path);
            if (tex == null && s != CordStyle.StarWarsJawa)
            {
                if (record) Fallbacks.Add(key ?? slot);
                path = SlotPath(CordStyle.StarWarsJawa, slot);
                tex = Tex(path);
            }
            if (record) SlotPaths[key ?? slot] = tex == null ? null : path;
            if (tex == null) { if (record) Missing.Add(path); else GlobalMissing.Add(path); return null; }
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

        private static Material PlantMat(Texture2D tex)
        {
            if (ShaderDatabase.CutoutPlant == null) return null;
            Material m = MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.CutoutPlant) { renderQueue = FaceQueue });
            if (m != null) plants.Add(m);
            return m;
        }

        public static bool IsPlant(Material m) => m != null && plants.Contains(m);
        public static Material StrandPlantFor(int v) => v >= 0 && v < plantV.Length ? plantV[v] : StrandPlant;

        public static int VariantCount => strandV.Length;

        /// <summary>The strand variant for a net seed: uniform over the extension-cord colours, weighted for the
        /// Star Wars kinds, always 0 for a single-strand family or the single-colour mode.</summary>
        public static int VariantFor(int netSeed)
        {
            int n = strandV.Length;
            if (n <= 1) return 0;
            // one rule, kept in the Verse-free ConduitStyles (stage 2 draws legacy pieces through it as well)
            return Mathf.Clamp(Aerial.ConduitStyles.LegacyVariant(Aerial.AerialMaterials.LookOf(GimmeSomeSlackSettings.style), netSeed, false, 0), 0, n - 1);
        }

        public static Material StrandFor(int v) => v >= 0 && v < strandV.Length ? strandV[v] : Strand;
        public static Material StrandFaceFor(int v) => v >= 0 && v < faceV.Length ? faceV[v] : StrandFace;
        public static Material StrandLodFor(int v) => v >= 0 && v < lodV.Length ? lodV[v] : StrandLod;

        public static bool IsLod(Material m) => m != null && lods.Contains(m);

        public static Material Decal(DecalKind k) => decals.TryGetValue(k, out Material m) ? m : null;

        private static Dictionary<DecalKind, Material>[] variantDecals = new Dictionary<DecalKind, Material>[0];
        /// <summary>State read: the cord colour each piece variant was built for (extension-cord look only).</summary>
        public static readonly List<string> PieceColors = new List<string>();
        /// <summary>The extension-cord pieces whose art carries a cord stub, and so must follow the cord colour (B14).</summary>
        public static readonly Dictionary<DecalKind, string> ColourSlots = new Dictionary<DecalKind, string>
        {
            { DecalKind.Plug, "Plug" }, { DecalKind.JunctionTape, "Junction_T" }, { DecalKind.JunctionTin, "Junction_X" },
            { DecalKind.StubWall, "StubWall" }, { DecalKind.StubRock, "StubRock" }, { DecalKind.FrayDead, "EndFrayed_Dead" }
        };

        /// <summary>A piece in its net's cord colour (falls back to the style's own piece).</summary>
        public static Material Decal(DecalKind k, int variant)
        {
            if (variant >= 0 && variant < variantDecals.Length && variantDecals[variant].TryGetValue(k, out Material m)) return m;
            return Decal(k);
        }

        /// <summary>The texture behind a piece variant (state read for the probe), or null.</summary>
        public static string DecalTexName(DecalKind k, int variant) => Decal(k, variant)?.mainTexture?.name;

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
