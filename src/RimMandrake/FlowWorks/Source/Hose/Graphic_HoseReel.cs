using UnityEngine;
using Verse;
using RimWorld;

namespace RimMandrake.FlowWorks.Hose
{
    /// <summary>
    /// The hose reel's graphic (owner review 2026-10-04 B26 / round 2): the stored art (texPath) while the hose is reeled in,
    /// the sibling "Reel_Deployed" art (empty drum, hose entering the reel) while it is laid. A SWAP, not an overlay: the two
    /// drawings do not share a pixel-exact outline (measured 2026-10-04: 10% of the stored silhouette falls outside the
    /// deployed one), so drawing one over the other leaves a rim of the stored coils showing. CompHoseReel dirties the map
    /// mesh when the hose is laid or reeled in. Missing deployed art = the stored art stands in. Carry stage S4: the drum shows
    /// deployed from the moment a colonist takes the end (Carrying / Retracting too); RM_MapComponent_Hoses reprints on that change.
    /// REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST (owner card 2026-10-22, "Player turns the reel"): the reel turns, and the picture
    /// with it (HoseReelRect.ArtPose): west as drawn, east mirrored. REEL_FACINGS_REDRAW_NORTH_SOUTH_OWED (owner card
    /// 2026-10-22, "install all 16"): north and south draw their own pictures, found beside each art as "<art>_north" /
    /// "<art>_south", unturned (the west-turned stand-in is gone; a missing one logs an error once and shows the west art).
    /// Graphic_Single's own rotation would turn the picture for every facing (west = 270 degrees), so Print and DrawWorker
    /// place the plane themselves.
    /// </summary>
    public class Graphic_HoseReel : Graphic_Single
    {
        private Material deployed;
        /// <summary>North / south pictures: [0] stored, [1] laid; index 0 = north, 1 = south. Null = missing (west shows).</summary>
        private readonly Material[,] facing = new Material[2, 2];
        /// <summary>State read: the laid-art path this graphic found beside its stored texPath (null when missing).</summary>
        public string DeployedPath;

        public override void Init(GraphicRequest req)
        {
            base.Init(req);
            int slash = req.path.LastIndexOf('/');
            string dir = slash >= 0 ? req.path.Substring(0, slash + 1) : "";
            string p = dir + "Reel_Deployed";
            Texture2D t = ContentFinder<Texture2D>.Get(p, reportFailure: false);
            if (t != null) DeployedPath = p;
            if (t != null)
                deployed = MaterialPool.MatFrom(new MaterialRequest(t, req.shader, color) { colorTwo = colorTwo, renderQueue = req.renderQueue });
            string[] suffix = { "_north", "_south" };
            for (int f = 0; f < 2; f++)
                for (int laid = 0; laid < 2; laid++)
                {
                    string fp = (laid == 0 ? req.path : p) + suffix[f];
                    Texture2D ft = ContentFinder<Texture2D>.Get(fp, reportFailure: false);
                    if (ft != null)
                        facing[laid, f] = MaterialPool.MatFrom(new MaterialRequest(ft, req.shader, color) { colorTwo = colorTwo, renderQueue = req.renderQueue });
                    else if (laid == 0 || deployed != null)
                        Log.ErrorOnce("[FlowWorks] hose reel art missing: " + fp + " (the west picture shows for that facing)", fp.GetHashCode());
                }
        }

        public bool HasDeployed => deployed != null;

        /// <summary>State read: true when this facing (Rot4 int) draws a picture of its own (west always; east = west mirrored).</summary>
        public bool HasFacingArt(int rot, bool laid)
        {
            int r = ((rot % 4) + 4) % 4;
            return r == 1 || r == 3 || facing[laid && deployed != null ? 1 : 0, r == 0 ? 0 : 1] != null;
        }

        public override Material MatAt(Rot4 rot, Thing thing = null)
        {
            bool laid = deployed != null && thing is ThingWithComps tw && tw.GetComp<CompHoseReel>() is CompHoseReel r && (r.laid || r.carry != HoseCarryState.Stored);
            if (rot == Rot4.North || rot == Rot4.South)
            {
                Material m = facing[laid ? 1 : 0, rot == Rot4.North ? 0 : 1];
                if (m != null) return m;
            }
            return laid ? deployed : mat;
        }

        public override Material MatSingleFor(Thing thing) => MatAt(Rot4.West, thing);

        public override Mesh MeshAt(Rot4 rot)
        {
            HoseReelRect.ArtPose(rot.AsInt, out _, out bool mirror);
            return mirror ? MeshPool.GridPlaneFlip(drawSize) : MeshPool.GridPlane(drawSize);
        }

        public override void DrawWorker(Vector3 loc, Rot4 rot, ThingDef thingDef, Thing thing, float extraRotation)
        {
            HoseReelRect.ArtPose(rot.AsInt, out float angle, out _);
            Quaternion quat = Quaternion.AngleAxis(angle + extraRotation, Vector3.up);
            loc += DrawOffset(rot);
            Graphics.DrawMesh(MeshAt(rot), loc, quat, MatAt(rot, thing), 0);
            ShadowGraphic?.DrawWorker(loc, rot, thingDef, thing, extraRotation);
        }

        public override void Print(SectionLayer layer, Thing thing, float extraRotation)
        {
            HoseReelRect.ArtPose(thing.Rotation.AsInt, out float angle, out bool mirror);
            Vector3 center = thing.TrueCenter() + DrawOffset(thing.Rotation);
            Material material = MatAt(thing.Rotation, thing);
            TryGetTextureAtlasReplacementInfo(material, thing.def.category.ToAtlasGroup(), mirror, vertexColors: true, out material, out Vector2[] uvs, out Color32 vc);
            Printer_Plane.PrintPlane(layer, center, drawSize, material, angle + extraRotation, mirror, uvs, new Color32[4] { vc, vc, vc, vc });
            ShadowGraphic?.Print(layer, thing, 0f);
        }

        public override Graphic GetColoredVersion(Shader newShader, Color newColor, Color newColorTwo) =>
            GraphicDatabase.Get<Graphic_HoseReel>(path, newShader, drawSize, newColor, newColorTwo, data);
    }
}
