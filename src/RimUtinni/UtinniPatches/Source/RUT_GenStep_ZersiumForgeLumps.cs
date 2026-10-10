using System.Collections.Generic;
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
        public List<BiomeDef> allowedBiomes = new List<BiomeDef>();

        public override int SeedPart => 734119052;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!UtinniPatchesSettings.zersiumForgeEnabled || !Allowed(map, allowedBiomes))
            {
                return;
            }
            base.Generate(map, parms);
        }

        public static bool Allowed(Map map, List<BiomeDef> biomes)
        {
            return map != null && map.Biome != null && !biomes.NullOrEmpty() && biomes.Contains(map.Biome);
        }
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
}
