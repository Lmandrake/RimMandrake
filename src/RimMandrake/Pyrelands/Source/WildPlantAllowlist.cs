using System;
using System.Collections.Generic;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    // PYRELANDS_FLORA_LEAK_1 — runtime enforcement, not a per-def patch.
    //
    // MEASURED 2026-09-18 (owner spotted it live): AB_SessileMechanoid
    // (Alpha Biomes) and AB_GiantStikehr (Alpha Biomes) were growing wild on
    // Pyrelands maps despite Pyrelands.xml's <wildPlants> listing only the
    // two RM_FE_ grasses. TRACED (RimSage source reads, 2026-09-19): NEITHER
    // def carries a `plant.wildBiomes` entry naming Pyrelands, and neither
    // is referenced by any TileMutatorDef.AdditionalWildPlants in Alpha
    // Biomes — both intruders live only in their OWN dedicated biomes'
    // (AB_MechanoidIntrusion, AB_RockyCrags) <wildPlants> lists. The actual
    // route is more general than either guess: RimWorld/WildPlantSpawner.cs
    // CalculatePlantsWhichCanGrowAt() builds its candidate list from
    // `map.BiomeAt(c).AllWildPlants` (per-CELL biome — Tile.Biomes can yield
    // a SECONDARY biome whenever a TileMutatorWorker_MixedBiome-family
    // mutator applies, and MixedBiomeComp.GetBiomeAt then hands whole
    // patches of the map to that secondary biome's own, unrelated wildPlants
    // roster) plus `WildPlantSpawner.MutatorWildPlants` (any tile mutator's
    // AdditionalWildPlants(), biome-independent by design). A heavily
    // biome-modded stack (m00nl1ght.geologicallandforms +
    // .biometransitions, kopp.biomecompatibilityproject, sarg.alphabiomes,
    // multiple biome-expansion mods, all active in the owner's full list)
    // gives this machinery every opportunity to hand a Pyrelands map a
    // foreign biome's flora, and Pyrelands' own <wildPlants> list has no way
    // to filter either path — that list is only ever consulted for
    // Pyrelands' OWN AllWildPlants property, never for what a DIFFERENT
    // biome or mutator injects into `outPlants`.
    //
    // So a per-def PatchOperationRemove strips nothing here (there is
    // nothing on the intruding defs themselves to strip) and would need
    // re-deriving, mod by mod, for every future flora def that reaches
    // Pyrelands the same way — the exact "multiplies across every flora
    // mod" the filer warned about. Runtime enforcement closes the whole
    // class at once: whatever gets a candidate into `outPlants` — a
    // secondary biome, a mutator, a wildBiomes entry, a future mechanism —
    // this postfix removes anything off the allowlist before it can be
    // chosen, for any map whose PRIMARY biome is Pyrelands. It does not
    // touch any other biome, including a map where Pyrelands is merely the
    // SECONDARY biome of a mixed tile (that map's owner biome's own rules
    // apply there, unchanged).
    [StaticConstructorOnStartup]
    public static class WildPlantAllowlistHookMod
    {
        static WildPlantAllowlistHookMod()
        {
            var h = new Harmony("mandrake.rm.pyrelands.wildplantallowlist");
            var target = AccessTools.Method(typeof(WildPlantSpawner), "CalculatePlantsWhichCanGrowAt");
            if (target == null)
            {
                Log.Error("[RimMandrake.Pyrelands] pyrelands-wildplant-allowlist: "
                          + "TARGET METHOD NOT FOUND — a game update renamed WildPlantSpawner."
                          + "CalculatePlantsWhichCanGrowAt. The Pyrelands flora leak is NOT guarded "
                          + "this session.");
                return;
            }
            try
            {
                h.Patch(target, postfix: new HarmonyMethod(typeof(Patch_EnforcePyrelandsWildPlantAllowlist), "Postfix"));
                Log.Message("[RimMandrake.Pyrelands] pyrelands-wildplant-allowlist: "
                            + "armed; only RM_FE_ grasses may spawn wild on a Pyrelands map, "
                            + "however a foreign plant reaches the candidate list.");
            }
            catch (Exception e)
            {
                Log.Error("[RimMandrake.Pyrelands] pyrelands-wildplant-allowlist: "
                          + "patch FAILED, rule NOT in effect — " + e.Message);
            }
        }
    }

    public static class Patch_EnforcePyrelandsWildPlantAllowlist
    {
        private const string PyrelandsDefName = "RM_Pyrelands";

        // Kept in step with Pyrelands.xml's own <wildPlants> list by hand —
        // this IS that list's runtime backstop, not a second source of
        // truth to drift from it. Scorch-fruit is deliberately absent: it
        // never spawns through WildPlantSpawner (FireEcologyHook.cs seeds it
        // directly on a burned cell), so it never reaches this method.
        private static readonly HashSet<string> Allowlist = new HashSet<string>
        {
            "RM_FE_Plant_EmberGrass",
            "RM_FE_Plant_Quickgrass",
        };

        // outPlants is mutated in place by the original method; Harmony
        // hands a postfix the same List<ThingDef> reference, so removing
        // from it here is visible to the caller with no return-value dance.
        // ___map reaches the private `map` field on the WildPlantSpawner
        // instance (Harmony's underscore-prefixed field-access convention).
        public static void Postfix(List<ThingDef> outPlants, Map ___map)
        {
            try
            {
                if (!RM_PyrelandsSettings.pyrelandsEnabled || !RM_PyrelandsSettings.wildPlantAllowlistEnabled) return;
                if (___map == null || outPlants == null || outPlants.Count == 0) return;
                if (___map.Biome == null || ___map.Biome.defName != PyrelandsDefName) return;

                for (int i = outPlants.Count - 1; i >= 0; i--)
                {
                    if (!Allowlist.Contains(outPlants[i].defName))
                    {
                        outPlants.RemoveAt(i);
                    }
                }
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] pyrelands-wildplant-allowlist: "
                                + e.Message, 0x46E03);
            }
        }
    }
}
