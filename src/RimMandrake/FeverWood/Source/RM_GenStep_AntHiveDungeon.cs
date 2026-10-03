using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_ANT_HIVE_DUNGEON_1. Owner ruling 2026-09-22: ant hives are
    // "dungeons in their own right (procedural are fine, not plot based)".
    // `dungeons_arc_spec.md` was read this pass and provides no runtime
    // layout generation at all — its two dungeons (Assailant complex, the
    // Forsaken vaults) are FIXED, plot-bearing sites hand-authored via KCSG
    // StructureLayoutDefs, drafted by an agent/human and placed once. This
    // class is the genuinely new piece: an algorithmic, non-plot layout that
    // varies every time it fires, occasionally, on an ordinary Fever Wood map
    // — same GenStep idiom as RM_GenStep_RootCauseways/RM_GenStep_ScatterPools
    // (BiomeDef-modExtension-gated, no-op elsewhere), reusing their
    // anchor-chain-then-connect shape rather than inventing a new one.
    //
    // What this builds: a chain of `roomCountRange` roomsi, each a radial
    // blob, linked room-to-room by a straight corridor, all roofed so the
    // whole thing reads as a dug-out enclosure — then populates every
    // non-entrance room with workers and the last (deepest) room with one
    // queen. See RM_AntHiveBiomeExtension's own header for what is
    // deliberately NOT built here (the parasite and guard chambers) and why.
    public class RM_GenStep_AntHiveDungeon : GenStep
    {
        private static readonly IntVec3[] EightDirs =
        {
            new IntVec3(1, 0, 0), new IntVec3(1, 0, 1), new IntVec3(0, 0, 1), new IntVec3(-1, 0, 1),
            new IntVec3(-1, 0, 0), new IntVec3(-1, 0, -1), new IntVec3(0, 0, -1), new IntVec3(1, 0, -1),
        };

        public override int SeedPart => 1758952022;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_FeverWoodSettings.antHiveDungeonEnabled)
            {
                return; // MOD_OPTIONS_RETROFIT_1: WORLDGEN-AFFECTING master toggle
            }

            RM_AntHiveBiomeExtension ext = map.Biome?.GetModExtension<RM_AntHiveBiomeExtension>();
            if (ext == null)
            {
                return;
            }

            if (ext.workerKind == null || ext.queenKind == null)
            {
                Log.Error("[RM FeverWood] RM_GenStep_AntHiveDungeon: biome " + map.Biome.defName
                    + "'s RM_AntHiveBiomeExtension is missing workerKind/queenKind — skipping.");
                return;
            }

            float chance = Mathf.Clamp01(ext.hiveChance * RM_FeverWoodSettings.antHiveChanceMultiplier);
            if (!Rand.Chance(chance))
            {
                return; // most maps carry no hive at all — this is meant to be a rare find
            }

            RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();

            if (!TryFindAnchor(map, ext, tenant, out IntVec3 start))
            {
                Log.Warning("[RM FeverWood] RM_GenStep_AntHiveDungeon: no valid starting site found on "
                    + map.Biome.defName + " — hive skipped this map.");
                return;
            }

            List<IntVec3> rooms = BuildRoomChain(map, ext, tenant, start);
            if (rooms.Count == 0)
            {
                return;
            }

            RoofDef roof = ext.hiveRoofDef ?? RoofDefOf.RoofRockThin;
            for (int i = 0; i < rooms.Count; i++)
            {
                PaintRoom(map, rooms[i], ext.roomRadiusRange.RandomInRange, roof, ext.hiveFloorTerrain);
                if (i > 0)
                {
                    PaintCorridor(map, rooms[i - 1], rooms[i], ext.corridorWidth, roof, ext.hiveFloorTerrain);
                }
            }

            RM_MapComponent_AntHive hiveComp = map.GetComponent<RM_MapComponent_AntHive>();
            if (hiveComp != null)
            {
                hiveComp.roomCenters.AddRange(rooms);
                hiveComp.alarmTag = ext.alarmTag;
            }

            Populate(map, ext, rooms);
            PlaceFarm(map, ext, rooms);

            Log.Message("[RM FeverWood] RM_GenStep_AntHiveDungeon: placed a " + rooms.Count
                + "-room ant hive on " + map.Biome.defName + " at " + start + ".");
        }

        // Same rejection-sampling shape as RM_GenStep_ScatterPools.TryFindSite.
        private bool TryFindAnchor(Map map, RM_AntHiveBiomeExtension ext, RUT_MapComponent_TheTenant tenant, out IntVec3 result)
        {
            for (int attempt = 0; attempt < ext.placementAttempts; attempt++)
            {
                IntVec3 candidate = CellFinder.RandomCell(map);
                if (candidate.x < ext.edgeMargin || candidate.z < ext.edgeMargin
                    || candidate.x >= map.Size.x - ext.edgeMargin
                    || candidate.z >= map.Size.z - ext.edgeMargin)
                {
                    continue;
                }

                if (!candidate.Standable(map))
                {
                    continue;
                }

                if (tenant != null && ext.minDistanceFromRegisteredWater > 0f
                    && tenant.IsRegisteredWater(candidate))
                {
                    continue;
                }

                result = candidate;
                return true;
            }

            result = IntVec3.Invalid;
            return false;
        }

        // A random walk of room centers, each a bounded hop from the last —
        // the same "anchor chain" idiom RM_GenStep_RootCauseways uses for its
        // splines, but building a chain of discrete rooms rather than a
        // continuous lane. Degrades gracefully: a room whose hop lands
        // out-of-bounds or too close to registered water after several
        // attempts simply ends the chain there, rather than looping forever.
        private List<IntVec3> BuildRoomChain(Map map, RM_AntHiveBiomeExtension ext, RUT_MapComponent_TheTenant tenant, IntVec3 start)
        {
            List<IntVec3> rooms = new List<IntVec3> { start };
            int targetCount = ext.roomCountRange.RandomInRange;

            while (rooms.Count < targetCount)
            {
                IntVec3 prev = rooms[rooms.Count - 1];
                bool placed = false;

                for (int attempt = 0; attempt < ext.placementAttempts; attempt++)
                {
                    IntVec3 dir = EightDirs[Rand.Range(0, EightDirs.Length)];
                    float hop = ext.corridorHopRange.RandomInRange;
                    IntVec3 candidate = new IntVec3(
                        prev.x + Mathf.RoundToInt(dir.x * hop),
                        0,
                        prev.z + Mathf.RoundToInt(dir.z * hop));

                    if (candidate.x < ext.edgeMargin || candidate.z < ext.edgeMargin
                        || candidate.x >= map.Size.x - ext.edgeMargin
                        || candidate.z >= map.Size.z - ext.edgeMargin)
                    {
                        continue;
                    }

                    if (!candidate.InBounds(map))
                    {
                        continue;
                    }

                    if (tenant != null && ext.minDistanceFromRegisteredWater > 0f
                        && tenant.IsRegisteredWater(candidate))
                    {
                        continue;
                    }

                    rooms.Add(candidate);
                    placed = true;
                    break;
                }

                if (!placed)
                {
                    break; // fewer rooms than targeted is fine — a shorter hive, not a failed one
                }
            }

            return rooms;
        }

        private void PaintRoom(Map map, IntVec3 center, float radius, RoofDef roof, TerrainDef floor)
        {
            foreach (IntVec3 c in GenRadial.RadialCellsAround(center, radius, true))
            {
                if (!c.InBounds(map))
                {
                    continue;
                }

                map.roofGrid.SetRoof(c, roof);
                if (floor != null)
                {
                    map.terrainGrid.SetTerrain(c, floor);
                }
            }
        }

        // Same line-connect idiom as RM_GenStep_RootCauseways.ConnectAnchors.
        private void PaintCorridor(Map map, IntVec3 a, IntVec3 b, int width, RoofDef roof, TerrainDef floor)
        {
            float dx = b.x - a.x;
            float dz = b.z - a.z;
            float dist = Mathf.Sqrt(dx * dx + dz * dz);
            if (dist < 1f)
            {
                return;
            }
            dx /= dist;
            dz /= dist;

            int steps = Mathf.CeilToInt(dist);
            for (int i = 0; i <= steps; i++)
            {
                IntVec3 cell = new IntVec3(Mathf.RoundToInt(a.x + dx * i), 0, Mathf.RoundToInt(a.z + dz * i));
                foreach (IntVec3 c in GenRadial.RadialCellsAround(cell, width, true))
                {
                    if (!c.InBounds(map))
                    {
                        continue;
                    }

                    map.roofGrid.SetRoof(c, roof);
                    if (floor != null)
                    {
                        map.terrainGrid.SetTerrain(c, floor);
                    }
                }
            }
        }

        // Chamber 1 of 3, the farm: the shallowest worker room keeps a calm,
        // wild herd of `farmKind` (thornbugs) that the hive's map component
        // herds back whenever one strays. Needs at least entrance + farm +
        // queen rooms, so a 2-room hive carries no farm.
        private static void PlaceFarm(Map map, RM_AntHiveBiomeExtension ext, List<IntVec3> rooms)
        {
            if (ext.farmKind == null || !RM_FeverWoodSettings.antHiveFarmChamberEnabled || rooms.Count < 3)
            {
                return;
            }

            RM_MapComponent_AntHive hive = map.GetComponent<RM_MapComponent_AntHive>();
            if (hive == null)
            {
                return;
            }

            IntVec3 farm = rooms[1];
            hive.farmRoom = farm;
            hive.farmHerdRadius = ext.farmHerdRadius;
            int count = ext.farmStockRange.RandomInRange;
            for (int j = 0; j < count; j++)
            {
                if (!CellFinder.TryFindRandomCellNear(farm, map, 3, c => c.Standable(map), out IntVec3 cell))
                {
                    continue;
                }

                Pawn stock = PawnGenerator.GeneratePawn(ext.farmKind, null);
                if (stock == null)
                {
                    continue;
                }

                GenSpawn.Spawn(stock, cell, map);
                hive.farmStock.Add(stock);
            }
        }

        // REACTION_MECHANISM_GENERALISE_1 step 3. A defender whose race
        // carries the shared reaction source (RM_Kurreth does) is placed CALM
        // and tethered to its room: it notices an intruder, rings the alarm,
        // and the alarm rallies the hive — the reacting dungeon the owner
        // chose. A race without that comp falls back to the v1 behaviour
        // (spawned Manhunter), so a content swap can never leave a hive that
        // ignores intruders entirely.
        private static void SettleDefender(Pawn pawn, IntVec3 room)
        {
            if (pawn.TryGetComp<RimMandrake.CreatureBehaviors.RM_CompReactionSource>() != null)
            {
                pawn.TryGetComp<RimMandrake.CreatureBehaviors.RM_CompHomeTether>()?.SetHome(room);
                return;
            }

            pawn.mindState?.mentalStateHandler?.TryStartMentalState(
                MentalStateDefOf.Manhunter, reason: "Ant hive defender", forceWake: true, causedByMood: false);
        }

        // Wild, faction-less defenders: every non-entrance room gets workers,
        // the deepest gets the queen and an escort; SettleDefender decides
        // calm-and-reacting vs v1 Manhunter per race.
        private void Populate(Map map, RM_AntHiveBiomeExtension ext, List<IntVec3> rooms)
        {
            for (int i = 1; i < rooms.Count; i++)
            {
                bool isQueenRoom = i == rooms.Count - 1;
                int count = isQueenRoom ? 1 : ext.workersPerRoomRange.RandomInRange;
                PawnKindDef kind = isQueenRoom ? ext.queenKind : ext.workerKind;

                for (int j = 0; j < count; j++)
                {
                    if (!CellFinder.TryFindRandomCellNear(rooms[i], map, 3,
                        c => c.Standable(map), out IntVec3 spawnCell))
                    {
                        continue;
                    }

                    Pawn pawn = PawnGenerator.GeneratePawn(kind, null);
                    if (pawn == null)
                    {
                        continue;
                    }

                    GenSpawn.Spawn(pawn, spawnCell, map);
                    SettleDefender(pawn, rooms[i]);
                }

                if (isQueenRoom)
                {
                    // one extra worker escort in the queen's room, per the roster's
                    // own "hive castes as plain-modifier variants" framing — the
                    // queen is never alone.
                    for (int j = 0; j < ext.workersPerRoomRange.min; j++)
                    {
                        if (!CellFinder.TryFindRandomCellNear(rooms[i], map, 3,
                            c => c.Standable(map), out IntVec3 spawnCell))
                        {
                            continue;
                        }

                        Pawn escort = PawnGenerator.GeneratePawn(ext.workerKind, null);
                        if (escort == null)
                        {
                            continue;
                        }

                        GenSpawn.Spawn(escort, spawnCell, map);
                        SettleDefender(escort, rooms[i]);
                    }
                }
            }
        }
    }
}
