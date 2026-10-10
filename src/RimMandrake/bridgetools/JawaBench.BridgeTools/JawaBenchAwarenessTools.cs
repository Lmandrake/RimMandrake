// JawaBenchAwarenessTools.cs - map awareness read tools: jawa/thing_explain, jawa/incident_journal, jawa/pawn_origin,
// jawa/awareness (status / arm / switches / measured cost), jawa/wild_spawner_block.
//
// Items THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER, INCIDENT_JOURNAL_BUILD_CALLED_IS_NOT_FIRED,
// PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN. Doc: design/RimMandrake/map_awareness.md. Recorder: JawaBenchAwareness.cs; pure
// rules: JawaBenchAwarenessCore.cs (unit-tested offline in bridgetools/AwarenessSelfTest).
//
// RimSage-verified members used here (decompiled 1.6, 2026-10-10):
//   Verse/ContentFinder.cs     Get<T>: walks LoadedModManager.RunningModsListForReading from the END, first hit wins,
//                              then base Resources, then asset bundles
//   Verse/ModContentHolder.cs  Get(path): a pure dictionary lookup (loads nothing)
//   Verse/PawnRenderTree.cs    BodyGraphic calls TrySetupGraphIfNeeded -> read ONLY when `Resolved` (never force a graph)
//   Verse/PawnRenderer.cs      public PawnRenderTree renderTree ; Verse/Pawn_AgeTracker CurKindLifeStage (animals only:
//                              it logs an error for a humanlike) ; Verse/PawnKindLifeStage bodyGraphicData/femaleGraphicData
//   Verse/Def.cs               public ModContentPack modContentPack (the DEFINING pack: not XML patchers, not textures)
//   Verse/LookTargets.cs       no ToString override (why jawa/letter_list now also emits lookTargetIds)
//
// LAWS: one selector, never a silent pick between ambiguous matches; the defining mod is never named as the texture
// supplier; an appearance provider is OBSERVED only when the rendered texture object was matched to a pack, else
// CANDIDATE (last running pack holding the path) or UNKNOWN; origin text comes from the core's Statement(), never
// "caused by".

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI.Group;
using A = JawaBench.BridgeTools.JawaBenchAwarenessCore;
using AW = JawaBench.BridgeTools.JawaBenchAwareness;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ================================================================ jawa/awareness
        [Tool(
            "jawa/awareness",
            Description =
                "Map awareness recorder status and control (incident journal + pawn origin recorder). action=status " +
                "(default): install status, recording epoch, retained rows, evictions, faults, per-metric switches and " +
                "MEASURED cost per hook call. action=arm minutes=N: write awareness rows into the TPS record (kind " +
                "'awareness') for N minutes (default 30, max 240). action=disarm. action=switch metric=<id> on=true|false: " +
                "turn one metric on or off for this session (the file JawaBench/tps/awareness_settings.json sets launch defaults).",
            ResultDescription = "success, installed, installStatus, startedBy, epoch, counts, evictions, switches, meters, disk.")]
        public static async Task<object> Awareness(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "status | arm | disarm | switch", DefaultValue = "status")] string action = "status",
            [ToolParameter(Description = "arm: minutes (default 30, max 240)", DefaultValue = 30)] double minutes = 30,
            [ToolParameter(Description = "switch: metric id (aware.*)", DefaultValue = null)] string metric = null,
            [ToolParameter(Description = "switch: true = on", DefaultValue = true)] bool on = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                AW.EnsureInstalled();
                var a = (action ?? "status").Trim().ToLowerInvariant();
                if (a == "arm") AW.DiskArm.Set(DateTime.UtcNow, minutes, "jawa/awareness");
                else if (a == "disarm") AW.DiskArm.Clear();
                else if (a == "switch")
                {
                    if (string.IsNullOrWhiteSpace(metric) || !AW.Sw.Set(metric.Trim(), on))
                        return Fail("unknown metric id '" + metric + "'", new { metricIds = A.MetricIds });
                }
                else if (a != "status") return Fail("action must be status, arm, disarm or switch");
                return AwarenessStatus();
            }, cancellationToken).ConfigureAwait(false);
        }

        private static object AwarenessStatus()
        {
            var r = AW.Rec;
            double f = System.Diagnostics.Stopwatch.Frequency;
            lock (r.Gate)
            {
                return new
                {
                    success = true,
                    installed = AW.InstallStatus == "complete" || AW.InstallStatus == "partial",
                    installStatus = AW.InstallStatus, installDetail = AW.InstallDetail, startedBy = AW.StartedBy,
                    installedUtc = AW.InstalledUtc.ToString("o"), settings = AW.SettingsPath, settingsNote = AW.Sw.Note,
                    epoch = r.Epoch, seq = r.Seq, installSeq = r.InstallSeq,
                    retained = new { generationTags = r.Tags.Count, spawns = r.Spawns.Snapshot().Count, incidents = r.Incidents.Snapshot().Count, seen = r.Seen.Count },
                    evictions = new { generationTags = r.Tags.Evicted, seen = r.Seen.Evicted, spawns = r.Spawns.Overwritten, incidents = r.Incidents.Overwritten },
                    untaggedGenerations = r.UntaggedGenerations, loadRespawns = r.LoadRespawns, lateRowsDropped = r.LateRowsDropped,
                    scopesTruncated = A.Scope.Truncated, scopesUnbalanced = A.Scope.Unbalanced,
                    faults = r.Faults, lastFault = r.LastFault,
                    switches = AW.Sw.Snapshot(),
                    meters = A.MetricIds.ToDictionary(id => id, id => (object)new
                    {
                        calls = AW.Meters[id].Calls,
                        meanUs = Math.Round(AW.Meters[id].MeanUs(f), 3), maxUs = Math.Round(AW.Meters[id].MaxUs(f), 1),
                        totalMs = Math.Round(AW.Meters[id].TotalMs(f), 3),
                        note = "hook body only; Harmony dispatch not included"
                    }),
                    disk = new { armed = AW.DiskArm.Armed(DateTime.UtcNow), until = AW.DiskArm.Until == DateTime.MinValue ? null : AW.DiskArm.Until.ToString("o"),
                                 rows = AW.DiskRows, dropped = AW.DiskDropped, writerRunning = JawaBenchTpsWriter.Running },
                    wildSpawner = new { blocked = AW.WildBlocked, skippedTicks = AW.WildSkipped, patch = AW.WildPatch },
                    ticksGame = TicksGameSafe()
                };
            }
        }

        // ================================================================ jawa/wild_spawner_block
        [Tool(
            "jawa/wild_spawner_block",
            Description =
                "Quiet-world control: block the map's ONGOING wild-animal replenishment (WildAnimalSpawner." +
                "WildAnimalSpawnerTick, called from Map.MapPreTick - the only ongoing replenish path in decompiled 1.6). " +
                "Mapgen wildlife (GenStep_Animals) and deliberate spawns are untouched. action=block | release | get. " +
                "Read back `blocked` and `skippedTicks` (calls skipped since the block): a block that skips nothing over " +
                "1213+ ticks has not been exercised, not proven.",
            ResultDescription = "success, blocked, skippedTicks, patch.")]
        public static async Task<object> WildSpawnerBlock(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "block | release | get", DefaultValue = "get")] string action = "get")
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                var a = (action ?? "get").Trim().ToLowerInvariant();
                if (a == "block")
                {
                    var err = AW.EnsureWildPatch();
                    if (err != null) return Fail("could not patch the wild spawner: " + err);
                    AW.WildBlocked = true;
                }
                else if (a == "release") AW.WildBlocked = false;
                else if (a != "get") return Fail("action must be block, release or get");
                return new { success = true, blocked = AW.WildBlocked, skippedTicks = AW.WildSkipped, patch = AW.WildPatch,
                             switchOn = AW.Sw.On(A.MWild), ticksGame = TicksGameSafe() };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================ jawa/incident_journal
        [Tool(
            "jawa/incident_journal",
            Description =
                "Every IncidentWorker.TryExecute CALL since the recorder installed (storyteller, queue, quests, scenario " +
                "parts, mods, our own tools): def, target, parms, the context chain, and HONEST outcome fields - " +
                "outerBodyRan (from __runOriginal), returned, exception (observed, never swallowed), workerEntered " +
                "(false only on the one established early-return branch, else unknown). 'Called' is not 'fired'.",
            ResultDescription = "success, installed, rows[], overwritten, oldestRetainedSeq, epoch.")]
        public static async Task<object> IncidentJournal(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Only rows with aseq > this.", DefaultValue = -1)] long sinceSeq = -1,
            [ToolParameter(Description = "Max rows (newest kept).", DefaultValue = 200)] int limit = 200)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                AW.EnsureInstalled();
                var all = AW.Rec.Incidents.Snapshot();
                var rows = all.Where(r => r.Seq > sinceSeq).ToList();
                int cut = Math.Max(0, rows.Count - Math.Max(1, limit));
                rows = rows.Skip(cut).ToList();
                return new
                {
                    success = true,
                    installed = AW.InstallStatus == "complete" || AW.InstallStatus == "partial", installStatus = AW.InstallStatus,
                    switchOn = AW.Sw.On(A.MIncident), epoch = AW.Rec.Epoch,
                    overwritten = AW.Rec.Incidents.Overwritten, oldestRetainedSeq = all.Count > 0 ? all[0].Seq : -1,
                    truncatedByLimit = cut,
                    rows = rows.Select(r => new
                    {
                        aseq = r.Seq, epoch = r.Epoch, tick = r.Tick, def = r.Def, target = r.Target, faction = r.Faction,
                        forced = r.Forced, points = r.Points, strategy = r.Strategy, arrival = r.Arrival, quest = r.Quest,
                        called = true, outerBodyRan = r.OuterBodyRan, returned = r.Returned, exception = r.Exception,
                        workerEntered = r.WorkerEntered, workerEnteredWhy = r.WorkerEnteredWhy,
                        pawnsGeneratedDuring = r.PawnsGeneratedDuring, pawnsSpawnedDuring = r.PawnsSpawnedDuring,
                        chain = r.Chain, statement = A.IncidentStatement(r)
                    }).ToList(),
                    coverage = "TryExecute calls only; an incident body a mod runs without TryExecute is not seen, and deferred " +
                               "deliveries (drop pods, shuttles) land after the call",
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        // ================================================================ jawa/pawn_origin
        [Tool(
            "jawa/pawn_origin",
            Description =
                "What the origin recorder observed for pawns: the generation observation (context chain at " +
                "PawnGenerator.GeneratePawn, new vs reused) and the latest spawn observation (Pawn.SpawnSetup, never on " +
                "load: firstObservedSpawn | observedRespawn | mapTransfer | unknown), with a statement that never claims " +
                "more than that ('origin unknown' when nothing was recorded). ids: comma-separated ThingIDs; omit for " +
                "every spawned pawn on the current map.",
            ResultDescription = "success, installed, epoch, pawns[] (id, kind, generation, spawn, ourInvolvement, statement), health.")]
        public static async Task<object> PawnOrigin(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ThingIDs (bare or Thing_ prefixed).", DefaultValue = null)] string ids = null,
            [ToolParameter(Description = "Cap on rows.", DefaultValue = 500)] int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                AW.EnsureInstalled();
                int ep = AW.Rec.EpochFor(Current.Game);
                var pawns = new List<Pawn>();
                var missing = new List<string>();
                if (!string.IsNullOrWhiteSpace(ids))
                {
                    var want = new HashSet<string>(ids.Split(',').Select(s => s.Trim()).Where(s => s.Length > 0)
                                                     .Select(s => s.StartsWith("Thing_") ? s.Substring(6) : s));
                    foreach (var p in AllPawnsEverywhere()) if (want.Remove(p.ThingID)) pawns.Add(p);
                    missing.AddRange(want);
                }
                else if (Find.CurrentMap != null) pawns.AddRange(Find.CurrentMap.mapPawns.AllPawnsSpawned);
                var rows = new List<object>();
                foreach (var p in pawns.Take(Math.Max(1, limit)))
                {
                    A.GenObs g; A.SpawnObs s;
                    lock (AW.Rec.Gate) AW.Rec.Tags.TryGet(p.thingIDNumber, out g);
                    s = AW.Rec.LatestSpawnOf(p.thingIDNumber);
                    string root = g?.RootKind;
                    rows.Add(new
                    {
                        id = p.ThingID, kind = p.kindDef?.defName,
                        generation = g == null ? null : (object)new { seq = g.Seq, tick = g.Tick, chain = g.Chain, cause = g.Cause, reuse = g.Reuse, reobserved = g.Reobserved, thread = g.Thread },
                        spawn = s == null ? null : (object)new { seq = s.Seq, tick = s.Tick, map = s.MapId, classification = s.Classification, spawnChain = s.SpawnChain, ranOriginal = s.RanOriginal },
                        ourInvolvement = A.Involvement(root),
                        statement = s != null ? A.Statement(s)
                                  : g != null ? "generated or selected during " + g.Chain + "; no spawn observed in this recording epoch"
                                  : A.Statement(null)
                    });
                }
                return new
                {
                    success = true,
                    installed = AW.InstallStatus == "complete" || AW.InstallStatus == "partial", installStatus = AW.InstallStatus,
                    startedBy = AW.StartedBy, epoch = ep, notFound = missing, pawns = rows,
                    health = new { untaggedGenerations = AW.Rec.UntaggedGenerations, tagEvictions = AW.Rec.Tags.Evicted,
                                   seenEvictions = AW.Rec.Seen.Evicted, spawnOverwritten = AW.Rec.Spawns.Overwritten, faults = AW.Rec.Faults },
                    limits = "provenance does not survive a save/load (a load opens a new epoch); a pawn present before install " +
                             "reads 'origin unknown'; ourInvolvement confirmedIndirectAction means generated DURING one of our " +
                             "bridge operations, never 'made on purpose by us'",
                    ticksGame = TicksGameSafe()
                };
            }, cancellationToken).ConfigureAwait(false);
        }

        private static IEnumerable<Pawn> AllPawnsEverywhere()
        {
            foreach (var m in Find.Maps) foreach (var p in m.mapPawns.AllPawns) yield return p;
            if (Find.WorldPawns != null) foreach (var p in Find.WorldPawns.AllPawnsAliveOrDead) yield return p;
        }

        // ================================================================ jawa/thing_explain
        [Tool(
            "jawa/thing_explain",
            Description =
                "'What is that?' in one call. Exactly ONE selector: id (ThingID), cell 'x,z' (current map), name (pawn " +
                "name or label, current map) or selected=true. Several matches are LISTED, never silently picked. Answers " +
                "the definition chain (PawnKindDef -> race ThingDef -> runtime type) with each def's DEFINING mod (not XML " +
                "patchers), faction/state, the origin recorder's statement, and appearance: texture paths with the mods that " +
                "hold each (load order), the provider labelled OBSERVED only when the rendered texture was matched, else " +
                "CANDIDATE. The defining mod is never reported as the texture supplier. Hover targets are not supported.",
            ResultDescription = "success, resolved | ambiguous[] , what{}, owners[], appearance{}, origin{}.")]
        public static async Task<object> ThingExplain(
            IRimBridgeContext ctx, CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingID (bare or Thing_ prefixed).", DefaultValue = null)] string id = null,
            [ToolParameter(Description = "Cell 'x,z' on the current map.", DefaultValue = null)] string cell = null,
            [ToolParameter(Description = "Pawn name or label on the current map (case-insensitive).", DefaultValue = null)] string name = null,
            [ToolParameter(Description = "Explain the current selection.", DefaultValue = false)] bool selected = false)
        {
            var problem = A.SelectorProblem(id, cell, name, selected);
            if (problem != null) return Fail(problem);
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
                try
                {
                    AW.EnsureInstalled();
                    var map = Find.CurrentMap;
                    var cands = new List<Thing>();
                    string how;
                    if (!string.IsNullOrWhiteSpace(id))
                    {
                        string tid = id.Trim().StartsWith("Thing_") ? id.Trim().Substring(6) : id.Trim();
                        how = "id";
                        foreach (var m in Find.Maps) foreach (var t in m.listerThings.AllThings) if (t.ThingID == tid) cands.Add(t);
                        if (cands.Count == 0) foreach (var p in AllPawnsEverywhere()) if (p.ThingID == tid && !cands.Contains(p)) cands.Add(p);
                    }
                    else if (!string.IsNullOrWhiteSpace(cell))
                    {
                        how = "cell";
                        if (map == null) return Fail("No current map.");
                        var parts = cell.Split(',');
                        if (parts.Length != 2 || !int.TryParse(parts[0].Trim(), out var cx) || !int.TryParse(parts[1].Trim(), out var cz))
                            return Fail("cell must be 'x,z'");
                        var c = new IntVec3(cx, 0, cz);
                        if (!c.InBounds(map)) return Fail("cell outside the map");
                        cands.AddRange(map.thingGrid.ThingsListAt(c));
                    }
                    else if (!string.IsNullOrWhiteSpace(name))
                    {
                        how = "name";
                        if (map == null) return Fail("No current map.");
                        string n = name.Trim();
                        foreach (var p in map.mapPawns.AllPawnsSpawned)
                            if (string.Equals(p.Name?.ToStringShort, n, StringComparison.OrdinalIgnoreCase)
                                || string.Equals(p.LabelShort, n, StringComparison.OrdinalIgnoreCase)) cands.Add(p);
                    }
                    else
                    {
                        how = "selected";
                        foreach (var o in Find.Selector.SelectedObjects) if (o is Thing t) cands.Add(t);
                    }
                    if (cands.Count == 0) return Fail("nothing matched the " + how + " selector", new { selector = how });
                    if (cands.Count > 1)
                        return new
                        {
                            success = true, resolved = false, selector = how,
                            ambiguous = cands.Take(50).Select(t => new { id = t.ThingID, label = t.LabelShort, def = t.def?.defName, type = t.GetType().Name,
                                                                       x = t.PositionHeld.x, z = t.PositionHeld.z }).ToList(),
                            message = cands.Count + " things match; pass one id. The tool never picks.",
                            ticksGame = TicksGameSafe()
                        };
                    return Explain(cands[0], how);
                }
                finally { AW.M(A.MExplain).Add(System.Diagnostics.Stopwatch.GetTimestamp() - t0); }
            }, cancellationToken).ConfigureAwait(false);
        }

        private static object PackRow(Def d) => d == null ? null : new
        {
            def = d.defName, type = d.GetType().Name,
            definingPackage = d.modContentPack?.PackageId, definingMod = d.modContentPack?.Name,
            note = "the DEFINING pack only; XML patches from other mods are not tracked"
        };

        private static object Explain(Thing t, string how)
        {
            var pawn = t as Pawn;
            var owners = new List<object> { PackRow(t.def) };
            if (pawn?.kindDef != null) owners.Insert(0, PackRow(pawn.kindDef));
            var rt = t.GetType();
            object state = null;
            if (pawn != null)
            {
                var ms = pawn.MentalStateDef;
                state = new
                {
                    faction = pawn.Faction?.def?.defName, isPlayer = pawn.Faction == Faction.OfPlayer,
                    factionHostileToPlayer = pawn.Faction != null && pawn.Faction.HostileTo(Faction.OfPlayer),
                    dead = pawn.Dead, downed = !pawn.Dead && pawn.Downed, spawned = pawn.Spawned,
                    mentalState = ms?.defName, aggroMental = ms != null && ms.IsAggro,
                    lordJob = pawn.GetLord()?.LordJob?.GetType().Name,
                    lordNote = "a lord job says what it is doing, not who made it"
                };
            }
            object origin = null;
            if (pawn != null)
            {
                A.GenObs g;
                lock (AW.Rec.Gate) AW.Rec.Tags.TryGet(pawn.thingIDNumber, out g);
                var s = AW.Rec.LatestSpawnOf(pawn.thingIDNumber);
                origin = new
                {
                    generationChain = g?.Chain, reuse = g?.Reuse, spawnClassification = s?.Classification,
                    ourInvolvement = A.Involvement(g?.RootKind),
                    statement = s != null ? A.Statement(s) : g != null ? "generated or selected during " + g.Chain : A.Statement(null)
                };
            }
            return new
            {
                success = true, resolved = true, selector = how,
                what = new
                {
                    id = t.ThingID, label = t.LabelCap.ToString(), def = t.def?.defName, pawnKind = pawn?.kindDef?.defName,
                    race = pawn != null ? t.def?.defName : null, runtimeType = rt.FullName, runtimeAssembly = rt.Assembly.GetName().Name,
                    x = t.PositionHeld.x, z = t.PositionHeld.z, map = t.MapHeld?.uniqueID
                },
                owners,
                state,
                origin,
                appearance = Appearance(t, pawn),
                ticksGame = TicksGameSafe()
            };
        }

        private static readonly string[] Facings = { "", "_south", "_east", "_north" };

        /// <summary>For each texture path a def configures: which running packs hold it (load order), the
        /// candidate winner, and OBSERVED when the rendered texture object is one of those packs' textures.</summary>
        private static object Appearance(Thing t, Pawn pawn)
        {
            var paths = new List<KeyValuePair<string, string>>();   // (role, texPath)
            string limits;
            Texture rendered = null;
            if (pawn != null && pawn.RaceProps != null && !pawn.RaceProps.Humanlike)
            {
                var ls = pawn.ageTracker?.CurKindLifeStage;
                if (ls?.bodyGraphicData?.texPath != null) paths.Add(new KeyValuePair<string, string>("body", ls.bodyGraphicData.texPath));
                if (ls?.femaleGraphicData?.texPath != null) paths.Add(new KeyValuePair<string, string>("body (female)", ls.femaleGraphicData.texPath));
                limits = "animal life-stage graphics only; alternate graphics, genes, apparel and custom render nodes are not resolved";
                try
                {
                    var tree = pawn.Drawer?.renderer?.renderTree;
                    if (tree != null && tree.Resolved) rendered = tree.BodyGraphic?.MatSouth?.mainTexture;   // Resolved: no graph is forced
                    else limits += "; render tree not resolved yet (never forced), so no OBSERVED provider";
                }
                catch (Exception e) { limits += "; rendered texture unreadable: " + e.GetType().Name; }
            }
            else if (pawn != null)
            {
                if (pawn.story?.bodyType?.bodyNakedGraphicPath != null) paths.Add(new KeyValuePair<string, string>("body type", pawn.story.bodyType.bodyNakedGraphicPath));
                if (pawn.story?.headType?.graphicPath != null) paths.Add(new KeyValuePair<string, string>("head type", pawn.story.headType.graphicPath));
                limits = "humanlike: body/head type paths only (body naked path is a prefix the renderer extends); apparel, " +
                         "hair, genes and render-tree nodes are not resolved: provider UNKNOWN beyond these candidates";
            }
            else
            {
                if (t.def?.graphicData?.texPath != null) paths.Add(new KeyValuePair<string, string>("graphic", t.def.graphicData.texPath));
                limits = "def graphicData only; a building's or item's runtime graphic overrides are not resolved";
            }
            var running = LoadedModManager.RunningModsListForReading;
            var rows = new List<object>();
            foreach (var kv in paths)
            {
                var holders = new List<string>();
                string observed = null;
                foreach (var pack in running)
                {
                    bool has = false;
                    foreach (var f in Facings)
                    {
                        var tex = pack.GetContentHolder<Texture2D>().Get(kv.Value + f);
                        if (tex == null) continue;
                        has = true;
                        if (rendered != null && ReferenceEquals(tex, rendered)) observed = pack.PackageId;
                    }
                    if (has) holders.Add(pack.PackageId);
                }
                var v = A.ProviderVerdict(holders, observed);
                rows.Add(new { role = kv.Key, texPath = kv.Value, packsHoldingPath = holders, provider = v[0], label = v[1], note = v[2] });
            }
            return new
            {
                paths = rows, limits,
                rule = "ContentFinder takes the LAST running mod holding the path (decompiled 1.6); the defining mod is not the painter"
            };
        }
    }
}
