using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Utinni.UtinniPatches
{
    // ZERSIUM_FORGE_BIOME_1 — zersium's only source on the planet: a few small lumps of
    // RSW_MineableZersium scattered into natural rock on Forge maps (owner, question cards
    // 2026-10-09: "a rare local ore in ONE home biome", that biome The Forge). RSW_MineableZersium
    // has scatter and deep commonality 0, so this GenStep is the whole placement.
    //
    // Vanilla GenStep_ScatterLumpsMineable with forcedDefToScatter (the same field Core uses for
    // glacier ore and Odyssey for obsidian), gated on map.Biome and the Mod Settings toggle. The
    // def is registered on every player map generator and gates itself — the
    // RUT_FoundryTowerScatter "global registration, self-gating" pattern.
    //
    // Lives in the Utinni layer because the RimMandrake Forge biome may not name Star Wars content
    // (biome_mod_architecture.md §7 Q11); the mineral itself is RSW tier (mandrake.rsw.armoury).
    public class RUT_GenStep_ZersiumForgeLumps : GenStep_ScatterLumpsMineable
    {
        // PROVISIONAL: guaranteed lumps per Forge map (no ruling); set in the GenStepDef.
        public int minLumps = 2;
        public List<BiomeDef> allowedBiomes = new List<BiomeDef>();

        public override int SeedPart => 734119052;

        // The Mod Settings switch for this step; the phrikite subclass swaps it.
        protected virtual bool Enabled => UtinniPatchesSettings.zersiumForgeEnabled;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!Enabled || !Allowed(map, allowedBiomes))
            {
                return;
            }
            // The vanilla loop draws random cells (CellFinderLoose.TryFindRandomNotEdgeCellWith, a bounded number
            // of tries) and RETURNS on the first miss, so a Forge map whose natural rock is sparse could place 0
            // lumps. Guarantee minLumps by falling back to an exhaustive scan of eligible rock cells, and count
            // only lumps that actually spawned ore (IrregularLump can return 0 cells on a Caves cell).
            minSpacing = 5f;
            warnOnFail = false;
            int want = System.Math.Max(CalculateFinalCount(map), minLumps);
            int placed = 0;
            ThingDef ore = forcedDefToScatter;
            var cands = new List<IntVec3>();
            for (int i = 0; i < want; i++)
            {
                IntVec3 c;
                bool found = TryFindScatterCell(map, out c);
                if (!found)
                {
                    if (cands.Count == 0)
                    {
                        foreach (IntVec3 cell in map.AllCells)
                        {
                            if (!cell.CloseToEdge(map, 5) && CanScatterAt(cell, map)) cands.Add(cell);
                        }
                        cands.Shuffle();
                    }
                    while (cands.Count > 0 && !found)
                    {
                        c = cands[cands.Count - 1];
                        cands.RemoveAt(cands.Count - 1);
                        found = CanScatterAt(c, map);
                        if (found) { ScatterAtAndCount(c, map, parms, ref placed); usedSpots.Add(c); }
                    }
                    if (!found) break;
                    continue;
                }
                ScatterAtAndCount(c, map, parms, ref placed);
                usedSpots.Add(c);
            }
            usedSpots.Clear();
            if (placed < minLumps)
            {
                Log.Warning("[" + GetType().Name + "] placed " + placed + " of minimum " + minLumps + " lumps on a gated map (no eligible natural rock?).");
            }
        }

        private void ScatterAtAndCount(IntVec3 c, Map map, GenStepParams parms, ref int placed)
        {
            ScatterAt(c, map, parms);
            if (recentLumpCells.Count > 0) placed++;
        }

        public static bool Allowed(Map map, List<BiomeDef> biomes)
        {
            return map != null && map.Biome != null && !biomes.NullOrEmpty() && biomes.Contains(map.Biome);
        }
    }

    // ASTEROID_DESERT_ORES_1 — phrikite's only placement: a few small lumps of RSW_MineablePhrikite in the natural
    // rock of ONE desert biome (RM_Stillsand and its twin RUT_ExtremeDesert; PROVISIONAL, owner question open).
    // Same gate-and-guarantee logic as the zersium step, own seed and own Mod Settings switch.
    public class RUT_GenStep_PhrikiteDesertLumps : RUT_GenStep_ZersiumForgeLumps
    {
        public override int SeedPart => 734119077;
        protected override bool Enabled => UtinniPatchesSettings.phrikiteDesertEnabled;
    }

    // Bridge proof (jawa/static_call): the gate's verdict for the current map, and the count of
    // zersium ore cells on it. "allowed=<bool> enabled=<bool> biome=<defName> cells=<n>".
    public static class RUT_ZersiumForgeProof
    {
        public static string Probe(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "no map";
            }
            GenStepDef gs = DefDatabase<GenStepDef>.GetNamedSilentFail("RUT_ZersiumForgeLumps");
            RUT_GenStep_ZersiumForgeLumps step = gs?.genStep as RUT_GenStep_ZersiumForgeLumps;
            ThingDef ore = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_MineableZersium");
            if (step == null || ore == null)
            {
                return "no defs";
            }
            bool allowed = RUT_GenStep_ZersiumForgeLumps.Allowed(map, step.allowedBiomes);
            return "allowed=" + allowed + " enabled=" + UtinniPatchesSettings.zersiumForgeEnabled
                 + " biome=" + map.Biome.defName + " cells=" + map.listerThings.ThingsOfDef(ore).Count;
        }
    }

    // Same probe for phrikite: "allowed=<bool> enabled=<bool> biome=<defName> cells=<n>".
    public static class RUT_PhrikiteDesertProof
    {
        public static string Probe(string unused)
        {
            Map map = Find.CurrentMap;
            if (map == null)
            {
                return "no map";
            }
            GenStepDef gs = DefDatabase<GenStepDef>.GetNamedSilentFail("RUT_PhrikiteDesertLumps");
            RUT_GenStep_PhrikiteDesertLumps step = gs?.genStep as RUT_GenStep_PhrikiteDesertLumps;
            ThingDef ore = DefDatabase<ThingDef>.GetNamedSilentFail("RSW_MineablePhrikite");
            if (step == null || ore == null)
            {
                return "no defs";
            }
            bool allowed = RUT_GenStep_ZersiumForgeLumps.Allowed(map, step.allowedBiomes);
            return "allowed=" + allowed + " enabled=" + UtinniPatchesSettings.phrikiteDesertEnabled
                 + " biome=" + map.Biome.defName + " cells=" + map.listerThings.ThingsOfDef(ore).Count;
        }
    }
}
