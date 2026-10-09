using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_PANE_STRIKE_1 — danger pass D1, "Veil-fall pane strike: the
    // sky sheds." See RM_VeilFallIncoming.xml's header for why this class
    // needs no Skyfaller subclass and no bespoke footprint cell-finder:
    // CellFinderLoose.TryFindSkyfallerCell already walks the full
    // GenAdj.OccupiedRect for the skyfaller ThingDef's own <size>, and
    // Skyfaller.Impact() already runs the explosion + spawns <spawnThing>
    // on its own. The one thing this class MUST override is vanilla's
    // default steer-away-from-colonists behavior — §5 C6 (ruled): "it can
    // kill outright; the ~15 s shadow warning is the fairness," so the
    // strike must be allowed to land on top of a pawn, not avoid one.
    public class RM_IncidentWorker_PaneStrike : IncidentWorker
    {
        // minDistToEdge kept small (6, vs. vanilla meteorite's 10): these
        // sea-floor pocket maps are small, and D1's own text ("the strike
        // zone is random ... a colony strung out along a chained lamp
        // field is exposed") wants the whole worked floor in range, not
        // just its interior.
        private const int MinDistToEdge = 6;

        // TERMINAL_SETTINGS_CONSUMERS_WIRE_1: the Frequency slider scales the whole-pane strike too, not only litter.
        public override float BaseChanceThisGame => base.BaseChanceThisGame * RM_TerminalBiomesSettings.twilightPaneStrikeFrequency;

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!RM_TerminalBiomesSettings.TwilightPaneStrikeActive)
            {
                return false;
            }
            Map map = (Map)parms.target;
            return TryFindStrikeCell(map, out _);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            if (!TryFindStrikeCell(map, out IntVec3 cell))
            {
                return false;
            }
            SkyfallerMaker.SpawnSkyfaller(RM_VeilFallDefOf.RM_VeilFallIncoming, cell, map);
            SendWarningLetter(map, cell);
            return true;
        }

        private static bool TryFindStrikeCell(Map map, out IntVec3 cell)
        {
            // avoidColonistsIfExplosive/alwaysAvoidColonists BOTH false —
            // deliberate. Vanilla's own default (avoidColonistsIfExplosive:
            // true) exists precisely to steer meteors away from colonists;
            // the ruling for THIS incident is the opposite.
            return CellFinderLoose.TryFindSkyfallerCell(
                RM_VeilFallDefOf.RM_VeilFallIncoming,
                map,
                TerrainAffordanceDefOf.Light,
                out cell,
                MinDistToEdge,
                default(IntVec3),
                -1,
                allowRoofedCells: true,
                allowCellsWithItems: false,
                allowCellsWithBuildings: false,
                colonyReachable: false,
                avoidColonistsIfExplosive: false,
                alwaysAvoidColonists: false);
        }

        private void SendWarningLetter(Map map, IntVec3 cell)
        {
            Letter letter = LetterMaker.MakeLetter(
                "RM_VeilFallPaneStrikeLabel".Translate(),
                "RM_VeilFallPaneStrikeText".Translate(),
                LetterDefOf.ThreatBig,
                new TargetInfo(cell, map));
            Find.LetterStack.ReceiveLetter(letter);
        }
    }
}
