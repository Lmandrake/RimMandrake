using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_LIGHT_ECONOMY_1 §4.1. RM_ClaimBuoy: "a small lit building at
    // a well." This comp is only the buoy's own bookkeeping — which well
    // (if any) it stands on, and whether it is a Compact hold or a player's
    // free hold. Compact placement/re-placement as wells drift is NOT built
    // here — it rides TWILIGHT_DEEPWATER_HOUSES_1's bottom-house cast,
    // which does not exist in this codebase yet. A player-placed buoy is
    // "honoured... but unprotected" per spec, which needs no code: it is
    // simply never removed by anything in this mod.
    public class RM_CompProperties_ClaimBuoy : CompProperties
    {
        public RM_CompProperties_ClaimBuoy()
        {
            compClass = typeof(RM_Comp_ClaimBuoy);
        }
    }

    public class RM_Comp_ClaimBuoy : ThingComp
    {
        public int wellId = -1;
        public bool compactOwned; // false = a player's free hold (§4.1)

        public RM_CompProperties_ClaimBuoy Props => (RM_CompProperties_ClaimBuoy)props;

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            if (respawningAfterLoad || wellId >= 0)
            {
                return;
            }
            // Player-built buoy, freshly spawned: claim the nearest open,
            // as-yet-unclaimed well under it, if any — "the player may
            // place their own buoy on any unclaimed well."
            RM_MapComponent_WellLedger ledger = RM_MapComponent_WellLedger.GetFor(parent.Map);
            if (ledger == null)
            {
                return;
            }
            foreach (RM_MapComponent_WellLedger.WellRecord w in ledger.OpenWells())
            {
                if (w.position.DistanceTo(parent.Position) <= 6f && w.buoyThing == null)
                {
                    wellId = w.id;
                    w.buoyThing = parent;
                    compactOwned = false;
                    break;
                }
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref wellId, "rmClaimBuoyWellId", -1);
            Scribe_Values.Look(ref compactOwned, "rmClaimBuoyCompactOwned");
        }

        public override string CompInspectStringExtra()
        {
            if (wellId < 0)
            {
                return "RM_ClaimBuoy_NoWell".Translate();
            }
            return compactOwned
                ? "RM_ClaimBuoy_CompactHold".Translate(wellId)
                : "RM_ClaimBuoy_FreeHold".Translate(wellId);
        }
    }
}
