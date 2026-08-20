// ============================================================================
// JawaBenchFactionTools.cs - faction IDENTITY, as opposed to faction relations.
//
// 🔴 THE FINDING THAT FORCED THIS FILE, measured 2026-08-20 over the bridge on
// the authored 21,872-tile world:
//
//   TEN OF THE ELEVEN CAMPAIGN FACTIONS WERE WEARING NAMES THE DICE PICKED.
//   `Jawa_Junkers` was "Marina's Asteroids". `Jawa_HuttCartel` was "Southeast
//   Thiourhium". `Jawa_IndigenousTribes` - the Jawa Trade Moot, the player's own
//   people - was "Union of Aloisa". Only `Empire` was right, and only because it
//   is the single def carrying a `fixedName`.
//
// Every one of those defs has a CORRECT `label`. That is the trap: `label` is
// what the def is called, `fixedName` is what the world object carries, and with
// no `fixedName` RimWorld's name generator names the faction at world creation.
//
// 🔴 AND PATCHING THE DEFS AFTERWARDS DOES NOT FIX AN EXISTING WORLD:
//
//     public string Name { get { if (HasName) return name; return def.LabelCap; } }
//     public bool HasName => name != null;
//
// The generated string is stored on the faction object and shadows the def
// forever. So a world that has already been generated can only be repaired by
// writing to that field - which nothing on the bridge could do, which is why
// this file exists.
//
// ⭐ AND THE CHEAPEST REPAIR IS TO WRITE NOTHING: clearing the stored name makes
// `Name` fall through to `def.LabelCap`, which is already the authored label. No
// list of names to retype, and no chance of a typo putting a THIRD name into the
// world.
// ============================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimWorld;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/faction_name_get",
            Description =
                "Read what each faction is ACTUALLY called against what its def says it " +
                "should be called. Answers the one question no UI shows side by side: is " +
                "this faction wearing its authored name, or one the name generator picked " +
                "at world creation? A faction with storedName set and defLabel different " +
                "is wearing a generated name, and on a world meant to be frozen and " +
                "shipped that is permanent unless it is repaired.",
            ResultDescription =
                "Per faction: defName, currentName, storedName (null means it inherits), " +
                "defLabel, defFixedName, and isGenerated - true when a stored name differs " +
                "from the def label, which is the defect. Plus generatedCount.")]
        public static async Task<object> FactionNameGet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Include hidden factions (def.hidden), engine bookkeeping rather than " +
                "things the player meets.", DefaultValue = false)]
            bool includeHidden = false,
            [ToolParameter(Description = "Cap on returned factions.", DefaultValue = 500)]
            int limit = 500)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.World == null)
                    return Fail("No world loaded. Load or generate a game first.");
                var fm = Find.FactionManager;
                if (fm == null)
                    return Fail("No FactionManager on the current world.");

                var rows = new List<object>();
                int generated = 0, hiddenSkipped = 0;

                foreach (var f in fm.AllFactionsListForReading)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (f?.def == null) continue;
                    if (!includeHidden && f.def.hidden) { hiddenSkipped++; continue; }
                    if (rows.Count >= limit) break;

                    string stored = f.HasName ? f.Name : null;
                    string defLabel = f.def.LabelCap;
                    bool isGenerated = stored != null &&
                                       !string.Equals(stored, defLabel, StringComparison.Ordinal);
                    if (isGenerated) generated++;

                    rows.Add(new
                    {
                        defName = f.def.defName,
                        currentName = f.Name,
                        storedName = stored,
                        defLabel,
                        defFixedName = f.def.fixedName,
                        isPlayer = f.IsPlayer,
                        isGenerated
                    });
                }

                return (object)new
                {
                    success = true,
                    factions = rows,
                    count = rows.Count,
                    generatedCount = generated,
                    hiddenSkipped,
                    message = generated == 0
                        ? "Every faction is wearing its authored name."
                        : $"{generated} faction(s) are wearing a GENERATED name. On a world " +
                          "that will be frozen and shipped this is permanent unless repaired.",
                    ticksGame = TicksGameSafe()
                };
            });
        }

        [Tool(
            "jawa/faction_name_set",
            Description =
                "Repair or set a faction's name on a world that already exists. This is the " +
                "ONLY way to fix a faction wearing a generated name, because Faction.Name " +
                "returns the STORED name and a def patch cannot reach it. " +
                "DEFAULTS TO dryRun=true - it reports what it would do and writes nothing " +
                "until dryRun is passed false. " +
                "PREFER action=clear: it nulls the stored name so the faction inherits its " +
                "def label, which is already the authored one, with no list to retype and " +
                "no chance of a typo introducing a third name. Use action=set only where " +
                "the world must say something the def label does not. " +
                "Refuses by default to touch a faction already wearing its def label, so a " +
                "broad clear cannot quietly overwrite a deliberate name. " +
                "No redraw call is needed: a faction name is read on demand, and settlement " +
                "labels carry their own name and do not inherit it.",
            ResultDescription =
                "Per op: defName, before, after, changed, and refused with a reason when " +
                "skipped. Plus changedCount and refusedCount. A refusal is always reported, " +
                "never swallowed.")]
        public static async Task<object> FactionNameSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "clear = null the stored name so the faction inherits its def label. " +
                "set = write an explicit name.", DefaultValue = "clear")]
            string action = "clear",
            [ToolParameter(Description =
                "Which factions. Comma-separated defNames. Empty with action=clear means " +
                "EVERY faction currently wearing a generated name, which is the repair case.",
                DefaultValue = null)]
            string defNames = null,
            [ToolParameter(Description =
                "action=set only. Semicolon-separated defName=New Name pairs. Ignored by " +
                "action=clear.", DefaultValue = null)]
            string names = null,
            [ToolParameter(Description =
                "Refuse any faction whose stored name already equals its def label, so a " +
                "broad sweep cannot overwrite a name somebody chose on purpose.",
                DefaultValue = true)]
            bool onlyGenerated = true,
            [ToolParameter(Description =
                "Refuse to touch the player faction, whose name the player chose.",
                DefaultValue = true)]
            bool protectPlayer = true,
            [ToolParameter(Description =
                "Report only. Nothing is written unless this is false.", DefaultValue = true)]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.World == null)
                    return Fail("No world loaded. Load or generate a game first.");
                var fm = Find.FactionManager;
                if (fm == null)
                    return Fail("No FactionManager on the current world.");

                bool clearing = string.Equals(action, "clear", StringComparison.OrdinalIgnoreCase);
                if (!clearing && !string.Equals(action, "set", StringComparison.OrdinalIgnoreCase))
                    return Fail($"Unknown action '{action}'. Use clear or set.");

                // action=set needs an explicit name per faction. Parse first so a
                // malformed pair refuses before anything is written.
                var wanted = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
                if (!clearing)
                {
                    if (string.IsNullOrWhiteSpace(names))
                        return Fail("action=set needs names, as defName=New Name pairs " +
                                    "separated by semicolons.");
                    foreach (var piece in names.Split(';'))
                    {
                        if (string.IsNullOrWhiteSpace(piece)) continue;
                        int eq = piece.IndexOf('=');
                        if (eq <= 0)
                            return Fail($"Malformed pair '{piece.Trim()}'. Expected " +
                                        "defName=New Name.");
                        string k = piece.Substring(0, eq).Trim();
                        string v = piece.Substring(eq + 1).Trim();
                        if (k.Length == 0 || v.Length == 0)
                            return Fail($"Malformed pair '{piece.Trim()}'. Both halves are " +
                                        "required.");
                        wanted[k] = v;
                    }
                }

                var only = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                if (!string.IsNullOrWhiteSpace(defNames))
                    foreach (var d in defNames.Split(','))
                        if (!string.IsNullOrWhiteSpace(d)) only.Add(d.Trim());
                if (!clearing)
                    foreach (var k in wanted.Keys) only.Add(k);

                var results = new List<object>();
                int changed = 0, refused = 0;

                foreach (var f in fm.AllFactionsListForReading)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (f?.def == null) continue;
                    if (only.Count > 0 && !only.Contains(f.def.defName)) continue;

                    string before = f.Name;
                    string stored = f.HasName ? f.Name : null;
                    string defLabel = f.def.LabelCap;
                    bool isGenerated = stored != null &&
                                       !string.Equals(stored, defLabel, StringComparison.Ordinal);

                    string reason = null;
                    if (protectPlayer && f.IsPlayer)
                        reason = "player faction; pass protectPlayer false to include it";
                    else if (only.Count == 0 && !isGenerated)
                        reason = "not wearing a generated name";
                    else if (onlyGenerated && !isGenerated)
                        reason = "already wearing its def label; pass onlyGenerated false to force";

                    string after = before;
                    if (reason == null)
                    {
                        if (clearing) after = defLabel;
                        else if (!wanted.TryGetValue(f.def.defName, out after))
                            reason = "no name supplied for this defName";
                    }

                    if (reason != null)
                    {
                        refused++;
                        results.Add(new
                        {
                            defName = f.def.defName, before, after = before,
                            changed = false, refused = reason
                        });
                        continue;
                    }

                    if (string.Equals(before, after, StringComparison.Ordinal))
                    {
                        refused++;
                        results.Add(new
                        {
                            defName = f.def.defName, before, after,
                            changed = false, refused = "already that name"
                        });
                        continue;
                    }

                    if (!dryRun)
                    {
                        // The setter is a plain field write with no notify of any
                        // kind, so the read-back below is the whole verification.
                        f.Name = clearing ? null : after;
                    }

                    string readBack = dryRun ? after : f.Name;
                    bool ok = string.Equals(readBack, after, StringComparison.Ordinal);
                    if (ok) changed++; else refused++;

                    results.Add(new
                    {
                        defName = f.def.defName,
                        before,
                        after = readBack,
                        changed = ok,
                        refused = ok ? null : "write did not take; read-back disagrees"
                    });
                }

                return (object)new
                {
                    success = true,
                    dryRun,
                    action = clearing ? "clear" : "set",
                    results,
                    changedCount = changed,
                    refusedCount = refused,
                    message = dryRun
                        ? $"DRY RUN. {changed} faction(s) WOULD be renamed, {refused} " +
                          "refused. Nothing was written. Pass dryRun false to apply."
                        : $"{changed} faction(s) renamed, {refused} refused.",
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
