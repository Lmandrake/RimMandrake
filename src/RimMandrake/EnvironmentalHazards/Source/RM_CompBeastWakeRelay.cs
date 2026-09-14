using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_MECHANICS_1 S3 (sump_kit_spec.md "S3. The tar beast set-pieces").
    //
    // The dormant-Building-to-pawn TRANSITION itself needs no new class:
    // RimWorld ships CompPawnSpawnOnWakeup / CompProperties_PawnSpawnOnWakeup
    // (RimWorld/CompPawnSpawnOnWakeup.cs, read in full this pass) for
    // exactly this shape. Vanilla's own CocoonMegaspider / CocoonMegascarab
    // / CocoonSpelopede (Data/Core/Defs/ThingDefs_Buildings/
    // Buildings_Natural.xml, read directly from the live install) already
    // ship "a dormant Building that spawns a pawn and destroys itself the
    // instant its sibling CompCanBeDormant.Awake flips true" — its own
    // CompTick: `bool flag = parent.GetComp<CompCanBeDormant>()?.Awake ??
    // true; if (points > 0f && flag && parent.Spawned) Spawn();`. This IS
    // the TunnelHiveSpawner-family emergence shape the spec's own S3 text
    // asks to crib, and closer to it than TunnelHiveSpawner/GroundSpawner
    // itself — it is already wired to CompCanBeDormant rather than a fixed
    // timer. RUT_BeastBulge.xml wires it directly; no C# subclass of
    // CompCanBeDormant was written for this pass.
    //
    // What vanilla does NOT provide is this kit's own S2 signal seam (deep
    // digs / greedy pumping waking the beast): RM_CompWorkedLottery's
    // static BeastWakeRequested event (RM_CompWorkedLottery.cs) has no
    // vanilla listener. This small, generic comp is the only new C# the
    // dormancy/emergence side of S3 needs: it relays that event into the
    // NATIVE CompWakeUpDormant.Activate() call, satisfying the item's own
    // "explicit Activate() call from S2's dig lottery" instruction without
    // duplicating anything vanilla already does well. Not Sump-specific —
    // any dormant Thing wanting to listen for a worked-lottery-driven
    // disturbance reuses this comp unchanged.
    public class RM_CompBeastWakeRelay : ThingComp
    {
        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);
            RM_CompWorkedLottery.BeastWakeRequested += OnBeastWakeRequested;
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            RM_CompWorkedLottery.BeastWakeRequested -= OnBeastWakeRequested;
            base.PostDeSpawn(map, mode);
        }

        // No distance/targeting gate — see RUT_BeastBulge.xml's own header
        // for why (this item's own N=1 dormant beast per map has no stated
        // tie-break rule to gate on in the first place; every still-dormant
        // relay-carrying Thing on the signalling map wakes).
        //
        // S1's own tie-in needs no code here, on purpose: RUT_TarBlaze / the
        // moat ignition work through real fire and explosion damage
        // (RM_CompFloodIgniter.cs's own header), which reaches whatever
        // this comp is attached to exactly like any other damage source —
        // through CompWakeUpDormant.PostPostApplyDamage's native
        // wakeUpOnDamage branch, already wired in RUT_BeastBulge.xml.
        // Confirmed, not assumed: PostPostApplyDamage fires from
        // Thing.TakeDamage synchronously, independent of tickerType or any
        // poll — a second, parallel signal path from S1 would be a
        // redundant hook onto a cause the stock field already covers.
        private void OnBeastWakeRequested(Map map, IntVec3 cell, int stratumDepth)
        {
            if (!parent.Spawned || parent.Map != map)
            {
                return;
            }
            parent.GetComp<CompWakeUpDormant>()?.Activate(null);
        }
    }
}
