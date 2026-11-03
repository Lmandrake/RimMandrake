using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Stillsand
{
    /// <summary>
    /// HORIZON_CARAVAN_VANILLA_REFUSES_1: why does a vanilla TraderCaravanArrival refuse on this map? A static_call surface
    /// (validation.py horizon chain) that runs the engine's OWN predicates, read-only, instead of guessing.
    ///
    /// The cause found 2026-11-02 (decompiled 1.6): canFireNow true means at least one faction passed
    /// IncidentWorker_TraderCaravanArrival.FactionCanBeGroupSource, so "no trader faction" is ruled out; TryExecute then failed
    /// at SpawnPawns == 0, because PawnGroupKindWorker_Trader.CanGenerateFrom on a valid tile demands a carrier whose race is in
    /// the tile biome's allowedPackAnimals, and RM_Stillsand listed only RM_Vaalok, which no vanilla trader group carried.
    /// RM_TraderCarriers_Stillsand.xml (2026-10-11) gives every trader group RM_Vaalok. This probe reads both halves live.
    /// </summary>
    public static class RM_StillsandTraderProbe
    {
        /// <summary>"-" -&gt; one line: "TRADERS biome=defName entryCell=bool source=n desperate=n generable=n | rows",
        /// a row per non-player faction with trader kinds: "defName:src=bool,desp=bool,carrierAllowed=bool,gen=bool".
        /// generable counts factions that are a group source (normal or desperate) AND have a Trader group the engine
        /// would generate here; 0 means a vanilla trade caravan cannot arrive on this map.</summary>
        public static string Report(string arg)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "REFUSED: no current map";
            }
            IncidentWorker_PawnsArrive worker = IncidentDefOf.TraderCaravanArrival.Worker as IncidentWorker_PawnsArrive;
            if (worker == null)
            {
                return "REFUSED: TraderCaravanArrival's worker is " + IncidentDefOf.TraderCaravanArrival.Worker?.GetType().Name;
            }
            BiomeDef biome = map.Biome;
            bool entry = RCellFinder.TryFindRandomPawnEntryCell(out IntVec3 _, map, CellFinder.EdgeRoadChance_Neutral);
            int source = 0, desperate = 0, generable = 0;
            List<string> rows = new List<string>();
            foreach (Faction f in Find.FactionManager.AllFactions)
            {
                if (f.IsPlayer || f.def.caravanTraderKinds.NullOrEmpty())
                {
                    continue;
                }
                IncidentParms parms = new IncidentParms { target = map };
                bool src = worker.FactionCanBeGroupSource(f, parms, false);
                bool desp = !src && worker.FactionCanBeGroupSource(f, parms, true);
                parms.faction = f;
                // ensureCanGenerateAtLeastOnePawn: true, exactly as the engine's SpawnPawns (IncidentWorker_NeutralGroup)
                // builds it. Without it the points stay at IncidentParms' default -1f, below the Trader worker's minimum 0,
                // and PawnGroupMaker.CanGenerateFrom refuses every group: the 2026-11-03 live FAIL was that probe bug.
                PawnGroupMakerParms gp = IncidentParmsUtility.GetDefaultPawnGroupMakerParms(PawnGroupKindDefOf.Trader, parms, true);
                IEnumerable<PawnGroupMaker> traders = (f.def.pawnGroupMakers ?? new List<PawnGroupMaker>())
                    .Where(g => g.kindDef == PawnGroupKindDefOf.Trader);
                BiomeDef tileBiome = Find.WorldGrid[map.Tile].PrimaryBiome;   // what CanGenerateFrom reads, not map.Biome
                bool carrier = traders.Any(g => g.carriers.Any(c => tileBiome.IsPackAnimalAllowed(c.kind.race)));
                bool gen = traders.Any(g => g.CanGenerateFrom(gp));
                if (src) source++;
                if (desp) desperate++;
                if ((src || desp) && gen) generable++;
                rows.Add(f.def.defName + ":src=" + src + ",desp=" + desp + ",carrierAllowed=" + carrier + ",gen=" + gen);
            }
            return "TRADERS biome=" + biome.defName + " entryCell=" + entry + " source=" + source + " desperate=" + desperate
                + " generable=" + generable + " | " + string.Join("; ", rows);
        }
    }
}
