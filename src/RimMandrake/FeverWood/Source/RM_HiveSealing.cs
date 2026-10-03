using System.Collections.Generic;
using RimMandrake.CreatureBehaviors;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_HIVE_SEALED_PASSAGES_1. The owner named "sealed doors" among
    // the signs a reacting hive must give (FEVERWOOD_ANT_HIVE_DUNGEON_1). When
    // a kurreth alarm rings (RM_ReactionEvents.AlarmAnnounced, once per
    // alarm), the hive plugs the corridor BEHIND the intruder — the one
    // between the room nearest the intruder and the room before it, toward the
    // entrance — with resin plugs. Retreat now costs a dig (or a wait: plugs
    // crumble on their own lifespan).
    //
    // Bounds: one corridor per alarm, and none if that corridor already holds
    // a plug or the intruder is still in the entrance room (they are at the
    // door; sealing it would trap nothing). Cells holding a pawn are skipped
    // rather than crushing it. Telegraph: the hive-spawn sound at the plug.
    public static class RM_HiveSealing
    {
        public const string PlugDefName = "RM_KurrethResinPlug";

        /// <summary>Plug radius around the corridor midpoint. Corridors are painted RadialCellsAround(cell, width=1), so 1.5 spans them.</summary>
        private const float PlugRadius = 1.5f;

        public static void OnAlarm(RM_ReactionEvent evt)
        {
            if (!RM_FeverWoodSettings.antHiveSealingEnabled || evt?.Map == null)
            {
                return;
            }

            RM_MapComponent_AntHive hive = evt.Map.GetComponent<RM_MapComponent_AntHive>();
            if (hive == null || !hive.HasHive || hive.alarmTag.NullOrEmpty() || evt.Tag != hive.alarmTag)
            {
                return;
            }

            Pawn intruder = evt.Instigator;
            if (intruder == null || !intruder.Spawned || intruder.Map != evt.Map)
            {
                return;
            }

            int k = NearestRoom(hive.roomCenters, intruder.Position);
            if (k <= 0)
            {
                return;
            }

            ThingDef plugDef = DefDatabase<ThingDef>.GetNamedSilentFail(PlugDefName);
            if (plugDef == null)
            {
                return;
            }

            IntVec3 a = hive.roomCenters[k - 1];
            IntVec3 b = hive.roomCenters[k];
            IntVec3 mid = new IntVec3((a.x + b.x) / 2, 0, (a.z + b.z) / 2);
            Seal(evt.Map, mid, plugDef);
        }

        /// <summary>Plugs the corridor around `mid`. Returns how many plugs were placed (0 if one is already there). Public for a proof seam.</summary>
        public static int Seal(Map map, IntVec3 mid, ThingDef plugDef)
        {
            List<IntVec3> cells = new List<IntVec3>();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(mid, PlugRadius, true))
            {
                if (!c.InBounds(map) || !c.Roofed(map))
                {
                    continue; // only the hive's own (roofed) corridor
                }

                if (c.GetFirstThing(map, plugDef) != null)
                {
                    return 0; // this corridor is already sealed
                }

                if (c.Standable(map) && c.GetFirstPawn(map) == null)
                {
                    cells.Add(c);
                }
            }

            for (int i = 0; i < cells.Count; i++)
            {
                GenSpawn.Spawn(ThingMaker.MakeThing(plugDef), cells[i], map);
            }

            if (cells.Count > 0)
            {
                SoundDef sound = DefDatabase<SoundDef>.GetNamedSilentFail("Hive_Spawn");
                sound?.PlayOneShot(SoundInfo.InMap(new TargetInfo(mid, map)));
            }
            return cells.Count;
        }

        private static int NearestRoom(List<IntVec3> rooms, IntVec3 at)
        {
            int best = -1;
            int bestD = int.MaxValue;
            for (int i = 0; i < rooms.Count; i++)
            {
                int d = (rooms[i] - at).LengthHorizontalSquared;
                if (d < bestD)
                {
                    bestD = d;
                    best = i;
                }
            }
            return best;
        }
    }
}
