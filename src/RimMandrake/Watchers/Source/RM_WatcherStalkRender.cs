using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.Watchers
{
    // The Rust Cathedral Watcher's render tree (RM_WatcherStalkTree; pitch §5.2/§5.6). Every mechanism here is the engine's own:
    //   - the stalk and head are ordinary PawnRenderNodes tagged RM_WatcherStalk / RM_WatcherHead, moved and scaled by vanilla keyframe
    //     AnimationDefs (AnimationWorker_Keyframes, keyed by node tag) played with PawnRenderer.SetAnimation;
    //   - the head's direction is a per-draw worker choice, the PawnRenderNodeWorker_TurretGun pattern (Centurion, Warqueen, Diabolus turn
    //     one part of a moving pawn from a comp angle), except the angle picks one of eight pictures instead of spinning one sprite.
    // RimSage 1.6 reads behind each override: PawnRenderTree.TryGetMatrix (transforms are recomputed every frame) and ParallelPreDraw
    // (draw requests, so CanDrawNow and the material, are cached until SetDirty; the comp dirties on every phase or octant change).

    /// <summary>A part drawn from one plain texture (Graphic_Single), with a fixed foot pivot so the stalk grows up out of the seam
    /// whether an animation is playing or not.</summary>
    public class RM_PawnRenderNodeProperties_WatcherPart : PawnRenderNodeProperties
    {
        /// <summary>Scale/rotation pivot in the part's own unit square: (0.5, 0) = the middle of its bottom edge.</summary>
        public Vector2 footPivot = new Vector2(0.5f, 0f);

        /// <summary>Head only. The five drawn look directions, in order N, NE, E, SE, S (the west side mirrors). Empty = the
        /// placeholder mode: texPath is a top-down lens and is turned in 45-degree steps (TurretTop's art rotation applies).</summary>
        public List<string> octantTexPaths;

        /// <summary>Placeholder mode only: the texture's own facing, as TurretTop.ArtworkRotation (-90 for vanilla turret tops).</summary>
        public float artworkRotation = -90f;
    }

    public class RM_PawnRenderNode_WatcherPart : PawnRenderNode
    {
        private Graphic[] octantGraphics;

        public RM_PawnRenderNode_WatcherPart(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree) : base(pawn, props, tree)
        {
        }

        public RM_PawnRenderNodeProperties_WatcherPart PartProps => (RM_PawnRenderNodeProperties_WatcherPart)props;

        public bool HasOctants => PartProps.octantTexPaths != null && PartProps.octantTexPaths.Count == 5;

        public override Graphic GraphicFor(Pawn pawn)
        {
            if (props.texPath.NullOrEmpty())
            {
                return null;
            }
            return GraphicDatabase.Get<Graphic_Single>(props.texPath, ShaderFor(pawn), Vector2.one, ColorFor(pawn));
        }

        public Graphic OctantGraphic(int picture)
        {
            if (!HasOctants)
            {
                return null;
            }
            if (octantGraphics == null)
            {
                octantGraphics = new Graphic[5];
                for (int i = 0; i < 5; i++)
                {
                    octantGraphics[i] = GraphicDatabase.Get<Graphic_Single>(PartProps.octantTexPaths[i], ShaderFor(tree.pawn), Vector2.one,
                        ColorFor(tree.pawn));
                }
            }
            return octantGraphics[picture];
        }
    }

    /// <summary>The stalk: drawn only while it is up or moving (RM_WatcherStalkKernel.StalkDrawn), never on a dead pawn.</summary>
    public class RM_PawnRenderNodeWorker_WatcherStalk : PawnRenderNodeWorker
    {
        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
        {
            if (!base.CanDrawNow(node, parms))
            {
                return false;
            }
            RM_CompWatcherStalk stalk = parms.pawn?.GetComp<RM_CompWatcherStalk>();
            return stalk != null && RM_WatcherStalkKernel.StalkDrawn(stalk.phase, node.tree.currentAnimation != null, parms.pawn.Dead);
        }

        protected override Vector3 PivotFor(PawnRenderNode node, PawnDrawParms parms)
        {
            // AnimationPart.pivot and DrawData pivot use opposite signs in vanilla (PawnRenderNodeWorker.PivotFor); one fixed pivot here keeps
            // the static pose and the animated one identical: the foot stays on the seam.
            Vector2 p = node.Props is RM_PawnRenderNodeProperties_WatcherPart wp ? wp.footPivot : new Vector2(0.5f, 0f);
            return new Vector3(p.x - 0.5f, 0f, p.y - 0.5f);
        }
    }

    /// <summary>The camera head: rides the stalk top (its animation moves it with the stalk), and shows one of eight look directions.</summary>
    public class RM_PawnRenderNodeWorker_WatcherHead : RM_PawnRenderNodeWorker_WatcherStalk
    {
        protected override Vector3 PivotFor(PawnRenderNode node, PawnDrawParms parms)
        {
            return Vector3.zero; // the head turns about its own centre
        }

        public override void AppendDrawRequests(PawnRenderNode node, PawnDrawParms parms, List<PawnGraphicDrawRequest> requests)
        {
            var part = node as RM_PawnRenderNode_WatcherPart;
            RM_CompWatcherStalk stalk = parms.pawn?.GetComp<RM_CompWatcherStalk>();
            if (part == null || stalk == null || !part.HasOctants)
            {
                base.AppendDrawRequests(node, parms, requests);
                return;
            }
            int picture = RM_WatcherStalkKernel.PictureFor(stalk.Octant, out bool mirrored);
            Graphic g = part.OctantGraphic(picture);
            Material mat = g?.MatSingle;
            if (mat == null)
            {
                return;
            }
            // A west-facing mesh from a plane set is the flipped one (GraphicMeshSet(width, height): meshes[3] flipped).
            Mesh mesh = MeshPool.GetMeshSetForSize(1f, 1f).MeshAt(mirrored ? Rot4.West : Rot4.East);
            requests.Add(new PawnGraphicDrawRequest(node, mesh, mat));
        }

        public override Quaternion RotationFor(PawnRenderNode node, PawnDrawParms parms)
        {
            Quaternion q = base.RotationFor(node, parms);
            var part = node as RM_PawnRenderNode_WatcherPart;
            RM_CompWatcherStalk stalk = parms.pawn?.GetComp<RM_CompWatcherStalk>();
            if (part == null || stalk == null || part.HasOctants)
            {
                return q;
            }
            // Placeholder mode: a top-down lens turned to the octant's centre, in 45-degree steps (still eight-step, never free-spinning).
            float a = RM_WatcherStalkKernel.OctantAngle(stalk.Octant) + part.PartProps.artworkRotation;
            return q * Quaternion.AngleAxis(a, Vector3.up);
        }
    }

    /// <summary>The seam hatch / crawler base. Vanilla's animal body worker drops the stationary picture while ANY animation plays
    /// (PawnRenderNodeWorker_AnimalBody), which would swap the hatch for the crawler every time the stalk rises; this keeps the hatch
    /// whenever the pawn is not walking. Dead: the life stage's corpse picture, the collapsed husk (PawnRenderNode_AnimalPart.GraphicFor).</summary>
    public class RM_PawnRenderNodeWorker_WatcherBase : PawnRenderNodeWorker_AnimalBody
    {
        protected override GraphicStateDef GetGraphicState(PawnRenderNode node, PawnDrawParms parms)
        {
            Pawn pawn = parms.pawn;
            if (pawn != null && !pawn.Dead && pawn.Spawned && !pawn.pather.Moving && pawn.ageTracker.CurKindLifeStage.stationaryGraphicData != null)
            {
                return RimWorld.GraphicStateDefOf.Stationary;
            }
            return base.GetGraphicState(node, parms);
        }
    }
}
