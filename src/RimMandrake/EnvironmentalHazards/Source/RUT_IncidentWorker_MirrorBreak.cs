using RimMandrake.CreatureBehaviors;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F2. A rare event on a random registered
    // pool: ripple + dread (flecks/sound are content, not this class's
    // concern) plus the silence beat and a 3-day agitation raise that F1
    // reads as an elevated strike rate and F3 reports as "moved lately".
    //
    // Silence-cue reuse (sibling class, per the sheet's cross-flow ledger
    // and the kit spec's "sibling reuses" list): RimMandrake.
    // CreatureBehaviors.RM_MapComponent_SilenceCue's PredatorHunt trigger
    // does not fit an unrelated map event, so it now carries a second,
    // public entry point (TriggerHush) built for exactly this call —
    // WIRED this pass. mandrake.rm.environmentalhazards now depends on
    // mandrake.rm.creaturebehaviors (About.xml modDependencies/loadAfter),
    // same shape mandrake.rm.shipvermin's own cross-reference already
    // ships with.
    public class RUT_IncidentWorker_MirrorBreak : IncidentWorker
    {
        private const int AgitationDurationTicks = 60000 * 3; // INVENTED, kit spec: 3 days

        // The silence beat's own length — reused verbatim from
        // RM_SilenceAuraExtension's shipped default (900 ticks,
        // RM_Greentide_FaunaHooks.xml), not a new invented number: the kit
        // spec's own words are "the same mechanic pointed at water", so
        // this pass takes the sibling's existing tuning rather than
        // picking a second one for the same beat.
        private const int SilenceBeatDurationTicks = 900;

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            RUT_MapComponent_TheTenant tenant = map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null)
            {
                return false; // not a Fever Wood map (no registered pools) — no-op, never errors
            }

            IntVec3 seed;
            if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(0, (IntVec3 c) => c.InBounds(map) && c.GetTerrain(map)?.GetModExtension<RM_LurkingWaterExtension>() != null, map, out seed))
            {
                return false; // no registered pool on this map — nothing to break
            }

            tenant.RaiseAgitation(seed, 1f, AgitationDurationTicks);
            map.GetComponent<RM_MapComponent_SilenceCue>()?.TriggerHush(SilenceBeatDurationTicks);
            return true;
        }
    }
}
