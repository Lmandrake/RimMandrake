using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // SEA_DIVE_MAPS_BUILD_1 / SHIP-ONLY ACCESS RULING (owner, 2026-09-26,
    // mid-turn, this item's ledger): "the gravship is the sole dive/
    // resurface mechanism." Enforced here at CONSTRUCTION time rather than
    // guessing at gravship world-tile-travel rules this item doesn't own:
    // RM_SeaDiveHatch may only be built on a map that already carries a
    // real, existing ThingDef — GravEngine (Odyssey) — i.e. inside a
    // gravship's own structure. Checkable offline against the live def set;
    // does not touch or assume anything about tile-impassability travel
    // rules, which stay an open engine question for a future item.
    public class PlaceWorker_NeedsGravEngine : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
            Thing thingToIgnore = null, Thing thing = null)
        {
            if (!RM_DivingSettings.requireGravEngine)
            {
                return true;
            }
            ThingDef gravEngineDef = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (gravEngineDef == null)
            {
                // Odyssey not installed. This building is itself gated to
                // load only with Odyssey present (RM_SeaDiveHatch.xml), so
                // reaching this with a null def means the requirement is
                // moot — nothing to check against.
                return true;
            }
            if (map != null && map.listerThings.ThingsOfDef(gravEngineDef).Count > 0)
            {
                return true;
            }
            return "RM_SeaDiveHatchNeedsGravEngine".Translate();
        }
    }
}
