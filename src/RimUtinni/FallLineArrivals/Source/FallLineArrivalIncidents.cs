using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.FallLineArrivals
{
    /// <summary>
    /// FALL_LINE_ARRIVAL_MECHANISM_1 Band A (spec §4): a wreck skyfaller lands near the colony. The
    /// wreck building carries Ship Vermin's RM_CompVerminNest, whose initial burst (2~4 vermin a few
    /// hundred ticks after landing) sends the arrival letter; the nest keeps producing under the shared
    /// cap. Here only a neutral message on the fall — the letter comes with the first vermin (§7).
    /// </summary>
    public class IncidentWorker_FallArrival : IncidentWorker
    {
        private static readonly (string wreck, string incoming, float weight, System.Func<bool> on)[] Kinds =
        {
            ("RUT_FallWreck_Hull", "RUT_FallWreckIncoming_Hull", 1f, () => FallLineArrivalsSettings.wreckHull),
            ("RUT_FallWreck_Cargo", "RUT_FallWreckIncoming_Cargo", 1.2f, () => FallLineArrivalsSettings.wreckCargo),
            ("RUT_FallWreck_Tank", "RUT_FallWreckIncoming_Tank", 0.6f, () => FallLineArrivalsSettings.wreckTank),
        };

        public override float BaseChanceThisGame => base.BaseChanceThisGame * FallLineArrivalsSettings.wreckFrequency;

        private static bool TryPickKind(out ThingDef wreck, out ThingDef incoming)
        {
            wreck = null;
            incoming = null;
            List<(ThingDef w, ThingDef i, float weight)> pool = new List<(ThingDef, ThingDef, float)>();
            foreach (var k in Kinds)
            {
                if (!k.on())
                {
                    continue;
                }
                ThingDef w = DefDatabase<ThingDef>.GetNamedSilentFail(k.wreck);
                ThingDef i = DefDatabase<ThingDef>.GetNamedSilentFail(k.incoming);
                if (w != null && i != null)
                {
                    pool.Add((w, i, k.weight));
                }
            }
            if (pool.Count == 0)
            {
                return false;
            }
            var pick = pool.RandomElementByWeight(p => p.weight);
            wreck = pick.w;
            incoming = pick.i;
            return true;
        }

        private static bool TryFindCell(ThingDef incoming, ThingDef wreck, Map map, out IntVec3 cell)
        {
            return CellFinderLoose.TryFindSkyfallerCell(incoming, map, wreck.terrainAffordanceNeeded, out cell,
                minDistToEdge: 10, allowRoofedCells: false, alwaysAvoidColonists: true);
        }

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            if (!FallLineArrivalsSettings.wreckFallsEnabled || !FallLineGate.Allowed(map))
            {
                return false;
            }
            return TryPickKind(out ThingDef wreck, out ThingDef incoming) && TryFindCell(incoming, wreck, map, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!TryPickKind(out ThingDef wreck, out ThingDef incoming) || !TryFindCell(incoming, wreck, map, out IntVec3 cell))
            {
                return false;
            }
            SkyfallerMaker.SpawnSkyfaller(incoming, wreck, cell, map);
            Messages.Message("Something has come down on the flats.", new TargetInfo(cell, map),
                MessageTypeDefOf.NeutralEvent);
            return true;
        }
    }

    /// <summary>
    /// FALL_LINE_ARRIVAL_MECHANISM_1 Band C (spec §6): one white lab rat, alone, in one escape pod.
    /// Owner 2026-09-20: "actual terrestrial rats might be fun to fall from a ship as a white lab rat."
    /// </summary>
    public class IncidentWorker_LabRatFalls : IncidentWorker
    {
        private const int PodOpenDelayTicks = 180;

        public override float BaseChanceThisGame => base.BaseChanceThisGame * FallLineArrivalsSettings.labRatFrequency;

        private static PawnKindDef Kind => DefDatabase<PawnKindDef>.GetNamedSilentFail("RUT_LabRat");

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            Map map = parms.target as Map;
            return FallLineArrivalsSettings.labRatEnabled && Kind != null && FallLineGate.Allowed(map);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            PawnKindDef kind = Kind;
            if (kind == null)
            {
                return false;
            }
            Pawn rat = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, faction: null,
                context: PawnGenerationContext.NonPlayer, forceGenerateNewPawn: true, allowDowned: false,
                canGeneratePawnRelations: false, allowFood: false, allowAddictions: false));
            IntVec3 spot = DropCellFinder.RandomDropSpot(map);
            // Positional bools as ScavengerEvents' SurvivalPod (canInstaDropDuringInit, leaveSlag,
            // canRoofPunch, forbid, allowFogged).
            DropPodUtility.DropThingsNear(spot, map, new List<Thing> { rat }, PodOpenDelayTicks, false, false, true, false, true, null);
            Find.LetterStack.ReceiveLetter("Specimen",
                "A single escape pod has come down on the flats. It contains one white rat, ear-tagged, in good "
                + "health, and nothing else. Whatever it was part of, it is not any more.",
                LetterDefOf.NeutralEvent, new TargetInfo(spot, map));
            return true;
        }
    }
}
