using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // CHILL_THERMAL_ENGINE_1 — the boil shroud.
    //
    // Owner (2026-09-27, typed verbatim): "There should be bubbling
    // animations surrounding the hot ship boiling the propane simply by
    // being normal temperature." And, on the second, smaller half: "Any
    // warm thing OUTSIDE the ship (a working pawn, a powered lamp, a
    // heater) carries its own SMALLER shimmer/boil effect around it too —
    // the player's own presence and activity should read as a visible
    // disturbance in the medium before they've built or triggered
    // anything."
    //
    // SCOPE: RM_ChillFireGate.IsChillSeabedMap(map) only — see that file's
    // header for why a bare biome-defName check cannot tell the seabed from
    // the surface Chill (both carry biome RM_TheChill).
    //
    // ⚠️ WHY "LIQUID-TERRAIN CELLS" READS AS "ANY OUTDOOR FLOOR CELL" HERE,
    // NOT A LITERAL WATER TERRAIN. GenStep_SeaFloorTerrain paints the WHOLE
    // pocket-map floor as the walkable RM_SeaFloorGround, never the
    // biome's own water terrain — its own header explains why: the real
    // waterDeepTerrain is Impassable, "correct for the SURFACE tile, wrong
    // for a floor pocket map a weighted-belt diver is meant to walk." A
    // diver down here is fictionally standing on the BOTTOM of the lake,
    // fully submerged, not beside it — every outdoor cell on this map
    // already IS "the liquid" in the sense the ruling means. Scattering a
    // literal pool terrain (the Grey Sea's brine-pool shape,
    // GenStep_GreySeaFloorDressing) would be new art/terrain this item
    // never asked for, and would introduce exactly the kind of ZONE the
    // cooling-severity ruling explicitly declined ("no gentle shallows, no
    // zones"). Assumption recorded here per FOUNDRY's "specs state
    // outcomes" rule — implement a better route, say what you assumed.
    //
    // TWO TRIGGERS, TWO SIZES. Grade 1 = small warm-thing shimmer, grade 2
    // = larger hull boil; hull always wins where both would mark one cell
    // (SetGrade only ever raises the grade).
    //   HULL  — an outdoor cell on this room's own BorderCellsCardinal (the
    //           engine's own "just outside this room" set, Verse/Room.cs),
    //           for any ENCLOSED room (!UsesOutdoorTemperature &&
    //           !PsychologicallyOutdoors) whose Room.Temperature has
    //           cleared HullWarmThresholdC — "simply by being normal
    //           temperature," not by hitting some engineered ideal.
    //   THING — an outdoor cell within ThingRadius of a live spawned pawn,
    //           or of a spawned Thing with an active CompPowerTrader (a
    //           "powered lamp, a heater" — any switched-on electrical
    //           device), matching the ruling's own three examples exactly.
    //
    // VISUAL: reuses FleckMaker.ThrowSmoke — the exact call
    // MapComponent_GasSaturationTracker's HazeVisualTick already uses in
    // this same campaign for "gas escaping a liquid" (PropaneLakeMechanics,
    // RimUtinni tier). No new FleckDef, no new art. The camera-sampled,
    // cost-bounded recurring-fleck architecture below (rescan a grade grid,
    // then sample a few cells from the current view each tick) is
    // RM_MapComponent_WaterAgitation's own idiom, copied because it is
    // already the shape this codebase uses for "a fleck the player can
    // actually see, without spawning across an unwatched map."
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ChillBoilShroud : MapComponent
    {
        // Pawn/device positions move; BrineCrystallisation (the other
        // pawn-position sweep on this same map family) uses the same 60-
        // tick cadence for the same reason — cheap on a small pocket map,
        // and tight enough that a moving pawn's shimmer visibly follows it.
        private const int RescanIntervalTicks = 60;
        private const int SamplesPerTick = 3;

        // "Normal (non-cryogenic) temperature" — well above the map's own
        // -110 ambient (RM_SeaDiveGenerators.xml), but not an engineered
        // ideal-comfort bar either: ANY room that has genuinely fought the
        // cold back counts as boiling the hull beside it.
        private const float HullWarmThresholdC = -20f;

        private const float ThingRadius = 1.9f;

        private const float HullBoilChance = 0.14f;
        private const float ThingBoilChance = 0.05f;

        private const float HullBoilSizeMin = 0.5f;
        private const float HullBoilSizeMax = 0.9f;
        private const float ThingBoilSizeMin = 0.22f;
        private const float ThingBoilSizeMax = 0.4f;

        // 0 none, 1 warm-thing shimmer, 2 hull boil. Byte-per-cell, same
        // storage shape as RM_MapComponent_WaterAgitation's own grade grid.
        private byte[] grade;
        private bool anyBoiling;
        private bool isChillSeabed;
        private int ticksUntilRescan = 1;

        public RM_MapComponent_ChillBoilShroud(Map map) : base(map)
        {
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            isChillSeabed = RM_ChillFireGate.IsChillSeabedMap(map);
            if (isChillSeabed)
            {
                Rebuild();
            }
            ticksUntilRescan = RescanIntervalTicks;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();

            if (!isChillSeabed)
            {
                return; // every other map in the game: one bool check, nothing else
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.chillBoilShroudEnabled)
            {
                return;
            }

            if (--ticksUntilRescan <= 0)
            {
                ticksUntilRescan = RescanIntervalTicks;
                Rebuild();
            }

            if (!anyBoiling || map != Find.CurrentMap)
            {
                return; // cosmetic-only; a fleck the player cannot see is waste (same rule WaterAgitation follows)
            }

            CameraDriver camera = Find.CameraDriver;
            if (camera == null)
            {
                return;
            }
            CellRect view = camera.CurrentViewRect;
            view.ClipInsideMap(map);
            if (view.Width <= 0 || view.Height <= 0)
            {
                return;
            }

            for (int i = 0; i < SamplesPerTick; i++)
            {
                IntVec3 cell = new IntVec3(
                    Rand.RangeInclusive(view.minX, view.maxX), 0,
                    Rand.RangeInclusive(view.minZ, view.maxZ));

                byte g = grade[map.cellIndices.CellToIndex(cell)];
                if (g == 0 || cell.Fogged(map))
                {
                    continue;
                }

                bool hull = g == 2;
                if (!Rand.Chance(hull ? HullBoilChance : ThingBoilChance))
                {
                    continue;
                }

                float size = hull
                    ? Rand.Range(HullBoilSizeMin, HullBoilSizeMax)
                    : Rand.Range(ThingBoilSizeMin, ThingBoilSizeMax);

                Vector3 loc = cell.ToVector3Shifted();
                loc.x += Rand.Range(-0.35f, 0.35f);
                loc.z += Rand.Range(-0.35f, 0.35f);
                FleckMaker.ThrowSmoke(loc, map, size);
            }
        }

        private void Rebuild()
        {
            int area = map.Area;
            if (grade == null || grade.Length != area)
            {
                grade = new byte[area];
            }
            else
            {
                Array.Clear(grade, 0, grade.Length);
            }
            anyBoiling = false;

            MarkHullAdjacent();
            MarkWarmThings();
        }

        private void MarkHullAdjacent()
        {
            IReadOnlyList<Room> rooms = map.regionGrid.AllRooms;
            for (int i = 0; i < rooms.Count; i++)
            {
                Room room = rooms[i];
                if (room == null || room.UsesOutdoorTemperature || room.PsychologicallyOutdoors)
                {
                    continue; // only an ENCLOSED, actually-heated room counts as "the hull"
                }
                if (room.Temperature < HullWarmThresholdC)
                {
                    continue;
                }
                foreach (IntVec3 c in room.BorderCellsCardinal)
                {
                    if (!c.InBounds(map) || c.Roofed(map) || !c.Standable(map))
                    {
                        continue; // roofed border = a doorway into another room, not open lake
                    }
                    SetGrade(c, 2);
                }
            }
        }

        private void MarkWarmThings()
        {
            IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || !p.Spawned || p.Position.Roofed(map))
                {
                    continue; // sheltered indoors already reads calm, not a disturbance in the open lake
                }
                MarkRadius(p.Position);
            }

            List<Thing> powered = map.listerThings.ThingsInGroup(ThingRequestGroup.PowerTrader);
            for (int i = 0; i < powered.Count; i++)
            {
                Thing t = powered[i];
                if (t == null || !t.Spawned || t.Position.Roofed(map))
                {
                    continue;
                }
                CompPowerTrader power = t.TryGetComp<CompPowerTrader>();
                if (power != null && power.PowerOn)
                {
                    MarkRadius(t.Position);
                }
            }
        }

        private void MarkRadius(IntVec3 centre)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(centre, ThingRadius, true))
            {
                if (!c.InBounds(map) || c.Roofed(map) || !c.Standable(map))
                {
                    continue;
                }
                SetGrade(c, 1);
            }
        }

        private void SetGrade(IntVec3 c, byte g)
        {
            int idx = map.cellIndices.CellToIndex(c);
            if (grade[idx] < g)
            {
                grade[idx] = g;
            }
            anyBoiling = true;
        }
    }
}
