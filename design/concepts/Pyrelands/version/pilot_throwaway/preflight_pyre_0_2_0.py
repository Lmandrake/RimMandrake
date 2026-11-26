#!/usr/bin/env python3
"""THROWAWAY Stage 2 preflight for Pyrelands, the version VERSION.json names (0.2.0 from 2026-11-26).
A copy of preflight_pyre.py (0.1.0, 2026-11-14), changed in these places only (steward run
RIMMANDRAKE_STEWARD_PYRELANDS_PREFLIGHT_STAGE), after preflight_ek_0_2_0.py: the version is read from VERSION.json; C1 reads
the locked ids from version/locked_bars.json (a coverage leaf is not a bar); C6 counts a deciding test the table marks new
(specified, not built) as Stage 3 work, not a refusal (spec Stage 2 exit), and refuses one marked new whose offline file
or live entry is already built (a stale flag); C16 resolves a coverage_rest entry's `checks` as well as its `by`, and
takes a scene left out of the table when version/polish.md records its removal (the rule of 2026-11-20: a check no bar
needs leaves the table, with a record line); C9 takes a name of ours that is a Keyed translation key (or a key's stem
before Label/Text), a texture path or a Defs/Patches file name in the repo, because scenes name those as well as defs
(a name that is none of them, or a deleted texture, still refuses: probes below); --out writes the record elsewhere.
No model. Checks version/test_table.json against the repo, the def dump and the mod list; writes version/preflight.json.
Usage: python3 preflight_pyre.py <repo> [--dump <defs.sqlite>]"""
import json, os, re, sqlite3, subprocess, sys, time, glob, datetime, math
T0 = time.time()
REPO = os.path.abspath(sys.argv[1]); os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils")); from game_paths import DUMP_ROOT  # noqa: E402
DUMP = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else os.path.join(str(DUMP_ROOT), "defs.sqlite")
C = "design/concepts/Pyrelands"; M = "src/RimMandrake/Pyrelands"
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
t = time.time(); want = json.load(open(C + "/version/locked_bars.json"))["ids"]; have = [b["id"] for b in bars]
check("C1_bars_complete", "the table holds exactly the locked bars (version/locked_bars.json)",
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
t = time.time(); r = []; owed = []
valsrc = open(M + "/validation.py", errors="replace").read()
for k, v in tests.items():
    users = [b["id"] for b in bars if k in b["decides"]]
    if not users or k == "LOOK_STAGE8": continue
    if v.get("new"):
        f = (v.get("file") or "").split(" ")[0]
        built = (re.search(r"\b%s\b" % re.escape(v["entry"]), valsrc) is not None) if v["kind"].startswith("live") and v.get("entry") \
            else (v.get("built_in_stage") == "3" and bool(f) and os.path.exists(f))
        if built: r.append("%s: marked new (built in Stage 3) but %s is already built (clear the flag)" % (k, v.get("entry") or f))
        else: owed.append(k)
        continue
    elif v["kind"].startswith("live") and not v.get("entry_exists"): r.append("%s (entry %s::%s absent; item %s) decides %s" % (k, v["file"].split("/")[-1], v["entry"], v.get("item"), ", ".join(users)))
check("C6_built_tests_run", "built mod: every deciding test runs today (his card 2026-11-13, 'Built: runs. New: specified.')", r,
      "%d deciding tests not runnable; %d specified for Stage 3 (new: %s)" % (len(r), len(owed), ", ".join(owed) or "none"), "build each named test, watched failing first, under its named item", "Stage 3 (reconcile): the bar is sound, the test is owed", t)
# C7 a game-stage test says why the game is needed; a full-list test says why
t = time.time(); r = []
for k, v in tests.items():
    if v["kind"].startswith("live") and (not v.get("why_game") or v["why_game"] == "UNSTATED"): r.append("%s: no reason the game is needed" % k)
    if v["kind"] == "live_full" and not v.get("why_full_list"): r.append("%s: no reason the full list is needed" % k)
check("C7_game_reason_written", "every in-game test says why an offline test cannot decide it; every full-list test says why", r, "the reason's truth is the Stage 4 challenger's question, not this program's", "write the reason", "Stage 1", t)
# C8 every held look statement for this mod is placed (found by content: Pyrelands has no file of its own)
t = time.time(); r = []; n = 0
for f in glob.glob("design/RimMandrake/validation_holding/owner_look_defects_*.md"):
    for l in open(f):
        if re.match(r"^\| \d+ \|", l) and re.search(r"pyre|ember|scorch|furnace|ashwallow|flamefang|ullai|\bash\b", l, re.I):
            n += 1; num = int(l.split("|")[1])
            if not any(h["file"] == f and h["row"] == num for h in tab["held_statements"]): r.append("%s row %d not placed" % (f, num))
check("C8_held_statements_placed", "every held look statement for this mod is placed on a bar and a test", r, "%d held rows name this mod's words" % n, "place the row", "Stage 1", t)
# C9 every named def is real (def dump + repo XML)
t = time.time(); r = []; prov = {}
con = sqlite3.connect("file:" + DUMP + "?mode=ro&immutable=1", uri=True)
prov = dict(con.execute("select key, value from provenance"))
defs = set(x[0] for x in con.execute("select def_name from defs"))
pkgs = set(x[0].lower() for x in con.execute("select package_id from mods") if x[0])
repo_defs = set()
for f in glob.glob("src/RimMandrake/**/Defs/**/*.xml", recursive=True):
    repo_defs |= set(re.findall(r"<defName>(\w+)</defName>", open(f, errors="replace").read()))
named = set()
stext = json.dumps(scenes) + json.dumps([{k: l[k] for k in ("oracle_proposed", "scenario")} for l in tree["leaves"]]) + json.dumps(tests)
named |= set(re.findall(r"\b((?:RM|RUT|RSW|LWM)_[A-Za-z0-9_]+)\b", stext))
named |= set(w for w in re.findall(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b", stext) if w in defs or w in repo_defs)  # CamelCase words that are defs: counted as found
code_names = set(re.findall(r"\b(RM_\w+)\b", " ".join(open(f, errors="replace").read() for f in glob.glob(M + "/Source/*.cs"))))
ours_in_dump = set(x[0] for x in con.execute("select def_name from defs where package_id like 'mandrake.%'"))
for f in glob.glob("src/Rim*/**/Defs/**/*.xml", recursive=True) + glob.glob("src/Rim*/**/Patches/**/*.xml", recursive=True):
    repo_defs |= set(re.findall(r"<defName>(\w+)</defName>", open(f, errors="replace").read()))
# Stage 3 fix (the stale-def-list hole, lesson 2026-11-14): a name with OUR prefix is judged against the repo's CURRENT
# defs only (Defs + Patches XML); the dump decides only names that are not ours, because a dump captured before a def was
# deleted still holds it. A C# string mentioning a deleted def no longer vouches for it: only a declared C# type does.
cs_types = set(re.findall(r"\b(?:class|struct|enum)\s+(RM_\w+|RUT_\w+|RSW_\w+)\b", " ".join(
    open(f, errors="replace").read() for f in glob.glob("src/Rim*/**/Source/**/*.cs", recursive=True))))
OURS = re.compile(r"^(RM|RUT|RSW)_")
keys = set(); stems = set()
for f in glob.glob("src/Rim*/*/Languages/**/Keyed/*.xml", recursive=True):
    keys |= set(re.findall(r"<((?:RM|RUT|RSW)_\w+)>", open(f, errors="replace").read()))
for f in glob.glob("src/Rim*/*/Textures/**/*", recursive=True):
    stems.add(re.sub(r"(_north|_south|_east|_west|_[a-z])?\.png$", "", os.path.basename(f)))
for f in glob.glob("src/Rim*/**/Defs/**/*.xml", recursive=True) + glob.glob("src/Rim*/**/Patches/**/*.xml", recursive=True):
    stems.add(os.path.basename(f)[:-4])
def def_verdict(d, defs=defs, repo_defs=repo_defs, ours_in_dump=ours_in_dump, cs_types=cs_types, keys=keys, stems=stems):
    if OURS.match(d) or d in ours_in_dump:
        if d in repo_defs or d in cs_types: return None
        if d in keys or d + "Label" in keys or d + "Text" in keys or d in stems: return None  # a key, a texture or a file of ours
        return d + (" (our def, only in the %s dump: deleted from the repo)" % prov.get("captured_utc", "?") if d in defs
                    else " (our prefix, not in the repo's current defs or C# types)")
    return None if (d in defs or d in repo_defs) else d
for d in sorted(named):
    v = def_verdict(d)
    if v: r.append(v)
_probe = [def_verdict("RM_FE_Filth_LooseAsh") is None and "RM_FE_Filth_LooseAsh" in defs,  # dump-only def of ours must refuse
          def_verdict("RM_FE_NoSuchDef_Probe") is None, def_verdict("RM_Pyrelands") is not None, def_verdict("Rain") is not None,
          def_verdict("RM_StruckGlassRing") is None,  # a texture deleted 2026-10-23 (f100b170dc) must refuse
          def_verdict("RM_Ash") is not None, def_verdict("RM_FireHawkSighted") is not None,  # a key and a key stem pass
          def_verdict("RM_Pyrelands_NoForeignArrivals") is not None]  # a Patches file of ours passes
if any(_probe): r.append("C9 instrument probe failed %s: the check cannot see a stale or a real def" % _probe)
missing_from_dump = sorted(x for x in repo_defs if OURS.match(x) and x not in defs)
check("C9_defs_real", "every def named exists: ours (RM_/RUT_/RSW_) in the repo's current Defs/Patches or as a C# type; others in the def dump or the repo", r,
      "%d names checked; dump %s (captured %s, %d defs, %d mods); %d of our repo defs are newer than the dump" % (len(named), DUMP.split("/")[-1], prov.get("captured_utc", "?"), len(defs), len(pkgs), len(missing_from_dump)),
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
# C11 every Mod Settings field named by the scenes, the leaves and the table exists in RM_PyrelandsMod.cs
t = time.time()
ms = open(M + "/Source/RM_PyrelandsMod.cs").read()
fields = set(re.findall(r"public static (?:bool|float|int|string|double) (\w+)\s*=", ms))
want = sorted(set(re.findall(r"\b([a-z][a-zA-Z]+(?:Enabled|Fertility|Bonus|Chance|Override|Radius|Hours|Giant|Strength))\b", stext)))
r = [w for w in want if w not in fields]
check("C11_settings_fields_real", "every settings field named by the scenes, the leaves and the table exists in RM_PyrelandsMod.cs", r,
      "%d named, %d static fields in the settings class" % (len(want), len(fields)), "correct the field name in the text", "Stage 1", t)
# C12 the locked files still match their pinned blobs
t = time.time(); r = []
pins = re.findall(r"\| `(design/concepts/Pyrelands/[\w.]+)` \| `([0-9a-f]{40})` \|", open(C + "/version/bars.md").read())
for f, blob in pins:
    if f.endswith("stage.json"): continue  # state, not a bar
    now = subprocess.run(["git", "hash-object", f], capture_output=True, text=True).stdout.strip()
    if now != blob: r.append("%s: pinned %s, now %s" % (f, blob[:10], now[:10]))
check("C12_locked_files_unchanged", "the locked bar files match the blobs pinned in version/bars.md", r, "%d pins" % len(pins),
      "the Conductor reads each post-lock change; a test-text change is re-pinned in bars.md, a meaning change goes to him", "Conductor (judgment: test text or meaning?)", t)
# C13 the six applied judge corrections still hold (the judges' own would_pass checks, made exact)
t = time.time(); r = []
sc_t = open(C + "/scenes.json").read(); tr_t = open(C + "/tree.json").read(); sh_t = open(C + "/sheet.md").read(); rc_t = open(C + "/record.json").read()
if re.search(r"LooseAsh|loose-ash filth", sc_t + tr_t): r.append("g1: the deleted loose-ash def is still counted")
if re.search(r"about 40%|about 90%", sc_t + tr_t): r.append("g3: a stale fertility number remains")
if "nothing checks it" in sh_t or "no leaf, no scene, no check" in rc_t: r.append("g5: the sheet or record still says the world switch is unchecked")
if "description text still promising it" in sh_t or "still promise it" in rc_t: r.append("g12: a false migration line remains")
if "furnace-beast in a blackened ruin" in sh_t: r.append("g13: showcase 3 still described as unstaged")
cr = [c for c in scenes["coverage_rest"] if c["capability"] == "inv_art_and_text"]
if not cr or "his approval" not in cr[0]["why"]: r.append("g11: the art coverage why does not rest on his approval")
check("C13_corrections_hold", "the coverage judge's CORRECTION gaps g1 g3 g5 g11 g12 g13 stay applied", r, "text checks of scenes.json, tree.json, sheet.md, record.json", "re-apply the named correction", "Stage 1", t)
# C14 every C# Type.Method the scenes and leaves name exists in the mod's source
t = time.time(); r = []
cs = {os.path.basename(f)[:-3]: open(f, errors="replace").read() for f in glob.glob(M + "/Source/**/*.cs", recursive=True)}
allcs = " ".join(cs.values())
pairs = sorted(set(re.findall(r"\b([A-Z][A-Za-z_]+)\.([A-Z][A-Za-z]+)\b", stext)))
nchk = 0
for typ, meth in pairs:
    if not re.search(r"\b(class|struct) %s\b" % typ, allcs): continue  # not one of ours (a vanilla or prose name)
    nchk += 1
    if not re.search(r"\b%s\b" % meth, allcs): r.append("%s.%s" % (typ, meth))
check("C14_csharp_symbols_real", "every Type.Member of ours that the scenes, leaves or table name exists in the mod's C#", r, "%d of our types named" % nchk, "correct the name", "Stage 1", t)
# C16 every scene's requirement is a locked leaf, and every scene is in the table
t = time.time(); r = []
lids = set(l["id"] for l in tree["leaves"])
def removed_ids(text):
    r"""Ids whose removal from the test table polish.md records: a `record:` line naming it, or a `- \`id\`` item under a
    heading that says checks were removed from the test table."""
    out, under = set(), False
    for l in text.splitlines():
        if l.startswith("#"): under = "removed from the test table" in l
        elif l.startswith("record:"): out |= set(re.findall(r"`(\w+)`", l))
        elif under and re.match(r"^- `(\w+)`", l): out.add(re.match(r"^- `(\w+)`", l).group(1))
    return out
_pol = os.path.join(C, "version/polish.md"); removed = removed_ids(open(_pol).read()) if os.path.exists(_pol) else set()
_p16 = [removed_ids("## x, checks removed from the test table\n- `sc_a` (why)\n## other\n- `sc_b` (why)\nrecord: `sc_c` gone") != {"sc_a", "sc_c"}]
if any(_p16): r.append("C16 instrument probe failed: the removal reader cannot tell a recorded removal from another line")
for s in scenes["scenes"]:
    for q in s.get("requirement") or []:
        if q not in lids: r.append("%s requires unknown leaf %s" % (s["id"], q))
    if s["id"] not in tests and s["id"] not in removed: r.append("%s not in the table, and polish.md records no removal" % s["id"])
for c in scenes["coverage_rest"]:
    for x in c.get("by", []) + c.get("checks", []):
        if x not in lids and x not in S and x not in tests: r.append("coverage_rest %s names unknown %s" % (c["capability"], x))
check("C16_scenes_wired", "every scene's requirement is a locked leaf, every scene is in the table, every coverage_rest name resolves", r, "%d scenes; %d left the table by a recorded removal (polish.md): %s" % (len(scenes["scenes"]), len([x for x in S if x in removed and x not in tests]), ", ".join(sorted(x for x in S if x in removed and x not in tests))), "fix the id, or record the removal", "Stage 1", t)
# C15 the items a test names exist in the ledger
t = time.time(); r = []
items = sorted(set(v["item"].split(" ")[0] for v in tests.values() if v.get("item")))
led = ""
for f in glob.glob("infrastructure/state/ledger/events/*.jsonl"): led += open(f, errors="replace").read()
for it in items:
    if '"%s"' % it not in led: r.append(it)
check("C15_items_real", "every ticket a test is owed under exists in the ledger", r, "%d items" % len(items), "file the item", "Stage 1", t)
out = dict(mod="Pyrelands", version=VER, program="design/concepts/Pyrelands/version/pilot_throwaway/preflight_pyre_0_2_0.py (throwaway, no model)", at=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           dump=dict(path=DUMP, provenance={k: prov[k] for k in list(prov)[:8]}), seconds=round(time.time() - T0, 2),
           verdict="refuse" if any(c["verdict"] == "refuse" for c in checks) else "pass",
           refusals=sum(len(c["refusals"]) for c in checks), checks=checks)
json.dump(out, open(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else C + "/version/preflight.json", "w"), indent=1)
for c in checks: print("%-44s %-6s %3d %s" % (c["id"], c["verdict"], len(c["refusals"]), "; ".join(c["refusals"])[:150]))
print("VERDICT", out["verdict"], "refusals", out["refusals"], "seconds", out["seconds"])
