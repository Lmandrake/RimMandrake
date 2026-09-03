// JawaBenchRenderTools.cs - Group K: map things & buildings, Anomaly, save/load side
// artifacts, rendering/camera/screenshots, terrain/roof/grids (room heat), and a
// diagnostics stat-explanation tool. See
// infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md (Group K) for the census
// this file answers.
//
// EVERY SIGNATURE READ FROM 1.6 SOURCE, NOT REMEMBERED - GenConstruct.cs, Frame.cs,
// PowerNet.cs, CompPowerTrader.cs, GameComponent_Anomaly.cs, CompHoldingPlatformTarget.cs,
// CompStudiable.cs, Game.cs (DeinitAndRemoveMap), GameDataSaveLoader.cs, GenFilePaths.cs,
// CustomXenotype.cs, Scenario.cs, Ideo.cs, PortraitsCache.cs, TextureAtlasHelper.cs,
// GlobalTextureAtlasManager.cs, Room.cs, GenTemperature.cs, StatWorker.cs, StatExtension.cs.
//
// ONE ROW WAS ALREADY BUILT AND IS SKIPPED HERE: "lock-weather" is jawa/weather_set's
// lockWeather=true path (GameConditionDef "WeatherController" via
// GameCondition_ForceWeather) - already registers a permanent forcing condition, which
// is exactly what this row asked for. See JawaBenchEventTools.cs.
//
// TWO DLC GUARDS THAT ARE NOT OPTIONAL:
//   - jawa/anomaly_monolith_set and jawa/anomaly_containment both require
//     ModsConfig.AnomalyActive. Find.Anomaly is a GameComponent that simply is not
//     added without the DLC, and CompHoldingPlatformTarget/CompStudiable are Anomaly
//     comps that will not exist on any def without it either.
//   - jawa/artifact_transfer's xenotype kind requires ModsConfig.BiotechActive
//     (pawn.genes is a Biotech tracker) and its ideo kind requires
//     ModsConfig.IdeologyActive (mirrors jawa/ideo_of's own guard).
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches game
// state - including RenderTexture/Texture2D work, which is Unity API and doubly
// unforgiving about this - is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.IO;
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
        // ================================================================
        //  jawa/blueprint_place
        // ================================================================
        [Tool(
            "jawa/blueprint_place",
            Description =
                "Place a REAL blueprint via GenConstruct.PlaceBlueprintForBuild - the same call " +
                "Designator_Build makes - so the colony's own construction WorkGivers pick it up and " +
                "build it, unlike jawa/build_batch's finished buildings. " +
                "Resolves 'def' as a ThingDef first, then a TerrainDef (for floors/bridges); a def with " +
                "no blueprintDef (BuildableByPlayer false) is REFUSED, not silently ignored. " +
                "🔑 Checked against GenConstruct.CanPlaceBlueprintAt before spawning - a cell that is " +
                "already occupied, out of the map, or otherwise invalid is refused WITH THE ENGINE'S OWN " +
                "REASON; pass ignoreValidity=true to force the spawn anyway (god-mode placement can " +
                "still succeed where the check fails). " +
                "⚠ If the def MADE FROM STUFF and no 'stuff' is given, GenStuff.DefaultStuffFor picks " +
                "one - it is never left null on a stuff-requiring def, which would otherwise silently " +
                "confuse the construction WorkGiver. " +
                "Faction defaults to the player colony ('Player'); an unresolved 'faction' name is " +
                "refused with the live faction list, never silently dropped to no-faction.",
            ResultDescription =
                "success, blueprint (id, defName, label, faction, stuff, position, rotation), " +
                "placementCheck (accepted, reason - from CanPlaceBlueprintAt, even when ignored).")]
        public static async Task<object> BlueprintPlace(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "ThingDef or TerrainDef defName to build, e.g. 'Wall' or 'PavedTile'.")]
            string def = null,
            [ToolParameter(Description = "Cell X.")] int x = -1,
            [ToolParameter(Description = "Cell Z.")] int z = -1,
            [ToolParameter(Description = "Rotation: north/east/south/west, n/e/s/w, or 0-3. Default north.")]
            string rot = "north",
            [ToolParameter(Description = "ThingDef defName for the stuff to build from. Omit to let GenStuff.DefaultStuffFor choose when the def requires stuff.")]
            string stuff = null,
            [ToolParameter(Description = "Faction defName, or 'Player' for the player colony (default).")]
            string faction = null,
            [ToolParameter(Description = "Skip GenConstruct.CanPlaceBlueprintAt and spawn regardless of what it says.")]
            bool ignoreValidity = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string merr;
                var map = MapOrNull(out merr);
                if (map == null) return Fail(merr);
                if (string.IsNullOrWhiteSpace(def)) return Fail("Give a ThingDef or TerrainDef name in 'def'.");
                if (x < 0 || z < 0 || x >= map.Size.x || z >= map.Size.z)
                    return Fail("Cell (" + x + "," + z + ") is outside the map.");

                BuildableDef entDef = DefDatabase<ThingDef>.GetNamedSilentFail(def.Trim());
                if (entDef == null) entDef = DefDatabase<TerrainDef>.GetNamedSilentFail(def.Trim());
                if (entDef == null)
                    return Fail("No ThingDef or TerrainDef '" + def + "'.",
                        new { suggestions = DefSuggestions<ThingDef>(def) });
                if (entDef.blueprintDef == null)
                    return Fail("'" + def + "' has no blueprintDef - it is not BuildableByPlayer, so " +
                                 "GenConstruct.PlaceBlueprintForBuild would crash making one.");

                Rot4 rotation;
                if (!TryRot(rot, out rotation))
                    return Fail("rot must be north/east/south/west, n/e/s/w, or 0-3, got '" + rot + "'.");

                ThingDef stuffDef = null;
                if (!string.IsNullOrWhiteSpace(stuff))
                {
                    stuffDef = DefDatabase<ThingDef>.GetNamedSilentFail(stuff.Trim());
                    if (stuffDef == null)
                        return Fail("No ThingDef '" + stuff + "' for stuff.", new { suggestions = DefSuggestions<ThingDef>(stuff) });
                }
                else if (entDef.MadeFromStuff)
                {
                    stuffDef = GenStuff.DefaultStuffFor(entDef);
                }

                Faction fac;
                if (string.IsNullOrWhiteSpace(faction))
                {
                    fac = Faction.OfPlayer;
                }
                else
                {
                    fac = ResolveFactionArg(faction);
                    if (fac == null) return FactionNotFound(faction);
                }

                var cell = new IntVec3(x, 0, z);
                AcceptanceReport check;
                try { check = GenConstruct.CanPlaceBlueprintAt(entDef, cell, rotation, map, false, null, null, stuffDef); }
                catch (Exception ex) { check = new AcceptanceReport("CanPlaceBlueprintAt threw: " + ex.GetType().Name + ": " + ex.Message); }

                if (!check.Accepted && !ignoreValidity)
                    return Fail("Placement refused by the engine: " + check.Reason, new
                    {
                        placementCheck = new { accepted = false, reason = check.Reason }
                    });

                Blueprint_Build bp;
                try { bp = GenConstruct.PlaceBlueprintForBuild(entDef, cell, map, rotation, fac, stuffDef); }
                catch (Exception ex) { return Fail("PlaceBlueprintForBuild threw: " + ex.GetType().Name + ": " + ex.Message); }
                if (bp == null) return Fail("PlaceBlueprintForBuild returned null.");

                return new
                {
                    success = true,
                    message = "Blueprint for '" + def + "' placed at (" + x + "," + z + ").",
                    blueprint = new
                    {
                        id = bp.ThingID,
                        defName = entDef.defName,
                        label = bp.LabelCap.ToString(),
                        faction = fac != null ? fac.def.defName : null,
                        stuff = stuffDef != null ? stuffDef.defName : null,
                        position = new { x = bp.Position.x, z = bp.Position.z },
                        rotation = rotation.ToString()
                    },
                    placementCheck = new { accepted = check.Accepted, reason = check.Reason },
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/frame_finish
        // ================================================================
        [Tool(
            "jawa/frame_finish",
            Description =
                "Instantly complete a construction Frame via Frame.CompleteConstruction(worker) - the " +
                "exact call a pawn's finishing swing makes, regardless of how many materials have " +
                "actually been delivered to it. The Frame is DESTROYED and replaced by the real thing " +
                "(or terrain) as a side effect; this tool then reports whatever now occupies that cell. " +
                "⚠ ⛔ REQUIRES A REAL, RESOLVABLE WORKER PAWN - Frame.CompleteConstruction reads " +
                "worker.Faction and calls worker.records/GetLord() internally and NREs on a null worker, " +
                "so 'worker' is refused up front rather than passed through to crash the call. " +
                "⚠ Quality (if any) is rolled from the WORKER's Construction skill " +
                "(QualityUtility.GenerateQualityCreatedByPawn), so the worker you name affects the " +
                "result, not just whether the call succeeds.",
            ResultDescription =
                "success, sourceFrame (id, entityDefToBuild, position, map), worker, " +
                "resultThings[] (id, defName, label, category) actually found at that cell afterward.")]
        public static async Task<object> FrameFinish(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id of the Frame, as returned by jawa/list_things.")]
            string thing = null,
            [ToolParameter(Description = "Pawn id/name to credit as the worker who finished it. Required - CompleteConstruction NREs on null.")]
            string worker = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = SystemToolsFindThing(thing, out terr);
                if (t == null) return Fail(terr ?? "No thing.");
                var frame = t as Frame;
                if (frame == null)
                    return Fail(t.ThingID + " is a " + (t.def != null ? t.def.defName : t.GetType().Name) +
                                ", not a Frame. Only an in-progress construction frame can be force-finished.");
                if (!frame.Spawned)
                    return Fail(frame.ThingID + " is not Spawned.");

                string werr;
                var workerPawn = FindPawn(worker, out werr);
                if (workerPawn == null) return Fail(werr ?? "No worker pawn. CompleteConstruction requires one.");

                var frameId = frame.ThingID;
                var entityDefToBuild = frame.def != null && frame.def.entityDefToBuild != null ? frame.def.entityDefToBuild.defName : null;
                var pos = frame.Position;
                var map = frame.Map;

                try { frame.CompleteConstruction(workerPawn); }
                catch (Exception ex) { return Fail("CompleteConstruction threw: " + ex.GetType().Name + ": " + ex.Message); }

                var resultThings = new List<object>();
                try
                {
                    foreach (var th in map.thingGrid.ThingsListAt(pos))
                    {
                        if (th.def == null || th.def.category == ThingCategory.Filth) continue;
                        resultThings.Add(new
                        {
                            id = th.ThingID,
                            defName = th.def.defName,
                            label = th.LabelCap.ToString(),
                            category = th.def.category.ToString()
                        });
                    }
                }
                catch { }

                return new
                {
                    success = true,
                    message = frameId + " (" + entityDefToBuild + ") force-completed by " + workerPawn.LabelShortCap + ".",
                    sourceFrame = new { id = frameId, entityDefToBuild, position = new { x = pos.x, z = pos.z }, map = map.Index },
                    worker = new { id = workerPawn.ThingID, name = workerPawn.LabelShortCap.ToString() },
                    resultThings,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/power_net
        // ================================================================
        [Tool(
            "jawa/power_net",
            Description =
                "Read a building's PowerNet - CurrentEnergyGainRate() and CurrentStoredEnergy(), plus " +
                "connector/transmitter/battery counts - and optionally force that ONE building's " +
                "CompPowerTrader.PowerOn directly, bypassing the net's own restart scheduling. " +
                "⚠ A thing with no CompPower at all is REFUSED, not reported as a net with zero of " +
                "everything. An unconnected CompPower (net == null) is a real, reportable state - " +
                "'connected: false' - not an error. " +
                "⚠ ⚠ forcePowerOn only works on a CompPowerTrader specifically - a battery, transmitter " +
                "or connector-only CompPower is refused by name, since PowerOn does not exist on those. " +
                "The setter itself can silently no-op (Log.Warning, no exception) if the parent does not " +
                "want to be on or is broken down, so powerOnAfter is READ BACK from the comp, never " +
                "assumed to equal what was requested.",
            ResultDescription =
                "success, thing (id, defName), connected, net (currentEnergyGainRate, " +
                "currentStoredEnergy, hasPowerSource, connectorsCount, transmittersCount, powerCompsCount, " +
                "batteryCompsCount) or null, isPowerTrader, powerOnBefore, powerOnAfter, " +
                "energyOutputPerTick.")]
        public static async Task<object> PowerNetTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id of a building carrying CompPower.")]
            string thing = null,
            [ToolParameter(Description = "Set CompPowerTrader.PowerOn on THIS building. Omit to only read.")]
            bool? forcePowerOn = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var t = SystemToolsFindThing(thing, out terr);
                if (t == null) return Fail(terr ?? "No thing.");
                var twc = t as ThingWithComps;
                if (twc == null) return Fail(t.ThingID + " is not a ThingWithComps - it cannot carry CompPower.");
                var cp = twc.GetComp<CompPower>();
                if (cp == null) return Fail(t.ThingID + " (" + (t.def != null ? t.def.defName : "?") + ") has no CompPower.");

                var net = cp.PowerNet;
                var trader = cp as CompPowerTrader;

                bool? before = trader != null ? trader.PowerOn : (bool?)null;
                bool? after = before;
                if (forcePowerOn.HasValue)
                {
                    if (trader == null)
                        return Fail("CompPower on " + t.ThingID + " is a " + cp.GetType().Name +
                                    ", not a CompPowerTrader - PowerOn cannot be forced on it.");
                    try { trader.PowerOn = forcePowerOn.Value; }
                    catch (Exception ex) { return Fail("Setting PowerOn threw: " + ex.GetType().Name + ": " + ex.Message); }
                    after = trader.PowerOn;
                }

                return new
                {
                    success = true,
                    message = net == null
                        ? t.ThingID + " has CompPower but is not connected to any PowerNet."
                        : t.ThingID + "'s net: gain " + net.CurrentEnergyGainRate() + " W/tick-day, stored " + net.CurrentStoredEnergy() + ".",
                    thing = new { id = t.ThingID, defName = t.def != null ? t.def.defName : null },
                    connected = net != null,
                    net = net == null ? null : (object)new
                    {
                        currentEnergyGainRate = net.CurrentEnergyGainRate(),
                        currentStoredEnergy = net.CurrentStoredEnergy(),
                        hasPowerSource = net.hasPowerSource,
                        connectorsCount = net.connectors.Count,
                        transmittersCount = net.transmitters.Count,
                        powerCompsCount = net.powerComps.Count,
                        batteryCompsCount = net.batteryComps.Count
                    },
                    isPowerTrader = trader != null,
                    powerOnBefore = before,
                    powerOnAfter = after,
                    energyOutputPerTick = trader != null ? (float?)trader.EnergyOutputPerTick : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/anomaly_monolith_set
        // ================================================================
        [Tool(
            "jawa/anomaly_monolith_set",
            Description =
                "Advance or reset the Anomaly monolith arc via Find.Anomaly.SetLevel(MonolithLevelDef, " +
                "silent) - the same call the monolith activation sequence makes. Fires " +
                "Notify_LevelChanged (and the MonolithLevelChanged signal) unless silent=true. " +
                "🔑 Read-only sibling is jawa/anomaly_monolith_get. " +
                "⚠ ⚠ REQUIRES ModsConfig.AnomalyActive - refused by name when the DLC is off, rather " +
                "than calling Find.Anomaly against a GameComponent that was never added.",
            ResultDescription = "success, levelBefore, levelDefBefore, levelAfter, levelDefAfter, changed.")]
        public static async Task<object> AnomalyMonolithSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "MonolithLevelDef defName to set.")]
            string levelDef = null,
            [ToolParameter(Description = "Suppress the level-change notification/signal.")]
            bool silent = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.AnomalyActive)
                    return Fail("ModsConfig.AnomalyActive is false. The Anomaly DLC is not active, so there is no monolith arc to set.");
                if (string.IsNullOrWhiteSpace(levelDef)) return Fail("Give a MonolithLevelDef defName in 'levelDef'.");

                var ld = DefDatabase<MonolithLevelDef>.GetNamedSilentFail(levelDef.Trim());
                if (ld == null) return Fail("No MonolithLevelDef '" + levelDef + "'.", new { suggestions = DefSuggestions<MonolithLevelDef>(levelDef) });

                var a = Find.Anomaly;
                if (a == null) return Fail("Find.Anomaly returned null (GameComponent_Anomaly missing from this game).");

                var beforeLevel = a.Level;
                var beforeDef = a.LevelDef != null ? a.LevelDef.defName : null;

                try { a.SetLevel(ld, silent); }
                catch (Exception ex) { return Fail("SetLevel threw: " + ex.GetType().Name + ": " + ex.Message); }

                var afterLevel = a.Level;
                var afterDef = a.LevelDef != null ? a.LevelDef.defName : null;

                return new
                {
                    success = true,
                    message = "Monolith level " + beforeLevel + " (" + beforeDef + ") -> " + afterLevel + " (" + afterDef + ").",
                    levelBefore = beforeLevel,
                    levelDefBefore = beforeDef,
                    levelAfter = afterLevel,
                    levelDefAfter = afterDef,
                    changed = beforeLevel != afterLevel,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/anomaly_containment
        // ================================================================

        // SystemToolsFindThing walks spawned things plus pawn equipment/apparel/inventory
        // and NOTHING ELSE. An entity that is actually ON a holding platform is DESPAWNED
        // into Building_HoldingPlatform.innerContainer (that is why the platform implements
        // IThingHolderWithDrawnPawn and draws the pawn itself), so it appears in neither
        // list - and that is precisely the state jawa/anomaly_containment exists to read.
        // Fall back to a recursive walk of every map's thing holders (platforms, caskets,
        // carry trackers) before reporting the entity as missing. alsoGetSpawnedThings is
        // false because SystemToolsFindThing already covered the spawned lister.
        private static Thing FindThingIncludingContainers(string id, out string err)
        {
            var t = SystemToolsFindThing(id, out err);
            if (t != null || string.IsNullOrWhiteSpace(id) || Find.Maps == null) return t;

            var tok = id.Trim();
            var bare = tok.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) ? tok.Substring(6) : tok;
            var contained = new List<Thing>();
            foreach (var m in Find.Maps)
            {
                try
                {
                    ThingOwnerUtility.GetAllThingsRecursively(
                        m, ThingRequest.ForGroup(ThingRequestGroup.Everything), contained,
                        true, null, false);
                }
                catch { continue; }
                for (int i = 0; i < contained.Count; i++)
                {
                    var h = contained[i];
                    if (h != null && (h.ThingID == tok || h.ThingID == bare)) { err = null; return h; }
                }
            }
            return null;
        }

        [Tool(
            "jawa/anomaly_containment",
            Description =
                "Read and optionally write an Anomaly entity's containment/study state - " +
                "CompHoldingPlatformTarget.containmentMode and CompStudiable's study fields. Omit every " +
                "setter to just read. " +
                "🔑 forceStudy calls CompStudiable.Study(studier, studyAmount, anomalyKnowledgeAmount) " +
                "DIRECTLY - it adds study progress and Anomaly Knowledge right now, it does NOT drive a " +
                "pawn to walk over and interact with the platform (there is no job simulation here). " +
                "⛔ THIS DOES NOT PHYSICALLY MOVE THE ENTITY ONTO A HOLDING PLATFORM - that is a job-driven " +
                "hauling/capture interaction (WorkGiver + JobDriver) out of scope for a direct field write; " +
                "only containmentMode and study state are touched. " +
                "⚠ ⚠ REQUIRES ModsConfig.AnomalyActive. A thing with no CompHoldingPlatformTarget is " +
                "REFUSED BY NAME, not reported as an empty containment state. " +
                "🔑 The entity is found whether it is loose on the map or DESPAWNED inside a holding " +
                "platform's container - a held entity is in no map thing list at all.",
            ResultDescription =
                "success, thing, containmentMode, canBeCaptured, canStudy, studiedAtHoldingPlatform, " +
                "currentlyHeldOnPlatform, isEscaping, extractBioferrite, heldPlatform (id or null), " +
                "studiable (present, studyEnabled, studyPoints, anomalyKnowledgeGained, progressPercent, " +
                "completed, ticksTilNextStudy, knowledgeCategory) or null if the entity has no CompStudiable.")]
        public static async Task<object> AnomalyContainment(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id of the entity (Pawn or item) carrying CompHoldingPlatformTarget.")]
            string thing = null,
            [ToolParameter(Description = "Set containmentMode: MaintainOnly, Study, Release, or Execute. Omit to leave unchanged.")]
            string containmentMode = null,
            [ToolParameter(Description = "Set CompStudiable.studyEnabled. Omit to leave unchanged. Refused if the entity has no CompStudiable.")]
            bool? studyEnabled = null,
            [ToolParameter(Description = "Call CompStudiable.Study(studier, studyAmount, anomalyKnowledgeAmount) once, right now.")]
            bool forceStudy = false,
            [ToolParameter(Description = "Pawn id/name credited as the studier. Required when forceStudy=true.")]
            string studier = null,
            [ToolParameter(Description = "Study amount passed to CompStudiable.Study. Default 1.")]
            float studyAmount = 1f,
            [ToolParameter(Description = "Anomaly Knowledge amount passed to CompStudiable.Study. Default 0 (let the comp's own rate apply).")]
            float anomalyKnowledgeAmount = 0f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.AnomalyActive)
                    return Fail("ModsConfig.AnomalyActive is false. Containment/study comps do not exist without the Anomaly DLC.");

                string terr;
                var t = FindThingIncludingContainers(thing, out terr);
                if (t == null) return Fail(terr ?? "No thing.");
                var twc = t as ThingWithComps;
                if (twc == null) return Fail(t.ThingID + " is not a ThingWithComps.");
                var comp = twc.GetComp<CompHoldingPlatformTarget>();
                if (comp == null)
                    return Fail(t.ThingID + " (" + (t.def != null ? t.def.defName : "?") + ") has no CompHoldingPlatformTarget - not an Anomaly containment-capable entity.");

                if (!string.IsNullOrWhiteSpace(containmentMode))
                {
                    EntityContainmentMode parsed;
                    if (!Enum.TryParse(containmentMode.Trim(), true, out parsed))
                        return Fail("Unknown containmentMode '" + containmentMode + "'. Valid: " + string.Join(", ", Enum.GetNames(typeof(EntityContainmentMode))));
                    comp.containmentMode = parsed;
                }

                var studiable = comp.CompStudiable;

                if (studyEnabled.HasValue)
                {
                    if (studiable == null) return Fail(t.ThingID + " has no CompStudiable - cannot set studyEnabled.");
                    try { studiable.SetStudyEnabled(studyEnabled.Value); }
                    catch (Exception ex) { return Fail("SetStudyEnabled threw: " + ex.GetType().Name + ": " + ex.Message); }
                }

                if (forceStudy)
                {
                    if (studiable == null) return Fail(t.ThingID + " has no CompStudiable - cannot force study.");
                    string swerr;
                    var studierPawn = FindPawn(studier, out swerr);
                    if (studierPawn == null) return Fail(swerr ?? "Give 'studier' (a pawn) when forceStudy=true.");
                    try { studiable.Study(studierPawn, studyAmount, anomalyKnowledgeAmount); }
                    catch (Exception ex) { return Fail("Study() threw: " + ex.GetType().Name + ": " + ex.Message); }
                }

                var heldPlatform = comp.HeldPlatform;

                return new
                {
                    success = true,
                    thing = new { id = t.ThingID, defName = t.def != null ? t.def.defName : null },
                    containmentMode = comp.containmentMode.ToString(),
                    canBeCaptured = comp.CanBeCaptured,
                    canStudy = comp.CanStudy,
                    studiedAtHoldingPlatform = comp.StudiedAtHoldingPlatform,
                    currentlyHeldOnPlatform = comp.CurrentlyHeldOnPlatform,
                    isEscaping = comp.isEscaping,
                    extractBioferrite = comp.extractBioferrite,
                    heldPlatform = heldPlatform != null ? heldPlatform.ThingID : null,
                    studiable = studiable == null ? null : (object)new
                    {
                        present = true,
                        studyEnabled = studiable.studyEnabled,
                        studyPoints = studiable.studyPoints,
                        anomalyKnowledgeGained = studiable.anomalyKnowledgeGained,
                        progressPercent = studiable.ProgressPercent,
                        completed = studiable.Completed,
                        ticksTilNextStudy = studiable.TicksTilNextStudy,
                        knowledgeCategory = studiable.KnowledgeCategory != null ? studiable.KnowledgeCategory.defName : null
                    },
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/map_drop
        // ================================================================
        [Tool(
            "jawa/map_drop",
            Description =
                "Free one map mid-session via Game.DeinitAndRemoveMap(map, notifyPlayer) - without " +
                "quitting to the main menu or saving. Deinits every map component, removes it from " +
                "Current.Game.Maps, and switches CurrentMap to whatever is left (or to the world view if " +
                "nothing is). " +
                "⚠ The Map object is DISPOSED by this call - nothing about it is readable afterward, so " +
                "this tool captures index/tile/label BEFORE calling and reports mapCountBefore/After as " +
                "the read-back proof, rather than touching the disposed object.",
            ResultDescription = "success, removedMap (index, tile, parentLabel), mapCountBefore, mapCountAfter.")]
        public static async Task<object> MapDrop(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Map index to remove. Omit (-1) to use the current map.")]
            int mapIndex = -1,
            [ToolParameter(Description = "Show the player the 'colony abandoned/map removed' notification.")]
            bool notifyPlayer = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                Map map = mapIndex < 0 ? Find.CurrentMap : Find.Maps.FirstOrDefault(m => m.Index == mapIndex);
                if (map == null) return Fail(mapIndex < 0 ? "No current map." : "No map with index " + mapIndex + ".");

                var removedIndex = map.Index;
                var removedTile = map.Tile;
                var removedLabel = map.Parent != null ? map.Parent.Label : null;
                var countBefore = Find.Maps.Count;

                try { Current.Game.DeinitAndRemoveMap(map, notifyPlayer); }
                catch (Exception ex) { return Fail("DeinitAndRemoveMap threw: " + ex.GetType().Name + ": " + ex.Message); }

                var countAfter = Find.Maps.Count;

                return new
                {
                    success = true,
                    message = "Map " + removedIndex + " (" + removedLabel + ") removed; " + countBefore + " -> " + countAfter + " map(s).",
                    removedMap = new { index = removedIndex, tile = removedTile, parentLabel = removedLabel },
                    mapCountBefore = countBefore,
                    mapCountAfter = countAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/artifact_transfer
        // ================================================================
        [Tool(
            "jawa/artifact_transfer",
            Description =
                "Save or load a side artifact file: a scenario (.rsc), an ideo (.rid), or a xenotype " +
                "(.xtp) - via GameDataSaveLoader.SaveScenario/SaveIdeo/SaveXenotype and " +
                "TryLoadScenario/TryLoadIdeo/TryLoadXenotype. Always takes an explicit absolute 'path' - " +
                "there is no default folder helper for scenario or ideo in 1.6 (only xenotype/modlist/" +
                "camera-config have GenFilePaths.AbsFilePathFor*, so this tool does not guess one for " +
                "the others either, for consistency). " +
                "🔑 kind=scenario saves/loads the CURRENT RUNNING Find.Scenario; there is no 'which " +
                "scenario' parameter because there is only ever one live. kind=ideo needs 'ideo' (id or " +
                "name substring, as jawa/ideo_of matches) on save. kind=xenotype needs 'pawn' on save - " +
                "the CustomXenotype is BUILT FROM THAT PAWN'S GENES (geneSource default 'xenogenes'). " +
                "⚠ A LOADED scenario/ideo/xenotype is NOT registered as the live one - Scribe just parses " +
                "the file and hands back the object. Loading does not start a new game, change the " +
                "running ideo, or grant genes to anyone; it is read-only proof the file round-trips. " +
                "⚠ ⚠ kind=ideo REQUIRES ModsConfig.IdeologyActive; kind=xenotype REQUIRES " +
                "ModsConfig.BiotechActive (pawn.genes is a Biotech tracker). " +
                "🔴 Every save is READ BACK via File.Exists + file size, not assumed from a successful " +
                "call - GameDataSaveLoader's Save* methods swallow their own exceptions (log and return), " +
                "so a write failure would otherwise show up only in Player.log.",
            ResultDescription =
                "success, kind, mode, path, and either saved{fileExists, fileSizeBytes, sourceSummary} " +
                "or loaded{...fields specific to the kind}.")]
        public static async Task<object> ArtifactTransfer(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'scenario', 'ideo', or 'xenotype'.")]
            string kind = null,
            [ToolParameter(Description = "'save' or 'load'.")]
            string mode = null,
            [ToolParameter(Description = "Absolute file path.")]
            string path = null,
            [ToolParameter(Description = "kind=ideo, mode=save: ideo id (number) or a substring of its name, as jawa/ideo_of matches.")]
            string ideo = null,
            [ToolParameter(Description = "kind=xenotype, mode=save: pawn id/name to build the CustomXenotype from.")]
            string pawn = null,
            [ToolParameter(Description = "kind=xenotype, mode=save: 'xenogenes' (default), 'endogenes', or 'all'.")]
            string geneSource = "xenogenes",
            [ToolParameter(Description = "kind=xenotype, mode=save: name for the saved xenotype. Defaults to '<Pawn>Xenotype'.")]
            string xenotypeName = null,
            [ToolParameter(Description = "kind=xenotype, mode=save: CustomXenotype.inheritable.")]
            bool inheritable = false,
            [ToolParameter(Description = "kind=xenotype, mode=save: XenotypeIconDef defName. Omit for the default icon.")]
            string iconDef = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (string.IsNullOrWhiteSpace(path)) return Fail("Give an absolute file path in 'path'.");
                var k = (kind ?? "").Trim().ToLowerInvariant();
                var m = (mode ?? "").Trim().ToLowerInvariant();
                if (k != "scenario" && k != "ideo" && k != "xenotype")
                    return Fail("kind must be 'scenario', 'ideo', or 'xenotype', got '" + kind + "'.");
                if (m != "save" && m != "load")
                    return Fail("mode must be 'save' or 'load', got '" + mode + "'.");

                if (k == "ideo" && !ModsConfig.IdeologyActive)
                    return Fail("ModsConfig.IdeologyActive is false. There is no ideo to save or load.");
                if (k == "xenotype" && !ModsConfig.BiotechActive)
                    return Fail("ModsConfig.BiotechActive is false. pawn.genes does not exist without Biotech.");

                // ---------------- SAVE ----------------
                if (m == "save")
                {
                    string sourceSummary;
                    try
                    {
                        if (k == "scenario")
                        {
                            var scen = Find.Scenario;
                            if (scen == null) return Fail("Find.Scenario is null.");
                            sourceSummary = scen.name;
                            GameDataSaveLoader.SaveScenario(scen, path);
                        }
                        else if (k == "ideo")
                        {
                            if (string.IsNullOrWhiteSpace(ideo)) return Fail("Give 'ideo' (id or name substring) to save.");
                            var mgr = Find.IdeoManager;
                            if (mgr == null) return Fail("No IdeoManager.");
                            var wanted = ideo.Trim();
                            int byId;
                            var isId = int.TryParse(wanted, out byId);
                            var picked = mgr.IdeosListForReading.Where(q => q != null).FirstOrDefault(q =>
                                (isId && q.id == byId)
                                || (q.name ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0);
                            if (picked == null)
                                return Fail("No ideo matched '" + ideo + "'.", new
                                {
                                    liveIdeos = mgr.IdeosListForReading.Where(q => q != null).Select(q => new { q.id, q.name }).ToList()
                                });
                            sourceSummary = picked.name;
                            GameDataSaveLoader.SaveIdeo(picked, path);
                        }
                        else // xenotype
                        {
                            if (string.IsNullOrWhiteSpace(pawn)) return Fail("Give 'pawn' to build the xenotype from.");
                            string perr;
                            var p = FindPawn(pawn, out perr);
                            if (p == null) return Fail(perr ?? "No pawn.");
                            if (p.genes == null) return Fail(p.LabelShortCap + " has no gene tracker.");

                            var gs = (geneSource ?? "xenogenes").Trim().ToLowerInvariant();
                            List<Gene> source;
                            if (gs == "xenogenes") source = p.genes.Xenogenes;
                            else if (gs == "endogenes") source = p.genes.Endogenes;
                            else if (gs == "all") source = p.genes.GenesListForReading;
                            else return Fail("geneSource must be 'xenogenes', 'endogenes', or 'all', got '" + geneSource + "'.");

                            var geneDefs = source.Where(g => g != null && g.def != null).Select(g => g.def).Distinct().ToList();
                            if (geneDefs.Count == 0)
                                return Fail(p.LabelShortCap + " has no genes in source '" + gs + "'. Nothing to save.");

                            XenotypeIconDef icon = null;
                            if (!string.IsNullOrWhiteSpace(iconDef))
                            {
                                icon = DefDatabase<XenotypeIconDef>.GetNamedSilentFail(iconDef.Trim());
                                if (icon == null) return Fail("No XenotypeIconDef '" + iconDef + "'.", new { suggestions = DefSuggestions<XenotypeIconDef>(iconDef) });
                            }

                            var cx = new CustomXenotype
                            {
                                name = string.IsNullOrWhiteSpace(xenotypeName) ? (p.LabelShortCap + "Xenotype") : xenotypeName.Trim(),
                                inheritable = inheritable,
                                iconDef = icon
                            };
                            cx.genes.AddRange(geneDefs);
                            sourceSummary = p.LabelShortCap + " (" + geneDefs.Count + " gene(s) from " + gs + ")";
                            GameDataSaveLoader.SaveXenotype(cx, path);
                        }
                    }
                    catch (Exception ex) { return Fail("Save threw: " + ex.GetType().Name + ": " + ex.Message); }

                    var exists = File.Exists(path);
                    long size = 0;
                    if (exists) { try { size = new FileInfo(path).Length; } catch { } }
                    if (!exists)
                        return Fail("Save call returned but the file does not exist at '" + path + "'. " +
                                     "GameDataSaveLoader swallows its own write exceptions - check Player.log.");

                    return new
                    {
                        success = true,
                        message = "Saved " + k + " to " + path + " (" + size + " bytes).",
                        kind = k,
                        mode = m,
                        path,
                        saved = new { fileExists = true, fileSizeBytes = size, sourceSummary },
                        ticksGame = TicksGameSafe()
                    };
                }

                // ---------------- LOAD ----------------
                if (!File.Exists(path)) return Fail("No file at '" + path + "'.");

                object loaded;
                try
                {
                    if (k == "scenario")
                    {
                        Scenario scen;
                        if (!GameDataSaveLoader.TryLoadScenario(path, ScenarioCategory.CustomLocal, out scen) || scen == null)
                            return Fail("TryLoadScenario returned false/null for '" + path + "'. Check Player.log.");
                        loaded = new { name = scen.name, summary = scen.summary, description = scen.description, partsCount = scen.AllParts != null ? scen.AllParts.Count() : 0 };   // AllParts, not parts: `parts` is internal to Assembly-CSharp
                    }
                    else if (k == "ideo")
                    {
                        Ideo ideoObj;
                        if (!GameDataSaveLoader.TryLoadIdeo(path, out ideoObj) || ideoObj == null)
                            return Fail("TryLoadIdeo returned false/null for '" + path + "'. Check Player.log.");
                        loaded = new { name = ideoObj.name, memeCount = ideoObj.memes.Count, memes = ideoObj.memes.Where(mm => mm != null).Select(mm => mm.defName).ToList() };
                    }
                    else
                    {
                        CustomXenotype xeno;
                        if (!GameDataSaveLoader.TryLoadXenotype(path, out xeno) || xeno == null)
                            return Fail("TryLoadXenotype returned false/null for '" + path + "'. Check Player.log.");
                        loaded = new { name = xeno.name, inheritable = xeno.inheritable, geneCount = xeno.genes.Count, genes = xeno.genes.Where(g => g != null).Select(g => g.defName).ToList() };
                    }
                }
                catch (Exception ex) { return Fail("Load threw: " + ex.GetType().Name + ": " + ex.Message); }

                return new
                {
                    success = true,
                    message = "Loaded " + k + " from " + path + ". NOT registered as the live " + k + " - this only proves the file round-trips.",
                    kind = k,
                    mode = m,
                    path,
                    loaded,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/pawn_portrait
        // ================================================================
        [Tool(
            "jawa/pawn_portrait",
            Description =
                "Render a pawn off-screen via PortraitsCache.Get - the same call the colonist bar and " +
                "character cards use - and write the result to a PNG via " +
                "TextureAtlasHelper.WriteDebugPNG(RenderTexture, path). " +
                "⚠ PortraitsCache caches by (pawn, size, rotation, ...) for ~1 real-time second and " +
                "reuses a stale frame within that window; pass forceDirty=true to call " +
                "PortraitsCache.SetDirty(pawn) first and guarantee a fresh render. " +
                "🔴 File write is READ BACK via File.Exists + size, not assumed from a successful call.",
            ResultDescription = "success, pawn, path, width, height, rotation, fileSizeBytes.")]
        public static async Task<object> PawnPortrait(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id/name, as accepted by jawa/pawn_stats.")]
            string pawn = null,
            [ToolParameter(Description = "Absolute output PNG path.")]
            string path = null,
            [ToolParameter(Description = "Render width in pixels. Default 256.")]
            int width = 256,
            [ToolParameter(Description = "Render height in pixels. Default 256.")]
            int height = 256,
            [ToolParameter(Description = "north/east/south/west, n/e/s/w, or 0-3. Default south.")]
            string rotation = "south",
            [ToolParameter(Description = "Render headgear.")] bool renderHeadgear = true,
            [ToolParameter(Description = "Render worn clothes.")] bool renderClothes = true,
            [ToolParameter(Description = "Call PortraitsCache.SetDirty(pawn) first to bypass the ~1s cache.")]
            bool forceDirty = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (string.IsNullOrWhiteSpace(path)) return Fail("Give an absolute output PNG path in 'path'.");
                if (width <= 0 || height <= 0) return Fail("width and height must be positive.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");

                Rot4 rot;
                if (!TryRot(rotation, out rot))
                    return Fail("rotation must be north/east/south/west, n/e/s/w, or 0-3, got '" + rotation + "'.");

                if (forceDirty) { try { PortraitsCache.SetDirty(p); } catch { } }

                // supersample/compensateForUIScale are OFF so the output PNG is exactly
                // width x height - PortraitsCache.Get otherwise multiplies size by 1.25
                // and Prefs.UIScale, which would make the returned dimensions a surprise.
                RenderTexture rt;
                try { rt = PortraitsCache.Get(p, new Vector2(width, height), rot, default(Vector3), 1f, false, false, renderHeadgear, renderClothes); }
                catch (Exception ex) { return Fail("PortraitsCache.Get threw: " + ex.GetType().Name + ": " + ex.Message); }
                if (rt == null) return Fail("PortraitsCache.Get returned null.");

                try { TextureAtlasHelper.WriteDebugPNG(rt, path); }
                catch (Exception ex) { return Fail("WriteDebugPNG threw: " + ex.GetType().Name + ": " + ex.Message); }

                if (!File.Exists(path)) return Fail("WriteDebugPNG returned but no file exists at '" + path + "'.");
                long size = 0;
                try { size = new FileInfo(path).Length; } catch { }

                return new
                {
                    success = true,
                    message = p.LabelShortCap + "'s portrait written to " + path + " (" + size + " bytes).",
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    path,
                    width = rt.width,
                    height = rt.height,
                    rotation = rot.ToString(),
                    fileSizeBytes = size,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/pawn_atlas
        // ================================================================
        [Tool(
            "jawa/pawn_atlas",
            Description =
                "mode=refresh: GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty(pawn) - force one " +
                "pawn's baked texture frames to redraw next frame, the fix for art that changed but " +
                "still shows the old bake. mode=dump: GlobalTextureAtlasManager.DumpPawnAtlases(folder) - " +
                "writes every currently-baked pawn atlas page as a PNG, for inspecting what actually got " +
                "packed. " +
                "⚠ refresh on a pawn with NO frame set yet allocated returns marked:false - that is a " +
                "real answer ('nothing to mark dirty yet'), not a failure. " +
                "⚠ dump requires 'folder' to already exist or be creatable - this tool tries " +
                "Directory.CreateDirectory first - and the result is READ BACK by listing the dump_*.png " +
                "files actually written, not assumed from the call returning.",
            ResultDescription =
                "success, mode, and either {pawn, marked} for refresh or {folder, filesWritten[]} for dump.")]
        public static async Task<object> PawnAtlas(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'refresh' or 'dump'.")]
            string mode = null,
            [ToolParameter(Description = "mode=refresh: pawn id/name.")]
            string pawn = null,
            [ToolParameter(Description = "mode=dump: absolute output folder.")]
            string folder = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                var mo = (mode ?? "").Trim().ToLowerInvariant();

                if (mo == "refresh")
                {
                    if (string.IsNullOrWhiteSpace(pawn)) return Fail("Give 'pawn' for mode=refresh.");
                    string perr;
                    var p = FindPawn(pawn, out perr);
                    if (p == null) return Fail(perr ?? "No pawn.");

                    bool marked;
                    try { marked = GlobalTextureAtlasManager.TryMarkPawnFrameSetDirty(p); }
                    catch (Exception ex) { return Fail("TryMarkPawnFrameSetDirty threw: " + ex.GetType().Name + ": " + ex.Message); }

                    return new
                    {
                        success = true,
                        message = marked ? p.LabelShortCap + "'s frame set marked dirty." : p.LabelShortCap + " has no allocated frame set yet - nothing to mark.",
                        mode = mo,
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        marked,
                        ticksGame = TicksGameSafe()
                    };
                }

                if (mo == "dump")
                {
                    if (string.IsNullOrWhiteSpace(folder)) return Fail("Give an absolute output folder in 'folder' for mode=dump.");
                    try { Directory.CreateDirectory(folder); }
                    catch (Exception ex) { return Fail("Could not create/access folder '" + folder + "': " + ex.GetType().Name + ": " + ex.Message); }

                    try { GlobalTextureAtlasManager.DumpPawnAtlases(folder); }
                    catch (Exception ex) { return Fail("DumpPawnAtlases threw: " + ex.GetType().Name + ": " + ex.Message); }

                    List<string> written;
                    try { written = Directory.GetFiles(folder, "dump_*.png").ToList(); }
                    catch { written = new List<string>(); }

                    return new
                    {
                        success = true,
                        message = written.Count + " atlas PNG(s) written to " + folder + ".",
                        mode = mo,
                        folder,
                        filesWritten = written,
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("mode must be 'refresh' or 'dump', got '" + mode + "'.");
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/room_heat
        // ================================================================
        [Tool(
            "jawa/room_heat",
            Description =
                "mode=set: write Room.Temperature directly at the room touching (x,z). mode=push: add " +
                "or remove energy via GenTemperature.PushHeat(cell, map, energy) - the same call an " +
                "explosion or a heater's tick uses; a heatless (unroofed) cell spreads the energy across " +
                "its roofed 8-way neighbor rooms instead of failing. " +
                "⚠ EqualizeTemperature runs every room-temperature tick and drags the result back toward " +
                "ambient over time - a pushed or set value is a ONE-TIME nudge, not a lock. " +
                "⚠ A cell with no room (outdoors, or fully unroofed with no roofed neighbor) is REFUSED " +
                "for mode=set (Room.Temperature has no meaning there) and reported as pushed:false for " +
                "mode=push (a true, unforced answer - not an error).",
            ResultDescription =
                "success, mode, cell, and for mode=set: roomId, temperatureBefore, temperatureAfter; " +
                "for mode=push: pushed, directRoom (id, temperature) or null if the energy went to " +
                "neighbor rooms instead.")]
        public static async Task<object> RoomHeat(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Cell X.")] int x = -1,
            [ToolParameter(Description = "Cell Z.")] int z = -1,
            [ToolParameter(Description = "'set' or 'push'.")]
            string mode = null,
            [ToolParameter(Description = "mode=set: target temperature in °C. mode=push: energy to add (negative to remove).")]
            float value = 0f)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                string merr;
                var map = MapOrNull(out merr);
                if (map == null) return Fail(merr);
                if (x < 0 || z < 0 || x >= map.Size.x || z >= map.Size.z)
                    return Fail("Cell (" + x + "," + z + ") is outside the map.");
                var mo = (mode ?? "").Trim().ToLowerInvariant();
                if (mo != "set" && mo != "push") return Fail("mode must be 'set' or 'push', got '" + mode + "'.");

                var cell = new IntVec3(x, 0, z);
                var cellObj = new { x, z };

                if (mo == "set")
                {
                    Room room;
                    try { room = cell.GetRoom(map); } catch (Exception ex) { return Fail("GetRoom threw: " + ex.GetType().Name + ": " + ex.Message); }
                    if (room == null)
                        return Fail("No room at (" + x + "," + z + ") - Room.Temperature has no meaning outdoors.");

                    var before = room.Temperature;
                    try { room.Temperature = value; }
                    catch (Exception ex) { return Fail("Setting Room.Temperature threw: " + ex.GetType().Name + ": " + ex.Message); }
                    var after = room.Temperature;

                    return new
                    {
                        success = true,
                        message = "Room " + room.ID + " temperature " + before.ToString("0.0") + " -> " + after.ToString("0.0") + " °C.",
                        mode = mo,
                        cell = cellObj,
                        roomId = room.ID,
                        temperatureBefore = before,
                        temperatureAfter = after,
                        ticksGame = TicksGameSafe()
                    };
                }

                bool pushed;
                try { pushed = GenTemperature.PushHeat(cell, map, value); }
                catch (Exception ex) { return Fail("PushHeat threw: " + ex.GetType().Name + ": " + ex.Message); }

                Room direct;
                try { direct = cell.GetRoom(map); } catch { direct = null; }

                return new
                {
                    success = true,
                    message = pushed
                        ? "Pushed " + value + " energy at (" + x + "," + z + ")."
                        : "No room at or adjacent to (" + x + "," + z + ") - nothing received the energy.",
                    mode = mo,
                    cell = cellObj,
                    pushed,
                    directRoom = direct != null ? (object)new { id = direct.ID, temperature = direct.Temperature } : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/stat_explain
        // ================================================================
        [Tool(
            "jawa/stat_explain",
            Description =
                "The number AND why it is that number: StatExtension.GetStatValue for the value, then " +
                "StatWorker.GetExplanationFull(StatRequest, numberSense, value) for the SAME breakdown " +
                "text the game's own info card tooltip shows - base value, each StatPart's contribution, " +
                "post-process steps, in order. jawa/pawn_stats and jawa/thing_stats give the number alone; " +
                "this is the only tool that gives the reasoning. Works on a pawn OR an item - both are " +
                "just Things. " +
                "⚠ An unknown StatDef is REFUSED BY NAME with suggestions, never reported as 0/empty.",
            ResultDescription =
                "success, subject (id, defName, label), count, stats[]: defName, label, value, " +
                "valueString, explanation (the full multi-line breakdown). Plus refused[] for any stat " +
                "that did not resolve.")]
        public static async Task<object> StatExplain(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Thing id - a pawn or an item - as returned by jawa/list_things or jawa/list_pawns.")]
            string subject = null,
            [ToolParameter(Description = "Comma-separated StatDef defNames.")]
            string stats = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (string.IsNullOrWhiteSpace(stats)) return Fail("Give at least one StatDef name in 'stats'.");

                string terr;
                var t = SystemToolsFindThing(subject, out terr);
                if (t == null) return Fail(terr ?? "No thing.");

                var req = StatRequest.For(t);
                var rows = new List<object>();
                var refused = new List<object>();

                foreach (var raw in stats.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var nm = raw.Trim();
                    if (nm.Length == 0) continue;
                    var sd = DefDatabase<StatDef>.GetNamedSilentFail(nm);
                    if (sd == null)
                    {
                        refused.Add(new { stat = nm, reason = "NoSuchStatDef", suggestions = DefSuggestions<StatDef>(nm) });
                        continue;
                    }

                    float v;
                    try { v = t.GetStatValue(sd); }
                    catch (Exception ex)
                    {
                        refused.Add(new { stat = nm, reason = ex.GetType().Name, message = ex.Message });
                        continue;
                    }

                    string explanation;
                    try { explanation = sd.Worker.GetExplanationFull(req, sd.toStringNumberSense, v); }
                    catch (Exception ex) { explanation = "(GetExplanationFull threw: " + ex.GetType().Name + ": " + ex.Message + ")"; }

                    string vs;
                    try { vs = sd.Worker.ValueToString(v, true, sd.toStringNumberSense); } catch { vs = v.ToString(); }

                    rows.Add(new { defName = sd.defName, label = sd.label, value = v, valueString = vs, explanation });
                }

                if (rows.Count == 0)
                    return Fail("No named stat resolved. Nothing was explained.", new { refused });

                QualityCategory qc;
                bool hasQuality = t.TryGetQuality(out qc);

                return new
                {
                    success = true,
                    message = rows.Count + " stat(s) explained for " + t.ThingID + (refused.Count > 0 ? ", " + refused.Count + " REFUSED" : "") + ".",
                    subject = new
                    {
                        id = t.ThingID,
                        defName = t.def != null ? t.def.defName : null,
                        label = t.LabelCap.ToString(),
                        quality = hasQuality ? qc.ToString() : null
                    },
                    count = rows.Count,
                    stats = rows,
                    refused,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
