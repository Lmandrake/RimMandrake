using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SCALD_IMMERSION_BERTH_1 — the Scald's ship-touch voice (owner sitting 2026-10-02, Q2).
    // A parked ship's rooms slowly heat. The heat load scales with a room's hull border, so a
    // compact ship is cheap to cool and a sprawling one is not. It uses vanilla room temperature,
    // vanilla coolers and vanilla power. It NEVER seals doors and NEVER gates launch: this
    // component touches nothing but room temperature.
    //
    // Scope: the Scald sea floor only (planet-layer floor biome, or the retiring hatch pocket map).
    // Every other map pays one cached bool per tick.
    public class RM_MapComponent_ScaldImmersionBerth : MapComponent
    {
        private const int SweepInterval = 250;
        private const int RampTicks = 15000;                // 6 game hours to full load
        private const float HeatPerBorderCellPerTick = 0.04f; // at intensity 1, full ramp

        private int heatingSince = -1;
        private bool messaged;
        private bool isScaldFloor;

        public RM_MapComponent_ScaldImmersionBerth(Map map) : base(map)
        {
        }

        public static bool IsScaldFloorMap(Map map)
        {
            string b = map?.Biome?.defName;
            if (b == "RM_SeabedFloor_TheScald")
            {
                return true;
            }
            return b == "RM_TheScald" && map.IsPocketMap;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref heatingSince, "scaldBerthHeatingSince", -1);
            Scribe_Values.Look(ref messaged, "scaldBerthMessaged", false);
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isScaldFloor = IsScaldFloorMap(map);
        }

        /// <summary>0..1 ramp for a given game tick; -1 start means not heating.</summary>
        public static float Ramp(int since, int now)
        {
            if (since < 0)
            {
                return 0f;
            }
            float r = (now - since) / (float)RampTicks;
            return r < 0f ? 0f : (r > 1f ? 1f : r);
        }

        public override void MapComponentTick()
        {
            if (!isScaldFloor || Find.TickManager.TicksGame % SweepInterval != 0)
            {
                return;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.scaldBerthEnabled)
            {
                return;
            }

            int now = Find.TickManager.TicksGame;
            bool anyRoom = false;
            HashSet<Room> seen = new HashSet<Room>();
            IReadOnlyList<Room> rooms = map.regionGrid.AllRooms;
            for (int i = 0; i < rooms.Count; i++)
            {
                Room room = rooms[i];
                if (room == null || !seen.Add(room) || !room.ProperRoom || room.UsesOutdoorTemperature
                    || room.PsychologicallyOutdoors || room.CellCount == 0)
                {
                    continue;
                }
                anyRoom = true;
                if (heatingSince < 0)
                {
                    heatingSince = now;
                }
                float ramp = Ramp(heatingSince, now);
                int border = room.BorderCellsCardinal.Count();
                float energy = border * HeatPerBorderCellPerTick * SweepInterval
                    * RM_DivingSettings.scaldBerthIntensity * ramp;
                if (energy > 0f)
                {
                    GenTemperature.PushHeat(room.Cells.First(), map, energy);
                }
            }

            if (!anyRoom)
            {
                heatingSince = -1;
                messaged = false;
            }
            else if (!messaged && Ramp(heatingSince, now) > 0.1f)
            {
                messaged = true;
                Messages.Message("The Scald presses in: the ship's rooms are slowly warming. A compact hull is easier to keep cool.",
                    MessageTypeDefOf.NeutralEvent, false);
            }
        }
    }
}
