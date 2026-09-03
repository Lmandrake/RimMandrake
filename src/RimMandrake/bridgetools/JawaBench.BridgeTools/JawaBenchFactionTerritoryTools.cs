// JawaBenchFactionTerritoryTools.cs - read and tune "Faction Territories and Vassalage"
// (jaeger972.factionterritories)'s own territory-generation knobs, live, from outside the
// game.
//
// WHY THIS EXISTS
// ===============
// The owner asked (after seeing screenshots): make the territory borders bigger, and make
// them bleed further along roads than out into open desert. The instinct was that this
// would need a new Harmony patch substituting a road-weighted cost-distance calculation
// into the mod's region-growing algorithm. It does not.
//
// Decompiled straight from the shipped FactionTerritories.dll (ilspycmd, into
// vendor/mod_sources/FactionTerritories_decompiled/ - see TerritoryOwnershipCache.cs):
// the mod ALREADY computes territory as a genuine multi-source Dijkstra cost-distance
// flood fill from every settlement (a min-heap over WorldGrid tiles, not a naive Voronoi
// by raw tile distance), and the per-edge step cost is
// FactionTerritoriesUtility.EdgeMovementDifficultyNoWinter, which is
// biome.movementDifficulty (real vanilla BiomeDef data) for the base cost, times
// grid.GetRoadMovementDifficultyMultiplier(fromTile, toTile, null) - RimWorld's OWN
// vanilla world-pathfinding API, the exact one this tool would otherwise have had to
// reinvent - for the road discount. Both terms are already exposed as ModSettings:
//   radiusSteps                  - "bigger" (base cost-radius from each settlement)
//   variationSteps                - ± noise on the radius, for a non-perfect-circle edge
//   roadMovementDifficultyPercent - Lerp(1, vanilla road multiplier, this/100), then
//                                    EXTRAPOLATED past 100 (200 -> roads cost ~0, so
//                                    territory runs far along a road relative to the
//                                    full-price desert around it) - exactly "bleed along
//                                    roads, not open desert"
//   impassableHillinessOffset     - extra cost added to impassable-hill tiles
//   settlementUncontestedRange    - a guaranteed-owned ring immediately around a base
// One field, terrainDifficultyImpactPercent, is drawn in the settings UI, saved, and
// hashed into the cache-invalidation key, but is never actually read by
// TileBaseMovementDifficulty/EdgeMovementDifficultyNoWinter/ComputeStepCostScaled - a
// dead setting in the shipped mod itself. This tool still reports it (as `noop: true` in
// the result) rather than silently hiding a field the mod's own UI exposes.
//
// So the entire ask is a settings change against the mod's own real algorithm, not a
// patch. This tool is that settings change, made reachable from outside the game and
// live-applied (Settings.Write() persists it to
// Config\Mod_3626725895_FactionTerritoriesMod.xml - the SAME file a normal player edits
// via the in-game Mod Settings window - so it survives every future load, not just this
// bridge session; FactionTerritoriesUtility.RequestRegenerateInternal(clearCache:true) is
// the mod's own SYNCHRONOUS live-refresh path (MapModeComponent.RegenerateNow() - the same
// call jawa/world_map_mode's mode switch already uses), used deliberately in place of the
// public RequestRegenerate() its settings window and WriteSettings() call, which only sets
// a `pending` flag consumed on the next GameComponentTick - a tick that does not run while
// the game is paused. This was found the hard way: an early version of this tool called
// RequestRegenerate() and needed the caller to unpause a REAL, persistent save just to make
// one tick elapse before the new radius was visible - unpausing a real campaign to force a
// cosmetic refresh is not an acceptable price for a settings tool to charge.
//
// REFLECTION, DELIBERATELY
// ========================
// jaeger972.factionterritories is a Workshop mod, not a build-time dependency of this
// companion, and this assembly must load with or without it. Everything below resolves
// by name through GenTypes.GetTypeInAnyAssembly and reports a missing type as DATA -
// never a throw - the same discipline JawaBenchMapModeTools.cs uses for MapModeFramework
// and JawaBenchSwcpCharacterTools.cs uses for SWCP.
//
// ⛔ NO jawa/ PREFIXES IN PROSE ANYWHERE IN THIS FILE other than an EXACT, REAL tool name.
// build.py scans the assembly for jawa/... literals and a partial mention becomes a
// phantom tool name and refuses the next deploy.

using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private const BindingFlags FtPublicInstance = BindingFlags.Public | BindingFlags.Instance;
        private const BindingFlags FtPublicStatic = BindingFlags.Public | BindingFlags.Static;

        private static Type FtType(string fullName) => GenTypes.GetTypeInAnyAssembly(fullName);

        /// <summary>Every FactionTerritoriesSettings field this tool knows how to read or
        /// write, keyed by the exact field name in the decompiled source. `noop` marks
        /// terrainDifficultyImpactPercent, which the mod itself never reads.</summary>
        private static readonly (string field, bool noop)[] FtSettingsFields =
        {
            ("radiusSteps", false),
            ("variationSteps", false),
            ("roadMovementDifficultyPercent", false),
            ("terrainDifficultyImpactPercent", true),
            ("impassableHillinessOffset", false),
            ("settlementUncontestedRange", false),
            ("includeWaterTiles", false),
        };

        [Tool(
            "jawa/faction_territory_settings",
            Description =
                "Read, and optionally SET, the live ModSettings that drive " +
                "jaeger972.factionterritories's own territory-generation algorithm - a real " +
                "multi-source cost-distance flood fill from every settlement, already " +
                "weighted by vanilla road movement difficulty (WorldGrid." +
                "GetRoadMovementDifficultyMultiplier) and biome movementDifficulty. There is " +
                "no separate 'bigger' or 'road-weighted' patch to write: these ARE the knobs. " +
                "Omit all setter parameters to read current values only. " +
                "radiusSteps raises the base cost-radius from each settlement (bigger " +
                "territory overall). roadMovementDifficultyPercent above 100 extrapolates " +
                "the road discount past the vanilla multiplier (roads approach zero cost, " +
                "so territory runs far along a road relative to full-price open desert); " +
                "100 is the mod's own default (exact vanilla multiplier), 0 removes the road " +
                "effect entirely, 200 is the mod's own clamp ceiling. impassableHillinessOffset " +
                "adds extra cost to impassable-hill tiles, further channelling growth away " +
                "from harsh terrain and along easier ground. terrainDifficultyImpactPercent " +
                "is accepted and reported for parity with the mod's own settings UI, but is " +
                "DEAD in the shipped mod - it is drawn, saved and cache-hashed, never read by " +
                "the actual cost function - so setting it changes nothing in-game; the result " +
                "flags it noopField:true rather than hiding that fact. " +
                "🔴 A value is written straight into the live Settings object AND persisted " +
                "via Settings.Write() to the mod's own Config\\Mod_3626725895_FactionTerritoriesMod.xml " +
                "- the same file the in-game Mod Settings window writes - so it survives every " +
                "future load, not only this session. Pass regenerate=false to skip the " +
                "immediate, PAUSE-SAFE live refresh (RequestRegenerateInternal - no need to " +
                "unpause the game) if you are about to set several fields in a row and only " +
                "want the LAST call to trigger a rebuild. " +
                "Requires jaeger972.factionterritories active; reports a missing mod as data " +
                "rather than throwing.",
            ResultDescription =
                "success, modPresent, before{} and after{} (every known field's value), " +
                "changed[] (field names actually written), noopField (terrainDifficultyImpactPercent, " +
                "always present so a caller never mistakes it for live), persisted, " +
                "regenerated (true only when RequestRegenerateInternal actually ran - checked, not " +
                "just invoked without an exception), regenerateNote (why not, when false and a " +
                "regenerate was requested), ticksGame.")]
        public static async Task<object> FactionTerritorySettings(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Base cost-radius steps from each settlement (mod default 5; live default may differ). 1-200.")]
            int? radiusSteps = null,
            [ToolParameter(Description = "± noise steps on the radius; 0 = perfect cost-contour, no jitter. 0-100.")]
            int? variationSteps = null,
            [ToolParameter(Description = "Road-discount strength, percent. 100 = exact vanilla road multiplier; 0 = roads ignored; 200 = roads pushed toward zero cost (strong road-bleed). 0-200, rounded to a multiple of 5 by the mod's own settings clamp.")]
            int? roadMovementDifficultyPercent = null,
            [ToolParameter(Description = "DEAD in the shipped mod - accepted for parity with its settings UI, but never read by the actual cost function. Setting this changes nothing live; see noopField in the result.")]
            int? terrainDifficultyImpactPercent = null,
            [ToolParameter(Description = "Extra movement-difficulty cost added to impassable-hill tiles (mod default 10). 0-1000.")]
            float? impassableHillinessOffset = null,
            [ToolParameter(Description = "Ring of tiles immediately around every settlement guaranteed to that faction regardless of cost-distance. 0 = disabled. 0-20.")]
            int? settlementUncontestedRange = null,
            [ToolParameter(Description = "Whether water tiles can be claimed as territory at all.")]
            bool? includeWaterTiles = null,
            [ToolParameter(Description = "Persist any change to the mod's own settings XML via Settings.Write() (default true). False leaves the live object changed for this session only - the mod's own game-exit path may still write it later.")]
            bool persist = true,
            [ToolParameter(Description = "Call FactionTerritoriesUtility.RequestRegenerateInternal(clearCache:true) after any change - the mod's own SYNCHRONOUS, pause-safe live-refresh path (MapModeComponent.RegenerateNow()), not the settings window's tick-gated RequestRegenerate. Default true.")]
            bool regenerate = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                Type modType = FtType("FactionTerritories.FactionTerritoriesMod");
                if (modType == null)
                {
                    return Fail(
                        "FactionTerritories.FactionTerritoriesMod did not resolve in any " +
                        "loaded assembly. jaeger972.factionterritories is not active, or its " +
                        "assembly failed to load - check the log for a load error.",
                        new { modPresent = false });
                }

                FieldInfo instanceField = modType.GetField("Instance", FtPublicStatic);
                object modInstance = instanceField?.GetValue(null);
                if (modInstance == null)
                {
                    return Fail(
                        "FactionTerritoriesMod.Instance is null - the mod's own Mod " +
                        "constructor has not run, which should not be possible once RimWorld " +
                        "has loaded mods at all.",
                        new { modPresent = true });
                }

                FieldInfo settingsField = modType.GetField("Settings", FtPublicInstance);
                object settings = settingsField?.GetValue(modInstance);
                if (settings == null)
                {
                    return Fail(
                        "FactionTerritoriesMod.Instance.Settings is null - the mod's API " +
                        "changed and this tool needs updating.",
                        new { modPresent = true });
                }

                Type settingsType = settings.GetType();

                var requested = new Dictionary<string, object>
                {
                    ["radiusSteps"] = radiusSteps,
                    ["variationSteps"] = variationSteps,
                    ["roadMovementDifficultyPercent"] = roadMovementDifficultyPercent,
                    ["terrainDifficultyImpactPercent"] = terrainDifficultyImpactPercent,
                    ["impassableHillinessOffset"] = impassableHillinessOffset,
                    ["settlementUncontestedRange"] = settlementUncontestedRange,
                    ["includeWaterTiles"] = includeWaterTiles,
                };

                object ReadAll()
                {
                    var dict = new Dictionary<string, object>();
                    foreach (var (fieldName, _) in FtSettingsFields)
                    {
                        FieldInfo fi = settingsType.GetField(fieldName, FtPublicInstance);
                        dict[fieldName] = fi?.GetValue(settings);
                    }
                    return dict;
                }

                object before = ReadAll();

                // 🔴 FactionTerritoriesSettings applies its own Mathf.Clamp calls inside
                // ExposeData, under `Scribe.mode == PostLoadInit` ONLY - never on Write() and
                // never on assignment. So an out-of-range value written here is applied to the
                // live algorithm, persisted to the mod's XML, reported in after{} - and then
                // silently snaps back to the clamp the NEXT time the game loads settings. That
                // makes after{} a number the game will not keep, which is exactly the failure
                // this tool exists to avoid. Refuse up front, before ANY field is written, so a
                // rejected call also cannot leave a half-applied settings object behind.
                // Ranges below are the mod's own, read out of the decompiled ExposeData.
                var outOfRange = new List<string>();
                void CheckRange(string fieldName, double? v, double lo, double hi)
                {
                    if (v.HasValue && (v.Value < lo || v.Value > hi))
                        outOfRange.Add($"{fieldName}={v.Value} (allowed {lo}..{hi})");
                }
                CheckRange("radiusSteps", radiusSteps, 1, 200);
                CheckRange("variationSteps", variationSteps, 0, 100);
                CheckRange("roadMovementDifficultyPercent", roadMovementDifficultyPercent, 0, 200);
                CheckRange("terrainDifficultyImpactPercent", terrainDifficultyImpactPercent, 0, 200);
                CheckRange("impassableHillinessOffset", impassableHillinessOffset, 0, 1000);
                CheckRange("settlementUncontestedRange", settlementUncontestedRange, 0, 20);
                if (outOfRange.Count > 0)
                {
                    return Fail(
                        "Refusing - value(s) outside the mod's own clamp range: " +
                        string.Join("; ", outOfRange) +
                        ". FactionTerritoriesSettings clamps these on LOAD only, so writing one would " +
                        "take effect live, persist to the mod's XML, and then snap back on the next " +
                        "load - after{} would report a value the game does not keep. Nothing was written.",
                        new { modPresent = true, before, outOfRange });
                }

                var changed = new List<string>();
                var missingFields = new List<string>();

                foreach (var (fieldName, _) in FtSettingsFields)
                {
                    if (!requested.TryGetValue(fieldName, out object wanted) || wanted == null)
                        continue;

                    FieldInfo fi = settingsType.GetField(fieldName, FtPublicInstance);
                    if (fi == null)
                    {
                        missingFields.Add(fieldName);
                        continue;
                    }

                    try
                    {
                        object coerced = Convert.ChangeType(wanted, fi.FieldType);
                        fi.SetValue(settings, coerced);
                        changed.Add(fieldName);
                    }
                    catch (Exception e)
                    {
                        return Fail(
                            $"Could not set {fieldName}: {e.Message}",
                            new { modPresent = true, before, changed });
                    }
                }

                bool persisted = false;
                if (changed.Count > 0 && persist)
                {
                    MethodInfo writeMethod = settingsType.GetMethod("Write", FtPublicInstance, null, Type.EmptyTypes, null);
                    if (writeMethod != null)
                    {
                        try { writeMethod.Invoke(settings, null); persisted = true; }
                        catch (Exception e)
                        {
                            return Fail(
                                "Settings.Write() threw: " + e.Message,
                                new { modPresent = true, before, changed });
                        }
                    }
                }

                bool regenerated = false;
                string regenerateNote = null;
                if (changed.Count > 0 && regenerate)
                {
                    // RequestRegenerateInternal, NOT RequestRegenerate. RequestRegenerate (the
                    // one the mod's own settings window and WriteSettings() call) only sets a
                    // `pending` flag on GameComponent_FactionTerritories, consumed the next time
                    // GameComponentTick runs - which does NOT run while the game is paused. A
                    // caller sitting at the world map (as this tool's own caller usually is) who
                    // wants to SEE the new radius immediately would otherwise have to unpause the
                    // game just to make one tick elapse - on a real save, not a scratch map, that
                    // is genuine unintended gameplay, not a harmless refresh. RequestRegenerateInternal
                    // is the synchronous, main-thread, pause-safe path (MapModeComponent.RegenerateNow(),
                    // the exact call jawa/world_map_mode already uses for a mode switch) with the
                    // same clearCache behaviour, so this never needs the sim to tick.
                    //
                    // 🔴 RequestRegenerateInternal itself (FactionTerritoriesUtility.cs) returns
                    // silently, with NO exception, when MapModeComponent.Instance is null (no
                    // game loaded yet) or when no MapMode_FactionTerritories is registered in
                    // instance.mapModes - reflection's Invoke() would still succeed in both cases,
                    // which is exactly the "success for something else" pattern this DLL's review
                    // has already fixed four times over. Check the same precondition the method
                    // itself checks, the same discipline JawaBenchMapModeTools.cs already uses for
                    // this framework, so `regenerated` means an actual regeneration ran.
                    Type compType = FtType("MapModeFramework.MapModeComponent");
                    object mmfInstance = compType?.GetField("Instance", FtPublicStatic)?.GetValue(null);
                    bool hasFactionTerritoriesMode = false;
                    if (mmfInstance != null)
                    {
                        object modesRaw = compType.GetField("mapModes", FtPublicInstance)?.GetValue(mmfInstance);
                        Type ftModeType = FtType("FactionTerritories.MapMode_FactionTerritories");
                        if (modesRaw is IEnumerable modesEnum && ftModeType != null)
                        {
                            foreach (object m in modesEnum)
                                if (ftModeType.IsInstanceOfType(m)) { hasFactionTerritoriesMode = true; break; }
                        }
                    }

                    if (mmfInstance == null)
                    {
                        regenerateNote = "MapModeComponent.Instance is null - no game is loaded, so " +
                            "there is no live view to refresh. The settings change above is still " +
                            "written and persisted; it will apply once a game is loaded.";
                    }
                    else if (!hasFactionTerritoriesMode)
                    {
                        regenerateNote = "No MapMode_FactionTerritories is registered in " +
                            "MapModeComponent.mapModes, so RequestRegenerateInternal would be a " +
                            "no-op. The settings change above is still written and persisted.";
                    }
                    else
                    {
                        Type utilType = FtType("FactionTerritories.FactionTerritoriesUtility");
                        MethodInfo regenMethod = utilType?.GetMethod("RequestRegenerateInternal", FtPublicStatic);
                        if (regenMethod == null)
                        {
                            regenerateNote = "FactionTerritoriesUtility.RequestRegenerateInternal did " +
                                "not resolve - the mod's API changed and this tool needs updating.";
                        }
                        else
                        {
                            try { regenMethod.Invoke(null, new object[] { true }); regenerated = true; }
                            catch (Exception e)
                            {
                                return Fail(
                                    "FactionTerritoriesUtility.RequestRegenerateInternal threw: " + e.Message,
                                    new { modPresent = true, before, changed, persisted });
                            }
                        }
                    }
                }

                return (object)new
                {
                    success = true,
                    modPresent = true,
                    before,
                    after = ReadAll(),
                    changed,
                    missingFields,
                    noopField = "terrainDifficultyImpactPercent",
                    persisted,
                    regenerated,
                    regenerateNote,
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }
    }
}
