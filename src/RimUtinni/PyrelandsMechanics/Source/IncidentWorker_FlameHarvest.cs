using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;
using Verse.AI.Group;

namespace RimMandrake.Utinni.PyrelandsMechanics
{
    /// <summary>
    /// PYRELANDS_MECHANICS_1, mechanism 5a — the flame harvest
    /// (the_pyrelands.md §8: "controlled burns on the Tribes' schedule; the
    /// burn-line walked for scorch-fruit").
    ///
    /// The player already has the harvest: scorch-fruit seeds in burning cells
    /// through mandrake.rm.pyrelands's own FireEcologyHook, and anyone can walk
    /// the line and pick it. What was owed here is the OTHER half of §8 — that
    /// the Tribes are the fire's farmers and turn out to work a live burn. So this
    /// incident is not a threat and not a gift: it is the biome's owners walking
    /// past you into the smoke, on a map where a burn is already standing.
    ///
    /// It cannot fire without a burn (MapComponent_BurnLine.FireCount), which is
    /// what makes it read as harvesting rather than as a random visit — and it
    /// cannot fire while the Tribes are hostile, because then the thing that
    /// arrives is IncidentWorker_FireRaid instead.
    ///
    /// The party is a vanilla peaceful pawn group under LordJob_TravelAndExit,
    /// pointed at the burn's centroid: they walk to the fire, and when they get
    /// there they leave. No trade, no quest hook, no scorch-fruit handout — the
    /// sheet asks for the Tribes to be SEEN farming the fire, and anything more
    /// would pre-empt ECONOMY_TRADE_SWEEP_1.
    /// </summary>
    public class IncidentWorker_FlameHarvest : IncidentWorker
    {
        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms) || !(parms.target is Map map))
            {
                return false;
            }

            MapComponent_BurnLine watch = MapComponent_BurnLine.For(map);
            if (watch == null || !watch.IsPyrelandsMap)
            {
                return false;
            }
            if (!watch.AnyBurn || watch.FireCount < PyrelandsTuning.FlameHarvestMinFires)
            {
                return false;
            }

            Faction tribes = PyrelandsFactions.TribesOrNull();
            return tribes != null && !tribes.HostileTo(Faction.OfPlayer);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map))
            {
                return false;
            }

            MapComponent_BurnLine watch = MapComponent_BurnLine.For(map);
            if (watch == null || !watch.AnyBurn)
            {
                return false;
            }

            Faction tribes = PyrelandsFactions.TribesOrNull();
            if (tribes == null || tribes.HostileTo(Faction.OfPlayer))
            {
                return false;
            }

            if (!RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 entry, map, CellFinder.EdgeRoadChance_Neutral))
            {
                return false;
            }

            PawnGroupMakerParms groupParms = new PawnGroupMakerParms
            {
                groupKind = PawnGroupKindDefOf.Peaceful,
                tile = map.Tile,
                faction = tribes,
                points = PyrelandsTuning.FlameHarvestPoints,
            };

            List<Pawn> harvesters = PawnGroupMakerUtility.GeneratePawns(groupParms).ToList();
            if (harvesters.Count == 0)
            {
                return false;
            }

            for (int i = 0; i < harvesters.Count; i++)
            {
                IntVec3 cell = CellFinder.RandomClosewalkCellNear(entry, map, 8);
                GenSpawn.Spawn(harvesters[i], cell, map);
            }

            // Walk to the burn, then leave. The Lord is what keeps them together
            // and what makes them exit on arrival instead of milling about — the
            // plain Goto-with-exitMapOnArrival shape used for the animal migration
            // incident does not hold a humanlike group together.
            LordMaker.MakeNewLord(tribes, new LordJob_TravelAndExit(watch.BurnCenter), map, harvesters);

            SendStandardLetter(
                "RUT_FlameHarvest".Translate(),
                "RUT_FlameHarvestDesc".Translate(tribes.Name),
                LetterDefOf.NeutralEvent,
                parms,
                harvesters[0]);

            return true;
        }
    }
}
