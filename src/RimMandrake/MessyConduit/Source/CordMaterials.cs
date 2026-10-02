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
        public static readonly Material SparkGlow;
        private static readonly Dictionary<DecalKind, Material> decals = new Dictionary<DecalKind, Material>();
        public static readonly Material DecalFrayLive;

        static CordMaterials()
        {
            Strand = Tiled(Dir + "Strand_Jawa");
            Shadow = Tiled(Dir + "StrandShadow");
            SparkGlow = Mat(Dir + "SparkGlow");
            decals[DecalKind.Plug] = Mat(Dir + "Plug");
            decals[DecalKind.JunctionTape] = Mat(Dir + "Junction_Tape");
            decals[DecalKind.JunctionTin] = Mat(Dir + "Junction_Tin");
            decals[DecalKind.StubWall] = Mat(Dir + "StubWall");
            decals[DecalKind.StubRock] = Mat(Dir + "StubRock");
            decals[DecalKind.PowerStrip] = Mat(Dir + "PowerStrip");
            decals[DecalKind.FrayDead] = Mat(Dir + "EndFrayed_Dead");
            decals[DecalKind.FrayLive] = Mat(Dir + "EndFrayed_Live");
        }

        public static Material Decal(DecalKind k) => decals.TryGetValue(k, out Material m) ? m : null;

        private static Material Mat(string path)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, reportFailure: true);
            return tex == null ? null : MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent));
        }

        private static Material Tiled(string path)
        {
            Texture2D tex = ContentFinder<Texture2D>.Get(path, reportFailure: true);
            if (tex == null) return null;
            tex.wrapMode = TextureWrapMode.Repeat;
            return MaterialPool.MatFrom(new MaterialRequest(tex, ShaderDatabase.Transparent));
        }

        /// <summary>Phase 1a ships the Jawa (Star Wars family) set only; the other families are
        /// listed in the settings but not selectable until their strips exist.</summary>
        public static bool StyleInstalled(CordStyle s) => s == CordStyle.StarWarsJawa && Strand != null;
    }
}
