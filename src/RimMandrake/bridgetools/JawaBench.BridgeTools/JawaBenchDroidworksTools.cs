// JawaBenchDroidworksTools.cs - DROIDWORKS_FORMAT_TIERS_1 root-cause pass, 2026-09-18.
//
// jawa/pawn_health cannot correctly test format-tier need gating, and this is
// structural, not a misuse - read start-to-finish and independently re-confirmed
// against 1.6 source this pass (see the item file's root-cause sections):
//   * Hediff.Severity's setter (Source/Verse/Hediff.cs) calls
//     Pawn_HealthTracker.Notify_HediffChanged -> HediffSet.DirtyCache on a
//     stage-index change, which refreshes cachedDisabledNeeds, but never calls
//     Pawn_NeedsTracker.AddOrRemoveNeedsAsAppropriate() - so the actual Need
//     object list does not move.
//   * That rebuild fires only from HediffSet.AddDirect (once, at the stage
//     active when the hediff is first added) and from Hediff.PostRemoved (once,
//     at removal) - both read via HediffStage.disablesNeeds/enablesNeeds on
//     the CurStage at that one moment, never again afterward.
//   * jawa/pawn_health's action='add' path (JawaBenchPawnTools.cs, PawnHealth)
//     calls health.AddHediff(hd, part) - firing the rebuild once at
//     hd.initialSeverity (3.0 = Programmable for RSW_DW_FormatTier) - then, only
//     if severity>=0 was passed, does a bare `h.Severity = severity` poke that
//     changes the stage but never re-triggers the rebuild. So a probe that adds
//     the hediff and then walks it through four severities via that tool reads
//     the SAME stale Programmable-stage need snapshot at all four "different"
//     stages, which is exactly the false FAIL the 2026-09-08 quicktest logged.
//
// DroidFormatTierUtility.SetTier (Source/Droidworks/DroidFormatTier.cs) already
// calls pawn.needs?.AddOrRemoveNeedsAsAppropriate() explicitly after moving the
// severity - it is the correct, already-shipped fix for exactly this vanilla
// gap. This file exposes that method directly to the bridge instead of adding
// a parallel reimplementation, the same route JawaBenchOracleTools.cs already
// uses for RimMandrakeOracle.dll: Droidworks.dll is an ordinary RimWorld mod
// (mandrake.rsw.droidworks) that the mod loader has already loaded into the
// process well before RimBridgeServer attaches its companions, so calling
// straight into it needs a Reference (csproj's DroidworksModDir), not a new
// Harmony patch or a duplicated needs-rebuild call.
//
// action='set' is therefore the one bridge-side route that can correctly prove
// or disprove need gating by tier (DROIDWORKS_FORMAT_TIERS_1's boxes 2/3/6/7) -
// jawa/pawn_health cannot, for any severity value, on this or any other hediff
// whose gate depends on AddOrRemoveNeedsAsAppropriate reading the CURRENT stage.

using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimMandrake.StarWars.Droidworks;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/droid_format_tier",
            Description =
                "Read (action='get') or set (action='set', tier='blank'|'mindless'|" +
                "'programmable'|'sapient') a droid's DROIDWORKS_FORMAT_TIERS_1 format " +
                "tier by calling RimMandrake.StarWars.Droidworks.DroidFormatTierUtility" +
                ".SetTier directly - the EXACT path the three format recipes use, " +
                "including its explicit AddOrRemoveNeedsAsAppropriate() needs-rebuild " +
                "call. ⭐ Use this, never jawa/pawn_health, to test need gating by " +
                "tier: pawn_health's add-then-poke-Severity pattern cannot trigger " +
                "that rebuild after the initial add, so every stage after the first " +
                "it probes reads a stale needs snapshot. Refuses on a non-droid " +
                "(RaceProps.FleshType != RSW_DW_FleshType_Droid).",
            ResultDescription =
                "success, action, tier, severity, and needs[] read back from " +
                "pawn.needs.AllNeeds AFTER the rebuild - the actual live Need list, " +
                "not the cached disabled-needs set.")]
        public static async Task<object> DroidFormatTierTool(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "Pawn id or name.")] string pawn = null,
            [ToolParameter(Description = "'get' | 'set'.")] string action = "get",
            [ToolParameter(Description = "'blank'|'mindless'|'programmable'|'sapient'. Required for action='set'.")] string tier = null)
        {
            return await ctx.MainThread.InvokeAsync(() =>
            {
                string err; var p = FindPawn(pawn, out err);
                if (p == null) return Fail(err);
                if (!DroidFormatTierUtility.IsDroid(p))
                    return Fail("'" + p.LabelShortCap + "' is not a droid (RaceProps.FleshType != RSW_DW_FleshType_Droid) - format tiers are droid-only.");

                string A = (action ?? "get").Trim().ToLowerInvariant();
                if (A == "set")
                {
                    if (string.IsNullOrEmpty(tier)) return Fail("Give tier: blank|mindless|programmable|sapient.");
                    DroidFormatTier t;
                    switch (tier.Trim().ToLowerInvariant())
                    {
                        case "blank": t = DroidFormatTier.Blank; break;
                        case "mindless": t = DroidFormatTier.Mindless; break;
                        case "programmable": t = DroidFormatTier.Programmable; break;
                        case "sapient": t = DroidFormatTier.Sapient; break;
                        default: return Fail("Unknown tier '" + tier + "'. Use blank|mindless|programmable|sapient.");
                    }
                    DroidFormatTierUtility.SetTier(p, t);
                }
                else if (A != "get")
                {
                    return Fail("action must be 'get' or 'set'.");
                }

                var curTier = DroidFormatTierUtility.TierOf(p);
                var hediff = p.health?.hediffSet?.GetFirstHediffOfDef(DroidworksDefOf.RSW_DW_FormatTier);
                return (object)new
                {
                    success = true,
                    action = A,
                    tier = curTier?.ToString() ?? "(none - no RSW_DW_FormatTier hediff on this pawn)",
                    severity = hediff?.Severity ?? -1f,
                    needs = p.needs?.AllNeeds?.Select(n => n.def.defName).ToList(),
                    ticksGame = TicksGameSafe(),
                };
            });
        }
    }
}
