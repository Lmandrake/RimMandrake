using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using RimWorld;
using Verse;

namespace RimDefDump
{
    /// <summary>
    /// Entry point. [StaticConstructorOnStartup] runs after every mod has
    /// loaded, every PatchOperation has applied, and every def has had its
    /// cross-references resolved — which is exactly the moment we want to
    /// photograph.
    ///
    /// INERT BY DEFAULT. Without a request marker file this does nothing but
    /// log one line. That is deliberate: game loads on the full stack take
    /// ~23 minutes and are frequently being used to debug something else, so
    /// this tool must never add cost unless it was actually asked for.
    /// </summary>
    [StaticConstructorOnStartup]
    public static class RimDefDumpBootstrap
    {
        static RimDefDumpBootstrap()
        {
            try
            {
                DefDumper.Run();
            }
            catch (Exception ex)
            {
                // A research tool must never be the reason a 23-minute load
                // fails. Swallow everything, loudly.
                Log.Error("[RimDefDump] dump failed (game unaffected): " + ex);
            }
        }
    }

    public static class DefDumper
    {
        private const string FolderName = "DefDump";
        private const string MarkerName = "dump_request.txt";

        /// <summary>
        /// Stats to resolve per animal. Deliberately mirrors STAT_MAP in
        /// Utils/animal_inventory.py so the live and offline tables join
        /// column-for-column.
        /// </summary>
        private static readonly string[] AnimalStats =
        {
            "MoveSpeed", "MarketValue", "Mass",
            "ArmorRating_Sharp", "ArmorRating_Blunt", "ArmorRating_Heat",
            "ComfyTemperatureMin", "ComfyTemperatureMax",
            "LeatherAmount", "MeatAmount", "CarryingCapacity",
            "ToxicResistance", "ToxicEnvironmentResistance",
            "PsychicSensitivity", "FilthRate",
            "MinimumHandlingSkill", "AnimalsLearningFactor",
            "Insulation_Cold", "Insulation_Heat",
        };

        public static void Run()
        {
            string root = Path.Combine(GenFilePaths.SaveDataFolderPath, FolderName);
            string marker = Path.Combine(root, MarkerName);

            if (!File.Exists(marker))
            {
                Log.Message("[RimDefDump] inert (no " + MarkerName + "). To enable, create: " + marker);
                return;
            }

            string mode = "animals";
            try
            {
                string raw = File.ReadAllText(marker).Trim().ToLowerInvariant();
                if (raw.Length > 0) mode = raw;
            }
            catch (Exception ex)
            {
                Log.Warning("[RimDefDump] could not read marker, defaulting to 'animals': " + ex.Message);
            }

            bool dumpAll = mode == "all";
            Log.Message("[RimDefDump] starting, mode=" + mode + ", out=" + root);

            var total = Stopwatch.StartNew();
            Directory.CreateDirectory(root);

            var counts = new List<KeyValuePair<string, int>>();
            long animalMs = TimeIt(() => WriteAnimals(root));
            long allMs = 0;
            if (dumpAll) allMs = TimeIt(() => WriteAllDefs(root, counts));

            WriteManifest(root, mode, counts, total.ElapsedMilliseconds, animalMs, allMs);

            total.Stop();
            Log.Message("[RimDefDump] done in " + total.ElapsedMilliseconds + " ms"
                        + " (animals " + animalMs + " ms, all-defs " + allMs + " ms)");
        }

        private static long TimeIt(Action a)
        {
            var sw = Stopwatch.StartNew();
            a();
            sw.Stop();
            return sw.ElapsedMilliseconds;
        }

        private static StreamWriter Open(string path)
        {
            // No BOM: the Python side reads these with plain utf-8.
            return new StreamWriter(path, false, new UTF8Encoding(false));
        }

        // ------------------------------------------------------------------
        // manifest.json — what this dump is a photograph OF.
        // Without this, a dump is unattributable a week later.
        // ------------------------------------------------------------------
        private static void WriteManifest(string root, string mode,
                                          List<KeyValuePair<string, int>> counts,
                                          long totalMs, long animalMs, long allMs)
        {
            using (StreamWriter sw = Open(Path.Combine(root, "manifest.json")))
            {
                var w = new JsonWriter(sw);
                w.StartObject();
                w.Prop("tool", "RimDefDump");
                w.Prop("toolVersion", "1.0");
                w.Prop("mode", mode);
                w.Prop("capturedUtc", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"));

                try { w.Prop("gameVersion", VersionControl.CurrentVersionStringWithRev); }
                catch { }

                w.Name("timingsMs");
                w.StartObject();
                w.Prop("total", totalMs);
                w.Prop("animals", animalMs);
                w.Prop("allDefs", allMs);
                w.EndObject();

                // The load set, in load order. This is the single most important
                // piece of provenance: these CSVs/JSONs are a snapshot of a mod
                // set, not of RimWorld.
                w.Name("mods");
                w.StartArray();
                List<ModContentPack> mods = LoadedModManager.RunningModsListForReading;
                for (int i = 0; i < mods.Count; i++)
                {
                    ModContentPack m = mods[i];
                    w.StartObject();
                    w.Prop("loadOrder", i);
                    w.Prop("name", DefReflector.SafeString(m.Name));
                    w.Prop("packageId", m.PackageId);
                    try { w.Prop("rootDir", m.RootDir); } catch { }
                    w.EndObject();
                }
                w.EndArray();
                w.Prop("modCount", mods.Count);

                w.Name("defCounts");
                w.StartObject();
                for (int i = 0; i < counts.Count; i++) w.Prop(counts[i].Key, counts[i].Value);
                w.EndObject();

                w.EndObject();
            }
        }

        // ------------------------------------------------------------------
        // animals.json — the curated pass. Fast, and shaped to join directly
        // against Utils/animal_inventory.py's CSVs.
        // ------------------------------------------------------------------
        private static void WriteAnimals(string root)
        {
            // Resolve the stat defs once. Missing ones are normal: mods and DLC
            // move stats around, so a null here is data, not an error.
            var stats = new List<StatDef>();
            var statNames = new List<string>();
            for (int i = 0; i < AnimalStats.Length; i++)
            {
                StatDef sd = DefDatabase<StatDef>.GetNamedSilentFail(AnimalStats[i]);
                if (sd != null) { stats.Add(sd); statNames.Add(AnimalStats[i]); }
            }

            List<PawnKindDef> allKinds = DefDatabase<PawnKindDef>.AllDefsListForReading;

            using (StreamWriter sw = Open(Path.Combine(root, "animals.json")))
            {
                var w = new JsonWriter(sw);
                w.StartObject();
                w.Prop("capturedUtc", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"));

                // --- animals -------------------------------------------------
                int nAnimals = 0;
                w.Name("animals");
                w.StartArray();
                List<ThingDef> things = DefDatabase<ThingDef>.AllDefsListForReading;
                for (int i = 0; i < things.Count; i++)
                {
                    ThingDef td = things[i];
                    RaceProperties race = null;
                    try { race = td.race; } catch { }
                    if (race == null) continue; // same filter as the offline tool

                    nAnimals++;
                    w.StartObject();
                    w.Prop("defName", td.defName);
                    w.Prop("label", DefReflector.SafeString(td.label));
                    w.Prop("shortHash", (long)td.shortHash);
                    w.Prop("thingClass", td.thingClass != null ? td.thingClass.FullName : null);

                    ModContentPack pack = null;
                    try { pack = td.modContentPack; } catch { }
                    w.Prop("modName", pack != null ? DefReflector.SafeString(pack.Name) : null);
                    w.Prop("packageId", pack != null ? pack.PackageId : null);

                    try { w.Prop("isAnimal", race.Animal); } catch { }
                    try { w.Prop("intelligence", race.intelligence.ToString()); } catch { }

                    // Resolved stat values. THIS is what the offline scan
                    // fundamentally cannot produce: statBases holds only what a
                    // def explicitly declares, while the real value comes from
                    // the StatWorker after parents, offsets and factors apply.
                    w.Name("stats");
                    w.StartObject();
                    for (int s = 0; s < stats.Count; s++)
                    {
                        try { w.Prop(statNames[s], td.GetStatValueAbstract(stats[s])); }
                        catch { }
                    }
                    w.EndObject();

                    // Full resolved RaceProperties, reflected. Cheaper to keep
                    // everything than to guess now which field we will want.
                    w.Name("race");
                    DefReflector.WriteNested(w, race);

                    // Which PawnKindDefs point at this race, post-patch.
                    w.Name("pawnKinds");
                    w.StartArray();
                    for (int k = 0; k < allKinds.Count; k++)
                    {
                        PawnKindDef pk = allKinds[k];
                        if (pk.race != td) continue;
                        w.StartObject();
                        w.Prop("defName", pk.defName);
                        w.Prop("shortHash", (long)pk.shortHash);
                        try { w.Prop("combatPower", pk.combatPower); } catch { }
                        try { w.Prop("ecoSystemWeight", pk.ecoSystemWeight); } catch { }
                        try { w.Prop("canArriveManhunter", pk.canArriveManhunter); } catch { }
                        ModContentPack kpack = null;
                        try { kpack = pk.modContentPack; } catch { }
                        w.Prop("modName", kpack != null ? DefReflector.SafeString(kpack.Name) : null);
                        w.EndObject();
                    }
                    w.EndArray();

                    w.EndObject();
                }
                w.EndArray();

                // --- biome x animal, post-patch ------------------------------
                // The offline tool reconstructs this from two directions and
                // guesses at conflicts. Here the game has already merged them,
                // so this list settles what actually spawns where.
                int nPairs = 0;
                w.Name("biomeAnimals");
                w.StartArray();
                List<BiomeDef> biomes = DefDatabase<BiomeDef>.AllDefsListForReading;
                for (int i = 0; i < biomes.Count; i++)
                {
                    BiomeDef b = biomes[i];
                    IEnumerable<PawnKindDef> kinds;
                    try { kinds = b.AllWildAnimals; }
                    catch (Exception ex)
                    {
                        Log.Warning("[RimDefDump] biome " + b.defName + " AllWildAnimals threw: " + ex.Message);
                        continue;
                    }
                    foreach (PawnKindDef pk in kinds)
                    {
                        if (pk == null) continue;
                        nPairs++;
                        w.StartObject();
                        w.Prop("biome", b.defName);
                        w.Prop("pawnKind", pk.defName);
                        w.Prop("race", pk.race != null ? pk.race.defName : null);
                        try { w.Prop("commonality", b.CommonalityOfAnimal(pk)); } catch { }
                        w.EndObject();
                    }
                }
                w.EndArray();

                w.Prop("animalCount", nAnimals);
                w.Prop("biomeCount", biomes.Count);
                w.Prop("biomeAnimalPairCount", nPairs);
                w.EndObject();

                Log.Message("[RimDefDump] animals=" + nAnimals + " biomes=" + biomes.Count
                            + " biomeAnimalPairs=" + nPairs);
            }
        }

        // ------------------------------------------------------------------
        // defs/<Type>.json — the full generic pass (mode=all).
        // ------------------------------------------------------------------
        private static void WriteAllDefs(string root, List<KeyValuePair<string, int>> counts)
        {
            string dir = Path.Combine(root, "defs");
            Directory.CreateDirectory(dir);

            foreach (Type defType in GenDefDatabase.AllDefTypesWithDatabases())
            {
                IEnumerable defs;
                try { defs = AllDefsOf(defType); }
                catch (Exception ex)
                {
                    Log.Warning("[RimDefDump] cannot enumerate " + defType.Name + ": " + ex.Message);
                    continue;
                }
                if (defs == null) continue;

                int n = 0;
                string path = Path.Combine(dir, defType.Name + ".json");
                try
                {
                    using (StreamWriter sw = Open(path))
                    {
                        var w = new JsonWriter(sw);
                        w.StartObject();
                        w.Prop("defType", defType.Name);
                        w.Name("defs");
                        w.StartArray();
                        foreach (object o in defs)
                        {
                            var d = o as Def;
                            if (d == null) continue;
                            n++;
                            DefReflector.WriteDef(w, d);
                        }
                        w.EndArray();
                        w.Prop("count", n);
                        w.EndObject();
                    }
                }
                catch (Exception ex)
                {
                    Log.Warning("[RimDefDump] failed writing " + defType.Name + ": " + ex.Message);
                    continue;
                }
                counts.Add(new KeyValuePair<string, int>(defType.Name, n));
            }

            Log.Message("[RimDefDump] wrote " + counts.Count + " def-type files to " + dir);
        }

        /// <summary>
        /// DefDatabase&lt;T&gt;.AllDefs by reflection, since T is only known at
        /// runtime. Uses the generic database directly rather than a helper, so
        /// this does not depend on a helper signature staying stable across
        /// RimWorld versions.
        /// </summary>
        private static IEnumerable AllDefsOf(Type defType)
        {
            Type db = typeof(DefDatabase<>).MakeGenericType(defType);
            PropertyInfo p = db.GetProperty("AllDefs", BindingFlags.Public | BindingFlags.Static);
            if (p == null) return null;
            return p.GetValue(null, null) as IEnumerable;
        }
    }
}
