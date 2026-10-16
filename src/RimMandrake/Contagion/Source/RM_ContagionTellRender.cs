using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Contagion
{
    // CONTAGION_MECHANICS_BUILD_1 — the VISIBLE Burn tells (owner Q6, 2026-10-15, by card: "Build the visible Burn tell
    // motion -> Build the visible sink and shake"). Before this, the tells were a behaviour (gawpsacks stop) and puffs;
    // the "render seam" the item listed is closed with the engine's own extension points, no Harmony:
    //   - the gawpsack SINKS: its race uses RM_GawpsackSink, Core's Animal render tree with the body node's worker swapped
    //     for PawnRenderNodeWorker_RM_TellSink, which lowers and squashes the body by the sky clock (transforms are
    //     recomputed every frame, PawnRenderTree.TryGetMatrix);
    //   - the rattlegrope SHAKES: its thingClass RM_Plant_Rattlegrope leaves the static map mesh while shaking and draws
    //     itself each frame with a sideways rattle (drawerType MapMeshAndRealTime); RM_MapComponent_ContagionSky dirties
    //     the rattlers' mesh sections when shaking starts and stops.
    // The arithmetic is Kernel/RM_TellRenderKernel.cs. Both are gated by the "Burn tells" setting.
    public static class RM_ContagionTellRender
    {
        public const int RampTicks = 250;

        public static float SinkFraction(Map map)
        {
            if (map == null) return 0f;
            RM_ContagionSkyExtension ext = RM_ContagionSky.ExtFor(map);
            if (ext == null) return 0f;
            RM_MapComponent_ContagionSky sky = map.GetComponent<RM_MapComponent_ContagionSky>();
            if (sky == null) return 0f;
            return RM_TellRenderKernel.SinkFraction(RM_ContagionSettings.burnTellsEnabled, sky.TellsBegun, Find.TickManager.TicksGame,
                sky.NextBurnTick, ext.tellLeadTicks, sky.BurnActive, sky.LastBurnEndTick, RampTicks);
        }

        public static bool Shaking(Map map)
        {
            if (map == null || RM_ContagionSky.ExtFor(map) == null) return false;
            RM_MapComponent_ContagionSky sky = map.GetComponent<RM_MapComponent_ContagionSky>();
            return sky != null && RM_TellRenderKernel.Shaking(RM_ContagionSettings.burnTellsEnabled, sky.TellsBegun, sky.BurnActive);
        }
    }

    public class RM_PawnRenderNodeProperties_TellSink : PawnRenderNodeProperties
    {
        // How far the body drops, in cells, when fully settled.
        public float sinkDepth = 0.3f;
        // How much the body flattens (and widens by half as much) when fully settled.
        public float squash = 0.12f;
    }

    public class PawnRenderNodeWorker_RM_TellSink : PawnRenderNodeWorker_AnimalBody
    {
        private static float Fraction(PawnDrawParms parms)
        {
            Pawn p = parms.pawn;
            if (p == null || p.Dead || !p.Spawned || parms.flags.FlagSet(PawnRenderFlags.Portrait)) return 0f;
            return RM_ContagionTellRender.SinkFraction(p.Map);
        }

        public override Vector3 OffsetFor(PawnRenderNode node, PawnDrawParms parms, out Vector3 pivot)
        {
            Vector3 v = base.OffsetFor(node, parms, out pivot);
            float f = Fraction(parms);
            if (f > 0f && node.Props is RM_PawnRenderNodeProperties_TellSink sp)
            {
                v.z -= sp.sinkDepth * f;
            }
            return v;
        }

        public override Vector3 ScaleFor(PawnRenderNode node, PawnDrawParms parms)
        {
            Vector3 s = base.ScaleFor(node, parms);
            float f = Fraction(parms);
            if (f > 0f && node.Props is RM_PawnRenderNodeProperties_TellSink sp)
            {
                s.z *= 1f - sp.squash * f;
                s.x *= 1f + 0.5f * sp.squash * f;
            }
            return s;
        }
    }

    // The rattlegrope. Identical to a vanilla Plant except while the sky clock says it is shaking: then it prints
    // nothing into the static mesh and draws its one mesh (maxMeshCount 1, Graphic_Single) per frame, offset sideways.
    // Size, position jitter and flip are computed exactly as Plant.Print does for a single-mesh plant.
    public class RM_Plant_Rattlegrope : Plant
    {
        // Sideways rattle in cells at full amplitude.
        private const float ShakeAmplitude = 0.06f;

        public override void Print(SectionLayer layer)
        {
            if (RM_ContagionTellRender.Shaking(Map)) return;
            base.Print(layer);
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            if (!Spawned || !RM_ContagionTellRender.Shaking(Map)) return;
            Vector3 center = this.TrueCenter();
            Rand.PushState();
            Rand.Seed = Position.GetHashCode();
            float visual = def.plant.visualSizeRange.LerpThroughRange(Growth);
            float size = def.graphicData.drawSize.x * visual;
            Vector3 pos = center + Gen.RandomHorizontalVector(0.05f);
            if (pos.z - visual / 2f < Position.z) pos.z = Position.z + visual / 2f;
            bool flipUv = Rand.Bool;
            Rand.PopState();
            pos.x += RM_TellRenderKernel.ShakeOffset(Find.TickManager.TicksGame, thingIDNumber, ShakeAmplitude * size);
            Material mat = Graphic.MatSingleFor(this);
            Mesh mesh = flipUv ? MeshPool.GridPlaneFlip(new Vector2(size, size)) : MeshPool.GridPlane(new Vector2(size, size));
            Graphics.DrawMesh(mesh, pos, Quaternion.identity, mat, 0);
        }
    }
}
