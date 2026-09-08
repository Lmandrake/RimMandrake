using System.Linq;
using LudeonTK;
using RimWorld;
using Verse;
using Verse.AI;

namespace RimMandrake.TheftHauler
{
    /// <summary>
    /// BUILDING_THEFT_HAULER_1's own test harness. The real feature is
    /// gated behind TheftHaulerExtension, carried only by Droidworks'
    /// Muckraker Crab Droid (see FloatMenuOptionProvider_TheftHaulUninstall's
    /// own comment) -- and mandrake.rsw.droidworks is not on the live mod
    /// list, confirmed by grepping ModsConfig.xml, not assumed. That leaves
    /// no pawn kind on this list that could ever see the real float-menu
    /// option. This action skips the eligibility gate (cosmetic/flavor,
    /// per the item's own note: "carry-weight-scales-with-chassis is
    /// explicitly deferred") on ANY pawn, to prove the thing that IS
    /// uncertain: JobDriver_TheftHaulUninstall.FinishedRemoving actually
    /// fires PropertyEngine.Fire(TakingAct.Strip) and a Stolen record lands
    /// against the acting pawn for a building that belongs to someone else.
    /// Does NOT prove the chassis gate itself works -- that still needs
    /// Droidworks live, flagged rather than silently assumed.
    /// </summary>
    public static class DebugActions_TheftHauler
    {
        private const string Cat = "RimMandrake.TheftHauler";

        [DebugAction(Cat, "Test: theft-haul-uninstall clicked building (any pawn, bypasses chassis gate)",
            allowedGameStates = AllowedGameStates.PlayingOnMap,
            actionType = DebugActionType.ToolMap)]
        private static void TestTheftHaulUninstall()
        {
            IntVec3 cell = UI.MouseCell();
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return;
            }
            Building building = cell.GetFirstBuilding(map);
            if (building == null)
            {
                Log.Warning("[RimMandrake.TheftHauler] no building at " + cell + ".");
                return;
            }
            // Matches FloatMenuOptionProvider_TheftHaulUninstall's own gate
            // exactly (category == Building AND Minifiable) -- adversarial
            // review, 2026-09-07: this harness previously checked Minifiable
            // alone, so a hypothetical non-Building-category Minifiable thing
            // would pass here while the real player-facing feature would
            // refuse it, undermining this comment's own claim.
            if (building.def.category != ThingCategory.Building || !building.def.Minifiable)
            {
                Log.Warning("[RimMandrake.TheftHauler] " + building.LabelShort + " is not Minifiable -- "
                    + "the real job would refuse this target too (see FloatMenuOptionProvider's own gate).");
                return;
            }
            Pawn actor = PawnsFinder.AllMaps_FreeColonists.FirstOrDefault(p => !p.Downed && p.jobs != null);
            if (actor == null)
            {
                Log.Warning("[RimMandrake.TheftHauler] no free, undowned colonist available to run the job.");
                return;
            }
            Job job = JobMaker.MakeJob(TheftHaulerDefOf.RM_TheftHaulUninstall, building);
            bool started = actor.jobs.TryTakeOrderedJob(job, JobTag.Misc);
            Log.Message("[RimMandrake.TheftHauler] " + actor.LabelShort + " ordered to theft-haul-uninstall "
                + building.LabelShort + " (faction " + (building.Faction?.Name ?? "none") + ") -- job started="
                + started + ". Watch for FinishedRemoving's PropertyEngine.Fire log / ClaimRecord once it "
                + "completes.");
        }
    }
}
