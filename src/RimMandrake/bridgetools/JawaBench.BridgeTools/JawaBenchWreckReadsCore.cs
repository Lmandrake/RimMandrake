// The Verse-free decisions of four generic reads and acts (item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL):
//   jawa/thing_set_sample      run a ThingSetMakerDef, or a TraderKindDef's stock, N times and list the defs it produced
//   jawa/install_blueprint     place the install blueprint of a carried (minified) building, or the reinstall one of a standing one
//   jawa/study_record          read the game's study (analysis) record for a kind of thing, and the projects that need it
//   jawa/processor_fill        place the inputs of a factory process (PipeSystem's processor holds counts, not a ThingOwner,
//                              so jawa/container_fill cannot reach it; measured from PipeSystem.dll metadata 2026-11-27)
// The game half is JawaBenchWreckTools.cs. Offline harness: src/RimMandrake/bridgetools/WreckReadsSelfTest (net8.0, no RimWorld),
// run by src/RimMandrake/bridgetools/selftest_wreck_reads.py, which plants a fault in each rule and sees its unit go red.
using System;
using System.Collections.Generic;
using System.Linq;

namespace JawaBench.BridgeTools
{
    internal static class JawaBenchWreckReadsCore
    {
        // ------------------------------------------------------------ thing_set_sample
        // LIMIT, a hang guard, not a speed bar: every run happens on the game's main thread inside one bridge call, so a typo
        // such as runs=2000000 freezes the game for minutes and the bridge call dies (danger: a wedged game, seen as the
        // reason for jawa/run_until's cap). The measured need is the scene sc_no_handouts: 200 runs per generator (the vanilla
        // debug output runs 50, DebugOutputsMisc.ThingSetMakerTest). 10 x 200 = 2000.
        public const int MaxRuns = 2000;

        // null when `runs` is allowed, else the refusal (never clamped: a clamped count would pass for the asked one).
        public static string RunsRefusal(int runs)
        {
            if (runs < 1) return "runs must be at least 1, got " + runs + ".";
            if (runs > MaxRuns) return "runs " + runs + " is over " + MaxRuns + " (a hang guard: every run holds the game's main thread).";
            return null;
        }

        public sealed class TallyRow
        {
            public string def;
            public int runsWith;   // runs whose output held this def at least once
            public int things;     // Thing objects of this def over all runs
            public int count;      // stack count summed over all runs
        }

        public sealed class Tally
        {
            public int runs;
            public int emptyRuns;  // runs that produced nothing (a legitimate answer, kept apart from "could not run")
            public int failedRuns; // runs that threw (kept apart from empty: a throw is not "produced nothing")
            public List<string> failures = new List<string>();
            readonly Dictionary<string, TallyRow> rows = new Dictionary<string, TallyRow>(StringComparer.Ordinal);

            // One run's output, as (defName, stackCount) pairs. A null list is a failed run, not an empty one.
            public void AddRun(IList<KeyValuePair<string, int>> made, string failure = null)
            {
                runs++;
                if (made == null)
                {
                    failedRuns++;
                    if (failures.Count < 5) failures.Add(failure ?? "the generator returned null");
                    return;
                }
                if (made.Count == 0) { emptyRuns++; return; }
                var seen = new HashSet<string>(StringComparer.Ordinal);
                foreach (var kv in made)
                {
                    string d = string.IsNullOrEmpty(kv.Key) ? "(no def)" : kv.Key;
                    TallyRow r;
                    if (!rows.TryGetValue(d, out r)) { r = new TallyRow { def = d }; rows[d] = r; }
                    r.things++;
                    r.count += Math.Max(1, kv.Value);
                    if (seen.Add(d)) r.runsWith++;
                }
            }

            // Most often first, then by name, so two reads of one game compare line by line.
            public List<TallyRow> Rows()
            {
                return rows.Values.OrderByDescending(r => r.runsWith).ThenBy(r => r.def, StringComparer.Ordinal).ToList();
            }
        }

        // ------------------------------------------------------------ install_blueprint
        public enum InstallMode { Install, Reinstall, Refused }

        // isMinified: the thing is a MinifiedThing (a carried form); spawned: it lies on a map; held: a pawn carries it or it is in
        // an inventory; innerHasInstallBlueprint: the inner thing's def has an installBlueprintDef. isBuilding: a standing building;
        // buildingMinifiable: its def can be minified. The engine makes an install blueprint only from a MinifiedThing
        // (GenConstruct.PlaceBlueprintForInstall) and a reinstall blueprint only from a spawned building
        // (GenConstruct.PlaceBlueprintForReinstall); anything else is refused by name, never attempted.
        public static InstallMode Classify(bool isMinified, bool spawned, bool held, bool innerHasInstallBlueprint,
                                           bool isBuilding, bool buildingMinifiable, out string why)
        {
            why = null;
            if (isMinified)
            {
                if (!innerHasInstallBlueprint) { why = "the carried thing's inner def has no installBlueprintDef"; return InstallMode.Refused; }
                if (!spawned && !held) { why = "the carried thing is neither on a map nor held by a pawn"; return InstallMode.Refused; }
                return InstallMode.Install;
            }
            if (isBuilding)
            {
                if (!spawned) { why = "the building is not spawned on a map"; return InstallMode.Refused; }
                if (!buildingMinifiable) { why = "the building's def is not minifiable: it has no carried form"; return InstallMode.Refused; }
                if (!innerHasInstallBlueprint) { why = "the building's def has no installBlueprintDef"; return InstallMode.Refused; }
                return InstallMode.Reinstall;
            }
            why = "the thing is neither a carried (minified) building nor a standing building";
            return InstallMode.Refused;
        }

        // ------------------------------------------------------------ study_record
        // The four answers kept apart (no comp, no record, part, complete). The trap this guards: AnalysisManager.IsAnalysisComplete
        // returns TRUE when no record exists, so "never studied" would read as "complete" through it.
        public const string NoComp = "no_study_comp", NoRecord = "no_record", Partial = "partial", Complete = "complete";

        public static string StudyStatus(bool hasComp, bool hasRecord, int timesDone, int required)
        {
            if (!hasComp) return NoComp;
            if (!hasRecord) return NoRecord;
            return timesDone >= required ? Complete : Partial;
        }

        // ResearchProjectDef.AnalyzedThingsCompleted: a required def counts only when its record exists and is satisfied.
        public static int CompletedCount(IEnumerable<string> statuses)
        {
            return statuses.Count(s => s == Complete);
        }

        // ------------------------------------------------------------ processor_fill
        public sealed class FillLine
        {
            public string def;      // the ThingDef to make, or null when the owner takes no thing (a pipe net) or only a category
            public string category; // the ThingCategoryDef when the owner names one and no def
            public string net;      // the PipeNetDef when the owner is filled from a net
            public int have, required, want; // want = what the fill should add
            public string skip;     // why this owner is left alone, null when it is filled
        }

        // have/required per owner, as PipeSystem.ThingAndResourceOwner reports them (Count, Required). `firstOfCategory` is the
        // def the game would take for a category owner (the caller picks it), or null. A net owner is skipped by name: its input
        // comes from a pipe, not a thing.
        public static FillLine Plan(string def, string category, string net, int have, int required, string firstOfCategory)
        {
            var l = new FillLine { def = def, category = category, net = net, have = have, required = required };
            if (!string.IsNullOrEmpty(net) && string.IsNullOrEmpty(def) && string.IsNullOrEmpty(category))
            { l.skip = "fed from the pipe net " + net + ", not by a thing"; return l; }
            if (string.IsNullOrEmpty(l.def) && !string.IsNullOrEmpty(category)) l.def = firstOfCategory;
            if (string.IsNullOrEmpty(l.def)) { l.skip = "names no thing def" + (category != null ? " and the category " + category + " has none" : ""); return l; }
            l.want = Math.Max(0, required - have);
            if (l.want == 0) l.skip = "already full (" + have + " of " + required + ")";
            return l;
        }
    }
}
