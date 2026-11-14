#!/usr/bin/env python3
"""Throwaway Stage 2 preflight for FlowWorks 0.1.0 (Maturation advance, row 3). Checks the test-and-stage table against the
repo, the def dump and the ledger. No model. Writes design/concepts/FlowWorks/version/preflight.json.
Check ids and record shape follow the pilot's preflight_ek.py (design/concepts/ExplosiveKnockback/version/preflight.json)."""
import json, os, re, glob, sqlite3, subprocess, time, datetime

T0 = time.time()
ROOT = "/home/mandrake/rm/relentless/clones/RIMMANDRAKE_ADVANCE_FLOWWORKS_OFFLINE_BESIDE_THE_PILOT.det"
os.chdir(ROOT)
C = "design/concepts/FlowWorks"
FW = "src/RimMandrake/FlowWorks"
tab = json.load(open(os.environ.get("FW_TABLE", C + "/version/test_table.json")))
tests, bars = tab["tests"], tab["bars"]
tree = json.load(open(C + "/tree.json"))
rec = json.load(open(C + "/record.json"))
scn = json.load(open(C + "/scenes.json"))
DUMP = os.environ.get("FW_DEFS", "/tmp/fw_pilot/defs.sqlite")
checks = []

def check(cid, what, fn):
    t = time.time()
    refusals, evidence = fn()
    checks.append({"id": cid, "what": what, "verdict": "refuse" if refusals else "pass", "refusals": refusals,
                   "evidence": evidence, "seconds": round(time.time() - t, 3)})

def R(line, why, fix, route, would_pass):
    return {"line": line, "evidence": why, "smallest_fix": fix, "route": route, "would_pass": would_pass}

def c1():
    want = [x["id"] for x in rec["inventory"]] + [l["id"] for l in tree["leaves"]]
    have = [b["id"] for b in bars]
    out = [R(i, "locked bar absent from the table", "add its row", "Stage 1", "a row for it") for i in want if i not in have]
    out += [R(i, "table row is not a locked bar", "remove the row", "Stage 1", "no extra rows") for i in have if i not in want]
    return out, "%d locked, %d in table" % (len(want), len(have))

def c2():
    out = []
    for b in bars:
        if not b["decides"]:
            out.append(R(b["id"], "no deciding test", "name the test that decides it", "Stage 1", "decides non-empty"))
        for t in b["decides"] + b["supports"]:
            if t not in tests:
                out.append(R(b["id"], "names undefined test %s" % t, "define %s or drop it" % t, "Stage 1", "every named test defined"))
    return out, "%d bars" % len(bars)

def c3():
    out = [R(k, "stage %r" % t.get("stage"), "set stage to 2, 4-5, 6 or 8", "Stage 1", "a known stage")
           for k, t in tests.items() if t.get("stage") not in ("2", "4-5", "6", "8")]
    return out, "%d tests" % len(tests)

def built(t):
    return t["file"].startswith("src/")

def c4():
    out = [R(k, "file %s absent" % t["file"], "fix the path or mark it specified", "Stage 1", "the file exists")
           for k, t in tests.items() if built(t) and not os.path.exists(t["file"])]
    return out, "%d built tests" % sum(1 for t in tests.values() if built(t))

def c5():
    out = []
    n = 0
    for k, t in tests.items():
        for f in t.get("reads") or []:
            n += 1
            if not os.path.exists(f):
                out.append(R(k, "reads %s, absent" % f, "fix the path", "Stage 1", "every read file exists"))
    return out, "%d reads" % n

def c6():
    out = []
    used = {t for b in bars for t in b["decides"]}
    for k in sorted(used):
        if k not in tests:
            continue  # C2 reports it
        t = tests[k]
        r = t["runs_today"]
        users = [b["id"] for b in bars if k in b["decides"]]
        if t["kind"] == "offline":
            if not built(t):
                out.append(R(k, "specified, not built (deciding %d bars: %s)" % (len(users), ", ".join(users[:4])),
                             "Stage 3 builds it, failing first", "Stage 3", "it runs and is green"))
            elif not r.get("ran"):
                out.append(R(k, "built but not run: %s" % r.get("why"), "run it", "Stage 3", "rc 0"))
            elif r.get("rc") != 0:
                det = r.get("failed") or r.get("tail") or ""
                out.append(R(k, "red today (rc %s): %s" % (r.get("rc"), str(det)[:200]), "fix the code or the test (a red test is a Stage 3 line)",
                             "Stage 3", "rc 0"))
        elif t["kind"].startswith("live"):
            if not r.get("entry_exists"):
                out.append(R(k, "in-game scene: entry %s absent from %s" % (t.get("entry"), t["file"]),
                             "build the entry (owed under %s)" % t.get("owed_under"), "Stage 3", "the entry function exists"))
    return out, "%d deciding tests; built: runs (his card 2026-11-13). Live scenes judged by entry existence only (offline run)" % len(used)

def c7():
    out = []
    for k, t in tests.items():
        if t["kind"].startswith("live") and not (t.get("why_game") or "").strip():
            out.append(R(k, "in-game test with no reason an offline test cannot decide it", "write why_game", "Stage 1", "a written reason"))
        if t["kind"] == "live_full" and "full" not in (t.get("why_game") or "") and "breadth" not in (t.get("why_game") or ""):
            out.append(R(k, "full-list test with no full-list reason", "say why the full list is needed", "Stage 1", "a written reason"))
    return out, "%d in-game tests" % sum(1 for t in tests.values() if t["kind"].startswith("live"))

NOBAR = ("NO 0.1.0 BAR", "harness", "rule", "question", "process")
def c8():
    out = []
    n = 0
    for f in sorted(glob.glob("design/RimMandrake/validation_holding/owner_look_defects_2026-11-1*.md")):
        if "explosive" in f:
            continue
        tag = os.path.basename(f)[19:-3]
        rows = set()
        for line in open(f):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if line.startswith("| ") and cells[0] not in ("#",) and not set(cells[0]) <= set("-"):
                rows.add(cells[0])
        placed = {h["row"]: h for h in tab["held_statements"] if h["tag"] == tag}
        for r in sorted(rows):
            n += 1
            h = placed.get(r)
            if not h:
                out.append(R("%s#%s" % (tag, r), "held row not placed", "place it on a bar and a test", "Stage 1", "placed"))
            elif not h["bars"] and not any(w in h["kind"] for w in NOBAR):
                out.append(R("%s#%s" % (tag, r), "no bar and no reason", "name the bar or why none", "Stage 1", "placed"))
            elif not h["test"]:
                out.append(R("%s#%s" % (tag, r), "no test", "name the test", "Stage 1", "placed"))
    nob = [h for h in tab["held_statements"] if "NO 0.1.0 BAR" in h["kind"]]
    for h in nob:
        out.append(R("%s#%s" % (h["tag"], h["row"]), "held statement has no 0.1.0 bar (%s)" % h["kind"],
                     "his call: Problem in 0.1.0 (a new bar) or Divergent (next_version)", "owner question", "a bar or a next-version entry"))
    return out, "%d held rows in the files, %d placed" % (n, len(tab["held_statements"]))

def defnames():
    names = set()
    if os.path.exists(DUMP):
        c = sqlite3.connect("file:%s?immutable=1" % DUMP, uri=True)
        names |= {r[0] for r in c.execute("select def_name from defs")}
    for f in glob.glob("src/RimMandrake/**/*.xml", recursive=True):
        try:
            names |= set(re.findall(r"<defName>([^<]+)</defName>", open(f, errors="replace").read()))
        except OSError:
            pass
    for f in glob.glob(FW + "/Source/**/*.cs", recursive=True):
        names |= set(re.findall(r"\b(?:class|struct|enum)\s+(\w+)", open(f, errors="replace").read()))
    return names

def c9():
    names = defnames()
    text = json.dumps(scn) + json.dumps(tab["tests"]) + json.dumps(tab["held_statements"])
    toks = sorted(set(re.findall(r"\b(?:RM|RUT|RSW)_[A-Za-z0-9_]+", text)))
    out = [R(t, "named in scenes/table but in neither the def dump nor the repo", "fix the name or build the def", "Stage 1", "the def exists")
           for t in toks if t not in names and t.rstrip("_") not in names]
    return out, "%d names checked against %d defs/classes (dump %s)" % (len(toks), len(names), os.path.basename(DUMP) if os.path.exists(DUMP) else "ABSENT")

def c10():
    text = json.dumps(scn) + json.dumps(tab)
    pk = sorted(set(re.findall(r"\b(?:mandrake|ludeon)\.[a-z0-9_.]+", text, re.I)))
    have = set()
    if os.path.exists(DUMP):
        c = sqlite3.connect("file:%s?immutable=1" % DUMP, uri=True)
        have |= {(r[0] or "").lower() for r in c.execute("select package_id from mods")}
    for f in glob.glob("src/RimMandrake/*/About/About.xml"):
        have |= {m.lower() for m in re.findall(r"<packageId>([^<]+)</packageId>", open(f, errors="replace").read())}
    out = [R(p, "packageId not in the dump's mods or the repo", "fix it", "Stage 1", "a real mod") for p in pk if p.lower().rstrip(".") not in have]
    return out, "%d packageIds named" % len(pk)

def c11():
    src = "".join(open(f, errors="replace").read() for f in glob.glob(FW + "/Source/**/*.cs", recursive=True))
    text = json.dumps(scn) + json.dumps(tree)
    fields = sorted(set(re.findall(r"\b[a-z][A-Za-z]+(?:Enabled|On|Off)\b", text)) - {"On", "Off"})
    out = [R(f, "settings field named by a scene or leaf, absent from FlowWorks C#", "fix the name", "Stage 1", "the field exists")
           for f in fields if not re.search(r"\b%s\b" % f, src)]
    return out, "%d settings fields named" % len(fields)

def c12():
    pins = dict(re.findall(r"`(design/concepts/FlowWorks/[^`]+)` \| `([0-9a-f]{40})`", open(C + "/version/bars.md").read()))
    out = []
    for f, blob in pins.items():
        now = subprocess.run(["git", "hash-object", f], capture_output=True, text=True).stdout.strip()
        if now != blob and not f.endswith("stage.json"):
            out.append(R(f, "blob %s, pinned %s" % (now[:10], blob[:10]), "explain the change in the journal (test text) or restore", "Stage 1", "pinned bytes"))
    return out, "%d pinned files (stage.json is state, not a bar: exempt)" % len(pins)

def c13():
    out = []
    for s in scn["scenes"]:
        reqs = s.get("requirement")
        if not reqs:
            out.append(R(s["id"], "scene names no requirement (no leaf it proves)", "name its leaves or mark it a showcase-only scene", "Stage 1",
                         "requirement non-empty"))
    return out, "%d scenes" % len(scn["scenes"])

def c14():
    items = set()
    for p in glob.glob("infrastructure/state/items/*.md") + glob.glob("infrastructure/state/items/closed/*.md"):
        items.add(os.path.basename(p)[:-3])
    for p in glob.glob("infrastructure/state/ledger/events/*.jsonl"):
        for line in open(p, errors="replace"):
            m = re.search(r'"id":\s*"([A-Z0-9_]+)"', line)
            if m:
                items.add(m.group(1))
    out = []
    for k, t in tests.items():
        it = (t.get("owed_under") or "").split()[0] if t.get("owed_under") else ""
        if it and re.fullmatch(r"[A-Z0-9_]{8,}", it) and it not in items:
            out.append(R(k, "owed under %s, which is not in the ledger" % it, "file the item (with its acceptance test)", "Stage 3", "the item exists"))
    return out, "%d items known" % len(items)

def c15():
    out = []
    leaf = {l["id"]: l for l in tree["leaves"]}
    for b in bars:
        for k in b["decides"]:
            if k not in tests:
                continue
            t = tests[k]
            if t["kind"] == "live_minimal" and leaf.get(b["id"], {}).get("tier_proposed") == "live_full":
                out.append(R(b["id"], "leaf tier is live_full but its deciding scene %s is minimal" % k, "align tier and scene", "Stage 1", "consistent tier"))
    return out, "tiers"

check("C1_bars_complete", "the table holds exactly the locked bars (record inventory + tree leaves)", c1)
check("C2_every_bar_has_a_test", "every bar names at least one deciding test, and every named test is defined", c2)
check("C3_every_test_has_a_stage", "every test names a stage of 2, 4-5, 6 or 8", c3)
check("C4_test_files_real", "every built test's file exists", c4)
check("C5_read_files_real", "every file a test reads exists", c5)
check("C6_built_tests_run", "built mod: every deciding test runs today (his card 2026-11-13, 'Built: runs. New: specified.')", c6)
check("C7_game_reason_written", "every in-game test says why an offline test cannot decide it; every full-list test says why", c7)
check("C8_held_statements_placed", "every held look statement for this mod is placed on a bar and a test, or says why it has none", c8)
check("C9_defs_real", "every RM_/RUT_/RSW_ name in the scenes and the table exists in the def dump or the repo (C# class names accepted)", c9)
check("C10_mods_real", "every packageId named is a mod in the dump's mod list or the repo", c10)
check("C11_settings_fields_real", "every settings field a scene or leaf names exists in FlowWorks C#", c11)
check("C12_locked_files_unchanged", "the locked bar files match the blobs pinned in version/bars.md", c12)
check("C13_scenes_prove_a_leaf", "every scene names the leaves it proves", c13)
check("C14_items_real", "every ticket a test is owed under exists in the ledger", c14)
check("C15_tiers_consistent", "a leaf whose tier is the full list is decided by a full-list scene", c15)

prov = {}
if os.path.exists(DUMP):
    c = sqlite3.connect("file:%s?immutable=1" % DUMP, uri=True)
    prov = dict(c.execute("select key, value from provenance"))
    prov = {k: prov[k] for k in ("builder", "captured_utc", "defs_total") if k in prov}
nref = sum(len(c["refusals"]) for c in checks)
out = {"mod": "FlowWorks", "version": "0.1.0", "program": "preflight_fw.py (throwaway, advance row 3; copy in version/advance_scripts/)",
       "at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
       "dump": {"path": "a copy of game_paths.DEF_DUMP at " + DUMP, "provenance": prov},
       "seconds": round(time.time() - T0, 2), "verdict": "refuse" if nref else "pass", "refusals": nref, "checks": checks}
json.dump(out, open(os.environ.get("FW_OUT", C + "/version/preflight.json"), "w"), indent=1)
print(out["verdict"], nref, "refusals in", out["seconds"], "s")
for c in checks:
    print(" ", c["id"], c["verdict"], len(c["refusals"]), "|", c["evidence"])
