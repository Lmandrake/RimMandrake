#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline Stage 2, LeaningScrub 0.1.0): preflight of test_table.json. No model.

Shape copied from design/concepts/Graffiti/version/pilot_throwaway/preflight_graffiti.py (its checks, the stale-dump
fix and its instrument probe, the PLANT mode). Not src/RimMandrake/LeaningScrub/preflight_leaningscrub.py, which is the
retired biomes_sprint round's readiness check.

Usage: python3 preflight_leaningscrub_stage2.py [--dump <defs.sqlite>]
  LEANINGSCRUB_PREFLIGHT_PLANT=1  plants one fault per check, expects every check to refuse, writes nothing.
A deciding test whose code is not written yet is NOT a refusal: it is listed as Stage 3 work (C6).
"""
import copy, glob, json, os, re, sqlite3, subprocess, sys, time
from pathlib import Path

T0 = time.time()
ROOT = Path(__file__).resolve().parents[5]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
sys.path.insert(0, str(ROOT / "src/RimMandrake/rimflow"))
from game_paths import DUMP_ROOT  # noqa: E402
from maturation import LOCK_PINNED  # noqa: E402

PLANT = os.environ.get("LEANINGSCRUB_PREFLIGHT_PLANT") == "1"
DUMP = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else os.path.join(str(DUMP_ROOT), "defs.sqlite")
MOD = "LeaningScrub"
CON = Path("design/concepts/LeaningScrub")
VER = CON / "version"
LSD = Path("src/RimMandrake/LeaningScrub")
HOLD_DIR = Path("design/RimMandrake/validation_holding")
LOCKED_FILES = list(LOCK_PINNED)
STAGE_OF_KIND = {"offline": "4-5", "live_minimal": "6", "live_full": "6", "look": "8"}
ORDER = {"4-5": 1, "6": 2, "8": 3}
OURS = re.compile(r"^(RM|RUT|RSW)_")
SETTING = re.compile(r"\b([a-z][a-z0-9]*[A-Z]\w*(?:Enabled|Factor|Days|Range|Bias|Chance|Share|Ready|Size|Ticks))\b")

tt = json.loads((VER / "test_table.json").read_text())
tree = json.loads((CON / "tree.json").read_text())
rec = json.loads((CON / "record.json").read_text())
scn = json.loads((CON / "scenes.json").read_text())
locked = json.loads((VER / "locked_bars.json").read_text())

# ---- instruments ----
con = sqlite3.connect("file:" + DUMP + "?mode=ro&immutable=1", uri=True)
dump_defs = {r[0] for r in con.execute("select def_name from defs")}
dump_mods = {r[0].lower() for r in con.execute("select package_id from mods")}
prov = dict(con.execute("select key, value from provenance").fetchall())
xml = " ".join(open(f, errors="replace").read() for f in glob.glob("src/Rim*/**/Defs/**/*.xml", recursive=True)
               + glob.glob("src/Rim*/**/Patches/**/*.xml", recursive=True))
repo_defs = set(re.findall(r"<defName>\s*([A-Za-z0-9_]+)\s*</defName>", xml))
allcs = {f: open(f, errors="replace").read() for f in glob.glob("src/Rim*/**/*.cs", recursive=True)}
allcs_text = " ".join(allcs.values())
cs_types = set(re.findall(r"\b(?:class|struct|enum)\s+(\w+)\b", allcs_text))
cs_fields = set(re.findall(r"\b(?:public|private|internal)\s+static\s+(?:bool|int|float)\s+(\w+)\s*=", allcs_text))
ls_cs = {f: s for f, s in allcs.items() if f.startswith(str(LSD))}
repo_pkgs = {m.lower() for f in glob.glob("src/Rim*/**/About/About.xml", recursive=True)
             for m in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", open(f, errors="replace").read())}
ledger_ids = set()
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
    ledger_ids |= set(re.findall(r'"id"\s*:\s*"([^"]+)"', open(f, errors="replace").read()))
ours_in_dump = {d for d in dump_defs if OURS.match(d)}
dump_only_ours = sorted(d for d in ours_in_dump if d not in repo_defs and d not in cs_types)


# The locked prose names files, sites and items as well as defs (RM_VenomvineForms.cs, RM_TestSite_leaningscrub_v3,
# RM_RAWVENOM_ART_1, and RM_SweetlineGuardians.cs in a history_check): a name is real when it is a def, a C# type, a
# file stem under src/ (or one git deleted from src/, cited as history), a ledger id, or a whole word in our code.
src_stems = {os.path.splitext(os.path.basename(f))[0] for f in glob.glob("src/**/*", recursive=True)}
gone_stems = {os.path.splitext(os.path.basename(f))[0] for f in subprocess.run(
    ["git", "log", "--diff-filter=D", "--name-only", "--format=", "--", "src"], capture_output=True, text=True).stdout.split()}
code_words = set(re.findall(r"\b(?:RM|RUT|RSW)_\w+", " ".join(
    open(f, errors="replace").read() for pat in ("py", "json") for f in glob.glob("src/Rim*/**/*." + pat, recursive=True))
    + " " + allcs_text + " " + xml))
NAME_KINDS = (("a file under src/", src_stems), ("a file git deleted from src/ (history)", gone_stems),
              ("a ledger id", ledger_ids), ("a name in our code", code_words))


def def_verdict(d):
    """None = real; else the reason it refuses. Our names are judged against the repo NOW, never the dump."""
    if OURS.match(d):
        if d in repo_defs or d in cs_types or any(d in pool for _, pool in NAME_KINDS):
            return None
        return "only in the dump: deleted from the repo" if d in dump_defs else "not in the repo's current defs or C# types"
    return None if (d in dump_defs or d in repo_defs) else "not in the dump or the repo"


# ---- planted faults: one per check ----
STALE = dump_only_ours[0] if dump_only_ours else None
LOCKED_PIN_OVERRIDE = {}
if PLANT:
    tt = copy.deepcopy(tt)
    T, B = tt["tests"], tt["bars"]
    bmap = {b["id"]: b for b in B}
    B.pop()                                                          # C1 a locked bar is missing
    bmap["biome_cast"]["decides"].append("T_NOT_DEFINED")            # C2 an undefined decider
    T["T_FUZZ"]["stage"] = "7"                                       # C3 a stage that is not 4-5/6/8
    T["T_WIND"]["file"] = str(LSD / "selftest_nosuch.py")            # C4 a test file that is not real
    T["T_SITE"]["reads"].append(str(LSD / "nosuch.py"))              # C5 a read path that is not real
    T["sc_raid_weight"]["entry_exists"] = True                       # C6 the table claims an entry the code lacks
    T["sc_raid_weight"]["why_game"] = ""                             # C7 a game test with no reason
    tt["held_statements"] = []                                       # C8 the held row dropped
    T["T_LINT_DEFS"]["defs"].append(STALE or "RM_LeaningScrub_PlantedStale")  # C9 a stale def of ours
    T["T_LINT_DEFS"]["mods"].append("mandrake.rm.nosuchmod")         # C10 a mod that is not real
    T["sc_settings"]["observes"] += " `fakeScrubSwitchEnabled`"      # C11 a setting field that is not real
    LOCKED_PIN_OVERRIDE = {"tree.json": "0" * 40}                    # C12 a pin that moved
    T["T_FUZZ"]["symbols"].append("RM_LeaningScrubNoSuchKernel")     # C13 a C# type that is not real
    T["sc_native_cast"]["item"] = "RIMMANDRAKE_PLANTED_NO_SUCH_ITEM"  # C14 an item not in the ledger
    for b in B:                                                      # C15 a scene wired to no bar
        b["decides"] = [x for x in b["decides"] if x != "sc_raid_weight"]
        b["supports"] = [x for x in b["supports"] if x != "sc_raid_weight"]
    T["T_WIND"]["runs_today"] = dict(T["T_WIND"]["runs_today"], result="FAIL", rc=1)  # C16 a built test red
    rec = copy.deepcopy(rec)
    rec["inventory"][0]["impl_evidence"] = list(rec["inventory"][0].get("impl_evidence") or []) + ["ITEM:RIMMANDRAKE_PLANTED_FAKE"]  # C17
    bmap["settings"]["every_decider_runnable_today"] = True          # C18 a runnable flag the tests do not support

T, B = tt["tests"], tt["bars"]
bids = {b["id"]: b for b in B}
checks = []


def check(cid, what, refusals, evidence, t=None, notes=None):
    checks.append(dict(id=cid, what=what, verdict="refuse" if refusals else "pass", refusals=refusals,
                       evidence=evidence, notes=notes, seconds=round(time.time() - t, 3) if t else None))


def R(line, evidence, fix, route, would_pass=None):
    return dict(line=line, evidence=evidence, smallest_fix=fix, route=route, would_pass=would_pass or fix)


# C1 bars complete
t = time.time(); ref = []
want = [l["id"] for l in tree["leaves"]] + [i["id"] for i in rec["inventory"]]
have = [b["id"] for b in B]
if set(have) != set(locked["ids"]):
    ref.append(R("test_table.json bars", "missing %s, extra %s" % (sorted(set(locked["ids"]) - set(have)),
                 sorted(set(have) - set(locked["ids"]))), "make the bar list equal locked_bars.json ids", "neutral fixer"))
if set(want) != set(locked["ids"]):  # 15 ids are both a leaf and an inventory row: membership, not multiset
    ref.append(R("locked_bars.json ids", "differ from tree leaves + record inventory", "re-lock", "Stage 1"))
if len(set(have)) != len(have):
    ref.append(R("test_table.json bars", "duplicate bar ids", "dedupe", "neutral fixer"))
check("C1_bars_complete", "the table holds exactly the locked bars (tree leaves + record inventory)", ref,
      "%d bars, %d locked" % (len(have), len(locked["ids"])), t=t)

# C2 every bar names its check(s) and every named check is defined
t = time.time(); ref = []
for b in B:
    if not b["decides"]:
        ref.append(R("bar " + b["id"], "no deciding test", "name the test that decides it", "Stage 1"))
    for x in b["decides"] + b["supports"]:
        if x not in T:
            ref.append(R("bar " + b["id"], "names test %s, which the table does not define" % x, "define it or drop it", "neutral fixer"))
check("C2_bars_name_checks", "every bar names a deciding check and every named check is defined", ref,
      "%d bars, %d tests" % (len(B), len(T)), t=t)

# C3 every check names its stage (4-5, 6, 8) and proves_at agrees
t = time.time(); ref = []
for tid, x in T.items():
    if x.get("stage") not in ORDER:
        ref.append(R("test " + tid, "stage %r" % x.get("stage"), "give it stage 4-5, 6 or 8", "neutral fixer"))
    elif STAGE_OF_KIND.get(x["kind"]) != x["stage"]:
        ref.append(R("test " + tid, "kind %s at stage %s" % (x["kind"], x["stage"]), "match kind and stage", "neutral fixer"))
for b in B:
    st = [T[d]["stage"] for d in b["decides"] if d in T and T[d].get("stage") in ORDER]
    if st and b["proves_at"] != max(st, key=lambda s: ORDER[s]):
        ref.append(R("bar " + b["id"], "proves_at %s, deciders reach %s" % (b["proves_at"], max(st, key=lambda s: ORDER[s])),
                     "recompute proves_at", "neutral fixer"))
check("C3_stages_named", "every check names its stage and each bar's proves_at is its highest decider", ref,
      "%d tests" % len(T), t=t)

# C4 test files real
t = time.time(); ref = []
for tid, x in T.items():
    if not x.get("file"):
        if x["kind"] != "look":
            ref.append(R("test " + tid, "no file", "name its file", "neutral fixer"))
        continue
    if not Path(x["file"]).is_file():
        ref.append(R("test " + tid, "%s not real" % x["file"], "point it at the real file", "neutral fixer"))
check("C4_test_files_real", "every named test file is real", ref, "%d tests" % len(T), t=t)

# C5 read paths real
t = time.time(); ref = []; n = 0
for tid, x in T.items():
    for r in x.get("reads", []):
        n += 1
        if not Path(r.split(":")[0]).exists():
            ref.append(R("test " + tid, "reads %s, not real" % r, "fix the path", "neutral fixer"))
check("C5_reads_real", "every file a test reads is real", ref, "%d read paths" % n, t=t)

# C6 entries: the table's claim agrees with the code (independent grep); absent entries are Stage 3 work
t = time.time(); ref = []; owed = []
for tid, x in T.items():
    if not x.get("entry"):
        continue
    src = Path(x["file"]).read_text(errors="replace") if Path(x["file"]).exists() else ""
    real = bool(re.search(r"^def %s\(" % re.escape(x["entry"]), src, re.M))
    if bool(x.get("entry_exists")) != real:
        ref.append(R("test " + tid, "table says entry_exists=%s, %s::%s is %s" % (x.get("entry_exists"), x["file"], x["entry"],
                     "present" if real else "absent"), "re-measure entry_exists", "neutral fixer"))
    if not real:
        owed.append("%s (%s::%s, item %s)" % (tid, x["file"], x["entry"], x.get("item")))
check("C6_entries_measured", "each scene test's entry_exists matches its code; unwritten entries are Stage 3 work, not refusals",
      ref, "%d scene entries owed to Stage 3" % len(owed), t=t, notes={"stage3_owed": owed})

# C7 why a game, why the full list
t = time.time(); ref = []; by_maker = []
for tid, x in T.items():
    if x["kind"].startswith("live") and not (x.get("why_game") or "").strip():
        ref.append(R("test " + tid, "no why_game", "say why an offline test cannot decide it", "Stage 1"))
    if x["kind"] == "live_full" and not (x.get("why_full_list") or "").strip():
        ref.append(R("test " + tid, "no why_full_list", "say why the minimal list cannot decide it", "Stage 1"))
    if (x.get("why_game_by") or "").startswith("table maker"):
        by_maker.append(tid)
check("C7_why_game_and_full_list", "every game test says why offline cannot decide it; every full-list test says why", ref,
      "%d live tests; %d reasons written by the table maker from the scene's kind (Stage 4 judges them)" % (
          sum(1 for x in T.values() if x["kind"].startswith("live")), len(by_maker)), t=t,
      notes={"why_game_by_table_maker": by_maker})

# C8 every held look statement naming this mod is placed on a real bar and a test that bar names
t = time.time(); ref = []; held_src = []
for f in sorted(HOLD_DIR.glob("*.md")):
    for line in f.read_text(errors="replace").splitlines():
        mm = re.match(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|", line)
        if mm and ("leaningscrub" in f.name.lower() or re.search(r"leaning\s?scrub", line, re.I)):
            held_src.append((str(f), int(mm.group(1))))
placed = {(h["source"].rsplit(" row ", 1)[0], h["row"]): h for h in tt.get("held_statements", [])}
for src, row in held_src:
    h = placed.get((src, row))
    if not h:
        ref.append(R("%s row %d" % (src, row), "held statement not placed", "place it on a bar and a test", "neutral fixer"))
        continue
    if not h["bars"] or not h["tests"]:
        ref.append(R("%s row %d" % (src, row), "placed with no bar or no test", "name both", "neutral fixer"))
    for b in h["bars"]:
        if b not in bids:
            ref.append(R("%s row %d" % (src, row), "bar %s not real" % b, "use a locked bar", "neutral fixer"))
    for x in h["tests"]:
        if x not in T:
            ref.append(R("%s row %d" % (src, row), "test %s not defined" % x, "define it", "neutral fixer"))
        elif not any(x in bids[b]["decides"] + bids[b]["supports"] for b in h["bars"] if b in bids):
            ref.append(R("%s row %d" % (src, row), "test %s is on none of its bars" % x, "put the test on the bar", "neutral fixer"))
check("C8_held_statements_placed", "every held look statement naming LeaningScrub in validation_holding/ is on a bar and a test",
      ref, "%d held rows found (%s)" % (len(held_src), ", ".join("%s row %d" % s for s in held_src)), t=t)

# C9 every named def is real; ours judged against the repo NOW (stale-dump fix), with an instrument probe
t = time.time(); ref = []
named = set()
for x in T.values():
    named |= set(x.get("defs", []))
lock_text = " ".join((CON / f).read_text(errors="replace") for f in LOCKED_FILES if (CON / f).exists())
named |= set(re.findall(r"\b((?:RM|RUT|RSW)_\w+)", lock_text))
families = sorted(d for d in named if OURS.match(d) and def_verdict(d)
                  and sum(1 for r in repo_defs | cs_types if r.startswith(d)) >= 2)   # a prose family ("RM_Twitcher*")
for d in sorted(named):
    if d in families:
        continue
    why = def_verdict(d)
    if why:
        ref.append(R("def " + d, why, "name a current def or C# type", "Stage 1" if d in lock_text else "neutral fixer"))
probe = [(STALE, False, "a dump-only def of ours"), ("RM_LeaningScrub_NoSuchProbeDef", False, "a fake name of ours"),
         ("RM_Segnosaurus", True, "a real def of ours"), ("Wall", True, "a vanilla def")]
probe_out = []
for name, should_pass, label in probe:
    if name is None:
        probe_out.append("%s: UNMEASURED (no dump-only def of ours in this dump)" % label)
        continue
    got = def_verdict(name) is None
    probe_out.append("%s %s: %s" % (label, name, "pass" if got else "refuse"))
    if got != should_pass:
        ref.append(R("probe " + name, "%s should %s" % (label, "pass" if should_pass else "refuse"), "fix def_verdict", "neutral fixer"))
check("C9_defs_real", "every named def is real; our RM_/RUT_/RSW_ names against the repo's current XML and C# types", ref,
      "%d names (%d family prefixes, each with >=2 current repo names: %s); dump %s captured %s (%d defs); %d dump-only defs "
      "of ours; probe: %s" % (len(named), len(families), ", ".join(families), DUMP, prov.get("captured_utc", "UNMEASURED"),
                              len(dump_defs), len(dump_only_ours), "; ".join(probe_out)), t=t)

# C10 every named mod is real
t = time.time(); ref = []; mods = set()
for x in T.values():
    mods |= {m.lower() for m in x.get("mods", [])}
for mo in sorted(mods):
    if mo not in dump_mods and mo not in repo_pkgs:
        ref.append(R("mod " + mo, "in neither the dump's mods nor a repo About.xml", "name a real packageId", "neutral fixer"))
check("C10_mods_real", "every named mod is real", ref, "%d mods named: %s" % (len(mods), ", ".join(sorted(mods))), t=t)

# C11 every named settings field is real (a static field in the repo's C#, ours or a sibling mod's)
t = time.time(); ref = []
blob = lock_text + " ".join(x.get("observes", "") for x in T.values())
named_fields = set(SETTING.findall(blob))
ls_fields = set(re.findall(r"\bpublic\s+static\s+(?:bool|int|float)\s+(\w+)\s*=", " ".join(ls_cs.values())))
for fn in sorted(named_fields):
    if fn not in cs_fields and not re.search(r"\b%s\b" % re.escape(fn), allcs_text):
        ref.append(R("setting " + fn, "not a field or name in the repo's C#", "name a real field",
                     "Stage 1" if fn in lock_text else "neutral fixer"))
check("C11_settings_real", "every named settings field is real", ref,
      "%d named (%s); %d static fields in LeaningScrub C#" % (len(named_fields), ", ".join(sorted(named_fields)), len(ls_fields)), t=t)

# C12 lock pins unchanged
t = time.time(); ref = []
pins = dict(re.findall(r"\|\s*`design/concepts/LeaningScrub/([\w.]+)`\s*\|\s*`([0-9a-f]{40})`", (VER / "bars.md").read_text()))
pins.update(LOCKED_PIN_OVERRIDE)
for f in LOCKED_FILES:
    blob_now = subprocess.run(["git", "hash-object", str(CON / f)], capture_output=True, text=True).stdout.strip()
    if f not in pins:
        ref.append(R("bars.md", "%s has no pin" % f, "pin it", "Stage 1"))
    elif pins[f] != blob_now:
        last = subprocess.run(["git", "log", "-1", "--format=%h %ci %s", "--", str(CON / f)], capture_output=True, text=True).stdout.strip()
        ref.append(R("design/concepts/LeaningScrub/" + f, "blob %s, pinned %s; last changed by %s" % (blob_now[:12], pins[f][:12], last[:140]),
                     "re-pin it in bars.md (test text only) or restore the pinned blob; a changed bar is his card", "Stage 1"))
check("C12_lock_pins_current", "the locked files still hash to their pins in bars.md", ref, "%d pins read" % len(pins), t=t)

# C13 C# symbols real (types, and Type.member names written in observes)
t = time.time(); ref = []; nsym = 0
ls_all = " ".join(ls_cs.values())
for tid, x in T.items():
    for s in x.get("symbols", []):
        nsym += 1
        if not re.search(r"\b(?:class|struct|enum)\s+%s\b" % re.escape(s), ls_all):
            ref.append(R("test " + tid, "C# type %s not in LeaningScrub sources" % s, "name a real type", "neutral fixer"))
    for typ, mem in re.findall(r"\b([A-Z]\w+)\.([A-Za-z_]\w*)\b", x.get("observes", "")):
        files = [f for f, s in ls_cs.items() if re.search(r"\b(?:class|struct|enum)\s+%s\b" % typ, s)]
        if not files:
            continue
        nsym += 1
        if not any(re.search(r"\b%s\b" % re.escape(mem), ls_cs[f]) for f in files):
            ref.append(R("test " + tid, "%s.%s not in %s" % (typ, mem, files), "name a real member", "neutral fixer"))
check("C13_cs_symbols_real", "every C# type and member a test names is real", ref, "%d symbols" % nsym, t=t)

# C14 items real
t = time.time(); ref = []
for tid, x in T.items():
    it = x.get("item")
    if it and it not in ledger_ids:
        ref.append(R("test " + tid, "item %s not in the ledger" % it, "name a real item", "neutral fixer"))
for s in scn["scenes"]:
    it = s.get("entry_point_item")
    if it and it not in ledger_ids:
        ref.append(R("scenes.json " + s["id"], "entry_point_item %s not in the ledger" % it, "file or fix it", "Stage 1"))
check("C14_items_real", "every named ledger item is real", ref, "%d ledger ids read" % len(ledger_ids), t=t)

# C15 every scene is a test on a bar, and decides the leaves it is required for / the bars it exercises
t = time.time(); ref = []; unwired = []
for s in scn["scenes"]:
    if s["id"] not in T:
        ref.append(R("scenes.json " + s["id"], "no test", "add the scene's test", "neutral fixer")); continue
    if not any(s["id"] in b["decides"] + b["supports"] for b in B):
        unwired.append(s["id"])
        if s.get("kind") == "acceptance":
            ref.append(R("scenes.json " + s["id"], "an acceptance scene on no bar", "put it on its bar", "neutral fixer"))
    for leaf in (s.get("requirement") or []) + (s.get("exercises") or []):
        if leaf in bids and s["id"] not in bids[leaf]["decides"]:
            ref.append(R("bar " + leaf, "scene %s is required for / exercises it but does not decide it" % s["id"],
                         "add it to decides", "neutral fixer"))
for cr in scn.get("coverage_rest", []):
    b = bids.get(cr["capability"])
    for by in cr["by"]:
        if b and by in T and by not in b["decides"] + b["supports"]:
            ref.append(R("bar " + cr["capability"], "coverage_rest names %s, the bar does not" % by, "add it", "neutral fixer"))
check("C15_scenes_wired", "every acceptance scene is a test on a bar and decides what it is required for", ref,
      "%d scenes; on no bar (exploration/interaction, not acceptance): %s" % (len(scn["scenes"]), unwired or "none"), t=t)

# C16 built offline tests green today
t = time.time(); ref = []
for tid, x in T.items():
    if x["kind"] != "offline" or x.get("entry"):
        continue
    rt = x.get("runs_today", {})
    if rt.get("result") == "PASS":
        continue
    lines = Path(rt["log"]).read_text(errors="replace").splitlines() if Path(rt.get("log", "")).exists() else []
    fails = [l.strip() for l in lines if re.match(r"^\s*(Z\d+|FAIL|\w+\s+FAIL)", l.strip())]
    ref.append(R("test " + tid, "today %s rc=%s: %s" % (rt.get("result"), rt.get("rc"), (" | ".join(fails[-3:]) or rt.get("last", ""))[:300]),
                 "make it green", "Stage 3"))
check("C16_built_offline_green", "every built offline test passes today", ref,
      "%d built offline tests" % sum(1 for x in T.values() if x["kind"] == "offline" and not x.get("entry")), t=t)

# C17 inventory impl_evidence real (paths, :line within the file, ITEM: ids in the ledger)
t = time.time(); ref = []; n = 0
for inv in rec["inventory"]:
    for ev in inv.get("impl_evidence") or []:
        n += 1
        if ev.startswith("ITEM:"):
            if ev[5:] not in ledger_ids:
                ref.append(R("record.json " + inv["id"], "%s not in the ledger" % ev, "name a real item", "Stage 1"))
            continue
        path, _, ln = ev.partition(":")
        p = Path(path)
        if not p.exists():
            ref.append(R("record.json " + inv["id"], "%s not real" % path, "fix the path", "Stage 1"))
        elif ln.isdigit() and p.is_file() and int(ln) > len(p.read_text(errors="replace").splitlines()):
            ref.append(R("record.json " + inv["id"], "%s past the end of the file" % ev, "fix the line", "Stage 1"))
check("C17_inventory_evidence_real", "every record.json impl_evidence path and ITEM is real", ref, "%d evidence entries" % n, t=t)


# C18 every_decider_runnable_today agrees with the measured tests
def runnable(tid):
    x = T.get(tid)
    if not x:
        return False
    if x.get("entry"):
        return bool(x.get("entry_exists"))
    if x["kind"] == "offline":
        return bool(x.get("runs_today", {}).get("ran")) and x["runs_today"].get("result") == "PASS"
    return False


t = time.time(); ref = []
for b in B:
    want_flag = bool(b["decides"]) and all(runnable(d) for d in b["decides"])
    if not isinstance(b.get("every_decider_runnable_today"), bool):
        ref.append(R("bar " + b["id"], "every_decider_runnable_today is not a bool", "write a bool", "neutral fixer"))
    elif b["every_decider_runnable_today"] != want_flag:
        ref.append(R("bar " + b["id"], "every_decider_runnable_today=%s, its deciders say %s" % (
            b["every_decider_runnable_today"], want_flag), "recompute", "neutral fixer"))
check("C18_runnable_flags_measured", "each bar's every_decider_runnable_today agrees with its measured deciders", ref,
      "%d bars runnable today" % sum(1 for b in B if b.get("every_decider_runnable_today") is True), t=t)

# ---- verdict ----
nref = sum(len(c["refusals"]) for c in checks)
out = dict(mod=MOD, version="0.1.0", program="design/concepts/LeaningScrub/version/pilot_throwaway/preflight_leaningscrub_stage2.py",
           at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           dump=dict(path=DUMP, provenance={k: prov[k] for k in list(prov)[:8]}),
           seconds=round(time.time() - T0, 2), verdict="refuse" if nref else "pass", refusals=nref,
           known_red={}, checks=checks)
red = [c["id"] for c in checks if c["verdict"] == "refuse"]
if PLANT:
    green = [c["id"] for c in checks if c["verdict"] == "pass"]
    print("PLANTED: %d of %d checks refused; still green: %s" % (len(red), len(checks), green or "none"))
    for c in checks:
        print("  %s: %s" % (c["id"], (c["refusals"][0]["line"] + " | " + c["refusals"][0]["evidence"])[:150] if c["refusals"] else "GREEN"))
    print("PLANTED run wrote nothing")
    sys.exit(0 if not green else 1)
(VER / "preflight.json").write_text(json.dumps(out, indent=1) + "\n")
print("verdict %s, %d refusals, red checks %s, %.2f s" % (out["verdict"], nref, red, out["seconds"]))
for c in checks:
    for r in c["refusals"]:
        print("  %s | %s | %s | %s" % (c["id"], r["line"], r["evidence"][:160], r["route"]))
