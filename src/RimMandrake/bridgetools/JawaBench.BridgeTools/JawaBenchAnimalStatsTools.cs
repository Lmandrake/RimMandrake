// JawaBenchAnimalStatsTools.cs - jawa/animal_stats, the fauna normalization instrument.
//
// WHY THIS FILE EXISTS
// ====================
// FAUNA_STATS_BRIDGE_TOOL_1. The normalization graphs (FAUNA_GRAPHS_SITTING_1)
// need six numbers per animal race and NOTHING on this bridge could deliver
// them in one call:
//
//   * jawa/get_defs reads named fields off any def reflectively, but MEASURED
//     2026-09-11 it cannot reach nested `race` fields (RaceProperties is a
//     nested object, not a scalar on ThingDef) nor list contents. bodySize and
//     the melee tool list are both on the far side of that wall.
//   * jawa/pawn_stats and jawa/thing_stats read a LIVE INSTANCE. Deliberately -
//     that is the whole point of those two. But a roster question ("where does
//     every animal sit on the bodySize/temperature/meat curve") is a question
//     about the DEFS, and answering it by spawning 326 pawns would be absurd,
//     would need a map, and would fold generation RNG into the answer.
//
// So this is the third member of the family and the only def-level one.
//
// THREE THINGS THE ITEM'S BRIEF GOT WRONG, ALL VERIFIED AGAINST 1.6 SOURCE
// =======================================================================
// The brief asked for `race.wildness`, `ComfortableTemperatureMin` and
// `ComfortableTemperatureMax`. None of those three exist in 1.6:
//
//   1. RaceProperties has NO `wildness` field. Wildness is a StatDef
//      (StatDefOf.Wildness, StatWorker_Wildness) read with
//      GetStatValueAbstract - see ThingDef.cs:1919, TrainableUtility.cs:189,
//      StockGenerator_Animals.cs:106. A reflective read of `race.wildness`
//      would have returned "(no such field)" forever.
//   2/3. The temperature stats are spelled ComfyTemperatureMin /
//      ComfyTemperatureMax, NOT Comfortable... (RimWorld/StatDefOf.cs; the
//      same trap jawa/pawn_stats' own Description already warns about).
//
// Vanilla's own animal debug table (Verse/DebugOutputsPawns.cs:344) is this
// exact row shape, and is the calibration reference for every getter here.
//
// WHY `explicitInDef` IS RETURNED BESIDE EVERY STAT VALUE
// =======================================================
// FAUNA_GRAPHS_SITTING_1 found only 14 of 326 animals carry an explicit
// meatAmount; the rest are engine-computed from bodySize. A graph that cannot
// tell an authored number from a derived one is drawing a straight line
// through the formula that made it and calling it a finding. StatBaseDefined
// (RimWorld/StatExtension.cs:27) answers that, so every stat row carries it.
//
// WHY MELEE IS A DEF-LEVEL WALK AND NOT StatDefOf.MeleeDPS
// ========================================================
// Vanilla's MeleeDps (DebugOutputsPawns.cs:542) GENERATES A PAWN, strips its
// hediffs, reads the stat and discards it to the world pawn pool. That is a
// write, it needs a game, and it is not what was asked for. Tool.power and
// Tool.cooldownTime are on the def and are what the graphs are normalizing.
//
// NO GAME REQUIRED. Every read here is off the DefDatabase, so this answers at
// the MAIN MENU with no map and no colony loaded. ticksGame will read -1 then,
// which is TicksGameSafe working, not a failure.
//
// THREAD AFFINITY: same rule as every other file here. Everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

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
        // ================================================================
        //  jawa/animal_stats
        // ================================================================
        [Tool(
            "jawa/animal_stats",
            Description =
                "Read the normalization numbers off ANIMAL RACE DEFS - body size, wildness, " +
                "comfortable temperature band, meat and leather yield, and the best melee tool - " +
                "for the whole roster in one call. " +
                "🔑 THIS READS THE DEF, NOT AN INSTANCE, and that is deliberate: jawa/pawn_stats " +
                "and jawa/thing_stats already read live things, but a roster curve is a question " +
                "about defs and spawning 326 pawns to answer it would fold generation RNG into " +
                "the answer. It needs NO MAP and NO GAME - it answers at the main menu. " +
                "It exists because jawa/get_defs cannot reach nested `race` fields or list " +
                "contents (MEASURED 2026-09-11), which is where bodySize and the tool list live. " +
                "⚠ THE OBVIOUS NAMES ARE WRONG, and this tool uses the real ones: there is no " +
                "`race.wildness` field in 1.6 - wildness is StatDefOf.Wildness, read abstractly - " +
                "and the temperature stats are ComfyTemperatureMin/ComfyTemperatureMax, NOT " +
                "Comfortable... " +
                "⚠ EVERY STAT CARRIES `explicitInDef`. Only 14 of 326 animals author meatAmount; " +
                "the rest are computed from bodySize by the stat worker, so a graph that cannot " +
                "tell the two apart is plotting the formula against its own input. " +
                "⚠ Melee is the DEF-LEVEL tool walk (Tool.power / Tool.cooldownTime), NOT " +
                "StatDefOf.MeleeDPS - vanilla computes that by generating and discarding a pawn, " +
                "which is a write and needs a game. bestByPower and bestByDps are BOTH returned " +
                "because they disagree (a slow heavy bite versus a fast light one) and 'best' " +
                "alone would silently pick one. " +
                "This tool writes nothing.",
            ResultDescription =
                "success, matched (how many races the filter selected before paging), count, " +
                "offset, limit, and animals[]: defName, label, modName, packageId, isAnimal, " +
                "bodySize (race.baseBodySize), healthScale (race.baseHealthScale), " +
                "stats{wildness, comfyTemperatureMin, comfyTemperatureMax, temperatureSpan, " +
                "meatAmount, leatherAmount} each a {value, explicitInDef} pair where value is " +
                "null - never 0 - if the worker threw, plus any names given in extraStats. " +
                "melee{toolCount, bestByPower, bestByDps, source} where each pick is " +
                "{label, power, cooldownTime, dps, armorPenetration, capacities[]}; melee is " +
                "null for a race with no tools and no melee verbs, which is a real answer. " +
                "notFound[] names every requested defName that did not resolve to a race def, " +
                "and refused[] every stat that did not resolve or threw, with suggestions.")]
        public static async Task<object> AnimalStats(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description =
                "Comma- or semicolon-separated ThingDef defNames, e.g. 'Muffalo,Thrumbo,Dromedary'. " +
                "Empty means THE WHOLE ROSTER - every ThingDef with a race, subject to animalsOnly. " +
                "A name that does not resolve, or resolves to a def with no race, is named in " +
                "notFound rather than dropped.")]
            string defs = null,
            [ToolParameter(Description =
                "With an empty 'defs': keep only race.Animal, i.e. exclude humanlikes, mechanoids " +
                "and entities. On by default - the normalization graphs are about animals. " +
                "Ignored when 'defs' names defs explicitly; a named def is always returned.",
                DefaultValue = true)]
            bool animalsOnly = true,
            [ToolParameter(Description =
                "Extra StatDef defNames to read abstractly off each def, comma-separated, e.g. " +
                "'MoveSpeed,MarketValue,FilthRate'. They land in the same stats map with the same " +
                "{value, explicitInDef} shape. This is here so a new axis on the graphs does NOT " +
                "cost a companion rebuild - and a rebuild can only happen with the game closed.")]
            string extraStats = null,
            [ToolParameter(Description =
                "Return the FULL tools[] list per animal beside the two picks. Off by default: " +
                "the roster is ~3 tools x 300+ races and it drowns the answer.",
                DefaultValue = false)]
            bool includeTools = false,
            [ToolParameter(Description = "Cap on rows returned. Default 400 - enough for the whole animal roster in one call.",
                DefaultValue = 400)]
            int limit = 400,
            [ToolParameter(Description = "Skip this many matching rows before returning any. Paging for a roster larger than 'limit'; 'matched' tells you how many there are in total.",
                DefaultValue = 0)]
            int offset = 0)
        {
            if (limit <= 0) return Fail("limit must be positive.");
            if (offset < 0) return Fail("offset cannot be negative.");

            var wantNames = (defs ?? "")
                .Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(q => q.Trim()).Where(q => q.Length > 0).ToList();
            var wantExtra = (extraStats ?? "")
                .Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries)
                .Select(q => q.Trim()).Where(q => q.Length > 0).ToList();

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                var refused = new List<object>();
                var notFound = new List<object>();

                // ---- resolve the stat defs ONCE ------------------------------
                // A stat that does not resolve is refused BY NAME with
                // suggestions. It is never quietly omitted: an absent key and a
                // key whose value is genuinely null must not look alike, and a
                // typo must not read as "this animal has no wildness".
                Func<string, StatDef> stat = nm =>
                {
                    var sd = DefDatabase<StatDef>.GetNamedSilentFail(nm);
                    if (sd == null)
                        refused.Add(new
                        {
                            stat = nm,
                            reason = "NoSuchStatDef",
                            suggestions = DefSuggestions<StatDef>(nm)
                        });
                    return sd;
                };

                // The five named stats, by their REAL 1.6 defNames.
                var sWildness = stat("Wildness");
                var sTempMin = stat("ComfyTemperatureMin");
                var sTempMax = stat("ComfyTemperatureMax");
                var sMeat = stat("MeatAmount");
                var sLeather = stat("LeatherAmount");

                var extra = new List<StatDef>();
                foreach (var nm in wantExtra)
                {
                    var sd = stat(nm);
                    if (sd != null) extra.Add(sd);
                }
                // A named extra stat that resolved nowhere is a failed call, not a
                // footnote - the caller asked a question about that axis and got no
                // answer. Same rule jawa/pawn_stats and jawa/thing_stats enforce.
                if (wantExtra.Count > 0 && extra.Count == 0)
                    return Fail("No extraStats name resolved. Nothing extra was measured.",
                        new { refused });

                // ---- select the defs -----------------------------------------
                var selected = new List<ThingDef>();
                if (wantNames.Count > 0)
                {
                    foreach (var nm in wantNames)
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        var d = DefDatabase<ThingDef>.GetNamedSilentFail(nm);
                        if (d == null)
                        {
                            notFound.Add(new
                            {
                                defName = nm,
                                reason = "NoSuchThingDef",
                                suggestions = DefSuggestions<ThingDef>(nm)
                            });
                            continue;
                        }
                        if (d.race == null)
                        {
                            // Loud, because this is the likely mistake: asking for
                            // a PawnKindDef name (Muffalo the kind) or a corpse def
                            // and getting an empty row would read as "that animal
                            // has no stats".
                            notFound.Add(new
                            {
                                defName = nm,
                                reason = "NotARaceDef",
                                message = "'" + nm + "' is a ThingDef but has no race block, so it is "
                                        + "not an animal race. If this is a PawnKindDef name, give the "
                                        + "RACE ThingDef it points at instead."
                            });
                            continue;
                        }
                        selected.Add(d);
                    }
                }
                else
                {
                    foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
                    {
                        cancellationToken.ThrowIfCancellationRequested();
                        if (d.race == null) continue;
                        if (animalsOnly && !d.race.Animal) continue;
                        selected.Add(d);
                    }
                    selected.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));
                }

                var matched = selected.Count;
                var page = selected.Skip(offset).Take(limit).ToList();

                var rows = new List<object>();
                foreach (var d in page)
                {
                    cancellationToken.ThrowIfCancellationRequested();

                    // Only the two temperature ends are read back as floats; the span
                    // below is the one derived number. Everything else goes straight
                    // into the map.
                    float? vTempMin, vTempMax, unused;
                    var statMap = new Dictionary<string, object>();
                    statMap["wildness"] = StatCell(d, sWildness, refused, out unused);
                    statMap["comfyTemperatureMin"] = StatCell(d, sTempMin, refused, out vTempMin);
                    statMap["comfyTemperatureMax"] = StatCell(d, sTempMax, refused, out vTempMax);
                    statMap["meatAmount"] = StatCell(d, sMeat, refused, out unused);
                    statMap["leatherAmount"] = StatCell(d, sLeather, refused, out unused);
                    foreach (var sd in extra)
                        statMap[sd.defName] = StatCell(d, sd, refused, out unused);

                    // The span is the number the tolerance law is actually about, and
                    // deriving it here means every consumer derives it the same way.
                    // It is null unless BOTH ends were measured - a span computed from
                    // one real end and one missing one is a fiction, and a fiction that
                    // would land in the middle of the healthy band rather than standing
                    // out as absent.
                    statMap["temperatureSpan"] = new
                    {
                        value = (vTempMin.HasValue && vTempMax.HasValue)
                            ? (float?)(vTempMax.Value - vTempMin.Value)
                            : null,
                        explicitInDef = (bool?)null
                    };

                    rows.Add(new
                    {
                        defName = d.defName,
                        label = d.label,
                        modName = d.modContentPack?.Name,
                        packageId = d.modContentPack?.PackageId,
                        isAnimal = d.race.Animal,
                        bodySize = d.race.baseBodySize,
                        healthScale = d.race.baseHealthScale,
                        stats = statMap,
                        melee = BestMelee(d, includeTools)
                    });
                }

                return new
                {
                    success = true,
                    message = string.Format(
                        "{0} animal race(s) read off the DEFS ({1} matched{2}){3}.",
                        rows.Count, matched,
                        offset > 0 || matched > rows.Count + offset
                            ? ", offset " + offset + " limit " + limit
                            : "",
                        refused.Count > 0 ? ", " + refused.Count + " REFUSED" : ""),
                    matched,
                    count = rows.Count,
                    offset,
                    limit,
                    animals = rows,
                    notFound,
                    refused,
                    readTheDefNotTheInstance = true,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // One stat, read off the DEF, as the {value, explicitInDef} pair every row
        // uses - and handed back through `value` as well, so a derived number like
        // the temperature span is computed from the float rather than dug back out
        // of the serialised shape.
        //
        // 🔴 A value we could not compute is null, NEVER 0. Zero meat and "the
        // worker threw" are different findings, and a graph cannot tell them apart
        // once they are both 0.
        //
        // explicitInDef is StatBaseDefined: did the def AUTHOR this number, or did
        // the stat worker derive it? FAUNA_GRAPHS_SITTING_1 found 14 of 326 animals
        // author meatAmount, and a curve fitted through 312 engine-computed values
        // is a picture of the engine's formula, not of the roster.
        private static object StatCell(ThingDef def, StatDef stat,
                                       List<object> refused, out float? value)
        {
            value = null;
            if (stat == null) return null;
            float? v = null;
            try { v = def.GetStatValueAbstract(stat); }
            catch (Exception ex)
            {
                refused.Add(new
                {
                    defName = def.defName,
                    stat = stat.defName,
                    reason = ex.GetType().Name,
                    message = ex.Message
                });
            }
            bool? isExplicit = null;
            try { isExplicit = def.StatBaseDefined(stat); } catch { isExplicit = null; }
            value = v;
            return new { value = v, explicitInDef = isExplicit };
        }

        // Walk the race's melee surface and pick the best tool two different ways.
        //
        // TOOLS FIRST, VERBS AS A FALLBACK, and the distinction is reported. A 1.6
        // animal carries Verse.Tool entries (claw, bite, head) and VerbProperties
        // only describes HOW they are swung. But a modded or hand-rolled race can
        // still declare a bare melee verb with meleeDamageBaseAmount and no tools
        // at all, and reporting that race as "no melee" would be a lie of exactly
        // the kind this bridge exists to stop.
        //
        // NULL IS A REAL ANSWER. A race with neither (a dryad, a plant-like entity)
        // returns melee: null, not a zero-power row - zero power and "nothing to
        // measure" are different facts.
        private static object BestMelee(ThingDef def, bool includeTools)
        {
            var rows = new List<Dictionary<string, object>>();
            string source = null;

            if (def.tools != null && def.tools.Count > 0)
            {
                source = "tools";
                foreach (var t in def.tools)
                {
                    if (t == null) continue;
                    rows.Add(new Dictionary<string, object>
                    {
                        { "label", t.label },
                        { "power", t.power },
                        { "cooldownTime", t.cooldownTime },
                        { "dps", t.cooldownTime > 0f ? (float?)(t.power / t.cooldownTime) : null },
                        // -1 is Tool's own "unset" sentinel, not a real penetration
                        // of minus one. Returned as null so nobody plots it.
                        { "armorPenetration", t.armorPenetration >= 0f ? (float?)t.armorPenetration : null },
                        { "capacities", t.capacities != null
                            ? t.capacities.Where(c => c != null).Select(c => c.defName).ToList()
                            : new List<string>() }
                    });
                }
            }
            // ⚠ ThingDef.verbs is PRIVATE in 1.6; ThingDef.Verbs is the only route,
            // and it returns a shared EMPTY LIST rather than null when there are
            // none. A null check against it would therefore never fire and a `.Count`
            // on the field would not compile - both worth knowing before the next
            // person "simplifies" this back.
            else if (def.Verbs.Count > 0)
            {
                foreach (var v in def.Verbs)
                {
                    if (v == null) continue;
                    bool melee;
                    try { melee = v.IsMeleeAttack; } catch { melee = false; }
                    if (!melee) continue;
                    source = "verbs";
                    rows.Add(new Dictionary<string, object>
                    {
                        { "label", v.label },
                        { "power", (float)v.meleeDamageBaseAmount },
                        { "cooldownTime", v.defaultCooldownTime },
                        { "dps", v.defaultCooldownTime > 0f
                            ? (float?)(v.meleeDamageBaseAmount / v.defaultCooldownTime) : null },
                        { "armorPenetration", (float?)null },
                        { "capacities", new List<string>() }
                    });
                }
            }

            if (rows.Count == 0) return null;

            // Highest power wins; a tie goes to the FASTER tool, because two
            // equal-power tools are not equally good and an arbitrary tie-break
            // would make the roster order decide the answer.
            var byPower = rows
                .OrderByDescending(r => (float)r["power"])
                .ThenBy(r => (float)r["cooldownTime"])
                .First();
            // A tool with no cooldown has no dps and must not sort as if it were
            // the worst - it is unmeasured, so it is excluded from this pick only.
            var dpsRows = rows.Where(r => r["dps"] != null).ToList();
            var byDps = dpsRows.Count > 0
                ? dpsRows.OrderByDescending(r => (float)r["dps"]).First()
                : null;

            return new
            {
                toolCount = rows.Count,
                source,
                bestByPower = byPower,
                bestByDps = byDps,
                // They disagree whenever a fast light tool out-DPSes a slow heavy
                // one, which is the common case on predators. Saying so here means
                // a caller cannot use one picture and think it is the other.
                picksAgree = byDps != null && ReferenceEquals(byPower, byDps),
                tools = includeTools ? rows : null
            };
        }
    }
}
