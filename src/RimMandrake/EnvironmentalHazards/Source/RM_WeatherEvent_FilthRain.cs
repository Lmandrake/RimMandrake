using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // SUMP_TAR_LIVING_SYSTEMS_1 part 2 — tar rain. Owner, typed 2026-10-09: "Flowworks supports tar rain but
    // campaign does not. The biome itself does except for the campaign. Correct."
    //
    // A filth rain is a WeatherDef whose eventMakers fire this event: each firing coats a handful of random OPEN-SKY
    // cells with the weather's filth (through RM_TarCoatingUtility, the proven FilthMaker path, so each terrain's own
    // filthAcceptanceMask decides) and gives each pawn standing under open sky a chance to pick a unit up on its body
    // (Pawn_FilthTracker.GainFilth — so tar filth becomes the tarred condition through the existing
    // RM_CarriedFilthHediffExtension, nothing new). The weather sets rainRate 0 on purpose: tar does not douse fire,
    // wet pawns, or fill pits with water.
    //
    // Data on the WeatherDef (RM_FilthRainExtension); an RM_MechanicGateExtension on the same WeatherDef lets the
    // owning biome mod switch the coating off, and intensityKey scales it (RM_MechanicGates.Scale).
    public class RM_FilthRainExtension : DefModExtension
    {
        public ThingDef filthDef;

        // Cells one event tries to coat on a 250x250 map; scaled to the real map area (RM_FilthRainKernel).
        public float cellsPerEvent = 6f;

        // Chance per event that a pawn under open sky gains one unit of filthDef.
        public float pawnFilthChance = 0.1f;

        // RM_MechanicGates scale key multiplying both figures above. Null = 1.
        public string intensityKey;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (filthDef == null || filthDef.filth == null)
            {
                yield return "RM_FilthRainExtension needs a filthDef that is a filth.";
            }
        }
    }

    public class RM_WeatherEvent_FilthRain : WeatherEvent
    {
        private bool fired;

        public RM_WeatherEvent_FilthRain(Map map)
            : base(map)
        {
        }

        public override bool Expired => fired;

        public override void FireEvent()
        {
            fired = true;
            WeatherDef weather = map?.weatherManager?.curWeather;
            RM_FilthRainExtension ext = weather?.GetModExtension<RM_FilthRainExtension>();
            if (ext == null || ext.filthDef == null || !RM_MechanicGates.Enabled(weather))
            {
                return;
            }
            float intensity = RM_MechanicGates.Scale(ext.intensityKey);

            int want = RM_FilthRainKernel.CellsPerEvent(ext.cellsPerEvent, map.Area, intensity);
            if (want > 0)
            {
                List<IntVec3> cells = new List<IntVec3>(want);
                // A bounded number of random draws: roofed cells are skipped, never retried forever.
                for (int tries = 0; tries < want * 4 && cells.Count < want; tries++)
                {
                    IntVec3 c = CellFinder.RandomCell(map);
                    if (!c.Roofed(map))
                    {
                        cells.Add(c);
                    }
                }
                RM_TarCoatingUtility.CoatCells(map, cells, ext.filthDef);
            }

            float p = RM_FilthRainKernel.PawnChance(ext.pawnFilthChance, intensity);
            if (p <= 0f)
            {
                return;
            }
            var pawns = map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn pawn = pawns[i];
                if (pawn.filth != null && !pawn.Position.Roofed(map) && Rand.Chance(p))
                {
                    pawn.filth.GainFilth(ext.filthDef);
                }
            }
        }

        public override void WeatherEventTick()
        {
        }
    }
}
