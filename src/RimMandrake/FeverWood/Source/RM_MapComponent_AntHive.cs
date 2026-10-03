using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_ANT_HIVE_DUNGEON_1. Records what RM_GenStep_AntHiveDungeon
    // actually carved on this map (and its farm chamber's herd, which it
    // keeps herded), so follow-on work (the parasite/guard chambers once
    // their creatures exist) can place content into the already-generated layout instead of
    // re-deriving room positions from scratch. A map with no generated hive
    // simply has an empty RoomCenters list — always present, never null,
    // same "component always exists, data may be empty" shape as
    // RM_MapComponent_LivingRegrowth.BoleCenters.
    public class RM_MapComponent_AntHive : MapComponent
    {
        // Every room center, entrance first, deepest (queen's room) last.
        public List<IntVec3> roomCenters = new List<IntVec3>();

        public bool HasHive => roomCenters.Count > 0;

        public IntVec3 EntranceRoom => roomCenters.Count > 0 ? roomCenters[0] : IntVec3.Invalid;

        public IntVec3 QueenRoom => roomCenters.Count > 0 ? roomCenters[roomCenters.Count - 1] : IntVec3.Invalid;

        // Chamber 1 of 3, the farm (RM_GenStep_AntHiveDungeon.PlaceFarm).
        // Invalid / empty on a map whose hive has no farm.
        public IntVec3 farmRoom = IntVec3.Invalid;

        public float farmHerdRadius = 5f;

        // The defenders' reaction tag (RM_AntHiveBiomeExtension.alarmTag);
        // RM_HiveSealing answers only an alarm carrying it.
        public string alarmTag;

        public List<Pawn> farmStock = new List<Pawn>();

        private const int HerdIntervalTicks = 500;

        public RM_MapComponent_AntHive(Map map) : base(map)
        {
        }

        // The ants herd: a farm animal that has strayed past farmHerdRadius
        // and is idling walks back into the farm room. An animal that is
        // dead, gone, tamed (has a faction: the player stole it back), or in
        // a mental state leaves the herd for good — the hive does not chase
        // its livestock across the map.
        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (farmStock.Count == 0 || !farmRoom.IsValid || Find.TickManager.TicksGame % HerdIntervalTicks != 0)
            {
                return;
            }

            farmStock.RemoveAll(p => p == null || p.Dead || p.Destroyed || p.Faction != null || p.Map != map);
            if (!RM_FeverWoodSettings.antHiveFarmChamberEnabled)
            {
                return;
            }

            float radiusSq = farmHerdRadius * farmHerdRadius;
            for (int i = 0; i < farmStock.Count; i++)
            {
                Pawn p = farmStock[i];
                if (!p.Spawned || p.Downed || p.InMentalState || !p.Awake() || p.jobs == null)
                {
                    continue;
                }

                if ((p.Position - farmRoom).LengthHorizontalSquared <= radiusSq)
                {
                    continue;
                }

                JobDef cur = p.CurJob?.def;
                if (cur != null && cur != JobDefOf.Wait_Wander && cur != JobDefOf.GotoWander && cur != JobDefOf.Wait)
                {
                    continue;
                }

                if (CellFinder.TryFindRandomCellNear(farmRoom, map, Mathf.Max(1, Mathf.FloorToInt(farmHerdRadius / 2f)),
                        c => c.Standable(map) && p.CanReach(c, PathEndMode.OnCell, Danger.Some), out IntVec3 cell))
                {
                    p.jobs.StartJob(JobMaker.MakeJob(JobDefOf.Goto, cell), JobCondition.InterruptForced);
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref roomCenters, "roomCenters", LookMode.Value);
            Scribe_Values.Look(ref farmRoom, "farmRoom", IntVec3.Invalid);
            Scribe_Values.Look(ref farmHerdRadius, "farmHerdRadius", 5f);
            Scribe_Values.Look(ref alarmTag, "alarmTag");
            Scribe_Collections.Look(ref farmStock, "farmStock", LookMode.Reference);
            if (roomCenters == null)
            {
                roomCenters = new List<IntVec3>();
            }
            if (farmStock == null)
            {
                farmStock = new List<Pawn>();
            }
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                farmStock.RemoveAll(p => p == null);
                if (alarmTag == null && HasHive)
                {
                    alarmTag = new RM_AntHiveBiomeExtension().alarmTag; // a hive generated before sealing existed
                }
            }
        }
    }
}
