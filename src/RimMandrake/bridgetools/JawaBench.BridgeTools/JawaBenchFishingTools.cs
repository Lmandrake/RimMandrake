// JawaBenchFishingTools.cs - read a fishing zone and its water body, and dry-roll a catch.
//
// Written for POND_DEPTH_BUILD_SHALLOWS_BEFORE_MUD A7 ("fishing on a dug reservoir"), which
// design/RimMandrake/flowworks_live_session_plan_2026-10-18.md listed as UNMEASURED because no
// bridge tool made or read a fishing zone. The zone itself is made by map_zones
// (zoneType='fishing'); a REAL catch is a colonist running JobDefOf.Fish through ordered_job with
// targetA = fishCell and targetB = standSpot, both of which this tool's read returns. Every API
// below was read from 1.6 source (RimSage): Zone_Fishing, WaterBody, WaterBodyTracker,
// FishingUtility.GetCatchesFor, WorkGiver_Fish.BestStandSpotFor, JobDriver_Fish.
//
// THREAD AFFINITY: everything that touches game state is inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/fishing",
            Description =
                "Read a fishing zone and the water body under it, or DRY-ROLL catches. " +
                "action='read': give a zone label OR a cell x/z. Returns the WaterBody (type, size, " +
                "population, maxPopulation, hasFish, commonFish, uncommonFish, frozen cells) read from " +
                "the raw tracker, the Zone_Fishing at that cell (or the named one) with shouldFishNow and " +
                "the vanilla reason it would NOT fish (under target population, forbidden, over target " +
                "count, paused, frozen, blocked), and fishOnMap (every Fish-group stack on the map, so a " +
                "caller diffs it before and after a job). With pawn given it also returns fishCell + " +
                "standSpot from WorkGiver_Fish.BestStandSpotFor and the job length (7500 / FishingSpeed): " +
                "order the real catch with the ordered-job tool, jobDef Fish, targetA = fishCell, " +
                "targetB = standSpot. A cell with no water body reads hasBody=false - never a fake zero. " +
                "action='roll' (needs pawn): calls FishingUtility.GetCatchesFor rolls times. DRY: nothing " +
                "is spawned and population does not move, but it CONSUMES Rand, and it skips the 2% " +
                "negative-outcome roll the real job makes first. A roll is not a catch: the A7 bar is a job.",
            ResultDescription =
                "success, body{hasBody,type,size,population,maxPopulation,populationPct,hasFish,commonFish," +
                "uncommonFish,numCellsFrozen,numCellsCanFreeze,pollutionPct}, zone{label,cells,fishableCells," +
                "fishType,allowed,shouldFishNow,whyNot,ownedFishCount,...} or null, fishOnMap[{def,count}], " +
                "fishTotal, and with pawn: fishCell, standSpot, jobTicks; for roll: rolls[{catches[{def,count}],rare}].")]
        public static async Task<object> Fishing(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'read' or 'roll'.")] string action = "read",
            [ToolParameter(Description = "Fishing zone label (or give x/z).")] string zone = null,
            [ToolParameter(Description = "Cell x (or give zone).", DefaultValue = -1)] int x = -1,
            [ToolParameter(Description = "Cell z (or give zone).", DefaultValue = -1)] int z = -1,
            [ToolParameter(Description = "Pawn id/name: adds fishCell/standSpot/jobTicks to read; required for roll.")] string pawn = null,
            [ToolParameter(Description = "roll only: how many dry rolls, 1-50.", DefaultValue = 10)] int rolls = 10)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (!ModsConfig.OdysseyActive) return Fail("Fishing is an Odyssey system and Odyssey is not active.");
                var A = (action ?? "read").Trim().ToLowerInvariant();
                if (A != "read" && A != "roll") return Fail("action must be 'read' or 'roll', got '" + action + "'.");

                // ---- resolve the zone / cell ---------------------------------------------------
                Zone_Fishing fz = null;
                IntVec3 cell = IntVec3.Invalid;
                if (!string.IsNullOrEmpty(zone))
                {
                    var hits = map.zoneManager.AllZones.OfType<Zone_Fishing>()
                        .Where(q => string.Equals(q.label, zone.Trim(), StringComparison.OrdinalIgnoreCase)).ToList();
                    if (hits.Count == 0)
                        return Fail("No fishing zone labelled '" + zone + "'.",
                            new { fishingZones = map.zoneManager.AllZones.OfType<Zone_Fishing>().Select(q => q.label).ToList() });
                    if (hits.Count > 1) return Fail(hits.Count + " fishing zones share the label '" + zone + "'; give a cell x/z instead.");
                    fz = hits[0];
                    if (fz.Cells.Count == 0) return Fail("Fishing zone '" + zone + "' has no cells.");
                    cell = fz.Cells[0];
                }
                else
                {
                    if (x < 0 || z < 0) return Fail("Give a zone label or a cell x/z.");
                    cell = new IntVec3(x, 0, z);
                    if (!cell.InBounds(map)) return Fail("Cell " + x + "," + z + " is outside the map.");
                    fz = map.zoneManager.ZoneAt(cell) as Zone_Fishing;
                }

                // ---- the water body, raw ------------------------------------------------------
                var wb = map.waterBodyTracker.WaterBodyAt(cell);
                object body = wb == null
                    ? (object)new { hasBody = false, cell = new { x = cell.x, z = cell.z }, terrain = cell.GetTerrain(map)?.defName,
                                    waterBodyType = cell.GetWaterBodyType(map).ToString() }
                    : new
                    {
                        hasBody = true, type = wb.waterBodyType.ToString(),
                        rootCell = new { x = wb.rootCell.x, z = wb.rootCell.z },
                        size = wb.Size, trackedCells = wb.cells.Count,
                        population = wb.Population, maxPopulation = wb.MaxPopulation,
                        populationPct = wb.MaxPopulation > 0f ? wb.Population / wb.MaxPopulation : 0f,
                        populationFactor = wb.PopulationFactor,
                        hasFish = wb.HasFish,
                        commonFish = wb.CommonFish.Where(d => d != null).Select(d => d.defName).ToList(),
                        uncommonFish = wb.UncommonFish.Where(d => d != null).Select(d => d.defName).ToList(),
                        numCellsFrozen = wb.numCellsFrozen, numCellsCanFreeze = wb.numCellsCanFreeze,
                        pollutionPct = wb.Size > 0 ? wb.PollutionPct : 0f,
                    };

                // ---- fish on the map (diff this around a job) ----------------------------------
                var fishThings = map.listerThings.ThingsInGroup(ThingRequestGroup.Fish);
                var fishOnMap = fishThings.GroupBy(t => t.def.defName)
                    .Select(g => new { def = g.Key, count = g.Sum(t => t.stackCount), stacks = g.Count() }).ToList();
                int fishTotal = fishThings.Sum(t => t.stackCount);

                // ---- the zone, with the vanilla why-not (Zone_Fishing.ShouldFishNow's order) ----
                object zoneOut = null;
                if (fz != null)
                {
                    float popPct = map.waterBodyTracker.PopulationPercentAt(fz.Cells[0]);
                    bool overTargetPop = !(map.TileInfo.MaxFishPopulation <= 0f || fz.Cells.Count == 0 || fz.FishType == WaterBodyType.None)
                                         && popPct > fz.targetPopulationPct;
                    int owned = fz.OwnedFishCount;
                    bool underTargetCount =
                        fz.repeatMode == FishRepeatMode.DoForever ? true :
                        fz.repeatMode == FishRepeatMode.TargetCount ? owned < fz.targetCount :
                        fz.repeatMode == FishRepeatMode.RepeatCount ? fz.repeatCount > 0 : owned < fz.repeatCount;
                    int fishable = fz.FishbleCells.Count;
                    string whyNot = null;
                    if (!fz.ShouldFishNow)
                    {
                        if (!overTargetPop) whyNot = map.TileInfo.MaxFishPopulation <= 0f
                            ? "this tile's MaxFishPopulation is 0" : "under target population (" + popPct.ToString("F2") + " <= " + fz.targetPopulationPct + ")";
                        else if (!fz.Allowed) whyNot = "forbidden (allowed=false)";
                        else if (!underTargetCount) whyNot = "over target fish count (" + owned + " >= " + fz.targetCount + ")";
                        else if (fz.PausedDueToResourceCount) whyNot = "paused due to resource count";
                        else whyNot = "ShouldFishNow false for a reason this read does not know";
                    }
                    else if (fishable == 0) whyNot = fz.AllFishableCellsFrozen ? "every fishable cell is frozen" : "no fishable cell (blocked)";
                    zoneOut = new
                    {
                        label = fz.label, cells = fz.Cells.Count, fishableCells = fishable,
                        fishType = fz.FishType.ToString(), allowed = fz.Allowed,
                        repeatMode = fz.repeatMode.ToString(), targetCount = fz.targetCount, repeatCount = fz.repeatCount,
                        targetPopulationPct = fz.targetPopulationPct, populationPctAtZone = popPct,
                        overTargetPopulation = overTargetPop, ownedFishCount = owned,
                        shouldFishNow = fz.ShouldFishNow, whyNot,
                        allFishableCellsFrozen = fz.AllFishableCellsFrozen,
                    };
                }

                // ---- pawn: stand spot / job length / rolls -------------------------------------
                Pawn p = null;
                if (!string.IsNullOrEmpty(pawn))
                {
                    string perr; p = FindPawn(pawn, out perr);
                    if (p == null) return Fail(perr);
                    if (!p.Spawned || p.Map != map) return Fail("Pawn '" + pawn + "' is not spawned on the current map.");
                }
                if (A == "roll" && p == null) return Fail("action 'roll' needs a pawn (GetCatchesFor reads its FishingYield and map).");

                object fishCellOut = null, standOut = null; int? jobTicks = null; float? speed = null; string spotWhy = null;
                if (p != null)
                {
                    IntVec3 fc = IntVec3.Invalid, spot = IntVec3.Invalid;
                    var cands = fz != null ? fz.FishbleCells.ToList() : new List<IntVec3> { cell };
                    foreach (var c in cands)
                    {
                        var s = WorkGiver_Fish.BestStandSpotFor(p, c);
                        if (s.IsValid) { fc = c; spot = s; break; }
                    }
                    if (fc.IsValid)
                    {
                        fishCellOut = new { x = fc.x, z = fc.z };
                        standOut = new { x = spot.x, z = spot.z, terrain = spot.GetTerrain(map).defName };
                    }
                    else spotWhy = "no candidate cell (" + cands.Count + ") has a standable, reachable, reservable cardinal neighbour";
                    speed = p.GetStatValue(StatDefOf.FishingSpeed);
                    jobTicks = speed > 0f ? Mathf.RoundToInt(7500f / speed.Value) : (int?)null;
                }

                List<object> rollsOut = null;
                if (A == "roll")
                {
                    if (rolls < 1 || rolls > 50) return Fail("rolls must be 1-50, got " + rolls + ".");
                    if (wb == null) return Fail("No water body at " + cell.x + "," + cell.z + " - nothing to roll.", new { body });
                    rollsOut = new List<object>();
                    for (int i = 0; i < rolls; i++)
                    {
                        bool rare;
                        // GetCatchesFor returns a STATIC list it clears on every call: copy it now.
                        var got = FishingUtility.GetCatchesFor(p, cell, false, out rare)
                            .Select(t => new { def = t.def.defName, count = t.stackCount }).ToList();
                        rollsOut.Add(new { catches = got, rare });
                    }
                }

                return (object)new
                {
                    success = true, action = A,
                    cell = new { x = cell.x, z = cell.z },
                    tileMaxFishPopulation = map.TileInfo.MaxFishPopulation,
                    waterBodies = map.waterBodyTracker.Bodies?.Count ?? 0,
                    body, zone = zoneOut,
                    fishOnMap, fishTotal,
                    pawn = p?.ThingID, fishCell = fishCellOut, standSpot = standOut, standSpotWhyNone = spotWhy,
                    fishingSpeed = speed, jobTicks,
                    rolls = rollsOut,
                    rollNote = A == "roll" ? "DRY rolls: nothing spawned, population unchanged, Rand consumed, negative outcomes skipped" : null,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
