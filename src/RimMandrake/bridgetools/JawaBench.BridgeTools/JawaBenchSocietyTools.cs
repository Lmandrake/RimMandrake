// JawaBenchSocietyTools.cs - Group J out of
// infrastructure/state/work/BRIDGE_TOOLS_MEDIUM_REMAINING.md:
// Ideology/precepts/rituals, settlements/caravans/gravship, genes/xenotypes,
// pawn state & health.
//
// EVERY SIGNATURE BELOW WAS READ OUT OF 1.6 SOURCE VIA rimsage, NOT GUESSED:
//   RimWorld/IdeoGenerator.cs, RimWorld/IdeoGenerationParms.cs,
//   RimWorld/PreceptMaker.cs, RimWorld/Ideo.cs, RimWorld/IdeoFoundation.cs,
//   RimWorld/IdeoManager.cs, RimWorld/Precept_Ritual.cs, RimWorld/RitualObligation.cs,
//   Verse/ThingStyleCategoryWithPriority.cs, Verse/GetOrGenerateMapUtility.cs,
//   RimWorld/Planet/SettlementAbandonUtility.cs, RimWorld/Planet/MapParent.cs,
//   Verse/WorldObject.cs, Verse/Game.cs (FindMap, DeinitAndRemoveMap),
//   RimWorld/Planet/CaravanFormingUtility.cs, RimWorld/Planet/CaravanExitMapUtility.cs,
//   RimWorld/Planet/CaravanMaker.cs, RimWorld/GeneUtility.cs, RimWorld/GeneSet.cs,
//   RimWorld/Pawn_GeneTracker.cs, Verse/HealthUtility.cs, Verse/Pawn_HealthTracker.cs.
//
// 11 roster rows, 1 SKIPPED as already covered (see bottom of this comment):
//   install-bionic  -> jawa/pawn_health (action='bionic') ALREADY does exactly the
//                      "cheap route" the roster names: RestorePart(part) then
//                      AddHediff(def, part) - no RecipeDef, no surgeon. Nothing new
//                      was needed for that row.
//
// TWO TRAPS THIS PROJECT HAS ALREADY PAID FOR, BOTH LIVE HERE:
//   1. THERE IS NO IdeoDef. An Ideo is a runtime object with no def-database
//      identity - it is reached ONLY through Find.IdeoManager.IdeosListForReading,
//      matched by numeric id or a substring of its generated `name`. Every tool
//      below that takes an "ideo" argument uses the SAME resolver
//      (ResolveIdeoArg, in JawaBenchGroupTools.cs) jawa/ideo_set_primary and
//      jawa/ideo_development already use - not a fresh lookup.
//   2. ADDING A GENE FIRES Notify_GenesChanged, WHICH RE-ROLLS THE HEAD TYPE.
//      jawa/gene_random_set and jawa/gene_reimplant both add genes (directly, or
//      via GeneUtility.ReimplantXenogerm's own AddGene loop) - order is genes
//      first, any appearance/head edit second. This is documented in each tool's
//      Description, not suppressed.
//
// OTHER SILENT-FAILURE TRAPS NAMED BY THE ROSTER AND HANDLED EXPLICITLY HERE:
//   * Ideo.AddPrecept has NO return value and Log.Errors (not throws) on a null
//     or duplicate precept - jawa/ideo_precept_edit calls IdeoFoundation.CanAdd
//     BEFORE adding and refuses on its AcceptanceReport, rather than trusting a
//     void call.
//   * Precept_Ritual.AddObligation is void and SILENTLY DOES NOTHING when
//     ideo.ObligationsActive is false (and the ritual does not allow optional
//     obligations), OR when a required, currently-inactive role exists on the
//     ritual. jawa/ideo_ritual_obligation reads activeObligations.Count before
//     and after and reports success = (after > before), never trusting the void
//     return.
//   * HealthUtility.AdjustSeverity is an OFFSET, not an absolute severity, and it
//     is ALSO a silent no-op: sevOffset == 0 does nothing, and a NEGATIVE offset
//     on a hediff the pawn does not have does nothing (only a positive offset
//     creates one). jawa/pawn_severity_adjust refuses both no-op shapes instead
//     of reporting a false success, and calls Pawn_HealthTracker.CheckForStateChange
//     afterward - AdjustSeverity itself never does, so a severity push into death
//     or downed is not re-evaluated unless something calls it.
//   * GeneUtility.ReimplantXenogerm does NOT itself guard against killing the
//     CASTER - the death guard (SetXenotype to Baseliner) lives inside
//     ExtractXenogerm, which ReimplantXenogerm calls on the caster as its last
//     step. jawa/gene_reimplant pre-checks GeneUtility.PawnWouldDieFromReimplanting
//     on the CASTER (the pawn whose xenogerm is being extracted) and refuses
//     unless force=true, rather than relying on that internal mitigation.
//
// THREAD AFFINITY: same rule as every other file here - everything that touches
// game state is inside ctx.MainThread.InvokeAsync and nothing else is.

using System;
using System.Collections.Generic;
using System.Linq;
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
        // ================================================================
        //  Ideology, precepts & rituals
        // ================================================================

        [Tool(
            "jawa/ideo_create",
            Description =
                "IdeoGenerator.GenerateIdeo(IdeoGenerationParms) + Find.IdeoManager.Add(ideo) - a " +
                "whole new religion at runtime, not attached to any faction until " +
                "jawa/ideo_set_primary points one at it. " +
                "🔴 THERE IS NO IdeoDef - the result is a runtime object identified only by " +
                "numeric id and generated name; every other ideo tool on this bridge (jawa/ideo_of, " +
                "jawa/ideo_set_primary, jawa/ideo_development, jawa/ideo_precept_edit, " +
                "jawa/ideo_ritual_obligation, jawa/ideo_style) resolves it that same way. " +
                "⚠️ GenerateIdeo picks a RANDOM IdeoFoundationDef and its abstract Init(parms) " +
                "rolls memes appropriate to 'faction' - there is no direct control over the " +
                "foundation type or the exact meme roll beyond 'forcedMemes'/'disallowedMemes'. " +
                "'name'/'description'/'hidden' are applied AFTER Init, the same order " +
                "IdeoGenerator.MakeFixedIdeo uses for a scenario-fixed ideo, because Init's own " +
                "handling of those three fields is foundation-specific and not guaranteed. " +
                "Requires Ideology.",
            ResultDescription =
                "success, id, name, description, hidden, foundation (class name), memes[], " +
                "preceptCount, addedToManager (IdeoManager.Add's own bool).")]
        public static async Task<object> IdeoCreate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "FactionDef defName this ideo is generated FOR - shapes which memes Init is allowed to roll. Required by IdeoGenerationParms.")]
            string faction,
            [ToolParameter(Description = "Name the generated ideo. Empty keeps whatever Init produced.")]
            string name = null,
            [ToolParameter(Description = "Description text. Empty keeps whatever Init produced.")]
            string description = null,
            [ToolParameter(Description = "Mark the ideo hidden (not shown in the normal ideo list UI).")]
            bool hidden = false,
            [ToolParameter(Description = "Comma-separated MemeDef defNames that MUST be included.")]
            string forcedMemes = null,
            [ToolParameter(Description = "Comma-separated MemeDef defNames that must NOT be included.")]
            string disallowedMemes = null,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(faction)) return Fail("faction is required - IdeoGenerationParms needs a forFaction.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There is no IdeoGenerator to run.");

                var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));

                List<MemeDef> forced = null, disallowed = null;
                var badMemes = new List<object>();
                Func<string, List<MemeDef>> parseMemes = raw =>
                {
                    if (string.IsNullOrWhiteSpace(raw)) return null;
                    var list = new List<MemeDef>();
                    foreach (var tok in raw.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                    {
                        var nm = tok.Trim();
                        if (nm.Length == 0) continue;
                        var md = DefDatabase<MemeDef>.GetNamedSilentFail(nm);
                        if (md == null) badMemes.Add(new { meme = nm, suggestions = DefSuggestions<MemeDef>(nm) });
                        else list.Add(md);
                    }
                    return list;
                };
                forced = parseMemes(forcedMemes);
                disallowed = parseMemes(disallowedMemes);
                if (badMemes.Count > 0) return Fail("Unknown MemeDef(s).", new { badMemes });

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        faction = fd.defName,
                        name,
                        description,
                        hidden,
                        forcedMemes = forced != null ? forced.Select(m => m.defName).ToList() : null,
                        disallowedMemes = disallowed != null ? disallowed.Select(m => m.defName).ToList() : null
                    };

                var parms = new IdeoGenerationParms(
                    fd,
                    disallowedMemes: disallowed,
                    forcedMemes: forced,
                    name: name ?? "",
                    hidden: hidden,
                    description: description ?? "");

                Ideo ideo;
                try { ideo = IdeoGenerator.GenerateIdeo(parms); }
                catch (Exception e) { return Fail("GenerateIdeo threw: " + e.GetType().Name + ": " + e.Message); }
                if (ideo == null) return Fail("GenerateIdeo returned null.");

                // Applied AFTER Init, same order IdeoGenerator.MakeFixedIdeo uses - Init's
                // own field handling is foundation-specific and not guaranteed to set these.
                if (!string.IsNullOrEmpty(name)) ideo.name = name;
                if (!string.IsNullOrEmpty(description)) ideo.description = description;
                ideo.hidden = hidden;

                bool added;
                try { added = Find.IdeoManager.Add(ideo); }
                catch (Exception e) { return Fail("IdeoManager.Add threw: " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = added,
                    id = ideo.id,
                    name = ideo.name,
                    description = ideo.description,
                    hidden = ideo.hidden,
                    foundation = ideo.foundation != null ? ideo.foundation.GetType().Name : null,
                    memes = ideo.memes != null ? ideo.memes.Select(m => m.defName).ToList() : new List<string>(),
                    preceptCount = ideo.PreceptsListForReading != null ? ideo.PreceptsListForReading.Count : 0,
                    addedToManager = added,
                    note = "The ideo has NO IdeoDef and no faction yet - use jawa/ideo_set_primary to attach it.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/ideo_precept_edit",
            Description =
                "Add or remove a precept on a runtime Ideo (resolved the same way jawa/ideo_of does " +
                "- id or a substring of its name). action='add': PreceptMaker.MakePrecept(PreceptDef) " +
                "then Ideo.AddPrecept(p, init:true, null, def.ritualPatternBase) so a ritual precept " +
                "is filled the same way generation fills one. action='remove': Ideo.RemovePrecept on " +
                "a live Precept matched by defName or label. " +
                "⚠️ AddPrecept ITSELF HAS NO REFUSAL PATH - it Log.Errors on null/duplicate and " +
                "otherwise always adds. The real gate is IdeoFoundation.CanAdd (exclusionTags, " +
                "conflictingMemes, requiredMemes, issue collisions, the 2-multi-role cap) and THIS " +
                "TOOL CALLS IT BEFORE ADDING, refusing on its AcceptanceReport reason rather than " +
                "trusting AddPrecept's void return.",
            ResultDescription =
                "success, action, ideo{id,name}, precept{def,label}, acceptance (CanAdd's reason, " +
                "add only), preceptCountBefore, preceptCountAfter.")]
        public static async Task<object> IdeoPreceptEdit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")]
            string ideo,
            [ToolParameter(Description = "'add' or 'remove'.")]
            string action = "add",
            [ToolParameter(Description = "add: a PreceptDef defName. remove: a defName or label substring matching a precept already on this ideo.")]
            string precept = null,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(ideo)) return Fail("ideo is required - a numeric id or a substring of its name, per jawa/ideo_of.");
            if (string.IsNullOrWhiteSpace(precept)) return Fail("precept is required.");
            var A = (action ?? "add").Trim().ToLowerInvariant();
            if (A != "add" && A != "remove") return Fail("action must be add|remove.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There are no runtime precepts to edit.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;
                if (target.foundation == null) return Fail("This ideo has no IdeoFoundation (target.foundation is null) - cannot evaluate CanAdd.");

                int before = target.PreceptsListForReading != null ? target.PreceptsListForReading.Count : 0;

                if (A == "add")
                {
                    var pd = DefDatabase<PreceptDef>.GetNamedSilentFail(precept.Trim());
                    if (pd == null) return Fail("No PreceptDef '" + precept + "'.", DefSuggestions<PreceptDef>(precept));

                    var accept = target.foundation.CanAdd(pd);
                    if (!accept.Accepted)
                        return Fail("IdeoFoundation.CanAdd refused '" + pd.defName + "': " + accept.Reason);

                    if (dryRun)
                        return new { success = true, dryRun = true, action = A, ideo = new { target.id, target.name }, precept = pd.defName, preceptCountBefore = before };

                    Precept made;
                    try { made = PreceptMaker.MakePrecept(pd); }
                    catch (Exception e) { return Fail("MakePrecept threw: " + e.GetType().Name + ": " + e.Message); }

                    try { target.AddPrecept(made, init: true, null, pd.ritualPatternBase); }
                    catch (Exception e) { return Fail("AddPrecept threw: " + e.GetType().Name + ": " + e.Message); }

                    int after = target.PreceptsListForReading.Count;
                    return new
                    {
                        success = after > before,
                        action = A,
                        ideo = new { target.id, target.name },
                        precept = new { def = pd.defName, label = made.Label },
                        acceptance = accept.Reason,
                        preceptCountBefore = before,
                        preceptCountAfter = after,
                        ticksGame = TicksGameSafe()
                    };
                }
                else
                {
                    var wanted = precept.Trim();
                    var matches = (target.PreceptsListForReading ?? new List<Precept>()).Where(p => p != null && (
                        string.Equals(p.def != null ? p.def.defName : null, wanted, StringComparison.OrdinalIgnoreCase)
                        || (p.def != null && p.def.defName != null && p.def.defName.IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)
                        || (p.Label ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();

                    if (matches.Count == 0)
                        return Fail("'" + wanted + "' matches no precept on ideo '" + target.name + "'.",
                            new { precepts = target.PreceptsListForReading.Select(p => new { def = p.def != null ? p.def.defName : null, label = p.Label }).ToList() });
                    if (matches.Count > 1)
                        return Fail("'" + wanted + "' matches " + matches.Count + " precepts ambiguously.",
                            new { matches = matches.Select(p => new { def = p.def != null ? p.def.defName : null, label = p.Label }).ToList() });
                    var victim = matches[0];

                    if (dryRun)
                        return new { success = true, dryRun = true, action = A, ideo = new { target.id, target.name }, precept = new { def = victim.def.defName, label = victim.Label }, preceptCountBefore = before };

                    try { target.RemovePrecept(victim); }
                    catch (Exception e) { return Fail("RemovePrecept threw: " + e.GetType().Name + ": " + e.Message); }

                    int after = target.PreceptsListForReading.Count;
                    bool stillPresent = target.PreceptsListForReading.Contains(victim);
                    return new
                    {
                        success = !stillPresent,
                        action = A,
                        ideo = new { target.id, target.name },
                        precept = new { def = victim.def.defName, label = victim.Label },
                        preceptCountBefore = before,
                        preceptCountAfter = after,
                        note = "RemovePrecept can auto-replace a required-issue precept with a randomly chosen " +
                               "default one of the same issue - preceptCountAfter may equal preceptCountBefore " +
                               "even though the NAMED precept is gone.",
                        ticksGame = TicksGameSafe()
                    };
                }
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/ideo_ritual_obligation",
            Description =
                "Precept_Ritual.AddObligation(new RitualObligation(ritual, expires)) - make the " +
                "colony owe a named ritual on a named ideo, resolved the same way jawa/ideo_of does. " +
                "🔴 AddObligation IS A SILENT NO-OP, not a refusal, in TWO cases: (1) " +
                "ideo.ObligationsActive is false AND the ritual's def does not allow optional " +
                "obligations, or (2) the ritual has a REQUIRED role that is currently inactive - " +
                "AddObligation returns void either way. THIS TOOL READS activeObligations.Count " +
                "BEFORE AND AFTER and reports success = (after > before), never the bare call.",
            ResultDescription =
                "success, ideo{id,name}, ritual{def,label}, obligationCountBefore, " +
                "obligationCountAfter, obligationsActiveOnIdeo, allowsOptionalObligations.")]
        public static async Task<object> IdeoRitualObligation(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")]
            string ideo,
            [ToolParameter(Description = "PreceptDef defName or label substring matching a Precept_Ritual already on this ideo.")]
            string ritual,
            [ToolParameter(Description = "RitualObligation.sendLetter - fire the vanilla opportunity letter if the ritual's def allows it.")]
            bool sendLetter = false,
            [ToolParameter(Description = "RitualObligation.expires - let it lapse after the vanilla expiry window.")]
            bool expires = true,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(ideo)) return Fail("ideo is required - a numeric id or a substring of its name, per jawa/ideo_of.");
            if (string.IsNullOrWhiteSpace(ritual)) return Fail("ritual is required.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There are no ritual obligations.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;

                var wanted = ritual.Trim();
                var matches = (target.PreceptsListForReading ?? new List<Precept>()).OfType<Precept_Ritual>().Where(r => r != null && (
                    string.Equals(r.def != null ? r.def.defName : null, wanted, StringComparison.OrdinalIgnoreCase)
                    || (r.def != null && r.def.defName != null && r.def.defName.IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)
                    || (r.Label ?? "").IndexOf(wanted, StringComparison.OrdinalIgnoreCase) >= 0)).ToList();

                if (matches.Count == 0)
                    return Fail("'" + wanted + "' matches no ritual precept on ideo '" + target.name + "'.",
                        new { rituals = target.PreceptsListForReading.OfType<Precept_Ritual>().Select(r => new { def = r.def.defName, label = r.Label }).ToList() });
                if (matches.Count > 1)
                    return Fail("'" + wanted + "' matches " + matches.Count + " ritual precepts ambiguously.",
                        new { matches = matches.Select(r => new { def = r.def.defName, label = r.Label }).ToList() });
                var targetRitual = matches[0];

                int before = targetRitual.activeObligations != null ? targetRitual.activeObligations.Count : 0;
                bool obligationsActive = target.ObligationsActive;
                bool allowsOptional = targetRitual.def != null && targetRitual.def.allowOptionalRitualObligations;

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        ideo = new { target.id, target.name },
                        ritual = new { def = targetRitual.def.defName, label = targetRitual.Label },
                        obligationCountBefore = before,
                        obligationsActiveOnIdeo = obligationsActive,
                        allowsOptionalObligations = allowsOptional,
                        willLikelyNoOp = !obligationsActive && !allowsOptional
                    };

                var obligation = new RitualObligation(targetRitual, expires) { sendLetter = sendLetter };
                try { targetRitual.AddObligation(obligation); }
                catch (Exception e) { return Fail("AddObligation threw: " + e.GetType().Name + ": " + e.Message); }

                int after = targetRitual.activeObligations != null ? targetRitual.activeObligations.Count : 0;
                bool ok = after > before;

                return new
                {
                    success = ok,
                    ideo = new { target.id, target.name },
                    ritual = new { def = targetRitual.def.defName, label = targetRitual.Label },
                    obligationCountBefore = before,
                    obligationCountAfter = after,
                    obligationsActiveOnIdeo = obligationsActive,
                    allowsOptionalObligations = allowsOptional,
                    note = ok
                        ? "Obligation queued."
                        : "AddObligation returned without adding one. Either ObligationsActive is false " +
                          "and the ritual does not allow optional obligations, or a required role on this " +
                          "ritual is currently inactive - the engine does not say which.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/ideo_style",
            Description =
                "How a runtime Ideo LOOKS: list/add/remove entries in Ideo.thingStyleCategories " +
                "(StyleCategoryDef + priority), or set its icon via Ideo.SetIcon(IdeoIconDef, " +
                "ColorDef, clearPrimaryFactionColor). " +
                "⚠️ SetIcon OVERWRITES BOTH iconDef AND colorDef UNCONDITIONALLY - action='icon' " +
                "requires BOTH 'icon' and 'color' even if only one is actually changing, so a " +
                "caller never silently blanks the other.",
            ResultDescription =
                "success, action, ideo{id,name}, and for list/add/remove: styles[] " +
                "{category,priority}; for icon: iconDef, colorDef, colorHex.")]
        public static async Task<object> IdeoStyle(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Ideo id (numeric) or a substring of its name, per jawa/ideo_of.")]
            string ideo,
            [ToolParameter(Description = "'list' | 'add' | 'remove' | 'icon'.")]
            string action = "list",
            [ToolParameter(Description = "add/remove: a StyleCategoryDef defName.")]
            string category = null,
            [ToolParameter(Description = "add: priority for the new entry. Higher sorts first via Ideo.SortStyleCategories().")]
            float priority = 1f,
            [ToolParameter(Description = "icon: an IdeoIconDef defName. Required together with 'color'.")]
            string icon = null,
            [ToolParameter(Description = "icon: a ColorDef defName - SetIcon's signature takes a ColorDef, not a raw color, so 'r,g,b' or '#RRGGBB' cannot be used here. Required together with 'icon'.")]
            string color = null,
            [ToolParameter(Description = "icon: also clear Ideo.primaryFactionColor so the new color actually shows.")]
            bool clearPrimaryFactionColor = false,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(ideo)) return Fail("ideo is required - a numeric id or a substring of its name, per jawa/ideo_of.");
            var A = (action ?? "list").Trim().ToLowerInvariant();
            if (A != "list" && A != "add" && A != "remove" && A != "icon") return Fail("action must be list|add|remove|icon.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (!ModsConfig.IdeologyActive) return Fail("Ideology is NOT active. There is no Ideo to style.");

                Ideo target;
                var resolveFail = ResolveIdeoArg(ideo, out target);
                if (resolveFail != null) return resolveFail;

                Func<object> listStyles = () => target.thingStyleCategories == null
                    ? new List<object>()
                    : target.thingStyleCategories.Select(s => new { category = s.category != null ? s.category.defName : null, s.priority }).ToList();

                if (A == "list")
                    return new
                    {
                        success = true,
                        action = A,
                        ideo = new { target.id, target.name },
                        styles = listStyles(),
                        iconDef = target.iconDef != null ? target.iconDef.defName : null,
                        colorDef = target.colorDef != null ? target.colorDef.defName : null,
                        ticksGame = TicksGameSafe()
                    };

                if (A == "add" || A == "remove")
                {
                    if (string.IsNullOrWhiteSpace(category)) return Fail("category is required for add|remove.");
                    var cd = DefDatabase<StyleCategoryDef>.GetNamedSilentFail(category.Trim());
                    if (cd == null) return Fail("No StyleCategoryDef '" + category + "'.", DefSuggestions<StyleCategoryDef>(category));

                    if (target.thingStyleCategories == null) target.thingStyleCategories = new List<ThingStyleCategoryWithPriority>();
                    var existing = target.thingStyleCategories.FirstOrDefault(s => s.category == cd);

                    if (A == "add")
                    {
                        if (existing != null) return Fail("'" + cd.defName + "' is already on this ideo's style list (priority " + existing.priority + "). Remove it first to change priority.");
                        if (dryRun) return new { success = true, dryRun = true, action = A, ideo = new { target.id, target.name }, category = cd.defName, priority };
                        target.thingStyleCategories.Add(new ThingStyleCategoryWithPriority(cd, priority));
                        try { target.SortStyleCategories(); } catch { }
                    }
                    else
                    {
                        if (existing == null) return Fail("'" + cd.defName + "' is not on this ideo's style list.", new { styles = listStyles() });
                        if (dryRun) return new { success = true, dryRun = true, action = A, ideo = new { target.id, target.name }, category = cd.defName };
                        target.thingStyleCategories.Remove(existing);
                    }

                    return new { success = true, action = A, ideo = new { target.id, target.name }, styles = listStyles(), ticksGame = TicksGameSafe() };
                }

                // action == "icon"
                if (string.IsNullOrWhiteSpace(icon) || string.IsNullOrWhiteSpace(color))
                    return Fail("action='icon' needs BOTH 'icon' and 'color' - SetIcon overwrites both fields unconditionally.");

                var iconDef = DefDatabase<IdeoIconDef>.GetNamedSilentFail(icon.Trim());
                if (iconDef == null) return Fail("No IdeoIconDef '" + icon + "'.", DefSuggestions<IdeoIconDef>(icon));

                // SetIcon's second parameter is a ColorDef, not a raw Color - unlike
                // TryParseColor's usual callers, an 'r,g,b'/hex string cannot satisfy this
                // signature at all, so only a ColorDef defName is accepted here.
                var colorDef = DefDatabase<ColorDef>.GetNamedSilentFail(color.Trim());
                if (colorDef == null) return Fail("No ColorDef '" + color + "'.", DefSuggestions<ColorDef>(color));

                if (dryRun)
                    return new { success = true, dryRun = true, action = A, ideo = new { target.id, target.name }, icon = iconDef.defName, color = colorDef.defName, clearPrimaryFactionColor };

                try { target.SetIcon(iconDef, colorDef, clearPrimaryFactionColor); }
                catch (Exception e) { return Fail("SetIcon threw: " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = target.iconDef == iconDef && target.colorDef == colorDef,
                    action = A,
                    ideo = new { target.id, target.name },
                    iconDef = target.iconDef != null ? target.iconDef.defName : null,
                    colorDef = target.colorDef != null ? target.colorDef.defName : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Settlements, caravans & gravship
        // ================================================================

        [Tool(
            "jawa/world_tile_map_generate",
            Description =
                "GetOrGenerateMapUtility.GetOrGenerateMap(tile, size, suggestedMapParentDef) - make " +
                "the Map a world tile would produce, the same lazy path clicking into a Settlement " +
                "or Site takes, but callable directly. jawa/colony_found explicitly does NOT " +
                "generate a map; this is that missing other half. " +
                "🔑 IDEMPOTENT: if a Map already exists at this tile it is returned as-is, no error, " +
                "with wasAlreadyGenerated=true - and if no MapParent world object exists there yet, " +
                "one of type 'suggestedMapParentDef' is created and added first.",
            ResultDescription =
                "success, tile, mapParentDef, wasAlreadyGenerated, mapSize{x,z}, mapIndex " +
                "(Find.Maps position), pawnCount, thingCount.")]
        public static async Task<object> WorldTileMapGenerate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "World tile id.")] int tile = -1,
            [ToolParameter(Description = "WorldObjectDef defName to create at this tile if none exists yet. Default 'Settlement'.")]
            string suggestedMapParent = "Settlement",
            [ToolParameter(Description = "Map width. -1 uses Find.World.info.initialMapSize.")] int sizeX = -1,
            [ToolParameter(Description = "Map height. -1 uses Find.World.info.initialMapSize.")] int sizeZ = -1,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            if (tile < 0) return Fail("Give 'tile', a valid world tile id.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a world loaded.");
                if (tile >= grid.TilesCount) return Fail("Tile " + tile + " out of range (0.." + (grid.TilesCount - 1) + ").");

                var wod = DefDatabase<WorldObjectDef>.GetNamedSilentFail((suggestedMapParent ?? "Settlement").Trim());
                if (wod == null) return Fail("No WorldObjectDef '" + suggestedMapParent + "'.", DefSuggestions<WorldObjectDef>(suggestedMapParent));

                var pt = new PlanetTile(tile, grid.Surface);
                var existing = Current.Game != null ? Current.Game.FindMap(pt) : null;

                var size = (sizeX > 0 && sizeZ > 0) ? new IntVec3(sizeX, 1, sizeZ)
                    : (Find.World != null ? Find.World.info.initialMapSize : new IntVec3(250, 1, 250));

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        tile,
                        mapParentDef = wod.defName,
                        wasAlreadyGenerated = existing != null,
                        mapSize = new { x = size.x, z = size.z }
                    };

                Map map;
                try { map = GetOrGenerateMapUtility.GetOrGenerateMap(pt, size, wod); }
                catch (Exception e) { return Fail("GetOrGenerateMap threw: " + e.GetType().Name + ": " + e.Message); }
                if (map == null) return Fail("GetOrGenerateMap returned null - no MapParent exists at this tile and '" + wod.defName + "' could not be created there. Check the game log.");

                return new
                {
                    success = true,
                    tile,
                    mapParentDef = wod.defName,
                    wasAlreadyGenerated = existing != null,
                    mapSize = new { x = map.Size.x, z = map.Size.z },
                    mapIndex = map.Index,
                    pawnCount = map.mapPawns != null ? map.mapPawns.AllPawnsSpawned.Count : 0,
                    thingCount = map.listerThings != null ? map.listerThings.AllThings.Count : 0,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/settlement_remove",
            Description =
                "Remove a settlement OR drop a map, the two halves of SettlementAbandonUtility / " +
                "Game.DeinitAndRemoveMap. mode='settlement': MapParent.Abandon(wasGravshipLaunch: " +
                "false) on a live WorldObject id - the same call the vanilla 'Abandon Home' command " +
                "reaches AFTER its confirmation dialogs, which this tool skips entirely (no " +
                "Find.WindowStack involved). mode='map': Game.DeinitAndRemoveMap(map, notifyPlayer) " +
                "on a tile's live Map, leaving its MapParent WorldObject (Settlement, Site, ...) " +
                "in place - the map regenerates lazily on the next visit, same as any unvisited tile. " +
                "⚠️ mode='settlement' mirrors the vanilla UI's OWN disable condition " +
                "(AllColonistsThere - true when abandoning here would leave every free colonist with " +
                "nowhere else on the map layer) and refuses unless force=true.",
            ResultDescription =
                "success, mode, and for settlement: label, wasHomeMap, destroyed; for map: tile, " +
                "mapIndex, parentDef, stillHasMaps.")]
        public static async Task<object> SettlementRemove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "'settlement' or 'map'.")] string mode = "settlement",
            [ToolParameter(Description = "mode='settlement': live MapParent WorldObject id (Settlement, Site, ...).")] int settlementId = -1,
            [ToolParameter(Description = "mode='map': world tile id whose live Map should be dropped.")] int tile = -1,
            [ToolParameter(Description = "mode='map': Game.DeinitAndRemoveMap's own notifyPlayer flag.")] bool notifyPlayer = false,
            [ToolParameter(Description = "mode='settlement': bypass the AllColonistsThere guard.")] bool force = false,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            var M = (mode ?? "settlement").Trim().ToLowerInvariant();
            if (M != "settlement" && M != "map") return Fail("mode must be settlement|map.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                if (M == "settlement")
                {
                    if (settlementId < 0) return Fail("Give 'settlementId' for mode='settlement'.");
                    var mp = Find.WorldObjects != null
                        ? Find.WorldObjects.AllWorldObjects.OfType<MapParent>().FirstOrDefault(o => o.ID == settlementId)
                        : null;
                    if (mp == null) return Fail("No live MapParent WorldObject with id " + settlementId + ".");

                    bool allColonistsThere;
                    try { allColonistsThere = SettlementAbandonUtility.AllColonistsThere(mp); } catch { allColonistsThere = false; }
                    bool hasMap = mp.Map != null;

                    if (allColonistsThere && !force)
                        return Fail("AllColonistsThere is true for '" + mp.Label + "' - the vanilla UI DISABLES 'Abandon Home' here " +
                                    "because every free colonist on this map layer has nowhere else to be. Pass force=true to override.");

                    if (dryRun)
                        return new { success = true, dryRun = true, mode = M, label = mp.Label, wasHomeMap = hasMap && mp.Map.IsPlayerHome, allColonistsThere };

                    try { mp.Abandon(wasGravshipLaunch: false); }
                    catch (Exception e) { return Fail("Abandon threw: " + e.GetType().Name + ": " + e.Message); }
                    try { Find.GameEnder.CheckOrUpdateGameOver(); } catch { }

                    return new
                    {
                        success = mp.Destroyed,
                        mode = M,
                        label = mp.Label,
                        wasHomeMap = hasMap,
                        destroyed = mp.Destroyed,
                        ticksGame = TicksGameSafe()
                    };
                }
                else
                {
                    if (tile < 0) return Fail("Give 'tile' for mode='map'.");
                    var grid = Find.WorldGrid;
                    if (grid == null) return Fail("No WorldGrid.");
                    if (tile >= grid.TilesCount) return Fail("Tile " + tile + " out of range (0.." + (grid.TilesCount - 1) + ").");
                    var pt = new PlanetTile(tile, grid.Surface);
                    var map = Current.Game.FindMap(pt);
                    if (map == null) return Fail("No live Map at tile " + tile + ". Nothing to drop.");

                    var parentDef = map.Parent != null ? map.Parent.def.defName : null;
                    int mapIndex = map.Index;

                    if (dryRun)
                        return new { success = true, dryRun = true, mode = M, tile, mapIndex, parentDef, notifyPlayer };

                    try { Current.Game.DeinitAndRemoveMap(map, notifyPlayer); }
                    catch (Exception e) { return Fail("DeinitAndRemoveMap threw: " + e.GetType().Name + ": " + e.Message); }

                    return new
                    {
                        success = Current.Game.FindMap(pt) == null,
                        mode = M,
                        tile,
                        mapIndex,
                        parentDef,
                        note = parentDef != null ? "MapParent '" + parentDef + "' was left in place and will regenerate lazily on the next visit." : null,
                        stillHasMaps = Find.Maps != null && Find.Maps.Count > 0,
                        ticksGame = TicksGameSafe()
                    };
                }
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/caravan_form_exit",
            Description =
                "CaravanFormingUtility.FormAndCreateCaravan(pawns, faction, exitFromTile, " +
                "directionTile, destinationTile) - the REAL leave-the-map path (Pawn.ExitMap on " +
                "every pawn, GenWorldClosest to pick a passable exit tile, an arrival action at " +
                "destinationTile if one applies), distinct from jawa/caravan_create which builds a " +
                "Caravan world object directly via CaravanMaker.MakeCaravan with no exit animation " +
                "and no arrival action. Use this when the pawns are actually leaving a live map; use " +
                "jawa/caravan_create for a bare, already-off-map caravan. " +
                "⚠️ The API takes NO sendMessage parameter - CaravanExitMapUtility's default " +
                "(sendMessage=true) always applies, so the vanilla 'formed caravan' Message always " +
                "fires. " +
                "🔑 FormAndCreateCaravan returns void - this tool identifies the resulting Caravan " +
                "by finding which live Caravan now contains the resolved pawns, rather than trusting " +
                "the call succeeded.",
            ResultDescription =
                "success, pawnCount, refused[] (pawn tokens that did not resolve), caravanId, name, " +
                "tile, destTile, pathed.")]
        public static async Task<object> CaravanFormExit(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Comma-separated pawn ids/names/thingIds - must be spawned on a map to actually exit it.")]
            string pawns,
            [ToolParameter(Description = "FactionDef defName for the caravan. Empty uses the first resolved pawn's own faction.")]
            string faction = null,
            [ToolParameter(Description = "World tile to exit from. -1 uses the first spawned pawn's Map.Tile.")]
            int exitTile = -1,
            [ToolParameter(Description = "World tile giving the exit direction (GenWorldClosest picks the nearest PASSABLE tile toward it). -1 uses exitTile itself.")]
            int directionTile = -1,
            [ToolParameter(Description = "Destination tile. -1 forms the caravan in place with no arrival action.")]
            int destTile = -1,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(pawns)) return Fail("Give 'pawns' - comma-separated ids/names.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                var grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a world loaded.");

                var found = new List<Pawn>();
                var refused = new List<object>();
                foreach (var raw in pawns.Split(new[] { ',', ';', '\n' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    var tok = raw.Trim();
                    if (tok.Length == 0) continue;
                    string perr; var p = FindPawn(tok, out perr);
                    if (p == null) refused.Add(new { pawn = tok, reason = perr });
                    else found.Add(p);
                }
                if (found.Count == 0) return Fail("No pawn resolved. Nothing to caravan.", new { refused });

                Faction fac;
                if (!string.IsNullOrEmpty(faction))
                {
                    var fd = DefDatabase<FactionDef>.GetNamedSilentFail(faction.Trim());
                    if (fd == null) return Fail("No FactionDef '" + faction + "'.", DefSuggestions<FactionDef>(faction));
                    fac = Find.FactionManager != null ? Find.FactionManager.FirstFactionOfDef(fd) : null;
                    if (fac == null) return Fail("FactionDef '" + faction + "' exists but no such faction is in this world.");
                }
                else fac = found[0].Faction ?? Faction.OfPlayer;
                if (fac == null) return Fail("Could not resolve a faction for the caravan - give 'faction' explicitly.");

                var spawnedPawn = found.FirstOrDefault(p => p.Spawned && p.Map != null);
                int exitTileId = exitTile;
                if (exitTileId < 0)
                {
                    if (spawnedPawn == null) return Fail("No resolved pawn is spawned on a map, and no 'exitTile' was given. Give exitTile explicitly.");
                    exitTileId = spawnedPawn.Map.Tile;
                }
                if (exitTileId < 0 || exitTileId >= grid.TilesCount) return Fail("Resolved exitTile " + exitTileId + " is out of range.");
                var exitPt = new PlanetTile(exitTileId, grid.Surface);
                var dirPt = directionTile >= 0 && directionTile < grid.TilesCount ? new PlanetTile(directionTile, grid.Surface) : exitPt;
                var destPt = destTile >= 0 && destTile < grid.TilesCount ? new PlanetTile(destTile, grid.Surface) : PlanetTile.Invalid;

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        pawnCount = found.Count,
                        pawns = found.Select(p => p.LabelShort).ToList(),
                        faction = fac.def.defName,
                        exitTile = exitTileId,
                        directionTile = dirPt.tileId,
                        destTile = destPt.Valid ? (int?)destPt.tileId : null,
                        refused
                    };

                var existingCaravanIds = new HashSet<int>(
                    Find.WorldObjects != null ? Find.WorldObjects.AllWorldObjects.OfType<Caravan>().Select(c => c.ID) : Enumerable.Empty<int>());

                try { CaravanFormingUtility.FormAndCreateCaravan(found, fac, exitPt, dirPt, destPt); }
                catch (Exception e) { return Fail("FormAndCreateCaravan threw: " + e.GetType().Name + ": " + e.Message); }

                var resultCaravan = Find.WorldObjects != null
                    ? Find.WorldObjects.AllWorldObjects.OfType<Caravan>()
                        .FirstOrDefault(c => !existingCaravanIds.Contains(c.ID) && found.Any(p => c.ContainsPawn(p)))
                    : null;
                if (resultCaravan == null)
                    resultCaravan = Find.WorldObjects != null
                        ? Find.WorldObjects.AllWorldObjects.OfType<Caravan>().FirstOrDefault(c => found.Any(p => c.ContainsPawn(p)))
                        : null;

                if (resultCaravan == null)
                    return Fail("FormAndCreateCaravan ran but no live Caravan now contains any resolved pawn - it may have merged into an existing caravan at the exit tile, or every pawn failed to exit.", new { refused });

                return new
                {
                    success = true,
                    pawnCount = found.Count,
                    refused,
                    caravanId = resultCaravan.ID,
                    name = resultCaravan.Name,
                    tile = resultCaravan.Tile.tileId,
                    destTile = destPt.Valid ? (int?)destPt.tileId : null,
                    pathed = resultCaravan.pather != null && resultCaravan.pather.Moving,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Genes & xenotypes
        // ================================================================

        [Tool(
            "jawa/gene_reimplant",
            Description =
                "GeneUtility.ReimplantXenogerm(caster, recipient) - copy the CASTER's whole xenogerm " +
                "(xenotype, xenotypeName, icon, every xenogene) onto the RECIPIENT, clearing the " +
                "recipient's existing xenogenes first, then adding XenogerminationComa to the " +
                "recipient and running ExtractXenogerm on the caster (XenogermLossShock + a " +
                "replicating cooldown hediff). " +
                "🔴 ADDING GENES FIRES Notify_GenesChanged, WHICH RE-ROLLS THE RECIPIENT'S HEAD TYPE - " +
                "do any appearance edit on the recipient AFTER this call, never before. " +
                "🔴 ReimplantXenogerm does NOT itself guard the CASTER against dying from re-extraction " +
                "- that guard (auto-revert to Baseliner) lives INSIDE the ExtractXenogerm call this " +
                "makes on the caster. THIS TOOL PRE-CHECKS GeneUtility.PawnWouldDieFromReimplanting " +
                "ON THE CASTER and refuses unless force=true, rather than relying on that internal " +
                "mitigation silently changing the caster's xenotype out from under the caller. " +
                "Requires Biotech.",
            ResultDescription =
                "success, caster, recipient, casterWouldDieFromReimplanting, recipient xenotype " +
                "before/after, xenogeneCountBefore/After.")]
        public static async Task<object> GeneReimplant(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name - whose xenogerm is copied.")] string caster = null,
            [ToolParameter(Description = "Pawn id, thingId or name - who receives it.")] string recipient = null,
            [ToolParameter(Description = "Proceed even if PawnWouldDieFromReimplanting(caster) is true.")] bool force = false,
            [ToolParameter(Description = "Report what would happen and change nothing.")] bool dryRun = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.BiotechActive) return Fail("Biotech is not active. Xenogerms do not exist in this game.");

                string cerr; var c = FindPawn(caster, out cerr);
                if (c == null) return Fail(cerr ?? "No caster pawn.");
                string rerr; var r = FindPawn(recipient, out rerr);
                if (r == null) return Fail(rerr ?? "No recipient pawn.");
                if (c == r) return Fail("caster and recipient are the same pawn.");
                if (c.genes == null) return Fail(c.LabelShortCap + " has no Pawn_GeneTracker.");
                if (r.genes == null) return Fail(r.LabelShortCap + " has no Pawn_GeneTracker.");
                if (c.genes.Xenotype == null) return Fail(c.LabelShortCap + " has no xenotype set - nothing to copy.");

                bool wouldDie;
                try { wouldDie = GeneUtility.PawnWouldDieFromReimplanting(c); }
                catch (Exception e) { return Fail("PawnWouldDieFromReimplanting threw: " + e.GetType().Name + ": " + e.Message); }

                if (wouldDie && !force)
                    return Fail(c.LabelShortCap + " already carries XenogermReplicating - " +
                                "GeneUtility.PawnWouldDieFromReimplanting is true. ReimplantXenogerm's internal " +
                                "ExtractXenogerm step would auto-revert " + c.LabelShortCap + " to Baseliner rather " +
                                "than block, which is a bigger side effect than most callers expect. Pass " +
                                "force=true to proceed anyway.");

                var recipXenoBefore = r.genes.Xenotype != null ? r.genes.Xenotype.defName : null;
                var recipXenoNameBefore = r.genes.xenotypeName;
                int xenoCountBefore = r.genes.Xenogenes.Count;

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        caster = c.LabelShortCap.ToString(),
                        recipient = r.LabelShortCap.ToString(),
                        casterWouldDieFromReimplanting = wouldDie,
                        recipientXenotypeBefore = recipXenoBefore,
                        casterXenogenesToCopy = c.genes.Xenogenes.Count
                    };

                try { GeneUtility.ReimplantXenogerm(c, r); }
                catch (Exception e) { return Fail("ReimplantXenogerm threw: " + e.GetType().Name + ": " + e.Message); }

                return new
                {
                    success = true,
                    caster = c.LabelShortCap.ToString(),
                    recipient = r.LabelShortCap.ToString(),
                    casterWouldDieFromReimplanting = wouldDie,
                    recipientXenotypeBefore = recipXenoBefore,
                    recipientXenotypeAfter = r.genes.Xenotype != null ? r.genes.Xenotype.defName : null,
                    recipientXenotypeNameBefore = recipXenoNameBefore,
                    recipientXenotypeNameAfter = r.genes.xenotypeName,
                    xenogeneCountBefore = xenoCountBefore,
                    xenogeneCountAfter = r.genes.Xenogenes.Count,
                    note = "Notify_GenesChanged already re-rolled the recipient's head type - do any appearance edit now, not before.",
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/gene_random_set",
            Description =
                "GeneUtility.GenerateGeneSet(seed) - a seeded (or uncontrolled) valid combination of " +
                "genes respecting biostat range, prerequisites and conflicts, plus its own generated " +
                "name, for fuzzing. Standalone if 'pawn' is empty; with 'pawn' given, the set is " +
                "APPLIED as that pawn's xenogenes (existing xenogenes cleared first via " +
                "ClearXenogenes, endogenes untouched) and xenotypeName is set to the set's label. " +
                "🔴 ADDING GENES FIRES Notify_GenesChanged, WHICH RE-ROLLS THE HEAD TYPE - order is " +
                "genes first, any appearance edit on 'pawn' second. Requires Biotech.",
            ResultDescription =
                "success, seed (as given, or null if uncontrolled), label, geneCount, genes[], " +
                "complexityTotal, metabolismTotal, architesTotal, and (with 'pawn') appliedToPawn, " +
                "xenogeneCountAfter.")]
        public static async Task<object> GeneRandomSet(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Seed for reproducible generation. -1 = uncontrolled (GenerateGeneSet(null)).")]
            int seed = -1,
            [ToolParameter(Description = "Pawn id, thingId or name to apply the generated set to as xenogenes. Empty just returns the set.")]
            string pawn = null,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.BiotechActive) return Fail("Biotech is not active. There is no gene pool to draw from.");

                Pawn p = null;
                if (!string.IsNullOrWhiteSpace(pawn))
                {
                    string perr; p = FindPawn(pawn, out perr);
                    if (p == null) return Fail(perr ?? "No pawn.");
                    if (p.genes == null) return Fail(p.LabelShortCap + " has no Pawn_GeneTracker.");
                }

                int? s = seed >= 0 ? seed : (int?)null;
                GeneSet set;
                try { set = GeneUtility.GenerateGeneSet(s); }
                catch (Exception e) { return Fail("GenerateGeneSet threw: " + e.GetType().Name + ": " + e.Message); }
                if (set == null) return Fail("GenerateGeneSet returned null (ModLister.CheckBiotech refused despite ModsConfig.BiotechActive being true).");
                if (set.Empty) return Fail("GenerateGeneSet produced an empty set on this roll. Try a different seed.");

                var geneNames = set.GenesListForReading.Select(g => g.defName).ToList();

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        seed = s,
                        label = set.Label,
                        geneCount = geneNames.Count,
                        genes = geneNames,
                        complexityTotal = set.ComplexityTotal,
                        metabolismTotal = set.MetabolismTotal,
                        architesTotal = set.ArchitesTotal,
                        wouldApplyToPawn = p != null ? p.LabelShortCap.ToString() : null
                    };

                string appliedToPawn = null;
                int? xenoCountAfter = null;
                if (p != null)
                {
                    try
                    {
                        p.genes.ClearXenogenes();
                        foreach (var g in set.GenesListForReading) p.genes.AddGene(g, true);
                        p.genes.xenotypeName = set.Label;
                    }
                    catch (Exception e) { return Fail("Applying the gene set threw: " + e.GetType().Name + ": " + e.Message); }
                    appliedToPawn = p.LabelShortCap.ToString();
                    xenoCountAfter = p.genes.Xenogenes.Count;
                }

                return new
                {
                    success = true,
                    seed = s,
                    label = set.Label,
                    geneCount = geneNames.Count,
                    genes = geneNames,
                    complexityTotal = set.ComplexityTotal,
                    metabolismTotal = set.MetabolismTotal,
                    architesTotal = set.ArchitesTotal,
                    appliedToPawn,
                    xenogeneCountAfter = xenoCountAfter,
                    note = appliedToPawn != null ? "Notify_GenesChanged already re-rolled the pawn's head type - do any appearance edit now, not before." : null,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  Pawn state & health
        // ================================================================
        //
        // install-bionic (Recipe_InstallArtificialBodyPart.ApplyOnPawn) is SKIPPED here:
        // jawa/pawn_health (action='bionic') in JawaBenchPawnTools.cs already does exactly
        // the "cheap route" the roster names - RestorePart(part) then AddHediff(def, part),
        // no RecipeDef, no surgeon, no billDoer. Nothing new was needed for that row.

        [Tool(
            "jawa/pawn_severity_adjust",
            Description =
                "HealthUtility.AdjustSeverity(pawn, hediffDef, offset) - push an EXISTING hediff's " +
                "severity up or down by an OFFSET (not an absolute value), or create one if the " +
                "offset is positive and the pawn does not have it yet. " +
                "🔴 AdjustSeverity IS A SILENT NO-OP IN TWO SHAPES, BOTH REFUSED HERE INSTEAD OF " +
                "REPORTED AS SUCCESS: offset == 0 always does nothing; a NEGATIVE offset on a hediff " +
                "the pawn does not have does nothing (only a positive offset creates one). " +
                "🔴 AdjustSeverity NEVER CALLS Pawn_HealthTracker.CheckForStateChange ITSELF - a " +
                "severity push into death or downed range is NOT re-evaluated unless something calls " +
                "it. THIS TOOL CALLS CheckForStateChange(null, hediff) IMMEDIATELY AFTER, every time.",
            ResultDescription =
                "success, pawn, hediff, existedBefore, severityBefore, severityAfter, wasCreated, " +
                "stateChangeChecked, pawnDeadAfter, pawnDownedAfter.")]
        public static async Task<object> PawnSeverityAdjust(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "HediffDef defName.")] string hediff = null,
            [ToolParameter(Description = "Severity OFFSET to apply (can be negative). 0 is refused - it is a documented no-op.")]
            float offset = 0f,
            [ToolParameter(Description = "Report what would happen and change nothing.")]
            bool dryRun = false)
        {
            if (string.IsNullOrWhiteSpace(hediff)) return Fail("hediff is required.");
            if (offset == 0f) return Fail("offset is 0 - HealthUtility.AdjustSeverity does nothing on a zero offset. Give a nonzero value.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr; var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.health == null) return Fail(p.LabelShortCap + " has no health tracker.");

                var hd = DefDatabase<HediffDef>.GetNamedSilentFail((hediff ?? "").Trim());
                if (hd == null) return Fail("No HediffDef '" + hediff + "'.", DefSuggestions<HediffDef>(hediff));

                var before = p.health.hediffSet.GetFirstHediffOfDef(hd);
                bool existedBefore = before != null;
                float? severityBefore = before != null ? (float?)before.Severity : null;

                if (!existedBefore && offset < 0f)
                    return Fail(p.LabelShortCap + " has no '" + hd.defName + "' hediff, and AdjustSeverity does NOT " +
                                "create one on a negative offset - only a positive offset creates a new hediff. " +
                                "Nothing would happen.");

                if (dryRun)
                    return new
                    {
                        success = true,
                        dryRun = true,
                        pawn = p.LabelShortCap.ToString(),
                        hediff = hd.defName,
                        existedBefore,
                        severityBefore,
                        willCreate = !existedBefore
                    };

                try { HealthUtility.AdjustSeverity(p, hd, offset); }
                catch (Exception e) { return Fail("AdjustSeverity threw: " + e.GetType().Name + ": " + e.Message); }

                var after = p.health.hediffSet.GetFirstHediffOfDef(hd);
                if (after == null)
                    return Fail("AdjustSeverity ran but " + p.LabelShortCap + " has no '" + hd.defName + "' hediff afterward - unexpected given the guards above.");

                bool stateChecked = true; string stateCheckError = null;
                try { p.health.CheckForStateChange(null, after); }
                catch (Exception e) { stateChecked = false; stateCheckError = e.GetType().Name + ": " + e.Message; }

                return new
                {
                    success = true,
                    pawn = p.LabelShortCap.ToString(),
                    hediff = hd.defName,
                    existedBefore,
                    severityBefore,
                    severityAfter = after.Severity,
                    wasCreated = !existedBefore,
                    stateChangeChecked = stateChecked,
                    stateCheckError,
                    pawnDeadAfter = p.Dead,
                    pawnDownedAfter = p.Downed,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
