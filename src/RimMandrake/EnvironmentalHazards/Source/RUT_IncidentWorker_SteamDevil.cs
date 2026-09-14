using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M3 remainder build (greentide_kit_spec.md M3:
    // "Spawned by an IncidentDef weighted into the biome and, rarely, by the
    // Roil condition itself"). Only the plain IncidentDef route ships this
    // pass — checked before build: RUT_RoilWeather.xml/RUT_RoilLock.xml
    // exist on disk but uncommitted, still being actively built by another
    // window's M4/M5 pass this same session (GREENTIDE_MECHANICS_2's own
    // build-order note), so M4 has not landed as far as this item's own
    // ledger is concerned. Per the build brief's own explicit fallback for
    // exactly this situation, the rare Roil-triggered spawn hook is owed,
    // not wired — wiring it now would mean hooking a condition class that
    // might still change shape before that window's own commit lands.
    //
    // RUT_-prefixed content class in the shared EnvironmentalHazards
    // assembly, same posture as RUT_IncidentWorker_ContagionProbe/
    // RUT_IncidentWorker_Breaklight/RUT_IncidentWorker_WalkerSurfacing.
    public class RUT_IncidentWorker_SteamDevil : IncidentWorker
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

            ThingDef steamDevilDef = DefDatabase<ThingDef>.GetNamedSilentFail("RUT_SteamDevil");
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
                "RUT_SteamDevilAppears".Translate(),
                "RUT_SteamDevilAppearsDesc".Translate(),
                LetterDefOf.NeutralEvent,
                parms,
                new TargetInfo(cell, map));

            return true;
        }

        // "Spins off the river" per the spec's own player-experience line —
        // spawned directly on a water cell (Ethereal, no pathing/standing
        // constraint applies to it, same as vanilla Tornado spawning
        // anywhere InBounds).
        private static bool TryFindRiverCell(Map map, out IntVec3 result)
        {
            result = CellFinderLoose.RandomCellWith(
                (IntVec3 c) => c.InBounds(map) && (c.GetTerrain(map)?.IsWater ?? false),
                map,
                SampleCells);
            return result.IsValid;
        }
    }
}
