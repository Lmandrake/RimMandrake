using RimWorld;
using Verse;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_RULED_CONTENT_1 §9 (Q13) — the shared consequence.
    //
    // Lifted out of MapComponent_BrineCrystallisation's own private Encase
    // method (per grey_deep_pool_sentinel_2026-09-27.md §2: "lift the
    // private Encase(Pawn, ThingDef) into a small shared static... call it
    // from both the map component and the orruhmu's one new comp") so the
    // pool/chimney triggers and the orruhmu's squirt (RM_CompPoolSentinelSquirt)
    // resolve into ONE mechanism, not two. No behaviour changed from the
    // original method — same clear-cell-first, same TryEncase/Spawn/Message
    // shape.
    // ════════════════════════════════════════════════════════════════════
    public static class BrineEncasementUtility
    {
        public static bool TryEncase(Pawn p, Map map)
        {
            if (p == null || map == null || !p.Spawned)
            {
                return false;
            }
            ThingDef jacketDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BrineEncasement");
            if (jacketDef == null)
            {
                return false;
            }

            IntVec3 cell = p.Position;
            bool wasPlayers = p.Faction != null && p.Faction.IsPlayer;
            string label = p.LabelShortCap;

            // Clear the cell first: a jacket is an Impassable edifice and
            // cannot share a cell with a pillar or a dome that scattered here.
            // An indestructible edifice (the dive exit, destroyable=false) is
            // never destroyed: the engine refuses and logs an error. No
            // encasement on such a cell (SEA_DIVE_LIVE_ERRORS_1).
            Building edifice = cell.GetEdifice(map);
            if (edifice != null && !edifice.def.destroyable)
            {
                return false;
            }
            edifice?.Destroy();

            RM_Building_BrineEncasement jacket =
                (RM_Building_BrineEncasement)ThingMaker.MakeThing(jacketDef);

            if (!jacket.TryEncase(p))
            {
                // Never spawned, so there is nothing to Destroy — dropping
                // the reference is the correct cleanup for an unspawned Thing.
                return false;
            }
            GenSpawn.Spawn(jacket, cell, map);

            if (wasPlayers)
            {
                Messages.Message(
                    label + " touched the brine and the salt closed over them. "
                    + "Mine the jacket out before they smother.",
                    jacket, MessageTypeDefOf.ThreatBig, false);
            }
            return true;
        }
    }
}
