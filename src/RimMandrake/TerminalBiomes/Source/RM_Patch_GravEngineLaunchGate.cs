using RimWorld;
using Verse;
using HarmonyLib;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_PANE_STRIKE_1 — danger pass D8, "The laden deck: the sky
    // lands on your ship." "Launch requires a cleared deck: a clearing job
    // per pane... panes DELAY departure behind a job the colony can always
    // do; they never disable the engine and never fire during an emergency
    // launch already in progress — the never-strand guarantee stays a
    // binding bar on the item."
    //
    // ENFORCEMENT OF THE NEVER-STRAND BAR, stated plainly because this repo
    // has no bridge/game-launch access this pass to prove it live
    // (BUILD subagent hard rule):
    //
    //   1. This is a HARMONY POSTFIX on Building_GravEngine.CanLaunch, the
    //      single choke point CompPilotConsole.CanUseNow() already reads
    //      before it ever offers the "use console" job to a pawn (RimSage-
    //      verified, RimWorld/CompPilotConsole.cs:266). It runs AFTER
    //      vanilla's own checks (substructure/fuel/thrusters/cooldown) and
    //      can only ever turn an ALREADY-Accepted report into a Rejected
    //      one — the `if (!__result.Accepted) return;` guard below means it
    //      can never CREATE a launch vanilla itself refused, and it never
    //      writes to `engine` (no fuel consumed, no cooldown set, no
    //      substructure edited): pure read of AcceptanceReport, pure
    //      possible downgrade of the return value. That is what makes it a
    //      DELAY and structurally incapable of being a stranding.
    //   2. Odyssey ships NO "emergency launch" bypass of CanLaunch at all
    //      (RimSage search_source across *.cs for Emergency/emergency
    //      returned zero hits, 2026-09-27) — there is no forced-takeoff
    //      code path this patch could be sitting in front of and blocking
    //      by mistake. Every real player launch goes through CanLaunch.
    //   3. The gate counts real, already-landed RM_VeilPane things via
    //      Building_GravEngine.OnValidSubstructure(thing) — the same
    //      wall-attachment-aware test the engine uses for its own
    //      substructure bookkeeping — never a synthetic counter that could
    //      drift from what a player can actually see and clear.
    //   4. The clearing job is vanilla Deconstruct (RM_VeilPane.xml,
    //      ParentName="ShipChunkBase", `alwaysDeconstructible`) — "a job
    //      the colony can always do" is not asserted, it is the SAME job
    //      already used for every other salvage building in this mod
    //      (RUT_ScaldWreckHull/Tank/Frame).
    //
    // No selftest harness in this repo exercises gravship launch mechanics
    // offline (checked: no validation.py under this mod, and the CHARTER's
    // north-star system has no coverage for Odyssey defs) — a live
    // verification is owed to a session with the bridge and the owner
    // present, per this repo's own flyer-testing precedent for anything
    // that needs an actual game tick to prove.
    [RimMandrake.Shared.PatchFeature("RM_Patch_GravEngineLaunchGate", typeof(RM_TerminalBiomesSettings), "TwilightDeckAccumulationActive")]
    [HarmonyPatch(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch))]
    public static class RM_Patch_GravEngineLaunchGate
    {
        [HarmonyPostfix]
        public static void Postfix(Building_GravEngine __instance, ref AcceptanceReport __result)
        {
            if (!__result.Accepted)
            {
                return;
            }
            if (!RM_TerminalBiomesSettings.TwilightDeckAccumulationActive)
            {
                return;
            }
            Map map = __instance.Map;
            if (map == null)
            {
                return;
            }
            if (RM_VeilFallDefOf.RM_VeilPane == null)
            {
                // A failed def load must never turn a launch-gate postfix
                // into a launch-gate crash. This postfix can only ever
                // downgrade an already-Accepted report (see this file's own
                // header) — skipping it on a null DefOf fails open, which
                // stays honest with that guarantee.
                return;
            }
            foreach (Thing thing in map.listerThings.ThingsOfDef(RM_VeilFallDefOf.RM_VeilPane))
            {
                if (__instance.OnValidSubstructure(thing))
                {
                    __result = new AcceptanceReport("RM_GravEngineCannotLaunchVeilFall".Translate());
                    return;
                }
            }
        }
    }
}
