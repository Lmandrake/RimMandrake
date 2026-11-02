using System;
using System.Collections.Generic;
using System.Linq;
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
    // .biometransitions, kopp.biomecompatibilityproject,
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
    //
    // ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES: stripping alone left a mixed
    // patch bare. Vanilla fills a secondary-biome cell's list from that
    // biome only, so nothing allowlisted is on it, and CheckSpawnWildPlantAt
    // returns false on an empty list. On those cells the postfix supplies
    // the native grasses that can grow there. Their weights already exist:
    // the spawner's commonalities cover every biome in map.Biomes.
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

        // Same two names, resolved once the defs exist.
        private static List<ThingDef> nativeGrasses;

        private static List<ThingDef> NativeGrasses
        {
            get
            {
                if (nativeGrasses == null)
                {
                    var found = new List<ThingDef>();
                    foreach (string name in Allowlist)
                    {
                        ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                        if (def != null) found.Add(def);
                    }
                    nativeGrasses = found;
                }
                return nativeGrasses;
            }
        }

        // outPlants is mutated in place by the original method; Harmony
        // hands a postfix the same List<ThingDef> reference, so changing it
        // here is visible to the caller with no return-value dance.
        // ___map reaches the private `map` field on the WildPlantSpawner
        // instance (Harmony's underscore-prefixed field-access convention).
        // An empty list is not a reason to leave: a mixed patch can arrive
        // empty (a secondary biome with no plant fit for this cell).
        public static void Postfix(IntVec3 c, List<ThingDef> outPlants, bool cavePlants, Map ___map)
        {
            try
            {
                if (!PyrelandsMechanicsGate.On || !RM_PyrelandsSettings.wildPlantAllowlistEnabled) return;
                if (___map == null || outPlants == null) return;
                if (___map.Biome == null || ___map.Biome.defName != PyrelandsDefName) return;

                Map map = ___map;
                RM_FireEcoKernel.ApplyWildAllowlist(outPlants, NativeGrasses, d => Allowlist.Contains(d.defName),
                    d => d.CanEverPlantAt(c, map), !cavePlants && map.BiomeAt(c) != map.Biome);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] pyrelands-wildplant-allowlist: "
                                + e.Message, 0x46E03);
            }
        }
    }

    /// <summary>static_call probe for ALLOWLIST_DIAGNOSE_BARE_MIXED_PATCHES. A Pyrelands tile with a mixed-biome mutator exists only after
    /// the end-of-project paint, so this stages the same state: it hands half the current Pyrelands map to a secondary biome through the
    /// vanilla MixedBiomeMapComponent, reads the real candidate method at up to 20 open cells there with the allowlist off (raw) and on
    /// (after), asks one roofed-for-caves read, then runs the real CheckSpawnWildPlantAt on them. A mixed map's spawner saturates locally
    /// (20-cell radius) and the grass already standing there grew at Pyrelands density, so the probe clears the small plants around one
    /// centre in the staged half and samples inside that clearing; without it every cell reads saturated and nothing can grow.
    /// "MIXEDPATCH cells N | rawForeign N | rawGrass N | afterEmpty N | afterForeign N | afterGrass N | nativeSupplied N | caveGrass N | grown N | grownForeign N | bare N | saturated N | secondary DEF".
    /// rawGrass 0 with afterEmpty 0 and grown > 0 = fixed. The grid and setting are restored, grown plants removed, cleared plants respawned.</summary>
    public static class RM_WildPlantAllowlistProof
    {
        private const string Secondary = "TemperateForest";
        private const float ClearRadius = 36f, SampleRadius = 8f;

        public static string ProofMixedPatch()
        {
            Map map = Find.CurrentMap;
            BiomeDef secondary = DefDatabase<BiomeDef>.GetNamedSilentFail(Secondary);
            if (map == null || secondary == null) return "REFUSED: no map or no " + Secondary;
            if (map.Biome == null || map.Biome.defName != "RM_Pyrelands") return "REFUSED: map biome is " + map.Biome?.defName;
            MixedBiomeMapComponent comp = map.MixedBiomeComp;
            if (comp == null) return "REFUSED: no MixedBiomeMapComponent";
            if (comp.IsMixedBiome) return "REFUSED: this map is already mixed";
            var calc = AccessTools.Method(typeof(WildPlantSpawner), "CalculatePlantsWhichCanGrowAt");
            if (calc == null) return "REFUSED: CalculatePlantsWhichCanGrowAt not found";

            var list = new List<ThingDef>();
            List<ThingDef> Read(IntVec3 cell, bool cave)
            {
                calc.Invoke(map.wildPlantSpawner, new object[] { cell, list, cave, 1f });
                return list;
            }
            bool IsGrass(ThingDef d) => d.defName.StartsWith("RM_FE_Plant_");

            bool wasOn = RM_PyrelandsSettings.wildPlantAllowlistEnabled;
            var grown = new List<Thing>();
            var cleared = new List<KeyValuePair<IntVec3, KeyValuePair<ThingDef, float>>>();
            int rawForeign = 0, rawGrass = 0, afterEmpty = 0, afterForeign = 0, afterGrass = 0, nativeSupplied = 0, caveGrass = 0, cells = 0, bare = 0, saturated = 0;
            try
            {
                var grid = new bool[map.Size.x * map.Size.z];
                for (int i = 0; i < grid.Length; i++) grid[i] = map.cellIndices.IndexToCell(i).x < map.Size.x / 2;
                comp.biomeGrid = grid;
                comp.secondaryBiome = secondary;

                ThingDef ember = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_Plant_EmberGrass");
                var sample = new List<IntVec3>();
                var centre = new IntVec3(map.Size.x / 4, 0, map.Size.z / 2);
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, Math.Min(ClearRadius, map.Size.x / 4f - 1f), true))
                {
                    if (!cell.InBounds(map)) continue;
                    Plant standing = cell.GetPlant(map);
                    if (standing == null || standing.def.plant.IsTree) continue;
                    cleared.Add(new KeyValuePair<IntVec3, KeyValuePair<ThingDef, float>>(cell, new KeyValuePair<ThingDef, float>(standing.def, standing.Growth)));
                    standing.Destroy();
                }
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(centre, SampleRadius, true).InRandomOrder())
                {
                    if (sample.Count >= 20) break;
                    if (!cell.InBounds(map) || map.BiomeAt(cell) != secondary || cell.GetEdifice(map) != null || cell.GetCover(map) != null
                        || cell.GetRoof(map) != null || map.fertilityGrid.FertilityAt(cell) <= 0f || cell.Fogged(map)) continue;
                    if (cell.GetPlant(map) == null && ember != null && ember.CanEverPlantAt(cell, map)) sample.Add(cell);
                }
                cells = sample.Count;

                RM_PyrelandsSettings.wildPlantAllowlistEnabled = false;
                foreach (IntVec3 cell in sample)
                {
                    foreach (ThingDef d in Read(cell, false)) { if (IsGrass(d)) rawGrass++; else rawForeign++; }
                }
                RM_PyrelandsSettings.wildPlantAllowlistEnabled = true;
                foreach (IntVec3 cell in sample)
                {
                    List<ThingDef> after = Read(cell, false);
                    if (after.Count == 0) afterEmpty++;
                    foreach (ThingDef d in after) { if (IsGrass(d)) afterGrass++; else afterForeign++; }
                    foreach (ThingDef d in Read(cell, true)) { if (IsGrass(d)) caveGrass++; }
                }
                IntVec3 home = map.AllCells.Where(x => x.x >= map.Size.x / 2 && x.GetRoof(map) == null && x.GetEdifice(map) == null).RandomElementWithFallback(IntVec3.Invalid);
                if (home.IsValid)
                {
                    // Native cell: nothing may be added beyond what vanilla offered.
                    RM_PyrelandsSettings.wildPlantAllowlistEnabled = false;
                    int nativeRaw = Read(home, false).Count(IsGrass);
                    RM_PyrelandsSettings.wildPlantAllowlistEnabled = true;
                    nativeSupplied = Read(home, false).Count(IsGrass) - nativeRaw;
                }

                var saturatedAt = AccessTools.Method(typeof(WildPlantSpawner), "SaturatedAt");
                foreach (IntVec3 cell in sample)
                {
                    if (saturatedAt != null && (bool)saturatedAt.Invoke(map.wildPlantSpawner, new object[] { cell, 1f, false, 1000000f })) saturated++;
                }
                foreach (IntVec3 cell in sample)
                {
                    for (int attempt = 0; attempt < 30 && cell.GetPlant(map) == null; attempt++)
                    {
                        map.wildPlantSpawner.CheckSpawnWildPlantAt(cell, 1f, 1000000f);
                    }
                    Plant p = cell.GetPlant(map);
                    if (p == null) bare++; else grown.Add(p);
                }
                int grownCount = grown.Count, grownForeign = grown.Count(g => !IsGrass(g.def));
                return "MIXEDPATCH cells " + cells + " | rawForeign " + rawForeign + " | rawGrass " + rawGrass + " | afterEmpty " + afterEmpty
                    + " | afterForeign " + afterForeign + " | afterGrass " + afterGrass + " | nativeSupplied " + nativeSupplied + " | caveGrass " + caveGrass
                    + " | grown " + grownCount + " | grownForeign " + grownForeign + " | bare " + bare + " | saturated " + saturated + " | secondary " + secondary.defName;
            }
            finally
            {
                RM_PyrelandsSettings.wildPlantAllowlistEnabled = wasOn;
                comp.biomeGrid = null;
                comp.secondaryBiome = null;
                foreach (Thing g in grown) if (g.Spawned) g.Destroy();
                foreach (var row in cleared)
                {
                    if (row.Key.GetPlant(map) != null) continue;
                    var back = (Plant)ThingMaker.MakeThing(row.Value.Key);
                    back.Growth = row.Value.Value;
                    GenSpawn.Spawn(back, row.Key, map);
                }
            }
        }
    }
}
