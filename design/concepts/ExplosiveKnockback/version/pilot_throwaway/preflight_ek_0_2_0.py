#!/usr/bin/env python3
"""THROWAWAY Stage 2 preflight for ExplosiveKnockback, the version VERSION.json names (0.2.0 from 2026-11-24).
A copy of preflight_ek.py (pilot row 3, 2026-11-14, 0.1.0), changed in three places only (steward run
RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE): the version is read from VERSION.json; C6 counts a deciding test
the table marks new (specified, not built) as Stage 3 work, not a refusal (spec Stage 2 exit: "A check whose code is not
written yet is not a refusal"), and refuses one marked new whose `marker` is already in Program.cs (a stale flag);
C12 skips coverage_verdict.json beside stage.json (state, not a bar).
No model. Checks version/test_table.json against the repo, the def dump and the mod list; writes version/preflight.json.
Usage: python3 preflight_ek.py <repo> [--dump <defs.sqlite>]"""
import json, os, re, sqlite3, subprocess, sys, time, glob, datetime, math
T0 = time.time()
REPO = os.path.abspath(sys.argv[1]); os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils")); from game_paths import DUMP_ROOT  # noqa: E402
DUMP = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else os.path.join(str(DUMP_ROOT), "defs.sqlite")
C = "design/concepts/ExplosiveKnockback"; M = "src/RimMandrake/ExplosiveKnockback"
VER = json.load(open(C + "/version/VERSION.json"))["version"]
tab = json.load(open(C + "/version/test_table.json")); tests, bars = tab["tests"], tab["bars"]
tree = json.load(open(C + "/tree.json")); rec = json.load(open(C + "/record.json")); scenes = json.load(open(C + "/scenes.json"))
S = {s["id"]: s for s in scenes["scenes"]}
checks = []
def check(cid, what, refusals, evidence, smallest_fix=None, route=None, t=None):
    checks.append(dict(id=cid, what=what, verdict="refuse" if refusals else "pass", refusals=refusals, evidence=evidence,
                       smallest_fix=smallest_fix if refusals else None, route=route if refusals else None,
                       seconds=round(time.time() - t, 3) if t else None))
# C1 the table holds exactly the 59 bars
t = time.time(); want = [l["id"] for l in tree["leaves"]] + [i["id"] for i in rec["inventory"]]; have = [b["id"] for b in bars]
check("C1_bars_complete", "the table holds exactly the locked bars (tree leaves + record inventory)",
      sorted(set(want) ^ set(have)) + (["duplicate bar ids"] if len(have) != len(set(have)) else []),
      "%d locked, %d in table" % (len(want), len(have)), "add or remove the named bars in test_table.json", "Stage 1", t)
# C2 every bar has a deciding test, every test id defined
t = time.time(); r = []
for b in bars:
    if not b["decides"]: r.append("%s: no deciding test" % b["id"])
    for x in b["decides"] + b["supports"]:
        if x not in tests: r.append("%s names undefined test %s" % (b["id"], x))
check("C2_every_bar_has_a_test", "every bar names at least one deciding test, and every named test is defined", r, "%d bars" % len(bars), "name the test", "Stage 1", t)
# C3 every test names its stage
t = time.time(); r = ["%s: stage %r" % (k, v.get("stage")) for k, v in tests.items() if v.get("stage") not in ("2", "4-5", "6", "8")]
check("C3_every_test_has_a_stage", "every test names a stage of 2, 4-5, 6 or 8", r, "%d tests" % len(tests), "set the stage", "Stage 1", t)
# C4/C5 every named file is real
t = time.time(); r4, r5 = [], []
for k, v in tests.items():
    f = v.get("file", "").split(" ")[0]
    if v["kind"] != "look" and not v.get("new") and f and not os.path.exists(f): r4.append("%s: %s" % (k, f))
    for p in v.get("reads", []):
        if "(" in p: continue  # a described set, not a path
        if not os.path.exists(p): r5.append("%s reads %s" % (k, p))
for h in tab["held_statements"]:
    if not os.path.exists(h["file"]): r4.append("held statement file " + h["file"])
check("C4_test_files_real", "every built test's file exists", r4, "", "fix the path", "Stage 1", t)
check("C5_read_files_real", "every file a test reads exists", sorted(set(r5)), "", "fix the path or build the file", "Stage 1", t)
# C6 Built: runs (his card 2026-11-13). A built mod's deciding tests must run at the lock.
# Measured LIVE here, not read from the table's frozen flags (Stage 3, 2026-11-14): an offline test is built when its file
# exists (and, for new kernel cases, its K- marker is in Program.cs); a live scene when its entry is a `case "<entry>":` of
# the proof code's Build switch (or a name in validation.py for a validation.py entry).
t = time.time(); r = []
proof_src = open(M + "/Source/RM_KnockbackProof.cs", errors="replace").read()
val_src = open(M + "/validation.py", errors="replace").read()
prog_src = open(M + "/Source/SelfTest/Program.cs", errors="replace").read()
def built(k, v):
    if v["kind"] == "offline":
        f = v.get("file", "").split(" ")[0]
        if not os.path.exists(f): return False
        if "new K- cases" in v.get("file", ""): return bool(re.search(r'Check\("K-2[1-9]', prog_src))
        return True
    if v["kind"].startswith("live"):
        e = v.get("entry", "")
        if v.get("file", "").endswith("validation.py"): return ('"%s"' % e) in val_src
        return ('case "%s":' % e) in proof_src
    return True
live_built = {}; owed = []
for k, v in tests.items():
    users = [b["id"] for b in bars if k in b["decides"]]
    live_built[k] = built(k, v)
    if not users or k == "LOOK_STAGE8": continue
    if v.get("new") is True:
        if v.get("marker") and v["marker"] in prog_src: r.append("%s: marked new but its marker %s is in Program.cs (clear the flag)" % (k, v["marker"]))
        else: owed.append(k)
        continue
    if not live_built[k]:
        if v["kind"] == "offline": r.append("%s (offline, file %s not built; item %s) decides %s" % (k, v.get("file"), v.get("item"), ", ".join(users)))
        else: r.append("%s (entry %s::%s absent; item %s) decides %s" % (k, v["file"].split("/")[-1], v["entry"], v.get("item"), ", ".join(users)))
stale = sorted(k for k, v in tests.items() if (v.get("new") or (v["kind"].startswith("live") and not v.get("entry_exists"))) and live_built.get(k) and k not in owed)
check("C6_built_tests_run", "built mod: every deciding test runs today (his card 2026-11-13, 'Built: runs. New: specified.'); measured live against the repo", r,
      "%d deciding tests not runnable; %d specified for Stage 3 (new: %s); %d built since the table was written (table flags stale: %s)" % (len(r), len(owed), ", ".join(owed) or "none", len(stale), ", ".join(stale) or "none"),
      "build each named test, watched failing first, under its named item", "Stage 3 (reconcile): the bar is sound, the test is owed", t)
# C7 a game-stage test says why the game is needed; a full-list test says why
t = time.time(); r = []
for k, v in tests.items():
    if v["kind"].startswith("live") and (not v.get("why_game") or v["why_game"] == "UNSTATED"): r.append("%s: no reason the game is needed" % k)
    if v["kind"] == "live_full" and not v.get("why_full_list"): r.append("%s: no reason the full list is needed" % k)
check("C7_game_reason_written", "every in-game test says why an offline test cannot decide it; every full-list test says why", r, "the reason's truth is the Stage 4 challenger's question, not this program's", "write the reason", "Stage 1", t)
# C8 every held look statement for this mod is placed
t = time.time(); r = []; n = 0
for f in glob.glob("design/RimMandrake/validation_holding/owner_look_defects_*explosive_knockback*.md"):
    rows = [l for l in open(f) if re.match(r"^\| \d+ \|", l)]
    for l in rows:
        n += 1; num = int(l.split("|")[1])
        if not any(h["file"] == f and h["row"] == num for h in tab["held_statements"]): r.append("%s row %d not placed" % (f, num))
    for h in tab["held_statements"]:
        if h["file"] == f and not any(t2 in b["id"] for b in bars for t2 in h["bars"]): r.append("held row %d names unknown bar" % h["row"])
check("C8_held_statements_placed", "every held look statement for this mod is placed on a bar and a test", r, "%d held rows found by file name" % n, "place the row", "Stage 1", t)
# C9 every named def is real (def dump + repo XML)
t = time.time(); r = []; prov = {}
con = sqlite3.connect("file:" + DUMP + "?mode=ro&immutable=1", uri=True)
prov = dict(con.execute("select key, value from provenance"))
defs = set(x[0] for x in con.execute("select def_name from defs"))
pkgs = set(x[0].lower() for x in con.execute("select package_id from mods") if x[0])
repo_defs = set()
for f in glob.glob("src/RimMandrake/**/Defs/**/*.xml", recursive=True):
    repo_defs |= set(re.findall(r"<defName>(\w+)</defName>", open(f, errors="replace").read()))
named = {"RM_PawnFlyer_Knockback"}
named |= set(re.findall(r'defName="(\w+)"', open(M + "/Patches/RM_Knockback_DamageDefs.xml").read()))
stext = json.dumps(scenes)
named |= set(re.findall(r"\b((?:RM|RUT|RSW|LWM)_[A-Za-z0-9_]+)\b", stext))
named |= set(w for w in re.findall(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b", stext) if w in defs or w in repo_defs)  # CamelCase words that are defs: counted as found
code_names = set(re.findall(r"\b(RM_\w+)\b", " ".join(open(f, errors="replace").read() for f in glob.glob(M + "/Source/*.cs"))))
# Stage 3 fix (lesson 20261114T194216Z, the Pyrelands run): the dump is older than the source. A def of OURS (mandrake.*
# in the dump, or an RM_/RSW_/RUT_ name) must be in the repo's CURRENT Defs or Patches XML; the dump alone does not count.
ours_in_dump = set(x[0] for x in con.execute("select def_name from defs where package_id like 'mandrake.%'"))
for f in glob.glob("src/Rim*/**/Defs/**/*.xml", recursive=True) + glob.glob("src/Rim*/**/Patches/**/*.xml", recursive=True):
    repo_defs |= set(re.findall(r"<defName>(\w+)</defName>", open(f, errors="replace").read()))
def ours(d): return d in ours_in_dump or re.match(r"(RM|RSW|RUT)_", d) is not None
for d in sorted(named):
    if ours(d) and d not in repo_defs and d not in code_names:
        r.append(d + (" (only in the dump: our def, gone from the repo; the dump is older than the source)" if d in defs else ""))
    elif not ours(d) and d not in defs and d not in repo_defs and d not in code_names: r.append(d)
check("C9_defs_real", "every def the table, the damage-def patch and the scenes name exists: ours in the repo's current Defs/Patches, others in the def dump (C# class names accepted)", r,
      "%d names checked; dump %s (%s, %d defs, %d mods)" % (len(named), DUMP.split("/")[-1], prov.get("modlist_fingerprint", prov.get("capturedUtc", "?")), len(defs), len(pkgs)),
      "correct the name or build the def", "Stage 1 if a wrong name, Stage 3 if owed", t)
# C10 every mod a scene names exists
t = time.time(); r = []
repo_pk = set()
for f in glob.glob("src/RimMandrake/*/About/About.xml"):
    m = re.search(r"<packageId>([^<]+)</packageId>", open(f, errors="replace").read()); repo_pk |= {m.group(1).strip().lower()} if m else set()
named_pk = set(p.lower() for p in re.findall(r"\b((?:mandrake|lwm|brrainz|ludeon)\.[a-z0-9_.]+[a-z0-9])\b", stext, re.I))
for p in sorted(named_pk):
    if p not in pkgs and p not in repo_pk: r.append(p)
check("C10_mods_real", "every packageId a scene names is a mod in the dump's mod list or the repo", r, "%d named: %s" % (len(named_pk), ", ".join(sorted(named_pk))), "correct the packageId", "Stage 1", t)
# C11 every Mod Settings field the sweep names exists
t = time.time()
sys.path.insert(0, M); import importlib; val = importlib.import_module("validation"); fields = val.settings_fields()
want = re.findall(r"\b([a-z][a-zA-Z]+(?:Limit|Percent|Enabled|Throw|Ticks|Force|Scale|Cells|PerCell|Damage|Stun|Closed|Vectors|Pits|Items|Corpses|Animals|Mechanoids|Downed))\b",
                  json.dumps(S["sc_settings_sweep"]) + tab["tests"]["T_SETTINGS_SWEEP_OFFLINE"]["observes"] + " ".join(tests["sc_settings_sweep"].get("why_game", "").split()))
want = sorted(set(w for w in want if w not in ("blastPowerRefPercent",) or True))
r = [w for w in want if w not in fields]
check("C11_settings_fields_real", "every settings field named by the sweep scene, its offline split and the table exists in RM_KnockbackMod.cs", r,
      "%d named, %d fields in the settings class" % (len(want), len(fields)), "correct the field name in the scene text", "Stage 1", t)
# C12 the locked files still match their pinned blobs
t = time.time(); r = []
pins = re.findall(r"\| `(design/concepts/ExplosiveKnockback/[\w.]+)` \| `([0-9a-f]{40})` \|", open(C + "/version/bars.md").read())
for f, blob in pins:
    if f.endswith("stage.json") or f.endswith("coverage_verdict.json"): continue  # state, not a bar
    now = subprocess.run(["git", "hash-object", f], capture_output=True, text=True).stdout.strip()
    if now != blob: r.append("%s: pinned %s, now %s" % (f, blob[:10], now[:10]))
check("C12_locked_files_unchanged", "the locked bar files match the blobs pinned in version/bars.md", r, "%d pins" % len(pins),
      "the Conductor reads each post-lock change; a test-text change is re-pinned in bars.md, a meaning change goes to him", "Conductor (judgment: test text or meaning?)", t)
# C13 sc_mass_and_power: the admitted colonist band against the expect's order, by the kernel formula the expect states
t = time.time(); r = []
mp = json.dumps(S["sc_mass_and_power"])
band = re.search(r"colonist[^()]*\((\d+) to (\d+) kg\)", mp)
def cells(m, ratio): return min(6, int(math.floor(4 * ratio * 0.655 * max(0.25, min(2.0, math.sqrt(70.0 / m))) + 0.5)))
if band:
    lo, hi = int(band.group(1)), int(band.group(2)); light = cells(12, 2.0)
    ties = [m for m in range(lo, hi + 1) if cells(m, 2.0) >= light]
    if ties and "light > colonist" in mp: r.append("colonist %d-%d kg admitted; %d-%d kg throw %d at damage 100, tying the capped light animal (%d), but the expect says 'light > colonist' and the leaf oracle says 'the colonist 5'" % (lo, hi, ties[0], ties[-1], cells(ties[0], 2.0), light))
else: r.append("colonist band not found in sc_mass_and_power")
check("C13_mass_scene_consistent", "sc_mass_and_power: every admitted colonist mass satisfies the expect's order (judge gap g4)", r, "band %s; kernel formula as the expect states it" % (band.group(0) if band else "?"),
      "a proof hook stages a 64-76 kg colonist (test code); or, his call, the oracle admits a tie at the cap", "Stage 3 test code (Conductor confirms it is not a meaning change)", t)
# C14 held statement 2 as a staging rule: a closed-container scene stages no drawing storage; the open-storage scene stages a shelf
t = time.time(); r = []
cc = " ".join(S["sc_closed_containers"]["start"]) if isinstance(S["sc_closed_containers"]["start"], list) else S["sc_closed_containers"]["start"]
for w in ("Shelf", "ShelfSmall", "Hopper"):
    for m in re.finditer(r"\b%s\b" % w, cc):  # each mention must sit in an open/drawing clause
        win = cc[max(0, m.start() - 40):m.end() + 40]
        if not re.search(r"open|draw", win, re.I): r.append("sc_closed_containers names %s outside an open/drawing clause: ...%s..." % (w, win.strip()[:80]))
if not re.search(r"shelf", json.dumps(S["sc_open_storage"]), re.I): r.append("sc_open_storage stages no shelf")
check("C14_closed_scene_stages_only_hiding_defs", "held statement 2: a closed-container scene stages only a def that hides its contents; goods on a shelf are thrown", r, "text check of scenes.json (a heuristic, not the def's flags)", "restage the scene", "Stage 1", t)
# C15 the items a test names exist in the ledger
t = time.time(); r = []
items = sorted(set(v["item"] for v in tests.values() if v.get("item")))
led = ""
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"): led += open(f, errors="replace").read()
for it in items:
    if '"%s"' % it not in led: r.append(it)
check("C15_items_real", "every ticket a test is owed under exists in the ledger", r, "%d items" % len(items), "file the item", "Stage 1", t)
out = dict(mod="ExplosiveKnockback", version=VER, program="design/concepts/ExplosiveKnockback/version/pilot_throwaway/preflight_ek_0_2_0.py (throwaway, no model)", at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           dump=dict(path=DUMP, provenance={k: prov[k] for k in list(prov)[:8]}), seconds=round(time.time() - T0, 2),
           verdict="refuse" if any(c["verdict"] == "refuse" for c in checks) else "pass",
           refusals=sum(len(c["refusals"]) for c in checks), checks=checks)
json.dump(out, open(C + "/version/preflight.json", "w"), indent=1)
for c in checks: print("%-44s %-6s %3d %s" % (c["id"], c["verdict"], len(c["refusals"]), "; ".join(c["refusals"])[:150]))
print("VERDICT", out["verdict"], "refusals", out["refusals"], "seconds", out["seconds"])
