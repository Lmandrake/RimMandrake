using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_CHATRAK_SNAP_BUILD_1 (WARSCAR_SNAP_MARK_1 spec 1, 2, 8; design
    // warscar_turn3_development_2026-09-30.md section 2.5). The chatrak's snap: on a Warscar map a
    // sweep arms every WILD RM_Chatrak already carrying vanilla Scaria (the biome rolls it at spawn,
    // wildAnimalScariaChance 0.5) with RM_ChatrakIncubation, whose visible stages are the warning:
    // plates lifting (render overlay, stage 1), off its feed (hunger 0, stage 2), circling (stage 3,
    // this comp walks it round a ring of radius 3), the snap (stage 4, ManhunterPermanent mtb 0.5 d).
    // The spec named EnvironmentalHazards' GameCondition_ArmLatentHazard in biomeMapConditions;
    // mandrake.rm.warscar does not depend on that mod, so the sweep is a MapComponent here (same
    // call as the mark). A clean chatrak is never armed, so it tames and never snaps.

    public class RM_HediffCompProperties_ChatrakTurning : HediffCompProperties
    {
        public float ringRadius = 3f;
        public int circleCheckTicks = 250;

        public RM_HediffCompProperties_ChatrakTurning()
        {
            compClass = typeof(RM_HediffComp_ChatrakTurning);
        }
    }

    public class RM_HediffComp_ChatrakTurning : HediffComp
    {
        public IntVec3 anchor = IntVec3.Invalid;
        public int ringStep;
        private int ticksToCheck;

        public const int CirclingStage = 3;
        public const float SnapOffCeiling = 0.95f;

        private RM_HediffCompProperties_ChatrakTurning Props => (RM_HediffCompProperties_ChatrakTurning)props;

        public override void CompPostTickInterval(ref float severityAdjustment, int delta)
        {
            // Snap off: one already turning stops short of the snap stage.
            if (!RM_WarscarSettings.snapEnabled && parent.Severity + severityAdjustment > SnapOffCeiling)
            {
                severityAdjustment = Mathf.Min(severityAdjustment, SnapOffCeiling - parent.Severity);
            }
            ticksToCheck -= delta;
            if (ticksToCheck > 0)
            {
                return;
            }
            ticksToCheck = Props.circleCheckTicks;
            if (parent.CurStageIndex != CirclingStage)
            {
                anchor = IntVec3.Invalid;
                return;
            }
            TryCircle();
        }

        private static bool Idle(Job job)
        {
            if (job == null)
            {
                return true;
            }
            JobDef d = job.def;
            return d == JobDefOf.Wait_Wander || d == JobDefOf.GotoWander || d == JobDefOf.Wait
                || d == JobDefOf.Ingest;
        }

        /// <summary>Walks the pawn to the next point of its ring. Returns the target cell or Invalid.</summary>
        public IntVec3 TryCircle()
        {
            Pawn p = Pawn;
            if (p == null || !p.Spawned || p.Downed || p.InMentalState || p.jobs == null
                || (p.jobs.curDriver != null && p.jobs.curDriver.asleep) || !Idle(p.CurJob))
            {
                return IntVec3.Invalid;
            }
            if (p.CurJob != null && p.CurJob.def == JobDefOf.GotoWander && p.CurJob.playerForced == false
                && anchor.IsValid && p.CurJob.targetA.Cell.DistanceTo(anchor) <= Props.ringRadius + 1.5f
                && p.jobs.curDriver != null && p.pather.Moving)
            {
                return p.CurJob.targetA.Cell;   // already walking the ring
            }
            if (!anchor.IsValid)
            {
                anchor = p.Position;
            }
            for (int attempt = 0; attempt < 8; attempt++)
            {
                ringStep = (ringStep + 1) % 8;
                float a = ringStep * Mathf.PI / 4f;
                IntVec3 c = anchor + new IntVec3(Mathf.RoundToInt(Mathf.Cos(a) * Props.ringRadius), 0,
                    Mathf.RoundToInt(Mathf.Sin(a) * Props.ringRadius));
                if (!c.InBounds(p.Map) || !c.Standable(p.Map) || c == p.Position
                    || !p.CanReach(c, PathEndMode.OnCell, Danger.Deadly))
                {
                    continue;
                }
                Job job = JobMaker.MakeJob(JobDefOf.GotoWander, c);
                job.locomotionUrgency = LocomotionUrgency.Walk;
                job.expiryInterval = 600;
                p.jobs.StartJob(job, JobCondition.InterruptForced);
                return c;
            }
            return IntVec3.Invalid;
        }

        public override void CompExposeData()
        {
            Scribe_Values.Look(ref anchor, "rmChatrakAnchor", IntVec3.Invalid);
            Scribe_Values.Look(ref ringStep, "rmChatrakRingStep", 0);
        }

        public override string CompDebugString()
        {
            return "ring anchor " + anchor + " step " + ringStep;
        }
    }

    /// <summary>Stage-1 overlay: the lifted plates, drawn at the chatrak's own life-stage size, only
    /// from <see cref="RM_ChatrakSnap.PlatesStage"/> on.</summary>
    public class RM_PawnRenderNode_ChatrakPlates : PawnRenderNode
    {
        public RM_PawnRenderNode_ChatrakPlates(Pawn pawn, PawnRenderNodeProperties props, PawnRenderTree tree)
            : base(pawn, props, tree)
        {
        }

        private static Vector2 BodySize(Pawn pawn)
        {
            PawnKindLifeStage ls = pawn.ageTracker?.CurKindLifeStage;
            return ls?.bodyGraphicData != null ? ls.bodyGraphicData.drawSize : Vector2.one;
        }

        public override Graphic GraphicFor(Pawn pawn)
        {
            if (props.texPath.NullOrEmpty())
            {
                return null;
            }
            return GraphicDatabase.Get<Graphic_Multi>(props.texPath, ShaderDatabase.Cutout, BodySize(pawn), Color.white);
        }

        public override GraphicMeshSet MeshSetFor(Pawn pawn)
        {
            Vector2 s = BodySize(pawn);
            return MeshPool.GetMeshSetForSize(s.x, s.y);
        }
    }

    public class RM_PawnRenderNodeWorker_ChatrakPlates : PawnRenderNodeWorker
    {
        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
        {
            if (!base.CanDrawNow(node, parms) || parms.rotDrawMode == RotDrawMode.Dessicated)
            {
                return false;
            }
            return node.hediff != null && node.hediff.CurStageIndex >= RM_ChatrakSnap.PlatesStage;
        }
    }

    public static class RM_ChatrakSnap
    {
        public const int PlatesStage = 1;

        private static HediffDef incubation;
        private static PawnKindDef chatrak;

        public static HediffDef Incubation => incubation ?? (incubation = DefDatabase<HediffDef>.GetNamedSilentFail("RM_ChatrakIncubation"));
        public static PawnKindDef Chatrak => chatrak ?? (chatrak = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Chatrak"));

        public static bool Armable(Pawn p)
        {
            return p != null && !p.Dead && p.Spawned && p.kindDef == Chatrak && p.Faction == null
                && p.health?.hediffSet != null && p.health.hediffSet.HasHediff(HediffDefOf.Scaria)
                && Incubation != null && !p.health.hediffSet.HasHediff(Incubation);
        }

        /// <summary>One arming sweep. Returns how many chatrak it armed.</summary>
        public static int Sweep(Map map)
        {
            if (!RM_WarscarSettings.snapEnabled || map == null || Incubation == null || Chatrak == null)
            {
                return 0;
            }
            int armed = 0;
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                if (Armable(pawns[i]))
                {
                    pawns[i].health.AddHediff(Incubation);
                    armed++;
                }
            }
            return armed;
        }

        private static Pawn ProofChatrak(Map map, bool scaria)
        {
            IntVec3 c;
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 20, x => x.Standable(map) && !x.Fogged(map), out c))
            {
                return null;
            }
            Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(Chatrak, null,
                PawnGenerationContext.NonPlayer, map.Tile, fixedBiologicalAge: 6f, fixedChronologicalAge: 6f));
            GenSpawn.Spawn(p, c, map);
            Hediff s = p.health.hediffSet.GetFirstHediffOfDef(HediffDefOf.Scaria);
            if (scaria && s == null)
            {
                p.health.AddHediff(HediffDefOf.Scaria);
            }
            else if (!scaria && s != null)
            {
                p.health.RemoveHediff(s);
            }
            return p;
        }

        /// <summary>Bridge proof (jawa/static_call "current|0.4"): spawns a wild scaria chatrak, runs one
        /// sweep, sets the incubation to <paramref name="severity"/> and reads the stage back:
        /// "PAWN RM_Chatrak123 armed 1 severity 0.40 stage plates lifting plates=shown hunger x1.00 circling=- snap=-".
        /// At 0.9 it also walks the ring once; at 1.0 it fires the stage's own mental-state giver.</summary>
        public static string ProofStage(Map map, float severity)
        {
            if (map == null)
            {
                return "REFUSED: no map";
            }
            if (Chatrak == null || Incubation == null)
            {
                return "REFUSED: RM_Chatrak or RM_ChatrakIncubation missing";
            }
            Pawn p = ProofChatrak(map, true);
            if (p == null)
            {
                return "REFUSED: no standable cell near the map centre";
            }
            int armed = Sweep(map);
            Hediff h = p.health.hediffSet.GetFirstHediffOfDef(Incubation);
            if (h == null)
            {
                return "PAWN " + p.ThingID + " armed " + armed + " | NOT ARMED (snapEnabled=" + RM_WarscarSettings.snapEnabled + ")";
            }
            h.Severity = severity;
            string circling = "-";
            if (h.CurStageIndex == RM_HediffComp_ChatrakTurning.CirclingStage)
            {
                RM_HediffComp_ChatrakTurning comp = ((HediffWithComps)h).GetComp<RM_HediffComp_ChatrakTurning>();
                IntVec3 t = comp == null ? IntVec3.Invalid : comp.TryCircle();
                circling = t.IsValid ? "ring@" + t + " r=" + t.DistanceTo(comp.anchor).ToString("0.0") : "none";
            }
            string snap = "-";
            if (h.CurStage?.mentalStateGivers != null && h.CurStage.mentalStateGivers.Count > 0)
            {
                bool started = p.mindState.mentalStateHandler.TryStartMentalState(h.CurStage.mentalStateGivers[0].mentalState,
                    "proof", forceWake: true);
                snap = started ? p.MentalStateDef?.defName ?? "?" : "refused";
            }
            return "PAWN " + p.ThingID + " armed " + armed + " severity " + h.Severity.ToString("0.##")
                + " stage " + (h.CurStage?.label ?? "-") + " visible=" + h.Visible
                + " plates=" + (h.CurStageIndex >= PlatesStage ? "shown" : "hidden")
                + " hunger x" + p.health.hediffSet.HungerRateFactor.ToString("0.00")
                + " circling=" + circling + " snap=" + snap;
        }

        /// <summary>Bridge proof: a clean (scaria-free) chatrak is never armed. "PAWN ... clean armed=False".</summary>
        public static string ProofClean(Map map)
        {
            if (map == null || Chatrak == null)
            {
                return "REFUSED: no map or no RM_Chatrak";
            }
            Pawn p = ProofChatrak(map, false);
            if (p == null)
            {
                return "REFUSED: no standable cell near the map centre";
            }
            Sweep(map);
            return "PAWN " + p.ThingID + " clean armed=" + (Incubation != null && p.health.hediffSet.HasHediff(Incubation));
        }
    }

    /// <summary>The arming sweep on a Warscar map, every snapArmingHours.</summary>
    public class RM_MapComponent_ChatrakSnap : MapComponent
    {
        private int nextSweepTick = -1;

        public RM_MapComponent_ChatrakSnap(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (!RM_WarscarSettings.snapEnabled || Find.TickManager.TicksGame % 250 != 113)
            {
                return;
            }
            if (map.Biome == null || map.Biome != RM_WarscarMark.Warscar)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (nextSweepTick >= 0 && now < nextSweepTick)
            {
                return;
            }
            nextSweepTick = now + Mathf.Max(2500, Mathf.RoundToInt(RM_WarscarSettings.snapArmingHours * 2500f));
            RM_ChatrakSnap.Sweep(map);
        }

        public override void ExposeData()
        {
            Scribe_Values.Look(ref nextSweepTick, "rmChatrakNextSweep", -1);
        }
    }

    /// <summary>Stage speed: scale the incubation's per-pawn climb range at startup (restart to apply).</summary>
    [StaticConstructorOnStartup]
    public static class RM_ChatrakSnapStartup
    {
        static RM_ChatrakSnapStartup()
        {
            float f = RM_WarscarSettings.snapStageSpeed;
            if (RM_ChatrakSnap.Incubation?.comps == null || Mathf.Approximately(f, 1f) || f <= 0f)
            {
                return;
            }
            foreach (HediffCompProperties cp in RM_ChatrakSnap.Incubation.comps)
            {
                if (cp is HediffCompProperties_SeverityPerDay spd)
                {
                    spd.severityPerDayRange = new FloatRange(spd.severityPerDayRange.min * f, spd.severityPerDayRange.max * f);
                    spd.severityPerDay *= f;
                }
            }
        }
    }
}
