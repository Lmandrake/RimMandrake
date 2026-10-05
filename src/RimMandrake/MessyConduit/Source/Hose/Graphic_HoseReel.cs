using UnityEngine;
using Verse;

namespace RimMandrake.MessyConduit.Hose
{
    /// <summary>
    /// The hose reel's graphic (owner review 2026-10-04 B26 / round 2): the stored art (texPath) while the hose is reeled in,
    /// the sibling "Reel_Deployed" art (empty drum, hose entering the reel) while it is laid. A SWAP, not an overlay: the two
    /// drawings do not share a pixel-exact outline (measured 2026-10-04: 10% of the stored silhouette falls outside the
    /// deployed one), so drawing one over the other leaves a rim of the stored coils showing. CompHoseReel dirties the map
    /// mesh when the hose is laid or reeled in. Missing deployed art = the stored art stands in. Carry stage S4: the drum shows
    /// deployed from the moment a colonist takes the end (Carrying / Retracting too); RM_MapComponent_Hoses reprints on that change.
    /// </summary>
    public class Graphic_HoseReel : Graphic_Single
    {
        private Material deployed;
        /// <summary>State read: the laid-art path this graphic found beside its stored texPath (null when missing).</summary>
        public string DeployedPath;

        public override void Init(GraphicRequest req)
        {
            base.Init(req);
            int slash = req.path.LastIndexOf('/');
            string p = (slash >= 0 ? req.path.Substring(0, slash + 1) : "") + "Reel_Deployed";
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: false);
            if (t != null) DeployedPath = p;
            if (t != null)
                deployed = MaterialPool.MatFrom(new MaterialRequest(t, req.shader, color) { colorTwo = colorTwo, renderQueue = req.renderQueue });
        }

        public bool HasDeployed => deployed != null;

        public override Material MatAt(Rot4 rot, Thing thing = null) =>
            deployed != null && thing is ThingWithComps tw && tw.GetComp<CompHoseReel>() is CompHoseReel r && (r.laid || r.carry != HoseCarryState.Stored) ? deployed : mat;

        public override Material MatSingleFor(Thing thing) => MatAt(Rot4.North, thing);

        public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo) =>
            GraphicDatabase.Get<Graphic_HoseReel>(path, newShader, drawSize, newColor, newColorTwo, data);
    }
}
