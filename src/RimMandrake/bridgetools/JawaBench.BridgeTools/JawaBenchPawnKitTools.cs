// JawaBenchPawnKitTools.cs - Group E: skills/relations, abilities/inspiration/psychic,
// genes/xenotypes, apparel locking and inventory/stack manipulation on a live pawn.
//
// Every signature here was read from the 1.6 source via rimsage before being called -
// several of the "obvious" ones are silent no-ops the doc sketch did not flag:
//
//   * Pawn_SkillTracker.Learn -> SkillRecord.Learn returns with NOTHING changed when
//     the skill is TotallyDisabled, or when a Mutant's PawnKindDef forbids XP gain.
//     Both are checked and named BEFORE calling Learn, not inferred from a flat xp read.
//   * GeneUtility.OffsetHemogen / SatisfyChemicalGenes both silently do nothing when
//     ModsConfig.BiotechActive is false OR the pawn has no matching gene - there is no
//     exception and no return value to catch it. Both are gated here explicitly.
//   * Pawn_InventoryTracker.TryAddAndUnforbid returns void and swallows the bool from
//     ThingOwner.TryAdd. This file works on the COUNT actually moved, and reports it.
//   * ThingOwner.TryAddOrTransfer CANNOT take a thing off the map: a spawned thing's
//     holdingOwner is map.spawnedThings, so it routes into TryTransferToContainer, whose
//     `owner is Map` guard returns 0 unconditionally. Measured live 2026-09-02 - it had
//     read as "the container refused it" for a day. Map things are DeSpawn'd then TryAdd'd.
//   * Pawn_InventoryTracker.RemoveCount touches at most ONE matching stack and returns
//     void - if the def is spread over several stacks a single call can silently remove
//     less than asked. This file measures Count(def) before/after and loops until the
//     requested count is actually gone, rather than trusting one call.
//
// THREAD AFFINITY: everything that touches game state is inside ctx.MainThread.InvokeAsync
// and nothing else is - same rule as every other file here.

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
        // Shared by jawa/inventory_transfer (add mode) and jawa/split_stack: a live
        // Thing is not just "on some map" - it can be sitting in another pawn's
        // equipment, apparel or inventory, and callers address it by the same id
        // jawa/list_things or jawa/pawn_gear reported.
        private static Thing FindLiveThingById(string id, out string err)
        {
            err = null;
            if (string.IsNullOrWhiteSpace(id)) { err = "Give a thing id."; return null; }
            var tok = id.Trim();
            var bare = tok.StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && tok.Length > 6
                ? tok.Substring(6) : tok;

            foreach (var m in Find.Maps ?? new List<Map>())
            {
                foreach (var t in m.listerThings.AllThings)
                    if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                foreach (var p in m.mapPawns.AllPawnsSpawned)
                {
                    if (p.equipment != null)
                        foreach (var t in p.equipment.AllEquipmentListForReading)
                            if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                    if (p.apparel != null)
                        foreach (var t in p.apparel.WornApparel)
                            if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                    if (p.inventory != null && p.inventory.innerContainer != null)
                        foreach (var t in p.inventory.innerContainer)
                            if (string.Equals(t.ThingID, bare, StringComparison.OrdinalIgnoreCase)) return t;
                }
            }
            err = "No live thing with id '" + bare + "' on any loaded map, or in any pawn's equipment, apparel or inventory.";
            return null;
        }

        // ================================================================
        //  jawa/grant_xp
        // ================================================================
        [Tool(
            "jawa/grant_xp",
            Description =
                "Grant (or dock) skill XP on a live pawn via Pawn_SkillTracker.Learn, the real " +
                "learn-rate path (passion multiplies it) unless ignoreLearnRate bypasses it. " +
                "⚠ Learn is a SILENT NO-OP in two cases neither throws nor returns a signal for: the " +
                "skill is TotallyDisabled for this pawn (a trait or the pawnKind forbids it), or the " +
                "pawn is an Anomaly mutant whose kind forbids XP gain entirely. Both are checked and " +
                "named BEFORE calling Learn, so a refusal always says WHY rather than reporting a " +
                "success that changed nothing.",
            ResultDescription =
                "success, pawn, skill, levelBefore/levelAfter (GetLevel(false), i.e. WITHOUT " +
                "aptitude - Level's getter adds it and would misreport what was actually written), " +
                "xpSinceLastLevelBefore/After, passion, xpRequiredForLevelUp.")]
        public static async Task<object> GrantXp(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "SkillDef defName, e.g. 'Shooting', 'Melee', 'Crafting'.")] string skill = null,
            [ToolParameter(Description = "XP to add. Negative docks XP (floored at 0 XP into level 0).")] float xp = 0f,
            [ToolParameter(Description = "Bypass the daily xpSinceMidnight tracking used for the 'learning saturated' check.")] bool direct = false,
            [ToolParameter(Description = "Skip the passion/learn-rate multiplier - xp is applied exactly as given.")] bool ignoreLearnRate = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.skills == null) return Fail(p.LabelShortCap + " has no Pawn_SkillTracker (not a skill-bearing pawn kind).");

                var sDef = DefDatabase<SkillDef>.GetNamedSilentFail(skill);
                if (sDef == null) return Fail("No SkillDef named '" + skill + "'.", new { suggestions = DefSuggestions<SkillDef>(skill) });

                var rec = p.skills.GetSkill(sDef);
                if (rec.TotallyDisabled)
                    return Fail(p.LabelShortCap + "'s " + sDef.defName + " is TotallyDisabled for this pawn. " +
                                "Pawn_SkillTracker.Learn no-ops silently on a disabled skill - nothing would have changed.");
                if (ModsConfig.AnomalyActive && p.IsMutant && p.mutant != null && p.mutant.Def != null && !p.mutant.Def.canGainXP)
                    return Fail(p.LabelShortCap + " is a mutant (" + p.mutant.Def.defName + ") whose kind forbids XP gain entirely.");

                int levelBefore = rec.GetLevel(false);
                float xpBefore = rec.xpSinceLastLevel;

                p.skills.Learn(sDef, xp, direct, ignoreLearnRate);

                int levelAfter = rec.GetLevel(false);
                float xpAfter = rec.xpSinceLastLevel;

                return new
                {
                    success = true,
                    message = string.Format("{0} {1}: level {2}->{3}, xpSinceLastLevel {4:0.##}->{5:0.##}.",
                        p.LabelShortCap, sDef.defName, levelBefore, levelAfter, xpBefore, xpAfter),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    skill = sDef.defName,
                    levelBefore,
                    levelAfter,
                    xpSinceLastLevelBefore = xpBefore,
                    xpSinceLastLevelAfter = xpAfter,
                    passion = rec.passion.ToString(),
                    xpRequiredForLevelUp = rec.XpRequiredForLevelUp,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/read_opinion
        // ================================================================
        [Tool(
            "jawa/read_opinion",
            Description =
                "Read the social relationship between two live pawns via Pawn_RelationsTracker: " +
                "OpinionOf (int, both directions - opinion is NOT symmetric), OpinionExplanation " +
                "(the game's own line-by-line breakdown of what built that number) and " +
                "CompatibilityWith (float, romance/marriage compatibility, read from 'pawn' only - " +
                "the underlying calculation is not guaranteed symmetric either).",
            ResultDescription =
                "success, pawn, other, opinionOfOther, opinionOfOtherExplanation, opinionOfPawn " +
                "(other's opinion of pawn), opinionOfPawnExplanation, compatibilityOfPawnWithOther.")]
        public static async Task<object> ReadOpinion(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "The subject pawn.")] string pawn = null,
            [ToolParameter(Description = "The other pawn.")] string other = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr, oerr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                var o = FindPawn(other, out oerr);
                if (o == null) return Fail(oerr ?? "No 'other' pawn.");
                if (p == o) return Fail("'pawn' and 'other' are the same pawn.");
                if (p.relations == null) return Fail(p.LabelShortCap + " has no Pawn_RelationsTracker.");
                if (o.relations == null) return Fail(o.LabelShortCap + " has no Pawn_RelationsTracker.");

                int opinionOfOther = p.relations.OpinionOf(o);
                string explOfOther = p.relations.OpinionExplanation(o);
                int opinionOfPawn = o.relations.OpinionOf(p);
                string explOfPawn = o.relations.OpinionExplanation(p);
                float compat = p.relations.CompatibilityWith(o);

                return new
                {
                    success = true,
                    message = string.Format("{0}->{1}: {2}. {1}->{0}: {3}. Compatibility (of {0} with {1}): {4:0.##}.",
                        p.LabelShortCap, o.LabelShortCap, opinionOfOther, opinionOfPawn, compat),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    other = new { id = o.ThingID, name = o.LabelShortCap.ToString() },
                    opinionOfOther,
                    opinionOfOtherExplanation = explOfOther,
                    opinionOfPawn,
                    opinionOfPawnExplanation = explOfPawn,
                    compatibilityOfPawnWithOther = compat,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/grant_ability
        // ================================================================
        [Tool(
            "jawa/grant_ability",
            Description =
                "⚠ OVERLAPS jawa/pawn_psychic action='grant', which calls the same GainAbility but " +
                "is scoped to PSYCASTS and also handles psylink levels and psyfocus. Use that one for " +
                "anything psycast-shaped; use this one for any other AbilityDef. Neither is a superset. " +
                "Give a pawn an AbilityDef via Pawn_AbilityTracker.GainAbility - a permanent grant " +
                "stored in abilities.abilities, distinct from abilities granted temporarily by " +
                "hediffs, equipment, apparel, mutant status or an ideo role (those all show up in " +
                "AllAbilitiesForReading but are NOT this list and are not removed by jawa/revoke - " +
                "there is no revoke tool yet). GainAbility is idempotent - granting one already held " +
                "is reported as a no-op, not an error. " +
                "⚠ self-notifies: it calls Notify_TemporaryAbilitiesChanged(), which dirties the " +
                "ability-gizmo cache. No letter or dialog fires.",
            ResultDescription = "success, pawn, ability, alreadyHad, abilityCountAfter.")]
        public static async Task<object> GrantAbility(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "AbilityDef defName, e.g. 'PsychicScream', 'Speech'.")] string ability = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.abilities == null) return Fail(p.LabelShortCap + " has no Pawn_AbilityTracker.");

                var def = DefDatabase<AbilityDef>.GetNamedSilentFail(ability);
                if (def == null) return Fail("No AbilityDef named '" + ability + "'.", new { suggestions = DefSuggestions<AbilityDef>(ability) });

                bool alreadyHad = p.abilities.GetAbility(def, false) != null;
                p.abilities.GainAbility(def);
                int countAfter = p.abilities.abilities.Count;

                return new
                {
                    success = true,
                    message = alreadyHad
                        ? p.LabelShortCap + " already had " + def.defName + "; no-op."
                        : p.LabelShortCap + " gained " + def.defName + ".",
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    ability = def.defName,
                    alreadyHad,
                    abilityCountAfter = countAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/start_inspiration
        // ================================================================
        [Tool(
            "jawa/start_inspiration",
            Description =
                "Force an InspirationDef via InspirationHandler.TryStartInspiration. " +
                "⚠ The engine bool return does not say WHY it failed, so this checks the same three " +
                "gates the engine does and NAMES the blocking one before calling: already inspired " +
                "(pass force=true to end the current one first), a hediff whose CurStage.blocksInspirations " +
                "is set, or InspirationDef.Worker.InspirationCanOccur(pawn) returning false (e.g. a " +
                "mood-gated inspiration on a pawn whose mood does not qualify).",
            ResultDescription = "success, pawn, inspiration, endedPrevious, reason, sendLetter.")]
        public static async Task<object> StartInspiration(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "InspirationDef defName.")] string inspiration = null,
            [ToolParameter(Description = "Reason string shown in the letter/tooltip. Empty uses the def's default.")] string reason = null,
            [ToolParameter(Description = "Send the normal inspiration-started letter.")] bool sendLetter = true,
            [ToolParameter(Description = "If the pawn is already inspired, end that inspiration first instead of refusing.")] bool force = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.mindState == null || p.mindState.inspirationHandler == null)
                    return Fail(p.LabelShortCap + " has no InspirationHandler.");

                var def = DefDatabase<InspirationDef>.GetNamedSilentFail(inspiration);
                if (def == null) return Fail("No InspirationDef named '" + inspiration + "'.", new { suggestions = DefSuggestions<InspirationDef>(inspiration) });

                var handler = p.mindState.inspirationHandler;
                bool endedPrevious = false;
                if (handler.Inspired)
                {
                    if (!force)
                        return Fail(p.LabelShortCap + " is already inspired (" + handler.CurStateDef.defName + "). Pass force=true to end it first.");
                    handler.EndInspiration(handler.CurState);
                    endedPrevious = true;
                }

                if (p.health != null && p.health.hediffSet != null)
                {
                    foreach (var h in p.health.hediffSet.hediffs)
                        if (h.CurStage != null && h.CurStage.blocksInspirations)
                            return Fail(p.LabelShortCap + "'s hediff " + h.def.defName + " blocks all inspirations.");
                }
                if (def.Worker != null && !def.Worker.InspirationCanOccur(p))
                    return Fail(def.defName + ".Worker.InspirationCanOccur returned false for " + p.LabelShortCap + " - this inspiration's own conditions are not met.");

                bool started = handler.TryStartInspiration(def, string.IsNullOrEmpty(reason) ? null : reason, sendLetter);
                if (!started)
                    return Fail("TryStartInspiration returned false for an unnamed reason despite passing every check this tool can reproduce.");

                return new
                {
                    success = true,
                    message = p.LabelShortCap + " is now inspired: " + def.defName + (endedPrevious ? " (previous inspiration ended first)." : "."),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    inspiration = def.defName,
                    endedPrevious,
                    reason,
                    sendLetter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/read_psychic_sensitivity
        // ================================================================
        [Tool(
            "jawa/read_psychic_sensitivity",
            Description =
                "Read Pawn_PsychicEntropyTracker.PsychicSensitivity, the multiplier that scales " +
                "every psychic effect (entropy gain from casting, incoming psychic damage, etc) on " +
                "this pawn. Read-only - there is no direct setter; it derives from the " +
                "PsychicSensitivity StatDef, so change it via genes, traits or apparel, not this tool. " +
                "Reported alongside the tracker's other live numbers for context.",
            ResultDescription =
                "success, pawn, psychicSensitivity, isPsychicallySensitive, entropyValue, " +
                "maxEntropy, currentPsyfocus.")]
        public static async Task<object> ReadPsychicSensitivity(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.psychicEntropy == null) return Fail(p.LabelShortCap + " has no Pawn_PsychicEntropyTracker.");

                var t = p.psychicEntropy;
                return new
                {
                    success = true,
                    message = string.Format("{0}: PsychicSensitivity {1:0.###}.", p.LabelShortCap, t.PsychicSensitivity),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    psychicSensitivity = t.PsychicSensitivity,
                    isPsychicallySensitive = t.IsPsychicallySensitive,
                    entropyValue = t.EntropyValue,
                    maxEntropy = t.MaxEntropy,
                    currentPsyfocus = t.CurrentPsyfocus,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/clear_xenogenes
        // ================================================================
        [Tool(
            "jawa/clear_xenogenes",
            Description =
                "Wipe a pawn's xenogenes via Pawn_GeneTracker.ClearXenogenes(), leaving endogenes " +
                "(the pawn's own heritable genes) untouched. Needs Biotech - pawn.genes is only " +
                "populated when the DLC generated it, and is refused rather than treated as 0 genes.",
            ResultDescription =
                "success, pawn, xenogeneCountBefore, xenogeneCountAfter, endogeneCountUnchanged.")]
        public static async Task<object> ClearXenogenes(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.genes == null)
                    return Fail(p.LabelShortCap + " has no Pawn_GeneTracker (Biotech was not active when this pawn was generated).");

                int xenoBefore = p.genes.Xenogenes.Count;
                int endoBefore = p.genes.Endogenes.Count;

                p.genes.ClearXenogenes();

                int xenoAfter = p.genes.Xenogenes.Count;
                int endoAfter = p.genes.Endogenes.Count;

                return new
                {
                    success = true,
                    message = string.Format("{0}: xenogenes {1}->{2}, endogenes unchanged at {3}.",
                        p.LabelShortCap, xenoBefore, xenoAfter, endoAfter),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    xenogeneCountBefore = xenoBefore,
                    xenogeneCountAfter = xenoAfter,
                    endogeneCountUnchanged = endoBefore == endoAfter,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/gene_resource_poke
        // ================================================================
        [Tool(
            "jawa/gene_resource_poke",
            Description =
                "Two Biotech gene-resource pokes that GeneUtility silently no-ops instead of erroring: " +
                "mode='hemogen' calls OffsetHemogen(pawn, offset, applyStatFactor), which does nothing " +
                "if the pawn has no Gene_Hemogen gene; mode='chemical' calls SatisfyChemicalGenes(pawn), " +
                "which resets every Gene_ChemicalDependency hediff to its initial (satisfied) severity " +
                "and does nothing if the pawn has none. ⚠ Both require ModsConfig.BiotechActive and are " +
                "REFUSED, not silently skipped, when the DLC is off or the pawn has no matching gene.",
            ResultDescription =
                "success, pawn, mode, and for hemogen: valueBefore/After, max (0..max); for chemical: " +
                "genesReset[] (defName, chemical).")]
        public static async Task<object> GeneResourcePoke(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "'hemogen' or 'chemical'.")] string mode = null,
            [ToolParameter(Description = "hemogen only: amount to add (negative to drain).")] float offset = 0f,
            [ToolParameter(Description = "hemogen only: apply the HemogenGainFactor stat to a positive offset, same as the vanilla eating path.")] bool applyStatFactor = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");
                if (!ModsConfig.BiotechActive) return Fail("Biotech is not active. Both hemogen and chemical genes are Biotech-only.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.genes == null) return Fail(p.LabelShortCap + " has no Pawn_GeneTracker.");

                var m = (mode ?? "").Trim().ToLowerInvariant();
                if (m == "hemogen")
                {
                    var gene = p.genes.GetFirstGeneOfType<Gene_Hemogen>();
                    if (gene == null)
                        return Fail(p.LabelShortCap + " has no Gene_Hemogen gene. GeneUtility.OffsetHemogen would silently do nothing.");

                    float before = gene.Value;
                    GeneUtility.OffsetHemogen(p, offset, applyStatFactor);
                    float after = gene.Value;

                    return new
                    {
                        success = true,
                        message = string.Format("{0}: hemogen {1:0.###}->{2:0.###} (max {3:0.###}).", p.LabelShortCap, before, after, gene.Max),
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        mode = m,
                        valueBefore = before,
                        valueAfter = after,
                        max = gene.Max,
                        ticksGame = TicksGameSafe()
                    };
                }
                if (m == "chemical")
                {
                    var deps = p.genes.GenesListForReading.OfType<Gene_ChemicalDependency>().ToList();
                    if (deps.Count == 0)
                        return Fail(p.LabelShortCap + " has no Gene_ChemicalDependency gene. GeneUtility.SatisfyChemicalGenes would silently do nothing.");

                    GeneUtility.SatisfyChemicalGenes(p);

                    var reset = deps.Select(g => (object)new
                    {
                        defName = g.def.defName,
                        chemical = g.def.chemical != null ? g.def.chemical.defName : null
                    }).ToList();

                    return new
                    {
                        success = true,
                        message = string.Format("{0}: {1} chemical-dependency gene(s) reset.", p.LabelShortCap, reset.Count),
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        mode = m,
                        genesReset = reset,
                        ticksGame = TicksGameSafe()
                    };
                }
                return Fail("mode must be 'hemogen' or 'chemical', got '" + mode + "'.");
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/lock_apparel
        // ================================================================
        [Tool(
            "jawa/lock_apparel",
            Description =
                "Lock or unlock worn apparel via Pawn_ApparelTracker.Lock/Unlock/LockAll/UnlockAll - " +
                "the same mechanism ideo roles and royal titles use to stop a pawn auto-swapping a " +
                "required outfit. Locked apparel is not removed by outfit policies or auto-strip jobs; " +
                "the pawn can still be forced out of it directly. Address one item with 'apparel' " +
                "(thingId, defName, or a case-insensitive label/defName substring - refused as " +
                "ambiguous if more than one worn item matches), or pass all=true for every worn item.",
            ResultDescription =
                "success, pawn, all, locked, and either one item {id, defName, label, isLockedNow} " +
                "or items[] (all worn apparel with isLockedNow) when all=true.")]
        public static async Task<object> LockApparel(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name.")] string pawn = null,
            [ToolParameter(Description = "Worn apparel: thingId, defName, or a label/defName substring. Required unless all=true.")] string apparel = null,
            [ToolParameter(Description = "true to lock, false to unlock.")] bool locked = true,
            [ToolParameter(Description = "Apply to every worn item via LockAll()/UnlockAll() instead of one named item.")] bool all = false)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.apparel == null) return Fail(p.LabelShortCap + " has no Pawn_ApparelTracker.");

                if (all)
                {
                    if (locked) p.apparel.LockAll(); else p.apparel.UnlockAll();
                    var items = p.apparel.WornApparel.Select(a => (object)new
                    {
                        id = a.ThingID,
                        defName = a.def.defName,
                        label = a.LabelCap.ToString(),
                        isLockedNow = p.apparel.IsLocked(a)
                    }).ToList();
                    return new
                    {
                        success = true,
                        message = string.Format("{0}: {1} worn item(s) {2}.", p.LabelShortCap, items.Count, locked ? "locked" : "unlocked"),
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        all = true,
                        locked,
                        items,
                        ticksGame = TicksGameSafe()
                    };
                }

                if (string.IsNullOrWhiteSpace(apparel)) return Fail("Give 'apparel', or pass all=true.");
                var worn = p.apparel.WornApparel;
                var bare = apparel.Trim().StartsWith("Thing_", StringComparison.OrdinalIgnoreCase) && apparel.Trim().Length > 6
                    ? apparel.Trim().Substring(6) : apparel.Trim();

                var byId = worn.FirstOrDefault(a => string.Equals(a.ThingID, bare, StringComparison.OrdinalIgnoreCase));
                var matches = byId != null
                    ? new List<Apparel> { byId }
                    : worn.Where(a => a.def.defName.IndexOf(bare, StringComparison.OrdinalIgnoreCase) >= 0
                                      || a.LabelCap.ToString().IndexOf(bare, StringComparison.OrdinalIgnoreCase) >= 0).ToList();

                if (matches.Count == 0)
                    return Fail(p.LabelShortCap + " wears nothing matching '" + apparel + "'.",
                        new { worn = worn.Select(a => a.def.defName).ToList() });
                if (matches.Count > 1)
                    return Fail("'" + apparel + "' matches " + matches.Count + " worn items on " + p.LabelShortCap + ". Be more specific or use the thingId.",
                        new { matches = matches.Select(a => new { id = a.ThingID, defName = a.def.defName }).ToList() });

                var item = matches[0];
                if (locked) p.apparel.Lock(item); else p.apparel.Unlock(item);
                bool isLockedNow = p.apparel.IsLocked(item);

                return new
                {
                    success = true,
                    message = string.Format("{0}: {1} is now {2}.", p.LabelShortCap, item.LabelCap, isLockedNow ? "locked" : "unlocked"),
                    pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                    all = false,
                    locked,
                    id = item.ThingID,
                    defName = item.def.defName,
                    label = item.LabelCap.ToString(),
                    isLockedNow,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/inventory_transfer
        // ================================================================
        [Tool(
            "jawa/inventory_transfer",
            Description =
                "Move a live thing INTO a pawn's inventory pack (mode='add'), or take a ThingDef " +
                "OUT of it (mode='remove'). " +
                "🔑 mode='add' works on the COUNT actually moved, not a bool - a partial or zero move is " +
                "visible rather than hidden behind success:true, which is why it avoids " +
                "Pawn_InventoryTracker.TryAddAndUnforbid (returns void, swallows the result). " +
                "🔴 A thing lying on the MAP is despawned first and then TryAdd'd: a spawned thing's " +
                "holdingOwner is map.spawnedThings, so TryAddOrTransfer alone hits vanilla's " +
                "'Can't transfer items to or from Maps directly' guard and moves 0, every time. " +
                "A thing already in a pawn's slots goes through TryAddOrTransfer unchanged. " +
                "⚠ mode='remove' calls Pawn_InventoryTracker.RemoveCount, which touches at most ONE " +
                "matching stack per call - if the def is split across several stacks a single call can " +
                "silently remove less than asked. This tool measures Count(def) before and after and " +
                "loops until the requested count is actually gone, or refuses naming the shortfall. " +
                "The thing being added is addressed the same way jawa/thing_stats does: an id from any " +
                "loaded map, or from any pawn's equipment, apparel or inventory (including the SAME " +
                "pawn - moving an equipped weapon into its own pack is a valid use).",
            ResultDescription =
                "success, pawn, mode, and for add: requestedCount, movedCount, thing{id, defName}; for " +
                "remove: thingDef, requestedCount, removedCount, remainingInInventory.")]
        public static async Task<object> InventoryTransfer(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id, thingId or name - whose inventory is being changed.")] string pawn = null,
            [ToolParameter(Description = "'add' or 'remove'.")] string mode = null,
            [ToolParameter(Description = "add mode: id of an existing thing to move in (from a map, or any pawn's equipment/apparel/inventory).")] string thing = null,
            [ToolParameter(Description = "remove mode: ThingDef defName to take out of the inventory.")] string thingDef = null,
            [ToolParameter(Description = "How many. add mode defaults to the whole found stack when omitted (0). remove mode requires a positive count.")] int count = 0,
            [ToolParameter(Description = "remove mode: destroy the removed things (default) vs merely detach them (they leak - only ever pass false if you immediately re-add them elsewhere).")] bool destroy = true,
            [ToolParameter(Description = "add mode: clear the CompForbiddable flag on success, so the pawn's own AI will use it. Default true.")] bool unforbid = true)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string perr;
                var p = FindPawn(pawn, out perr);
                if (p == null) return Fail(perr ?? "No pawn.");
                if (p.inventory == null || p.inventory.innerContainer == null)
                    return Fail(p.LabelShortCap + " has no Pawn_InventoryTracker.");

                var m = (mode ?? "").Trim().ToLowerInvariant();

                if (m == "add")
                {
                    string terr;
                    var found = FindLiveThingById(thing, out terr);
                    if (found == null) return Fail(terr);
                    if (found.stackCount <= 0) return Fail("'" + thing + "' resolved to a thing with stackCount <= 0.");

                    int requested = count > 0 ? Math.Min(count, found.stackCount) : found.stackCount;
                    if (count > found.stackCount)
                        return Fail(string.Format("Asked to move {0} of {1} but the stack only has {2}.", count, found.def.defName, found.stackCount));

                    if (unforbid)
                    {
                        var comp = found.TryGetComp<CompForbiddable>();
                        if (comp != null) comp.Forbidden = false;
                    }

                    // A map-spawned Thing's holdingOwner IS map.spawnedThings (Verse/Map.cs), so
                    // TryAddOrTransfer routes into ThingOwner.TryTransferToContainer, whose
                    // `owner is Map` guard returns 0 for every map thing, every time -
                    // "Can't transfer items to or from Maps directly." Despawn the portion first
                    // and TryAdd it, which is exactly what that warning tells you to do.
                    int moved;
                    if (found.Spawned)
                    {
                        var part = found.SplitOff(requested);
                        if (part.Spawned) part.DeSpawn(DestroyMode.Vanish);
                        moved = p.inventory.innerContainer.TryAdd(part, part.stackCount, true);
                        if (moved <= 0 && !part.Destroyed && part.holdingOwner == null && p.Map != null)
                            GenPlace.TryPlaceThing(part, p.Position, p.Map, ThingPlaceMode.Near);
                    }
                    else
                    {
                        moved = p.inventory.innerContainer.TryAddOrTransfer(found, requested, true);
                    }

                    if (moved <= 0)
                        return Fail(string.Format(
                            "Moved 0 of {0} {1} into {2}'s inventory - the container refused it " +
                            "(not acceptable, over capacity, or already there).", requested, found.def.defName, p.LabelShortCap));

                    return new
                    {
                        success = true,
                        message = string.Format("{0} of {1} moved into {2}'s inventory{3}.",
                            moved, found.def.defName, p.LabelShortCap, moved < requested ? string.Format(" ({0} requested, only {1} moved)", requested, moved) : ""),
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        mode = m,
                        requestedCount = requested,
                        movedCount = moved,
                        thing = new { defName = found.def.defName },
                        ticksGame = TicksGameSafe()
                    };
                }

                if (m == "remove")
                {
                    if (count <= 0) return Fail("remove mode needs a positive 'count'.");
                    var def = DefDatabase<ThingDef>.GetNamedSilentFail(thingDef);
                    if (def == null) return Fail("No ThingDef named '" + thingDef + "'.", new { suggestions = DefSuggestions<ThingDef>(thingDef) });

                    int before = p.inventory.Count(def);
                    if (before == 0)
                        return Fail(p.LabelShortCap + "'s inventory holds no " + def.defName + ".",
                            new { held = p.inventory.innerContainer.Select(t => t.def.defName).Distinct().ToList() });
                    if (before < count)
                        return Fail(string.Format("{0}'s inventory holds only {1} of {2}, cannot remove {3}.", p.LabelShortCap, before, def.defName, count));

                    int remaining = count;
                    int guard = 0;
                    while (remaining > 0 && guard++ < 64)
                    {
                        int loopBefore = p.inventory.Count(def);
                        p.inventory.RemoveCount(def, remaining, destroy);
                        int loopAfter = p.inventory.Count(def);
                        int removedThisCall = loopBefore - loopAfter;
                        if (removedThisCall <= 0) break;
                        remaining -= removedThisCall;
                    }
                    int after = p.inventory.Count(def);
                    int removed = before - after;

                    if (removed < count)
                        return Fail(string.Format("Only removed {0} of the requested {1} {2} from {3}'s inventory ({4} remain).",
                            removed, count, def.defName, p.LabelShortCap, after));

                    return new
                    {
                        success = true,
                        message = string.Format("{0} of {1} removed from {2}'s inventory ({3} remain).", removed, def.defName, p.LabelShortCap, after),
                        pawn = new { id = p.ThingID, name = p.LabelShortCap.ToString() },
                        mode = m,
                        thingDef = def.defName,
                        requestedCount = count,
                        removedCount = removed,
                        remainingInInventory = after,
                        ticksGame = TicksGameSafe()
                    };
                }

                return Fail("mode must be 'add' or 'remove', got '" + mode + "'.");
            }).ConfigureAwait(false);
        }

        // ================================================================
        //  jawa/split_stack
        // ================================================================
        [Tool(
            "jawa/split_stack",
            Description =
                "Peel N off a live stack via Thing.SplitOff, then place the split piece with " +
                "GenPlace.TryPlaceThing(mode=Near). Only a STRICT partial split is accepted - count " +
                "must be less than the stack's current stackCount; asking for the whole stack is " +
                "'move the thing', not this tool. The source may be on a map OR held in a pawn's " +
                "equipment/apparel/inventory (same id resolution as jawa/thing_stats); SplitOff " +
                "handles de-spawning/detaching itself. If no valid nearby cell can be found the split " +
                "piece is merged straight back into the source stack via TryAbsorbStack before " +
                "refusing, so a failed call leaves nothing missing.",
            ResultDescription =
                "success, source{id, defName, stackCountBefore, stackCountAfter}, placed{id, x, z, " +
                "map, stackCount}.")]
        public static async Task<object> SplitStack(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Id of the stack to split (map thing, or a pawn's equipment/apparel/inventory item).")] string thing = null,
            [ToolParameter(Description = "How many to peel off. Must be at least 1 and strictly less than the stack's current count.")] int count = 0,
            [ToolParameter(Description = "Target cell 'x,z' to place near. Omit to place near the source's current position.")] string at = null)
        {
            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();
                if (Current.Game == null) return Fail("No game loaded.");

                string terr;
                var found = FindLiveThingById(thing, out terr);
                if (found == null) return Fail(terr);
                if (count <= 0) return Fail("count must be at least 1.");
                if (count >= found.stackCount)
                    return Fail(string.Format(
                        "count ({0}) must be strictly less than the stack's current count ({1}). " +
                        "Splitting off the whole stack is not a split - move or transfer the thing instead.",
                        count, found.stackCount));

                Map map = found.Map;
                IntVec3 center = found.Spawned ? found.Position : IntVec3.Invalid;
                // A held (unspawned) source - equipment, apparel, inventory - has no map or
                // position of its own; fall back to whoever holds it, then the current map, so
                // 'at' stays optional in the common case.
                if (map == null)
                {
                    var holderPawn = FindHolderPawn(found);
                    map = holderPawn != null ? holderPawn.MapHeld : Find.CurrentMap;
                    center = holderPawn != null && holderPawn.Spawned ? holderPawn.Position : IntVec3.Invalid;
                }

                if (!string.IsNullOrWhiteSpace(at))
                {
                    var parts = at.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
                    int ax, az;
                    if (parts.Length != 2 || !int.TryParse(parts[0].Trim(), out ax) || !int.TryParse(parts[1].Trim(), out az))
                        return Fail("'at' must be 'x,z'.");
                    center = new IntVec3(ax, 0, az);
                }

                if (map == null) return Fail("Could not determine a map to place on - the source has no map and no 'at' was given.");
                if (!center.IsValid) return Fail("Could not determine a placement cell - the source is unspawned and no 'at' was given.");

                int stackBefore = found.stackCount;
                var piece = found.SplitOff(count);

                Thing resultingThing;
                bool placed = GenPlace.TryPlaceThing(piece, center, map, ThingPlaceMode.Near, out resultingThing);
                if (!placed)
                {
                    found.TryAbsorbStack(piece, false);
                    return Fail(string.Format(
                        "No valid nearby cell to place {0} x {1} near ({2},{3}) on {4}. Nothing moved - the split piece was merged back into the source.",
                        count, piece.def.defName, center.x, center.z, map));
                }

                return new
                {
                    success = true,
                    message = string.Format("{0} x {1} split off and placed at ({2},{3}).", count, piece.def.defName, resultingThing.Position.x, resultingThing.Position.z),
                    source = new
                    {
                        id = found.ThingID,
                        defName = found.def.defName,
                        stackCountBefore = stackBefore,
                        stackCountAfter = found.Destroyed ? 0 : found.stackCount
                    },
                    placed = new
                    {
                        id = resultingThing.ThingID,
                        x = resultingThing.Position.x,
                        z = resultingThing.Position.z,
                        map = map.Index,
                        stackCount = resultingThing.stackCount
                    },
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        private static Pawn FindHolderPawn(Thing t)
        {
            var ph = t.ParentHolder;
            var eq = ph as Pawn_EquipmentTracker;
            if (eq != null) return eq.pawn;
            var ap = ph as Pawn_ApparelTracker;
            if (ap != null) return ap.pawn;
            var inv = ph as Pawn_InventoryTracker;
            if (inv != null) return inv.pawn;
            return null;
        }
    }
}
