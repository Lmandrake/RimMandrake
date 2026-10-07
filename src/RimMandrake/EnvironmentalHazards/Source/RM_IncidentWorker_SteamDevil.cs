using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M3 (greentide_kit_spec.md M3: "Spawned by an IncidentDef weighted into
    // the biome and, rarely, by the Roil condition itself"). This is the IncidentDef route
    // (RM_SteamDevilAppears, mandrake.rm.terminalbiomes); the Roil route is
    // RM_MapComponent_RoilVortexSpawner, which reuses TryFindRiverCell. Renamed from RUT_ by
    // GREENTIDE_BASE_PORT_BUILD_1.
    public class RM_IncidentWorker_SteamDevil : IncidentWorker
    {
        private const int SampleCells = 60; // bounded sample, matching RUT_IncidentWorker_WalkerSurfacing's own posture — not a full-map scan

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms) || !(parms.target is Map map))
            {
                return false;
            }

            if (!RM_EnvironmentalHazardsSettings.steamDevilEnabled)
            {
                return false; // mod option: steam devils disabled
            }

            return map.Biome != null && map.Biome.defName == "RM_Greentide";
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            if (!(parms.target is Map map))
            {
                return false;
            }

            ThingDef steamDevilDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SteamDevil");
            if (steamDevilDef == null)
            {
                return false; // content not deployed — never a hard error over it, same posture as RUT_IncidentWorker_ContagionProbe
            }

            if (!TryFindRiverCell(map, out IntVec3 cell))
            {
                return false; // no water on this map — not a Greentide river map, quiet no-op
            }

            GenSpawn.Spawn(steamDevilDef, cell, map);

            SendStandardLetter(
                "RM_SteamDevilAppears".Translate(),
                "RM_SteamDevilAppearsDesc".Translate(),
                LetterDefOf.NeutralEvent,
                parms,
                new TargetInfo(cell, map));

            return true;
        }

        // "Spins off the river" per the spec's own player-experience line —
        // spawned directly on a water cell (Ethereal, no pathing/standing
        // constraint applies to it, same as vanilla Tornado spawning
        // anywhere InBounds). internal, not private: reused verbatim by
        // RM_MapComponent_RoilVortexSpawner (GREENTIDE_MECHANICS_2's Roil-
        // condition spawn route) so both routes pick a spawn cell the same
        // way rather than duplicating the sampling logic.
        internal static bool TryFindRiverCell(Map map, out IntVec3 result)
        {
            result = CellFinderLoose.RandomCellWith(
                (IntVec3 c) => c.InBounds(map) && (c.GetTerrain(map)?.IsWater ?? false),
                map,
                SampleCells);
            return result.IsValid;
        }
    }
}
