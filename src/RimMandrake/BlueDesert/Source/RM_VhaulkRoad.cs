// BLUEDESERT_GPT_ENRICHMENT_1 §4 — the vhaulk's stay and walk-off.
//
// Owner-picked by question card 2026-09-30 from the GPT enrichment consult
// (Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.md §9). The ruled
// giant (BLUEDESERT_RULED_CONTENT_1 §2) arrives with a letter and, after some
// days, walks off an edge with a letter. It never silently despawns.
// The rime road it pressed, the flora cropping, the frost wake and the seam
// booms were TRIMMED 2026-10-23 (fluff review, design/RimMandrake/
// fluff_cuts_2026-10-23.md: "scenic; keep walk-off letter").
//
// Engine seam (RimSage, decompiled 1.6, 2026-09-30):
//  - Pawn.ExitMap -> DeSpawnOrDeselect -> ThingComp.PostDeSpawn while the
//    pawn is still alive and standing on the edge cell; that is the exit
//    hook. A death despawns through Kill, which RM_HediffComp_HeatGated-
//    ExplodeOnDeath owns; this comp checks Dead and stays out of it.
//
// The ruled detonation gates (RM_VhaulkDetonation.cs: heat-family death,
// lightning free, EMP-on-hit) are untouched: nothing here deals damage,
// stuns, or kills. The departure is ordinary walking.
//
// Gate: masterEnabled && vhaulkDepartsEnabled (the walk-off after stayDays).

using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.BlueDesert
{
    public class CompProperties_VhaulkRoad : CompProperties
    {
        public int stepIntervalTicks = 60;
        /// <summary>Base days on a map before it walks off; Mod Settings
        /// scale it.</summary>
        public FloatRange stayDays = new FloatRange(2f, 5f);

        [MustTranslate] public string arrivalLetterLabel;
        [MustTranslate] public string arrivalLetterText;
        [MustTranslate] public string departureLetterLabel;
        [MustTranslate] public string departureLetterText;

        public CompProperties_VhaulkRoad()
        {
            compClass = typeof(RM_CompVhaulkRoad);
        }
    }

    public class RM_CompVhaulkRoad : ThingComp
    {
        private int departTick = -1;
        private bool departing;

        public CompProperties_VhaulkRoad Props => (CompProperties_VhaulkRoad)props;

        private Pawn Vhaulk => parent as Pawn;

        private static bool DepartOn =>
            RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.vhaulkDepartsEnabled;

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref departTick, "rmDepartTick", -1);
            Scribe_Values.Look(ref departing, "rmDeparting", false);
        }

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad)
            {
                return;
            }
            Pawn pawn = Vhaulk;
            Map map = parent.Map;
            if (pawn == null || map == null)
            {
                return;
            }
            departing = false;
            departTick = RM_BlueKernel.DepartTick(Find.TickManager.TicksGame, Props.stayDays.RandomInRange, RM_BlueDesertSettings.vhaulkStayDaysFactor);
            // A vhaulk placed at map generation is scenery, not an arrival.
            bool arrival = pawn.Faction == null && Find.TickManager.TicksGame - map.generationTick > 2500;
            if (arrival && RM_BlueDesertSettings.masterEnabled && !Props.arrivalLetterText.NullOrEmpty())
            {
                Find.LetterStack.ReceiveLetter(Props.arrivalLetterLabel ?? "Vhaulk", Props.arrivalLetterText,
                    LetterDefOf.NeutralEvent, pawn);
            }
        }

        public override void CompTick()
        {
            base.CompTick();
            Pawn pawn = Vhaulk;
            if (pawn == null || !pawn.Spawned || pawn.Dead)
            {
                return;
            }
            if (!parent.IsHashIntervalTick(Mathf.Max(1, Props.stepIntervalTicks)))
            {
                return;
            }
            // A flee, a fight or a meal can replace the walk-off job; when that happens, send it on its way again.
            int depart = RM_BlueKernel.DepartAction(DepartOn, departTick, Find.TickManager.TicksGame, parent.IsHashIntervalTick(250), departing,
                pawn.CurJob != null && pawn.CurJob.exitMapOnArrival);
            if (depart == 1)
            {
                departing = false;
            }
            if (depart != 0)
            {
                TryStartDeparture(pawn);
            }
        }

        private void TryStartDeparture(Pawn pawn)
        {
            // Only a wild, calm giant wanders off. A tamed one belongs to the
            // player; a manhunting one is busy; a downed one cannot walk.
            if (pawn.Faction != null || pawn.Downed || pawn.InMentalState || pawn.jobs == null)
            {
                return;
            }
            if (!RCellFinder.TryFindBestExitSpot(pawn, out IntVec3 exit, TraverseMode.ByPawn, false))
            {
                return;
            }
            Job job = JobMaker.MakeJob(JobDefOf.Goto, exit);
            job.exitMapOnArrival = true;
            job.locomotionUrgency = LocomotionUrgency.Walk;
            job.expiryInterval = -1;
            pawn.jobs.StartJob(job, JobCondition.InterruptForced);
            departing = true;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            base.PostDeSpawn(map, mode);
            Pawn pawn = Vhaulk;
            if (pawn == null || pawn.Dead || map == null || mode != DestroyMode.Vanish)
            {
                return;
            }
            // ExitMap despawns from the edge cell; anything else (a transport
            // pod, a debug despawn) is not a walk-off and gets no letter.
            if (!pawn.Position.IsValid || pawn.Position.DistanceToEdge(map) > 1)
            {
                return;
            }
            departing = false;
            if (!RM_BlueDesertSettings.masterEnabled || Props.departureLetterText.NullOrEmpty())
            {
                return;
            }
            Find.LetterStack.ReceiveLetter(Props.departureLetterLabel ?? "Vhaulk gone", Props.departureLetterText,
                LetterDefOf.NeutralEvent, new LookTargets(pawn.Position, map));
        }

        public override string CompInspectStringExtra()
        {
            if (!DepartOn || departTick < 0 || Vhaulk?.Faction != null)
            {
                return null;
            }
            return departing ? "Walking off the plateau." : null;
        }
    }
}
