// ============================================================================
// JawaBenchDiagnosticTools.cs - answer the questions that cost a human a night.
//
// Every tool here exists because on 2026-08-21 a real question could not be
// answered from the bridge and had to be answered by the owner squinting at his
// own screen. That is the exact inversion of what this seat is for.
//
//   "why can't I click these tiles?"      -> tile_settleable
//   "did the repaint leave stale caches?" -> tile_cache_audit
//   "why is that desert MAGENTA?"         -> biome_art_audit
//   "does the Empire have an Emperor?"    -> faction_leader_get
//
// 🔴 THE SHARED LESSON. Three of the four exist because a tool was reading the
// CONVENIENT value rather than the one the game uses. `world_tile_get` builds
// BOTH its hilliness fields from the raw `t.hilliness`, so it reports a tile as
// correct whether or not `HillinessLabel` - the value the UI reads - agrees.
// A readback that cannot disagree with itself is not a readback.
// ============================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using RimWorld.Planet;
using UnityEngine;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        // ====================================================================
        //  WHY CAN'T I CLICK THAT TILE
        // ====================================================================
        [Tool(
            "jawa/tile_settleable",
            Description =
                "Ask the ENGINE'S OWN gate whether a tile can be settled, and report the " +
                "engine's own reason string when it cannot. Calls " +
                "TileFinder.IsValidTileForNewSettlement with a StringBuilder, so this " +
                "cannot drift from what the landing page actually does. " +
                "With no tiles named it sweeps the whole planet and returns counts per " +
                "reason instead of rows. " +
                "🔑 THE REASON THIS EXISTS: a repaint can make a large slice of the planet " +
                "unsettleable without anything looking wrong. Importing 72 settlements " +
                "blocks 504 tiles by itself, because the gate refuses a tile that has a " +
                "settlement AT OR ADJACENT to it, not merely on it. " +
                "Reads only; changes nothing.",
            ResultDescription =
                "counts per refusal reason, total settleable, and per-tile rows with the " +
                "engine's own reason text when tiles are named.")]
        public static async Task<object> TileSettleable(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids. Empty sweeps the planet.")] string tiles = null,
            [ToolParameter(Description = "Ask as if landing a gravship.")] bool forGravship = false,
            [ToolParameter(Description = "Max example rows per reason on a sweep. Default 8.")] int examplesPerReason = 8)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var grid = Find.WorldGrid;
                if (Find.World == null || grid == null) return Fail("No world is loaded.");
                var surface = grid.Surface;

                var ids = new List<int>();
                foreach (var part in (tiles ?? "").Split(','))
                { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                bool sweep = ids.Count == 0;
                if (sweep) { for (int i = 0; i < grid.TilesCount; i++) ids.Add(i); }

                var counts = new Dictionary<string, int>();
                var examples = new Dictionary<string, List<int>>();
                var rows = new List<object>();
                int ok = 0;

                foreach (var id in ids)
                {
                    if (id < 0 || id >= grid.TilesCount) continue;
                    var pt = new PlanetTile(id, surface);
                    var sb = new StringBuilder();
                    bool valid;
                    try { valid = TileFinder.IsValidTileForNewSettlement(pt, sb, forGravship); }
                    catch (Exception ex)
                    { valid = false; sb.Length = 0; sb.Append(ex.GetType().Name + ": " + ex.Message); }

                    if (valid) { ok++; if (!sweep) rows.Add(new { tile = id, settleable = true, reason = (string)null }); continue; }

                    // 🔑 Bucket on the engine's own text. It is translated, so it is a
                    // label rather than an identifier - but it is the SAME string the
                    // player is shown, which is what makes a count of it meaningful.
                    string why = sb.Length > 0 ? sb.ToString() : "(refused with no reason given)";
                    int n; counts.TryGetValue(why, out n); counts[why] = n + 1;
                    List<int> ex2;
                    if (!examples.TryGetValue(why, out ex2)) { ex2 = new List<int>(); examples[why] = ex2; }
                    if (ex2.Count < Math.Max(1, examplesPerReason)) ex2.Add(id);
                    if (!sweep) rows.Add(new { tile = id, settleable = false, reason = why });
                }

                var byReason = counts.OrderByDescending(kv => kv.Value)
                    .Select(kv => (object)new { reason = kv.Key, count = kv.Value, examples = examples[kv.Key] })
                    .ToList();

                return (object)new
                {
                    success = true,
                    sweep,
                    tilesTested = ids.Count,
                    settleable = ok,
                    refused = ids.Count - ok,
                    byReason,
                    tiles = sweep ? null : (object)rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ====================================================================
        //  DID THE REPAINT LEAVE STALE CACHES
        // ====================================================================
        [Tool(
            "jawa/tile_cache_audit",
            Description =
                "Compare a tile's RAW fields against the CACHED values the UI actually " +
                "reads, and report every disagreement. " +
                "🔴 Tile caches `hillinessLabelCached`, `cachedMinTemp` and `cachedMaxTemp` " +
                "lazily and RimWorld has no reset method for any of them - they clear only " +
                "on reload. So after a repaint the raw field can be correct while the game " +
                "still behaves as the old value, and every other read tool reports the raw " +
                "one and looks clean. " +
                "⚠️ HillinessLabel is NOT purely a cache: a TileMutatorDef carrying " +
                "hillinessLabel overrides it by design, so a disagreement is only a defect " +
                "when no mutator on that tile explains it. This reports which mutator " +
                "supplied the label so the two cases can be told apart. " +
                "Reads only; changes nothing, and reading does NOT populate the cache " +
                "because it inspects the backing field by reflection.",
            ResultDescription =
                "counts of raw-vs-cached disagreements, split into explained-by-mutator and " +
                "unexplained, plus example rows.")]
        public static async Task<object> TileCacheAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated tile ids. Empty sweeps the planet.")] string tiles = null,
            [ToolParameter(Description = "Max example rows. Default 20.")] int limit = 20)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var grid = Find.WorldGrid;
                if (Find.World == null || grid == null) return Fail("No world is loaded.");

                // ⚠️ Reflection, deliberately. Calling the PROPERTY would populate the very
                // cache we are trying to observe, so the first call would always report
                // agreement and the tool would be a very convincing lie.
                var fCached = typeof(Tile).GetField("hillinessLabelCached",
                    BindingFlags.NonPublic | BindingFlags.Instance);
                var fMin = typeof(Tile).GetField("cachedMinTemp", BindingFlags.NonPublic | BindingFlags.Instance);
                var fMax = typeof(Tile).GetField("cachedMaxTemp", BindingFlags.NonPublic | BindingFlags.Instance);
                if (fCached == null)
                    return Fail("Tile.hillinessLabelCached not found by reflection - RimWorld's " +
                                "internals moved. This tool must be re-anchored against the current " +
                                "source before its numbers are trusted.");

                var ids = new List<int>();
                foreach (var part in (tiles ?? "").Split(','))
                { int v; if (int.TryParse(part.Trim(), out v)) ids.Add(v); }
                bool sweep = ids.Count == 0;
                if (sweep) { for (int i = 0; i < grid.TilesCount; i++) ids.Add(i); }

                int populated = 0, disagree = 0, explained = 0, unexplained = 0, tempCached = 0;
                var rows = new List<object>();

                foreach (var id in ids)
                {
                    if (id < 0 || id >= grid.TilesCount) continue;
                    var t = grid[id];
                    if (t == null) continue;

                    var boxed = fCached.GetValue(t);
                    bool hasCache = boxed != null;
                    if (!hasCache) continue;           // never asked for, so nothing to be stale
                    populated++;
                    var cached = (Hilliness)boxed;
                    if (cached == t.hilliness) continue;
                    disagree++;

                    // does a mutator on this tile legitimately supply that label?
                    string byMutator = null;
                    var st = t as SurfaceTile;
                    if (st != null && st.mutatorsNullable != null)
                        foreach (var m in st.mutatorsNullable)
                            if (m != null && m.hillinessLabel == cached) { byMutator = m.defName; break; }

                    if (byMutator != null) explained++; else unexplained++;
                    if (rows.Count < Math.Max(1, limit))
                        rows.Add(new
                        {
                            tile = id,
                            raw = t.hilliness.ToString(),
                            cachedLabel = cached.ToString(),
                            explainedBy = byMutator,
                            verdict = byMutator != null ? "by design" : "STALE",
                        });
                }

                if (fMin != null && fMax != null)
                    foreach (var id in ids)
                    {
                        if (id < 0 || id >= grid.TilesCount) continue;
                        var t = grid[id]; if (t == null) continue;
                        if (fMin.GetValue(t) != null || fMax.GetValue(t) != null) tempCached++;
                    }

                return (object)new
                {
                    success = true,
                    sweep,
                    tilesTested = ids.Count,
                    hillinessCachePopulated = populated,
                    disagreements = disagree,
                    explainedByMutator = explained,
                    unexplainedStale = unexplained,
                    temperatureCachePopulated = tempCached,
                    note = unexplained > 0
                        ? "Unexplained disagreements are STALE and clear only on reload - RimWorld " +
                          "has no reset method for this cache."
                        : "No unexplained disagreement. Every populated label matches its raw field " +
                          "or is supplied by a mutator.",
                    examples = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ====================================================================
        //  WHY IS THAT BIOME MAGENTA
        // ====================================================================
        [Tool(
            "jawa/biome_art_audit",
            Description =
                "For every biome PRESENT on this planet, report its world texture path and " +
                "whether that texture actually resolved. A BiomeDef whose texture is missing " +
                "renders MAGENTA on the globe and logs nothing useful, so the only way to " +
                "find it today is to look at the planet and squint. " +
                "Resolution is tested with ContentFinder, which is the same loader the def " +
                "uses, and the material's own main texture is checked as a second instrument. " +
                "Reads only; changes nothing.",
            ResultDescription =
                "per-biome rows with tile count, texture path, resolved true/false, and a " +
                "missing[] list naming any biome that will draw magenta.")]
        public static async Task<object> BiomeArtAudit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Only biomes actually painted on a tile. Default true.")] bool onlyInUse = true)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                var grid = Find.WorldGrid;
                if (Find.World == null || grid == null) return Fail("No world is loaded.");

                var used = new Dictionary<string, int>();
                for (int i = 0; i < grid.TilesCount; i++)
                {
                    var t = grid[i]; if (t == null) continue;
                    var b = t.PrimaryBiome; if (b == null) continue;
                    int n; used.TryGetValue(b.defName, out n); used[b.defName] = n + 1;
                }

                var rows = new List<object>();
                var missing = new List<string>();
                // ⚠️ Sort the SOURCE, not the anonymous objects. Reflecting a property off an
                // anonymous type to sort it works until the compiler renames it, and then
                // throws inside a diagnostic tool, which is the worst place for a surprise.
                var ordered = DefDatabase<BiomeDef>.AllDefsListForReading
                    .Select(b => { int c; used.TryGetValue(b.defName, out c); return new { def = b, count = c }; })
                    .OrderByDescending(x => x.count)
                    .ToList();
                foreach (var entry in ordered)
                {
                    var b = entry.def;
                    int count = entry.count;
                    if (onlyInUse && count == 0) continue;

                    bool found = false; string err = null;
                    try
                    {
                        if (!string.IsNullOrEmpty(b.texture))
                            found = ContentFinder<Texture2D>.Get(b.texture, false) != null;
                    }
                    catch (Exception ex) { err = ex.GetType().Name + ": " + ex.Message; }

                    bool matOk = false;
                    try { var m = b.DrawMaterial; matOk = m != null && m.mainTexture != null; }
                    catch (Exception ex) { if (err == null) err = ex.GetType().Name + ": " + ex.Message; }

                    if (!found || !matOk) missing.Add(b.defName);
                    rows.Add(new
                    {
                        biome = b.defName,
                        label = b.label,
                        tiles = count,
                        texture = b.texture,
                        textureResolved = found,
                        materialHasTexture = matOk,
                        error = err,
                    });
                }

                return (object)new
                {
                    success = true,
                    biomesReported = rows.Count,
                    missingCount = missing.Count,
                    missing,
                    note = missing.Count > 0
                        ? "A biome whose texture did not resolve draws MAGENTA on the globe."
                        : "Every biome reported resolved its world texture.",
                    biomes = rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }

        // ====================================================================
        //  WHAT IS THIS FACTION'S LEADER CALLED
        // ====================================================================
        [Tool(
            "jawa/faction_leader_get",
            Description =
                "Report each faction's leader title and current leader. " +
                "🔑 Faction.LeaderTitle is NOT simply def.leaderTitle - it prefers the " +
                "faction's primary ideoligion's leaderTitleMale/Female and only falls back " +
                "to the def. So a campaign that authored a title on the FactionDef can be " +
                "silently overridden by a generated ideoligion, and the def keeps reading " +
                "correct offline. This reports the effective title, the def's title and the " +
                "ideo's title side by side so they cannot be confused. " +
                "Reads only; changes nothing.",
            ResultDescription =
                "per-faction rows: effectiveTitle, defTitle, ideoTitle, whether the ideo " +
                "overrode the def, and the leader's name if one exists.")]
        public static async Task<object> FactionLeaderGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated FactionDef names. Empty reports all.")] string factions = null,
            [ToolParameter(Description = "Include hidden factions. Default false.")] bool includeHidden = false)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                if (Find.FactionManager == null) return Fail("No faction manager - is a game loaded?");
                var want = new HashSet<string>((factions ?? "")
                    .Split(',').Select(s => s.Trim()).Where(s => s.Length > 0),
                    StringComparer.OrdinalIgnoreCase);

                var rows = new List<object>();
                int overridden = 0;
                foreach (var f in Find.FactionManager.AllFactions.ToList())
                {
                    if (f == null || f.def == null) continue;
                    if (!includeHidden && f.Hidden) continue;
                    if (want.Count > 0 && !want.Contains(f.def.defName)) continue;

                    string ideoTitle = null;
                    try
                    {
                        var ideo = f.ideos != null ? f.ideos.PrimaryIdeo : null;
                        if (ideo != null) ideoTitle = ideo.leaderTitleMale;
                    }
                    catch { }

                    string effective = null;
                    try { effective = f.LeaderTitle; } catch (Exception ex) { effective = "ERROR: " + ex.Message; }

                    bool ideoWon = !string.IsNullOrEmpty(ideoTitle) && ideoTitle != f.def.leaderTitle;
                    if (ideoWon) overridden++;

                    rows.Add(new
                    {
                        defName = f.def.defName,
                        name = f.Name,
                        effectiveTitle = effective,
                        defTitle = f.def.leaderTitle,
                        defTitleFemale = f.def.leaderTitleFemale,
                        ideoTitle,
                        ideoOverrodeDef = ideoWon,
                        leader = f.leader != null ? f.leader.Name?.ToStringFull : null,
                        hidden = f.Hidden,
                    });
                }

                return (object)new
                {
                    success = true,
                    factions = rows.Count,
                    ideoOverrodeDefCount = overridden,
                    note = overridden > 0
                        ? "Some factions take their leader title from a generated ideoligion, not " +
                          "from the def. The def reads correct offline and the game shows the other one."
                        : "Every reported faction takes its leader title from its def.",
                    rows,
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
