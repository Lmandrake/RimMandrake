using System;
using RimWorld;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_BOTTLE_LOOP_1, the "use" half. Runs whenever a filled bottle
    /// is eaten/drunk by ANY route -- plain vanilla nutrition, a mod's own
    /// thirst need, a caravan meal tick -- because it hangs off
    /// IngestibleProperties.outcomeDoers, the one vanilla extension point
    /// every ingestion path already calls through Thing.Ingested. That is
    /// what "drinkable-agnostic" means in practice: this class never checks
    /// for DBH. The drink itself is IngestionOutcomeDoer_RM_Hydrate (FlowWorks'
    /// own thirst), and DBH's drinkable registration (the generated
    /// Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml) layers DBH's thirst on the
    /// SAME ingestion: design/RimMandrake/thirst_bottles_design_2026-10-16.md.
    ///
    /// Same shape as the local precedent, GelatinousSlime's
    /// IngestionOutcomeDoer_SlimeDose (Source/SlimeIngestion.cs) -- a try/
    /// catch around the whole body, because an outcome doer throwing must
    /// never turn "drank a bottle" into a stuck job.
    ///
    /// Only wired onto BOTTLES of rows with a thirstQuality set (fresh/salt/
    /// toxic/brine/coloured water, generate_liquid_suite.py's own gate; buckets
    /// and barrels are decanted, never drunk) -- boiling,
    /// icy, acid, tar and propane bottles carry no ingestible block at all,
    /// so this class is never called for them. "Use" for those (revert-on-
    /// bottle, industrial consumption) is separate, unbuilt work, not a case
    /// this doer silently mishandles.
    /// </summary>
    public class IngestionOutcomeDoer_BottleResidue : IngestionOutcomeDoer
    {
        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            try
            {
                if (pawn == null || ingested?.def == null)
                {
                    return;
                }
                RM_BottledLiquidExtension ext = ingested.def.GetModExtension<RM_BottledLiquidExtension>();
                if (ext == null || ext.liquid == null)
                {
                    // Not one of our bottles, or a bottle def with no
                    // recorded content (should never happen -- a filled
                    // bottle always carries `liquid`) -- leave nothing
                    // behind rather than guess.
                    return;
                }

                ThingDef residueDef = RimMandrakeFlowWorksSettings.bottleDirtyStageEnabled
                    ? RM_LiquidBottleUtility.DirtyDefFor(ext.size)
                    : RM_LiquidBottleUtility.EmptyDefFor(ext.size);
                if (residueDef == null)
                {
                    return;
                }

                Thing residue = RM_LiquidBottleUtility.MakeContainer(residueDef, ingested);
                residue.stackCount = Math.Max(1, ingestedCount);

                // On a map, the container goes to the ground beside the drinker: the wash and fill work givers only
                // see spawned things, and nothing unloads it from an inventory. Off a map (a caravan pawn has no
                // MapHeld) it goes into the inventory, so the caravan route keeps it (GPT FlowWorks review #25).
                Map map = pawn.MapHeld;
                if (map != null && pawn.SpawnedOrAnyParentSpawned
                    && GenPlace.TryPlaceThing(residue, pawn.PositionHeld, map, ThingPlaceMode.Near))
                {
                    return;
                }
                if (pawn.inventory != null && pawn.inventory.innerContainer.TryAdd(residue))
                {
                    return;
                }
                residue.Destroy();
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.FlowWorks] bottle residue outcome failed: " + e.Message, 0x8077E5);
            }
        }
    }
}
