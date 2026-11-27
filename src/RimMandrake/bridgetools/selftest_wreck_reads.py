#!/usr/bin/env python3
"""Selftest: the four wreck reads of the bridge (JawaBenchWreckReadsCore.cs and its game half JawaBenchWreckTools.cs).

Item RIMMANDRAKE_SCRIPT_WRECKED_MACHINES_SCENES_EVERY_REPAIR_A_FOIL. The tools:
  jawa/thing_set_sample   run a ThingSetMakerDef, or a TraderKindDef's stock, N times; list the defs it produced
  jawa/install_blueprint  place the install blueprint of a carried building (or the reinstall one of a standing one)
  jawa/study_record       read the game's study record for a kind of thing, and the projects that need it
  jawa/processor_fill     place the inputs of a factory process (PipeSystem's processor)
  jawa/caravan_mass       a caravan's load against its capacity; jawa/caravan_form_load starts the game's own formation

Checks: (1) every unit of WreckReadsSelfTest passes on the production core; (2) each planted fault (one rule broken in a copy of
the core) turns its named unit red; (3) each tool's game half calls its core rule inside its one main-thread hop, so a tool
cannot drift from the rule the units prove. No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_wreck_reads.py [--no-plants]"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchWreckReadsCore.cs"
TOOLS = "JawaBenchWreckTools.cs"
PROJ = os.path.join(HERE, "WreckReadsSelfTest", "WreckReadsSelfTest.csproj")
N_UNITS = 21

# (planted fault: old -> new in the core, the unit that must go red)
PLANTS = [
    ("if (runs < 1) return", "if (runs < 0) return", "runs_refused_below_one"),
    ("if (runs > MaxRuns) return", "if (runs > MaxRuns + 1) return", "runs_refused_over_cap"),
    ("if (made == null)\n                {", "if (made == null || made.Count == 0)\n                {", "tally_empty_apart_from_failed"),
    ("if (seen.Add(d)) r.runsWith++;", "r.runsWith++;", "tally_runs_with_counts_once_per_run"),
    ("r.count += Math.Max(1, kv.Value);", "r.count += kv.Value;", "tally_count_sums_stacks"),
    (".OrderByDescending(r => r.runsWith)", ".OrderBy(r => r.runsWith)", "tally_rows_most_often_first"),
    ("if (!spawned && !held) {", "if (!spawned) {", "install_minified_on_map_or_held"),
    ("if (!spawned && !held) { why", "if (false) { why", "install_refuses_minified_nowhere"),
    ("return InstallMode.Reinstall;", "return InstallMode.Install;", "reinstall_standing_minifiable"),
    ("if (!onThisMap) { why = \"the carried", "if (false) { why = \"the carried", "install_refuses_another_map"),
    ("if (!onThisMap) { why = \"the building", "if (false) { why = \"the building", "install_refuses_another_map"),
    ("if (!buildingMinifiable) {", "if (false) {", "refuse_not_minifiable_building"),
    ("if (!hasRecord) return NoRecord;", "if (!hasRecord) return Complete;", "study_no_record_not_complete"),
    ("return timesDone >= required ? Complete : Partial;", "return timesDone > 0 ? Complete : Partial;", "study_partial_complete"),
    ("statuses.Count(s => s == Complete)", "statuses.Count(s => s != NoComp)", "completed_count_only_complete"),
    ("l.want = Math.Max(0, required - have);", "l.want = required;", "fill_wants_shortfall"),
    ("{ l.skip = \"fed from the pipe net", "{ l.def = net; l.want = required; l.skip = null; return l; l.skip = \"fed from the pipe net",
     "fill_skips_net_owner"),
    ("l.def = firstOfCategory;", "l.def = category;", "fill_category_uses_first_def"),
    ("if (l.want == 0) l.skip", "if (l.want < 0) l.skip", "fill_full_skipped"),
    ("return usage > capacity;", "return usage >= capacity;", "caravan_over_only_above_capacity"),
    ("if (thingsElsewhere > 0) return", "if (thingsElsewhere > 1) return", "form_refuses_no_pawn_or_elsewhere"),
    ("            return null;\n        }\n\n        // ------------------------------------------------------------ processor_fill",
     "            return \"PassDoors\";\n        }\n\n        // ------------------------------------------------------------ processor_fill", "traverse_mode_named_or_refused"),
    ('"NoPassClosedDoorsOrWater" };', '"NoPassClosedDoorsOrWater", "PassAllDestroyableThings" };', "traverse_mode_named_or_refused"),
]

# (tool, the core call that must sit inside its main-thread hop)
WIRING = [
    ("jawa/thing_set_sample", [r"JawaBenchWreckReadsCore\.RunsRefusal\(runs\)", r"new JawaBenchWreckReadsCore\.Tally\(\)",
                               r"tally\.AddRun\(", r"tally\.Rows\(\)", r"\.Destroy\("]),
    ("jawa/install_blueprint", [r"JawaBenchWreckReadsCore\.Classify\(", r"GenConstruct\.PlaceBlueprintForInstall\(",
                                r"GenConstruct\.PlaceBlueprintForReinstall\(", r"GenConstruct\.CanPlaceBlueprintAt\(",
                                r"JawaBenchWreckReadsCore\.Classify\([^;]*t\.MapHeld == map"]),
    ("jawa/study_record", [r"JawaBenchWreckReadsCore\.StudyStatus\(", r"JawaBenchWreckReadsCore\.CompletedCount\(",
                           r"Find\.AnalysisManager\.TryGetAnalysisProgress\(", r"requiredAnalyzed"]),
    ("jawa/processor_fill", [r"JawaBenchWreckReadsCore\.Plan\(", r"\"AddFromThing\"", r"\"IngredientsOwners\"", r"\"processes\"\) as IEnumerable"]),
    ("jawa/caravan_mass", [r"JawaBenchWreckReadsCore\.OverCapacity\(", r"CollectionsMassCalculator\.Capacity\(",
                           r"CollectionsMassCalculator\.MassUsage\("]),
    ("jawa/reach_edge", [r"JawaBenchWreckReadsCore\.TraverseModeName\(", r"reachability\.CanReachMapEdge\("]),
    ("jawa/caravan_form_load", [r"JawaBenchWreckReadsCore\.FormRefusal\(", r"CaravanFormingUtility\.StartFormingCaravan\(",
                                r"new TransferableOneWay\(\)"]),
]


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def units(core_text):
    """Build the harness with this core text and run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="WreckReads_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_wreck_reads.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="WreckReadsSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
        if rc:
            raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
        dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\WreckReadsSelfTest.dll"
        # hang guard: a planted core may loop; a real run takes under a second (measured 2026-11-27)
        pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True,
                                           cwd="/mnt/d/Luke/dev" if os.path.isdir("/mnt/d/Luke/dev") else None, timeout=180)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built or run: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U ") and not ln.startswith("U-count"):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-300:], pr.stderr[-300:]))
    return out


def nocomment(s):
    return re.sub(r"//[^\n]*", "", s)


def tool_body(text, tool):
    s = nocomment(text)
    i = s.find('"%s"' % tool)
    j = s.find("[Tool(", i + 1) if i >= 0 else -1
    return s[i:j if j > i else len(s)] if i >= 0 else ""


def wiring(tools_text):
    bad = []
    for tool, pats in WIRING:
        body = tool_body(tools_text, tool)
        if not body:
            bad.append("%s is not declared in %s" % (tool, TOOLS))
            continue
        if body.count("MainThread.InvokeAsync") != 1:
            bad.append("%s must have exactly one main-thread hop" % tool)
            continue
        hop = body[body.index("MainThread.InvokeAsync"):]
        for p in pats:
            if not re.search(p, hop):
                bad.append("%s lacks /%s/ in its main-thread hop" % (tool, p))
    return bad


def main(argv):
    fails, plants = [], "--no-plants" not in argv
    try:
        core = read(os.path.join(CS, CORE))
        clean = units(core)
    except (OSError, Unmeasured) as e:
        print("selftest_wreck_reads: UNMEASURED: %s" % e)
        return 1
    for name, res in sorted(clean.items()):
        if res != "ok":
            fails.append("unit %s on the production core: %s" % (name, res))
    try:
        fails += wiring(read(os.path.join(CS, TOOLS)))
    except OSError as e:
        fails.append("could not read %s: %s" % (TOOLS, e))
    if plants:
        for old, new, unit in PLANTS:
            if old not in core:
                fails.append("plant for %s no longer matches the core (%r)" % (unit, old[:40]))
                continue
            try:
                got = units(core.replace(old, new, 1))
            except Unmeasured as e:
                fails.append("plant for %s: UNMEASURED: %s" % (unit, e))
                continue
            if got.get(unit, "").startswith("ok"):
                fails.append("plant for %s stayed green" % unit)
    for f in fails:
        print("  FAIL " + f)
    print("selftest_wreck_reads: %s (%d units, %d plants, %d tool wirings)" % (
        "FAIL" if fails else "PASS", len(clean), len(PLANTS) if plants else 0, len(WIRING)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
