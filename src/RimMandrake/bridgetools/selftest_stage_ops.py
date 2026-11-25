#!/usr/bin/env python3
"""Selftest: the stage read-back (JawaBenchStageReadBack.cs) and its ten staging tools. Page:
design/specs/2026-11-23-bridge-v2/boundary.md §THE STAGE READ-BACK, one test per promise, 6 checks. Each plant breaks one rule of a
copy of the core (or of a tool's call site) and must turn its named check red; the ticket's two plants are marked *. The call sites
in the game half are read from the source: a rule that no tool calls, or calls with a request value, or in a later hop, is red.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_stage_ops.py [--no-plants]"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchStageReadBack.cs"
TT, MT = "JawaBenchTerrainTools.cs", "JawaBenchMapTools.cs"
PT, JT = "JawaBenchPawnTools.cs", "JawaBenchJobTools.cs"
PROJ = os.path.join(HERE, "StageOpsSelfTest", "StageOpsSelfTest.csproj")
N_UNITS = 6


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def units(core_text):
    """Build the harness with this core text, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="StageOps_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_stage_ops.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="StageOpsSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
        if rc:
            raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
        dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\StageOpsSelfTest.dll"
        # hang guard: a planted core may loop; a real run takes under a second
        pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev" if os.path.isdir("/mnt/d/Luke/dev") else None, timeout=180)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built or run: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U "):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-300:], pr.stderr[-300:]))
    return out


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(read(os.path.join(CS, CORE)))
    return _CLEAN[0].get(name, "FAIL did not run")


def nocomment(s):
    return re.sub(r"//[^\n]*", "", s)


def tool_body(text, tool):
    """The source of one [Tool] method, with no comment: from its name to the next [Tool(."""
    s = nocomment(text)
    i = s.find('"%s"' % tool)
    j = s.find("[Tool(", i + 1) if i >= 0 else -1
    return s[i:j if j > i else len(s)] if i >= 0 else ""


def hop(body):
    """The text of the tool's one main-thread lambda: from InvokeAsync to its closing `}, cancellationToken)` or `});`."""
    i = body.find("MainThread.InvokeAsync")
    if i < 0:
        return ""
    m = re.compile(r"\n            \}(, cancellationToken)?\)").search(body, i)
    return body[i:m.start()] if m else ""


# (tool, file, the patterns that must be in its hop: each Got reads the game, never the request)
WIRING = [
    ("jawa/set_terrain_batch", TT, [r'StageReadBack\.Open\("jawa/set_terrain_batch", UnityEngine\.Time\.frameCount\)',
                                    r'var after = ReadLayer\(grid, cell, layer\);\s*rb\.Made\("terrain", null, cx, cz\)\.Want\("terrain", def\.defName\)\.Got\("terrain", after\?\.defName\);',
                                    r'StageReadBack\.Reply\(rb, UnityEngine\.Time\.frameCount\)', r'success = [^;]*\(bool\)readBack\["ok"\];', r'\breadBack,']),
    ("jawa/destroy_batch", TT, [r'StageReadBack\.Open\("jawa/destroy_batch", UnityEngine\.Time\.frameCount\)',
                                r'thing\.Destroy\(DestroyMode\.Vanish\);\s*rb\.Made\("gone", thing\.ThingID, cx, cz\)\.Want\("destroyed", "True"\)\.Got\("destroyed", thing\.Destroyed \? "True" : "False"\)',
                                r'foreach \(var cell in seen\)\s*foreach \(var thing in map\.thingGrid\.ThingsListAtFast\(cell\)\).*"still standing after the clean", true\);',
                                r'StageReadBack\.Reply\(rb, UnityEngine\.Time\.frameCount\)', r'ok = [^;]*\(bool\)readBack\["ok"\];', r'\breadBack,']),
    ("jawa/spawn_pawn", TT, [r'StageReadBack\.Open\("jawa/spawn_pawn", UnityEngine\.Time\.frameCount\)',
                             r'var kindNow = pawn\.kindDef\?\.defName;', r'\.Want\("kind", kind\.defName\)\.Got\("kind", kindNow\)',
                             r'\.Got\("spawned", pawn\.Spawned \? "True" : "False"\)', r'\.Got\("faction", pawn\.Faction\?\.def\?\.defName\)\.Got\("xenotype", xenoNow\)',
                             r'var xenoNow = pawn\.genes\?\.Xenotype\?\.defName;',
                             r'StageReadBack\.Reply\(rb, UnityEngine\.Time\.frameCount\)', r'success = [^;]*\(bool\)readBack\["ok"\],', r'\breadBack,']),
    ("jawa/build_batch", MT, [r'StageReadBack\.Open\("jawa/build_batch", Time\.frameCount\)',
                              r'\.Want\("def", td\.defName\)\.Got\("def", spawned\.def\.defName\)', r'\.Got\("stuff", spawned\.Stuff\?\.defName\)',
                              r'\.Got\("cell", spawned\.Position\.x \+ "," \+ spawned\.Position\.z\)', r'\.Got\("rot", spawned\.Rotation\.AsInt\.ToString\(\)\)',
                              r'\.Got\("hp", spawned\.def\.useHitPoints \? spawned\.HitPoints\.ToString\(\) : null\)', r'row\.Got\("quality", rq\.Quality\.ToString\(\)\)',
                              r'StageReadBack\.Reply\(rb, Time\.frameCount\)', r'success = [^,]*\(bool\)stageBack\["ok"\],', r'readBack = stageBack,']),
]


PAWN_WIRING = [
    ("pawn_gear", PT, r'(?:DestroyAllEquipment|DestroyAll|MakeRoomFor|AddEquipment|Wear|TryAddOrTransfer)\(', [
        r'\.Got\("remaining", p\.equipment\.AllEquipmentListForReading\.Count\.ToString\(\)\)',
        r'\.Got\("remaining", p\.apparel\.WornApparel\.Count\.ToString\(\)\)',
        r'\.Got\("remaining", p\.inventory\.innerContainer\.Count\.ToString\(\)\)',
        r'p\.equipment\.AddEquipment\(t\);\s*var held = p\.equipment\.Primary;',
        r'\.Got\("primary", \(held == t\)\.ToString\(\)\)',
        r'p\.apparel\.Wear\(ap, true, false\);\s*var held = p\.apparel\.WornApparel\.FirstOrDefault\(a => a == ap\);',
        r'var matching = inventory\.Where\(item => item\.def == td && item\.Stuff == sd && PawnGearQuality\(item\) == wantedQuality\);\s*int before = matching\.Sum\(item => item\.stackCount\);',
        r'inventory\.TryAddOrTransfer\(t, wantedCount\);\s*int added = matching\.Sum\(item => item\.stackCount\) - before;',
        r'\.Got\("count", added\.ToString\(\)\)',
        r'\.Got\("def", held\?\.def\.defName\)\.Got\("stuff", held\?\.Stuff\?\.defName\)',
        r'\.Got\("quality", PawnGearQuality\(held\)\)',
    ]),
    ("pawn_traits", PT, r'ts\.(?:GainTrait|RemoveTrait)\(', [
        r'ts\.GainTrait\([^;]+;\s*var held = ts\.allTraits\.FirstOrDefault\(t => t\.def == td\);',
        r'\.Got\("degree", held\?\.Degree\.ToString\(\)\)',
        r'ts\.RemoveTrait\(have\);\s*bool present = ts\.HasTrait\(td\);',
        r'\.Got\("present", present\.ToString\(\)\)',
    ]),
    ("set_pawn_skill", PT, r'sr\.(?:Level|passion|xpSinceLastLevel) =', [
        r'var after = new \{ levelRaw = sr\.GetLevel\(false\), levelEffective = sr\.Level, passion = sr\.passion\.ToString\(\), xp = sr\.xpSinceLastLevel \};',
        r'\.Got\("levelRaw", after\.levelRaw\.ToString\(\)\)',
        r'\.Got\("passion", after\.passion\)', r'\.Got\("xp", after\.xp\.ToString\("R", CultureInfo\.InvariantCulture\)\)',
    ]),
    ("pawn_need", PT, r'n\.CurLevelPercentage =|\.TryGainMemory\(', [
        r'n\.CurLevelPercentage = wanted;\s*var held = p\.needs\.TryGetNeed\(nd\);',
        r'\.Got\("level", held\?\.CurLevel\.ToString\("R", CultureInfo\.InvariantCulture\)\)',
        r'\.Got\("percentage", held\?\.CurLevelPercentage\.ToString\("R", CultureInfo\.InvariantCulture\)\)',
        r'tracker\.TryGainMemory\(td, other\);\s*var held = tracker\.Memories\.FirstOrDefault\(m => m\.def == td && m\.otherPawn == other\);',
        r'\.Got\("thought", held\?\.def\.defName\)',
    ]),
    ("pawn_health", PT, r'gp\.IsPermanent = true|\.RemoveHediff\(|\.RestorePart\(|\.AddHediff\(', [
        r'gp\.IsPermanent = true;\s*var held = p\.health\.hediffSet\.hediffs\.FirstOrDefault\(x => x == hx\);',
        r'\.Got\("permanent", heldComp\?\.IsPermanent\.ToString\(\)',
        r'\.Got\("remaining", p\.health\.hediffSet\.hediffs\.Count\(PawnHealthHealable\)\.ToString\(\)\)',
        r'\.Got\("present", p\.health\.hediffSet\.hediffs\.Contains\(h\)\.ToString\(\)\)',
        r'\.Got\("remaining", p\.health\.hediffSet\.hediffs\.Count\(h => IsOnPartOrChild\(h\.Part, part\)\)\.ToString\(\)\)',
        r'var held = p\.health\.hediffSet\.hediffs\.FirstOrDefault\(x => x == h\);',
        r'\.Got\("severity", held\?\.Severity\.ToString\("R", CultureInfo\.InvariantCulture\)\)',
    ]),
    ("set_work_priority", JT, r'\.EnableAndInitializeIfNotAlreadyInitialized\(|\.SetPriority\(|\.useWorkPriorities =', [
        r'pawn\.workSettings\.SetPriority\(wd, priority\);\s*var readBack = pawn\.workSettings\.GetPriority\(wd\);',
        r'var priorities = HarmonyLib\.AccessTools\.Field\(typeof\(Pawn_WorkSettings\), "priorities"\)\s*\?\.GetValue\(pawn\.workSettings\) as DefMap<WorkTypeDef, int>;',
        r'\.Got\("priority", priorities\?\[wd\]\.ToString\(\)\)',
        r'\.Got\("effectivePriority", readBack\.ToString\(\)\)',
        r'var manualPrioritiesOn = Find\.PlaySettings\?\.useWorkPriorities \?\? false;',
        r'\.Got\("manualPrioritiesOn", manualPrioritiesOn\.ToString\(\)\)',
    ]),
]


def wiring_sources():
    return {f: read(os.path.join(CS, f)) for f in (TT, MT, PT, JT)}


def pawn_wiring(tool, body, write, pats):
    h = hop(body)
    if body.count("MainThread.InvokeAsync") != 1 or not h:
        return "%s must have one main-thread hop" % tool
    block = "stageReadBack" if tool == "jawa/set_work_priority" else "readBack"
    frame = "UnityEngine.Time.frameCount" if block == "stageReadBack" else "Time.frameCount"
    opening = 'var rb = StageReadBack.Open("%s", %s);' % (tool, frame)
    reply = "var %s = StageReadBack.Reply(rb, %s);" % (block, frame)
    if (body.count("StageReadBack.Open(") != 1 or body.count("StageReadBack.Reply(") != 1
            or opening not in h or reply not in h):
        return "%s lacks an in-hop StageReadBack reply" % tool
    writes = list(re.finditer(write, h))
    if not writes or not h.index(opening) < writes[0].start() < writes[-1].end() < h.index(reply):
        return "%s writes outside its StageReadBack" % tool
    reads = h[writes[0].start():h.index(reply)]
    for p in pats:
        if not re.search(p, reads, re.S):
            return "%s lacks a game read after writing (/%s/)" % (tool, p)
    returns = h[h.index(reply):].split("return ")[1:]
    if not returns or any(not re.search(r'success = \(bool\)%s\["ok"\].*?\b%s,' % (block, block), ret, re.S)
                          for ret in returns):
        return "%s does not return the StageReadBack and its verdict" % tool
    if tool == "jawa/set_pawn_skill" and "wroteLevel = level >= 0 ? (object)after.levelRaw : null" not in returns[0]:
        return "%s does not report its read level in wroteLevel" % tool
    return None


def wired(srcs=None):
    """Null when every staging tool opens, reads back and replies inside its one hop."""
    srcs = srcs or wiring_sources()
    for tool, f, pats in WIRING:
        h = hop(tool_body(srcs[f], tool))
        if not h:
            return "FAIL not wired: %s has no main-thread hop in %s" % (tool, f)
        if h.count("StageReadBack.Open(") != 1 or h.count("StageReadBack.Reply(") != 1:
            return "FAIL not wired: %s opens %d and replies %d times inside its hop, want 1 and 1" % (tool, h.count("StageReadBack.Open("), h.count("StageReadBack.Reply("))
        if h.find("StageReadBack.Open(") > h.find("StageReadBack.Reply("):
            return "FAIL not wired: %s replies before it opens" % tool
        for p in pats:
            if not re.search(p, h, re.S):
                return "FAIL not wired: %s lacks /%s/ in its hop" % (tool, p[:90])
    faults = [pawn_wiring("jawa/" + tool, tool_body(srcs[f], "jawa/" + tool), write, pats)
              for tool, f, write, pats in PAWN_WIRING]
    faults = [f for f in faults if f]
    if faults:
        return "FAIL not wired: " + "; ".join(faults)
    return None


def t_a_reply_is_built_from_the_read_back_never_the_request():
    return wired() or unit("a_reply_is_built_from_the_read_back_never_the_request")


def t_a_replaced_pawn_kind_is_reported_as_made():
    return wired() or unit("a_replaced_pawn_kind_is_reported_as_made")


def t_the_write_and_the_read_back_share_one_frame():
    return wired() or unit("the_write_and_the_read_back_share_one_frame")


def t_a_clean_that_left_a_thing_names_it():
    return wired() or unit("a_clean_that_left_a_thing_names_it")


def t_a_refusal_by_name_leaves_nothing_made():
    return unit("a_refusal_by_name_leaves_nothing_made")


def t_two_builds_of_one_request_give_equal_digests():
    return unit("two_builds_of_one_request_give_equal_digests")


CORE_PLANTS = [
    ("* a reply that echoes the request", "a_reply_is_built_from_the_read_back_never_the_request",
     [("foreach (var kv in r.Gots) got[kv.Key] = kv.Value;", "foreach (var kv in r.Wants) got[kv.Key] = kv.Value;")]),
    ("* a clean that reports success with a corpse left", "a_clean_that_left_a_thing_names_it",
     [('if (blocking > 0) faults.Add("left_behind");', "")]),
    ("a read that is never compared", "a_replaced_pawn_kind_is_reported_as_made", [("if (!Gots.TryGetValue(kv.Key, out got)) got = null;", "got = kv.Value;")]),
    ("a moved frame passes", "the_write_and_the_read_back_share_one_frame", [("bool sameFrame = frameNow == rb.FrameOpen;", "bool sameFrame = true;")]),
    ("a refusal reads ok", "a_refusal_by_name_leaves_nothing_made", [('if (rb._refusal != null) faults.Add("refused");', "")]),
    ("a refusal hides what it made", "a_refusal_by_name_leaves_nothing_made", [("                if (made.Count < ListedWrong) made.Add(RowOut(r, null));", "                if (rb._refusal == null) made.Add(RowOut(r, null));")]),
    ("the digest holds the id", "two_builds_of_one_request_give_equal_digests", [(".Append(Op).Append('|')", ".Append(Op).Append(Id).Append('|')")]),
    ("the digest follows the order", "two_builds_of_one_request_give_equal_digests", [("lines.Sort(StringComparer.Ordinal);", "")]),
    ("the digest ignores the read values", "two_builds_of_one_request_give_equal_digests", [("Append('=').Append(kv.Value ?? \"~\")", "Append('=')")]),
]

# call-site plants: each turns the wiring red, so every check that reads the wiring goes red
SITE_PLANTS = [
    ("terrain echoes the request", "set_terrain_batch", TT, 'Got("terrain", after?.defName)', 'Got("terrain", def.defName)'),
    ("spawn_pawn echoes the kind asked", "spawn_pawn", TT, 'Got("kind", kindNow)', 'Got("kind", kind.defName)'),
    ("build_batch echoes the def asked", "build_batch", MT, 'Got("def", spawned.def.defName)', 'Got("def", td.defName)'),
    ("destroy_batch never reads the cells again", "destroy_batch", TT, '"still standing after the clean", true);', '"still standing after the clean", false);'),
    ("destroy_batch's success ignores the read-back", "destroy_batch", TT, 'bool ok = seen.Count > 0 && outOfBounds == 0 && (bool)readBack["ok"];', 'bool ok = seen.Count > 0 && outOfBounds == 0;'),
    ("pawn_need echoes the requested level", "pawn_need", PT,
     'Got("percentage", held?.CurLevelPercentage.ToString("R", CultureInfo.InvariantCulture))',
     'Got("percentage", wanted.ToString("R", CultureInfo.InvariantCulture))'),
]


def plants():
    good, src = True, read(os.path.join(CS, CORE))
    for name, must, subs in CORE_PLANTS:
        t = src
        for old, new in subs:
            if t.count(old) != 1:
                print("FAIL plant %r: its text is in %s %d times, want 1: %r" % (name, CORE, t.count(old), old[:70]))
                good = False
            t = t.replace(old, new)
        try:
            red = sorted(u for u, v in units(t).items() if v != "ok")
        except Unmeasured as e:
            red = ["UNMEASURED %s" % e]
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    srcs = wiring_sources()
    for name, tool, f, old, new in SITE_PLANTS:
        if srcs[f].count(old) != 1:
            print("FAIL plant %r: its text is in %s %d times, want 1" % (name, f, srcs[f].count(old)))
            good = False
            continue
        s2 = dict(srcs)
        s2[f] = srcs[f].replace(old, new)
        v = wired(s2)
        hit = v is not None and "jawa/" + tool in v
        good = good and hit
        print("%s plant %r turns the wiring red: %s" % ("ok  " if hit else "FAIL", name, v), flush=True)
    return good


def main(argv):
    tests = [t_a_reply_is_built_from_the_read_back_never_the_request, t_a_replaced_pawn_kind_is_reported_as_made,
             t_the_write_and_the_read_back_share_one_frame, t_a_clean_that_left_a_thing_names_it,
             t_a_refusal_by_name_leaves_nothing_made, t_two_builds_of_one_request_give_equal_digests]
    bad = 0
    try:
        for t in tests:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v))
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL stage ops UNMEASURED: %s" % e)
        return 1
    print("stage ops: %d of %d checks passed%s" % (len(tests) - bad, len(tests), "" if "--no-plants" in argv else ", plants %s" % ("all red" if good else "NOT all red")))
    return 0 if not bad and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
