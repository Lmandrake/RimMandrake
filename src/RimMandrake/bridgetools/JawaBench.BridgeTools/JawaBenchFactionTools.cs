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
        // 🔴 THE NAME A FACTION IS SUPPOSED TO WEAR IS `fixedName` WHEN IT HAS ONE, NOT
        // `label`. Comparing against the label alone flags every reskin as generated -
        // differing from the label is exactly what a fixedName IS - so the old check fired
        // hardest on the nine factions that were CORRECT, the Galactic Empire and the
        // Junkers among them. Measured on a live 578-mod quicktest: 24 reported, 9 of them
        // false positives wearing their own defFixedName, 15 genuinely nameless.
        // ⛔ That was worse than a wrong number. `FACTION_NAMES_ARE_GENERATED_1` tells a
        // seat to run `faction_name_set action=clear` against whatever this reports, and
        // clear rewrote the name to `defLabel` - so the repair would have DELETED nine
        // authored names and called it a fix.
        // Corrected 2026-08-21, ISGENERATED_COMPARES_WRONG_FIELD_1.
        private static string AuthoredName(Faction f)
        {
            var fixedName = f?.def?.fixedName;
            return !string.IsNullOrEmpty(fixedName) ? fixedName : f?.def?.LabelCap;
        }

        [Tool(
            "jawa/faction_name_get",
            Description =
                "Read what each faction is ACTUALLY called against what its def says it " +
                "should be called. Answers the one question no UI shows side by side: is " +
                "this faction wearing its authored name, or one the name generator picked " +
                "at world creation? A faction whose stored name differs from its AUTHORED " +
                "name - fixedName where the def has one, label otherwise - is wearing a " +
                "generated name, and on a world meant to be frozen and shipped that is " +
                "permanent unless it is repaired.",
            ResultDescription =
                "Per faction: defName, currentName, storedName (null means it inherits), " +
                "defLabel, defFixedName, authoredName, hasFixedName, and isGenerated - " +
                "true when a stored name differs from the AUTHORED name (fixedName where " +
                "the def has one, label otherwise). Plus generatedCount and " +
                "generatedOverAuthoredCount, reported separately: only the latter is a " +
                "defect with a known repair.")]
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
                int generated = 0, generatedOverAuthored = 0, hiddenSkipped = 0;

                foreach (var f in fm.AllFactionsListForReading)
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    if (f?.def == null) continue;
                    if (!includeHidden && f.def.hidden) { hiddenSkipped++; continue; }
                    if (rows.Count >= limit) break;

                    string stored = f.HasName ? f.Name : null;
                    string defLabel = f.def.LabelCap;
                    string authored = AuthoredName(f);
                    bool hasFixedName = !string.IsNullOrEmpty(f.def.fixedName);
                    bool isGenerated = stored != null &&
                                       !string.Equals(stored, authored, StringComparison.Ordinal);
                    if (isGenerated) generated++;
                    // 🔑 The two populations are reported SEPARATELY, never summed. A faction
                    // with no fixedName that drew a generated name is ordinary and may be
                    // what the design wants; one that HAS an authored name and is not
                    // wearing it is the actual defect. One number could not tell them apart.
                    if (isGenerated && hasFixedName) generatedOverAuthored++;

                    rows.Add(new
                    {
                        defName = f.def.defName,
                        currentName = f.Name,
                        storedName = stored,
                        defLabel,
                        defFixedName = f.def.fixedName,
                        authoredName = authored,
                        hasFixedName,
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
                    generatedOverAuthoredCount = generatedOverAuthored,
                    hiddenSkipped,
                    message = generated == 0
                        ? "Every faction is wearing its authored name."
                        : $"{generated} faction(s) are wearing a GENERATED name, " +
                          $"{generatedOverAuthored} of them OVER AN AUTHORED fixedName. On a " +
                          "world that will be frozen and shipped this is permanent unless " +
                          "repaired. Repair the generatedOverAuthored ones first - the rest " +
                          "carry no authored name to go back to.",
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
                    string authored = AuthoredName(f);
                    bool isGenerated = stored != null &&
                                       !string.Equals(stored, authored, StringComparison.Ordinal);

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
                        // ⛔ CLEARING GOES BACK TO THE AUTHORED NAME, NOT THE LABEL. This
                        // line used to write `defLabel`, which on a fixedName faction
                        // DESTROYS the authored name - the exact damage the corrected
                        // isGenerated above exists to stop being aimed at.
                        if (clearing) after = authored;
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

        [Tool(
            "jawa/faction_create",
            Description =
                "Create a faction that worldgen never made, and add it to the world. " +
                "This is the only route for a faction that is ABSENT from an existing " +
                "world: requiredCountAtGameStart is read at world generation and nowhere " +
                "else, and the only load-time top-up is a hardcoded list of five vanilla " +
                "factions, so a missing faction cannot arrive by patching a def. " +
                "WHY ONE GOES MISSING, which is worth checking before creating it: " +
                "FactionGenerator.InitializeFactions skips a def entirely when ANY other " +
                "def declares replacesFaction at it with requiredCountAtGameStart above " +
                "zero. Biotech's PirateWaster replaces vanilla Pirate that way, which is " +
                "why the reskinned Blackstar Company was never generated. " +
                "DEFAULTS TO dryRun=true. " +
                "REFUSES a def that already has a faction, and refuses a hidden def " +
                "unless forced, because a hidden faction is engine bookkeeping and " +
                "creating one by accident is silent. " +
                "TRAP: the new faction is NAMED BY THE GENERATOR unless its def carries " +
                "fixedName, so it will arrive wearing a random name. Clear it afterwards " +
                "with the faction name setter in this same family. " +
                "Relations with existing factions are wired automatically.",
            ResultDescription =
                "created, defName, name, wasHidden, plus factionCountBefore and " +
                "factionCountAfter so the add is visible as a delta and not only as a flag.")]
        public static async Task<object> FactionCreate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName to create.", DefaultValue = null)]
            string defName = null,
            [ToolParameter(Description =
                "Create it even though the def is hidden. Hidden factions are engine " +
                "bookkeeping and are almost never what you want.", DefaultValue = false)]
            bool allowHidden = false,
            [ToolParameter(Description =
                "Create a SECOND instance even though one already exists. Vanilla does " +
                "this for factions with a count above one; usually it is a mistake.",
                DefaultValue = false)]
            bool allowDuplicate = false,
            [ToolParameter(Description =
                "Report only. Nothing is created unless this is false.", DefaultValue = true)]
            bool dryRun = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                if (Find.World == null)
                    return Fail("No world loaded. Load or generate a game first.");
                var fm = Find.FactionManager;
                if (fm == null)
                    return Fail("No FactionManager on the current world.");
                if (string.IsNullOrWhiteSpace(defName))
                    return Fail("defName is required.");

                var def = DefDatabase<FactionDef>.GetNamedSilentFail(defName.Trim());
                if (def == null)
                    return Fail($"No FactionDef named '{defName.Trim()}'.",
                                new { suggestions = DefSuggestions<FactionDef>(defName.Trim()) });

                var existing = fm.AllFactionsListForReading
                    .Where(f => f?.def == def).ToList();
                if (existing.Count > 0 && !allowDuplicate)
                    return Fail(
                        $"'{def.defName}' already exists in this world as " +
                        $"'{existing[0].Name}'. Pass allowDuplicate to add another.",
                        new { existingCount = existing.Count, existingName = existing[0].Name });

                if (def.hidden && !allowHidden)
                    return Fail(
                        $"'{def.defName}' is a HIDDEN faction def - engine bookkeeping, not " +
                        "something the player meets. It will never appear on the Configure " +
                        "Factions screen and, with settlementGenerationWeight 0, never places " +
                        "a settlement. Pass allowHidden only if you are certain.",
                        new { hidden = true, settlementGenerationWeight = def.settlementGenerationWeight });

                int before = fm.AllFactionsListForReading.Count;

                // What SHOULD have created this at worldgen, and why it did not.
                // Reported either way, because it decides whether creating the
                // faction here is a repair or a workaround that recurs.
                var replacedBy = DefDatabase<FactionDef>.AllDefs
                    .Where(d => d.requiredCountAtGameStart > 0 && d.replacesFaction == def)
                    .Select(d => d.defName).ToList();

                if (dryRun)
                {
                    return (object)new
                    {
                        success = true,
                        dryRun = true,
                        created = false,
                        defName = def.defName,
                        defLabel = def.LabelCap,
                        defFixedName = def.fixedName,
                        factionCountBefore = before,
                        factionCountAfter = before,
                        displacedBy = replacedBy,
                        message = $"DRY RUN. Would create '{def.defName}'. Nothing was " +
                                  "written. Pass dryRun false to apply." +
                                  (replacedBy.Count > 0
                                      ? $" NOTE: worldgen skips this def because " +
                                        $"{string.Join(", ", replacedBy)} declares " +
                                        "replacesFaction at it, so any FUTURE world will be " +
                                        "missing it again unless that is addressed."
                                      : "") +
                                  (def.fixedName == null
                                      ? " NOTE: the def has no fixedName, so the new faction " +
                                        "will be named by the generator."
                                      : ""),
                        ticksGame = TicksGameSafe()
                    };
                }

                FactionGenerator.CreateFactionAndAddToManager(def);

                // Read back off the manager, not off the call - the method returns void.
                var made = fm.AllFactionsListForReading.LastOrDefault(f => f?.def == def);
                int after = fm.AllFactionsListForReading.Count;
                bool ok = made != null && after == before + 1;

                if (!ok)
                    return Fail(
                        $"Created '{def.defName}' but the FactionManager does not show it. " +
                        $"Count went {before} -> {after}.",
                        new { factionCountBefore = before, factionCountAfter = after });

                return (object)new
                {
                    success = true,
                    dryRun = false,
                    created = true,
                    defName = def.defName,
                    name = made.Name,
                    defLabel = def.LabelCap,
                    generatedName = def.fixedName == null &&
                                    !string.Equals(made.Name, def.LabelCap, StringComparison.Ordinal),
                    wasHidden = def.hidden,
                    factionCountBefore = before,
                    factionCountAfter = after,
                    displacedBy = replacedBy,
                    message = $"Created '{def.defName}' as '{made.Name}'. " +
                              (def.fixedName == null
                                  ? "It is wearing a GENERATED name - clear the stored name " +
                                    "to make it inherit its def label. "
                                  : "") +
                              "SAVE the game or this is lost.",
                    ticksGame = TicksGameSafe()
                };
            });
        }
    }
}
