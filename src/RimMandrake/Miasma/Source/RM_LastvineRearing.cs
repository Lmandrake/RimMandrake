using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Miasma
{
    /// <summary>
    /// Phase 0 P3 (design/RimMandrake/biome_sprint_kickoff_2026-10-15.md §0.5.3 item 2): the lastvine's two looks.
    /// The owner's Miasma sheet note on the creature (2026-10-08): "Needs both calm, closed-mouth, sessile-like imagery
    /// with head hung like a ripe pod... and then that same pod reared up horrifying into a huge gaping maw and actively
    /// writhing tentacles." This replaces the donor's twitching-limb render tree (Alpha Animals' SpasticScaled, donor code)
    /// with the vanilla graphic-state system the engine already uses for swimming and stationary animals:
    ///
    ///   RM_PawnRenderNode_RearingBody   the vanilla animal body node, plus one extra state graphic (RM_Reared) built
    ///                                   from the life stage's body texPath + rearedSuffix, only when that texture exists.
    ///   RM_PawnRenderNodeWorker_Rearing the vanilla animal body worker; it picks RM_Reared while the creature is engaged.
    ///
    /// Engaged = in an aggressive mental state, holding an enemy target, hunting or attacking, harmed or attacking within
    /// lingerTicks, or (checked every scanIntervalTicks, cached per pawn) any other creature within nearRadius cells.
    /// No comp and no tick: the state is read when the pawn is drawn. With the reared texture absent (art not installed)
    /// the node adds no state and the creature draws its calm body, as before. Mod Settings: lastvineRearingEnabled.
    /// </summary>
    public class RM_PawnRenderNodeProperties_Rearing : PawnRenderNodeProperties
    {
        public string rearedSuffix = "_Reared";
        public int lingerTicks = 300;
        public float nearRadius = 4.9f;
        public int scanIntervalTicks = 60;

        public RM_PawnRenderNodeProperties_Rearing()
        {
            nodeClass = typeof(RM_PawnRenderNode_RearingBody);
            workerClass = typeof(RM_PawnRenderNodeWorker_Rearing);
        }
    }

    [DefOf]
    public static class RM_MiasmaGraphicStateDefOf
    {
        public static GraphicStateDef RM_Reared;

        static RM_MiasmaGraphicStateDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_MiasmaGraphicStateDefOf));
        }
    }

    public class RM_PawnRenderNode_RearingBody : PawnRenderNode_AnimalPart_Body
    {
        private static readonly Dictionary<string, bool> textureExists = new Dictionary<string, bool>();  // main thread only (EnsureInitialized)

        // Per-pawn "something near" scan cache. Instance fields, not shared statics: GetGraphicState runs inside the
        // parallel pre-draw job, and only one job item handles a given pawn at a time.
        internal int lastScanTick = -99999;
        internal bool lastScanNear;

        public RM_PawnRenderNode_RearingBody(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
            : base(pawn, props, tree)
        {
        }

        protected override IEnumerable<(GraphicStateDef state, Graphic graphic)> StateGraphicsFor(Pawn pawn)
        {
            foreach (var item in base.StateGraphicsFor(pawn))
                yield return item;
            Graphic reared = RearedGraphic(pawn);
            if (reared != null)
                yield return (RM_MiasmaGraphicStateDefOf.RM_Reared, reared);
        }

        private Graphic RearedGraphic(Pawn pawn)
        {
            PawnKindLifeStage stage = pawn.ageTracker?.CurKindLifeStage;
            GraphicData data = stage?.bodyGraphicData;
            var p = props as RM_PawnRenderNodeProperties_Rearing;
            if (data == null || p == null || data.texPath.NullOrEmpty())
                return null;
            string path = data.texPath + p.rearedSuffix;
            if (!textureExists.TryGetValue(path, out bool exists))
            {
                exists = ContentFinder<Texture2D>.Get(path + "_south", false) != null;
                textureExists[path] = exists;
            }
            if (!exists)
                return null;
            Graphic calm = data.Graphic;
            Color c1 = calm.Color;
            Color c2 = calm.ColorTwo;
            if (pawn.IsMutant)
            {
                c1 = MutantUtility.GetMutantSkinColor(pawn, c1);
                c2 = MutantUtility.GetMutantSkinColor(pawn, c2);
            }
            c1 = pawn.health.hediffSet.GetSkinColor(c1);
            c2 = pawn.health.hediffSet.GetSkinColor(c2);
            return GraphicDatabase.Get<Graphic_Multi>(path, calm.Shader, calm.drawSize, c1, c2);
        }
    }

    public class RM_PawnRenderNodeWorker_Rearing : PawnRenderNodeWorker_AnimalBody
    {
        protected override GraphicStateDef GetGraphicState(PawnRenderNode node, PawnDrawParms parms)
        {
            GraphicStateDef reared = RM_MiasmaGraphicStateDefOf.RM_Reared;
            if (RM_MiasmaSettings.lastvineRearingEnabled
                && node.tree.currentAnimation == null
                && !parms.flags.FlagSet(PawnRenderFlags.Portrait)
                && parms.rotDrawMode == RotDrawMode.Fresh
                && node.ContainsGraphicState(reared)
                && node.Props is RM_PawnRenderNodeProperties_Rearing p
                && node is RM_PawnRenderNode_RearingBody body
                && Engaged(parms.pawn, p, body))
                return reared;
            return base.GetGraphicState(node, parms);
        }

        private static bool Engaged(Pawn pawn, RM_PawnRenderNodeProperties_Rearing p, RM_PawnRenderNode_RearingBody body)
        {
            if (pawn == null || pawn.Dead || pawn.Downed || !pawn.Spawned)
                return false;
            if (pawn.InAggroMentalState)
                return true;
            Pawn_MindState ms = pawn.mindState;
            if (ms == null)
                return false;
            if (ms.enemyTarget != null)
                return true;
            int now = Find.TickManager.TicksGame;
            if (now - ms.lastEngageTargetTick < p.lingerTicks || now - ms.lastAttackTargetTick < p.lingerTicks
                || now - ms.lastHarmTick < p.lingerTicks)
                return true;
            JobDef job = pawn.CurJobDef;
            if (job == JobDefOf.PredatorHunt || job == JobDefOf.AttackMelee || job == JobDefOf.AttackStatic)
                return true;
            return SomethingNear(pawn, p, body, now);
        }

        private static bool SomethingNear(Pawn pawn, RM_PawnRenderNodeProperties_Rearing p, RM_PawnRenderNode_RearingBody body,
            int now)
        {
            if (now - body.lastScanTick < p.scanIntervalTicks && now >= body.lastScanTick)
                return body.lastScanNear;
            bool near = false;
            foreach (Thing t in GenRadial.RadialDistinctThingsAround(pawn.Position, pawn.Map, p.nearRadius, true))
            {
                if (t is Pawn other && other != pawn && other.def != pawn.def && !other.Dead)
                {
                    near = true;
                    break;
                }
            }
            body.lastScanTick = now;
            body.lastScanNear = near;
            return near;
        }
    }
}
