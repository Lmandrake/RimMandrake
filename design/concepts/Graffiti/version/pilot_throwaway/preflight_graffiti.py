#!/usr/bin/env python3
"""THROWAWAY (Maturation Pipeline Stage 2, Graffiti 0.1.0): preflight of test_table.json. No model.

Shape copied from design/concepts/Pyrelands/version/pilot_throwaway/preflight_pyre.py (checks, the
stale-dump fix and its instrument probe) and the PLANT mode of
design/concepts/GimmeSomeSlack/version/preflight_throwaway.py.

Usage: python3 preflight_graffiti.py [--dump <defs.sqlite>]
  GRAFFITI_PREFLIGHT_PLANT=1  plants one fault per check, expects every check to refuse, writes nothing.
A deciding test whose code is not written yet is NOT a refusal: it is listed as Stage 3 work (C6).
"""
import copy, glob, json, os, re, sqlite3, subprocess, sys, time
from pathlib import Path

T0 = time.time()
ROOT = Path(__file__).resolve().parents[5]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
from game_paths import DUMP_ROOT  # noqa: E402

PLANT = os.environ.get("GRAFFITI_PREFLIGHT_PLANT") == "1"
DUMP = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else os.path.join(str(DUMP_ROOT), "defs.sqlite")
CON = Path("design/concepts/Graffiti")
VER = CON / "version"
GRF = Path("src/RimMandrake/Graffiti")
KNOWN_RED = "RIMMANDRAKE_REFUSE_HIDDEN_FACE_PAINT_ORDER_OUTLIVED_ITS_WALL"
HOLD_DIR = Path("design/RimMandrake/validation_holding")
LOCKED_FILES = ["tree.json", "sheet.md", "scenes.json", "floor.json", "exam.json", "record.json", "plan.md"]
STAGE_OF_KIND = {"offline": "4-5", "record": "4-5", "live_minimal": "6", "live_full": "6", "look": "8"}
ORDER = {"4-5": 1, "6": 2, "8": 3}
OURS = re.compile(r"^(RM|RUT|RSW)_")

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
allcs_files = glob.glob("src/Rim*/**/*.cs", recursive=True)
allcs = " ".join(open(f, errors="replace").read() for f in allcs_files)
cs_types = set(re.findall(r"\b(?:class|struct|enum)\s+(\w+)\b", allcs))
grf_cs = {f: open(f, errors="replace").read() for f in glob.glob(str(GRF / "Source/**/*.cs"), recursive=True)}
repo_pkgs = {m.lower() for f in glob.glob("src/Rim*/**/About/About.xml", recursive=True)
             for m in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", open(f, errors="replace").read())}
ledger_ids = set()
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
    ledger_ids |= set(re.findall(r'"id"\s*:\s*"([^"]+)"', open(f, errors="replace").read()))
ours_in_dump = {d for d in dump_defs if OURS.match(d)}
dump_only_ours = sorted(d for d in ours_in_dump if d not in repo_defs and d not in cs_types)


def def_verdict(d, dump_defs=dump_defs):
    """None = real; else the reason it refuses. Our names are judged against the repo NOW, never the dump."""
    if OURS.match(d):
        if d in repo_defs or d in cs_types:
            return None
        return "only in the dump: deleted from the repo" if d in dump_defs else "not in the repo's current defs or C# types"
    return None if (d in dump_defs or d in repo_defs) else "not in the dump or the repo"


# ---- planted faults: one per check ----
STALE = dump_only_ours[0] if dump_only_ours else None
if PLANT:
    tt = copy.deepcopy(tt)
    T, B = tt["tests"], tt["bars"]
    bmap = {b["id"]: b for b in B}
    B.pop()                                                         # C1 a locked bar is missing
    bmap["own_fun"]["decides"].append("T_NOT_DEFINED")              # C2 an undefined decider
    T["T_FUZZ"]["stage"] = "7"                                      # C3 a stage that is not 2/4-5/6/8
    T["T_LINT"]["file"] = "src/RimMandrake/Utils/selftest_graffiti_nosuch.py"   # C4 a test file that is not real
    T["T_PLAY_ZOOM"]["reads"].append("src/RimMandrake/Graffiti/nosuch.py")     # C5 a read path that is not real
    T["sc_visitors"]["entry_exists"] = True                          # C6 the table claims an entry the code lacks
    T["sc_walk"]["why_full_list"] = ""                               # C7 a full-list test with no reason
    tt["held_statements"] = [h for h in tt["held_statements"] if h["row"] != 3]  # C8 a held row dropped
    T["T_LINT"]["defs"].append(STALE or "RM_Graffiti_PlantedStale")  # C9 a stale def (dump-only, deleted from repo)
    T["T_SHIP_CHECK"]["mods"].append("mandrake.rm.nosuchmod")        # C10 a mod that is not real
    T["sc_settings"]["observes"] += " `fakeSwitchEnabled`"           # C11 a setting field that is not real
    LOCKED_PIN_OVERRIDE = {"tree.json": "0" * 40}                    # C12 a pin that moved
    T["P_A9"].pop("known_red", None)                                 # C13 the known defect off its test
    T["T_FUZZ"]["symbols"].append("RM_GraffitiNoSuchKernel")         # C14 a C# type that is not real
    T["sc_mockery"]["item"] = "RIMMANDRAKE_PLANTED_NO_SUCH_ITEM"     # C15 an item not in the ledger
    for b in B:                                                      # C16 a scene wired to no bar
        b["decides"] = [x for x in b["decides"] if x != "sc_temperament"]
        b["supports"] = [x for x in b["supports"] if x != "sc_temperament"]
    T["T_FUZZ"]["runs_today"] = dict(T["T_FUZZ"]["runs_today"], result="FAIL", rc=1)  # C17 a built test red
    rec = copy.deepcopy(rec)
    rec["inventory"][0]["impl_evidence"] = list(rec["inventory"][0]["impl_evidence"]) + ["ITEM:RIMMANDRAKE_PLANTED_FAKE"]  # C18
    bmap["answer_wall"]["every_decider_runnable_today"] = True       # C19 a runnable flag the tests do not support
else:
    LOCKED_PIN_OVERRIDE = {}

T, B = tt["tests"], tt["bars"]
checks = []


def check(cid, what, refusals, evidence, smallest_fix=None, route=None, t=None, notes=None):
    checks.append(dict(id=cid, what=what, verdict="refuse" if refusals else "pass", refusals=refusals,
                       evidence=evidence, smallest_fix=smallest_fix if refusals else None,
                       route=route if refusals else None, notes=notes,
                       seconds=round(time.time() - t, 3) if t else None))


def R(line, evidence, fix, route):
    return dict(line=line, evidence=evidence, smallest_fix=fix, route=route)


# C1 bars complete
t = time.time()
want = [l["id"] for l in tree["leaves"]] + [i["id"] for i in rec["inventory"]]
have = [b["id"] for b in B]
ref = []
if set(have) != set(locked["ids"]):  # maturation.py compares membership, not order
    ref.append(R("test_table.json bars", "missing %s, extra %s" % (sorted(set(locked["ids"]) - set(have)),
                 sorted(set(have) - set(locked["ids"]))), "make the bar list equal locked_bars.json ids", "neutral fixer"))
if sorted(want) != sorted(locked["ids"]):
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

# C3 every check names its stage (2, 4-5, 6, 8) and proves_at agrees
t = time.time(); ref = []
for tid, x in T.items():
    if x.get("stage") not in ("2", "4-5", "6", "8"):
        ref.append(R("test " + tid, "stage %r" % x.get("stage"), "give it stage 2, 4-5, 6 or 8", "neutral fixer"))
    elif STAGE_OF_KIND.get(x["kind"]) != x["stage"]:
        ref.append(R("test " + tid, "kind %s at stage %s" % (x["kind"], x["stage"]), "match kind and stage", "neutral fixer"))
for b in B:
    st = [T[d]["stage"] for d in b["decides"] if d in T and T[d].get("stage") in ORDER]
    if st and b["proves_at"] != max(st, key=lambda s: ORDER[s]):
        ref.append(R("bar " + b["id"], "proves_at %s, deciders reach %s" % (b["proves_at"], max(st, key=lambda s: ORDER[s])),
                     "recompute proves_at", "neutral fixer"))
check("C3_stages_named", "every check names its stage and each bar's proves_at is its highest decider", ref,
      "%d tests" % len(T), t=t)

# C4 test files real (a new test: its folder exists and the file does not yet)
t = time.time(); ref = []
for tid, x in T.items():
    if not x.get("file"):
        if x["kind"] != "look":
            ref.append(R("test " + tid, "no file", "name its file", "neutral fixer"))
        continue
    p = Path(x["file"])
    if x.get("new") and x["kind"] == "offline":
        if not p.parent.is_dir():
            ref.append(R("test " + tid, "folder %s not real" % p.parent, "put it in a real folder", "neutral fixer"))
        if p.exists():
            ref.append(R("test " + tid, "%s already exists but is marked new" % p, "mark it built and run it", "neutral fixer"))
    elif not p.is_file():
        ref.append(R("test " + tid, "%s not real" % p, "point it at the real file", "neutral fixer"))
check("C4_test_files_real", "every named test file is real (a new test's folder is real)", ref, "%d files" % len(T), t=t)

# C5 read paths real
t = time.time(); ref = []; n = 0
for tid, x in T.items():
    for r in x.get("reads", []):
        n += 1
        if not Path(r.split(":")[0]).exists():
            ref.append(R("test " + tid, "reads %s, not real" % r, "fix the path", "neutral fixer"))
check("C5_reads_real", "every file a test reads is real", ref, "%d read paths" % n, t=t)

# C6 live entries: table claim agrees with the code (independent grep); absent entries are Stage 3 work
t = time.time(); ref = []; owed = []
v1 = Path(GRF / "graffiti_v1_live_proof.py").read_text()
m = re.search(r"^CLAUSES\s*=\s*\(([^)]*)\)", v1, re.M)
clauses = set(re.findall(r'"(\w+)"', m.group(1))) if m else set()
for tid, x in T.items():
    if not x["kind"].startswith("live"):
        continue
    src = Path(x["file"]).read_text(errors="replace") if Path(x["file"]).exists() else ""
    real = (x["entry"] in clauses) if x["file"].endswith("graffiti_v1_live_proof.py") else \
        bool(re.search(r"^def %s\(" % re.escape(x["entry"]), src, re.M))
    if bool(x.get("entry_exists")) != real:
        ref.append(R("test " + tid, "table says entry_exists=%s, %s::%s is %s" % (x.get("entry_exists"), x["file"], x["entry"],
                     "present" if real else "absent"), "re-measure entry_exists", "neutral fixer"))
    if not real:
        owed.append("%s (%s::%s, item %s)" % (tid, x["file"], x["entry"], x.get("item")))
for tid, x in T.items():
    if x["kind"] == "offline" and x.get("new"):
        owed.append("%s (%s, item %s)" % (tid, x["file"], x.get("item")))
check("C6_entries_measured", "each live test's entry_exists matches its code; unwritten tests are Stage 3 work, not refusals",
      ref, "%d tests owed to Stage 3" % len(owed), t=t, notes={"stage3_owed": owed})

# C7 why a game, why the full list
t = time.time(); ref = []
for tid, x in T.items():
    if x["kind"].startswith("live") and not (x.get("why_game") or "").strip():
        ref.append(R("test " + tid, "no why_game", "say why an offline test cannot decide it", "Stage 1"))
    if x["kind"] == "live_full" and not (x.get("why_full_list") or "").strip():
        ref.append(R("test " + tid, "no why_full_list", "say why the minimal list cannot decide it", "Stage 1"))
check("C7_why_game_and_full_list", "every game test says why offline cannot decide it; every full-list test says why", ref,
      "%d live tests" % sum(1 for x in T.values() if x["kind"].startswith("live")), t=t)

# C8 every held look statement is placed on a real bar and a real test that bar names
t = time.time(); ref = []; held_src = []
for f in sorted(HOLD_DIR.glob("*.md")):
    for line in f.read_text(errors="replace").splitlines():
        mm = re.match(r"^\|\s*(\d+)\s*\|\s*(.*?)\s*\|", line)
        if not mm:
            continue
        if "graffiti" in f.name.lower() or re.search(r"graffit|scrawl", line, re.I):
            held_src.append((str(f), int(mm.group(1))))
placed = {(h["source"].rsplit(" row ", 1)[0], h["row"]): h for h in tt.get("held_statements", [])}
bids = {b["id"]: b for b in B}
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
check("C8_held_statements_placed", "every held look statement in validation_holding/ is on a bar and a test", ref,
      "%d held rows found (%s)" % (len(held_src), ", ".join(sorted({s for s, _ in held_src}))), t=t)

# C9 every named def is real; ours judged against the repo NOW (stale-dump fix), with an instrument probe
t = time.time(); ref = []
named = set()
for x in T.values():
    named |= set(x.get("defs", []))
lock_text = " ".join((CON / f).read_text(errors="replace") for f in LOCKED_FILES)
named |= {tok for tok in re.findall(r"\b((?:RM|RUT|RSW)_\w+)", lock_text)}
families = sorted(d for d in named if OURS.match(d) and def_verdict(d)
                  and sum(1 for r in repo_defs if r.startswith(d + "_")) >= 2)  # prose family name ("an RM_Graffiti mark")
for d in sorted(named):
    if d in families:
        continue
    why = def_verdict(d)
    if why:
        ref.append(R("def " + d, why, "name a current def or C# type", "Stage 1" if d in lock_text else "neutral fixer"))
probe = [(STALE, False, "a dump-only def of ours"), ("RM_Graffiti_NoSuchProbeDef", False, "a fake name of ours"),
         ("RM_Graffiti_ThrowUp_A", True, "a real def of ours"), ("Wall", True, "a vanilla def")]
probe_out = []
for name, should_pass, label in probe:
    if name is None:
        probe_out.append("%s: UNMEASURED (no dump-only def of ours in this dump)" % label)
        continue
    got = def_verdict(name) is None
    probe_out.append("%s %s: %s" % (label, name, "pass" if got else "refuse"))
    if got != should_pass:
        ref.append(R("probe " + name, "%s should %s" % (label, "pass" if should_pass else "refuse"),
                     "fix def_verdict", "neutral fixer"))
check("C9_defs_real", "every named def is real; our RM_/RUT_/RSW_ names against the repo's current XML and C# types", ref,
      "%d names (%d family prefixes, each with >=2 current repo defs: %s); dump %s captured %s (%d defs); %d dump-only defs of ours; probe: %s" % (
          len(named), len(families), ", ".join(families), DUMP, prov.get("captured_utc", "UNMEASURED"), len(dump_defs), len(dump_only_ours), "; ".join(probe_out)), t=t)

# C10 every named mod is real
t = time.time(); ref = []; mods = set()
for x in T.values():
    mods |= {m.lower() for m in x.get("mods", [])}
for mo in sorted(mods):
    if mo not in dump_mods and mo not in repo_pkgs:
        ref.append(R("mod " + mo, "in neither the dump's mods nor a repo About.xml", "name a real packageId", "neutral fixer"))
check("C10_mods_real", "every named mod is real", ref, "%d mods named" % len(mods), t=t)

# C11 every named settings field is real, and the scenes' count of shipped settings is the code's
t = time.time(); ref = []
modcs = (GRF / "Source/RM_GraffitiMod.cs").read_text()
fields = re.findall(r"public static (?:bool|int|float) (\w+)\s*=", modcs)
blob = lock_text + " ".join(x.get("observes", "") for x in T.values())
named_fields = set(re.findall(r"\b([a-z]\w*Enabled)\b", blob)) | set(re.findall(r"\b(paintIntervalTicks)\b", blob))
for fn in sorted(named_fields):
    if fn not in fields:
        ref.append(R("setting " + fn, "not a field of RM_GraffitiMod", "name a real field", "Stage 1" if fn in lock_text else "neutral fixer"))
claimed = set(re.findall(r"all (\d+) shipped settings", lock_text))
for c in claimed:
    if int(c) != len(fields):
        ref.append(R("scenes.json start", "claims %s shipped settings, RM_GraffitiMod has %d" % (c, len(fields)),
                     "fix the count", "Stage 1"))
check("C11_settings_real", "every named settings field is real and the shipped count matches", ref,
      "%d fields in RM_GraffitiMod.cs: %s; named %d; claimed counts %s" % (len(fields), ", ".join(fields), len(named_fields), sorted(claimed)), t=t)

# C12 lock pins unchanged
t = time.time(); ref = []
pins = dict(re.findall(r"\|\s*`design/concepts/Graffiti/([\w.]+)`\s*\|\s*`([0-9a-f]{40})`", (VER / "bars.md").read_text()))
pins.update(LOCKED_PIN_OVERRIDE)
for f in LOCKED_FILES:
    blob_now = subprocess.run(["git", "hash-object", str(CON / f)], capture_output=True, text=True).stdout.strip()
    if f not in pins:
        ref.append(R("bars.md", "%s has no pin" % f, "pin it", "Stage 1"))
    elif pins[f] != blob_now:
        last = subprocess.run(["git", "log", "-1", "--format=%h %ci %s", "--", str(CON / f)],
                              capture_output=True, text=True).stdout.strip()
        ref.append(R("design/concepts/Graffiti/" + f, "blob %s, pinned %s; last changed by %s" % (blob_now[:12], pins[f][:12], last[:140]),
                     "the owner/steward rules on the post-lock edit: re-pin it in bars.md (an amendment) or restore the pinned blob",
                     "Stage 1"))
check("C12_lock_pins_current", "the seven locked files still hash to their pins in bars.md", ref, "%d pins read" % len(pins), t=t)

# C13 the known open defect sits on a deciding test as known_red
t = time.time(); ref = []
holders = [tid for tid, x in T.items() if x.get("known_red") == KNOWN_RED]
deciding = {d for b in B for d in b["decides"]}
if not holders:
    ref.append(R("test_table.json", "no test carries known_red %s" % KNOWN_RED, "set known_red on P_A9", "neutral fixer"))
elif not any(h in deciding for h in holders):
    ref.append(R("test_table.json", "known_red test(s) %s decide no bar" % holders, "make it decide sits_on_wall", "neutral fixer"))
if KNOWN_RED not in ledger_ids:
    ref.append(R("ledger", "%s not in the ledger" % KNOWN_RED, "file it", "neutral fixer"))
check("C13_known_red_recorded", "the known defect is recorded as known_red on a deciding test", ref,
      "holders %s" % holders, t=t)

# C14 C# symbols real (types, and Type.member names written in observes)
t = time.time(); ref = []; nsym = 0
grf_all = " ".join(grf_cs.values())
for tid, x in T.items():
    for s in x.get("symbols", []):
        nsym += 1
        if not re.search(r"\b(?:class|struct|enum)\s+%s\b" % re.escape(s), grf_all):
            ref.append(R("test " + tid, "C# type %s not in Graffiti sources" % s, "name a real type", "neutral fixer"))
    for typ, mem in re.findall(r"\b([A-Z]\w+)\.([A-Za-z_]\w*)\b", x.get("observes", "")):
        files = [f for f, s in grf_cs.items() if re.search(r"\b(?:class|struct|enum)\s+%s\b" % typ, s)]
        if not files:
            continue  # not one of ours (a file name or prose)
        nsym += 1
        if not any(re.search(r"\b%s\b" % re.escape(mem), grf_cs[f]) for f in files):
            ref.append(R("test " + tid, "%s.%s not in %s" % (typ, mem, files), "name a real member", "neutral fixer"))
check("C14_cs_symbols_real", "every C# type and member a test names is real", ref, "%d symbols" % nsym, t=t)

# C15 items real (new ones are owed for filing, not refusals)
t = time.time(); ref = []; new_items = []
for tid, x in T.items():
    it = x.get("item")
    if not it:
        continue
    if x.get("new") and it not in ledger_ids:
        new_items.append(it)
    elif it not in ledger_ids:
        ref.append(R("test " + tid, "item %s not in the ledger" % it, "name a real item", "neutral fixer"))
for s in scn["scenes"]:
    it = s.get("entry_point_item")
    if it and it not in ledger_ids:
        ref.append(R("scenes.json " + s["id"], "entry_point_item %s not in the ledger" % it, "file or fix it", "Stage 1"))
check("C15_items_real", "every named ledger item is real (new test items are listed for the steward to file)", ref,
      "%d ledger ids read" % len(ledger_ids), t=t, notes={"new_items_unfiled": sorted(set(new_items))})

# C16 every scene is a test on a bar, and every scene decides the leaves it is required for
t = time.time(); ref = []
for s in scn["scenes"]:
    if s["id"] not in T:
        ref.append(R("scenes.json " + s["id"], "no test", "add the scene's test", "neutral fixer")); continue
    if not any(s["id"] in b["decides"] + b["supports"] for b in B):
        ref.append(R("scenes.json " + s["id"], "on no bar", "put it on its bar", "neutral fixer"))
    for leaf in s.get("requirement") or []:
        if leaf in bids and s["id"] not in bids[leaf]["decides"]:
            ref.append(R("bar " + leaf, "scene %s is required for it but does not decide it" % s["id"], "add it to decides", "neutral fixer"))
for cr in scn.get("coverage_rest", []):
    b = bids.get(cr["capability"])
    for by in cr["by"]:
        if b and by in T and by not in b["decides"] + b["supports"]:
            ref.append(R("bar " + cr["capability"], "coverage_rest names %s, the bar does not" % by, "add it", "neutral fixer"))
check("C16_scenes_wired", "every scene is a test on a bar and decides the leaves it is required for", ref,
      "%d scenes" % len(scn["scenes"]), t=t)

# C17 built offline tests green today (known red excepted)
t = time.time(); ref = []
for tid, x in T.items():
    if x["kind"] != "offline" or x.get("new"):
        continue
    rt = x.get("runs_today", {})
    if rt.get("result") == "PASS" or x.get("known_red"):
        continue
    if tid == "T_SHIP_CHECK" and Path(rt.get("log", "")).exists():
        for line in Path(rt["log"]).read_text().splitlines():
            if not line.startswith("FAIL"):
                continue
            clause = line.split()[1]
            if clause == "settings":
                ref.append(R("ship_check.py settings", line[:200], "update the settings clause to the 8 shipped fields and "
                             "the current viewerReactionEnabled label ('Feelings while near a mark')", "neutral fixer"))
            elif clause == "art":
                ref.append(R("ship_check.py art", line[:200], "let the art clause resolve vanilla AssetBundle textures "
                             "(UI/Designators/RemovePaint ships in Ideology)", "neutral fixer"))
            elif clause == "review":
                ref.append(R("ship_check.py review", line[:120] + "...", "review the 37 Graffiti files to CLEAN "
                             "(code_review_status.py)", "Stage 3"))
            else:
                ref.append(R("ship_check.py " + clause, line[:200], "fix the clause", "Stage 3"))
    else:
        ref.append(R("test " + tid, "today %s rc=%s (%s)" % (rt.get("result"), rt.get("rc"), rt.get("last", "")[:120]),
                     "make it green", "Stage 3"))
check("C17_built_offline_green", "every built offline test passes today (known red excepted)", ref,
      "%d built offline tests" % sum(1 for x in T.values() if x["kind"] == "offline" and not x.get("new")), t=t)

# C18 inventory impl_evidence real (paths, :line within the file, ITEM: ids in the ledger)
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
check("C18_inventory_evidence_real", "every record.json impl_evidence path and ITEM is real", ref, "%d evidence entries" % n, t=t)


# C19 every_decider_runnable_today agrees with the measured tests
def runnable(tid):
    x = T.get(tid)
    if not x:
        return False
    if x["kind"] in ("offline", "record"):
        return bool(x.get("runs_today", {}).get("ran")) and x["runs_today"].get("result") == "PASS"
    if x["kind"].startswith("live"):
        return bool(x.get("entry_exists")) and not x.get("known_red")
    return False


t = time.time(); ref = []
for b in B:
    if not isinstance(b.get("every_decider_runnable_today"), bool):
        ref.append(R("bar " + b["id"], "every_decider_runnable_today is not a bool", "write a bool", "neutral fixer"))
    elif b["every_decider_runnable_today"] != all(runnable(d) for d in b["decides"]):
        ref.append(R("bar " + b["id"], "every_decider_runnable_today=%s, its deciders say %s" % (
            b["every_decider_runnable_today"], not b["every_decider_runnable_today"]), "recompute", "neutral fixer"))
check("C19_runnable_flags_measured", "each bar's every_decider_runnable_today agrees with its measured deciders", ref,
      "%d bars runnable today" % sum(1 for b in B if b.get("every_decider_runnable_today") is True), t=t)

# ---- verdict ----
nref = sum(len(c["refusals"]) for c in checks)
out = dict(mod="Graffiti", version="0.1.0", program="design/concepts/Graffiti/version/pilot_throwaway/preflight_graffiti.py",
           at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           dump=dict(path=DUMP, provenance={k: prov[k] for k in list(prov)[:8]}),
           seconds=round(time.time() - T0, 2), verdict="refuse" if nref else "pass", refusals=nref,
           known_red={"P_A9": KNOWN_RED}, checks=checks)
red = [c["id"] for c in checks if c["verdict"] == "refuse"]
if PLANT:
    green = [c["id"] for c in checks if c["verdict"] == "pass"]
    print("PLANTED: %d of %d checks refused; still green: %s" % (len(red), len(checks), green or "none"))
    for c in checks:
        print("  %s: %s" % (c["id"], (c["refusals"][0]["line"] + " | " + c["refusals"][0]["evidence"])[:150] if c["refusals"] else "GREEN"))
    print("PLANTED run wrote nothing")
    sys.exit(0 if not green else 1)
(VER / "preflight.json").write_text(json.dumps(out, indent=1) + "\n")
print("verdict %s, %d refusals, red checks %s" % (out["verdict"], nref, red))
for c in checks:
    for r in c["refusals"]:
        print("  %s | %s | %s | %s" % (c["id"], r["line"], r["evidence"][:110], r["route"]))
