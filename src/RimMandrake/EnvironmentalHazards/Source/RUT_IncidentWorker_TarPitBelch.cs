using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_BELCH_EVENT_1. Owner ruling 2026-09-24, typed verbatim: "There
    // should also occasionally be a random event when a tar pit just belches
    // a huge amount of tar out all over the local terrain."
    //
    // SCOPE NOTE, read before extending this class: a later same-day ledger
    // note on this item re-frames the belch's EVENTUAL shape as a FlowWorks
    // flood pulse whose fronts cool to walkable glass, full rulings on
    // SUMP_TAR_HYDROLOGY_1. That item owns the whole canal-work/fire-network/
    // Deep-Black-mere FlowWorks integration for the tar biome, and none of
    // its engineering exists yet (RM_Tar carries no pulse-spread or glass-
    // cooling code today — those are that item's own "engineering-tier
    // questions, build's discretion"). This class ships the scenario-scoped
    // v1 the owner's own words describe: an occasional incident that finds
    // an existing tar pit (RM_TarDeep/RM_TarShallow terrain, already
    // generated on Sump maps via LIQUID_TYPES_MOD_1) and coats the
    // surrounding ground in tar filth, reusing RM_TarCoatingUtility
    // (SUMP_TAR_NASTINESS_1 S1) exactly as that item's own header names this
    // class as its intended first consumer. When SUMP_TAR_HYDROLOGY_1 builds
    // the real flood-pulse/glass-front mechanism, its own build should
    // replace this class's coating call (find epicenter -> flood pulse)
    // without needing to touch the IncidentDef, the settings toggle, or the
    // biome restriction below — the trigger/anchor shape stays the same.
    public class RUT_IncidentWorker_TarPitBelch : IncidentWorker
    {
        // Bounded sample, not a full-map scan — same posture
        // RUT_IncidentWorker_WalkerSurfacing already uses in this assembly
        // for "find one cell of a particular terrain somewhere on the map."
        private const int MaxSampleTries = 300;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            if (!RM_EnvironmentalHazardsSettings.tarBelchEnabled)
            {
                return false;
            }
            Map map = parms.target as Map;
            return map != null && TryFindTarPitCell(map, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (map == null || !TryFindTarPitCell(map, out IntVec3 epicenter))
            {
                return false; // no tar pit on this map — not a no-op bug, just nothing to belch
            }

            ThingDef tarFilth = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_Tar");
            if (tarFilth == null)
            {
                return false; // LIQUID_TYPES_MOD_1 content missing/renamed — refuse rather than crash
            }

            // "a huge amount of tar... all over the local terrain": a wide,
            // settings-tunable radius and a thick coat. thicknessPerCell 3 is
            // this pass's own INVENTED-BUILD constant, deliberately thicker
            // than a beast's own tracking splash (RM_Comp_TarCoatingSource's
            // own default of 1) since this is meant to read as a real event,
            // not ambient nastiness.
            int coated = RM_TarCoatingUtility.CoatRadius(
                map,
                epicenter,
                RM_EnvironmentalHazardsSettings.tarBelchRadius,
                tarFilth,
                thicknessPerCell: 3);

            if (coated == 0)
            {
                return false; // every cell in range refused the filth (e.g. all bare rock) — no-op, not a broken incident
            }

            Find.LetterStack.ReceiveLetter(
                "RUT_TarPitBelchLabel".Translate(),
                "RUT_TarPitBelchText".Translate(),
                LetterDefOf.NegativeEvent,
                new TargetInfo(epicenter, map));

            return true;
        }

        private static bool TryFindTarPitCell(Map map, out IntVec3 result)
        {
            result = CellFinderLoose.RandomCellWith(c => IsTarPit(c, map), map, MaxSampleTries);
            return result.IsValid;
        }

        private static bool IsTarPit(IntVec3 c, Map map)
        {
            if (!c.InBounds(map))
            {
                return false;
            }
            TerrainDef terrain = c.GetTerrain(map);
            return terrain != null && (terrain.defName == "RM_TarDeep" || terrain.defName == "RM_TarShallow");
        }
    }
}
