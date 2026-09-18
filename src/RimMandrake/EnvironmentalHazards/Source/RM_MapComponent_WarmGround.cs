using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_WARM_MAT_1 (the Rot kit's M3, "metabolic warmth"). Opt-in per biome
    // via RM_WarmGroundExtension on the BiomeDef (see that file's header);
    // inert everywhere else, same posture as RM_MapComponent_AcceleratedRot.
    //
    // WHY A ROOM AND NOT A CELL: RimWorld has no per-cell ground temperature
    // — heat is per-room (Verse.RoomTempTracker) or outdoors, verified this
    // pass against Source/Verse/Room.cs and Source/Verse/RoomTempTracker.cs.
    // So the mechanic is room-scoped, which is also exactly how a player
    // meets it: build your room ON the mat and it is warm without a heater.
    //
    // OWNER RULING (card 3, 2026-09-17): the mat is FREE HEATING FOREVER —
    // no fuel, no upkeep, no starvation clock, and the v2 "starving mat"
    // variant is NOT to be built toward. His calibration, verbatim: "It
    // doesn't make enough to trivialize the deep deep dark. It just helps a
    // lot." The two numbers that hold him to that are the absolute cap
    // (RM_WarmGroundExtension.maxRoomTemperature, 21 °C — the mat alone never
    // reaches a comfortable 20 °C room in real cold) and the ramp cap below,
    // which is what actually decides the equilibrium of a leaky room.
    //
    // No Scribe state: everything is re-derived from live terrain and live
    // room membership every sweep, same reasoning RM_MapComponent_
    // LivingProduce gives — a load re-establishes it within one interval.
    public class RM_MapComponent_WarmGround : MapComponent
    {
        // 250 ticks — vanilla's own "rare" cadence, and the same interval
        // RM_MapComponent_AcceleratedRot sweeps on. Room temperature itself
        // only equalizes every 120 ticks (MapTemperature.MapTemperatureTick),
        // so anything faster than this would be pushing heat into a number
        // that has not moved yet.
        private const int TickInterval = 250;

        // How much of the offset the mat can deliver in ONE sweep, expressed
        // as a divisor of the configured offset: degreesPerSweep = offset /
        // ThermalPowerDivisor. This is the mechanism's actual thermal power,
        // and it — not the target — is what sets a cold room's equilibrium.
        //
        // CALIBRATED, not guessed (arithmetic from Source/Verse/
        // RoomTempTracker.cs, read this pass):
        //   wall loss per 120 ticks  = ΔT * equalizeCells * 120 * 0.00017 / cells
        //   thin-roof loss per 120 t = ΔT * 1.0 * 5e-5 * 120
        // For a square s×s enclosed, thin-roofed room, equalizeCells ≈ 4s, so
        // the loss coefficient per 250-tick sweep is
        //   (0.0816/s + 0.006) * (250/120).
        // Equilibrium is where the mat's per-sweep push equals that loss:
        //   s=5  (25 cells):  ΔT ≈ 0.5 / 0.0465 ≈ 10.8 °C over outdoor
        //   s=10 (100 cells): ΔT ≈ 0.5 / 0.0296 ≈ 16.9 °C over outdoor
        //   s=20 (400 cells): ΔT ≈ 0.5 / 0.0210 ≈ 23.8 °C → clipped by the
        //                     +18 target and the 21 °C cap
        // At the shipped offset of 18 °C this divisor yields 0.5 °C/sweep,
        // which is the middle line above: a 10×10 mat room on a −19 °C night
        // settles near −2 °C. That is "helps a lot" (a heater now has 22 °C
        // to cover instead of 39, and the mat is doing the work of roughly
        // half a campfire per 100 cells — campfire heatPerSecond=21 = 87.5
        // energy/250 ticks, the mat = 0.5 × cellCount) while emphatically not
        // "trivializes the deep deep dark": nothing on the mat alone is ever
        // a comfortable room in real cold.
        //
        // Tying the ramp to the slider rather than fixing it means the one
        // player-facing dial scales the whole mechanism coherently — target
        // AND thermal power — instead of moving a ceiling the room can never
        // reach anyway.
        private const float ThermalPowerDivisor = 36f;

        private readonly HashSet<TerrainDef> warmTerrains = new HashSet<TerrainDef>();
        private bool warmTerrainsBuilt;

        public RM_MapComponent_WarmGround(Map map)
            : base(map)
        {
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!RM_EnvironmentalHazardsSettings.warmGroundEnabled)
            {
                return;
            }

            RM_WarmGroundExtension ext = map.Biome?.GetModExtension<RM_WarmGroundExtension>();
            if (ext == null)
            {
                return;
            }

            if (Find.TickManager.TicksGame % TickInterval != 0)
            {
                return;
            }

            float offset = RM_EnvironmentalHazardsSettings.warmGroundOffsetCelsius;
            if (offset <= 0f)
            {
                return;
            }

            BuildTerrainSet(ext);
            if (warmTerrains.Count == 0)
            {
                return;
            }

            HeatMatFlooredRooms(ext, offset);
        }

        private void BuildTerrainSet(RM_WarmGroundExtension ext)
        {
            if (warmTerrainsBuilt)
            {
                return;
            }

            warmTerrainsBuilt = true;
            if (ext.warmTerrains == null)
            {
                return;
            }

            for (int i = 0; i < ext.warmTerrains.Count; i++)
            {
                TerrainDef t = ext.warmTerrains[i];
                if (t != null)
                {
                    warmTerrains.Add(t);
                }
            }
        }

        private void HeatMatFlooredRooms(RM_WarmGroundExtension ext, float offset)
        {
            float outdoor = map.mapTemperature.OutdoorTemp;
            float target = Mathf.Min(outdoor + offset, ext.maxRoomTemperature);
            float maxStep = offset / ThermalPowerDivisor;

            IReadOnlyList<Room> rooms = map.regionGrid.AllRooms;
            for (int i = 0; i < rooms.Count; i++)
            {
                Room room = rooms[i];
                if (room == null || room.Dereferenced || room.IsDoorway)
                {
                    continue;
                }

                // PushHeat itself refuses an outdoor room (Room.PushHeat
                // returns false when UsesOutdoorTemperature) — test it here
                // too so the per-cell terrain scan below is never spent on
                // the map's one enormous outdoor room. ProperRoom is the
                // "enclosed, not map-edge, real interior" test.
                if (room.UsesOutdoorTemperature || !room.ProperRoom || room.Fogged)
                {
                    continue;
                }

                int cellCount = room.CellCount;
                if (cellCount <= 0)
                {
                    continue;
                }

                // Nothing to give: the room is already at or above where the
                // mat would hold it. Checked before the terrain scan, so a
                // warm base costs nothing per sweep.
                float current = room.Temperature;
                if (current >= target)
                {
                    continue;
                }

                if (!IsMatFloored(room, ext, cellCount))
                {
                    continue;
                }

                float step = Mathf.Min(target - current, maxStep);
                if (step <= 0f)
                {
                    continue;
                }

                // Room.PushHeat divides by CellCount, so multiply back: the
                // mat is an area source — a bigger mat room really is fed by
                // more living ground.
                room.PushHeat(step * cellCount);
            }
        }

        private bool IsMatFloored(Room room, RM_WarmGroundExtension ext, int cellCount)
        {
            int needed = Mathf.CeilToInt(cellCount * ext.requiredFloorFraction);
            if (needed <= 0)
            {
                needed = 1;
            }

            int mat = 0;
            int scanned = 0;
            TerrainGrid grid = map.terrainGrid;
            foreach (IntVec3 cell in room.Cells)
            {
                scanned++;
                if (warmTerrains.Contains(grid.TerrainAt(cell)))
                {
                    mat++;
                    if (mat >= needed)
                    {
                        return true;
                    }
                }
                else if (scanned - mat > cellCount - needed)
                {
                    // Already too many dead-floor cells for the threshold to
                    // be reachable — stop scanning this room.
                    return false;
                }
            }

            return mat >= needed;
        }
    }
}


