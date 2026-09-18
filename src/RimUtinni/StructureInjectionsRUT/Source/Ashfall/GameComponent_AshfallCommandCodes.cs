using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // Idempotency + persistence for AshfallCommandCodesFlag.Seize() -- same
    // discipline as GameComponent_WarLabCrater: a permanent, Scribe'd flag
    // that survives the RUT_RakatanCommandCodes item itself being lost or
    // consumed on redeem. Whoever finishes ANCIENT_WAR_LAB_1/
    // WAR_LAB_CRATER_HOOK_1's own locked-door check may gate on this flag OR
    // on raw possession of the item -- both are defensible reads of
    // ASHFALL_RESEARCH_BASE_1's "quest-item/quest-flag mechanism" phrasing;
    // this component only guarantees the flag exists and is honestly
    // persisted, not which one the door checks.
    public class GameComponent_AshfallCommandCodes : GameComponent
    {
        public bool CommandCodesSeized;

        public GameComponent_AshfallCommandCodes(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref CommandCodesSeized, "rutAshfallCommandCodesSeized", false);
        }
    }
}
