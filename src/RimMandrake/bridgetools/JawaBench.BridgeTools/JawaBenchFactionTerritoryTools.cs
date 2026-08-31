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
// bridge session; FactionTerritoriesUtility.RequestRegenerate(clearCache:true) is the
// mod's own live-refresh path, the same one its "Clear all faction colour overrides"
// button and its own WriteSettings() override call).
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
                "immediate live refresh (RequestRegenerate) if you are about to set several " +
                "fields in a row and only want the LAST call to trigger a rebuild. " +
                "Requires jaeger972.factionterritories active; reports a missing mod as data " +
                "rather than throwing.",
            ResultDescription =
                "success, modPresent, before{} and after{} (every known field's value), " +
                "changed[] (field names actually written), noopField (terrainDifficultyImpactPercent, " +
                "always present so a caller never mistakes it for live), persisted, " +
                "regenerated, ticksGame.")]
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
            [ToolParameter(Description = "Call FactionTerritoriesUtility.RequestRegenerate(clearCache:true) after any change, the mod's own live-refresh path - the same one its settings window and its own WriteSettings() use (default true).")]
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
                if (changed.Count > 0 && regenerate)
                {
                    Type utilType = FtType("FactionTerritories.FactionTerritoriesUtility");
                    MethodInfo regenMethod = utilType?.GetMethod("RequestRegenerate", FtPublicStatic);
                    if (regenMethod != null)
                    {
                        try { regenMethod.Invoke(null, new object[] { true }); regenerated = true; }
                        catch (Exception e)
                        {
                            return Fail(
                                "FactionTerritoriesUtility.RequestRegenerate threw: " + e.Message,
                                new { modPresent = true, before, changed, persisted });
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
                    ticksGame = TicksGameSafe(),
                };
            }).ConfigureAwait(false);
        }
    }
}
