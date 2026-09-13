using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F3 spike. RUT_MirrorList's use-effect: reads
    // F1's per-pool agitation state and applies a timed "flagged" window —
    // Sporefall sells the list, the list is a snapshot, agitation moves on
    // (the_fever_wood.md §8).
    //
    // Engine seam CONFIRMED, closing the spec's own ❓: CompUseEffect is a
    // real abstract ThingComp base (RimWorld/CompUseEffect.cs) with a
    // virtual DoEffect(Pawn usedBy) — the assumed base-class route in the
    // spec was correct, no correction needed here. The overlay-draw seam
    // the spec also flagged (MapComponentUpdate/MapComponentOnGUI,
    // Verse/MapComponent.cs:12,20) is real too, both virtual; actually
    // drawing the warning ring is deferred to the full build (screen-space
    // cell drawing is presentation work, not an engine-fact question).
    //
    // SPIKE SCOPE: this proves the use-effect fires and writes a flagged-
    // until-tick window that F1's agitation store can carry (reusing
    // RaiseAgitation's amount/duration as the "flagged" signal rather than
    // adding a second parallel per-cell array — the mirror list IS a
    // snapshot of agitation, so it does not need its own storage). NOT
    // done here: the trader-kind XML stocking RUT_MirrorList, and the
    // actual overlay draw call.
    public class RM_CompUseEffect_RevealHazards : CompUseEffect
    {
        private const int IntelValidityTicks = 60000 * 15; // INVENTED, kit spec: 15 days

        public override void DoEffect(Pawn usedBy)
        {
            base.DoEffect(usedBy);
            Map map = usedBy.Map;
            if (map == null)
            {
                return;
            }
            RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null)
            {
                return; // not a Fever Wood map — the item is a harmless no-op elsewhere
            }
            // Refresh the flagged window on every currently-agitated pool
            // this map already knows about, centered on the using pawn's
            // position as the query point (the full build reads the
            // component's own registry rather than re-deriving cells here).
            tenant.RaiseAgitation(usedBy.Position, tenant.AgitationAt(usedBy.Position), IntelValidityTicks, radius: 40f);
        }
    }
}
