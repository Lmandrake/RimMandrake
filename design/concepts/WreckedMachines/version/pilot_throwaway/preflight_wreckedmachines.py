#!/usr/bin/env python3
"""THROWAWAY Stage 2 preflight for WreckedMachines, the version that VERSION.json names. No model.

After design/concepts/Pyrelands/version/pilot_throwaway/preflight_pyre_0_2_0.py (steward run
RIMMANDRAKE_STEWARD_WRECKEDMACHINES_PREFLIGHT_STAGE). It checks version/test_table.json against the repo, the def dump and
the mod lists, by the exit of Stage 2 (design/specs/2026-11-13-maturation-pipeline.md, "Stage 2: Preflight"), and writes
version/preflight.json: each check, pass or refuse, the smallest fix for each refusal, its route, and the seconds it took.

A refusal with route "Stage 3" is build work on a sound bar (a check whose code is not written, a text the build changes, a
tier the build defines). A refusal with route "Stage 1" is a fault of the spec or of the table.

Usage: python3 preflight_wreckedmachines.py <repo> [--table <file>] [--out <file>] [--dump <defs.sqlite>]
  --table  read another table (a planted copy: the checks are shown refusing on it); --out writes the record elsewhere.
Exit 0 pass, 1 refuse, 2 could not look.
"""
import datetime
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import time

T0 = time.time()
REPO = os.path.abspath(sys.argv[1])
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
from game_paths import DUMP_ROOT  # noqa: E402
import designer_stage as D  # noqa: E402


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


C = "design/concepts/WreckedMachines"
M = "src/RimMandrake/WreckedMachines"
VAL = M + "/validation.py"
DUMP = arg("--dump", os.path.join(str(DUMP_ROOT), "defs.sqlite"))
TABLE = arg("--table", C + "/version/test_table.json")
OUT = arg("--out", C + "/version/preflight.json")
try:
    VERSION = json.load(open(C + "/version/VERSION.json"))
    tab = json.load(open(TABLE))
    tests, bars = tab["tests"], tab["bars"]
    tree = json.load(open(C + "/tree.json"))
    scenes = json.load(open(C + "/scenes.json"))
    locked = json.load(open(C + "/version/locked_bars.json"))["ids"]
    small = json.load(open(C + "/version/small_list.json"))
    valsrc = open(VAL, errors="replace").read()
    con = sqlite3.connect("file:" + DUMP + "?mode=ro&immutable=1", uri=True)
    prov = dict(con.execute("select key, value from provenance"))
    defs = set(x[0] for x in con.execute("select def_name from defs"))
    pkgs = set(x[0].lower() for x in con.execute("select package_id from mods") if x[0])
except Exception as e:      # could not look: no record is written
    print("COULD NOT LOOK: %s: %s" % (type(e).__name__, e))
    sys.exit(2)
VER = VERSION["version"]
S = {s["id"]: s for s in scenes["scenes"]}
LEAF = {l["id"] for l in tree["leaves"]}
checks = []


def check(cid, what, refusals, evidence, smallest_fix=None, route=None, t=None):
    checks.append(dict(id=cid, what=what, verdict="refuse" if refusals else "pass", refusals=refusals, evidence=evidence,
                       smallest_fix=smallest_fix if refusals else None, route=route if refusals else None,
                       seconds=round(time.time() - t, 3) if t else None))


def live(v):
    return str(v.get("kind", "")).startswith("live")


def deciders():
    return {d: [b["id"] for b in bars if d in (b.get("decides") or [])] for b in bars for d in (b.get("decides") or [])}


# C0 the version is locked, and the table is this version's
t = time.time()
r = []
if not str(VERSION.get("state", "")).startswith("locked"):
    r.append("VERSION.json state is %r" % VERSION.get("state"))
if str(tab.get("version")) != str(VER):
    r.append("the table is for version %r, VERSION.json names %r" % (tab.get("version"), VER))
check("C0_version_locked", "the Design Version is locked, and the test table is for it", r, "VERSION.json %s, state %s"
      % (VER, VERSION.get("state")), "remake the table for the locked version", "Stage 1", t)

# C1 the table holds exactly the locked bars
t = time.time()
have = [b.get("id") for b in bars]
check("C1_bars_complete", "the table holds exactly the locked bars (version/locked_bars.json), each once",
      sorted(set(locked) ^ set(have)) + (["duplicate bar ids"] if len(have) != len(set(have)) else []),
      "%d locked, %d in the table" % (len(locked), len(have)), "remake the table from the locked bars", "Stage 1", t)

# C2 every bar names its check
t = time.time()
r = []
for b in bars:
    if not b.get("decides"):
        r.append("%s: no deciding test" % b["id"])
    for x in (b.get("decides") or []) + (b.get("supports") or []):
        if x not in tests:
            r.append("%s names undefined test %s" % (b["id"], x))
    for x in b.get("decides") or []:
        if x in tests and (tests[x].get("support_only") or tests[x].get("kind") in ("exploration", "look")):
            r.append("%s is decided by %s, which accepts no bar (%s)" % (b["id"], x, tests[x].get("kind")))
    for x in b.get("offline_decides") or []:
        if x not in (b.get("decides") or []) or tests.get(x, {}).get("kind") != "offline":
            r.append("%s: offline_decides names %s, which is not an offline test among its deciders" % (b["id"], x))
check("C2_every_bar_has_a_test", "every bar names at least one deciding test; every named test is defined; no exploration, "
      "look or support-only row decides a bar", r, "%d bars" % len(bars), "name the test", "Stage 1", t)

# C3 every check names its stage
t = time.time()
r = ["%s: stage %r" % (k, v.get("stage")) for k, v in tests.items() if v.get("stage") not in ("2", "4-5", "6", "8")]
r += ["%s: kind %r at stage %s" % (k, v.get("kind"), v.get("stage")) for k, v in tests.items()
      if (v.get("kind") == "offline" and v.get("stage") != "4-5") or (live(v) and v.get("stage") != "6")
      or (v.get("kind") == "look" and v.get("stage") != "8")]
r += ["%s: proves_at %r is not the highest stage of its deciders" % (b["id"], b.get("proves_at")) for b in bars
      if b.get("decides") and all(d in tests for d in b["decides"])
      and b.get("proves_at") != max((tests[d].get("stage") or "" for d in b["decides"]),
                                    key=lambda s: {"4-5": 1, "6": 2, "8": 3}.get(s, 0))]
check("C3_every_test_has_a_stage", "every test names a stage of 2, 4-5, 6 or 8 that fits its kind, and each bar proves at the "
      "highest stage of its deciders", r, "%d tests" % len(tests), "set the stage", "Stage 1", t)

# C4, C5 every named file is real
t = time.time()
r4, r5 = [], []
for k, v in tests.items():
    f = (v.get("file") or "").split(" ")[0]
    if v.get("kind") not in ("look", "exploration") and not v.get("new") and not (f and os.path.exists(f)):
        r4.append("%s: %s" % (k, f or "no file"))
    for p in v.get("reads") or []:
        if not os.path.exists(p):
            r5.append("%s reads %s" % (k, p))
for f in (tab.get("unlisted_suites") or {}):
    if not os.path.exists(f):
        r4.append("unlisted suite " + f)
check("C4_test_files_real", "every built test's file exists", r4, "%d built tests" % sum(
    1 for v in tests.values() if v.get("kind") not in ("look", "exploration") and not v.get("new")), "fix the path", "Stage 1", t)
check("C5_read_files_real", "every file or folder that a test reads exists", sorted(set(r5)), "", "fix the path", "Stage 1", t)

# C6 the deciders: a built one runs; a specified one is Stage 3 work, not a refusal (spec, Stage 2 exit)
t = time.time()
r, r_flag, owed = [], [], []
dec = deciders()
for k, users in sorted(dec.items()):
    v = tests.get(k)
    if not v:
        continue
    f = (v.get("file") or "").split(" ")[0]
    if v.get("new"):
        built = D.entry_point_exists(".", "%s::%s" % (f, v["entry"])) if v.get("entry") else bool(f) and os.path.exists(f)
        if built:
            r_flag.append("%s: marked new (built in Stage 3), but %s is already built: clear the flag" % (k, v.get("entry") or f))
        else:
            owed.append(k)
        continue
    if v.get("entry"):
        real = D.entry_point_exists(".", "%s::%s" % (f, v["entry"]))
        if real != bool(v.get("entry_exists")):
            r_flag.append("%s: the table says entry_exists %s; %s::%s reads %s" % (k, v.get("entry_exists"), f, v["entry"], real))
        if not real:
            r.append("%s: entry %s::%s is not written (item %s); it decides %s" % (k, f, v["entry"], v.get("item"), ", ".join(users)))
            continue
    if v.get("kind") == "offline":
        rt = v.get("runs_today") or {}
        if not rt.get("ran"):
            r.append("%s: a built offline decider with no run today; it decides %s" % (k, ", ".join(users)))
        elif rt.get("result") != "PASS":
            r.append("%s: red today (rc %s: %s); it decides %s. %s" % (
                k, rt.get("rc"), (rt.get("last") or "")[:120], ", ".join(users), v.get("red_today") or "No reason is written"))
check("C6a_table_flags_true", "the table's flags are true: no test marked new is already built, and each entry_exists equals "
      "what the file holds", r_flag, "read with designer_stage.entry_point_exists", "remake the table", "Stage 1", t)
check("C6_built_deciders_run", "every built deciding test runs green today; a deciding test that is specified and not built is "
      "Stage 3 work, not a refusal", r,
      "%d deciding tests; %d not green or not written; %d specified for Stage 3: %s"
      % (len(dec), len(r), len(owed), ", ".join(owed) or "none"),
      "Stage 3 does the build work that each line names, then remakes the table", "Stage 3 (the bar is sound; the build is owed)", t)

# C7 a game-stage test says why the game is needed; a full-list test says why
t = time.time()
r = []
for k, v in tests.items():
    needs = live(v) or (v.get("kind") == "exploration" and v.get("stage") == "6")
    if needs and len(str(v.get("why_game") or "")) < 40:
        r.append("%s: no reason the game is needed" % k)
    if v.get("kind") == "live_full" and not v.get("why_full_list"):
        r.append("%s: no reason the full list is needed" % k)
check("C7_game_reason_written", "every in-game test says why an offline test cannot decide it; every full-list test says why", r,
      "%d in-game tests; whether each reason is true is the Stage 4 challenger's question, not this program's"
      % sum(1 for v in tests.values() if live(v)), "write the reason", "Stage 1", t)

# C8 every held look statement for this mod is placed
t = time.time()
r, hits = [], []
GREP = r"wreck|kludg|refurbish|smelter|vanometric|emanator|ancient component|alloy forge"
for f in sorted(glob.glob("design/RimMandrake/validation_holding/*.md")):
    for n, line in enumerate(open(f, errors="replace").read().splitlines(), 1):
        if re.search(GREP, line, re.I):
            hits.append("%s:%d" % (f, n))
placed = {h.get("source") for h in tab.get("held_statements") or []}
for h in hits:
    if h not in placed and h not in str(tab.get("held_note")):
        r.append("%s names this mod's words and is neither placed nor named in held_note" % h)
check("C8_held_statements_placed", "every held look statement for this mod is placed on a bar and a test (the placement is the "
      "ingest)", r, "%d line(s) of design/RimMandrake/validation_holding/*.md match %r; %d placed; the table's note: %s"
      % (len(hits), GREP, len(placed), tab.get("held_note")), "place the line, or name it in held_note as another mod's", "Stage 1", t)

# C9 every def named is real
t = time.time()
r = []
stext = json.dumps(scenes) + json.dumps(tree) + open(C + "/plan.md").read() + json.dumps(tests)
repo_defs, cs_types, stems = set(), set(), set()
for f in glob.glob("src/Rim*/**/Defs/**/*.xml", recursive=True) + glob.glob("src/Rim*/**/Patches/**/*.xml", recursive=True):
    repo_defs |= set(re.findall(r"<defName>(\w+)</defName>", open(f, errors="replace").read()))
    stems.add(os.path.basename(f)[:-4])
for f in glob.glob("src/Rim*/**/Source/**/*.cs", recursive=True):
    cs_types |= set(re.findall(r"\b(?:class|struct|enum)\s+((?:RM|RUT|RSW)_\w+)\b", open(f, errors="replace").read()))
OURS = re.compile(r"^(RM|RUT|RSW)_")
m_orig = re.search(r"^ORIGINAL = \{(.*?)\}", valsrc, re.M | re.S)
m_misc = re.search(r"^LAMP, WALL, BENCH, RUBBLE, SLAG = (.*)$", valsrc, re.M)
script_defs = set(re.findall(r'"\s*:\s*"(\w+)"', m_orig.group(1)) if m_orig else []) | set(re.findall(r'"(\w+)"', m_misc.group(1)) if m_misc else [])
named = set(re.findall(r"\b((?:RM|RUT|RSW)_[A-Za-z0-9_]+)\b", stext)) | set(re.findall(r"\b(VFEFactory_\w+)\b", stext)) | script_defs


def def_verdict(d):
    if OURS.match(d):
        return None if (d in repo_defs or d in cs_types or d in stems) else d + " (our prefix; not in the repo's Defs, Patches or C# types)"
    return None if (d in defs or d in repo_defs) else d + " (not in the def dump of %s, nor the repo)" % prov.get("captured_utc", "?")


for d in sorted(named):
    v = def_verdict(d)
    if v:
        r.append(v)
_probe = [def_verdict("RM_WM_NoSuchDef_Probe") is None, def_verdict("VFEFactory_NoSuchMachine_Probe") is None,
          def_verdict("RM_WM_AncientComponent") is not None, def_verdict("VFEFactory_AutomatedSmelter") is not None,
          def_verdict("RM_WreckedMachinesKernel") is not None, len(script_defs) < 8]
if any(_probe):
    r.append("C9 instrument probe failed %s: the check cannot tell a real def from a missing one, or read the script's names" % _probe)
check("C9_defs_real", "every def named exists: ours (RM_/RUT_/RSW_) in the repo's Defs or Patches or as a C# type; the factory "
      "mod's and the base game's, as the scenes' script names them, in the def dump", r,
      "%d names checked (%d from validation.py's ORIGINAL and staging constants); dump captured %s, %d defs, %d mods"
      % (len(named), len(script_defs), prov.get("captured_utc", "?"), len(defs), len(pkgs)),
      "correct the name, or build the def", "Stage 1 if a wrong name, Stage 3 if owed", t)

# C10 every mod and every tier named is real
t = time.time()
r, r_tier = [], []
msrc = open("src/RimMandrake/Utils/modset_builder.py").read()
tier_names = set(re.findall(r'^\s{4}"([a-z0-9_]+)":\s*\{', msrc, re.M))
consts = dict(re.findall(r'^([A-Z_]+) = "([a-z0-9_.]+)"', msrc, re.M))
repo_pk = set()
for f in glob.glob("src/Rim*/*/About/About.xml"):
    mm = re.search(r"<packageId>([^<]+)</packageId>", open(f, errors="replace").read())
    if mm:
        repo_pk.add(mm.group(1).strip().lower())
want = []
mt = re.search(r'"%s":\s*\{.*?"want":\s*\[(.*?)\]' % re.escape(small["tier"]), msrc, re.S)
if small["tier"] not in tier_names or not mt:
    r.append("small_list.json names tier %s, which modset_builder.TIERS does not hold" % small["tier"])
else:
    for tok in re.findall(r'"([^"]+)"|\b([A-Z_]{3,})\b', mt.group(1)):
        want.append(tok[0] or consts.get(tok[1], "UNKNOWN CONSTANT " + tok[1]))
env = re.findall(r'^\s+"([a-z0-9_.]+)",', open(M + "/modcheck_env.py").read(), re.M)
for p in sorted(set(x.lower() for x in want + env + [small.get("character_editor") or ""]) - {""}):
    if p not in pkgs and p not in repo_pk:
        r.append("%s: not a mod in the def dump's mod list or the repo" % p)
if "vanillaexpanded.vfefactory" not in [x.lower() for x in want] or len(want) < 5:
    r.append("C10 instrument probe failed: the tier's want list reads %s" % want)
for k, v in tests.items():
    if live(v):
        if not v.get("tier"):
            r.append("%s: an in-game test with no tier" % k)
        elif v["tier"] not in tier_names:
            r_tier.append("%s: tier %s is not defined in modset_builder.TIERS (%s)" % (k, v["tier"], v.get("tier_why") or "no reason written"))
        if v.get("tier") in tier_names and v.get("tier_defined") is False:
            r.append("%s: the table says tier_defined false, and %s is defined: remake the table" % (k, v["tier"]))
check("C10_mods_real", "every packageId of the mod's small list and its modcheck environment is a mod in the dump's mod list or "
      "the repo; every in-game test names a tier", r, "tier %s: %s" % (small["tier"], ", ".join(want)), "correct the id", "Stage 1", t)
check("C10b_tiers_defined", "every tier that an in-game test names is defined (a tier of a scene's own is built with its scene)",
      r_tier, "%d tiers named: %s" % (len({v.get('tier') for v in tests.values() if live(v)}),
                                       ", ".join(sorted({str(v.get("tier")) for v in tests.values() if live(v)}))),
      "Stage 3 defines each named tier in src/RimMandrake/Utils/modset_builder.py (all five expansions, the zoom mod and Character "
      "Editor stay on it), then remakes the table", "Stage 3 (the scene is written; its mod list is owed)", t)

# C11 the kind of each in-game scene (spec, Stage 2 exit; designer_scene_contract.md, 'The kind of a scene')
t = time.time()
r = []
for k, v in tests.items():
    tk = v.get("test_kind")
    if live(v) and tk not in ("A", "B", "C"):
        r.append("%s: test_kind %r" % (k, tk))
    if tk in ("B", "C") and len(str(v.get("tag_evidence") or "")) < 40:
        r.append("%s: tagged %s with no tag_evidence" % (k, tk))
    if tk == "B" and not (isinstance(v.get("budget"), int) and v["budget"] > 0):
        r.append("%s: tagged B with no whole-number budget" % k)
    xy = v.get("x_of_y")
    if xy is not None and not (isinstance(xy, list) and len(xy) == 2 and all(isinstance(n, int) for n in xy) and 0 < xy[0] <= xy[1]):
        r.append("%s: x_of_y %r is not [X, Y]" % (k, xy))
for b in bars:
    ds = [d for d in b.get("decides") or [] if d in tests]
    if ds and all(tests[d].get("test_kind") == "C" for d in ds):
        r.append("%s: only kind C scenes decide it (a hunt is never a bar's acceptance)" % b["id"])
for sid, sc in S.items():
    words = " ".join(str(sc.get(x) or "") for x in ("start", "action", "expect", "control"))
    if re.search(r"\braid", words, re.I) and not (tests.get(sid) or {}).get("stages_raid"):
        r.append("%s: its row speaks of a raid, and the table carries no stages_raid" % sid)
check("C11_scene_kinds", "every in-game test has a kind; a B or C tag carries its evidence, a B tag its budget; no bar rests on a "
      "hunt alone; a scene that stages a raid says so", r,
      "%d in-game tests: %s" % (sum(1 for v in tests.values() if live(v)), ", ".join(
          "%s %d" % (x, sum(1 for v in tests.values() if live(v) and v.get("test_kind") == x)) for x in "ABC")),
      "write the tag's evidence, or drop the tag", "Stage 1", t)

# C12 the locked files still match their pinned blobs
t = time.time()
r = []
pins = re.findall(r"\| `(design/concepts/WreckedMachines/[\w.]+)` \| `([0-9a-f]{40})` \|", open(C + "/version/bars.md").read())
for f, blob in pins:
    if f.endswith("stage.json"):
        continue        # state, not a bar
    now = subprocess.run(["git", "hash-object", f], capture_output=True, text=True).stdout.strip()
    if now != blob:
        r.append("%s: pinned %s, now %s" % (f, blob[:10], now[:10]))
if len(pins) < 9:
    r.append("C12 instrument probe failed: %d pins read from bars.md, 9 are written there" % len(pins))
check("C12_locked_files_unchanged", "the locked bar files match the blobs pinned in version/bars.md", r, "%d pins (stage.json is "
      "state and is not compared)" % len(pins), "a change of test text is re-pinned in bars.md with a journal line; a changed bar "
      "is his card", "the steward (judgment: test text or meaning?)", t)

# C13 the scenes and the tree's checks are wired into the table
t = time.time()
r = []
for s in scenes["scenes"]:
    for q in (s.get("requirement") or []) + (s.get("features") or []):
        if q not in LEAF:
            r.append("%s names unknown leaf %s" % (s["id"], q))
    if s["id"] not in tests:
        r.append("%s is not in the table" % s["id"])
    elif s.get("kind") != "exploration":
        ep = "%s::%s" % ((tests[s["id"]].get("file") or ""), tests[s["id"]].get("entry"))
        if ep != s.get("entry_point"):
            r.append("%s: the table's entry %s is not the scene's entry_point %s" % (s["id"], ep, s.get("entry_point")))
    for q in s.get("requirement") or []:
        b = next((x for x in bars if x["id"] == q), None)
        if s.get("kind") == "acceptance" and b and s["id"] not in (b.get("decides") or []):
            r.append("%s is an acceptance scene of %s and does not decide it" % (s["id"], q))
for c in scenes.get("coverage_rest") or []:
    for x in c.get("by") or []:
        if x not in LEAF and x not in S:
            r.append("coverage_rest %s names unknown %s" % (c["capability"], x))
cm = tab.get("checks_map") or {}
for c in tree["checks"]:
    tid = str(cm.get(c["id"], "")).split(" ")[0]
    if tid not in tests:
        r.append("tree check %s has no test in the table (checks_map: %r)" % (c["id"], cm.get(c["id"])))
for sh in scenes.get("showcases") or []:
    for sid in sh.get("scenes") or []:
        if sid not in S:
            r.append("showcase %s names unknown scene %s" % (sh["id"], sid))
check("C13_scenes_and_checks_wired", "every scene is in the table with its own entry point; every acceptance scene decides the "
      "leaves it is required for; every coverage_rest and showcase name resolves; every check of the tree has a test", r,
      "%d scenes, %d tree checks, %d showcases" % (len(S), len(tree["checks"]), len(scenes.get("showcases") or [])),
      "fix the id, or remake the table", "Stage 1", t)

# C14 every bridge tool that the scenes call exists in the bridge's C#
t = time.time()
r = []
bsrc = " ".join(open(f, errors="replace").read() for f in glob.glob("src/RimMandrake/bridgetools/**/*.cs", recursive=True))
called = set(re.findall(r'bridge_call\(\s*"(jawa/\w+)"', valsrc)) | set(re.findall(r"`(jawa/\w+)`", open(C + "/plan.md").read()))
for name in sorted(called):
    if '"%s"' % name not in bsrc:
        r.append("%s is called by the scenes (or named present by plan.md) and is no tool of the bridge's C#" % name)
if '"jawa/no_such_tool_probe"' in bsrc or '"jawa/list_things"' not in bsrc or len(called) < 10:
    r.append("C14 instrument probe failed: %d names read; the reader cannot tell a tool from a missing one" % len(called))
check("C14_bridge_tools_real", "every jawa/ tool that validation.py calls, and every one that plan.md names, is registered in "
      "src/RimMandrake/bridgetools", r, "%d tool names" % len(called), "build the generic bridge function, test first",
      "Stage 3", t)

# C15 the items a test names exist in the ledger
t = time.time()
r = []
items = sorted(set(str(v["item"]).split(" ")[0] for v in tests.values() if v.get("item")))
led = "".join(open(f, errors="replace").read() for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"))
for it in items:
    if '"%s"' % it not in led:
        r.append(it)
check("C15_items_real", "every ticket that a test names exists in the ledger", r, "%d items: %s" % (len(items), ", ".join(items)),
      "file the item", "Stage 1", t)

# C16 the mod's small list passes its own check
t = time.time()
p = subprocess.run(["python3", "src/RimMandrake/Utils/small_list.py", "check"], capture_output=True, text=True)
line = next((l for l in (p.stdout + p.stderr).splitlines() if "WreckedMachines" in l), "")
check("C16_small_list", "the mod's small list passes small_list.py check (every mod it patches or requires, all five expansions, "
      "a zoom mod, Character Editor)", [] if line.strip().startswith("ok") else [line.strip() or "small_list.py check printed no "
                                                                                 "line for WreckedMachines (rc %s)" % p.returncode],
      line.strip(), "repair version/small_list.json or the tier", "Stage 1", t)

by_route = {}
for c in checks:
    if c["refusals"]:
        by_route[c["route"]] = by_route.get(c["route"], 0) + len(c["refusals"])
out = dict(mod="WreckedMachines", version=VER,
           program="design/concepts/WreckedMachines/version/pilot_throwaway/preflight_wreckedmachines.py (throwaway, no model)",
           table=TABLE, at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           dump=dict(path=DUMP, provenance={k: prov[k] for k in ("captured_utc", "defs_total", "mod_count", "game_version",
                                                                 "modlist_fingerprint") if k in prov}),
           seconds=round(time.time() - T0, 2),
           verdict="refuse" if any(c["verdict"] == "refuse" for c in checks) else "pass",
           refusals=sum(len(c["refusals"]) for c in checks), refusals_by_route=by_route,
           stage3_owed=[k for k, v in tests.items() if v.get("new")], checks=checks)
json.dump(out, open(OUT, "w"), indent=1)
for c in checks:
    print("%-30s %-6s %3d %s" % (c["id"], c["verdict"], len(c["refusals"]), "; ".join(c["refusals"])[:170]))
print("VERDICT", out["verdict"], "refusals", out["refusals"], "by route", json.dumps(by_route), "seconds", out["seconds"])
sys.exit(1 if out["verdict"] == "refuse" else 0)
