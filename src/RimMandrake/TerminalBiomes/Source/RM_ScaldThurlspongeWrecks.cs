using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // ════════════════════════════════════════════════════════════════════
    // SCALD_UNDERWATER_FLORA_1 — thurlsponge wreck colonisation, the one piece
    // of design/Jawa/worldbuilding/biomes/the_scald_underwater_flora_pass_2026-09-27.md
    // §4 the def pass (09255bb7d) left unbuilt: "They colonize the wrecks for the
    // iron — a hull the pan swallowed wears a coat of them within a generation."
    //
    // Placement only, at map generation (the design names no runtime behaviour):
    // after the Wreckage engine's RM_WreckField_Scald (order 965) has placed the
    // three RUT_ScaldWreck* salvage buildings in the shallow band, ring each one
    // with thurlsponge on the cells touching its footprint. Same host-adjacent
    // shape as RM_GenStep_TwilightFloraDressing (33846bde3), but with its own
    // spawn check: the Twilight helper refuses water terrain and every Scald
    // wreck stands in water.
    //
    // JUDGEMENT CALLS (the design gives no numbers): every wreck is colonised;
    // each touching cell takes a sponge at CellChance; growth 0.5-1.0 because a
    // swallowed hull is old ("within a generation"). Cells must carry the
    // RUT_ScaldShallow tag the wreck field itself validates on.
    //
    // Gated by RM_TerminalBiomesSettings.ScaldThurlspongeWrecksActive. Runs only
    // where RUT_ScaldWreckScatter_Register.xml puts it: the Scald biomes'
    // extraGenSteps, beside the wreck field.
    // ════════════════════════════════════════════════════════════════════
    public class RM_GenStep_ScaldThurlspongeWrecks : GenStep
    {
        private const float CellChance = 0.55f;
        private const string ShallowTag = "RUT_ScaldShallow";
        private static readonly string[] WreckDefs = { "RUT_ScaldWreckHull", "RUT_ScaldWreckTank", "RUT_ScaldWreckFrame" };

        public override int SeedPart => 7302815;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_TerminalBiomesSettings.ScaldThurlspongeWrecksActive)
            {
                return;
            }
            ThingDef sponge = DefDatabase<ThingDef>.GetNamedSilentFail("RM_Thurlsponge");
            if (sponge == null)
            {
                return;
            }

            List<Thing> wrecks = new List<Thing>();
            foreach (string name in WreckDefs)
            {
                ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                if (def != null) wrecks.AddRange(map.listerThings.ThingsOfDef(def));
            }

            foreach (Thing wreck in wrecks)
            {
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(wreck))
                {
                    if (Rand.Chance(CellChance)) TrySpawnSponge(map, sponge, c);
                }
            }
        }

        private static void TrySpawnSponge(Map map, ThingDef def, IntVec3 c)
        {
            if (!c.InBounds(map) || !c.Standable(map) || c.GetEdifice(map) != null || c.GetPlant(map) != null)
            {
                return;
            }
            TerrainDef terrain = c.GetTerrain(map);
            if (terrain?.tags == null || !terrain.tags.Contains(ShallowTag) || !GenSpawn.CanSpawnAt(def, c, map))
            {
                return;
            }
            if (ThingMaker.MakeThing(def) is Plant p)
            {
                p.Growth = Rand.Range(0.5f, 1f);
                GenSpawn.Spawn(p, c, map);
            }
        }
    }
}
