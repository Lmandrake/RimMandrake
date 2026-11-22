// JawaBenchSeedFoilTools.cs - jawa/map_seed_foil: the same-seed, same-tile foil of the current map, generated with
// def fields held at override values through generation, read by a whole-map census, and dropped, in ONE main-thread
// call. Item RIMMANDRAKE_BUILD_PYRE_DENSITY_ONE_FOIL_BLIND_AT_FIVE (Pyrelands sc_grass_regreens: "the plantDensity-1.0
// map reads a lower open-cell plant share than the fresh enforced map").
//
// READ FROM 1.6 SOURCE (RimSage), NOT REMEMBERED:
//   MapGenerator.GenerateMap (Verse/MapGenerator.cs:79): seed = Gen.HashCombineInt(Find.World.info.Seed,
//     parent.Tile.GetHashCode()) for a non-pocket map, and each GenStep reseeds from it - so a second MapParent whose
//     Tile is the site's tile generates from the site's own seed. It refuses a parent that already HasMap, which is why
//     the foil needs its own (unregistered) MapParent: one world object can hold one map.
//   WildPlantSpawner.GetDesiredPlantsCountAt (:718) reads map.BiomeAt(c).plantDensity LIVE at generation, so a field
//     set on the BiomeDef before GenerateMap is the density the foil is generated with.
//   Game.DeinitAndRemoveMap / MapDeiniter.PassPawnsToWorld: a dropped map's pawns go to world pawns; factionless
//     animals of the foil are vanished first so a foil leaves no world pawns behind.
//
// WHY ONE CALL: no tick can run between override, generation, census and drop, so a GameComponent that re-asserts
// a def value every N ticks (the Pyrelands density enforcer, 250 ticks) cannot undo the override mid-generation, and
// the foil never ticks, renders or becomes the current map. The verdict stays in Python (companion rule 11): this
// tool returns raw counts only.
//
// THREAD AFFINITY: everything that touches game state is inside ctx.MainThread.InvokeAsync.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        private sealed class FoilOverride
        {
            public string Target, Field, Raw;
            public Def Def;
            public FieldInfo Info;
            public object Before, Value;
        }

        /// <summary>Parse 'DefType/defName.field=value;...' -> overrides, or an error string. Scalar fields only
        /// (float, int, bool): a list or object field is refused by name.</summary>
        private static string ParseFoilOverrides(string spec, List<FoilOverride> outList)
        {
            foreach (var raw in (spec ?? "").Split(';'))
            {
                var part = raw.Trim();
                if (part.Length == 0) continue;
                int eq = part.IndexOf('='), slash = part.IndexOf('/');
                int dot = eq > 0 ? part.LastIndexOf('.', eq) : -1;
                if (eq < 0 || slash < 0 || dot < slash)
                    return "override '" + part + "' is not 'DefType/defName.field=value'";
                string typeName = part.Substring(0, slash).Trim(), defName = part.Substring(slash + 1, dot - slash - 1).Trim();
                string field = part.Substring(dot + 1, eq - dot - 1).Trim(), val = part.Substring(eq + 1).Trim();
                var type = GenTypes.GetTypeInAnyAssembly(typeName);
                if (type == null || !typeof(Def).IsAssignableFrom(type)) return "no Def type '" + typeName + "'";
                var def = GenDefDatabase.GetDefSilentFail(type, defName, false);
                if (def == null) return "no " + typeName + " '" + defName + "'";
                var fi = type.GetField(field, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (fi == null) return typeName + " has no field '" + field + "'";
                object v;
                if (fi.FieldType == typeof(float) && float.TryParse(val, NumberStyles.Float, CultureInfo.InvariantCulture, out var f)) v = f;
                else if (fi.FieldType == typeof(int) && int.TryParse(val, NumberStyles.Integer, CultureInfo.InvariantCulture, out var n)) v = n;
                else if (fi.FieldType == typeof(bool) && bool.TryParse(val, out var b)) v = b;
                else return typeName + "." + field + " is " + fi.FieldType.Name + ": only float, int and bool fields, and '" +
                            val + "' must parse as one";
                outList.Add(new FoilOverride { Target = typeName + "/" + defName, Field = field, Raw = val, Def = def, Info = fi, Value = v });
            }
            return null;
        }

        [Tool(
            "jawa/map_seed_foil",
            Description =
                "Generate the SAME-SEED, SAME-TILE foil of the current map with def fields held at override values " +
                "through generation, census it, and drop it - one main-thread call, so no tick runs in between. " +
                "MapGenerator seeds a non-pocket map from the world seed and the parent's Tile, so a fresh unregistered " +
                "MapParent on the current map's tile, with the current map's generator def and size, generates from " +
                "the current map's own seed (seedEqual reports it). 'overrides' is 'DefType/defName.field=value;...' " +
                "(float, int or bool fields only), set before GenerateMap and restored in a finally, each with " +
                "before / heldAfterGeneration / restored read back RAW from the field. " +
                "The census is whole-map and raw: perDef of 'censusGroup' things (the same lister and count as a " +
                "whole-map list_things group= read), terrain cells per TOP terrain def, and the count of " +
                "'builtGroup' things. The verdict is the caller's. " +
                "🔴 The current map is NOT touched: the foil is never made current, never ticks or renders, and is " +
                "removed before the call returns (mapCountAfter == mapCountBefore, currentMapRestored). Its " +
                "factionless animals are vanished first so no world pawns are left; any other pawn goes to world " +
                "pawns the vanilla way (reported). A failed generation still restores every override and drops " +
                "whatever map it added. Generation takes as long as a map load of the current mod list.",
            ResultDescription =
                "success, site{mapIndex, mapId, tile, tileHash, generatorDef, biome, sizeX, sizeZ, generationTick}, " +
                "foil{seed, seedEqual, tileHash, generatorDef, biome, sizeX, sizeZ, cells, scanned, countMatched, " +
                "perDef{def:n}, terrain{def:cells}, terrainNull, built, pawnsVanished, pawnsToWorld}, " +
                "overrides[{target, field, value, before, heldAfterGeneration, restored}], mapCountBefore, " +
                "mapCountAfter, currentMapRestored, ticksBefore, ticksAfter, generateError, dropError.")]
        public static async Task<object> MapSeedFoil(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Def field overrides held through generation: 'DefType/defName.field=value;...' (float, int, bool). Empty = none.")]
            string overrides = "",
            [ToolParameter(Description = "ThingRequestGroup the census counts per def. Default 'Plant'.")]
            string censusGroup = "Plant",
            [ToolParameter(Description = "ThingRequestGroup counted as 'built'. Default 'BuildingArtificial'.")]
            string builtGroup = "BuildingArtificial",
            [ToolParameter(Description = "Report the site, the seed and the parsed overrides; generate nothing.")]
            bool dryRun = false)
        {
            if (!Enum.TryParse((censusGroup ?? "").Trim(), true, out ThingRequestGroup cg) || cg == ThingRequestGroup.Undefined)
                return Fail("No ThingRequestGroup named '" + censusGroup + "'.", new { valid = Enum.GetNames(typeof(ThingRequestGroup)) });
            if (!Enum.TryParse((builtGroup ?? "").Trim(), true, out ThingRequestGroup bg) || bg == ThingRequestGroup.Undefined)
                return Fail("No ThingRequestGroup named '" + builtGroup + "'.", new { valid = Enum.GetNames(typeof(ThingRequestGroup)) });

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null || Find.World == null) return Fail("No game loaded.");
                var site = Find.CurrentMap;
                if (site == null) return Fail("No current map.");
                if (site.IsPocketMap) return Fail("The current map is a pocket map: its seed is the parent's ID, not a tile.");
                if (site.generatorDef == null) return Fail("The current map has no generatorDef to regenerate with.");
                var siteTile = site.Tile;
                if (!siteTile.Valid) return Fail("The current map's tile is not valid.");

                var ovs = new List<FoilOverride>();
                var perr = ParseFoilOverrides(overrides, ovs);
                if (perr != null) return Fail(perr);

                var siteOut = new
                {
                    mapIndex = site.Index, mapId = site.uniqueID, tile = siteTile.tileId, tileHash = siteTile.GetHashCode(),
                    generatorDef = site.generatorDef.defName, biome = site.Biome != null ? site.Biome.defName : null,
                    sizeX = site.Size.x, sizeZ = site.Size.z, generationTick = site.generationTick
                };
                int seed = Gen.HashCombineInt(Find.World.info.Seed, siteTile.GetHashCode());
                int ticksBefore = TicksGameSafe();
                if (dryRun)
                    return new
                    {
                        success = true, dryRun = true, site = siteOut, seed,
                        overrides = ovs.Select(o => new { target = o.Target, field = o.Field, value = o.Value, current = o.Info.GetValue(o.Def) }).ToList(),
                        ticksGame = ticksBefore
                    };

                int countBefore = Find.Maps.Count;
                var mapsBefore = new HashSet<Map>(Find.Maps);
                Map foil = null;
                string genError = null, dropError = null;
                var held = new Dictionary<FoilOverride, object>();
                var census = new Dictionary<string, int>();
                var terrain = new Dictionary<string, int>();
                int scanned = 0, matched = 0, built = 0, terrainNull = 0, vanished = 0, toWorld = 0, cells = 0;
                int foilHash = 0;
                string foilGen = null, foilBiome = null;
                int fx = 0, fz = 0;
                try
                {
                    foreach (var o in ovs) { o.Before = o.Info.GetValue(o.Def); o.Info.SetValue(o.Def, o.Value); }
                    var parent = new MapParent();
                    parent.def = DefDatabase<WorldObjectDef>.GetNamedSilentFail("Debug_Arena") ?? site.Parent?.def;
                    parent.ID = Find.UniqueIDsManager.GetNextWorldObjectID();
                    parent.creationGameTicks = ticksBefore;
                    parent.Tile = siteTile;
                    foil = MapGenerator.GenerateMap(site.Size, parent, site.generatorDef);
                    foreach (var o in ovs) held[o] = o.Info.GetValue(o.Def);

                    foilHash = foil.Tile.GetHashCode();
                    foilGen = foil.generatorDef != null ? foil.generatorDef.defName : null;
                    foilBiome = foil.Biome != null ? foil.Biome.defName : null;
                    fx = foil.Size.x; fz = foil.Size.z;
                    foreach (var t in foil.listerThings.ThingsInGroup(cg))
                    {
                        if (t?.def == null) continue;
                        scanned++;
                        if (t is Pawn) continue;
                        matched++;
                        census.TryGetValue(t.def.defName, out var n);
                        census[t.def.defName] = n + 1;
                    }
                    built = foil.listerThings.ThingsInGroup(bg).Count;
                    foreach (var c in foil.AllCells)
                    {
                        cells++;
                        var td = foil.terrainGrid.TerrainAt(c);
                        if (td == null) { terrainNull++; continue; }
                        terrain.TryGetValue(td.defName, out var n);
                        terrain[td.defName] = n + 1;
                    }
                }
                catch (Exception ex)
                {
                    genError = ex.GetType().Name + ": " + ex.Message;
                }
                finally
                {
                    foreach (var o in ovs)
                        if (o.Before != null) o.Info.SetValue(o.Def, o.Before);
                    // the foil, or whatever a failed generation added
                    foreach (var m in Find.Maps.Where(m => !mapsBefore.Contains(m)).ToList())
                    {
                        try
                        {
                            foreach (var p in m.mapPawns.AllPawns.ToList())
                            {
                                if (p.Faction == null && p.RaceProps != null && p.RaceProps.Animal) { p.Destroy(DestroyMode.Vanish); vanished++; }
                                else toWorld++;
                            }
                            Current.Game.DeinitAndRemoveMap(m, false);
                        }
                        catch (Exception ex) { dropError = (dropError == null ? "" : dropError + "; ") + ex.GetType().Name + ": " + ex.Message; }
                    }
                    if (Find.Maps.Contains(site) && Find.CurrentMap != site) Current.Game.CurrentMap = site;
                }

                bool restored = ovs.All(o => Equals(o.Info.GetValue(o.Def), o.Before));
                bool ok = genError == null && dropError == null && foil != null && restored && Find.Maps.Count == countBefore;
                return new
                {
                    success = ok,
                    message = ok ? null : ("foil " + (genError != null ? "generation failed: " + genError : "") +
                                           (dropError != null ? " drop failed: " + dropError : "") +
                                           (!restored ? " an override was NOT restored" : "") +
                                           (Find.Maps.Count != countBefore ? " map count " + countBefore + " -> " + Find.Maps.Count : "")),
                    site = siteOut,
                    foil = foil == null ? null : (object)new
                    {
                        seed, seedEqual = foilHash == siteTile.GetHashCode(), tileHash = foilHash, generatorDef = foilGen,
                        biome = foilBiome, sizeX = fx, sizeZ = fz, cells, scanned, countMatched = matched,
                        perDef = census.OrderByDescending(kv => kv.Value).ToDictionary(kv => kv.Key, kv => kv.Value),
                        terrain = terrain.OrderByDescending(kv => kv.Value).ToDictionary(kv => kv.Key, kv => kv.Value),
                        terrainNull, built, pawnsVanished = vanished, pawnsToWorld = toWorld
                    },
                    overrides = ovs.Select(o => new
                    {
                        target = o.Target, field = o.Field, value = o.Value, before = o.Before,
                        heldAfterGeneration = held.TryGetValue(o, out var h) ? h : null, restored = o.Info.GetValue(o.Def)
                    }).ToList(),
                    mapCountBefore = countBefore,
                    mapCountAfter = Find.Maps.Count,
                    currentMapRestored = Find.CurrentMap == site,
                    ticksBefore,
                    ticksAfter = TicksGameSafe(),
                    generateError = genError,
                    dropError,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
