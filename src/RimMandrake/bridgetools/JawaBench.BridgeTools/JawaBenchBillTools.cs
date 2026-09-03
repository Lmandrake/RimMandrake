// JawaBenchBillTools.cs - the production loop, previously ZERO bridge coverage.
//
// design/Jawa/bridge/dll_capability_roster.html measured this as one of ten domains with
// no tool at all: "Bills & production - cannot put a recipe on a workbench - the whole
// production loop (BillStack returned zero hits)." Owner, 2026-08-29: "Build all of those."
//
// THE CANONICAL CONSTRUCTION PATH - do not hand-build a Bill_Production
// =======================================================================
// RimWorld/BillUtility.cs's RecipeDef.MakeNewBill() extension is what the game's own UI
// (ITab_Bills.cs) and its own test harness (Autotests_ColonyMaker.cs) call to create a bill -
// it initializes ingredientFilter and everything else the UI would. Constructing
// Bill_Production directly and setting fields from scratch risks missing whatever MakeNewBill
// does that a field-by-field build would not reproduce.
//
// suspended vs paused - read, not guessed
// =========================================
// Bill_Production.ShouldDoNow() (RimWorld/Bill_Production.cs:207-243), read in full: `suspended`
// (declared on the base Bill class) is checked FIRST and unconditionally blocks the bill
// regardless of repeat mode - the universal pause switch. `paused` is a SEPARATE, internal,
// self-managing field relevant only under BillRepeatModeDefOf.TargetCount (auto-set true when
// pauseWhenSatisfied and the target is met, auto-cleared otherwise) - not something a caller
// should set directly. This tool exposes `suspended` as the pause parameter and leaves `paused`
// alone to manage itself.
//
// Thread affinity, same rule as every other file here: everything touching game state is
// inside ctx.MainThread.InvokeAsync and nothing else is.

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
            "jawa/bill_add_legacy",
            Description =
                "🔴 RENAMED from 'jawa/bill_add' 2026-08-29 - that name collided with a second, " +
                "independently-written bill_add in JawaBenchZoneTools.cs (built 2026-08-26, " +
                "paired with jawa/configure_bill and the one PLACER_IDENTITY_REPLAY_1 documents " +
                "using), and RimBridge's capability registry refuses the WHOLE provider on a " +
                "duplicate alias - every jawa/ tool was dark until this was found and split. " +
                "Prefer jawa/bill_add; this sibling is kept only in case something relied on " +
                "its specific RecipeDef.MakeNewBill() code path. " +
                "Adds a production Bill for a RecipeDef to a workbench/billable thing - the " +
                "capability this bridge had zero coverage of (BillStack returned zero hits in " +
                "a full API grep). Uses RecipeDef.MakeNewBill(), the same call the game's own " +
                "Bills UI makes, then IBillGiver.BillStack.AddBill(). " +
                "⛔ Refuses a recipe/workbench pairing not in RecipeDef.recipeUsers rather than " +
                "silently accepting it. " +
                "🔑 repeatMode: 'forever' (never stops), 'repeatCount' (does repeatCount " +
                "batches then stops, DEFAULT), 'targetCount' (keeps a stock of targetCount, " +
                "auto-pauses when met if pauseWhenSatisfied). suspended is the universal pause " +
                "switch (Bill.suspended, checked before repeatMode in ShouldDoNow) - use it, " +
                "not a guess at the separate internal `paused` field.",
            ResultDescription =
                "success, thingId, thingDefName, recipeDefName, repeatMode, repeatCount, " +
                "targetCount, suspended, billIndex (position in the stack), billCount.")]
        public static async Task<object> BillAdd(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Id of the workbench/billable thing, as jawa/list_things reports.")]
            string thingId,
            [ToolParameter(Description = "RecipeDef defName. Must be usable on the thing's ThingDef (recipe.recipeUsers).")]
            string recipeDefName,
            [ToolParameter(Description = "'forever' | 'repeatCount' (default) | 'targetCount'.")]
            string repeatMode = null,
            [ToolParameter(Description = "Batches to run before stopping, when repeatMode is 'repeatCount'.", DefaultValue = 1)]
            int repeatCount = 1,
            [ToolParameter(Description = "Stock to maintain, when repeatMode is 'targetCount'.", DefaultValue = 10)]
            int targetCount = 10,
            [ToolParameter(Description = "The universal pause switch (Bill.suspended). False = active.", DefaultValue = false)]
            bool suspended = false)
        {
            cancellationToken.ThrowIfCancellationRequested();

            if (string.IsNullOrWhiteSpace(thingId)) return Fail("thingId is required.");
            if (string.IsNullOrWhiteSpace(recipeDefName)) return Fail("recipeDefName is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var thing = FindLiveThingById(thingId, out var findErr);
                if (thing == null) return Fail(findErr ?? "No thing '" + thingId + "'.");

                if (!(thing is IBillGiver billGiver))
                    return Fail("Thing '" + thingId + "' (" + thing.def.defName + ") is not an " +
                                "IBillGiver - it has no BillStack.");

                var recipe = DefDatabase<RecipeDef>.GetNamedSilentFail(recipeDefName.Trim());
                if (recipe == null)
                    return Fail("No RecipeDef '" + recipeDefName + "'.",
                        DefSuggestions<RecipeDef>(recipeDefName));

                bool compatible = thing.def.AllRecipes != null && thing.def.AllRecipes.Contains(recipe);
                if (!compatible)
                    return Fail("RecipeDef '" + recipeDefName + "' is not usable on ThingDef '" +
                                thing.def.defName + "' (not in thing.def.AllRecipes).",
                        new { recipeUsers = recipe.recipeUsers?.Select(t => t.defName).ToList() });

                BillRepeatModeDef mode = null;
                if (!string.IsNullOrWhiteSpace(repeatMode))
                {
                    switch (repeatMode.Trim().ToLowerInvariant())
                    {
                        case "forever": mode = BillRepeatModeDefOf.Forever; break;
                        case "repeatcount": mode = BillRepeatModeDefOf.RepeatCount; break;
                        case "targetcount": mode = BillRepeatModeDefOf.TargetCount; break;
                        default:
                            return Fail("Unknown repeatMode '" + repeatMode + "'. Use 'forever', " +
                                        "'repeatCount' or 'targetCount'.");
                    }
                }

                Bill bill;
                try { bill = recipe.MakeNewBill(); }
                catch (Exception e) { return Fail("MakeNewBill threw: " + e.GetType().Name + ": " + e.Message); }
                if (bill == null) return Fail("MakeNewBill returned null for '" + recipeDefName + "'.");

                if (bill is Bill_Production prod)
                {
                    if (mode != null) prod.repeatMode = mode;
                    prod.repeatCount = repeatCount;
                    prod.targetCount = targetCount;
                }
                else if (!string.IsNullOrWhiteSpace(repeatMode))
                {
                    return Fail("RecipeDef '" + recipeDefName + "' made a " + bill.GetType().Name +
                                ", not a Bill_Production - repeatMode/repeatCount/targetCount do " +
                                "not apply to it. Omit them and retry.");
                }
                bill.suspended = suspended;

                billGiver.BillStack.AddBill(bill);

                return (object)new
                {
                    success = true,
                    thingId,
                    thingDefName = thing.def.defName,
                    recipeDefName,
                    repeatMode = (bill as Bill_Production)?.repeatMode?.defName,
                    repeatCount = (bill as Bill_Production)?.repeatCount,
                    targetCount = (bill as Bill_Production)?.targetCount,
                    suspended = bill.suspended,
                    billIndex = billGiver.BillStack.Count - 1,
                    billCount = billGiver.BillStack.Count,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/bill_list",
            Description =
                "Lists every Bill on a workbench/billable thing's BillStack, in order (index " +
                "matches jawa/bill_remove's billIndex). Adds, removes and changes nothing. " +
                "Reports ShouldDoNow() live, so a caller can tell 'suspended' from 'active but " +
                "target already met' from 'active and will actually run next' without " +
                "re-deriving the logic. ⚠️ Not strictly side-effect-free: Bill_Production." +
                "ShouldDoNow() re-evaluates the bill's own self-managed `paused` flag as it " +
                "runs (sets it under TargetCount+pauseWhenSatisfied, clears it otherwise) - " +
                "the same write the game performs every time a pawn looks for work.",
            ResultDescription =
                "success, thingId, thingDefName, billCount, bills[] of {index, recipeDefName, " +
                "label, suspended, repeatMode, repeatCount, targetCount, shouldDoNow}.")]
        public static async Task<object> BillList(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Id of the workbench/billable thing.")]
            string thingId)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (string.IsNullOrWhiteSpace(thingId)) return Fail("thingId is required.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var thing = FindLiveThingById(thingId, out var findErr);
                if (thing == null) return Fail(findErr ?? "No thing '" + thingId + "'.");

                if (!(thing is IBillGiver billGiver))
                    return Fail("Thing '" + thingId + "' (" + thing.def.defName + ") is not an " +
                                "IBillGiver - it has no BillStack.");

                var bills = billGiver.BillStack.Bills;
                var rows = new List<object>();
                for (int i = 0; i < bills.Count; i++)
                {
                    var b = bills[i];
                    bool shouldDoNow;
                    try { shouldDoNow = b.ShouldDoNow(); }
                    catch { shouldDoNow = false; }
                    rows.Add(new
                    {
                        index = i,
                        recipeDefName = b.recipe?.defName,
                        label = b.Label,
                        suspended = b.suspended,
                        repeatMode = (b as Bill_Production)?.repeatMode?.defName,
                        repeatCount = (b as Bill_Production)?.repeatCount,
                        targetCount = (b as Bill_Production)?.targetCount,
                        shouldDoNow
                    });
                }

                return (object)new
                {
                    success = true,
                    thingId,
                    thingDefName = thing.def.defName,
                    billCount = bills.Count,
                    bills = rows,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }

        [Tool(
            "jawa/bill_remove",
            Description =
                "Removes one Bill from a workbench/billable thing's BillStack, by index (see " +
                "jawa/bill_list). Uses BillStack.Delete(bill), which also calls the billGiver's " +
                "own Notify_BillDeleted - not manual list removal.",
            ResultDescription = "success, thingId, removedRecipeDefName, billCountAfter.")]
        public static async Task<object> BillRemove(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Id of the workbench/billable thing.")]
            string thingId,
            [ToolParameter(Description = "Position in the BillStack, from jawa/bill_list's index.")]
            int billIndex,
            [ToolParameter(Description = "Must be true. Confirms the removal, which cannot be undone.")]
            bool confirmRemove = false)
        {
            cancellationToken.ThrowIfCancellationRequested();
            if (string.IsNullOrWhiteSpace(thingId)) return Fail("thingId is required.");
            if (!confirmRemove) return Fail("confirmRemove must be true - this removal cannot be undone.");

            return await ctx.MainThread.InvokeAsync(() =>
            {
                var thing = FindLiveThingById(thingId, out var findErr);
                if (thing == null) return Fail(findErr ?? "No thing '" + thingId + "'.");

                if (!(thing is IBillGiver billGiver))
                    return Fail("Thing '" + thingId + "' (" + thing.def.defName + ") is not an " +
                                "IBillGiver - it has no BillStack.");

                var bills = billGiver.BillStack.Bills;
                if (billIndex < 0 || billIndex >= bills.Count)
                    return Fail("billIndex " + billIndex + " out of range - this thing has " +
                                bills.Count + " bill(s) (0.." + (bills.Count - 1) + ").");

                var bill = bills[billIndex];
                var removedRecipe = bill.recipe?.defName;
                billGiver.BillStack.Delete(bill);

                return (object)new
                {
                    success = true,
                    thingId,
                    removedRecipeDefName = removedRecipe,
                    billCountAfter = billGiver.BillStack.Count,
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
