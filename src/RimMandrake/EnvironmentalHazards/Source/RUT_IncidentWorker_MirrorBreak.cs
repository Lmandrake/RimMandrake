using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // FEVER_WOOD_MECHANICS_1 F2 spike. A rare event on a random registered
    // pool: ripple + dread (flecks/sound are content, not this class's
    // concern) plus the silence beat and a 3-day agitation raise that F1
    // reads as an elevated strike rate and F3 reports as "moved lately".
    //
    // Silence-cue reuse (sibling class, per the sheet's cross-flow ledger
    // and the kit spec's "sibling reuses" list): RimMandrake.
    // CreatureBehaviors.RM_MapComponent_SilenceCue exists but its current
    // trigger is scoped to a carrying pawn's PredatorHunt job near a
    // colonist (RM_SilenceAuraExtension) — it has no public API for "hush
    // now" from an unrelated event. SPIKE SCOPE: this class proves the
    // IncidentWorker seam (TryExecuteWorker, RimWorld/IncidentWorker.cs:289,
    // confirmed real and protected virtual) and calls into F1's agitation
    // write path; wiring an actual hush call is owed to either extending
    // SilenceCue with a public TriggerHush(int durationTicks) entry point,
    // or the CreatureBehaviors/EnvironmentalHazards assembly split being
    // resolved so one can reference the other — a packaging question, not
    // an engine-fact question this spike needed to resolve.
    public class RUT_IncidentWorker_MirrorBreak : IncidentWorker
    {
        private const int AgitationDurationTicks = 60000 * 3; // INVENTED, kit spec: 3 days

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
            return true;
        }
    }
}
