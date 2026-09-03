// JawaBenchWorldEdit2.cs - six standalone gaps left in BRIDGE_CAPABILITY_ROSTER.md
// after the 2026-08-26 MEDIUM block (Groups H-K) shipped: the one missing field
// in an otherwise-complete pawn-editing suite, a map-level grid write pollution
// shares no code with, a battery Comp with no bridge access at all, the refund
// half of the wipe-before-build path, gravship substructure detail beyond the
// single count jawa/gravship_status already reports, and a read-only storyteller
// forecast the game's own debug tooling already knows how to run.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   Verse/Pawn.cs                 gender - plain public field (1278), never
//                                  written anywhere on this bridge before now.
//   Verse/PollutionGrid.cs        SetPolluted(IntVec3, bool, bool silent=false) -
//                                 a DIFFERENT system from jawa/world_tile_set's
//                                 planet-tile pollution SCALAR; this is the
//                                 per-cell MAP grid Biotech's overlay draws.
//   RimWorld/CompPowerBattery.cs  StoredEnergy, StoredEnergyPct, AmountCanAccept,
//                                 SetStoredEnergyPct(float), AddEnergy(float),
//                                 DrawPower(float) - all public.
//   Verse/GenSpawn.cs             WouldWipeAnythingWith(pos, rot, def, map, pred),
//                                 WipeExistingThings(...), WipeAndRefundExistingThings
//                                 (pos, rot, def, map, forbid) - the refund path
//                                 jawa/build_batch's wipeExisting never calls.
//   RimWorld/Building_GravEngine.cs   ValidSubstructure, AllConnectedSubstructure
//                                 (both HashSet<IntVec3>, computed via
//                                 GravshipUtility.GetConnectedSubstructure using
//                                 StatDefOf.SubstructureSupport as the cell budget).
//   RimWorld/StorytellerUtility.cs    DebugGetFutureIncidents(numTestDays,
//                                 currentMapOnly, out incCountsForTarget,
//                                 out incCountsForComp, out allIncidents,
//                                 out threatBigCount, ...) - the exact call behind
//                                 the storyteller page's own "test" button.
//
// 🔴 ONE TRAP THE SOURCE CONFIRMED: PollutionGrid.SetPolluted internally checks
// ModLister.CheckBiotech AND SILENTLY NO-OPS (no exception, no return value) when
// Biotech is inactive - a tool that only called it would report success on every
// install and change nothing on most of them. jawa/set_pollution checks
// ModsConfig.BiotechActive itself and refuses by name instead.
//
// GATING follows the rule stated in JawaBenchEventTools.cs, JawaBenchGroupTools.cs
// and JawaBenchIncidentTools.cs: #if JAWA_GM_TOOLS is for tools that make THE
// WORLD ACT on the player, not merely for tools that write a field or destroy
// what a placement would overwrite anyway. NONE of the six below are gated -
// they sit at the same tier as jawa/set_pawn_appearance, jawa/set_gas,
// jawa/set_snow and jawa/build_batch's own wipeExisting, all of which are
// ungated field/grid/thing writes rather than incidents fired at the colony.
// jawa/forecast_incidents and jawa/get_gravship_substructure are pure reads.
//
// THREAD AFFINITY: everything that touches game state is inside
// ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================
        //  Deep pawn editing - the one missing field
        // ================================================================

        [Tool(
            "jawa/set_pawn_gender",
            Description =
                "Write pawn.gender (a plain public field - Verse/Pawn.cs:1278). The last " +
                "unwritten row in an otherwise-complete pawn-editing suite: jawa/pawn_get " +
                "already reads it, nothing on this bridge wrote it before now. ⚠️ Nothing in " +
                "the engine validates the result against head type, body type or life stage - " +
                "an off-gender combination 'works' and simply looks wrong. Call " +
                "jawa/set_pawn_appearance afterward if the head/body should match. " +
                "🔴 The write alone does not dirty the renderer, so this tool calls " +
                "Drawer.renderer.SetAllGraphicsDirty() afterwards - without it an animal with " +
                "femaleGraphicData keeps drawing its old-gender sprite, and every pawn keeps " +
                "its cached portrait, for the rest of the session.",
            ResultDescription = "success, pawn, genderBefore, genderAfter, rendererDirtied.")]
        public static async Task<object> SetPawnGender(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name. Required.")]
            string pawn = null,
            [ToolParameter(Description = "'Male', 'Female' or 'None'. Required.")]
            string gender = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);

                if (string.IsNullOrWhiteSpace(gender)) return Fail("Give 'gender': Male, Female or None.");
                Gender g;
                if (!Enum.TryParse(gender.Trim(), true, out g))
                    return Fail("'" + gender + "' is not a Gender. Accepted: " + string.Join(", ", Enum.GetNames(typeof(Gender))));

                Gender before = p.gender;
                p.gender = g;

                // PawnRenderNode resolves its graphic from pawn.gender ONCE and
                // PawnRenderTree caches the resolved node (PawnRenderNode_AnimalPart and
                // _AnimalPart_Body pick femaleGraphicData off it; PortraitsCache keys off
                // the resolved tree). SetAllGraphicsDirty -> renderTree.SetDirty() is the
                // only thing that re-resolves them - the same rule jawa/set_pawn_appearance
                // already follows for head/body/hair.
                bool dirtied = false;
                try { p.Drawer.renderer.SetAllGraphicsDirty(); dirtied = true; }
                catch (Exception e) { Log.Warning("[JawaBench] SetAllGraphicsDirty failed: " + e.Message); }

                return new
                {
                    success = true,
                    pawn = p.LabelShortCap,
                    genderBefore = before.ToString(),
                    genderAfter = p.gender.ToString(),
                    rendererDirtied = dirtied,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Map-level pollution (Biotech)
        // ================================================================

        [Tool(
            "jawa/set_pollution",
            Description =
                "Write the per-cell MAP pollution grid over a rect - PollutionGrid.SetPolluted " +
                "(Biotech's overlay, canBePolluted terrain check included). A DIFFERENT system " +
                "from jawa/world_tile_set's planet-TILE pollution scalar; do not confuse the " +
                "two. 🔴 Biotech inactive is checked HERE and refused by name - " +
                "PollutionGrid.SetPolluted itself silently no-ops on ModLister.CheckBiotech " +
                "failure, which would otherwise report success while changing nothing.",
            ResultDescription =
                "success, rect, cellsRequested, cellsEverPollutable, cellsChanged (only cells " +
                "whose state actually flipped - SetPolluted no-ops a cell already at the " +
                "target state), totalPollutionAfter, totalPollutionPercentAfter.")]
        public static async Task<object> SetPollution(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Rect 'x,z,w,h'.")]
            string rect = null,
            [ToolParameter(Description = "true = pollute, false = clean. Default true.")]
            bool polluted = true,
            [ToolParameter(Description = "Skip the dissolution effecter/opportunity teaching this tick. Default true (silent).")]
            bool silent = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);
                if (!ModsConfig.BiotechActive)
                    return Fail("Biotech is not active. PollutionGrid.SetPolluted would silently no-op every cell.");

                CellRect r;
                if (!TryRect(rect, map, out r, out err)) return Fail(err);

                int requested = 0, everPollutable = 0, changed = 0;
                foreach (var c in r)
                {
                    requested++;
                    if (!map.pollutionGrid.EverPollutable(c)) continue;
                    everPollutable++;
                    bool before = map.pollutionGrid.IsPolluted(c);
                    if (before == polluted) continue;
                    map.pollutionGrid.SetPolluted(c, polluted, silent);
                    if (map.pollutionGrid.IsPolluted(c) != before) changed++;
                }

                return new
                {
                    success = true,
                    rect = new { x = r.minX, z = r.minZ, w = r.Width, h = r.Height },
                    cellsRequested = requested,
                    cellsEverPollutable = everPollutable,
                    cellsChanged = changed,
                    totalPollutionAfter = map.pollutionGrid.TotalPollution,
                    totalPollutionPercentAfter = map.pollutionGrid.TotalPollutionPercent,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Battery force-charge / drain
        // ================================================================

        [Tool(
            "jawa/battery_set",
            Description =
                "Force-charge, drain, or set a battery's stored energy directly via its " +
                "CompPowerBattery - SetStoredEnergyPct(pct), AddEnergy(watt-days) or " +
                "DrawPower(watt-days). AddEnergy is clamped to AmountCanAccept and scaled by " +
                "Props.efficiency internally (the engine's own rule, not this tool's); " +
                "DrawPower logs an error and clamps to 0 if asked to draw more than is stored - " +
                "read back storedEnergyAfter rather than trusting the amount you asked for. " +
                "Give a thing id, thingId or name of a building carrying CompPowerBattery.",
            ResultDescription =
                "success, thing, mode, storedEnergyBefore, storedEnergyAfter, " +
                "storedEnergyMax, storedEnergyPctAfter.")]
        public static async Task<object> BatterySet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Battery building's id, thingId or name. Required.")]
            string thing = null,
            [ToolParameter(Description = "'setPct' (0-1), 'add' (watt-days) or 'draw' (watt-days). Default 'setPct'.")]
            string mode = "setPct",
            [ToolParameter(Description = "Value for the chosen mode. Required.")]
            float value = 0f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var t = FindLiveThingById(thing, out err);
                if (t == null) return Fail(err);

                var comp = t.TryGetComp<CompPowerBattery>();
                if (comp == null) return Fail("'" + t.LabelCap + "' (" + (t.def != null ? t.def.defName : "?") + ") carries no CompPowerBattery.");

                float before = comp.StoredEnergy;
                string m = (mode ?? "setPct").Trim();
                if (string.Equals(m, "setPct", StringComparison.OrdinalIgnoreCase))
                {
                    comp.SetStoredEnergyPct(value);
                }
                else if (string.Equals(m, "add", StringComparison.OrdinalIgnoreCase))
                {
                    if (value < 0f) return Fail("'add' requires a non-negative value; CompPowerBattery.AddEnergy logs an error on negative input.");
                    comp.AddEnergy(value);
                }
                else if (string.Equals(m, "draw", StringComparison.OrdinalIgnoreCase))
                {
                    // CompPowerBattery.DrawPower is a bare `storedEnergy -= amount` with only
                    // a below-zero guard. A NEGATIVE draw therefore ADDS energy with no
                    // AmountCanAccept clamp, no efficiency scaling and no error, pushing
                    // storedEnergy past storedEnergyMax - which then powers the base off a
                    // battery the UI reports as over-full until a save/load clamps it in
                    // PostExposeData. 'add' already refuses negatives; so does this now.
                    if (value < 0f)
                        return Fail("'draw' requires a non-negative value; CompPowerBattery.DrawPower would ADD it " +
                                    "unclamped, past storedEnergyMax. Use mode='add' to charge.");
                    comp.DrawPower(value);
                }
                else
                {
                    return Fail("mode must be setPct, add or draw.");
                }

                return new
                {
                    success = true,
                    thing = t.LabelCap,
                    mode = m,
                    storedEnergyBefore = before,
                    storedEnergyAfter = comp.StoredEnergy,
                    storedEnergyMax = comp.Props.storedEnergyMax,
                    storedEnergyPctAfter = comp.StoredEnergyPct,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Wipe-before-build: the refund and pre-query half
        // ================================================================

        [Tool(
            "jawa/wipe_cell",
            Description =
                "Pre-query or actually clear whatever a placement of 'thingDef' at 'point' " +
                "would overwrite - the same GenSpawn.SpawningWipes check " +
                "WouldWipeAnythingWith uses, walked manually here to also list WHICH things " +
                "would be hit rather than a bare bool (dryRun), or " +
                "WipeExistingThings / WipeAndRefundExistingThings for real (dryRun=false). This is the " +
                "refund path jawa/build_batch's own wipeExisting never calls - that one is a " +
                "plain DestroyMode.Vanish with no minified-crate refund and no pre-query. " +
                "Destructive default is OFF: dryRun defaults true and only REPORTS what would " +
                "be wiped, spawnable or not.",
            ResultDescription =
                "success, dryRun, point, rot, thingDef, wouldWipeAnything, affected[] " +
                "(thingId, def, label, category) - populated in both modes; in dryRun=false " +
                "these are the things actually wiped, with 'refunded' true/false per the " +
                "'refund' argument.")]
        public static async Task<object> WipeCell(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell 'x,z'. Required.")]
            string point = null,
            [ToolParameter(Description = "Rotation 0-3 (North/East/South/West). Default 0.")]
            int rot = 0,
            [ToolParameter(Description = "BuildableDef whose footprint/SpawningWipes rules to check against. Required.")]
            string thingDef = null,
            [ToolParameter(Description = "true = report only, wipe nothing. Default true.")]
            bool dryRun = true,
            [ToolParameter(Description = "When dryRun=false: minify/refund what is wiped rather than destroying it outright. Default true.")]
            bool refund = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err; var map = MapOrNull(out err);
                if (map == null) return Fail(err);

                if (!TryParseCellLocal(point, out var cell, out err)) return Fail(err);
                if (!cell.InBounds(map)) return Fail("Point " + cell + " is outside the map (" + map.Size.x + "x" + map.Size.z + ").");
                if (rot < 0 || rot > 3) return Fail("rot must be 0-3.");
                var rotation = new Rot4(rot);

                if (string.IsNullOrWhiteSpace(thingDef)) return Fail("Give 'thingDef', the def that would be placed.");
                BuildableDef def = DefDatabase<ThingDef>.GetNamedSilentFail(thingDef.Trim());
                if (def == null) def = DefDatabase<TerrainDef>.GetNamedSilentFail(thingDef.Trim());
                if (def == null) return Fail("No ThingDef or TerrainDef '" + thingDef + "'.", DefSuggestions<ThingDef>(thingDef));

                var rect = GenAdj.OccupiedRect(cell, rotation, def.Size);
                var hit = new List<object>();
                var hitMinifiable = new List<bool>();
                var seenThingIds = new HashSet<int>();
                bool wouldWipe = false;
                foreach (var c in rect)
                {
                    // thingGrid registers a multi-cell thing at EVERY cell it occupies,
                    // so a 3x3 building would otherwise be added 9 times and inflate
                    // both `affected` and the wouldWipeAnything companion count.
                    foreach (var th in map.thingGrid.ThingsAt(c).ToList())
                    {
                        if (!GenSpawn.SpawningWipes(def, th.def)) continue;
                        if (!seenThingIds.Add(th.thingIDNumber)) continue;
                        wouldWipe = true;
                        hit.Add(new { thingId = th.ThingID, def = th.def != null ? th.def.defName : null, label = th.LabelCap, category = th.def != null ? th.def.category.ToString() : null });
                        hitMinifiable.Add(th.def != null && th.def.Minifiable);
                    }
                }

                if (dryRun)
                {
                    return new
                    {
                        success = true,
                        dryRun = true,
                        point = new { x = cell.x, z = cell.z },
                        rot,
                        thingDef = def.defName,
                        wouldWipeAnything = wouldWipe,
                        affected = hit,
                        ticksGame = TicksGameSafe()
                    };
                }

                try
                {
                    if (refund) GenSpawn.WipeAndRefundExistingThings(cell, rotation, def, map, false);
                    else GenSpawn.WipeExistingThings(cell, rotation, def, map, DestroyMode.Vanish);
                }
                catch (Exception e)
                {
                    return Fail("Wipe threw " + e.GetType().Name + ": " + e.Message, new { point = new { x = cell.x, z = cell.z }, affected = hit });
                }

                return new
                {
                    success = true,
                    dryRun = false,
                    point = new { x = cell.x, z = cell.z },
                    rot,
                    thingDef = def.defName,
                    wouldWipeAnything = wouldWipe,
                    // GenSpawn.WipeAndRefundExistingThings only minifies-and-replaces a
                    // Minifiable thing; everything else (walls, floors, plants, most
                    // items) is DESTROYED regardless of `refund`.
                    affected = hit.Select((o, i) => new { row = o, refunded = refund && hitMinifiable[i] }).ToList(),
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Gravship substructure detail
        // ================================================================

        [Tool(
            "jawa/get_gravship_substructure",
            Description =
                "Read a Building_GravEngine's substructure in full: ValidSubstructure and " +
                "AllConnectedSubstructure (both cell sets, not just the COUNT " +
                "jawa/gravship_status already reports), plus the support budget - " +
                "GetStatValue(StatDefOf.SubstructureSupport), the cell cap " +
                "GravshipUtility.GetConnectedSubstructure was given when it computed " +
                "AllConnectedSubstructure. Read-only. Omit 'engine' to use the first " +
                "Building_GravEngine on the current map.",
            ResultDescription =
                "success, engine (thingId, label), supportBudget, validCount, connectedCount, " +
                "validCells[] and connectedCells[] (each capped at 2000 with cellsTruncated " +
                "true if more exist - read the counts either way).")]
        public static async Task<object> GetGravshipSubstructure(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Building_GravEngine thing id. Omit to use the first one on the current map.")]
            string engine = null,
            [ToolParameter(Description = "Max cells to return per list. Default 2000.")]
            int maxCells = 2000)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.OdysseyActive) return Fail("Odyssey is not active - Building_GravEngine does not exist.");

                Building_GravEngine e;
                if (!string.IsNullOrWhiteSpace(engine))
                {
                    string err; var t = FindLiveThingById(engine, out err);
                    if (t == null) return Fail(err);
                    e = t as Building_GravEngine;
                    if (e == null) return Fail("'" + t.LabelCap + "' is not a Building_GravEngine.");
                }
                else
                {
                    string err; var map = MapOrNull(out err);
                    if (map == null) return Fail(err);
                    // allBuildingsColonist holds PLAYER-FACTION buildings only, so a derelict
                    // or quest-site gravship engine is invisible to AllBuildingsColonistOfClass
                    // and would read as "no engine on this map" while one is standing there.
                    e = map.listerBuildings.AllBuildingsColonistOfClass<Building_GravEngine>().FirstOrDefault()
                        ?? map.listerBuildings.allBuildingsNonColonist.OfType<Building_GravEngine>().FirstOrDefault();
                    if (e == null) return Fail("No Building_GravEngine on the current map. Give 'engine' explicitly, or check another map.");
                }

                HashSet<IntVec3> valid, connected;
                try { valid = e.ValidSubstructure; connected = e.AllConnectedSubstructure; }
                catch (Exception ex) { return Fail("Reading substructure threw " + ex.GetType().Name + ": " + ex.Message); }

                float budget;
                try { budget = e.GetStatValue(StatDefOf.SubstructureSupport); }
                catch (Exception ex) { return Fail("GetStatValue(SubstructureSupport) threw " + ex.GetType().Name + ": " + ex.Message); }

                if (maxCells < 0) maxCells = 0;
                var validList = valid.Select(c => new { x = c.x, z = c.z }).ToList();
                var connList = connected.Select(c => new { x = c.x, z = c.z }).ToList();

                return new
                {
                    success = true,
                    engine = new { thingId = e.ThingID, label = e.RenamableLabel },
                    supportBudget = budget,
                    validCount = valid.Count,
                    connectedCount = connected.Count,
                    validCells = validList.Take(maxCells).ToList(),
                    connectedCells = connList.Take(maxCells).ToList(),
                    cellsTruncated = valid.Count > maxCells || connected.Count > maxCells,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Storyteller forecast
        // ================================================================

        [Tool(
            "jawa/forecast_incidents",
            Description =
                "Dry-run N days of the storyteller's plan with NO game time spent - " +
                "StorytellerUtility.DebugGetFutureIncidents(numTestDays, currentMapOnly, ...), " +
                "the exact call behind the storyteller-select page's own 'test' button. " +
                "Fires nothing: it rolls the same RNG path a real playthrough would, and the " +
                "engine restores TicksGame, the incident queue and every StoryState itself. " +
                "🔴 What the engine does NOT restore is Storyteller.recentIncidentsAnomaly / " +
                "recentAnomalyIncidentFactor - DebugGetFutureIncidents calls " +
                "RecordIncidentFired per forecast incident and those two fields are SCRIBED, " +
                "so an unguarded forecast permanently skews the live anomaly incident chance. " +
                "This tool snapshots and restores them (anomalyStateRestored).",
            ResultDescription =
                "success, numTestDays, currentMapOnly, threatBigCount, totalIncidents, " +
                "anomalyStateRestored, byIncidentDef[] (defName, count), incidents[] (defName, " +
                "points, faction, target) capped at 200 with incidentsTruncated if more fired " +
                "in the forecast.")]
        public static async Task<object> ForecastIncidents(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Days to simulate forward. Default 15.")]
            int numTestDays = 15,
            [ToolParameter(Description = "Restrict to the current map's incident targets. Default true.")]
            bool currentMapOnly = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Current.Game.storyteller == null) return Fail("No active game/storyteller.");
                if (currentMapOnly && Find.CurrentMap == null) return Fail("No current map, and currentMapOnly=true.");
                if (numTestDays < 1) return Fail("numTestDays must be at least 1.");
                // The engine loops numTestDays*60 intervals synchronously on the main thread
                // (and overflows int past ~35.8M days). A four-digit request wedges the game.
                if (numTestDays > 1000) return Fail("numTestDays must be 1000 or less - DebugGetFutureIncidents runs " +
                                                   numTestDays + "*60 storyteller intervals synchronously on the main thread.");

                var storyteller = Current.Game.storyteller;
                // 🔴 DebugGetFutureIncidents restores TicksGame, the incident queue and every
                // StoryState - but it also calls Storyteller.RecordIncidentFired for each
                // forecast incident, and that writes recentIncidentsAnomaly /
                // recentAnomalyIncidentFactor, both SCRIBED in Storyteller.ExposeData and
                // never put back. Snapshot the QUEUE'S CONTENTS, not just its reference:
                // RecordIncidentFired mutates the same object in place.
                const BindingFlags privInst = BindingFlags.NonPublic | BindingFlags.Instance;
                FieldInfo fAnomQueue = typeof(Storyteller).GetField("recentIncidentsAnomaly", privInst);
                FieldInfo fAnomFactor = typeof(Storyteller).GetField("recentAnomalyIncidentFactor", privInst);
                Queue<bool> savedAnomQueue = null;
                object savedAnomFactor = null;
                bool anomalyStateRestored = false;
                try
                {
                    var live = fAnomQueue != null ? fAnomQueue.GetValue(storyteller) as Queue<bool> : null;
                    savedAnomQueue = live == null ? null : new Queue<bool>(live);
                    if (fAnomFactor != null) savedAnomFactor = fAnomFactor.GetValue(storyteller);
                }
                catch (Exception) { fAnomQueue = null; fAnomFactor = null; }

                Dictionary<IIncidentTarget, int> incCountsForTarget;
                int[] incCountsForComp;
                List<Pair<IncidentDef, IncidentParms>> allIncidents;
                int threatBigCount;
                try
                {
                    StorytellerUtility.DebugGetFutureIncidents(
                        numTestDays, currentMapOnly,
                        out incCountsForTarget, out incCountsForComp, out allIncidents, out threatBigCount);
                }
                catch (Exception e)
                {
                    return Fail("StorytellerUtility.DebugGetFutureIncidents threw " + e.GetType().Name + ": " + e.Message);
                }
                finally
                {
                    try
                    {
                        if (fAnomQueue != null) fAnomQueue.SetValue(storyteller, savedAnomQueue);
                        if (fAnomFactor != null) fAnomFactor.SetValue(storyteller, savedAnomFactor);
                        anomalyStateRestored = fAnomQueue != null && fAnomFactor != null;
                    }
                    catch (Exception e) { Log.Warning("[JawaBench] forecast_incidents could not restore anomaly state: " + e.Message); }
                }

                var byDef = allIncidents
                    .GroupBy(p => p.First != null ? p.First.defName : "(null)")
                    .Select(g => new { defName = g.Key, count = g.Count() })
                    .OrderByDescending(g => g.count)
                    .ToList();

                const int cap = 200;
                var rows = allIncidents.Take(cap).Select(p => new
                {
                    defName = p.First != null ? p.First.defName : null,
                    points = p.Second.points,
                    faction = p.Second.faction != null ? p.Second.faction.Name : null,
                    target = p.Second.target != null ? p.Second.target.ToString() : null
                }).ToList();

                return new
                {
                    success = true,
                    numTestDays,
                    currentMapOnly,
                    threatBigCount,
                    totalIncidents = allIncidents.Count,
                    anomalyStateRestored,
                    byIncidentDef = byDef,
                    incidents = rows,
                    incidentsTruncated = allIncidents.Count > cap,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
