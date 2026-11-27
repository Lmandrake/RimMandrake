// JawaBenchWreckTools.cs - seven generic reads and acts that the Wrecked Machines scenes name
// (item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL; design/concepts/WreckedMachines/plan.md, "order", step 2;
// the two caravan tools for the scene sc_caravan_wreck_home, added by the Designer's stage 5).
// Nothing here knows that mod: each tool works on any ThingSetMakerDef, TraderKindDef, minified building, analysable def or
// PipeSystem processor. The decisions (run limits, tally, install mode, study status, fill amounts) are in the Verse-free
// JawaBenchWreckReadsCore.cs and are proven offline by src/RimMandrake/bridgetools/selftest_wreck_reads.py.
//
// THREAD AFFINITY: everything that touches a Map, a Thing or a Def database runs inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimWorld;
using RimWorld.Planet;
using RimBridgeServer.Sdk;
using Verse;
using Verse.AI;
using Verse.AI.Group;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // A thing by ThingID anywhere a scene can leave it: on a map, carried by a pawn, or in a pawn's inventory.
        private static Thing WreckFindThing(string id, out string err)
        {
            err = null;
            if (string.IsNullOrWhiteSpace(id)) { err = "Give a thing id."; return null; }
            string bare = id.Trim();
            if (bare.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && bare.Length > 6) bare = bare.Substring(6);
            foreach (Map m in Find.Maps ?? new List<Map>())
            {
                foreach (Thing t in m.listerThings.AllThings)
                    if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                foreach (Pawn p in m.mapPawns.AllPawnsSpawned)
                {
                    Thing c = p.carryTracker?.CarriedThing;
                    if (c != null && string.Equals(c.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return c;
                    if (p.inventory?.innerContainer != null)
                        foreach (Thing t in p.inventory.innerContainer)
                            if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                }
            }
            err = "No thing with id '" + bare + "' on a loaded map, carried by a pawn, or in a pawn's inventory.";
            return null;
        }

        // ================================================================
        //  jawa/thing_set_sample
        // ================================================================
        [Tool(
            "jawa/thing_set_sample",
            Description =
                "Run a generator N times and list the defs that it produced, then destroy what it made (never spawned). " +
                "kind='thingSetMaker': ThingSetMakerDef.root.Generate(parms) with the def's own default params, as the game's " +
                "debug output ThingSetMakerTest does. kind='trader': ThingSetMakerDefOf.TraderStock with traderDef set, the call " +
                "that stocks a caravan, a ship or a settlement (every stockGenerator of the TraderKindDef). kind='list': no run; " +
                "every ThingSetMakerDef and TraderKindDef with the mod that added it. A run that throws is counted apart from a run " +
                "that produced nothing. runs above 2000 (JawaBenchWreckReadsCore.MaxRuns) are REFUSED, never clamped (a hang " +
                "guard: every run holds the game's main thread).",
            ResultDescription =
                "success, kind, def, runs, emptyRuns, failedRuns, failures[], rows[] (def, runsWith, things, count), most often " +
                "first; for kind=list: thingSetMakers[] and traders[] (defName, mod).")]
        public static async Task<object> ThingSetSample(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "thingSetMaker, trader or list.")] string kind = "thingSetMaker",
            [ToolParameter(Description = "The ThingSetMakerDef or TraderKindDef defName (not used by kind=list).")] string def = null,
            [ToolParameter(Description = "How many runs (1 to the hang-guard limit).")] int runs = 50,
            [ToolParameter(Description = "kind=trader: the faction defName that makes the stock; default the first faction that uses this trader kind, else none.")]
            string faction = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                string k = (kind ?? "").Trim().ToLowerInvariant();
                if (k == "list")
                {
                    return (object)new
                    {
                        success = true, kind = "list",
                        thingSetMakers = DefDatabase<ThingSetMakerDef>.AllDefsListForReading
                            .Select(d => new { defName = d.defName, mod = d.modContentPack?.PackageId }).ToList(),
                        traders = DefDatabase<TraderKindDef>.AllDefsListForReading
                            .Select(d => new { defName = d.defName, mod = d.modContentPack?.PackageId }).ToList(),
                        ticksGame = TicksGameSafe()
                    };
                }
                string refusal = JawaBenchWreckReadsCore.RunsRefusal(runs);
                if (refusal != null) return Fail(refusal);
                Func<List<Thing>> once;
                if (k == "thingsetmaker")
                {
                    var tsm = DefDatabase<ThingSetMakerDef>.GetNamedSilentFail((def ?? "").Trim());
                    if (tsm == null) return Fail("No ThingSetMakerDef '" + def + "'.", new { suggestions = DefSuggestions<ThingSetMakerDef>(def ?? "") });
                    once = () => tsm.root.Generate(tsm.debugParams);
                }
                else if (k == "trader")
                {
                    var tk = DefDatabase<TraderKindDef>.GetNamedSilentFail((def ?? "").Trim());
                    if (tk == null) return Fail("No TraderKindDef '" + def + "'.", new { suggestions = DefSuggestions<TraderKindDef>(def ?? "") });
                    Faction fac = null;
                    if (!string.IsNullOrWhiteSpace(faction))
                    {
                        fac = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f => f.def.defName == faction.Trim());
                        if (fac == null) return Fail("No faction of def '" + faction + "' in this game.");
                    }
                    else
                    {
                        fac = Find.FactionManager.AllFactionsListForReading.FirstOrDefault(f =>
                            f.def.caravanTraderKinds.Contains(tk) || f.def.visitorTraderKinds.Contains(tk) || f.def.baseTraderKinds.Contains(tk));
                    }
                    PlanetTile? tile = Find.CurrentMap != null ? (PlanetTile?)Find.CurrentMap.Tile : null;
                    once = () => ThingSetMakerDefOf.TraderStock.root.Generate(new ThingSetMakerParams { traderDef = tk, tile = tile, makingFaction = fac });
                }
                else return Fail("kind must be thingSetMaker, trader or list, got '" + kind + "'.");

                var tally = new JawaBenchWreckReadsCore.Tally();
                for (int i = 0; i < runs; i++)
                {
                    List<Thing> made = null;
                    string why = null;
                    try { made = once(); if (made == null) why = "the generator returned null"; }
                    catch (Exception ex) { why = ex.GetType().Name + ": " + ex.Message; made = null; }
                    if (made == null) { tally.AddRun(null, why); continue; }
                    var pairs = new List<KeyValuePair<string, int>>();
                    foreach (Thing t in made)
                    {
                        if (t == null) continue;
                        Thing inner = t is MinifiedThing mt && mt.InnerThing != null ? mt.InnerThing : t;
                        pairs.Add(new KeyValuePair<string, int>(inner.def?.defName, t.stackCount));
                    }
                    tally.AddRun(pairs);
                    foreach (Thing t in made)
                    {
                        try { if (t != null && !t.Destroyed) t.Destroy(); } catch (Exception) { /* a made thing that will not destroy is left to GC */ }
                    }
                }
                return (object)new
                {
                    success = true, kind = k, def = def, runs = tally.runs, emptyRuns = tally.emptyRuns, failedRuns = tally.failedRuns,
                    failures = tally.failures,
                    rows = tally.Rows().Select(r => new { def = r.def, runsWith = r.runsWith, things = r.things, count = r.count }).ToList(),
                    note = "a minified thing is listed by its inner def",
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        // ================================================================
        //  jawa/install_blueprint
        // ================================================================
        [Tool(
            "jawa/install_blueprint",
            Description =
                "Place the install blueprint of a carried (minified) building at a cell, the call Designator_Install makes " +
                "(GenConstruct.PlaceBlueprintForInstall), so a colonist hauls and installs it by his own work; for a standing " +
                "minifiable building, its reinstall blueprint (PlaceBlueprintForReinstall). The carried thing may lie on the map, be " +
                "carried by a pawn or be in a pawn's inventory, on the current map (a thing on another map is REFUSED). Earlier install blueprints of the same thing are cancelled first, as the " +
                "designator does. Checked with GenConstruct.CanPlaceBlueprintAt (the designator's own arguments): a refusal returns the " +
                "engine's reason and places nothing. A thing that is not a minified or minifiable building is REFUSED BY NAME.",
            ResultDescription =
                "success, mode (Install|Reinstall), thing (id, def), installDef, blueprint (id, def, position, rotation) read back " +
                "from the map, placementCheck (accepted, reason).")]
        public static async Task<object> InstallBlueprint(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the minified thing (or of the standing building to reinstall).")] string thing = null,
            [ToolParameter(Description = "Cell X.")] int x = -1,
            [ToolParameter(Description = "Cell Z.")] int z = -1,
            [ToolParameter(Description = "Rotation: north/east/south/west, n/e/s/w, or 0-3. Default north.")] string rot = "north")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                Map map = MapOrNull(out err);
                if (map == null) return Fail(err);
                Thing t = WreckFindThing(thing, out err);
                if (t == null) return Fail(err);
                if (x < 0 || z < 0 || x >= map.Size.x || z >= map.Size.z) return Fail("Cell (" + x + "," + z + ") is outside the map.");
                Rot4 rotation;
                if (!TryRot(rot, out rotation)) return Fail("rot must be north/east/south/west, n/e/s/w, or 0-3, got '" + rot + "'.");

                var mini = t as MinifiedThing;
                Thing toInstall = mini != null ? mini.InnerThing : t;
                bool held = mini != null && !mini.Spawned && (mini.ParentHolder is Pawn_CarryTracker || mini.ParentHolder is Pawn_InventoryTracker);
                string why;
                var mode = JawaBenchWreckReadsCore.Classify(
                    mini != null, t.Spawned, held, toInstall?.def?.installBlueprintDef != null,
                    mini == null && t is Building, t.def.Minifiable, t.MapHeld == map, out why);
                if (mode == JawaBenchWreckReadsCore.InstallMode.Refused)
                    return Fail(t.def.defName + " (" + t.ThingID + "): " + why + ".");

                var cell = new IntVec3(x, 0, z);
                AcceptanceReport check;
                try { check = GenConstruct.CanPlaceBlueprintAt(toInstall.def, cell, rotation, map, false, t, toInstall); }
                catch (Exception ex) { check = new AcceptanceReport("CanPlaceBlueprintAt threw: " + ex.GetType().Name + ": " + ex.Message); }
                if (!check.Accepted)
                    return Fail("Placement refused by the engine: " + check.Reason, new { placementCheck = new { accepted = false, reason = check.Reason } });

                InstallBlueprintUtility.CancelBlueprintsFor(t);
                Blueprint_Install bp = mode == JawaBenchWreckReadsCore.InstallMode.Install
                    ? GenConstruct.PlaceBlueprintForInstall(mini, cell, map, rotation, Faction.OfPlayer)
                    : GenConstruct.PlaceBlueprintForReinstall((Building)t, cell, map, rotation, Faction.OfPlayer);
                Blueprint_Install back = bp != null && bp.Spawned
                    ? map.thingGrid.ThingsListAtFast(cell).OfType<Blueprint_Install>().FirstOrDefault(b => b == bp) : null;
                if (back == null) return Fail("The engine returned no spawned blueprint at (" + x + "," + z + ").");
                return (object)new
                {
                    success = true, mode = mode.ToString(),
                    thing = new { id = t.ThingID, def = t.def.defName },
                    installDef = toInstall.def.defName,
                    blueprint = new { id = back.ThingID, def = back.def.defName, position = new { x = back.Position.x, z = back.Position.z },
                                      rotation = back.Rotation.AsInt },
                    placementCheck = new { accepted = true, reason = (string)null },
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        // ================================================================
        //  jawa/study_record
        // ================================================================
        [Tool(
            "jawa/study_record",
            Description =
                "Read the game's study (analysis) record for a kind of thing: the def's CompProperties_CompAnalyzableUnlockResearch " +
                "analysisID, and Find.AnalysisManager's record for it (timesDone, required), with one of four statuses kept apart: " +
                "no_study_comp, no_record (never studied: AnalysisManager.IsAnalysisComplete would say TRUE here, a trap), partial, " +
                "complete. Also every ResearchProjectDef that lists the def in requiredAnalyzed, each with how many of its required " +
                "things are complete (the rule of ResearchProjectDef.AnalyzedThingsCompleted) and whether it is finished. " +
                "def = a ThingDef defName, or thing = a ThingID whose def is read. Reads only; changes nothing.",
            ResultDescription =
                "success, def, analysisID, status, timesDone, required, projects[] (defName, requiredDefs[] (def, status), completed, " +
                "requiredCount, analyzedMet, gameSays (ResearchProjectDef.AnalyzedThingsCompleted), finished).")]
        public static async Task<object> StudyRecord(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingDef defName.")] string def = null,
            [ToolParameter(Description = "Or a ThingID; its def (the inner def of a minified thing) is read.")] string thing = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Find.AnalysisManager == null) return Fail("No game loaded.");
                ThingDef td = null;
                if (!string.IsNullOrWhiteSpace(thing))
                {
                    string err;
                    Thing t = WreckFindThing(thing, out err);
                    if (t == null) return Fail(err);
                    td = (t is MinifiedThing mt && mt.InnerThing != null ? mt.InnerThing : t).def;
                }
                else
                {
                    td = DefDatabase<ThingDef>.GetNamedSilentFail((def ?? "").Trim());
                    if (td == null) return Fail("No ThingDef '" + def + "'.", new { suggestions = DefSuggestions<ThingDef>(def ?? "") });
                }

                Func<ThingDef, object[]> rec = d =>
                {
                    var props = d.GetCompProperties<CompProperties_CompAnalyzableUnlockResearch>();
                    AnalysisDetails det = null;
                    bool has = props != null && Find.AnalysisManager.TryGetAnalysisProgress(props.analysisID, out det) && det != null;
                    string st = JawaBenchWreckReadsCore.StudyStatus(props != null, has, has ? det.timesDone : 0, has ? det.required : 0);
                    return new object[] { props != null ? (object)props.analysisID : null, st, has ? (object)det.timesDone : null, has ? (object)det.required : null };
                };
                object[] me = rec(td);
                var projects = new List<object>();
                foreach (ResearchProjectDef p in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
                {
                    if (p.requiredAnalyzed.NullOrEmpty() || !p.requiredAnalyzed.Contains(td)) continue;
                    var rows = p.requiredAnalyzed.Select(d => new { def = d.defName, status = (string)rec(d)[1] }).ToList();
                    int done = JawaBenchWreckReadsCore.CompletedCount(rows.Select(r => r.status));
                    projects.Add(new
                    {
                        defName = p.defName, requiredDefs = rows, completed = done, requiredCount = p.requiredAnalyzed.Count,
                        analyzedMet = done >= p.requiredAnalyzed.Count, gameSays = p.AnalyzedThingsCompleted, finished = p.IsFinished
                    });
                }
                return (object)new
                {
                    success = true, def = td.defName, analysisID = me[0], status = (string)me[1], timesDone = me[2], required = me[3],
                    projects, ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        // ================================================================
        //  jawa/processor_fill
        // ================================================================
        [Tool(
            "jawa/processor_fill",
            Description =
                "Place the inputs of a factory process in a PipeSystem processor (Vanilla Expanded's CompAdvancedResourceProcessor, " +
                "read by reflection: the companion does not reference PipeSystem). The processor keeps its inputs as counts on " +
                "ThingAndResourceOwner rows, not in a ThingOwner, so jawa/container_fill cannot reach it. For each input row of the " +
                "chosen process, a fresh thing of the row's def (the first def of its category for a category row) is made and handed " +
                "to the row's own AddFromThing, the call a colonist's delivery makes; a row fed by a pipe net is skipped by name. " +
                "process = a ProcessDef defName already in the processor's list (default the current process); add=true first adds " +
                "it to the list (ProcessStack.AddProcess, repeat count 1). Every row is read back after the fill.",
            ResultDescription =
                "success, thing, process, rows[] (def, category, net, haveBefore, required, wanted, used, haveAfter, skip), " +
                "processes[] (the processor's list), available[] (every ProcessDef its tab offers; also on a refusal), allFull.")]
        public static async Task<object> ProcessorFill(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID of the processor building.")] string thing = null,
            [ToolParameter(Description = "ProcessDef defName; default the processor's current process.")] string process = null,
            [ToolParameter(Description = "Add the process to the processor's list first when it is not there.")] bool add = false,
            [ToolParameter(Description = "Read only: report the rows and fill nothing.")] bool dryRun = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                Thing t = WreckFindThing(thing, out err);
                if (t == null) return Fail(err);
                var twc = t as ThingWithComps;
                object comp = twc?.AllComps.FirstOrDefault(c => c.GetType().Name == "CompAdvancedResourceProcessor");
                if (comp == null)
                    return Fail(t.def.defName + " (" + t.ThingID + ") has no CompAdvancedResourceProcessor.",
                        new { comps = twc?.AllComps.Select(c => c.GetType().Name).ToList() });
                const BindingFlags F = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance;
                Func<object, string, object> get = (o, name) =>
                {
                    if (o == null) return null;
                    var pi = o.GetType().GetProperty(name, F);
                    return pi != null ? pi.GetValue(o, null) : o.GetType().GetField(name, F)?.GetValue(o);
                };
                object stack = get(comp, "ProcessStack");
                // what the player can add in the processor's tab: the comp's props' process list
                var available = ((get(get(comp, "Props"), "processes") as IEnumerable)?.Cast<object>() ?? Enumerable.Empty<object>())
                    .Select(pd => (pd as Def)?.defName).Where(n => n != null).ToList();
                var list = (get(stack, "Processes") as IEnumerable)?.Cast<object>().ToList() ?? new List<object>();
                Func<object, string> defOf = pr => (get(pr, "Def") as Def)?.defName;
                object chosen;
                if (string.IsNullOrWhiteSpace(process)) chosen = get(comp, "Process") ?? list.FirstOrDefault();
                else
                {
                    chosen = list.FirstOrDefault(pr => defOf(pr) == process.Trim());
                    if (chosen == null && add)
                    {
                        Type pdType = comp.GetType().Assembly.GetType("PipeSystem.ProcessDef");
                        object pd = pdType == null ? null : GenDefDatabase.GetDefSilentFail(pdType, process.Trim());
                        if (pd == null) return Fail("No PipeSystem.ProcessDef '" + process + "'.");
                        MethodInfo addM = stack?.GetType().GetMethod("AddProcess", F);
                        if (addM == null) return Fail("ProcessStack.AddProcess not found: the PipeSystem API changed.");
                        addM.Invoke(stack, new object[] { pd, twc, BillRepeatModeDefOf.RepeatCount, 1, QualityCategory.Normal });
                        list = (get(stack, "Processes") as IEnumerable)?.Cast<object>().ToList() ?? new List<object>();
                        chosen = list.FirstOrDefault(pr => defOf(pr) == process.Trim());
                    }
                }
                var names = list.Select(defOf).ToList();
                if (chosen == null)
                    return Fail(string.IsNullOrWhiteSpace(process) ? "The processor has no process." : "Process '" + process + "' is not in the processor's list (add=true adds it).",
                        new { processes = names, available });
                var owners = (get(chosen, "IngredientsOwners") as IEnumerable)?.Cast<object>().ToList();
                if (owners == null) return Fail("Process.IngredientsOwners not readable: the PipeSystem API changed.");
                var rows = new List<object>();
                bool allFull = true;
                foreach (object o in owners)
                {
                    var td = get(o, "ThingDef") as ThingDef;
                    var cat = get(o, "ThingCategoryDef") as ThingCategoryDef;
                    var net = get(o, "PipeNetDef") as Def;
                    int have = Convert.ToInt32(get(o, "Count") ?? 0), req = Convert.ToInt32(get(o, "Required") ?? 0);
                    string first = cat?.DescendantThingDefs?.FirstOrDefault(d => d.category == ThingCategory.Item)?.defName;
                    var plan = JawaBenchWreckReadsCore.Plan(td?.defName, cat?.defName, net?.defName, have, req, first);
                    int used = 0;
                    if (plan.skip == null && !dryRun)
                    {
                        ThingDef make = DefDatabase<ThingDef>.GetNamedSilentFail(plan.def);
                        MethodInfo addFrom = o.GetType().GetMethod("AddFromThing", F);
                        if (make == null || addFrom == null) plan.skip = make == null ? "no ThingDef " + plan.def : "AddFromThing not found: the PipeSystem API changed";
                        else
                        {
                            int left = plan.want, guard = 0;
                            while (left > 0 && guard++ < 1000)   // hang guard: a row whose count never rises stops after 1000 hands
                            {
                                Thing made = ThingMaker.MakeThing(make, make.MadeFromStuff ? GenStuff.DefaultStuffFor(make) : null);
                                made.stackCount = Math.Min(left, Math.Max(1, make.stackLimit));
                                var args = new object[] { made, 0 };
                                addFrom.Invoke(o, args);
                                int u = Convert.ToInt32(args[1]);
                                if (!made.Destroyed) made.Destroy();
                                if (u <= 0) break;
                                used += u;
                                left -= u;
                            }
                        }
                    }
                    int after = Convert.ToInt32(get(o, "Count") ?? 0);
                    if (after < req && plan.net == null) allFull = false;
                    rows.Add(new { def = plan.def, category = plan.category, net = plan.net, haveBefore = have, required = req, wanted = plan.want,
                                   used, haveAfter = after, skip = plan.skip });
                }
                return (object)new
                {
                    success = true, thing = t.ThingID, process = defOf(chosen), dryRun, rows, processes = names, available, allFull,
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        // ================================================================
        //  jawa/caravan_mass, jawa/caravan_form_load
        // ================================================================
        private static List<Thing> WreckThings(string ids, out string err)
        {
            err = null;
            var list = new List<Thing>();
            foreach (string id in (ids ?? "").Split(new[] { ',', ';' }, StringSplitOptions.RemoveEmptyEntries))
            {
                Thing t = WreckFindThing(id.Trim(), out err);
                if (t == null) return null;
                list.Add(t);
            }
            return list;
        }

        [Tool(
            "jawa/caravan_mass",
            Description =
                "Read a candidate caravan's load the way the Form Caravan dialog does: CollectionsMassCalculator.Capacity of the " +
                "pawns (with what they carry) and MassUsage of the pawns' gear plus the named things, and whether the load is over " +
                "capacity (the dialog's rule: usage above capacity). Reads only; moves nothing.",
            ResultDescription = "success, pawns[], things[] (id, def, mass), capacity, usage, over.")]
        public static async Task<object> CaravanMass(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids (colonists and pack animals).")] string pawns = null,
            [ToolParameter(Description = "Comma-separated ids of the things to load.")] string things = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                string err;
                var ps = WreckThings(pawns, out err);
                if (ps == null) return Fail(err);
                if (ps.Any(p => !(p is Pawn))) return Fail("Not every id in 'pawns' is a pawn.");
                var ts = WreckThings(things, out err);
                if (ts == null) return Fail(err);
                var counts = ps.Select(p => new ThingCount(p, 1)).Concat(ts.Select(t => new ThingCount(t, t.stackCount))).ToList();
                float cap = CollectionsMassCalculator.Capacity(counts);
                float use = CollectionsMassCalculator.MassUsage(counts, IgnorePawnsInventoryMode.DontIgnore, false);
                return (object)new
                {
                    success = true, pawns = ps.Select(p => p.ThingID).ToList(),
                    things = ts.Select(t => new { id = t.ThingID, def = t.def.defName, mass = t.GetStatValue(StatDefOf.Mass) * t.stackCount }).ToList(),
                    capacity = cap, usage = use, over = JawaBenchWreckReadsCore.OverCapacity(use, cap), ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        [Tool(
            "jawa/caravan_form_load",
            Description =
                "Start forming a caravan the way the Form Caravan dialog does on accept (CaravanFormingUtility.StartFormingCaravan): " +
                "the named pawns join a LordJob_FormAndSendCaravan, colonists haul the named things into it by their own jobs, and the " +
                "caravan leaves at an edge cell that the first pawn can reach, bound for destTile. Refused by name: no pawn, an id in pawns " +
                "that is not a pawn, a downed or non-player pawn, a thing not spawned on the pawns' map. Returns at once; advance the clock to watch the loading.",
            ResultDescription = "success, lord (loadID), exit (x, z), startTile, destTile, things[], capacity, usage, over.")]
        public static async Task<object> CaravanFormLoad(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids (colonists and pack animals).")] string pawns = null,
            [ToolParameter(Description = "Comma-separated ids of the things to load.")] string things = null,
            [ToolParameter(Description = "The world tile to travel to (e.g. the home map's tile).")] int destTile = -1)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                string err;
                var ps = WreckThings(pawns, out err);
                if (ps == null) return Fail(err);
                var pawnList = ps.OfType<Pawn>().ToList();
                var ts = WreckThings(things, out err);
                if (ts == null) return Fail(err);
                Map map = pawnList.FirstOrDefault()?.MapHeld;
                int bad = pawnList.Count(p => p.Downed || p.Faction != Faction.OfPlayer) + (ps.Count - pawnList.Count);
                int elsewhere = ts.Count(t => !t.Spawned || t.Map != map);
                string refusal = JawaBenchWreckReadsCore.FormRefusal(pawnList.Count, bad, elsewhere, ts.Count);
                if (refusal != null) return Fail(refusal + ".");
                if (destTile < 0) return Fail("Give destTile, the world tile to travel to.");
                IntVec3 exit;
                Pawn lead = pawnList.First();
                if (!CellFinder.TryFindRandomEdgeCellWith(c => c.Standable(map) && lead.CanReach(c, Verse.AI.PathEndMode.OnCell, Danger.Deadly),
                        map, CellFinder.EdgeRoadChance_Ignore, out exit))
                    return Fail("No map edge cell that " + lead.LabelShort + " can reach.");
                var transfer = new List<TransferableOneWay>();
                foreach (Thing t in ts)
                {
                    var tr = new TransferableOneWay();
                    tr.things.Add(t);
                    tr.AdjustTo(t.stackCount);
                    transfer.Add(tr);
                }
                var counts = pawnList.Select(p => new ThingCount(p, 1)).Concat(ts.Select(t => new ThingCount(t, t.stackCount))).ToList();
                float cap = CollectionsMassCalculator.Capacity(counts);
                float use = CollectionsMassCalculator.MassUsage(counts, IgnorePawnsInventoryMode.DontIgnore, false);
                CaravanFormingUtility.StartFormingCaravan(pawnList, new List<Pawn>(), Faction.OfPlayer, transfer, lead.Position, exit,
                    map.Tile, new PlanetTile(destTile));
                var lord = lead.GetLord();
                return (object)new
                {
                    success = lord != null && lord.LordJob is LordJob_FormAndSendCaravan,
                    lord = lord?.loadID, exit = new { x = exit.x, z = exit.z }, startTile = map.Tile.tileId, destTile,
                    things = ts.Select(t => t.ThingID).ToList(), capacity = cap, usage = use,
                    over = JawaBenchWreckReadsCore.OverCapacity(use, cap), ticksGame = TicksGameSafe()
                };
            }, cancellationToken);
        }

        // ================================================================
        //  jawa/reach_edge
        // ================================================================
        [Tool(
            "jawa/reach_edge",
            Description =
                "For each named cell: can a pawn get from it to the map's edge, by the game's own Reachability.CanReachMapEdge with " +
                "TraverseParms.For(mode). mode PassDoors (default) walks and opens doors; NoPassClosedDoors and NoPassClosedDoorsOrWater " +
                "are the other names. The engine walks regions, so no mode digs or breaks through a wall: the destroyable-things modes " +
                "and any unknown mode are REFUSED, never defaulted. A cell inside a building is read from the building's interaction cell when it has one, else " +
                "from the first standable cell beside the building. Reads only.",
            ResultDescription = "success, mode, cells[] (x, z, from (x, z), canReachEdge, why).")]
        public static async Task<object> ReachEdge(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cells 'x,z;x,z;...'.")] string cells = null,
            [ToolParameter(Description = "PassDoors (default), NoPassClosedDoors or NoPassClosedDoorsOrWater.")]
            string mode = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string err;
                Map map = MapOrNull(out err);
                if (map == null) return Fail(err);
                string m = JawaBenchWreckReadsCore.TraverseModeName(mode);
                if (m == null) return Fail("Unknown mode '" + mode + "'.", new { modes = JawaBenchWreckReadsCore.TraverseModes });
                var tm = (TraverseMode)Enum.Parse(typeof(TraverseMode), m);
                var rows = new List<object>();
                foreach (string part in (cells ?? "").Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    var xz = part.Split(',');
                    int x, z;
                    if (xz.Length != 2 || !int.TryParse(xz[0].Trim(), out x) || !int.TryParse(xz[1].Trim(), out z))
                        return Fail("Cell '" + part + "' is not 'x,z'.");
                    var c = new IntVec3(x, 0, z);
                    if (!c.InBounds(map)) { rows.Add(new { x, z, from = (object)null, canReachEdge = (bool?)null, why = "outside the map" }); continue; }
                    IntVec3 from = c;
                    Building b = c.GetFirstBuilding(map);
                    if (b != null && !c.Standable(map))
                    {
                        if (b.def.hasInteractionCell) from = b.InteractionCell;
                        else
                        {
                            from = IntVec3.Invalid;
                            foreach (IntVec3 a in GenAdj.CellsAdjacent8Way(b))
                                if (a.InBounds(map) && a.Standable(map)) { from = a; break; }
                            if (!from.IsValid)
                            { rows.Add(new { x, z, from = (object)null, canReachEdge = (bool?)false, why = "no standable cell beside the building" }); continue; }
                        }
                    }
                    bool ok = map.reachability.CanReachMapEdge(from, TraverseParms.For(tm));
                    rows.Add(new { x, z, from = new { x = from.x, z = from.z }, canReachEdge = (bool?)ok, why = (string)null });
                }
                return (object)new { success = true, mode = m, cells = rows, ticksGame = TicksGameSafe() };
            }, cancellationToken);
        }
    }
}
