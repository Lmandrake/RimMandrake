// BLUEDESERT_GPT_ENRICHMENT_1 §4 — the vhaulk road.
//
// Owner-picked by question card 2026-09-30 from the GPT enrichment consult
// (Transient/bedazzle_gpt_enrich_2026-09-30/bluedesert.md §9). Deepens the
// ruled giant (BLUEDESERT_RULED_CONTENT_1 §2): its pillar feet press the ice
// into a broad rime road that lasts days, the flora it passes is cropped flat,
// its cistern seams boom at long intervals, and frost hangs in its wake. It
// arrives with a letter and, after some days, walks off an edge with a
// letter, leaving the road running to the edge. It never silently despawns.
//
// Engine seams (RimSage, decompiled 1.6, 2026-09-30):
//  - TerrainDef.temporary + TerrainGrid.SetTempTerrain puts the road in the
//    temp-terrain layer ABOVE the real terrain, and
//    Map.tempTerrain.QueueRemoveTerrain(cell, tick) removes it on schedule
//    (vanilla floods and lava do exactly this), so the underlying ice is never
//    overwritten and nothing of ours has to remember it.
//  - TerrainGrid.DoTerrainChangedEffects only Destroy()s (DestroyMode.Vanish)
//    a plant on a terrain change. CompPlantCharge detonates on KillFinalize
//    only, so laying road can never set off the flora; and cropping here only
//    lowers Plant.Growth, it deals no damage at all.
//  - Pawn.ExitMap -> DeSpawnOrDeselect -> ThingComp.PostDeSpawn while the
//    pawn is still alive and standing on the edge cell; that is the exit
//    hook. A death despawns through Kill, which RM_HediffComp_HeatGated-
//    ExplodeOnDeath owns; this comp checks Dead and stays out of it.
//
// The ruled detonation gates (RM_VhaulkDetonation.cs: heat-family death,
// lightning free, EMP-on-hit) are untouched: nothing here deals damage,
// stuns, or kills. The departure is ordinary walking.
//
// Gates: masterEnabled && vhaulkRoadEnabled (road, cropping, frost, booms);
// masterEnabled && vhaulkDepartsEnabled (the walk-off after stayDays).

using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.BlueDesert
{
    public class CompProperties_VhaulkRoad : CompProperties
    {
        public TerrainDef roadTerrain;
        /// <summary>Only these natural terrains take the road (never a
        /// player floor).</summary>
        public List<TerrainDef> roadOnTerrains;
        public float roadRadius = 1.5f;
        /// <summary>Base days the road lasts; Mod Settings scale it.</summary>
        public FloatRange roadDays = new FloatRange(2f, 3f);

        public float cropRadius = 2.9f;
        public float cropToGrowth = 0.08f;

        public int stepIntervalTicks = 60;
        public float frostChancePerStep = 0.5f;

        public float boomMtbHours = 5f;
        public SoundDef boomSound;

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

        private static bool RoadOn =>
            RM_BlueDesertSettings.masterEnabled && RM_BlueDesertSettings.vhaulkRoadEnabled;

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
            float factor = Mathf.Max(0.1f, RM_BlueDesertSettings.vhaulkStayDaysFactor);
            departTick = Find.TickManager.TicksGame + Mathf.RoundToInt(Props.stayDays.RandomInRange * factor * 60000f);
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
            Map map = pawn.Map;
            if (RoadOn)
            {
                if (pawn.pather != null && pawn.pather.MovingNow)
                {
                    LayRoad(pawn, map);
                    CropFlora(pawn, map);
                    if (Rand.Chance(Props.frostChancePerStep))
                    {
                        FleckMaker.ThrowDustPuffThick(pawn.DrawPos, map, Rand.Range(1.8f, 2.8f),
                            new Color(0.88f, 0.93f, 1f, 0.8f));
                    }
                }
                if (Props.boomSound != null
                    && Rand.MTBEventOccurs(Props.boomMtbHours, 2500f, Props.stepIntervalTicks))
                {
                    Props.boomSound.PlayOneShot(new TargetInfo(pawn.Position, map));
                }
            }
            if (DepartOn && !departing && departTick >= 0 && Find.TickManager.TicksGame >= departTick
                && parent.IsHashIntervalTick(250))
            {
                TryStartDeparture(pawn);
            }
        }

        private void LayRoad(Pawn pawn, Map map)
        {
            TerrainDef road = Props.roadTerrain;
            if (road == null || !road.temporary)
            {
                return;
            }
            float days = Props.roadDays.RandomInRange * Mathf.Max(0.1f, RM_BlueDesertSettings.vhaulkRoadDaysFactor);
            int removeAt = Find.TickManager.TicksGame + Mathf.RoundToInt(days * 60000f);
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.roadRadius, true))
            {
                if (!c.InBounds(map) || map.terrainGrid.TempTerrainAt(c) != null)
                {
                    continue; // already road (its first expiry stands), flood, lava...
                }
                TerrainDef under = map.terrainGrid.TerrainAt(c);
                if (Props.roadOnTerrains != null && !Props.roadOnTerrains.Contains(under))
                {
                    continue;
                }
                if (c.GetEdifice(map) != null)
                {
                    continue;
                }
                map.terrainGrid.SetTempTerrain(c, road);
                map.tempTerrain.QueueRemoveTerrain(c, removeAt);
            }
        }

        private void CropFlora(Pawn pawn, Map map)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.cropRadius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }
                Plant plant = c.GetPlant(map);
                if (plant == null || plant.def.plant == null || plant.def.plant.IsTree
                    || plant.Growth <= Props.cropToGrowth)
                {
                    continue;
                }
                plant.Growth = Props.cropToGrowth;
                map.mapDrawer.MapMeshDirty(c, MapMeshFlagDefOf.Things);
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
