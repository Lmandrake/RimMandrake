using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using RimWorld;
using LudeonTK;
using Verse;

namespace RimMandrake.RimDefDump
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
                Log.Error("[RimMandrake.RimDefDump] dump failed (game unaffected): " + ex);
            }
        }
    }

    /// <summary>
    /// The same dump, on demand, without a 23-minute load.
    ///
    /// 🔴 Why this exists (BENCH, 2026-09-02): `Run()` only ever fired from
    /// [StaticConstructorOnStartup], so the ONLY way to get a def dump matching the
    /// live mod set was to restart the game — and a dump that does not match is
    /// refused by every consumer (`harvest_log.py` refuses outright; a stale one
    /// "prints as BETTER-than-baseline, indistinguishable from a real pass"). A
    /// session that notices the dump is stale therefore had no move at all.
    /// It does now: this is bridge-reachable via
    /// `rimworld/execute_debug_action` and needs no map, no reload, no marker file
    /// (the marker gates the STARTUP path, whose whole point is costing a load
    /// nothing; asking for it here IS the request).
    ///
    /// Defs are fully loaded and cross-resolved by the time any game state exists,
    /// so the photograph is the same one the startup path takes.
    /// </summary>
    public static class RimDefDumpDebugActions
    {
        [DebugAction("RMDefDump", "Dump defs now (all)",
            allowedGameStates = AllowedGameStates.Entry | AllowedGameStates.Playing)]
        private static void DumpAll() { DefDumper.RunOnDemand("all"); }

        [DebugAction("RMDefDump", "Dump defs now (animals)",
            allowedGameStates = AllowedGameStates.Entry | AllowedGameStates.Playing)]
        private static void DumpAnimals() { DefDumper.RunOnDemand("animals"); }
    }

    public static class DefDumper
    {
        private const string FolderName = "DefDump";
        private const string MarkerName = "dump_request.txt";

        /// <summary>
        /// DUMP_PRODUCER_DATED_CAPTURES_1. Owner, 2026-08-21: "Option (a) all the
        /// way. Keep last three."
        ///
        /// A capture goes to DefDump/captures/&lt;capturedUtc&gt;/ and the newest three
        /// survive. `defs.sqlite` is DERIVED and stays at the root, outside any
        /// capture, so re-deriving it never costs a capture and pruning never costs
        /// the database.
        ///
        /// The id is the manifest's own capturedUtc with ':' replaced by '-', so it
        /// stays ISO-8601 with fixed-width fields and a plain lexicographic sort is
        /// chronological. `game_paths.captures()` matches
        /// ^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$ and ignores anything else,
        /// deliberately — so a half-written directory can never masquerade as a
        /// capture.
        ///
        /// ⛔ There is NO `current` or `official` symlink and that is measured, not a
        /// preference: a symlink WSL creates under LocalLow is unreadable from
        /// Windows, so the game could never follow one. Current = max(dirname).
        /// </summary>
        private const string CapturesDir = "captures";

        /// <summary>The scratch name a capture is built under before it is named.</summary>
        private const string WritingDir = ".writing";

        /// <summary>A capture holding this file is frozen and never counts against retention.</summary>
        private const string KeepMarker = ".keep";

        private const int KeepNewest = 3;

        /// <summary>
        /// Stamped ONCE per run and used for the capture id, the manifest and
        /// animals.json alike.
        /// ⚠️ This used to be a separate `DateTime.UtcNow` in each writer, so the
        /// manifest and animals.json could disagree by a second or more. The id has
        /// to equal the manifest's own value or a reader cannot join them, which is
        /// what turned a latent inconsistency into a real one.
        /// </summary>
        private static string CapturedUtc = "";

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
                Log.Message("[RimMandrake.RimDefDump] inert (no " + MarkerName + "). To enable, create: " + marker);
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
                Log.Warning("[RimMandrake.RimDefDump] could not read marker, defaulting to 'animals': " + ex.Message);
            }

            RunWithMode(mode);
        }

        /// <summary>
        /// The on-demand entry, reached from the debug menu and therefore from the
        /// bridge. No marker check: the marker exists so a STARTUP never costs a
        /// load anything it was not asked for, and clicking this IS the asking.
        /// Swallows everything for the same reason the bootstrap does — a research
        /// tool must never be why a session ends.
        /// </summary>
        public static void RunOnDemand(string mode)
        {
            try
            {
                mode = string.IsNullOrEmpty(mode) ? "all" : mode.Trim().ToLowerInvariant();
                Log.Message("[RimMandrake.RimDefDump] ON-DEMAND dump requested, mode=" + mode);
                RunWithMode(mode);
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.RimDefDump] on-demand dump failed (game unaffected): " + ex);
            }
        }

        private static void RunWithMode(string mode)
        {
            string root = Path.Combine(GenFilePaths.SaveDataFolderPath, FolderName);
            bool dumpAll = mode == "all";

            // A marker holding "ALL_DEFS", "full" or a typo used to fall through to
            // the animals-only pass without a word. The manifest records `mode`
            // verbatim so nothing downstream is poisoned, but the person who asked
            // for every def deserves to be told they did not get them.
            if (mode != "all" && mode != "animals")
                Log.Warning("[RimMandrake.RimDefDump] unrecognised mode '" + mode + "' — the only modes are "
                            + "'all' and 'animals'. Running the ANIMALS-ONLY pass; defs/ will not be written.");

            DateTime now = DateTime.UtcNow;
            CapturedUtc = now.ToString("yyyy-MM-ddTHH:mm:ssZ");
            string captureId = now.ToString("yyyy-MM-ddTHH-mm-ssZ");

            string capturesRoot = Path.Combine(root, CapturesDir);
            string writing = Path.Combine(capturesRoot, WritingDir);
            string final = Path.Combine(capturesRoot, captureId);

            Log.Message("[RimMandrake.RimDefDump] starting, mode=" + mode + ", capture=" + captureId
                        + ", out=" + capturesRoot);

            var total = Stopwatch.StartNew();
            Directory.CreateDirectory(capturesRoot);

            // A `.writing` left behind is the debris of a run that died. It is not a
            // capture and never was — `captures()` cannot see it — so removing it is
            // safe and is the only way a second attempt can proceed.
            if (Directory.Exists(writing))
            {
                Log.Warning("[RimMandrake.RimDefDump] removing a leftover " + WritingDir
                            + " from an earlier run that did not finish");
                try { Directory.Delete(writing, true); }
                catch (Exception ex)
                {
                    Log.Error("[RimMandrake.RimDefDump] cannot clear " + writing + ": " + ex.Message);
                    return;
                }
            }
            Directory.CreateDirectory(writing);

            var counts = new List<KeyValuePair<string, int>>();
            var typeEntries = new List<DefTypeEntry>();
            var collisions = new List<string>();
            var writeFailures = new List<DefTypeWriteFailure>();
            long animalMs = TimeIt(() => WriteAnimals(writing));
            long allMs = 0;
            if (dumpAll) allMs = TimeIt(() => WriteAllDefs(writing, counts, typeEntries, collisions, writeFailures));

            WriteManifest(writing, mode, counts, typeEntries, collisions, writeFailures,
                          total.ElapsedMilliseconds, animalMs, allMs);

            // 🔑 THE RENAME IS WHAT MAKES THE CAPTURE EXIST. Everything above wrote into
            // a name no reader will match, so a crash at any point leaves nothing that
            // could be mistaken for a finished capture. Directory.Move is atomic on NTFS.
            if (!Publish(writing, final, captureId)) return;

            Prune(capturesRoot);

            total.Stop();
            Log.Message("[RimMandrake.RimDefDump] done in " + total.ElapsedMilliseconds + " ms"
                        + " (animals " + animalMs + " ms, all-defs " + allMs + " ms)");
        }

        /// <summary>
        /// Name the finished capture. Returns false if it could not be named, in which
        /// case NOTHING is published and the previous captures are untouched.
        /// </summary>
        private static bool Publish(string writing, string final, string captureId)
        {
            try
            {
                // Two dumps inside one second is not a real scenario (a load is minutes),
                // but if it ever happened the id would already exist and Move would throw.
                // Clearing it would destroy a capture written seconds ago, so refuse instead.
                if (Directory.Exists(final))
                {
                    Log.Error("[RimMandrake.RimDefDump] capture " + captureId + " already exists; "
                              + "leaving the new one under " + WritingDir + " rather than "
                              + "overwriting a capture that is already on disk");
                    return false;
                }
                Directory.Move(writing, final);
                Log.Message("[RimMandrake.RimDefDump] capture published: " + final);
                return true;
            }
            catch (Exception ex)
            {
                Log.Error("[RimMandrake.RimDefDump] could not publish the capture (nothing was lost, "
                          + "the previous captures are intact): " + ex);
                return false;
            }
        }

        /// <summary>
        /// Keep the newest <see cref="KeepNewest"/> captures and delete the rest.
        ///
        /// 🔴 A CAPTURE HOLDING <see cref="KeepMarker"/> IS NEVER DELETED AND NEVER
        /// COUNTS AGAINST THE THREE. `refresh.py --freeze --by owner` writes that file
        /// into a capture somebody decided to keep, and it is the entire contract
        /// between retention and the freeze — it means the game needs no knowledge of
        /// the repo, the registry, or which capture anyone froze.
        ///
        /// ⚠️ Runs AFTER the rename on purpose. Pruning first would let a capture that
        /// then failed to publish cost an old one for nothing.
        /// </summary>
        private static void Prune(string capturesRoot)
        {
            try
            {
                var ids = new List<string>();
                foreach (string dir in Directory.GetDirectories(capturesRoot))
                {
                    string name = Path.GetFileName(dir);
                    if (!IsCaptureId(name)) continue;               // .writing, or junk
                    if (File.Exists(Path.Combine(dir, KeepMarker))) continue;   // frozen
                    ids.Add(name);
                }
                // The id is fixed-width ISO-8601, so ordinal sort IS chronological.
                ids.Sort(StringComparer.Ordinal);
                int drop = ids.Count - KeepNewest;
                for (int i = 0; i < drop; i++)
                {
                    string victim = Path.Combine(capturesRoot, ids[i]);
                    try
                    {
                        Directory.Delete(victim, true);
                        Log.Message("[RimMandrake.RimDefDump] pruned old capture " + ids[i]);
                    }
                    catch (Exception ex)
                    {
                        Log.Warning("[RimMandrake.RimDefDump] could not prune " + ids[i] + ": " + ex.Message);
                    }
                }
            }
            catch (Exception ex)
            {
                // Retention failing is untidy; it is not a reason to fail the dump.
                Log.Warning("[RimMandrake.RimDefDump] retention pass failed: " + ex.Message);
            }
        }

        /// <summary>
        /// yyyy-MM-ddTHH-mm-ssZ, and nothing else.
        /// 🔑 Hand-rolled rather than a Regex because this must agree EXACTLY with
        /// `game_paths.captures()`, which uses that same anchored pattern. A directory
        /// this rejects is invisible to every reader, so the two must not drift.
        /// </summary>
        private static bool IsCaptureId(string name)
        {
            if (name == null || name.Length != 20) return false;
            for (int i = 0; i < 20; i++)
            {
                char c = name[i];
                if (i == 4 || i == 7 || i == 13 || i == 16) { if (c != '-') return false; }
                else if (i == 10) { if (c != 'T') return false; }
                else if (i == 19) { if (c != 'Z') return false; }
                else if (c < '0' || c > '9') return false;
            }
            return true;
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
            // Buffered generously — these files are hundreds of MB and the
            // write is a measurable slice of a load nobody wants lengthened.
            return new StreamWriter(path, false, new UTF8Encoding(false), 1 << 20);
        }

        /// <summary>
        /// Indentation costs roughly a third of the file on data this deeply
        /// nested, and nothing reads these by eye — they are consumed by
        /// Utils/animal_live_diff.py. manifest.json is the exception: it is
        /// small and IS read by humans, so it stays pretty-printed.
        /// Pretty-print any of the others on demand with:
        ///     python -m json.tool &lt; defs/ThingDef.json
        /// </summary>
        private const bool IndentBulkFiles = false;

        // ------------------------------------------------------------------
        // manifest.json — what this dump is a photograph OF.
        // Without this, a dump is unattributable a week later.
        // ------------------------------------------------------------------
        private static void WriteManifest(string root, string mode,
                                          List<KeyValuePair<string, int>> counts,
                                          List<DefTypeEntry> typeEntries,
                                          List<string> collisions,
                                          List<DefTypeWriteFailure> writeFailures,
                                          long totalMs, long animalMs, long allMs)
        {
            using (StreamWriter sw = Open(Path.Combine(root, "manifest.json")))
            {
                var w = new JsonWriter(sw);
                w.StartObject();
                w.Prop("tool", "RimMandrake.RimDefDump");
                w.Prop("toolVersion", "1.0");
                w.Prop("mode", mode);
                w.Prop("capturedUtc", CapturedUtc);

                PropOrError(w, "gameVersion", () => VersionControl.CurrentVersionStringWithRev);

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
                    // 1-BASED, deliberately. rimworld_loadset.py, animals.csv
                    // and def_inventory.py all number the load order from 1;
                    // emitting the raw 0-based list index here would plant an
                    // off-by-one in every offline/live join.
                    w.Prop("loadOrder", i + 1);
                    w.Prop("name", DefReflector.SafeString(m.Name));
                    w.Prop("packageId", m.PackageId);
                    PropOrError(w, "rootDir", () => m.RootDir);
                    w.EndObject();
                }
                w.EndArray();
                w.Prop("modCount", mods.Count);

                // Keyed on the FILE STEM, not the simple type name. For the
                // 517 types whose simple name is unique those are the same
                // string; for the 13 that collide, the loser is now listed
                // under its full name instead of overwriting the winner.
                w.Name("defCounts");
                w.StartObject();
                for (int i = 0; i < counts.Count; i++) w.Prop(counts[i].Key, counts[i].Value);
                w.EndObject();

                // The authoritative index: which type landed in which file.
                // A reader that wants Verse.AbilityDef specifically looks here
                // rather than assuming defs/AbilityDef.json is it.
                w.Name("defTypes");
                w.StartArray();
                int publishedTypes = 0;
                for (int i = 0; i < typeEntries.Count; i++)
                {
                    DefTypeEntry e = typeEntries[i];
                    if (e.file == null) continue;
                    publishedTypes++;
                    w.StartObject();
                    w.Prop("name", e.type.Name);
                    w.Prop("fullName", e.type.FullName);
                    w.Prop("assembly", e.type.Assembly.GetName().Name);
                    w.Prop("file", e.file);
                    w.Prop("count", e.count);
                    w.EndObject();
                }
                w.EndArray();

                // Named loudly, because a collision is the one thing that used
                // to make a populated def type read as empty.
                w.Name("defTypeCollisions");
                w.StartArray();
                for (int i = 0; i < collisions.Count; i++) w.Str(collisions[i]);
                w.EndArray();
                // The number of types that actually LANDED IN A FILE — equal to the
                // length of the defTypes array above, never the count of types merely
                // seen. A type that failed is in defTypeWriteFailures instead, so
                // defTypeCount + defTypeWriteFailures.length = types found.
                w.Prop("defTypeCount", publishedTypes);

                // A type whose write threw mid-file is correctly ABSENT from
                // both defCounts and defTypes above — there is no file to point
                // to and no count worth trusting — but "absent from two lists"
                // and "never existed" read identically to a downstream reader.
                // This is the one place that says so out loud, so a type that
                // silently vanished from the dump is distinguishable from a
                // type that was never a def type at all.
                w.Name("defTypeWriteFailures");
                w.StartArray();
                for (int i = 0; i < writeFailures.Count; i++)
                {
                    DefTypeWriteFailure f = writeFailures[i];
                    w.StartObject();
                    w.Prop("type", f.typeFullName);
                    w.Prop("file", f.file);
                    w.Prop("error", f.error);
                    w.EndObject();
                }
                w.EndArray();

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
            var statsMissing = new List<string>();
            for (int i = 0; i < AnimalStats.Length; i++)
            {
                StatDef sd = DefDatabase<StatDef>.GetNamedSilentFail(AnimalStats[i]);
                if (sd != null) { stats.Add(sd); statNames.Add(AnimalStats[i]); }
                else statsMissing.Add(AnimalStats[i]);
            }
            if (statsMissing.Count > 0)
                Log.Warning("[RimMandrake.RimDefDump] " + statsMissing.Count + " of " + AnimalStats.Length
                            + " AnimalStats did not resolve and are absent from every animal's stats object: "
                            + string.Join(", ", statsMissing.ToArray()));

            List<PawnKindDef> allKinds = DefDatabase<PawnKindDef>.AllDefsListForReading;

            using (StreamWriter sw = Open(Path.Combine(root, "animals.json")))
            {
                var w = new JsonWriter(sw, IndentBulkFiles);
                w.StartObject();
                w.Prop("capturedUtc", CapturedUtc);

                // ⛔ Which of AnimalStats resolved, and which did not. A StatDef this mod
                // set does not have is simply ABSENT from every animal's `stats` object,
                // and an absent key reads downstream as "not applicable" — identical to a
                // stat the dumper failed to look up. Naming the misses is the only thing
                // that separates them. Same rule as PropOrError.
                w.Name("statsResolved");
                w.StartArray();
                for (int i = 0; i < statNames.Count; i++) w.Str(statNames[i]);
                w.EndArray();
                w.Name("statsMissing");
                w.StartArray();
                for (int i = 0; i < statsMissing.Count; i++) w.Str(statsMissing[i]);
                w.EndArray();

                // --- animals -------------------------------------------------
                int nAnimals = 0;
                int nCorpsesSkipped = 0;
                w.Name("animals");
                w.StartArray();
                List<ThingDef> things = DefDatabase<ThingDef>.AllDefsListForReading;
                for (int i = 0; i < things.Count; i++)
                {
                    ThingDef td = things[i];
                    RaceProperties race = null;
                    // ✅ These two stay bare on purpose: they are CONTROL FLOW, not published
                    // values. A null race skips the def entirely and the def's absence from
                    // animals.json is itself the signal; nothing downstream can mistake a
                    // throw here for a measurement.
                    try { race = td.race; } catch { }
                    if (race == null) continue; // same filter as the offline tool

                    // RimWorld GENERATES a Corpse_<X> ThingDef for every race at
                    // load, and each one carries the same RaceProperties. On the
                    // first full run they were 2,345 of 4,810 records — 49% of
                    // the file, every race dumped twice. They also exist in no
                    // XML anywhere, so they would show up in the offline/live
                    // diff as thousands of phantom "live_only" rows.
                    bool isCorpse = false;
                    try { isCorpse = td.IsCorpse; } catch { }
                    if (isCorpse) { nCorpsesSkipped++; continue; }

                    nAnimals++;
                    w.StartObject();
                    w.Prop("defName", td.defName);
                    w.Prop("label", DefReflector.SafeString(td.label));
                    w.Prop("shortHash", (long)td.shortHash);
                    w.Prop("thingClass", td.thingClass != null ? td.thingClass.FullName : null);

                    // modContentPack feeds two PUBLISHED keys, so a throw here would read
                    // downstream as "this def belongs to no mod" - which is a claim, not a gap.
                    ModContentPack pack = null;
                    string packError = null;
                    try { pack = td.modContentPack; }
                    catch (Exception ex) { packError = ex.GetType().Name + ": " + ex.Message; }
                    w.Prop("modName", pack != null ? DefReflector.SafeString(pack.Name) : null);
                    w.Prop("packageId", pack != null ? pack.PackageId : null);
                    if (packError != null) w.Prop("modContentPackError", packError);

                    PropOrError(w, "isAnimal", () => race.Animal);
                    PropOrError(w, "intelligence", () => race.intelligence.ToString());

                    // Resolved stat values. THIS is what the offline scan
                    // fundamentally cannot produce: statBases holds only what a
                    // def explicitly declares, while the real value comes from
                    // the StatWorker after parents, offsets and factors apply.
                    w.Name("stats");
                    w.StartObject();
                    for (int s = 0; s < stats.Count; s++)
                    {
                        int si = s;   // the lambda must not close over the loop variable
                        PropOrError(w, statNames[si], () => (double)td.GetStatValueAbstract(stats[si]));
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
                        PropOrError(w, "combatPower", () => (double)pk.combatPower);
                        PropOrError(w, "ecoSystemWeight", () => (double)pk.ecoSystemWeight);
                        PropOrError(w, "canArriveManhunter", () => pk.canArriveManhunter);
                        ModContentPack kpack = null;
                        string kpackError = null;
                        try { kpack = pk.modContentPack; }
                        catch (Exception ex) { kpackError = ex.GetType().Name + ": " + ex.Message; }
                        w.Prop("modName", kpack != null ? DefReflector.SafeString(kpack.Name) : null);
                        if (kpackError != null) w.Prop("modContentPackError", kpackError);
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
                var biomeFailures = new List<string>();
                // Resolve the reflection field BEFORE the loop, so the flag written after
                // it means "the dumper could look" even when there are zero biomes.
                bool declaredReadable = EnsureWildAnimalsField();
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
                        Log.Warning("[RimMandrake.RimDefDump] biome " + b.defName + " AllWildAnimals threw: " + ex.Message);
                        // ⛔ Without this the biome contributes zero rows and biomeCount
                        // still counts it, so a reader sees "this biome has no wild
                        // animals" where the truth is "the dumper could not ask".
                        biomeFailures.Add(b.defName + ": " + ex.GetType().Name + ": " + ex.Message);
                        continue;
                    }
                    // The record's own field, so a reader can tell what the DEF SAYS from
                    // what the ENGINE ANSWERS. See the block comment below.
                    Dictionary<PawnKindDef, float> declared = DeclaredWildAnimals(b);

                    foreach (PawnKindDef pk in kinds)
                    {
                        if (pk == null) continue;
                        nPairs++;
                        w.StartObject();
                        w.Prop("biome", b.defName);
                        w.Prop("pawnKind", pk.defName);
                        w.Prop("race", pk.race != null ? pk.race.defName : null);

                        // === DUMPER_SWALLOWS_CACHE_THROW_1 ===========================
                        // This used to be one line:
                        //     try { w.Prop("commonality", b.CommonalityOfAnimal(pk)); } catch { }
                        // Two defects, and together they cost an investigation on 2026-08-26.
                        //
                        //  1. It published the ENGINE'S computed answer under the name a
                        //     reader takes for the DEF'S FIELD. Those are different things
                        //     whenever the cache is not intact.
                        //  2. The bare `catch { }` hid the throw. CommonalityOfAnimal assigns
                        //     cachedAnimalCommonalities BEFORE filling it, so a duplicate-key
                        //     ArgumentException leaves it partial and non-null and every later
                        //     call returns a perfectly plausible 0f - forever, with no error.
                        //
                        // So: publish BOTH, under names that cannot be confused, and write the
                        // exception TYPE into the row when one is thrown. ⛔ A field that could
                        // not be read must never look like a field that read zero.
                        float declaredValue;
                        if (declared != null && declared.TryGetValue(pk, out declaredValue))
                            w.Prop("commonalityDeclared", declaredValue);
                        else
                            w.Prop("commonalityDeclared", (string)null); // not in wildAnimals: it reached this biome via race.wildBiomes

                        try
                        {
                            w.Prop("commonalityEngine", b.CommonalityOfAnimal(pk));
                        }
                        catch (Exception ex)
                        {
                            w.Prop("commonalityEngine", (string)null);
                            w.Prop("commonalityEngineError", ex.GetType().Name + ": " + ex.Message);
                        }
                        w.EndObject();
                    }
                }
                w.EndArray();

                // The biomes that produced NO rows because the engine threw, not because
                // they hold no animals. biomeCount counts them; biomeAnimals does not.
                w.Name("biomeFailures");
                w.StartArray();
                for (int i = 0; i < biomeFailures.Count; i++) w.Str(biomeFailures[i]);
                w.EndArray();

                // false ⇒ every commonalityDeclared in this file is null because the
                // dumper could not read BiomeDef.wildAnimals, NOT because nothing
                // declares a commonality. UNMEASURED is not 0.
                w.Prop("commonalityDeclaredReadable", declaredReadable);

                w.Prop("animalCount", nAnimals);
                w.Prop("corpseDefsSkipped", nCorpsesSkipped);
                w.Prop("biomeCount", biomes.Count);
                w.Prop("biomeAnimalPairCount", nPairs);
                w.EndObject();

                // Report the skip rather than letting it be a silent filter —
                // a reader comparing this count against the offline tool needs
                // to know what was excluded and why.
                Log.Message("[RimMandrake.RimDefDump] animals=" + nAnimals
                            + " (skipped " + nCorpsesSkipped + " generated corpse defs)"
                            + " biomes=" + biomes.Count
                            + " (" + biomeFailures.Count + " threw and produced no rows)"
                            + " biomeAnimalPairs=" + nPairs
                            + " statsMissing=" + statsMissing.Count);
            }
        }

        // ------------------------------------------------------------------
        // DUMPER_SWALLOWS_CACHE_THROW_1. ⛔ NEVER `try { w.Prop(...) } catch { }` on a
        // value this dump publishes. A property that THREW and a property that read a
        // legitimate 0 / false / null come out of a bare catch looking identical - the
        // first silently omits the key, and every downstream reader treats a missing key
        // as "not applicable". These write the exception TYPE into a sibling `<name>Error`
        // key instead, so an unreadable field can never be mistaken for a measured one.
        private static void PropOrError(JsonWriter w, string name, Func<string> read)
        {
            try { w.Prop(name, read()); }
            catch (Exception ex) { w.Prop(name, (string)null); w.Prop(name + "Error", ex.GetType().Name + ": " + ex.Message); }
        }

        private static void PropOrError(JsonWriter w, string name, Func<bool> read)
        {
            try { w.Prop(name, read()); }
            catch (Exception ex) { w.Prop(name, (string)null); w.Prop(name + "Error", ex.GetType().Name + ": " + ex.Message); }
        }

        private static void PropOrError(JsonWriter w, string name, Func<double> read)
        {
            try { w.Prop(name, read()); }
            catch (Exception ex) { w.Prop(name, (string)null); w.Prop(name + "Error", ex.GetType().Name + ": " + ex.Message); }
        }

        // ------------------------------------------------------------------
        // BiomeDef.wildAnimals is PRIVATE in 1.6, so the DECLARED value can only be
        // read by reflection. DUMPER_SWALLOWS_CACHE_THROW_1: publishing only the
        // engine's computed answer is what made 181 zeroes look like a content defect
        // when they were something else entirely.
        //
        // ⛔ Returns null - NOT an empty dictionary - when the field cannot be found.
        // An empty dictionary would make every animal report commonalityDeclared:null,
        // which reads as "declared nowhere" rather than "the dumper could not look".
        // Same rule as UNMEASURED-vs-0 everywhere else in this project.
        private static FieldInfo wildAnimalsField;
        private static bool wildAnimalsFieldResolved;

        /// <summary>
        /// Resolve the field once. Returns whether it CAN be read, which animals.json
        /// publishes as `commonalityDeclaredReadable` — a false there is the difference
        /// between "nothing declares a commonality" and "the dumper could not look".
        /// </summary>
        private static bool EnsureWildAnimalsField()
        {
            if (!wildAnimalsFieldResolved)
            {
                wildAnimalsFieldResolved = true;
                wildAnimalsField = typeof(BiomeDef).GetField(
                    "wildAnimals", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public);
                if (wildAnimalsField == null)
                    Log.Warning("[RimMandrake.RimDefDump] BiomeDef.wildAnimals not found by reflection - "
                                + "commonalityDeclared will be null for every row. The field was "
                                + "renamed or made public; fix DeclaredWildAnimals().");
            }
            return wildAnimalsField != null;
        }

        private static Dictionary<PawnKindDef, float> DeclaredWildAnimals(BiomeDef b)
        {
            if (!EnsureWildAnimalsField()) return null;

            var list = wildAnimalsField.GetValue(b) as IList;
            if (list == null) return null;

            var outMap = new Dictionary<PawnKindDef, float>();
            for (int i = 0; i < list.Count; i++)
            {
                var rec = list[i] as BiomeAnimalRecord;
                if (rec == null || rec.animal == null) continue;   // a dangling cross-ref leaves animal null
                outMap[rec.animal] = rec.commonality;              // indexer, not Add: a duplicate must not throw HERE
            }
            return outMap;
        }

        // ------------------------------------------------------------------
        // defs/<Type>.json — the full generic pass (mode=all).
        //
        // === WHY THIS IS NOT KEYED ON defType.Name ===
        // A def type's SIMPLE name is not unique across a 578-mod stack. The
        // 2026-08-21 capture enumerated 532 def types under only 517 distinct
        // simple names: 13 names were claimed by two or three unrelated types.
        // The old code wrote Path.Combine(dir, defType.Name + ".json"), so the
        // LAST type enumerated silently overwrote every earlier one's file.
        //
        // That is what made AbilityDef read as empty. Three types are called
        // AbilityDef in this stack, holding 612, 18 and 0 defs; the empty one
        // was written last, so defs/AbilityDef.json was
        // {"defType":"AbilityDef","defs":[],"count":0} and Verse.AbilityDef's
        // 612 defs — every vanilla psycast and Ideology ability — were gone.
        // Same failure: CharacterDef (0 beat 269), SymbolDef (0 beat 9099),
        // StructureLayoutDef (0 beat 301), FaceTypeDef (152 lost to 0).
        //
        // === THE RULE ===
        // Simple name is unique  -> "<Name>.json", exactly as before, so every
        //                           existing reader of defs/ThingDef.json is
        //                           unaffected.
        // Simple name collides   -> the type holding the MOST defs keeps
        //                           "<Name>.json"; the others get
        //                           "<FullName>.json". Ties break on
        //                           core-assembly-first, then ordinal FullName,
        //                           so the mapping is deterministic across runs.
        // Stem still taken       -> "<stem>__<assembly>.json". Every stem is claimed
        //                           case-insensitively against one set, because NTFS
        //                           folds case and a namespace-less type's FullName IS
        //                           its Name — two more routes to one file, one winner.
        // manifest.json gains a "defTypes" array giving fullName, assembly,
        // file and count for every type, and "defTypeCollisions" naming the
        // groups, so a reader can always find where a type actually landed.
        // ------------------------------------------------------------------
        private sealed class DefTypeEntry
        {
            public Type type;
            public int count;
            public bool core;
            public string file;
        }

        /// <summary>Recorded when a def type's own file throws partway through
        /// writing — see DUMPER_SWALLOWS_CACHE_THROW_1 above `PropOrError`: a
        /// gap must be reported, never left to look like the type just wasn't
        /// there.</summary>
        private sealed class DefTypeWriteFailure
        {
            public string typeFullName;
            public string file;
            public string error;
        }

        private static void WriteAllDefs(string root, List<KeyValuePair<string, int>> counts,
                                         List<DefTypeEntry> entries, List<string> collisions,
                                         List<DefTypeWriteFailure> writeFailures)
        {
            string dir = Path.Combine(root, "defs");
            Directory.CreateDirectory(dir);

            Assembly coreAsm = typeof(Def).Assembly;

            // --- pass 1: enumerate the types and how many defs each holds ----
            // Counting is a list walk; the expensive part is the reflection
            // write in pass 2. Doing it twice is cheap and is the only way to
            // know which type deserves the unqualified filename.
            foreach (Type defType in GenDefDatabase.AllDefTypesWithDatabases())
            {
                if (defType == null) continue;
                int n;
                try { n = CountDefsOf(defType); }
                catch (Exception ex)
                {
                    Log.Warning("[RimMandrake.RimDefDump] cannot enumerate " + defType.FullName + ": " + ex.Message);
                    // ⛔ A type dropped HERE never reaches entries, so it is absent from
                    // defCounts, from defTypes and from defs/ alike — indistinguishable
                    // from a type that was never a def type at all. Same rule as the
                    // pass-2 failures below: a gap gets reported, never left to look
                    // like an absence.
                    writeFailures.Add(new DefTypeWriteFailure
                    {
                        typeFullName = defType.FullName,
                        file = null,
                        error = "count: " + ex.GetType().Name + ": " + ex.Message,
                    });
                    continue;
                }
                if (n < 0)
                {
                    Log.Warning("[RimMandrake.RimDefDump] " + defType.FullName
                                + " exposes neither DefCount nor AllDefs; nothing can be written for it");
                    writeFailures.Add(new DefTypeWriteFailure
                    {
                        typeFullName = defType.FullName,
                        file = null,
                        error = "count: DefDatabase<T> exposes neither DefCount nor AllDefs",
                    });
                    continue;
                }
                entries.Add(new DefTypeEntry
                {
                    type = defType,
                    count = n,
                    core = defType.Assembly == coreAsm,
                });
            }

            // --- assign filenames, disambiguating collisions -----------------
            var byName = new Dictionary<string, List<DefTypeEntry>>();
            for (int i = 0; i < entries.Count; i++)
            {
                List<DefTypeEntry> group;
                if (!byName.TryGetValue(entries[i].type.Name, out group))
                {
                    group = new List<DefTypeEntry>();
                    byName[entries[i].type.Name] = group;
                }
                group.Add(entries[i]);
            }

            // 🔑 Stems are claimed against ONE reserved set, not per group, because a
            // per-group assignment cannot see two ways two types still end up in one file:
            //   * NTFS is CASE-INSENSITIVE. Two def types whose simple names differ only
            //     in case fall into two different groups and would both claim
            //     "<Name>.json" — one file, one winner, silently: exactly the overwrite
            //     this whole scheme was written to stop.
            //   * A def type declared in NO namespace has FullName == Name, so the loser
            //     of its own collision group would be handed the stem the winner holds.
            // Groups are walked in ordinal key order so the mapping stays deterministic
            // across runs, which is the property the tie-breaks below exist for.
            var assignedStems = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var groupKeys = new List<string>(byName.Keys);
            groupKeys.Sort(StringComparer.Ordinal);

            foreach (string key in groupKeys)
            {
                List<DefTypeEntry> group = byName[key];
                if (group.Count == 1)
                {
                    group[0].file = ReserveStem(assignedStems, key, group[0], collisions) + ".json";
                    continue;
                }

                group.Sort(delegate (DefTypeEntry a, DefTypeEntry b)
                {
                    if (a.count != b.count) return b.count.CompareTo(a.count);   // most defs first
                    if (a.core != b.core) return a.core ? -1 : 1;                // then the game's own
                    return string.CompareOrdinal(a.type.FullName, b.type.FullName);
                });

                var names = new List<string>();
                for (int i = 0; i < group.Count; i++)
                {
                    string stem = i == 0 ? key : SafeFileName(group[i].type.FullName);
                    group[i].file = ReserveStem(assignedStems, stem, group[i], collisions) + ".json";
                    names.Add(group[i].type.FullName + "=" + group[i].count + "->" + group[i].file);
                }
                collisions.Add(key + ": " + string.Join(", ", names.ToArray()));
                Log.Warning("[RimMandrake.RimDefDump] def type name collision — " + key + ": "
                            + string.Join(", ", names.ToArray()));
            }

            // --- pass 2: write ------------------------------------------------
            for (int e = 0; e < entries.Count; e++)
            {
                DefTypeEntry entry = entries[e];
                Type defType = entry.type;

                IEnumerable defs;
                try { defs = AllDefsOf(defType); }
                catch (Exception ex)
                {
                    Log.Warning("[RimMandrake.RimDefDump] cannot enumerate " + defType.FullName + ": " + ex.Message);
                    RecordTypeSkipped(writeFailures, entry, "enumerate: " + ex.GetType().Name + ": " + ex.Message);
                    continue;
                }
                if (defs == null)
                {
                    Log.Warning("[RimMandrake.RimDefDump] " + defType.FullName
                                + " exposes no readable AllDefs; no file written");
                    RecordTypeSkipped(writeFailures, entry, "enumerate: DefDatabase<T>.AllDefs is not readable");
                    continue;
                }

                int n = 0;
                string path = Path.Combine(dir, entry.file);
                try
                {
                    using (StreamWriter sw = Open(path))
                    {
                        var w = new JsonWriter(sw, IndentBulkFiles);
                        w.StartObject();
                        w.Prop("defType", defType.Name);
                        w.Prop("defTypeFullName", defType.FullName);
                        w.Prop("assembly", defType.Assembly.GetName().Name);
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
                    Log.Warning("[RimMandrake.RimDefDump] failed writing " + defType.FullName + ": " + ex.Message);
                    // The StreamWriter above may have flushed a partial, syntactically
                    // broken object before throwing. A file that looks like JSON but
                    // isn't is worse than no file — delete it rather than leave debris
                    // a later reader could try to parse.
                    try { if (File.Exists(path)) File.Delete(path); }
                    catch (Exception delEx)
                    {
                        Log.Warning("[RimMandrake.RimDefDump] also failed deleting the partial "
                                    + path + ": " + delEx.Message);
                    }
                    RecordTypeSkipped(writeFailures, entry, ex.GetType().Name + ": " + ex.Message);
                    continue;
                }
                entry.count = n;
                // Keyed on the FILE stem, which is unique by construction, so
                // defCounts can no longer report one type's count under another
                // type's name.
                counts.Add(new KeyValuePair<string, int>(
                    entry.file.EndsWith(".json") ? entry.file.Substring(0, entry.file.Length - 5) : entry.file, n));
            }

            Log.Message("[RimMandrake.RimDefDump] wrote " + counts.Count + " def-type files to " + dir
                        + " (" + collisions.Count + " simple-name collisions disambiguated)");
        }

        /// <summary>
        /// Claim a unique file stem, CASE-INSENSITIVELY, so no two def types can ever
        /// share a file. Returns <paramref name="stem"/> untouched in the ordinary case —
        /// every existing reader of defs/ThingDef.json is unaffected — and only a genuine
        /// clash gets an assembly suffix, which is written into `defTypeCollisions` so a
        /// reader is never left guessing which type a file holds.
        /// </summary>
        private static string ReserveStem(HashSet<string> assigned, string stem,
                                          DefTypeEntry e, List<string> collisions)
        {
            if (assigned.Add(stem)) return stem;

            string asm = SafeFileName(e.type.Assembly.GetName().Name);
            string candidate = stem + "__" + asm;
            for (int i = 2; !assigned.Add(candidate); i++) candidate = stem + "__" + asm + "_" + i;

            collisions.Add(stem + ": file stem already claimed — " + e.type.FullName
                           + " -> " + candidate + ".json");
            Log.Warning("[RimMandrake.RimDefDump] def-type file stem '" + stem + "' was already claimed; "
                        + e.type.FullName + " goes to " + candidate + ".json instead of overwriting it");
            return candidate;
        }

        /// <summary>
        /// A type that reached pass 2 and produced no file.
        /// ⛔ Clearing <c>entry.file</c> is the load-bearing half: WriteManifest skips a
        /// null-file entry, so without it `defTypes` advertises a file that does not exist
        /// carrying pass 1's count — the manifest claiming more than the capture holds.
        /// </summary>
        private static void RecordTypeSkipped(List<DefTypeWriteFailure> writeFailures,
                                              DefTypeEntry entry, string error)
        {
            writeFailures.Add(new DefTypeWriteFailure
            {
                typeFullName = entry.type.FullName,
                file = entry.file,
                error = error,
            });
            entry.file = null;
        }

        /// <summary>
        /// A type's full name is legal in a filename here (dots are fine), but
        /// nested types use '+' and generics use '`', neither of which is worth
        /// gambling on across filesystems.
        /// </summary>
        private static string SafeFileName(string s)
        {
            var sb = new StringBuilder(s.Length);
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                sb.Append(char.IsLetterOrDigit(c) || c == '.' || c == '_' || c == '-' ? c : '_');
            }
            return sb.ToString();
        }

        /// <summary>
        /// How many defs a type's database holds, without materialising them.
        /// </summary>
        private static int CountDefsOf(Type defType)
        {
            Type db = typeof(DefDatabase<>).MakeGenericType(defType);
            PropertyInfo cp = db.GetProperty("DefCount", BindingFlags.Public | BindingFlags.Static);
            if (cp != null) return (int)cp.GetValue(null, null);

            IEnumerable defs = AllDefsOf(defType);
            if (defs == null) return -1;
            int n = 0;
            foreach (object o in defs) if (o is Def) n++;
            return n;
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
