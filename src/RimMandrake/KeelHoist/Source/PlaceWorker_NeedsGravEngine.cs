using RimWorld;
using Verse;

namespace RimMandrake.KeelHoist
{
    // Copied from DivingInteraction (design §1a: copy, never reference — that mod's hatch is being retired),
    // and tightened: the hoist is a SHIP PART, so every cell of its footprint must be substructure on a map
    // that carries a grav engine.
    public class PlaceWorker_NeedsGravEngine : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map,
            Thing thingToIgnore = null, Thing thing = null)
        {
            if (!KeelHoistSettings.requireGravEngine || map == null)
            {
                return true;
            }

            ThingDef gravEngineDef = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (gravEngineDef == null || map.listerThings.ThingsOfDef(gravEngineDef).Count == 0)
            {
                return "A keel hoist is a ship part: build it on a gravship (no grav engine on this map).";
            }

            foreach (IntVec3 c in GenAdj.OccupiedRect(loc, rot, checkingDef.Size))
            {
                if (!c.InBounds(map) || !c.GetTerrain(map).IsSubstructure)
                {
                    return "A keel hoist must stand on the ship's substructure.";
                }
            }

            return true;
        }
    }
}
