using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.CreatureBehaviors
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_MIRAGE_CONDITION_1 — the mirage.
    //
    // On a sun-heat biome whose RM_SunHeatExtension names a mirageCondition,
    // and while the map's sun stands at or above mirageMinElevationDegrees
    // (RM_MapComponent_ShadeGrid.SunElevationDegrees — never re-derived), the
    // map holds a permanent RM_GameCondition_Mirage. It:
    //   - paints a shimmering false-water band along the sun-ward map edge
    //     (RM_SunHeatMath.MirageEdge), drawn each frame, nothing spawned;
    //   - cuts medium/long-range accuracy for a shooter in full sun
    //     (RM_StatPart_MirageShimmer, patched onto vanilla
    //     ShootingAccuracyFactor_Medium/_Long — the distance terms ShotReport
    //     already multiplies in);
    //   - lets a heat-struck pawn in full sun break into "chasing the water"
    //     (RM_MentalState_ChasingWater): it walks for the band and the water
    //     recedes as it arrives. It ends when it collapses (downed), when a
    //     friend reaches it (a drafted colonist adjacent, or any same-faction
    //     pawn for an AI faction), or on the def's timers. Its targets are
    //     always inside the map margin and the job never exits, so the pawn
    //     always stays on the map, and the end always sends a letter.
    // Mod Settings: mirageEnabled (off: the condition ends on the next
    // recompute, no band, no accuracy cut, no new breaks) and
    // mirageBreakChanceMultiplier.
    // ════════════════════════════════════════════════════════════════════
    public static class RM_Mirage
    {
        /// <summary>Cells kept between a chase target and the map edge.</summary>
        public const int EdgeMargin = 4;

        /// <summary>Called on every shade-grid recompute: hold or end the
        /// condition to match the sun and the settings.</summary>
        public static void Sync(Map map, RM_MapComponent_ShadeGrid grid)
        {
            RM_SunHeatExtension ext = grid.HeatExtension;
            GameConditionDef def = ext?.mirageCondition;
            if (def == null)
            {
                return;
            }
            bool wanted = RM_CreatureBehaviorsSettings.mirageEnabled && grid.SunHeatActive
                          && RM_SunHeatMath.MirageActive(grid.SunElevationDegrees, ext.mirageMinElevationDegrees);
            GameCondition existing = map.gameConditionManager.GetActiveCondition(def);
            if (wanted && existing == null)
            {
                map.gameConditionManager.RegisterCondition(GameConditionMaker.MakeConditionPermanent(def));
            }
            else if (!wanted && existing != null)
            {
                existing.suppressEndMessage = true;
                existing.End();
            }
        }

        /// <summary>The live mirage on this map, or null.</summary>
        public static RM_GameCondition_Mirage ActiveOn(Map map)
        {
            if (map == null || !RM_CreatureBehaviorsSettings.mirageEnabled)
            {
                return null;
            }
            List<GameCondition> active = map.gameConditionManager.ActiveConditions;
            for (int i = 0; i < active.Count; i++)
            {
                if (active[i] is RM_GameCondition_Mirage m)
                {
                    return m;
                }
            }
            return null;
        }

        /// <summary>A standable, reachable cell in the band near the
        /// sun-ward edge for this pawn, or Invalid.</summary>
        public static IntVec3 ChaseTarget(Pawn pawn, int edge)
        {
            Map map = pawn.Map;
            IntVec3 size = map.Size;
            for (int attempt = 0; attempt < 6; attempt++)
            {
                IntVec3 root;
                switch (edge)
                {
                    case 1: root = new IntVec3(size.x - 1 - EdgeMargin, 0, Rand.RangeInclusive(EdgeMargin, size.z - 1 - EdgeMargin)); break;
                    case 2: root = new IntVec3(Rand.RangeInclusive(EdgeMargin, size.x - 1 - EdgeMargin), 0, EdgeMargin); break;
                    case 3: root = new IntVec3(EdgeMargin, 0, Rand.RangeInclusive(EdgeMargin, size.z - 1 - EdgeMargin)); break;
                    default: root = new IntVec3(Rand.RangeInclusive(EdgeMargin, size.x - 1 - EdgeMargin), 0, size.z - 1 - EdgeMargin); break;
                }
                if (CellFinder.TryFindRandomCellNear(root, map, 6,
                        c => !c.CloseToEdge(map, EdgeMargin - 1) && c.Standable(map)
                             && pawn.CanReach(c, PathEndMode.OnCell, Danger.Deadly), out IntVec3 found))
                {
                    return found;
                }
            }
            return IntVec3.Invalid;
        }
    }

    public class RM_GameCondition_Mirage : GameCondition
    {
        private const int BreakCheckInterval = 250;
        private const int BandDepth = 6;

        private static Material bandMat;
        private static MaterialPropertyBlock bandProps;
        private static readonly int ColorId = Shader.PropertyToID("_Color");
        private static readonly Color WaterColor = new Color(0.78f, 0.88f, 0.97f);

        /// <summary>The sun-ward edge, from the shade grid's shadow vector.</summary>
        public int Edge
        {
            get
            {
                RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(SingleMap);
                if (grid == null || !grid.IsDirectional)
                {
                    return 0;
                }
                Vector2 d = grid.SunShadowDirection;
                return RM_SunHeatMath.MirageEdge(d.x, d.y);
            }
        }

        public override void GameConditionTick()
        {
            base.GameConditionTick();
            Map map = SingleMap;
            if (map == null || !RM_CreatureBehaviorsSettings.mirageEnabled
                || Find.TickManager.TicksGame % BreakCheckInterval != 0)
            {
                return;
            }
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(map);
            RM_SunHeatExtension ext = grid?.HeatExtension;
            if (ext?.mirageMentalState == null || !grid.SunHeatActive)
            {
                return;
            }
            float mtb = ext.mirageBreakMtbDays / Mathf.Max(0.0001f, RM_CreatureBehaviorsSettings.mirageBreakChanceMultiplier);
            if (RM_CreatureBehaviorsSettings.mirageBreakChanceMultiplier <= 0f)
            {
                return;
            }
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = pawns.Count - 1; i >= 0; i--)
            {
                Pawn p = pawns[i];
                if (p.RaceProps == null || !p.RaceProps.Humanlike || p.Downed || p.InMentalState || p.Drafted
                    || !p.Awake())
                {
                    continue;
                }
                Hediff hs = p.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.Heatstroke);
                if (hs == null || hs.Severity < ext.mirageHeatstrokeMin)
                {
                    continue;
                }
                if (grid.ExposureFor(p) < ext.mirageFullSunExposureMin)
                {
                    continue;
                }
                if (Rand.MTBEventOccurs(mtb, 60000f, BreakCheckInterval))
                {
                    p.mindState.mentalStateHandler.TryStartMentalState(ext.mirageMentalState,
                        "The heat has gone to their head, and the water on the horizon looks real.");
                }
            }
        }

        public override void GameConditionDraw(Map map)
        {
            base.GameConditionDraw(map);
            if (!RM_CreatureBehaviorsSettings.mirageEnabled)
            {
                return;
            }
            if (bandMat == null)
            {
                bandMat = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, Color.white);
                bandProps = new MaterialPropertyBlock();
            }
            int edge = Edge;
            IntVec3 size = map.Size;
            float y = AltitudeLayer.MoteOverhead.AltitudeFor();
            float t = Time.realtimeSinceStartup;
            for (int k = 0; k < BandDepth; k++)
            {
                float fade = 1f - k / (float)BandDepth;
                float shimmer = 0.6f + 0.4f * Mathf.Sin(t * 1.7f + k * 0.9f);
                Color c = WaterColor;
                c.a = 0.32f * fade * shimmer;
                bandProps.SetColor(ColorId, c);
                Vector3 pos;
                Vector3 scale;
                switch (edge)
                {
                    case 1: pos = new Vector3(size.x - 0.5f - k, y, size.z / 2f); scale = new Vector3(1f, 1f, size.z); break;
                    case 2: pos = new Vector3(size.x / 2f, y, 0.5f + k); scale = new Vector3(size.x, 1f, 1f); break;
                    case 3: pos = new Vector3(0.5f + k, y, size.z / 2f); scale = new Vector3(1f, 1f, size.z); break;
                    default: pos = new Vector3(size.x / 2f, y, size.z - 0.5f - k); scale = new Vector3(size.x, 1f, 1f); break;
                }
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(pos, Quaternion.identity, scale), bandMat, 0, null, 0, bandProps);
            }
        }
    }

    public class RM_MentalState_ChasingWater : MentalState
    {
        private IntVec3 target = IntVec3.Invalid;
        private Pawn rescuedBy;

        public IntVec3 Target
        {
            get
            {
                if (!target.IsValid || pawn.Map == null || !target.InBounds(pawn.Map))
                {
                    Recede();
                }
                return target;
            }
        }

        /// <summary>The water is not there: pick the next shimmer along the
        /// band.</summary>
        public void Recede()
        {
            if (pawn.Map == null)
            {
                target = IntVec3.Invalid;
                return;
            }
            RM_GameCondition_Mirage m = RM_Mirage.ActiveOn(pawn.Map);
            int edge = m != null ? m.Edge : 0;
            target = RM_Mirage.ChaseTarget(pawn, edge);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref target, "target", IntVec3.Invalid);
            Scribe_References.Look(ref rescuedBy, "rescuedBy");
        }

        public override void MentalStateTick(int delta)
        {
            if (pawn.Spawned && pawn.IsHashIntervalTick(60, delta))
            {
                if (target.IsValid && pawn.Position.InHorDistOf(target, 2.5f))
                {
                    Recede();
                    pawn.jobs?.EndCurrentJob(JobCondition.InterruptForced);
                }
                Pawn friend = AdjacentRescuer();
                if (friend != null)
                {
                    rescuedBy = friend;
                    RecoverFromState();
                    return;
                }
            }
            base.MentalStateTick(delta);
        }

        private Pawn AdjacentRescuer()
        {
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(pawn))
            {
                if (!c.InBounds(pawn.Map))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(pawn.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i] is Pawn other && other != pawn && other.RaceProps.Humanlike && !other.Downed
                        && !other.InMentalState && other.Faction != null && other.Faction == pawn.Faction
                        && (other.Drafted || other.Faction != Faction.OfPlayer))
                    {
                        return other;
                    }
                }
            }
            return null;
        }

        public override void PostEnd()
        {
            base.PostEnd();
            if (pawn == null || pawn.Dead || !PawnUtility.ShouldSendNotificationAbout(pawn))
            {
                return;
            }
            string text;
            if (pawn.Downed)
            {
                text = pawn.LabelShortCap + " collapsed in the sand, still reaching for water that was never there.";
            }
            else if (rescuedBy != null)
            {
                text = rescuedBy.LabelShortCap + " caught up with " + pawn.LabelShort
                     + " and turned them away from the water that is not there.";
            }
            else
            {
                text = pawn.LabelShortCap + " stopped. The water on the horizon is only light.";
            }
            Find.LetterStack.ReceiveLetter("Mirage: " + pawn.LabelShortCap, text, LetterDefOf.NeutralEvent, pawn);
        }
    }

    /// <summary>Walks a chasing pawn at the receding water. Lives in a node
    /// prepended to vanilla MentalStateNonCritical (Patches/RM_Mirage_ThinkTree.xml).
    /// A plain Goto never exits the map.</summary>
    public class RM_JobGiver_ChaseMirage : ThinkNode_JobGiver
    {
        protected override Job TryGiveJob(Pawn pawn)
        {
            if (!(pawn.MentalState is RM_MentalState_ChasingWater chase))
            {
                return null;
            }
            IntVec3 dest = chase.Target;
            if (!dest.IsValid)
            {
                return null;
            }
            Job job = JobMaker.MakeJob(JobDefOf.Goto, dest);
            job.locomotionUrgency = LocomotionUrgency.Jog;
            job.expiryInterval = 600;
            job.checkOverrideOnExpire = true;
            return job;
        }
    }

    /// <summary>Heat shimmer: a shooter standing in full sun under a mirage
    /// loses medium/long-range accuracy. Patched onto vanilla
    /// ShootingAccuracyFactor_Medium and _Long.</summary>
    public class RM_StatPart_MirageShimmer : StatPart
    {
        public float factor = 0.75f;

        private bool Applies(StatRequest req, out float f)
        {
            f = 1f;
            if (!req.HasThing || !(req.Thing is Pawn p) || !p.Spawned)
            {
                return false;
            }
            if (RM_Mirage.ActiveOn(p.Map) == null)
            {
                return false;
            }
            RM_MapComponent_ShadeGrid grid = RM_MapComponent_ShadeGrid.For(p.Map);
            RM_SunHeatExtension ext = grid?.HeatExtension;
            if (ext == null)
            {
                return false;
            }
            f = RM_SunHeatMath.MirageShimmerFactor(grid.ExposureFor(p), ext.mirageFullSunExposureMin, factor);
            return f < 1f;
        }

        public override void TransformValue(StatRequest req, ref float val)
        {
            if (Applies(req, out float f))
            {
                val *= f;
            }
        }

        public override string ExplanationPart(StatRequest req)
        {
            return Applies(req, out float f) ? "Heat shimmer (mirage, full sun): x" + f.ToStringPercent() : null;
        }
    }
}
