using System.Collections.Generic;
using RimMandrake.MessyConduit.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit
{
    /// <summary>Phase-1a placeholder art (Textures/RimMandrake/MessyConduit/, exported by
    /// src/RimMandrake/Utils/mockups/messy_conduit/export_textures.py). Strand strips tile along
    /// their length, so their wrap mode is forced to Repeat.</summary>
    [StaticConstructorOnStartup]
    public static class CordMaterials
    {
        private const string Dir = "RimMandrake/MessyConduit/";
        public static readonly Material Strand;
        public static readonly Material Shadow;
        /// <summary>A strand hanging over a wall face (wall terminal tail): drawn after the wall.</summary>
        public static readonly Material StrandFace;
        public static readonly Material SparkGlow;
        /// <summary>Additive glow pulsed at a LIVE end every frame (also while paused).</summary>
        public static readonly Material LiveGlow;
        private static readonly Dictionary<DecalKind, Material> decals = new Dictionary<DecalKind, Material>();
        public static readonly Material DecalFrayLive;
        /// <summary>Phase 1b: the far-zoom (LOD) strand, a separate Material instance so it lands in its own
        /// sub-mesh; the selection highlight (strand texture, warm, translucent, drawn over the cords).</summary>
        public static readonly Material StrandLod, Highlight;

        /// <summary>Render queues. Every SectionLayer submesh gets the SAME bounds
        /// (MapDrawLayer.RefreshSubMeshBounds, decompiled 1.6), so transparent submeshes tie on sort
        /// distance and their altitude alone does not order them: an explicit queue does. Shadow under
        /// strand, end pieces over strand, face pieces (wall/rock stubs, hanging tails) last.</summary>
        public static int StrandQueue, ShadowQueue, PieceQueue, FaceQueue;

        static CordMaterials()
        {
            Strand = Tiled(Dir + "Strand_Jawa", 0);
            StrandQueue = Strand != null ? Strand.renderQueue : 3000;
            ShadowQueue = StrandQueue - 1;
            PieceQueue = StrandQueue + 1;
            FaceQueue = StrandQueue + 2;
            Shadow = Tiled(Dir + "StrandShadow", ShadowQueue);
            StrandFace = Tiled(Dir + "Strand_Jawa", FaceQueue);
            SparkGlow = Mat(Dir + "SparkGlow", PieceQueue);
            Texture2D glow = ContentFinder<Texture2D>.Get(Dir + "SparkGlow", reportFailure: false);
            if (glow != null) LiveGlow = MaterialPool.MatFrom(new MaterialRequest(glow, ShaderDatabase.MoteGlow));
            decals[DecalKind.Plug] = Mat(Dir + "Plug", PieceQueue);
            decals[DecalKind.JunctionTape] = Mat(Dir + "Junction_Tape", PieceQueue);
            decals[DecalKind.JunctionTin] = Mat(Dir + "Junction_Tin", PieceQueue);
            decals[DecalKind.StubWall] = Mat(Dir + "StubWall", FaceQueue);
            decals[DecalKind.StubRock] = Mat(Dir + "StubRock", FaceQueue);
            decals[DecalKind.PowerStrip] = Mat(Dir + "PowerStrip", PieceQueue);
            // a dead end's fray is dulled further so it reads cold beside the live one
            decals[DecalKind.FrayDead] = Mat(Dir + "EndFrayed_Dead", PieceQueue, new Color(0.62f, 0.58f, 0.55f, 1f));
            decals[DecalKind.FrayLive] = Mat(Dir + "EndFrayed_Live", PieceQueue);
            // phase 1b B6: LEDs dark when the net is dead. Until PowerStrip_Lit/_Dark art lands (artpipe), the
            // dark strip is the placeholder strip tinted down.
            Texture2D stripDark = ContentFinder<Texture2D>.Get(Dir + "PowerStrip_Dark", reportFailure: false);
            decals[DecalKind.PowerStripDark] = stripDark != null
                ? MaterialPool.MatFrom(new MaterialRequest(stripDark, ShaderDatabase.Transparent) { renderQueue = PieceQueue })
                : Mat(Dir + "PowerStrip", PieceQueue, new Color(0.42f, 0.40f, 0.40f, 1f));
            if (Strand != null)
            {
                StrandLod = new Material(Strand) { name = "RM_MessyCords_StrandLod" };
                // a WHITE band tinted warm: tinting the near-black strand texture stayed near-black (live 1b-2 look)
                Highlight = MaterialPool.MatFrom(new MaterialRequest(BaseContent.WhiteTex, ShaderDatabase.Transparent, new Color(1f, 0.85f, 0.35f, 0.42f)) { renderQueue = FaceQueue + 1 });
            }
        }

        public static bool IsLod(Material m) => m != null && m == StrandLod;

        public static Material Decal(DecalKind k) => decals.TryGetValue(k, out Material m) ? m : null;

        public static bool IsFace(DecalKind k) => k == DecalKind.StubWall || k == DecalKind.StubRock;

        private static Material Mat(string path, int queue, Color? color = null)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, reportFailure: true);
            if (tex == null) return null;
            var req = new MaterialRequest(tex, ShaderDatabase.Transparent, color ?? Color.white) { renderQueue = queue };
            return MaterialPool.MatFrom(req);
        }

        private static Material Tiled(string path, int queue)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, reportFailure: true);
            if (tex == null) return null;
            tex.wrapMode = TextureWrapMode.Repeat;
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent) { renderQueue = queue });
        }

        /// <summary>Phase 1a ships the Jawa (Star Wars family) set only; the other families are
        /// listed in the settings but not selectable until their strips exist.</summary>
        public static bool StyleInstalled(CordStyle s) => s == CordStyle.StarWarsJawa && Strand != null;
    }
}
